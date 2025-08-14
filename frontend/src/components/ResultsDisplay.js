import React from 'react';
import { getMediaUrl } from '../api';

const ResultsDisplay = ({ storyData, generationType = 'full' }) => {
    if (!storyData) return null;

    const { 
        session_id, 
        story_text, 
        character_description, 
        background_description, 
        image_urls, 
        processing_status,
        total_time_seconds,
        error_messages 
    } = storyData;

    // Handle failed generation
    if (processing_status === 'failed') {
        return (
            <div className="alert alert-danger" role="alert">
                <h4 className="alert-heading">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    {generationType === 'full' ? 'Story Generation Failed' :
                     generationType === 'story' ? 'Story Generation Failed' :
                     generationType === 'character' ? 'Character Generation Failed' :
                     generationType === 'background' ? 'Background Generation Failed' :
                     'Image Merging Failed'}
                </h4>
                <p className="mb-1">Session ID: <code>{session_id}</code></p>
                {error_messages && Array.isArray(error_messages) && error_messages.length > 0 && (
                    <div className="mb-2">
                        <strong>Error Details:</strong>
                        <ul className="mb-0 mt-1">
                            {error_messages.map((error, index) => (
                                <li key={index}>{error}</li>
                            ))}
                        </ul>
                    </div>
                )}
                <p className="mb-0">Please try again with a different prompt.</p>
            </div>
        );
    }

    // Determine what content to show based on generation type
    const showStory = generationType === 'full' || generationType === 'story';
    const showImages = generationType === 'full' || generationType === 'character' || generationType === 'background' || generationType === 'merge';

    const getGenerationTitle = () => {
        switch (generationType) {
            case 'story':
                return 'Generated Story';
            case 'character':
                return 'Generated Character';
            case 'background':
                return 'Generated Background';
            case 'merge':
                return 'Merged Images';
            default:
                return 'Your Generated Story';
        }
    };

    const getGenerationIcon = () => {
        switch (generationType) {
            case 'story':
                return 'bi-file-text';
            case 'character':
                return 'bi-person';
            case 'background':
                return 'bi-image';
            case 'merge':
                return 'bi-layers';
            default:
                return 'bi-book';
        }
    };

    return (
        <div className="results-container">
            {/* Header with session info */}
            <div className="card mb-4 border-success">
                <div className="card-header bg-success text-white">
                    <h3 className="mb-0">
                        <i className={`${getGenerationIcon()} me-2`}></i>
                        {getGenerationTitle()}
                    </h3>
                    <div className="mt-2">
                        <small>
                            <i className="bi bi-hash me-1"></i>
                            Session: <code>{session_id}</code>
                        </small>
                        {total_time_seconds && (
                            <small className="ms-3">
                                <i className="bi bi-clock me-1"></i>
                                Generated in {Math.round(total_time_seconds)} seconds
                            </small>
                        )}
                        <small className="ms-3">
                            <i className="bi bi-gear me-1"></i>
                            Type: {generationType.charAt(0).toUpperCase() + generationType.slice(1)}
                        </small>
                    </div>
                </div>
            </div>

            {/* Story Text - Show for story or full generation */}
            {showStory && story_text && (
                <div className="card mb-4">
                    <div className="card-header">
                        <h4 className="mb-0">
                            <i className="bi bi-file-text me-2"></i>
                            {generationType === 'story' ? 'Generated Story' : 'Story'}
                        </h4>
                    </div>
                    <div className="card-body">
                        <div className="border rounded p-3 bg-light">
                            <p className="mb-0 story-text">{story_text}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Character Description - Show for character generation */}
            {generationType === 'character' && character_description && (
                <div className="card mb-4">
                    <div className="card-header">
                        <h4 className="mb-0">
                            <i className="bi bi-person me-2"></i>
                            Character Description
                        </h4>
                    </div>
                    <div className="card-body">
                        <div className="border rounded p-3 bg-light">
                            <p className="mb-0">{character_description}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Background Description - Show for background generation */}
            {generationType === 'background' && background_description && (
                <div className="card mb-4">
                    <div className="card-header">
                        <h4 className="mb-0">
                            <i className="bi bi-image me-2"></i>
                            Background Description
                        </h4>
                    </div>
                    <div className="card-body">
                        <div className="border rounded p-3 bg-light">
                            <p className="mb-0">{background_description}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Merge Info - Show for merge generation */}
            {generationType === 'merge' && story_text && (
                <div className="card mb-4">
                    <div className="card-header">
                        <h4 className="mb-0">
                            <i className="bi bi-layers me-2"></i>
                            Merge Information
                        </h4>
                    </div>
                    <div className="card-body">
                        <div className="border rounded p-3 bg-light">
                            <p className="mb-0">{story_text}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Character and Background Descriptions - Only show for full generation */}
            {generationType === 'full' && (character_description || background_description) && (
                <div className="row mb-4">
                    {/* Character Description */}
                    {character_description && (
                        <div className="col-md-6 mb-3">
                            <div className="card h-100">
                                <div className="card-header">
                                    <h5 className="mb-0">
                                        <i className="bi bi-person me-2"></i>
                                        Character Description
                                    </h5>
                                </div>
                                <div className="card-body">
                                    <p className="text-muted mb-0">{character_description}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Background Description */}
                    {background_description && (
                        <div className="col-md-6 mb-3">
                            <div className="card h-100">
                                <div className="card-header">
                                    <h5 className="mb-0">
                                        <i className="bi bi-image me-2"></i>
                                        Background Description
                                    </h5>
                                </div>
                                <div className="card-body">
                                    <p className="text-muted mb-0">{background_description}</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Generated Images - Show based on generation type */}
            {showImages && (
                <div className="card mb-4">
                    <div className="card-header">
                        <h4 className="mb-0">
                            <i className="bi bi-images me-2"></i>
                            {generationType === 'merge' ? 'Merged Images' : 'Generated Images'}
                        </h4>
                    </div>
                    <div className="card-body">
                        <div className="row">
                            {/* Character Image - Show for character, full, or merge */}
                            {(generationType === 'character' || generationType === 'full' || generationType === 'merge') && 
                             image_urls?.character_image && (
                                <div className="col-md-4 mb-3">
                                    <div className="card h-100">
                                        <div className="card-header text-center">
                                            <i className="bi bi-person me-2"></i>
                                            Character
                                        </div>
                                        <div className="card-body p-2 d-flex align-items-center justify-content-center">
                                            <img
                                                src={getMediaUrl(image_urls.character_image)}
                                                alt="Generated character"
                                                className="img-fluid rounded shadow-sm"
                                                style={{ maxHeight: '200px', maxWidth: '100%' }}
                                                onError={(e) => {
                                                    e.target.style.display = 'none';
                                                    e.target.nextSibling.style.display = 'block';
                                                }}
                                            />
                                            <div className="text-muted text-center" style={{ display: 'none' }}>
                                                <i className="bi bi-image" style={{ fontSize: '3rem' }}></i>
                                                <br />
                                                <small>Image not available</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                            
                            {/* Background Image - Show for background, full, or merge */}
                            {(generationType === 'background' || generationType === 'full' || generationType === 'merge') && 
                             image_urls?.background_image && (
                                <div className="col-md-4 mb-3">
                                    <div className="card h-100">
                                        <div className="card-header text-center">
                                            <i className="bi bi-image me-2"></i>
                                            Background
                                        </div>
                                        <div className="card-body p-2 d-flex align-items-center justify-content-center">
                                            <img
                                                src={getMediaUrl(image_urls.background_image)}
                                                alt="Generated background"
                                                className="img-fluid rounded shadow-sm"
                                                style={{ maxHeight: '200px', maxWidth: '100%' }}
                                                onError={(e) => {
                                                    e.target.style.display = 'none';
                                                    e.target.nextSibling.style.display = 'block';
                                                }}
                                            />
                                            <div className="text-muted text-center" style={{ display: 'none' }}>
                                                <i className="bi bi-image" style={{ fontSize: '3rem' }}></i>
                                                <br />
                                                <small>Image not available</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                            
                            {/* Final Merged Image - Show for full or merge */}
                            {(generationType === 'full' || generationType === 'merge') && 
                             image_urls?.merged_image && (
                                <div className="col-md-4 mb-3">
                                    <div className="card h-100">
                                        <div className="card-header text-center">
                                            <i className="bi bi-layers me-2"></i>
                                            Final Scene
                                        </div>
                                        <div className="card-body p-2 d-flex align-items-center justify-content-center">
                                            <img
                                                src={getMediaUrl(image_urls.merged_image)}
                                                alt="Final merged scene"
                                                className="img-fluid rounded shadow-sm"
                                                style={{ maxHeight: '200px', maxWidth: '100%' }}
                                                onError={(e) => {
                                                    e.target.style.display = 'none';
                                                    e.target.nextSibling.style.display = 'block';
                                                }}
                                            />
                                            <div className="text-muted text-center" style={{ display: 'none' }}>
                                                <i className="bi bi-image" style={{ fontSize: '3rem' }}></i>
                                                <br />
                                                <small>Image not available</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                        
                        {/* No images message */}
                        {(!image_urls?.character_image && !image_urls?.background_image && !image_urls?.merged_image) && (
                            <div className="text-center text-muted py-4">
                                <i className="bi bi-image" style={{ fontSize: '3rem' }}></i>
                                <p className="mt-2 mb-0">
                                    {generationType === 'merge' ? 'No images available for merging' :
                                     'No images were generated for this content'}
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Status Badge */}
            <div className="text-center">
                <span className={`badge fs-6 ${processing_status === 'completed' ? 'bg-success' : 'bg-warning'}`}>
                    <i className={`bi ${processing_status === 'completed' ? 'bi-check-circle' : 'bi-clock'} me-1`}></i>
                    {processing_status === 'completed' ? 'Generation Complete' : processing_status}
                </span>
            </div>

            {/* Success Message */}
            {processing_status === 'completed' && (
                <div className="alert alert-success mt-3" role="alert">
                    <h5 className="alert-heading">
                        <i className="bi bi-check-circle me-2"></i>
                        Success!
                    </h5>
                    <p className="mb-0">
                        {generationType === 'full' ? 'Your story has been generated successfully with all images!' :
                         generationType === 'story' ? 'Your story text has been generated successfully!' :
                         generationType === 'character' ? 'Your character image has been generated successfully!' :
                         generationType === 'background' ? 'Your background image has been generated successfully!' :
                         'Your images have been merged successfully!'}
                    </p>
                </div>
            )}
        </div>
    );
};

export default ResultsDisplay;

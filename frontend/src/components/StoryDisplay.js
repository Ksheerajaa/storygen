import React from 'react';
import { getMediaUrl } from '../api';

const StoryDisplay = ({ storyData }) => {
    if (!storyData) return null;

    const { 
        session_id, 
        story_text, 
        character_description, 
        background_description, 
        image_urls, 
        processing_status,
        total_time_seconds 
    } = storyData;

    if (processing_status === 'failed') {
        return (
            <div className="alert alert-danger" role="alert">
                <h4>Story Generation Failed</h4>
                <p>Session ID: {session_id}</p>
                <p>Please try again with a different prompt.</p>
            </div>
        );
    }

    return (
        <div className="card mt-4">
            <div className="card-header">
                <h3>Your Generated Story</h3>
                <small className="text-muted">Session ID: {session_id}</small>
                {total_time_seconds && (
                    <small className="text-muted ms-3">
                        Generated in {Math.round(total_time_seconds)} seconds
                    </small>
                )}
            </div>
            <div className="card-body">
                {/* Story Text */}
                <div className="mb-4">
                    <h4>Story</h4>
                    <div className="border rounded p-3 bg-light">
                        <p className="mb-0">{story_text}</p>
                    </div>
                </div>

                {/* Character Description */}
                {character_description && (
                    <div className="mb-4">
                        <h5>Character Description</h5>
                        <p className="text-muted">{character_description}</p>
                    </div>
                )}

                {/* Background Description */}
                {background_description && (
                    <div className="mb-4">
                        <h5>Background Description</h5>
                        <p className="text-muted">{background_description}</p>
                    </div>
                )}

                {/* Generated Images */}
                {image_urls && (
                    <div className="mb-4">
                        <h5>Generated Images</h5>
                        <div className="row">
                            {image_urls.character_image && (
                                <div className="col-md-4 mb-3">
                                    <div className="card">
                                        <div className="card-header">Character</div>
                                        <div className="card-body p-2">
                                            <img
                                                src={getMediaUrl(image_urls.character_image)}
                                                alt="Generated character"
                                                className="img-fluid rounded"
                                                style={{ maxHeight: '200px' }}
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}
                            
                            {image_urls.background_image && (
                                <div className="col-md-4 mb-3">
                                    <div className="card">
                                        <div className="card-header">Background</div>
                                        <div className="card-body p-2">
                                            <img
                                                src={getMediaUrl(image_urls.background_image)}
                                                alt="Generated background"
                                                className="img-fluid rounded"
                                                style={{ maxHeight: '200px' }}
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}
                            
                            {image_urls.merged_image && (
                                <div className="col-md-4 mb-3">
                                    <div className="card">
                                        <div className="card-header">Final Scene</div>
                                        <div className="card-body p-2">
                                            <img
                                                src={getMediaUrl(image_urls.merged_image)}
                                                alt="Final merged scene"
                                                className="img-fluid rounded"
                                                style={{ maxHeight: '200px' }}
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Status */}
                <div className="mt-3">
                    <span className={`badge ${processing_status === 'completed' ? 'bg-success' : 'bg-warning'}`}>
                        {processing_status}
                    </span>
                </div>
            </div>
        </div>
    );
};

export default StoryDisplay;

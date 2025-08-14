import React, { useState } from 'react';
import StoryForm from '../components/StoryForm';
import StoryDisplay from '../components/StoryDisplay';

const HomePage = () => {
    const [generatedStory, setGeneratedStory] = useState(null);

    const handleStoryGenerated = (storyData) => {
        setGeneratedStory(storyData);
        // Scroll to the story display
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <div className="container mt-4">
            <div className="row justify-content-center">
                <div className="col-lg-10">
                    {/* Header */}
                    <div className="text-center mb-5">
                        <h1 className="display-4">StoryGen</h1>
                        <p className="lead">
                            AI-Powered Story Generation with Custom Images
                        </p>
                        <p className="text-muted">
                            Create unique stories and watch them come to life with AI-generated characters, backgrounds, and scenes.
                        </p>
                    </div>

                    {/* Story Form */}
                    <StoryForm onStoryGenerated={handleStoryGenerated} />

                    {/* Generated Story Display */}
                    {generatedStory && (
                        <StoryDisplay storyData={generatedStory} />
                    )}

                    {/* Information Section */}
                    <div className="card mt-4">
                        <div className="card-header">
                            <h4>How It Works</h4>
                        </div>
                        <div className="card-body">
                            <div className="row">
                                <div className="col-md-3 text-center mb-3">
                                    <div className="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center" style={{ width: '60px', height: '60px' }}>
                                        <strong>1</strong>
                                    </div>
                                    <h6 className="mt-2">Write Prompt</h6>
                                    <small className="text-muted">Describe your story idea</small>
                                </div>
                                <div className="col-md-3 text-center mb-3">
                                    <div className="bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center" style={{ width: '60px', height: '60px' }}>
                                        <strong>2</strong>
                                    </div>
                                    <h6 className="mt-2">AI Generates</h6>
                                    <small className="text-muted">Story and descriptions</small>
                                </div>
                                <div className="col-md-3 text-center mb-3">
                                    <div className="bg-info text-white rounded-circle d-inline-flex align-items-center justify-content-center" style={{ width: '60px', height: '60px' }}>
                                        <strong>3</strong>
                                    </div>
                                    <h6 className="mt-2">Images Created</h6>
                                    <small className="text-muted">Characters and backgrounds</small>
                                </div>
                                <div className="col-md-3 text-center mb-3">
                                    <div className="bg-warning text-white rounded-circle d-inline-flex align-items-center justify-content-center" style={{ width: '60px', height: '60px' }}>
                                        <strong>4</strong>
                                    </div>
                                    <h6 className="mt-2">Final Scene</h6>
                                    <small className="text-muted">Merged composition</small>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Tips Section */}
                    <div className="card mt-4">
                        <div className="card-header">
                            <h4>Tips for Better Stories</h4>
                        </div>
                        <div className="card-body">
                            <ul className="list-unstyled">
                                <li className="mb-2">
                                    <i className="bi bi-lightbulb text-warning me-2"></i>
                                    <strong>Be descriptive:</strong> Include character details, setting, mood, and plot elements
                                </li>
                                <li className="mb-2">
                                    <i className="bi bi-lightbulb text-warning me-2"></i>
                                    <strong>Set the scene:</strong> Describe the environment, time period, and atmosphere
                                </li>
                                <li className="mb-2">
                                    <i className="bi bi-lightbulb text-warning me-2"></i>
                                    <strong>Character motivation:</strong> Explain what drives your characters
                                </li>
                                <li className="mb-2">
                                    <i className="bi bi-lightbulb text-warning me-2"></i>
                                    <strong>Conflict:</strong> Include challenges or obstacles for your characters
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HomePage;

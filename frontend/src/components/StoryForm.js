import React, { useState } from 'react';
import { generateStory } from '../api';

const StoryForm = ({ onStoryGenerated }) => {
    const [promptText, setPromptText] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!promptText.trim()) {
            setError('Please enter a story prompt');
            return;
        }

        setIsGenerating(true);
        setError('');

        try {
            const result = await generateStory(promptText);
            onStoryGenerated(result);
            setPromptText(''); // Clear form on success
        } catch (err) {
            console.error('Story generation failed:', err);
            setError(err.response?.data?.error || 'Failed to generate story. Please try again.');
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="card">
            <div className="card-header">
                <h3>Generate Your Story</h3>
            </div>
            <div className="card-body">
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label htmlFor="promptText" className="form-label">
                            Story Prompt
                        </label>
                        <textarea
                            id="promptText"
                            className="form-control"
                            rows="4"
                            value={promptText}
                            onChange={(e) => setPromptText(e.target.value)}
                            placeholder="Describe the story you want to generate... (e.g., A brave knight discovers a magical forest where trees whisper ancient secrets)"
                            disabled={isGenerating}
                        />
                        <div className="form-text">
                            Be descriptive! The more details you provide, the better your story will be.
                        </div>
                    </div>
                    
                    {error && (
                        <div className="alert alert-danger" role="alert">
                            {error}
                        </div>
                    )}
                    
                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={isGenerating || !promptText.trim()}
                    >
                        {isGenerating ? (
                            <>
                                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                Generating Story...
                            </>
                        ) : (
                            'Generate Story'
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default StoryForm;

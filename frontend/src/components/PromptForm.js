import React, { useState, useEffect, useRef } from 'react';

/**
 * Enhanced PromptForm component with separate generation options
 * Supports story-only, character-only, background-only, and full generation
 */
const PromptForm = ({ onSubmit, isLoading = false }) => {
    const [promptText, setPromptText] = useState('');
    const [generationType, setGenerationType] = useState('full');
    const [validationError, setValidationError] = useState('');
    const [charCount, setCharCount] = useState(0);
    const textareaRef = useRef(null);

    const handleSubmit = (e) => {
        e.preventDefault();

        // Clear previous validation errors
        setValidationError('');

        // Validate input
        if (!promptText.trim()) {
            setValidationError('Please enter a story prompt');
            return;
        }

        if (promptText.trim().length < 10) {
            setValidationError('Story prompt must be at least 10 characters long');
            return;
        }

        // Call parent onSubmit function with generation type
        onSubmit(promptText.trim(), generationType);
    };

    // Character count and validation
    useEffect(() => {
        setCharCount(promptText.length);
    }, [promptText]);

    // Auto-focus textarea on mount
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.focus();
        }
    }, []);

    const handleInputChange = (e) => {
        setPromptText(e.target.value);
        // Clear validation error when user starts typing
        if (validationError) {
            setValidationError('');
        }
    };

    /**
     * Handle keyboard shortcuts
     * @param {KeyboardEvent} e - Keyboard event
     */
    const handleKeyDown = (e) => {
        // Ctrl/Cmd + Enter to submit
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            handleSubmit(e);
        }

        // Tab to indent (add 2 spaces)
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = e.target.selectionStart;
            const end = e.target.selectionEnd;
            const newValue = promptText.substring(0, start) + '  ' + promptText.substring(end);
            setPromptText(newValue);

            // Set cursor position after indentation
            setTimeout(() => {
                e.target.selectionStart = e.target.selectionEnd = start + 2;
            }, 0);
        }
    };

    /**
     * Handle paste event to clean up formatting
     * @param {ClipboardEvent} e - Paste event
     */
    const handlePaste = (e) => {
        e.preventDefault();
        const text = e.clipboardData.getData('text/plain');
        document.execCommand('insertText', false, text);
    };

    const getGenerationTypeInfo = () => {
        switch (generationType) {
            case 'story':
                return {
                    title: 'Story Only',
                    description: 'Generate story text without images',
                    icon: 'bi-file-text',
                    color: 'primary'
                };
            case 'character':
                return {
                    title: 'Character Image',
                    description: 'Generate character image from story',
                    icon: 'bi-person',
                    color: 'success'
                };
            case 'background':
                return {
                    title: 'Background Image',
                    description: 'Generate background image from story',
                    icon: 'bi-image',
                    color: 'info'
                };
            case 'merge':
                return {
                    title: 'Merge Images',
                    description: 'Merge existing character and background',
                    icon: 'bi-layers',
                    color: 'warning'
                };
            default:
                return {
                    title: 'Full Generation',
                    description: 'Complete story with all images',
                    icon: 'bi-stars',
                    color: 'primary'
                };
        }
    };

    const info = getGenerationTypeInfo();

    return (
        <div className="card shadow-lg border-0" style={{ 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '20px'
        }}>
            <div className="card-header text-white text-center py-4" style={{
                background: 'rgba(255, 255, 255, 0.1)',
                borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '20px 20px 0 0'
            }}>
                <h3 className="mb-2">
                    <i className={`bi ${info.icon} me-3`}></i>
                    {info.title}
                </h3>
                <p className="mb-0 opacity-75">{info.description}</p>
            </div>
            
            <div className={`card-body p-4 ${isLoading ? 'form-loading' : ''}`}>
                {/* Generation Type Selection */}
                <div className="generation-type-selector">
                    <h5>Choose Generation Type</h5>
                    <div className="generation-type-options">
                        {[
                            {
                                value: 'full',
                                title: 'Full Generation',
                                description: 'Complete story with all images',
                                icon: 'bi-stars'
                            },
                            {
                                value: 'story',
                                title: 'Story Only',
                                description: 'Generate story text without images',
                                icon: 'bi-file-text'
                            },
                            {
                                value: 'character',
                                title: 'Character Only',
                                description: 'Generate character image from prompt',
                                icon: 'bi-person'
                            },
                            {
                                value: 'background',
                                title: 'Background Only',
                                description: 'Generate background image from prompt',
                                icon: 'bi-image'
                            },
                            {
                                value: 'merge',
                                title: 'Merge Images',
                                description: 'Combine character and background images',
                                icon: 'bi-layers'
                            }
                        ].map((option) => (
                            <div
                                key={option.value}
                                className={`generation-type-option ${
                                    generationType === option.value ? 'selected' : ''
                                }`}
                                onClick={() => setGenerationType(option.value)}
                            >
                                <i className={`bi ${option.icon} generation-type-icon`}></i>
                                <div className="generation-type-title">{option.title}</div>
                                <div className="generation-type-description">{option.description}</div>
                            </div>
                        ))}
                    </div>
                </div>

                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label htmlFor="storyPrompt" className="form-label fw-bold text-white">
                            <i className="bi bi-pencil me-2"></i>
                            {generationType === 'story' ? 'Story Prompt' : 
                             generationType === 'character' ? 'Character Description' :
                             generationType === 'background' ? 'Background Description' :
                             generationType === 'merge' ? 'Story Context for Merging' : 'Story Prompt'}
                        </label>
                        <textarea
                            ref={textareaRef}
                            id="storyPrompt"
                            className={`form-control ${validationError ? 'is-invalid' : ''}`}
                            rows="4"
                            value={promptText}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            onPaste={handlePaste}
                            placeholder={
                                generationType === 'story' ? 'Describe the story you want to generate...' :
                                generationType === 'character' ? 'Describe the character you want to generate...' :
                                generationType === 'background' ? 'Describe the background scene you want to generate...' :
                                generationType === 'merge' ? 'Provide story context for image merging...' :
                                'Describe the story you want to generate...'
                            }
                            disabled={isLoading}
                        />
                        {validationError && (
                            <div className="validation-error">
                                <i className="bi bi-exclamation-triangle me-1"></i>
                                {validationError}
                            </div>
                        )}

                        {/* Character count and keyboard shortcuts */}
                        <div className="d-flex justify-content-between align-items-center mt-3">
                            <div className={`char-count ${charCount < 10 ? 'limit-reached' : ''}`}>
                                <i className="bi bi-hash me-1"></i>
                                {charCount} characters
                                {charCount < 10 && ' (minimum 10 recommended)'}
                            </div>
                            <div className="keyboard-hint">
                                <i className="bi bi-keyboard me-1"></i>
                                Press <kbd className="bg-white text-dark">Ctrl</kbd> + <kbd className="bg-white text-dark">Enter</kbd> to submit
                            </div>
                        </div>

                        <div className="form-text text-white opacity-75 mt-2">
                            <i className="bi bi-lightbulb me-1"></i>
                            {generationType === 'story' ? 'Be descriptive! Include character details, setting, mood, and plot elements for better results.' :
                             generationType === 'character' ? 'Describe the character\'s appearance, clothing, pose, and expression in detail.' :
                             generationType === 'background' ? 'Describe the setting, lighting, atmosphere, and visual elements of the scene.' :
                             generationType === 'merge' ? 'Provide context about how the character and background should be composed together.' :
                             'Be descriptive! Include character details, setting, mood, and plot elements for better results.'}
                        </div>
                    </div>

                    <div className="d-grid">
                        <button
                            type="submit"
                            className="btn btn-submit btn-lg"
                            disabled={isLoading || !promptText.trim()}
                        >
                            {isLoading ? (
                                <>
                                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <i className={`bi ${info.icon} me-2`}></i>
                                    Generate {info.title}
                                </>
                            )}
                        </button>
                    </div>

                    {isLoading && (
                        <div className="text-center mt-4">
                            <small className="text-white opacity-75">
                                <i className="bi bi-info-circle me-1"></i>
                                {generationType === 'story' ? 'This may take a few minutes to generate your story' :
                                 generationType === 'character' ? 'This may take several minutes to generate your character image' :
                                 generationType === 'background' ? 'This may take several minutes to generate your background image' :
                                 generationType === 'merge' ? 'This may take a few minutes to merge your images' :
                                 'This may take several minutes as AI models generate your story and images'}
                            </small>
                        </div>
                    )}
                </form>
            </div>
        </div>
    );
};

export default PromptForm;

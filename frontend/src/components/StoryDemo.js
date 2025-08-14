import React, { useState } from 'react';
import AudioInput from './AudioInput';
import StoryGenerationOutput from './StoryGenerationOutput';
import './StoryDemo.css';

const StoryDemo = () => {
    const [generationType, setGenerationType] = useState('story');
  const [promptText, setPromptText] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
    const [mergeImages, setMergeImages] = useState({ image1: null, image2: null });
    const [generationResult, setGenerationResult] = useState(null);
    const [error, setError] = useState(null);
    const [isFormValid, setIsFormValid] = useState(false);

    // Update form validation whenever inputs change
    React.useEffect(() => {
        validateForm();
    }, [promptText, mergeImages, generationType]);

    const validateForm = () => {
        let valid = false;
        
        if (generationType === 'merge') {
            // For merge images, both images must be selected
            valid = mergeImages.image1 && mergeImages.image2;
        } else {
            // For other types, prompt text must be provided
            valid = promptText.trim().length > 0;
        }
        
        setIsFormValid(valid);
    };

  const handleSubmit = (e) => {
        if (e) e.preventDefault();
        
        if (!isFormValid) {
            alert('Please fill in all required fields');
            return;
        }

      setIsGenerating(true);
        
        // The actual generation will be handled by StoryGenerationOutput component
        // which will either call the backend or use mock data if backend is unavailable
    };

    const handleGenerationComplete = (result) => {
        setGenerationResult(result);
        setIsGenerating(false);
        setError(null);
  };

  const handleReset = () => {
        setPromptText('');
        setMergeImages({ image1: null, image2: null });
        setGenerationResult(null);
        setError(null);
    setIsGenerating(false);
        setIsFormValid(false);
    };

    const handleTypeChange = (e) => {
        setGenerationType(e.target.value);
        // Reset form when changing type
        setPromptText('');
        setMergeImages({ image1: null, image2: null });
        setIsFormValid(false);
    };

    const handleImageUpload = (imageNumber, file) => {
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                setMergeImages(prev => ({
                    ...prev,
                    [imageNumber]: {
                        file: file,
                        preview: e.target.result
                    }
                }));
            };
            reader.readAsDataURL(file);
        }
    };

    const renderInputSection = () => {
        if (generationType === 'merge') {
            return (
                <div className="merge-images-section">
                    <h3>Upload Two Images to Merge</h3>
                    <div className="image-upload-container">
                        <div className="image-upload">
                            <label className="upload-label">
                                <div className="upload-area">
                                    <div className="upload-icon">📷</div>
                                    <span>Upload Image 1</span>
                                </div>
                                <input
                                    type="file"
                                    className="file-input"
                                    accept="image/*"
                                    onChange={(e) => handleImageUpload('image1', e.target.files[0])}
                                />
                            </label>
                            {mergeImages.image1 && (
                                <div className="image-preview">
                                    <img src={mergeImages.image1.preview} alt="Image 1" className="preview-img" />
                                    <div className="image-name">{mergeImages.image1.file.name}</div>
                                </div>
                            )}
                        </div>

                        <div className="merge-arrow">🔄</div>

                        <div className="image-upload">
                            <label className="upload-label">
                                <div className="upload-area">
                                    <div className="upload-icon">📷</div>
                                    <span>Upload Image 2</span>
                                </div>
                                <input
                                    type="file"
                                    className="file-input"
                                    accept="image/*"
                                    onChange={(e) => handleImageUpload('image2', e.target.files[0])}
                                />
                            </label>
                            {mergeImages.image2 && (
                                <div className="image-preview">
                                    <img src={mergeImages.image2.preview} alt="Image 2" className="preview-img" />
                                    <div className="image-name">{mergeImages.image2.file.name}</div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            );
        } else {
            return (
                <div className="prompt-section">
                    <h3>Enter Your Prompt</h3>
                    <AudioInput
                        promptText={promptText}
                        setPromptText={setPromptText}
                        placeholder={`Describe what you want to generate...`}
                    />
                </div>
            );
        }
    };

  return (
    <div className="story-demo">
      <div className="demo-header">
                <h1>🚀 StoryGen AI</h1>
                <p>Create amazing stories and images with artificial intelligence</p>
      </div>

            {!generationResult && !error && !isGenerating ? (
                <>
                    {/* Generation Type Selector */}
              <div className="generation-type-selector">
                        <h2>Choose Your Creation</h2>
                        <div className="type-options">
                            <label className={`type-option ${generationType === 'story' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name="generation-type"
                    value="story"
                    checked={generationType === 'story'}
                    onChange={handleTypeChange}
                  />
                                <div className="option-content">
                                    <div className="option-icon">📖</div>
                                    <div className="option-text">
                                        <span className="option-title">Generate Story</span>
                                        <span className="option-description">Create story text with PDF download</span>
                                    </div>
                                </div>
                            </label>
                            
                            <label className={`type-option ${generationType === 'character' ? 'selected' : ''}`}>
                                <input
                                    type="radio"
                                    name="generation-type"
                                    value="character"
                                    checked={generationType === 'character'}
                                    onChange={handleTypeChange}
                                />
                                <div className="option-content">
                                    <div className="option-icon">👤</div>
                                    <div className="option-text">
                                        <span className="option-title">Generate Character Image</span>
                                        <span className="option-description">Create character image with download</span>
                                    </div>
                                </div>
                            </label>
                            
                            <label className={`type-option ${generationType === 'background' ? 'selected' : ''}`}>
                                <input
                                    type="radio"
                                    name="generation-type"
                                    value="background"
                                    checked={generationType === 'background'}
                                    onChange={handleTypeChange}
                                />
                                <div className="option-content">
                                    <div className="option-icon">🏞️</div>
                                    <div className="option-text">
                                        <span className="option-title">Generate Background Image</span>
                                        <span className="option-description">Create background image with download</span>
                                    </div>
                                </div>
                            </label>
                            
                            <label className={`type-option ${generationType === 'merge' ? 'selected' : ''}`}>
                                <input
                                    type="radio"
                                    name="generation-type"
                                    value="merge"
                                    checked={generationType === 'merge'}
                                    onChange={handleTypeChange}
                                />
                                <div className="option-content">
                                    <div className="option-icon">🔄</div>
                                    <div className="option-text">
                                        <span className="option-title">Merge Images</span>
                                        <span className="option-description">Combine two images into one</span>
                                    </div>
                                </div>
                </label>
                            
                            <label className={`type-option ${generationType === 'full' ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name="generation-type"
                    value="full"
                    checked={generationType === 'full'}
                    onChange={handleTypeChange}
                  />
                                <div className="option-content">
                                    <div className="option-icon">🎨</div>
                                    <div className="option-text">
                                        <span className="option-title">Full Generation</span>
                                        <span className="option-description">Complete story with all images</span>
                                    </div>
                                </div>
                </label>
              </div>
                    </div>

                    {/* Input Section */}
                    {renderInputSection()}
              
                    {/* Form Actions */}
                    <div className="form-actions">
              <button 
                type="submit" 
                className="generate-button"
                            disabled={!isFormValid}
                            onClick={handleSubmit}
                        >
                            🚀 Generate
                        </button>
                        
                        <button
                            type="button"
                            className="reset-button"
                            onClick={() => handleReset()}
                        >
                            🔄 Reset
              </button>
            </div>
                </>
      ) : (
        <StoryGenerationOutput
                    generationType={generationType}
          promptText={promptText}
                    mergeImages={mergeImages}
          onReset={handleReset}
                    onGenerationComplete={handleGenerationComplete}
        />
      )}
    </div>
  );
};

export default StoryDemo;

import React, { useState } from 'react';
import StoryGenerationOutput from './StoryGenerationOutput';
import AudioInput from './AudioInput';
import './StoryDemo.css';

const StoryDemo = () => {
  const [promptText, setPromptText] = useState('');
  const [generationType, setGenerationType] = useState('full');
  const [isGenerating, setIsGenerating] = useState(false);
  const [mergeImages, setMergeImages] = useState({ image1: null, image2: null });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (promptText.trim() || (generationType === 'merge' && mergeImages.image1 && mergeImages.image2)) {
      setIsGenerating(true);
    }
  };

  const handleReset = () => {
    setIsGenerating(false);
    setPromptText('');
    setMergeImages({ image1: null, image2: null });
  };

  const handleAudioTranscription = (transcription) => {
    setPromptText(transcription);
  };

  const handlePromptChange = (e) => {
    setPromptText(e.target.value);
    if (isGenerating) {
      setIsGenerating(false);
    }
  };

  const handleTypeChange = (e) => {
    setGenerationType(e.target.value);
    if (isGenerating) {
      setIsGenerating(false);
    }
  };

  const handleImageUpload = (imageNumber, file) => {
    setMergeImages(prev => ({
      ...prev,
      [imageNumber]: file
    }));
    if (isGenerating) {
      setIsGenerating(false);
    }
  };

  const renderInputSection = () => {
    if (generationType === 'merge') {
      return (
        <div className="merge-images-section">
          <h3>Upload Images to Merge</h3>
          <div className="image-upload-container">
            <div className="image-upload">
              <label htmlFor="image1" className="upload-label">
                <div className="upload-area">
                  {mergeImages.image1 ? (
                    <div className="image-preview">
                      <img 
                        src={URL.createObjectURL(mergeImages.image1)} 
                        alt="Image 1" 
                        className="preview-img"
                      />
                      <span className="image-name">{mergeImages.image1.name}</span>
                    </div>
                  ) : (
                    <>
                      <div className="upload-icon">📷</div>
                      <span>Upload First Image</span>
                    </>
                  )}
                </div>
                <input
                  id="image1"
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleImageUpload('image1', e.target.files[0])}
                  className="file-input"
                />
              </label>
            </div>
            
            <div className="merge-arrow">+</div>
            
            <div className="image-upload">
              <label htmlFor="image2" className="upload-label">
                <div className="upload-area">
                  {mergeImages.image2 ? (
                    <div className="image-preview">
                      <img 
                        src={URL.createObjectURL(mergeImages.image2)} 
                        alt="Image 2" 
                        className="preview-img"
                      />
                      <span className="image-name">{mergeImages.image2.name}</span>
                    </div>
                  ) : (
                    <>
                      <div className="upload-icon">📷</div>
                      <span>Upload Second Image</span>
                    </>
                  )}
                </div>
                <input
                  id="image2"
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleImageUpload('image2', e.target.files[0])}
                  className="file-input"
                />
              </label>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="prompt-section">
        <h3>Enter Your Prompt</h3>
        <div className="form-group">
          <textarea
            value={promptText}
            onChange={handlePromptChange}
            placeholder="Describe what you want to generate..."
            rows="3"
            required={generationType !== 'merge'}
            className="story-input"
          />
        </div>
        
        {/* Audio Input for all prompt-based functions */}
        <AudioInput onTranscriptionComplete={handleAudioTranscription} />
      </div>
    );
  };

  const isFormValid = () => {
    if (generationType === 'merge') {
      return mergeImages.image1 && mergeImages.image2;
    }
    return promptText.trim().length > 0;
  };

  return (
    <div className="story-demo">
      {/* Header with Title */}
      <div className="demo-header">
        <h1>StoryGen</h1>
        <p>AI-powered story generation with custom images</p>
      </div>

      {!isGenerating ? (
        <div className="demo-form">
          <form onSubmit={handleSubmit} className="chat-form">
            <div className="form-actions">
              <div className="generation-type-selector">
                <h3>Generation Type</h3>
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
              
              {renderInputSection()}
              
              <button 
                type="submit" 
                className="generate-button"
                disabled={!isFormValid()}
              >
                🚀 Generate
              </button>
            </div>
          </form>
        </div>
      ) : (
        <StoryGenerationOutput
          promptText={promptText}
          generationType={generationType}
          mergeImages={mergeImages}
          onReset={handleReset}
        />
      )}
    </div>
  );
};

export default StoryDemo;

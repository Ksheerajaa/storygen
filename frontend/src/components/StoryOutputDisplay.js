import React from 'react';
import './StoryOutputDisplay.css';

const StoryOutputDisplay = ({ generationResult, isLoading, error }) => {
  if (isLoading) {
    return <div className="loading">Loading results...</div>;
  }

  if (error) {
    return <div className="error">Error: {error}</div>;
  }

  if (!generationResult) {
    return <div className="no-result">No results to display</div>;
  }

  const { story_text, image_urls, session_id, total_time_seconds, timestamp } = generationResult;

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Unknown';
    try {
      return new Date(timestamp).toLocaleString();
    } catch (e) {
      return 'Invalid date';
    }
  };

  const downloadStoryAsPDF = () => {
    // Create a simple PDF-like document
    const storyText = story_text || 'No story content available';
    const blob = new Blob([storyText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'story.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadImage = (imageUrl, filename) => {
    if (!imageUrl) return;
    
    const a = document.createElement('a');
    a.href = imageUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const renderStoryContent = () => {
    if (!story_text) return null;
    
    return (
      <div className="story-content">
        <h3>Generated Story</h3>
        <div className="story-text">
          {story_text}
        </div>
        <button 
          className="download-button story-download"
          onClick={downloadStoryAsPDF}
        >
          📄 Download Story as Text
        </button>
      </div>
    );
  };

  const renderCharacterImage = () => {
    if (!image_urls?.character_image) return null;
    
    return (
      <div className="image-content">
        <h3>Character Image</h3>
        <div className="image-container">
          <img 
            src={image_urls.character_image} 
            alt="Generated character" 
            className="generated-image"
          />
        </div>
        <button 
          className="download-button image-download"
          onClick={() => downloadImage(
            image_urls.character_image, 
            'character_image.png'
          )}
        >
          🖼️ Download Character Image
        </button>
      </div>
    );
  };

  const renderBackgroundImage = () => {
    if (!image_urls?.background_image) return null;
    
    return (
      <div className="image-content">
        <h3>Background Image</h3>
        <div className="image-container">
          <img 
            src={image_urls.background_image} 
            alt="Generated background" 
            className="generated-image"
          />
        </div>
        <button 
          className="download-button image-download"
          onClick={() => downloadImage(
            image_urls.background_image, 
            'background_image.png'
          )}
        >
          🖼️ Download Background Image
        </button>
      </div>
    );
  };

  const renderMergedImage = () => {
    if (!image_urls?.merged_image) return null;
    
    return (
      <div className="image-content">
        <h3>Merged Image</h3>
        <div className="image-container">
          <img 
            src={image_urls.merged_image} 
            alt="Merged image" 
            className="generated-image"
          />
        </div>
        <button 
          className="download-button image-download"
          onClick={() => downloadImage(
            image_urls.merged_image, 
            'merged_image.png'
          )}
        >
          🖼️ Download Merged Image
        </button>
      </div>
    );
  };

  const renderFullGeneration = () => {
    if (!image_urls?.final_scene) return null;
    
    return (
      <div className="image-content">
        <h3>Final Scene</h3>
        <div className="image-container">
          <img 
            src={image_urls.final_scene} 
            alt="Final scene" 
            className="generated-image"
          />
        </div>
        <button 
          className="download-button image-download"
          onClick={() => downloadImage(
            image_urls.final_scene, 
            'final_scene.png'
          )}
        >
          🖼️ Download Final Scene
        </button>
      </div>
    );
  };

  return (
    <div className="story-output-display">
      <div className="output-header">
        <h2>Generation Complete! 🎉</h2>
        <p>Your content has been generated successfully. You can download the results below.</p>
      </div>

      <div className="output-content">
        {renderStoryContent()}
        {renderCharacterImage()}
        {renderBackgroundImage()}
        {renderMergedImage()}
        {renderFullGeneration()}
      </div>

      <div className="output-footer">
        <p><strong>Session ID:</strong> {session_id?.slice(0, 8)}...</p>
        <p><strong>Generation Time:</strong> {total_time_seconds || 0} seconds</p>
        <p><strong>Completed:</strong> {formatTimestamp(timestamp)}</p>
      </div>
    </div>
  );
};

export default StoryOutputDisplay;

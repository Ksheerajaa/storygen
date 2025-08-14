import React from 'react';
import './StoryOutputDisplay.css';

const StoryOutputDisplay = ({ 
    generationResult, 
    isLoading, 
    error,
    onBackToMenu 
}) => {
    if (isLoading) {
        return (
            <div className="story-output-display">
                <div className="loading-message">Generating your content...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="story-output-display">
                <div className="error-message">Error: {error}</div>
            </div>
        );
    }

    if (!generationResult) {
        return (
            <div className="story-output-display">
                <div className="no-result-message">No generation result available.</div>
            </div>
        );
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
      
      // Handle both real URLs and data URLs
      if (imageUrl.startsWith('data:')) {
        // For data URLs (base64 encoded images)
        const a = document.createElement('a');
        a.href = imageUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      } else if (imageUrl.startsWith('http')) {
        // For real URLs, try to fetch and download
        fetch(imageUrl)
          .then(response => response.blob())
          .then(blob => {
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
          })
          .catch(error => {
            console.error('Failed to download image:', error);
            // Fallback: open in new tab
            window.open(imageUrl, '_blank');
          });
      } else {
        // For relative URLs or other cases
        const a = document.createElement('a');
        a.href = imageUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      }
    };

    const renderImageWithFallback = (imageUrl, altText, title) => {
      if (!imageUrl) return null;
      
      return (
        <div className="image-content">
          <h3>{title}</h3>
          <div className="image-container">
            <img 
              src={imageUrl} 
              alt={altText} 
              className="generated-image"
              onError={(e) => {
                // If image fails to load, show a placeholder
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <div className="image-placeholder" style={{ display: 'none' }}>
              <div className="placeholder-icon">🖼️</div>
              <p>Image preview not available</p>
              <p className="placeholder-note">Click download to save the image</p>
            </div>
          </div>
          <button 
            className="download-button image-download"
            onClick={() => downloadImage(imageUrl, `${title.toLowerCase().replace(/\s+/g, '_')}.png`)}
          >
            🖼️ Download {title}
          </button>
        </div>
      );
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
        <div className="image-content character-image-content">
          <h3>Character Image</h3>
          <div className="image-container">
            <img 
              src={image_urls.character_image} 
              alt="Generated character" 
              className="generated-image"
              onError={(e) => {
                // If image fails to load, show a placeholder
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <div className="image-placeholder" style={{ display: 'none' }}>
              <div className="placeholder-icon">🖼️</div>
              <p>Image preview not available</p>
              <p className="placeholder-note">Click download to save the image</p>
            </div>
          </div>
          
          <div className="image-actions">
            <button 
              className="download-button image-download"
              onClick={() => downloadImage(image_urls.character_image, 'character_image.png')}
            >
              🖼️ Download Character Image
            </button>
            
            <div className="image-info">
              <p><strong>Generated from:</strong> Character description prompt</p>
              <p><strong>Processing:</strong> AI image generation with Stable Diffusion</p>
              <p><strong>Format:</strong> PNG with background removal</p>
            </div>
          </div>
        </div>
      );
    };

    const renderBackgroundImage = () => {
      if (!image_urls?.background_image) return null;
      
      return (
        <div className="image-content background-image-content">
          <h3>Background Image</h3>
          <div className="image-container">
            <img 
              src={image_urls.background_image} 
              alt="Generated background" 
              className="generated-image"
              onError={(e) => {
                // If image fails to load, show a placeholder
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <div className="image-placeholder" style={{ display: 'none' }}>
              <div className="placeholder-icon">🖼️</div>
              <p>Image preview not available</p>
              <p className="placeholder-note">Click download to save the image</p>
            </div>
          </div>
          
          <div className="image-actions">
            <button 
              className="download-button image-download"
              onClick={() => downloadImage(image_urls.background_image, 'background_image.png')}
            >
              🖼️ Download Background Image
            </button>
            
            <div className="image-info">
              <p><strong>Generated from:</strong> Background description prompt</p>
              <p><strong>Processing:</strong> AI image generation with Stable Diffusion</p>
              <p><strong>Format:</strong> PNG landscape format</p>
            </div>
          </div>
        </div>
      );
    };

    const renderMergedImage = () => {
      if (!image_urls?.merged_image) return null;
      
      return (
        <div className="image-content merged-image-content">
          <h3>Merged Image</h3>
          <div className="image-container">
            <img 
              src={image_urls.merged_image} 
              alt="Merged image" 
              className="generated-image"
              onError={(e) => {
                // If image fails to load, show a placeholder
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <div className="image-placeholder" style={{ display: 'none' }}>
              <div className="placeholder-icon">🖼️</div>
              <p>Image preview not available</p>
              <p className="placeholder-note">Click download to save the image</p>
            </div>
          </div>
          
          <div className="image-actions">
            <button 
              className="download-button image-download"
              onClick={() => downloadImage(image_urls.merged_image, 'merged_image.png')}
            >
              🖼️ Download Merged Image
            </button>
            
            <div className="image-info">
              <p><strong>Generated from:</strong> Two uploaded images</p>
              <p><strong>Processing:</strong> Background removal and composition</p>
              <p><strong>Format:</strong> PNG with transparency support</p>
            </div>
          </div>
        </div>
      );
    };

    const renderFullGeneration = () => {
      if (!image_urls?.final_scene) return null;
      
      return (
        <div className="image-content final-scene-content">
          <h3>Final Scene</h3>
          <div className="image-container">
            <img 
              src={image_urls.final_scene} 
              alt="Final scene" 
              className="generated-image"
              onError={(e) => {
                // If image fails to load, show a placeholder
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'block';
              }}
            />
            <div className="image-placeholder" style={{ display: 'none' }}>
              <div className="placeholder-icon">🖼️</div>
              <p>Image preview not available</p>
              <p className="placeholder-note">Click download to save the image</p>
            </div>
          </div>
          
          <div className="image-actions">
            <button 
              className="download-button image-download"
              onClick={() => downloadImage(image_urls.final_scene, 'final_scene.png')}
            >
              🖼️ Download Final Scene
            </button>
            
            <div className="image-info">
              <p><strong>Generated from:</strong> Character and background composition</p>
              <p><strong>Processing:</strong> AI image merging and scene composition</p>
              <p><strong>Format:</strong> PNG with layered composition</p>
            </div>
          </div>
        </div>
      );
    };

    return (
        <div className="story-output-display">
            {/* Back to Menu Button */}
            {onBackToMenu && (
                <div className="back-to-menu">
                    <button 
                        className="back-button"
                        onClick={onBackToMenu}
                    >
                        ← Back to Menu
                    </button>
                </div>
            )}

            {/* Output Header */}
            <div className="output-header">
                <h2>🎉 Generation Complete!</h2>
                <div className="output-meta">
                    <span>Session ID: {session_id}</span>
                    {total_time_seconds && <span>Time: {total_time_seconds}s</span>}
                    {timestamp && <span>Created: {new Date(timestamp).toLocaleString()}</span>}
                </div>
            </div>

            {/* Output Content */}
            <div className="output-content">
                {renderStoryContent()}
                {renderCharacterImage()}
                {renderBackgroundImage()}
                {renderMergedImage()}
                {renderFullGeneration()}
            </div>
        </div>
    );
};

export default StoryOutputDisplay;

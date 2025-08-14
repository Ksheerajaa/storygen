import React, { useState, useEffect } from 'react';
import StoryOutputDisplay from './StoryOutputDisplay';
import './StoryGenerationOutput.css';

const StoryGenerationOutput = ({ 
  promptText, 
  generationType, 
  mergeImages,
  onReset,
  backendUrl = 'http://127.0.0.1:8000'
}) => {
  const [generationState, setGenerationState] = useState('idle'); // idle, loading, success, error
  const [generationResult, setGenerationResult] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [stepProgress, setStepProgress] = useState({});
  const [useStreaming, setUseStreaming] = useState(true); // Try streaming first
  const [isCancelled, setIsCancelled] = useState(false);

  useEffect(() => {
    if (promptText && generationType && generationState === 'idle') {
      startGeneration();
    }
  }, [promptText, generationType]);

  const cancelGeneration = () => {
    setIsCancelled(true);
    setGenerationState('idle');
    setError(null);
    setProgress(0);
    setGenerationResult(null);
    setCurrentStep('');
    setStepProgress({});
    if (onReset) onReset();
  };

  const startGeneration = async () => {
    setGenerationState('loading');
    setError(null);
    setProgress(0);
    setGenerationResult(null);
    setCurrentStep('Initializing...');
    setStepProgress({});
    setIsCancelled(false); // Reset cancelled state

    try {
      // Try streaming endpoint first if enabled
      if (useStreaming && await tryStreamingGeneration()) {
        return; // Success with streaming
      }
      
      // Fallback to regular endpoint
      setUseStreaming(false); // Disable streaming for future attempts
      await tryRegularGeneration();
      
    } catch (err) {
      console.error('Generation error:', err);
      setError(err.message || 'Failed to generate story. Please try again.');
      setGenerationState('error');
    }
  };

  const tryStreamingGeneration = async () => {
    try {
      let response;
      
      if (generationType === 'merge') {
        // For merge images, we'll need to handle file uploads
        const formData = new FormData();
        formData.append('generation_type', generationType);
        if (mergeImages.image1) formData.append('image1', mergeImages.image1);
        if (mergeImages.image2) formData.append('image2', mergeImages.image2);
        
        response = await fetch(`${backendUrl}/api/stream-generate-story/`, {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          return false;
        }
      } else {
        // For other types, send prompt text
        const requestBody = {
          prompt_text: promptText,
          generation_type: generationType
        };
        
        response = await fetch(`${backendUrl}/api/stream-generate-story/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
          return false; // Fallback to regular endpoint
        }
      }

      // Handle streaming response with timeout
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      const startTime = Date.now();
      const timeout = 10 * 60 * 1000; // 10 minutes timeout

      while (true) {
        // Check for timeout
        if (Date.now() - startTime > timeout) {
          throw new Error('Generation timeout. The process is taking longer than expected.');
        }

        // Check if cancelled
        if (isCancelled) {
          reader.cancel();
          return false;
        }

        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'status') {
                // Update progress and current step
                setProgress(data.progress || 0);
                setCurrentStep(data.message || 'Processing...');
                
                // Update step progress based on message content and generation type
                if (generationType === 'story') {
                  if (data.message.includes('story content')) {
                    setStepProgress(prev => ({ ...prev, story: data.progress || 0 }));
                  }
                } else if (generationType === 'character') {
                  if (data.message.includes('character image')) {
                    setStepProgress(prev => ({ ...prev, character: data.progress || 0 }));
                  }
                } else if (generationType === 'background') {
                  if (data.message.includes('background image')) {
                    setStepProgress(prev => ({ ...prev, background: data.progress || 0 }));
                  }
                } else if (generationType === 'merge') {
                  if (data.message.includes('merging')) {
                    setStepProgress(prev => ({ ...prev, merge: data.progress || 0 }));
                  }
                } else if (generationType === 'full') {
                  // Full generation with detailed progress
                  if (data.message.includes('story content')) {
                    setStepProgress(prev => ({ ...prev, story: data.progress || 0 }));
                  } else if (data.message.includes('character image')) {
                    setStepProgress(prev => ({ ...prev, character: data.progress || 0 }));
                  } else if (data.message.includes('background image')) {
                    setStepProgress(prev => ({ ...prev, background: data.progress || 0 }));
                  } else if (data.message.includes('Compositing')) {
                    setStepProgress(prev => ({ ...prev, composite: data.progress || 0 }));
                  }
                }
              } else if (data.type === 'complete') {
                // Generation completed successfully
                setProgress(100);
                setCurrentStep('Generation complete!');
                setGenerationResult(data.data);
                setGenerationState('success');
                return true; // Success with streaming
              } else if (data.type === 'error') {
                // Generation failed
                throw new Error(data.message || 'Generation failed');
              }
            } catch (parseError) {
              console.warn('Failed to parse SSE data:', parseError);
            }
          }
        }
      }
      
      return false; // Streaming completed but no success
      
    } catch (err) {
      console.warn('Streaming generation failed, falling back to regular endpoint:', err);
      return false; // Fallback to regular endpoint
    }
  };

  const tryRegularGeneration = async () => {
    // Simulate progress for better UX with regular endpoint
      const progressInterval = setInterval(() => {
      if (isCancelled) {
        clearInterval(progressInterval);
        return;
      }
        setProgress(prev => {
        if (prev >= 95) {
            clearInterval(progressInterval);
          return 95;
        }
        return prev + 1;
      });
    }, 100);

    // Update steps based on progress and generation type
    const stepInterval = setInterval(() => {
      if (isCancelled) {
        clearInterval(stepInterval);
        return;
      }
      
      setCurrentStep(prevStep => {
        if (generationType === 'story') {
          if (progress < 50) return 'Processing prompt...';
          if (progress < 95) return 'Generating story content...';
          return 'Finalizing story...';
        } else if (generationType === 'character') {
          if (progress < 30) return 'Processing prompt...';
          if (progress < 95) return 'Creating character image...';
          return 'Finalizing image...';
        } else if (generationType === 'background') {
          if (progress < 30) return 'Processing prompt...';
          if (progress < 95) return 'Creating background image...';
          return 'Finalizing image...';
        } else if (generationType === 'merge') {
          if (progress < 30) return 'Processing images...';
          if (progress < 95) return 'Merging images...';
          return 'Finalizing merged image...';
        } else {
          // Full generation
          if (progress < 20) return 'Processing prompt...';
          if (progress < 40) return 'Generating story content...';
          if (progress < 60) return 'Creating character image...';
          if (progress < 80) return 'Creating background image...';
          if (progress < 95) return 'Compositing final scene...';
          return 'Finalizing results...';
        }
      });

      setStepProgress(prev => {
        const newProgress = { ...prev };
        if (generationType === 'story') {
          if (progress >= 50) newProgress.prompt = 100;
          if (progress >= 95) newProgress.story = 100;
        } else if (generationType === 'character') {
          if (progress >= 30) newProgress.prompt = 100;
          if (progress >= 95) newProgress.character = 100;
        } else if (generationType === 'background') {
          if (progress >= 30) newProgress.prompt = 100;
          if (progress >= 95) newProgress.background = 100;
        } else if (generationType === 'merge') {
          if (progress >= 30) newProgress.prompt = 100;
          if (progress >= 95) newProgress.merge = 100;
        } else {
          // Full generation
          if (progress >= 20) newProgress.prompt = 100;
          if (progress >= 40) newProgress.story = 100;
          if (progress >= 60) newProgress.character = 100;
          if (progress >= 80) newProgress.background = 100;
          if (progress >= 95) newProgress.composite = 100;
        }
        return newProgress;
      });
    }, 200);

    try {
      // Make API call to regular backend endpoint with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10 * 60 * 1000); // 10 minutes timeout

      let response;
      if (generationType === 'merge') {
        // Handle file upload for merge images
        const formData = new FormData();
        formData.append('generation_type', generationType);
        if (mergeImages.image1) formData.append('image1', mergeImages.image1);
        if (mergeImages.image2) formData.append('image2', mergeImages.image2);
        
        response = await fetch(`${backendUrl}/api/generate-story/`, {
          method: 'POST',
          body: formData,
          signal: controller.signal
        });
      } else {
        // Handle text-based requests
        response = await fetch(`${backendUrl}/api/generate-story/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt_text: promptText,
          generation_type: generationType
          }),
          signal: controller.signal
      });
      }

      clearTimeout(timeoutId);

      // Clear intervals
      clearInterval(progressInterval);
      clearInterval(stepInterval);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Set progress to 100% when complete
      setProgress(100);
      setCurrentStep('Generation complete!');
      
      if (result.processing_status === 'completed') {
        setGenerationResult(result);
        setGenerationState('success');
      } else if (result.processing_status === 'failed') {
        throw new Error(result.error_messages?.[0] || 'Generation failed');
      } else {
        throw new Error('Unexpected response status');
      }

    } catch (err) {
      if (err.name === 'AbortError') {
        throw new Error('Generation timeout. The process is taking longer than expected.');
      }
      throw err;
    } finally {
      // Ensure intervals are cleared
      clearInterval(progressInterval);
      clearInterval(stepInterval);
    }
  };

  const handleRetry = () => {
    setGenerationState('idle');
    setError(null);
    setProgress(0);
    setGenerationResult(null);
    setCurrentStep('');
    setStepProgress({});
  };

  const handleReset = () => {
    setGenerationState('idle');
    setError(null);
    setProgress(0);
    setGenerationResult(null);
    setCurrentStep('');
    setStepProgress({});
    if (onReset) onReset();
  };

  const getErrorMessage = (error) => {
    if (error.includes('network') || error.includes('fetch')) {
      return 'Connection failed. Please check your internet connection and try again.';
    }
    if (error.includes('timeout')) {
      return 'Request timed out. The generation process is taking longer than expected.';
    }
    if (error.includes('500') || error.includes('Internal Server Error')) {
      return 'Server error occurred. Please try again in a few moments.';
    }
    return error;
  };

  const getErrorIcon = (error) => {
    if (error.includes('network') || error.includes('fetch')) {
      return '🌐';
    }
    if (error.includes('timeout')) {
      return '⏰';
    }
    if (error.includes('500') || error.includes('Internal Server Error')) {
      return '🔧';
    }
    return '❌';
  };

  const renderLoadingState = () => {
    const renderSteps = () => {
      if (generationType === 'story') {
        return (
          <>
            <div className={`step ${progress >= 30 ? 'active' : ''}`}>
              <div className="step-icon">📝</div>
              <div className="step-content">
                <span className="step-text">Processing prompt</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.prompt || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className={`step ${progress >= 60 ? 'active' : ''}`}>
              <div className="step-icon">📖</div>
              <div className="step-content">
                <span className="step-text">Generating story</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.story || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </>
        );
      } else if (generationType === 'character') {
        return (
          <>
            <div className={`step ${progress >= 20 ? 'active' : ''}`}>
              <div className="step-icon">📝</div>
              <div className="step-content">
                <span className="step-text">Processing prompt</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.prompt || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className={`step ${progress >= 60 ? 'active' : ''}`}>
              <div className="step-icon">👤</div>
              <div className="step-content">
                <span className="step-text">Creating character</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.character || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </>
        );
      } else if (generationType === 'background') {
        return (
          <>
            <div className={`step ${progress >= 20 ? 'active' : ''}`}>
              <div className="step-icon">📝</div>
              <div className="step-content">
                <span className="step-text">Processing prompt</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.prompt || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className={`step ${progress >= 60 ? 'active' : ''}`}>
              <div className="step-icon">🏞️</div>
              <div className="step-content">
                <span className="step-text">Creating background</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.background || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </>
        );
      } else if (generationType === 'merge') {
        return (
          <>
            <div className={`step ${progress >= 30 ? 'active' : ''}`}>
              <div className="step-icon">📷</div>
              <div className="step-content">
                <span className="step-text">Processing images</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.prompt || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className={`step ${progress >= 60 ? 'active' : ''}`}>
              <div className="step-icon">🔄</div>
              <div className="step-content">
                <span className="step-text">Merging images</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.merge || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </>
        );
      } else {
        // Full generation
        return (
          <>
            <div className={`step ${progress >= 20 ? 'active' : ''}`}>
              <div className="step-icon">📝</div>
              <div className="step-content">
                <span className="step-text">Processing prompt</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.prompt || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className={`step ${progress >= 40 ? 'active' : ''}`}>
              <div className="step-icon">📖</div>
              <div className="step-content">
                <span className="step-text">AI generation</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.story || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className={`step ${progress >= 60 ? 'active' : ''}`}>
              <div className="step-icon">👤</div>
              <div className="step-content">
                <span className="step-text">Creating images</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.character || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className={`step ${progress >= 80 ? 'active' : ''}`}>
              <div className="step-icon">🏞️</div>
              <div className="step-content">
                <span className="step-text">Finalizing results</span>
                <div className="step-progress">
                  <div className="step-progress-bar">
                    <div 
                      className="step-progress-fill" 
                      style={{ width: `${stepProgress.composite || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </>
        );
      }
    };

    return (
    <div className="generation-loading">
      <div className="loading-header">
          <h3>Generating Your {getGenerationTypeTitle()}</h3>
          <p className="current-step">{currentStep}</p>
          {useStreaming && (
            <div className="streaming-status">
              <span className="status-badge streaming">🔄 Real-time updates</span>
            </div>
          )}
          {!useStreaming && (
            <div className="streaming-status">
              <span className="status-badge fallback">📡 Standard mode</span>
            </div>
          )}
      </div>
        
        <div className="loading-spinner"></div>
      
      <div className="progress-container">
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress}%` }}
          ></div>
        </div>
          <div className="progress-text">{Math.round(progress)}%</div>
      </div>

              <div className="loading-steps">
          {renderSteps()}
        </div>

      <div className="loading-tips">
          <p><strong>💡 Tip:</strong> This process may take several minutes as AI models generate your content.</p>
          <button className="cancel-button" onClick={cancelGeneration}>
            🚫 Cancel Generation
          </button>
      </div>
    </div>
  );
  };

  const getGenerationTypeTitle = () => {
    switch (generationType) {
      case 'story': return 'Story';
      case 'character': return 'Character Image';
      case 'background': return 'Background Image';
      case 'merge': return 'Merged Image';
      case 'full': return 'Story with Images';
      default: return 'Content';
    }
  };

  const renderContent = () => {
    switch (generationState) {
      case 'loading':
        return renderLoadingState();
      
      case 'success':
        return (
          <StoryOutputDisplay 
            generationResult={generationResult}
            isLoading={false}
            error={null}
          />
        );
      
      case 'error':
        return (
          <div className="generation-error">
            <div className="error-content">
              <div className="error-icon">{getErrorIcon(error)}</div>
              <h3>Generation Failed</h3>
              <p className="error-message">{getErrorMessage(error)}</p>
              <div className="error-actions">
                <button className="retry-button" onClick={handleRetry}>
                  🔄 Try Again
                </button>
                <button className="reset-button" onClick={handleReset}>
                  🏠 Start Over
                </button>
              </div>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="generation-idle">
            <div className="idle-content">
              <div className="idle-icon">📝</div>
              <h3>Ready to Generate</h3>
              <p>Enter a prompt and select a generation type to begin.</p>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="story-generation-output">
      {renderContent()}
    </div>
  );
};

export default StoryGenerationOutput;

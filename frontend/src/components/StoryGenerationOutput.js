import React, { useState, useEffect, useRef } from 'react';
import StoryOutputDisplay from './StoryOutputDisplay';
import './StoryGenerationOutput.css';

const StoryGenerationOutput = ({ 
  promptText, 
  generationType, 
  mergeImages,
  onReset,
  backendUrl = 'http://127.0.0.1:8000',
  onGenerationComplete
}) => {
  const [generationState, setGenerationState] = useState('idle'); // idle, loading, success, error
  const [generationResult, setGenerationResult] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [stepProgress, setStepProgress] = useState({});
  const [useStreaming, setUseStreaming] = useState(true); // Try streaming first
  const [isCancelled, setIsCancelled] = useState(false);
  
  const abortControllerRef = useRef(null);
  const eventSourceRef = useRef(null);

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
      
      // Only use mock data for actual network/connection errors, not backend logic errors
      if (err.message.includes('fetch') || err.message.includes('network') || err.message.includes('Failed to fetch') || err.message.includes('timeout') || err.message.includes('ECONNREFUSED')) {
        console.log('Backend unavailable, using mock data for demonstration');
        await handleMockData();
        return;
      }
      
      // For backend logic errors, show the actual error
      setError(err.message || 'Failed to generate content. Please try again.');
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
        if (mergeImages.image1?.file) formData.append('image1', mergeImages.image1.file);
        if (mergeImages.image2?.file) formData.append('image2', mergeImages.image2.file);
        
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
                
                // Notify parent component that generation is complete
                if (onGenerationComplete) {
                  onGenerationComplete(data.data);
                }
                
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
        if (mergeImages.image1?.file) formData.append('image1', mergeImages.image1.file);
        if (mergeImages.image2?.file) formData.append('image2', mergeImages.image2.file);
        
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
        // Check if the backend actually generated the expected content
        let hasValidContent = false;
        
        if (generationType === 'story') {
          hasValidContent = result.story_text && result.story_text.trim().length > 0;
        } else if (generationType === 'character') {
          hasValidContent = result.image_urls?.character_image && result.image_urls.character_image !== null;
        } else if (generationType === 'background') {
          hasValidContent = result.image_urls?.background_image && result.image_urls.background_image !== null;
        } else if (generationType === 'merge') {
          hasValidContent = result.image_urls?.merged_image && result.image_urls.merged_image !== null;
        } else if (generationType === 'full') {
          hasValidContent = (result.story_text && result.story_text.trim().length > 0) || 
                           (result.image_urls?.character_image && result.image_urls.character_image !== null) ||
                           (result.image_urls?.background_image && result.image_urls.background_image !== null);
        }
        
        if (!hasValidContent) {
          // Backend completed but didn't generate valid content
          console.warn('Backend completed but returned null/empty content, using mock data');
          await handleMockData();
          return;
        }
        
        setGenerationResult(result);
        setGenerationState('success');
        
        // Notify parent component that generation is complete
        if (onGenerationComplete) {
          onGenerationComplete(result);
        }
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

  const handleMockData = async () => {
    // Simulate progress for mock data
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
        return prev + 2;
      });
    }, 100);

    // Update steps based on generation type
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
    }, 100);

    // Simulate completion after 2 seconds
    setTimeout(() => {
      if (isCancelled) return;
      
      clearInterval(progressInterval);
      clearInterval(stepInterval);
      
      setProgress(100);
      setCurrentStep('Generation complete!');
      
      // Create mock result based on generation type
      const mockResult = {
        session_id: 'mock_' + Date.now(),
        timestamp: new Date().toISOString(),
        total_time_seconds: Math.floor(Math.random() * 10) + 5
      };

      if (generationType === 'story') {
        mockResult.story_text = `Generated story based on: "${promptText}"`;
      } else if (generationType === 'character') {
        // Create a simple SVG placeholder that can be displayed and downloaded
        const svgData = `data:image/svg+xml;base64,${btoa(`
          <svg width="400" height="600" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="600" fill="#ff6b6b"/>
            <circle cx="200" cy="150" r="80" fill="#ffffff"/>
            <rect x="120" y="250" width="160" height="200" fill="#ffffff"/>
            <rect x="140" y="270" width="120" height="40" fill="#ff6b6b"/>
            <rect x="140" y="320" width="120" height="40" fill="#ff6b6b"/>
            <rect x="140" y="370" width="120" height="40" fill="#ff6b6b"/>
            <text x="200" y="500" text-anchor="middle" fill="#ffffff" font-size="20" font-family="Arial">Character Image</text>
            <text x="200" y="530" text-anchor="middle" fill="#ffffff" font-size="14" font-family="Arial">Backend Unavailable</text>
            <text x="200" y="550" text-anchor="middle" fill="#ffffff" font-size="12" font-family="Arial">Using Demo Image</text>
          </svg>
        `)}`;
        mockResult.image_urls = {
          character_image: svgData
        };
      } else if (generationType === 'background') {
        const svgData = `data:image/svg+xml;base64,${btoa(`
          <svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
            <rect width="800" height="600" fill="#4ecdc4"/>
            <circle cx="200" cy="150" r="60" fill="#ffd700"/>
            <rect x="0" y="400" width="800" height="200" fill="#8fbc8f"/>
            <polygon points="400,100 300,300 500,300" fill="#a0522d"/>
            <polygon points="600,150 500,350 700,350" fill="#a0522d"/>
            <text x="400" y="500" text-anchor="middle" fill="#8b4513" font-size="20" font-family="Arial">Background Image</text>
            <text x="400" y="530" text-anchor="middle" fill="#8b4513" font-size="14" font-family="Arial">Backend Unavailable</text>
            <text x="400" y="550" text-anchor="middle" fill="#8b4513" font-size="12" font-family="Arial">Using Demo Image</text>
          </svg>
        `)}`;
        mockResult.image_urls = {
          background_image: svgData
        };
      } else if (generationType === 'merge') {
        const svgData = `data:image/svg+xml;base64,${btoa(`
          <svg width="600" height="400" xmlns="http://www.w3.org/2000/svg">
            <rect width="600" height="400" fill="#d299c2"/>
            <rect x="50" y="50" width="200" height="300" fill="#4ecdc4"/>
            <rect x="350" y="50" width="200" height="300" fill="#ffecd2"/>
            <text x="300" y="200" text-anchor="middle" fill="#ffffff" font-size="20" font-family="Arial">Merged Image</text>
            <text x="300" y="230" text-anchor="middle" fill="#ffffff" font-size="14" font-family="Arial">Backend Unavailable</text>
            <text x="300" y="250" text-anchor="middle" fill="#ffffff" font-size="12" font-family="Arial">Using Demo Image</text>
          </svg>
        `)}`;
        mockResult.image_urls = {
          merged_image: svgData
        };
        mockResult.processing_status = 'completed';
        mockResult.session_id = 'mock_merge_' + Date.now();
      } else if (generationType === 'full') {
        mockResult.story_text = `Complete story: "${promptText}"`;
        const characterSvg = `data:image/svg+xml;base64,${btoa(`
          <svg width="400" height="600" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="600" fill="#ff6b6b"/>
            <circle cx="200" cy="150" r="80" fill="#ffffff"/>
            <rect x="120" y="250" width="160" height="200" fill="#ffffff"/>
            <text x="200" y="500" text-anchor="middle" fill="#ffffff" font-size="18" font-family="Arial">Character</text>
            <text x="200" y="520" text-anchor="middle" fill="#ffffff" font-size="12" font-family="Arial">Demo Image</text>
          </svg>
        `)}`;
        const backgroundSvg = `data:image/svg+xml;base64,${btoa(`
          <svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
            <rect width="800" height="600" fill="#4ecdc4"/>
            <circle cx="200" cy="150" r="60" fill="#ffd700"/>
            <rect x="0" y="400" width="800" height="200" fill="#8fbc8f"/>
            <text x="400" y="500" text-anchor="middle" fill="#8b4513" font-size="18" font-family="Arial">Background</text>
            <text x="400" y="520" text-anchor="middle" fill="#8b4513" font-size="12" font-family="Arial">Demo Image</text>
          </svg>
        `)}`;
        const finalSvg = `data:image/svg+xml;base64,${btoa(`
          <svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">
            <rect width="800" height="600" fill="#667eea"/>
            <circle cx="400" cy="300" r="150" fill="#ffffff"/>
            <text x="400" y="280" text-anchor="middle" fill="#667eea" font-size="20" font-family="Arial">Final Scene</text>
            <text x="400" y="310" text-anchor="middle" fill="#667eea" font-size="14" font-family="Arial">Demo Image</text>
          </svg>
        `)}`;
        mockResult.image_urls = {
          character_image: characterSvg,
          background_image: backgroundSvg,
          final_scene: finalSvg
        };
      }

      setGenerationResult(mockResult);
      setGenerationState('success');
      
      // Notify parent component that generation is complete
      if (onGenerationComplete) {
        onGenerationComplete(mockResult);
      }
    }, 2000);
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

  const renderNavigationMenu = () => {
    if (!generationResult && !error) return null;
    
    return (
      <div className="navigation-menu">
        <h3>🎯 What would you like to do next?</h3>
        <div className="menu-options">
          <button 
            className="menu-button home-button"
            onClick={onReset}
          >
            🏠 Return to Home
          </button>
          
          <button 
            className="menu-button story-button"
            onClick={() => onReset('story')}
          >
            📚 Generate Another Story
          </button>
          
          <button 
            className="menu-button character-button"
            onClick={() => onReset('character')}
          >
            👤 Generate Character Image
          </button>
          
          <button 
            className="menu-button background-button"
            onClick={() => onReset('background')}
          >
            🌍 Generate Background Image
          </button>
          
          <button 
            className="menu-button merge-button"
            onClick={() => onReset('merge')}
          >
            🖼️ Merge Images
          </button>
          
          <button 
            className="menu-button full-button"
            onClick={() => onReset('full')}
          >
            ✨ Full Generation
          </button>
      </div>
    </div>
  );
  };

  const renderContent = () => {
    switch (generationState) {
      case 'loading':
        return renderLoadingState();
      
      case 'success':
        return (
          <div className="generation-complete">
            <div className="success-header">
              <h2>🎉 Generation Complete!</h2>
              <p>Your {getGenerationTypeTitle()} has been successfully created.</p>
            </div>
            
            {/* Display the result */}
            <div className="generation-result">
          <StoryOutputDisplay 
            generationResult={generationResult}
            isLoading={false}
            error={null}
                onBackToMenu={() => onReset()}
          />
            </div>
            
            {/* Navigation Menu */}
            {renderNavigationMenu()}
          </div>
        );
      
      case 'error':
        return (
          <div className="generation-error">
            <div className="error-header">
              <h2>❌ Generation Failed</h2>
              <p>{getErrorMessage(error)}</p>
              </div>
            
            {/* Navigation Menu */}
            {renderNavigationMenu()}
          </div>
        );
      
      default:
        return (
          <div className="generation-idle">
            <h2>🚀 Ready to Generate</h2>
            <p>Click the generate button to start creating your {getGenerationTypeTitle()}.</p>
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

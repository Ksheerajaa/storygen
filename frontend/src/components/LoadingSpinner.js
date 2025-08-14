import React from 'react';

/**
 * Professional loading spinner component with progress indicators
 * Supports different sizes, types, and progress states
 */
const LoadingSpinner = ({ 
  size = 'medium', 
  type = 'spinner', 
  progress = null, 
  text = 'Loading...',
  showProgress = false,
  className = ''
}) => {
  // Size classes
  const sizeClasses = {
    small: 'spinner-border-sm',
    medium: 'spinner-border',
    large: 'spinner-border',
    xl: 'spinner-border'
  };

  // Size dimensions
  const sizeStyles = {
    small: { width: '1rem', height: '1rem' },
    medium: { width: '2rem', height: '2rem' },
    large: { width: '3rem', height: '3rem' },
    xl: { width: '4rem', height: '4rem' }
  };

  // Type variants
  const renderSpinner = () => {
    switch (type) {
      case 'dots':
        return (
          <div className="loading-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        );
      
      case 'pulse':
        return (
          <div className="loading-pulse">
            <div className="pulse-circle"></div>
          </div>
        );
      
      case 'bars':
        return (
          <div className="loading-bars">
            <div className="bar"></div>
            <div className="bar"></div>
            <div className="bar"></div>
            <div className="bar"></div>
          </div>
        );
      
      case 'spinner':
      default:
        return (
          <div 
            className={`${sizeClasses[size]} text-primary`} 
            style={sizeStyles[size]}
            role="status"
          >
            <span className="visually-hidden">Loading...</span>
          </div>
        );
    }
  };

  return (
    <div className={`loading-container text-center ${className}`}>
      {/* Main spinner */}
      <div className="mb-3">
        {renderSpinner()}
      </div>

      {/* Loading text */}
      {text && (
        <div className="loading-text text-muted mb-2">
          {text}
        </div>
      )}

      {/* Progress bar */}
      {showProgress && progress !== null && (
        <div className="progress-container">
          <div className="progress" style={{ height: '6px' }}>
            <div 
              className="progress-bar bg-primary" 
              role="progressbar" 
              style={{ width: `${progress}%` }}
              aria-valuenow={progress} 
              aria-valuemin="0" 
              aria-valuemax="100"
            ></div>
          </div>
          <small className="text-muted mt-1 d-block">
            {Math.round(progress)}% complete
          </small>
        </div>
      )}

      {/* Progress percentage */}
      {progress !== null && !showProgress && (
        <div className="progress-percentage">
          <span className="badge bg-primary fs-6">
            {Math.round(progress)}%
          </span>
        </div>
      )}
    </div>
  );
};

/**
 * Story generation progress component
 * Shows step-by-step progress with custom messages
 */
export const StoryProgressSpinner = ({ currentStep, totalSteps, stepMessage, overallProgress }) => {
  const steps = [
    'Analyzing prompt...',
    'Generating story...',
    'Creating character image...',
    'Creating background image...',
    'Processing images...',
    'Compositing final scene...',
    'Finalizing results...'
  ];

  const currentStepText = stepMessage || steps[Math.min(currentStep, steps.length - 1)] || 'Processing...';
  const progressPercentage = overallProgress || ((currentStep / totalSteps) * 100);

  return (
    <div className="story-progress-container text-center p-4">
      {/* Progress indicator */}
      <div className="progress-circle mb-4">
        <div className="progress-circle-inner">
          <span className="progress-percentage-large">
            {Math.round(progressPercentage)}%
          </span>
        </div>
      </div>

      {/* Current step */}
      <h5 className="text-primary mb-3">{currentStepText}</h5>

      {/* Step progress */}
      <div className="step-progress mb-3">
        <div className="d-flex justify-content-between mb-2">
          <small className="text-muted">Step {currentStep} of {totalSteps}</small>
          <small className="text-muted">{Math.round(progressPercentage)}%</small>
        </div>
        <div className="progress" style={{ height: '8px' }}>
          <div 
            className="progress-bar bg-primary" 
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
      </div>

      {/* Step list */}
      <div className="step-list text-start">
        {steps.map((step, index) => (
          <div 
            key={index} 
            className={`step-item d-flex align-items-center mb-2 ${
              index < currentStep ? 'completed' : 
              index === currentStep ? 'current' : 'pending'
            }`}
          >
            <div className={`step-icon me-2 ${
              index < currentStep ? 'bg-success' : 
              index === currentStep ? 'bg-primary' : 'bg-secondary'
            }`}>
              {index < currentStep ? '✓' : index === currentStep ? '●' : '○'}
            </div>
            <small className={index < currentStep ? 'text-success' : 
                           index === currentStep ? 'text-primary' : 'text-muted'}>
              {step}
            </small>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LoadingSpinner;

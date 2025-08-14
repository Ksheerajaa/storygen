import React, { useState, useRef, useEffect } from 'react';
import './AudioInput.css';

const AudioInput = ({ onTranscriptionComplete, backendUrl = 'http://127.0.0.1:8000' }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [audioFile, setAudioFile] = useState(null);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recognitionRef = useRef(null);

  // Initialize Web Speech API
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';
      
      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }
        
        setTranscription(finalTranscript + interimTranscript);
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setError(`Speech recognition error: ${event.error}`);
        setIsRecording(false);
      };
      
      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
  }, []);

  // Start real-time speech recognition
  const startRecording = () => {
    if (!recognitionRef.current) {
      setError('Speech recognition not supported in this browser');
      return;
    }
    
    try {
      setError('');
      setTranscription('');
      recognitionRef.current.start();
      setIsRecording(true);
    } catch (err) {
      setError(`Failed to start recording: ${err.message}`);
    }
  };

  // Stop real-time speech recognition
  const stopRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  // Handle file upload
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/wave'];
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a valid audio file (.wav, .mp3)');
      return;
    }
    
    // Validate file size (max 25MB)
    if (file.size > 25 * 1024 * 1024) {
      setError('File size must be less than 25MB');
      return;
    }
    
    setAudioFile(file);
    setError('');
    setTranscription('');
  };

  // Transcribe uploaded audio file
  const transcribeAudioFile = async () => {
    if (!audioFile) return;
    
    setIsProcessing(true);
    setError('');
    setUploadProgress(0);
    
    try {
      const formData = new FormData();
      formData.append('audio_file', audioFile);
      
      const response = await fetch(`${backendUrl}/api/transcribe-audio/`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      
      if (result.success) {
        setTranscription(result.transcription);
        onTranscriptionComplete(result.transcription);
      } else {
        throw new Error(result.error || 'Transcription failed');
      }
      
    } catch (err) {
      setError(`Transcription failed: ${err.message}`);
    } finally {
      setIsProcessing(false);
      setUploadProgress(0);
    }
  };

  // Submit transcription to parent component
  const handleSubmitTranscription = () => {
    if (transcription.trim()) {
      onTranscriptionComplete(transcription);
    }
  };

  // Clear all input
  const handleClear = () => {
    setTranscription('');
    setAudioFile(null);
    setError('');
    setUploadProgress(0);
    if (isRecording) {
      stopRecording();
    }
  };

  return (
    <div className="audio-input-container">


      {/* Real-time Speech Recording */}
      <div className="recording-section">
        <h4>Voice Input</h4>
        <div className="recording-controls">
          {!isRecording ? (
            <button 
              className="record-button start"
              onClick={startRecording}
              disabled={isProcessing}
            >
              🎤 Start Recording
            </button>
          ) : (
            <button 
              className="record-button stop"
              onClick={stopRecording}
            >
              ⏹️ Stop Recording
            </button>
          )}
          
          {isRecording && (
            <div className="recording-indicator">
              <div className="pulse-dot"></div>
              <span>Recording...</span>
            </div>
          )}
        </div>
        
        {transcription && (
          <div className="transcription-preview">
            <h5>Transcription Preview:</h5>
            <div className="transcription-text">
              {transcription}
            </div>
            <div className="transcription-actions">
              <button 
                className="submit-button"
                onClick={handleSubmitTranscription}
              >
                ✅ Use This Text
              </button>
              <button 
                className="clear-button"
                onClick={handleClear}
              >
                🗑️ Clear
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Audio File Upload */}
      <div className="upload-section">
        <h4>File Upload</h4>
        <div className="file-upload-area">
          <input
            type="file"
            accept=".wav,.mp3,.mpeg,.wave"
            onChange={handleFileUpload}
            disabled={isProcessing}
            id="audio-file-input"
          />
          <label htmlFor="audio-file-input" className="file-upload-label">
            {audioFile ? `📁 ${audioFile.name}` : '📁 Choose audio file (.wav, .mp3)'}
          </label>
        </div>
        
        {audioFile && (
          <div className="file-info">
            <p>File: {audioFile.name}</p>
            <p>Size: {(audioFile.size / 1024 / 1024).toFixed(2)} MB</p>
            <button 
              className="transcribe-button"
              onClick={transcribeAudioFile}
              disabled={isProcessing}
            >
              {isProcessing ? '🔄 Transcribing...' : '🎵 Transcribe Audio'}
            </button>
          </div>
        )}
        
        {isProcessing && (
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <div className="progress-text">Processing audio...</div>
          </div>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <span className="error-icon">❌</span>
          {error}
        </div>
      )}


    </div>
  );
};

export default AudioInput;

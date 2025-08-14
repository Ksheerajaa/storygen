import React, { useState, useRef, useEffect } from 'react';
import './AudioInput.css';

const AudioInput = ({ promptText, setPromptText, placeholder = "Describe what you want to generate...", backendUrl = 'http://127.0.0.1:8000' }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [error, setError] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [audioFile, setAudioFile] = useState(null);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const recognitionRef = useRef(null);

  // Update promptText when transcription changes
  useEffect(() => {
    if (transcription && setPromptText) {
      setPromptText(transcription);
    }
  }, [transcription, setPromptText]);

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
        // onTranscriptionComplete(result.transcription); // This line was removed as per new_code
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
      // onTranscriptionComplete(transcription); // This line was removed as per new_code
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
    <div className="audio-input">
      <div className="input-section">
        <h4>Text Input</h4>
        <textarea
          value={promptText || ''}
          onChange={(e) => setPromptText(e.target.value)}
          placeholder={placeholder}
          rows="3"
          className="text-input"
        />
      </div>

      <div className="input-section">
        <h4>Voice Input</h4>
        <div className="voice-controls">
          {!isRecording ? (
            <button 
              type="button"
              onClick={startRecording}
              className="record-button"
              disabled={isProcessing}
            >
              🎤 Start Recording
            </button>
          ) : (
            <button 
              type="button"
              onClick={stopRecording}
              className="stop-button"
            >
              ⏹️ Stop Recording
            </button>
          )}
        </div>
        
        {transcription && (
          <div className="transcription-display">
            <h5>Voice Transcription:</h5>
            <p>{transcription}</p>
          </div>
        )}
      </div>

      <div className="input-section">
        <h4>Audio File Upload</h4>
        <div className="file-upload">
          <input
            type="file"
            accept="audio/*"
            onChange={handleFileUpload}
            className="file-input"
            id="audio-file"
          />
          <label htmlFor="audio-file" className="file-label">
            📁 Choose Audio File
          </label>
        </div>
        
        {audioFile && (
          <div className="file-info">
            <p>Selected: {audioFile.name}</p>
            <button 
              onClick={transcribeAudioFile}
              disabled={isProcessing}
              className="process-button"
            >
              {isProcessing ? '🔄 Processing...' : '🎵 Process Audio'}
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
        </div>
      )}

      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p>Uploading: {uploadProgress}%</p>
        </div>
      )}
    </div>
  );
};

export default AudioInput;

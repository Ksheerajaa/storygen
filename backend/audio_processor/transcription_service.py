import os
import time
import logging
from pathlib import Path
import tempfile
import subprocess
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


class AudioTranscriptionService:
    """Service for transcribing audio files using Whisper"""
    
    def __init__(self):
        self.whisper_model = getattr(settings, 'WHISPER_MODEL', 'openai/whisper-small')
        self.use_openai_whisper = getattr(settings, 'USE_OPENAI_WHISPER', False)
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        # Check if we can use Whisper
        self.whisper_available = self._check_whisper_availability()
        
        if not self.whisper_available:
            logger.warning("Whisper not available, transcription will use fallback methods")
    
    def _check_whisper_availability(self):
        """Check if Whisper is available for transcription"""
        try:
            if self.use_openai_whisper and self.openai_api_key:
                # Check OpenAI Whisper availability
                import openai
                return True
            else:
                # Check Hugging Face Whisper availability
                try:
                    import transformers
                    from transformers import WhisperProcessor, WhisperForConditionalGeneration
                    return True
                except ImportError:
                    logger.warning("Transformers library not available for Hugging Face Whisper")
                    return False
        except Exception as e:
            logger.error(f"Error checking Whisper availability: {e}")
            return False
    
    def transcribe_audio(self, audio_file_path, audio_file_name):
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_file_path: Path to the audio file
            audio_file_name: Original filename
            
        Returns:
            dict: Transcription result with success status and text
        """
        start_time = time.time()
        
        try:
            if not self.whisper_available:
                return self._fallback_transcription(audio_file_path, audio_file_name)
            
            # Convert audio to WAV if needed for better Whisper compatibility
            wav_path = self._ensure_wav_format(audio_file_path, audio_file_name)
            
            if self.use_openai_whisper and self.openai_api_key:
                transcription = self._transcribe_with_openai_whisper(wav_path)
            else:
                transcription = self._transcribe_with_huggingface_whisper(wav_path)
            
            processing_time = time.time() - start_time
            
            # Clean up temporary files
            if wav_path != audio_file_path:
                try:
                    os.remove(wav_path)
                except:
                    pass
            
            return {
                'success': True,
                'transcription': transcription,
                'processing_time': processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Transcription failed: {e}")
            
            return {
                'success': False,
                'transcription': '',
                'error': str(e),
                'processing_time': processing_time
            }
    
    def _ensure_wav_format(self, audio_file_path, audio_file_name):
        """Convert audio to WAV format if needed"""
        if audio_file_name.lower().endswith('.wav'):
            return audio_file_path
        
        try:
            # Use ffmpeg to convert to WAV
            wav_path = audio_file_path.replace('.mp3', '.wav').replace('.mpeg', '.wav')
            
            # Check if ffmpeg is available
            try:
                subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                logger.warning("ffmpeg not available, using original file format")
                return audio_file_path
            
            # Convert to WAV
            cmd = [
                'ffmpeg', '-i', audio_file_path,
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',  # Overwrite output file
                wav_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, check=True)
            
            if os.path.exists(wav_path):
                return wav_path
            else:
                logger.warning("ffmpeg conversion failed, using original file")
                return audio_file_path
                
        except Exception as e:
            logger.warning(f"Audio conversion failed: {e}, using original file")
            return audio_file_path
    
    def _transcribe_with_openai_whisper(self, audio_file_path):
        """Transcribe using OpenAI Whisper API"""
        try:
            import openai
            
            openai.api_key = self.openai_api_key
            
            with open(audio_file_path, 'rb') as audio_file:
                response = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            return response.strip()
            
        except ImportError:
            raise Exception("OpenAI library not available")
        except Exception as e:
            raise Exception(f"OpenAI Whisper transcription failed: {e}")
    
    def _transcribe_with_huggingface_whisper(self, audio_file_path):
        """Transcribe using Hugging Face Whisper model"""
        try:
            from transformers import WhisperProcessor, WhisperForConditionalGeneration
            import torch
            import librosa
            
            # Load model and processor
            model_name = self.whisper_model
            processor = WhisperProcessor.from_pretrained(model_name)
            model = WhisperForConditionalGeneration.from_pretrained(model_name)
            
            # Load and preprocess audio
            audio, sample_rate = librosa.load(audio_file_path, sr=16000)
            
            # Process audio
            input_features = processor(
                audio, 
                sampling_rate=sample_rate, 
                return_tensors="pt"
            ).input_features
            
            # Generate transcription
            predicted_ids = model.generate(input_features)
            transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
            
            return transcription.strip()
            
        except ImportError as e:
            raise Exception(f"Required libraries not available: {e}")
        except Exception as e:
            raise Exception(f"Hugging Face Whisper transcription failed: {e}")
    
    def _fallback_transcription(self, audio_file_path, audio_file_name):
        """Fallback transcription method when Whisper is not available"""
        logger.warning("Using fallback transcription method")
        
        # This is a placeholder - in a real implementation, you might:
        # 1. Use a different speech-to-text service
        # 2. Return a message asking user to type manually
        # 3. Use a simpler audio processing library
        
        return {
            'success': False,
            'transcription': '',
            'error': 'Audio transcription not available. Please type your story idea manually.',
            'processing_time': 0
        }


# Global instance
transcription_service = AudioTranscriptionService()

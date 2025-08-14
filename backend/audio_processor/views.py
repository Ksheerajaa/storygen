import os
import tempfile
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import AudioTranscription
from .serializers import (
    AudioTranscriptionRequestSerializer,
    AudioTranscriptionResponseSerializer
)
from .transcription_service import transcription_service

logger = logging.getLogger(__name__)


class AudioTranscriptionView(APIView):
    """API view for audio transcription"""
    
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        """Handle audio file upload and transcription"""
        try:
            # Validate request
            serializer = AudioTranscriptionRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'transcription': '',
                    'error': 'Invalid request data'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            audio_file = request.FILES.get('audio_file')
            if not audio_file:
                return Response({
                    'success': False,
                    'transcription': '',
                    'error': 'No audio file provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create transcription record
            transcription_record = AudioTranscription.objects.create(
                audio_file=audio_file,
                processing_status='processing'
            )
            
            try:
                # Save file to temporary location for processing
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                    for chunk in audio_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name
                
                # Transcribe audio
                result = transcription_service.transcribe_audio(
                    temp_file_path, 
                    audio_file.name
                )
                
                # Update transcription record
                if result['success']:
                    transcription_record.transcription = result['transcription']
                    transcription_record.processing_status = 'completed'
                    transcription_record.processing_time = result.get('processing_time', 0)
                else:
                    transcription_record.processing_status = 'failed'
                    transcription_record.error_message = result.get('error', 'Unknown error')
                    transcription_record.processing_time = result.get('processing_time', 0)
                
                transcription_record.save()
                
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                
                # Return response
                response_data = {
                    'success': result['success'],
                    'transcription': result.get('transcription', ''),
                    'error': result.get('error', ''),
                    'processing_time': result.get('processing_time', 0),
                    'transcription_id': str(transcription_record.id)
                }
                
                if result['success']:
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                # Update record with error
                transcription_record.processing_status = 'failed'
                transcription_record.error_message = str(e)
                transcription_record.save()
                
                logger.error(f"Transcription processing failed: {e}")
                
                return Response({
                    'success': False,
                    'transcription': '',
                    'error': f'Transcription processing failed: {str(e)}',
                    'processing_time': 0,
                    'transcription_id': str(transcription_record.id)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Audio transcription view error: {e}")
            return Response({
                'success': False,
                'transcription': '',
                'error': f'Server error: {str(e)}',
                'processing_time': 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def transcription_status(request, transcription_id):
    """Get status of a transcription request"""
    try:
        transcription = AudioTranscription.objects.get(id=transcription_id)
        
        return Response({
            'id': str(transcription.id),
            'processing_status': transcription.processing_status,
            'transcription': transcription.transcription,
            'error_message': transcription.error_message,
            'processing_time': transcription.processing_time,
            'created_at': transcription.created_at,
            'updated_at': transcription.updated_at,
            'file_name': transcription.file_name,
            'file_size_mb': transcription.file_size_mb
        })
        
    except AudioTranscription.DoesNotExist:
        return Response({
            'error': 'Transcription not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting transcription status: {e}")
        return Response({
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def transcription_list(request):
    """Get list of recent transcriptions"""
    try:
        transcriptions = AudioTranscription.objects.all()[:10]  # Last 10
        
        data = []
        for transcription in transcriptions:
            data.append({
                'id': str(transcription.id),
                'processing_status': transcription.processing_status,
                'file_name': transcription.file_name,
                'file_size_mb': transcription.file_size_mb,
                'created_at': transcription.created_at,
                'processing_time': transcription.processing_time
            })
        
        return Response(data)
        
    except Exception as e:
        logger.error(f"Error getting transcription list: {e}")
        return Response({
            'error': f'Server error: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

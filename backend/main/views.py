from django.shortcuts import render
from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.http import StreamingHttpResponse
from .models import Story, StoryGeneration, StorySession, GeneratedContent
from .serializers import StorySerializer, StoryGenerationSerializer, StorySessionSerializer
# Remove immediate imports of AI modules to prevent startup crashes
# from .pipelines.story_generator import StoryGeneratorPipeline
# from .pipelines.story_orchestrator import get_story_orchestrator
import uuid
import logging
import os
import time
import traceback
import json
from datetime import datetime
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class StoryViewSet(viewsets.ModelViewSet):
    """ViewSet for Story model"""
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new story using AI"""
        try:
            prompt = request.data.get('prompt', '')
            if not prompt:
                return Response(
                    {'error': 'Prompt is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Initialize the story generator pipeline
            pipeline = StoryGeneratorPipeline()
            
            if not pipeline.initialized:
                return Response(
                    {'error': 'AI pipeline not initialized'}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Generate the story
            result = pipeline.generate_story(prompt)
            
            if result['status'] == 'success':
                # Create a StoryGeneration record
                generation = StoryGeneration.objects.create(
                    prompt=prompt,
                    status='completed'
                )
                
                # Create the actual story
                story = Story.objects.create(
                    title=result['title'],
                    content=result['content'],
                    author=request.user if request.user.is_authenticated else None
                )
                
                # Link the generation to the story
                generation.generated_story = story
                generation.save()
                
                return Response({
                    'message': 'Story generated successfully',
                    'story': {
                        'id': story.id,
                        'title': story.title,
                        'content': story.content,
                        'character_desc': result.get('character_desc', ''),
                        'background_desc': result.get('background_desc', '')
                    },
                    'generation_id': generation.id
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': f'Story generation failed: {result.get("content", "Unknown error")}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def enhance(self, request, pk=None):
        """Enhance an existing story with additional details"""
        try:
            story = self.get_object()
            
            # Initialize the story generator pipeline
            pipeline = StoryGeneratorPipeline()
            
            if not pipeline.initialized:
                return Response(
                    {'error': 'AI pipeline not initialized'}, 
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Enhance the story
            result = pipeline.enhance_story(story.content)
            
            if result['status'] == 'success':
                # Update the story with enhanced content
                story.content = result['content']
                story.title = result['title']
                story.save()
                
                return Response({
                    'message': 'Story enhanced successfully',
                    'story': {
                        'id': story.id,
                        'title': story.title,
                        'content': story.content
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': f'Story enhancement failed: {result.get("content", "Unknown error")}'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StoryGenerationViewSet(viewsets.ModelViewSet):
    """ViewSet for StoryGeneration model"""
    queryset = StoryGeneration.objects.all()
    serializer_class = StoryGenerationSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class GenerateStoryView(APIView):
    """API view for generating stories with file uploads using StoryOrchestrator"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.AllowAny]  # Allow anyone to test for now
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
    
    def post(self, request):
        """Handle story generation requests"""
        try:
            # Lazy-load the story orchestrator to prevent startup crashes
            from .pipelines.story_orchestrator import get_story_orchestrator
            
            # Extract request data
            prompt_text = request.data.get('prompt_text', '')
            generation_type = request.data.get('generation_type', 'story')
            
            # Validate input based on generation type
            if generation_type == 'merge':
                # For merge, require two images
                image1 = request.FILES.get('image1')
                image2 = request.FILES.get('image2')
                if not image1 or not image2:
                    return Response({
                        'error': 'Both image1 and image2 are required for merge generation',
                        'timestamp': datetime.now().isoformat()
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # For other types, require prompt text
                if not prompt_text:
                    return Response({
                        'error': 'prompt_text is required for story generation',
                        'timestamp': datetime.now().isoformat()
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create session
            session = StorySession.objects.create(
                session_id=f"session_{uuid.uuid4().hex[:8]}",
                prompt_text=prompt_text or f"Merge images: {image1.name} + {image2.name}" if generation_type == 'merge' else prompt_text,
                status='in_progress'
            )
            
            # Get story orchestrator
            orchestrator = get_story_orchestrator()
            if not orchestrator:
                raise RuntimeError("Failed to initialize StoryOrchestrator")
            
            self.logger.info(f"Starting {generation_type} generation for prompt: {prompt_text[:50]}...")
            
            # Call orchestrator based on generation type
            if generation_type == 'story':
                result = orchestrator.generate_story_only(prompt_text, session.session_id)
            elif generation_type == 'character':
                result = orchestrator.generate_character_only(prompt_text, session.session_id)
            elif generation_type == 'background':
                result = orchestrator.generate_background_only(prompt_text, session.session_id)
            elif generation_type == 'merge':
                result = orchestrator.merge_images_only(prompt_text, session.session_id)
            else:
                # Full generation
                result = orchestrator.process_user_request(prompt_text, session.session_id)
            
            if result["status"] == "success":
                # Update session status
                session.status = 'completed'
                session.save()
                
                # Save results to GeneratedContent model
                try:
                    generated_content = self._save_generated_content(session, result)
                    self.logger.info(f"Generated content saved with ID: {generated_content.id}")
                except Exception as e:
                    self.logger.warning(f"Failed to save generated content: {e}")
                
                # Prepare response data
                try:
                    response_data = self._prepare_response_data(result, session, generation_type)
                    return Response(response_data, status=status.HTTP_200_OK)
                except Exception as e:
                    self.logger.error(f"Failed to prepare response data: {e}")
                    # Return basic success response
                    basic_response = {
                        'session_id': session.session_id,
                        'processing_status': 'completed',
                        'total_time_seconds': result.get('total_time_seconds', 0),
                        'timestamp': datetime.now().isoformat(),
                        'story_text': 'Generation completed successfully',
                        'character_description': '',
                        'background_description': '',
                        'image_urls': {}
                    }
                    return Response(basic_response, status=status.HTTP_200_OK)
                
            else:
                # Handle failed generation
                error_msg = result.get('error', 'Unknown error occurred')
                self.logger.error(f"{generation_type} generation failed: {error_msg}")
                
                # Update session status
                session.status = 'failed'
                session.save()
                
                return Response({
                    'error': error_msg,
                    'session_id': session.session_id,
                    'processing_status': 'failed',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            self.logger.error(f"Unexpected error in GenerateStoryView: {str(e)}", exc_info=True)
            return Response({
                'error': f'Unexpected error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _save_generated_content(self, session, result):
        """Save generated content to database"""
        try:
            # Extract file paths from result
            character_image_path = result['output_files'].get('character_image', '')
            background_image_path = result['output_files'].get('background_image', '')
            merged_image_path = result['output_files'].get('final_scene', '')
            
            # Create GeneratedContent record
            generated_content = GeneratedContent.objects.create(
                session=session,
                story_text=result['results']['story']['content'],
                character_description=result['results']['story']['character_descriptions'],
                background_description=result['results']['story']['background_descriptions'],
                character_image=self._save_image_to_model(character_image_path, 'characters/'),
                background_image=self._save_image_to_model(background_image_path, 'backgrounds/'),
                merged_image=self._save_image_to_model(merged_image_path, 'merged/'),
                processing_status='completed',
                error_messages=''
            )
            
            self.logger.info(f"Generated content saved with ID: {generated_content.id}")
            return generated_content
            
        except Exception as e:
            self.logger.error(f"Failed to save generated content: {str(e)}")
            raise
    
    def _prepare_response_data(self, result, session, generation_type):
        """Prepare response data based on generation type"""
        try:
            base_response = {
                'session_id': session.session_id,
                'processing_status': 'completed',
                'total_time_seconds': result.get('total_time_seconds', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            if generation_type == 'story':
                # Story-only generation
                return {
                    **base_response,
                    'story_text': result['results']['story']['content'],
                    'character_description': result['results']['story'].get('character_descriptions', ''),
                    'background_description': result['results']['story'].get('background_descriptions', ''),
                    'image_urls': {}
                }
                
            elif generation_type == 'character':
                # Character-only generation
                character_result = result['results'].get('character', {})
                return {
                    **base_response,
                    'story_text': '',
                    'character_description': character_result.get('description', ''),
                    'background_description': '',
                    'image_urls': {
                        'character_image': self._get_media_url(result['output_files'].get('character_image', ''))
                    }
                }
                
            elif generation_type == 'background':
                # Background-only generation
                background_result = result['results'].get('background', {})
                return {
                    **base_response,
                    'story_text': '',
                    'character_description': '',
                    'background_description': background_result.get('description', ''),
                    'image_urls': {
                        'background_image': self._get_media_url(result['output_files'].get('background_image', ''))
                    }
                }
                
            elif generation_type == 'merge':
                # Image merging
                return {
                    **base_response,
                    'story_text': result['results'].get('merge_info', 'Image merging completed successfully'),
                    'character_description': '',
                    'background_description': '',
                    'image_urls': {}
                }
                
            else:
                # Full generation (default)
                return {
                    **base_response,
                    'story_text': result['results']['story']['content'],
                    'character_description': result['results']['story'].get('character_descriptions', ''),
                    'background_description': result['results']['story'].get('background_descriptions', ''),
                    'image_urls': {
                        'character_image': self._get_media_url(result['output_files'].get('character_image', '')),
                        'background_image': self._get_media_url(result['output_files'].get('background_image', '')),
                        'merged_image': self._get_media_url(result['output_files'].get('final_scene', ''))
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Failed to prepare response data: {str(e)}")
            # Return basic error response
            return {
                'session_id': session.session_id,
                'processing_status': 'failed',
                'error_messages': [f'Failed to prepare response: {str(e)}'],
                'timestamp': datetime.now().isoformat()
            }

    def _save_image_to_model(self, file_path, upload_dir):
        """Save image file to Django model with proper media handling"""
        try:
            if not file_path or not os.path.exists(file_path):
                return None
            
            # Convert Windows path to proper format
            file_path = Path(file_path).resolve()
            
            # Create the upload directory if it doesn't exist
            media_root = Path('media')
            upload_path = media_root / upload_dir
            upload_path.mkdir(parents=True, exist_ok=True)
            
            # Copy file to media directory with proper name
            filename = f"{file_path.stem}_{uuid.uuid4().hex[:8]}{file_path.suffix}"
            destination = upload_path / filename
            
            import shutil
            shutil.copy2(file_path, destination)
            
            # Return the relative path for the model
            return f"{upload_dir}{filename}"
            
        except Exception as e:
            self.logger.error(f"Failed to save image {file_path}: {str(e)}")
            return None
    
    def _get_media_url(self, file_path):
        """Convert file path to media URL"""
        if not file_path:
            return None
        
        # Convert to relative path from media root
        if file_path.startswith('media/'):
            return f"/media/{file_path[6:]}"
        elif file_path.startswith('characters/') or file_path.startswith('backgrounds/') or file_path.startswith('merged/'):
            return f"/media/{file_path}"
        else:
            return None


# Debug endpoints for testing individual pipeline components
class TestStoryView(APIView):
    """Debug endpoint for testing story generation only"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Test story generation pipeline"""
        try:
            prompt_text = request.data.get('prompt_text', 'A brave knight discovers a magical forest')
            
            logger.info(f"Testing story generation with prompt: {prompt_text}")
            
            # Test story generator
            from .pipelines.story_generator import get_story_generator
            
            generator = get_story_generator()
            if not generator:
                return Response({
                    'error': 'Story generator not initialized'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            start_time = time.time()
            result = generator.generate_story(prompt_text)
            generation_time = time.time() - start_time
            
            if result and 'content' in result:
                return Response({
                    'status': 'success',
                    'test_type': 'story_generation',
                    'prompt': prompt_text,
                    'generation_time_seconds': round(generation_time, 2),
                    'story_length': len(result['content']),
                    'character_desc_length': len(result.get('character_desc', '')),
                    'background_desc_length': len(result.get('background_desc', '')),
                    'result': result
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'failed',
                    'test_type': 'story_generation',
                    'error': 'Story generation failed',
                    'result': result
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'test_type': 'story_generation',
                'error': str(e),
                'traceback': traceback.format_exc() if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestImagesView(APIView):
    """Debug endpoint for testing image generation and processing"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Test image generation and processing pipeline"""
        try:
            character_desc = request.data.get('character_desc', 'A brave knight in shining armor')
            background_desc = request.data.get('background_desc', 'A magical forest with ancient trees')
            
            logger.info(f"Testing image generation with descriptions:")
            logger.info(f"  Character: {character_desc}")
            logger.info(f"  Background: {background_desc}")
            
            # Test image generator
            from .pipelines.image_generator import get_image_generator
            
            generator = get_image_generator()
            if not generator:
                return Response({
                    'error': 'Image generator not initialized'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Create test output directory
            test_dir = Path('test_output')
            test_dir.mkdir(exist_ok=True)
            
            # Test character image generation
            start_time = time.time()
            character_path = test_dir / f'test_character_{int(time.time())}.png'
            
            char_result = generator.generate_character_image(character_desc, str(character_path))
            char_time = time.time() - start_time
            
            # Test background image generation
            start_time = time.time()
            background_path = test_dir / f'test_background_{int(time.time())}.png'
            
            bg_result = generator.generate_background_image(background_desc, str(background_path))
            bg_time = time.time() - start_time
            
            # Test image processing
            from .pipelines.image_processor import get_image_processor
            processor = get_image_processor()
            
            if char_result and bg_result and character_path.exists() and background_path.exists():
                # Test background removal
                start_time = time.time()
                char_no_bg = test_dir / f'char_no_bg_{int(time.time())}.png'
                bg_removal_result = processor.remove_background(str(character_path), str(char_no_bg))
                bg_removal_time = time.time() - start_time
                
                # Test image merging
                start_time = time.time()
                merged_path = test_dir / f'merged_{int(time.time())}.png'
                merge_result = processor.merge_images(str(char_no_bg), str(background_path), str(merged_path))
                merge_time = time.time() - start_time
                
                # Collect file information
                files_info = {}
                for file_path, file_type in [
                    (character_path, 'character_image'),
                    (background_path, 'background_image'),
                    (char_no_bg, 'character_no_background'),
                    (merged_path, 'merged_image')
                ]:
                    if file_path.exists():
                        files_info[file_type] = {
                            'path': str(file_path),
                            'size_bytes': file_path.stat().st_size,
                            'exists': True
                        }
                    else:
                        files_info[file_type] = {
                            'exists': False
                        }
                
                return Response({
                    'status': 'success',
                    'test_type': 'image_generation_and_processing',
                    'character_description': character_desc,
                    'background_description': background_desc,
                    'timing': {
                        'character_generation': round(char_time, 2),
                        'background_generation': round(bg_time, 2),
                        'background_removal': round(bg_removal_time, 2),
                        'image_merging': round(merge_time, 2),
                        'total_time': round(char_time + bg_time + bg_removal_time + merge_time, 2)
                    },
                    'files': files_info,
                    'results': {
                        'character_generation': char_result,
                        'background_generation': bg_result,
                        'background_removal': bg_removal_result,
                        'image_merging': merge_result
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'failed',
                    'test_type': 'image_generation_and_processing',
                    'error': 'Image generation failed',
                    'character_result': char_result,
                    'background_result': bg_result,
                    'files_exist': {
                        'character': character_path.exists(),
                        'background': background_path.exists()
                    }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'test_type': 'image_generation_and_processing',
                'error': str(e),
                'traceback': traceback.format_exc() if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestOrchestratorView(APIView):
    """Debug endpoint for testing complete orchestrator"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Test complete orchestrator pipeline"""
        try:
            prompt_text = request.data.get('prompt_text', 'A brave knight discovers a magical forest')
            
            logger.info(f"Testing complete orchestrator with prompt: {prompt_text}")
            
            # Test orchestrator
            orchestrator = get_story_orchestrator()
            if not orchestrator:
                return Response({
                    'error': 'Orchestrator not initialized'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Create test session
            session_id = f"test_orchestrator_{int(time.time())}"
            
            start_time = time.time()
            result = orchestrator.process_user_request(prompt_text, session_id)
            total_time = time.time() - start_time
            
            if result and result.get('status') == 'success':
                # Check output files
                output_files = result.get('output_files', {})
                files_info = {}
                
                for file_type, file_path in output_files.items():
                    if file_path and Path(file_path).exists():
                        files_info[file_type] = {
                            'path': str(file_path),
                            'size_bytes': Path(file_path).stat().st_size,
                            'exists': True
                        }
                    else:
                        files_info[file_type] = {
                            'exists': False
                        }
                
                return Response({
                    'status': 'success',
                    'test_type': 'complete_orchestrator',
                    'prompt': prompt_text,
                    'session_id': session_id,
                    'total_time_seconds': round(total_time, 2),
                    'story_length': len(result['results']['story']['content']),
                    'files': files_info,
                    'result_summary': {
                        'story_generated': 'content' in result['results']['story'],
                        'character_description': 'character_descriptions' in result['results']['story'],
                        'background_description': 'background_descriptions' in result['results']['story'],
                        'character_image': 'character_image' in output_files,
                        'background_image': 'background_image' in output_files,
                        'final_scene': 'final_scene' in output_files
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'status': 'failed',
                    'test_type': 'complete_orchestrator',
                    'error': result.get('error', 'Unknown error'),
                    'result': result
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'test_type': 'complete_orchestrator',
                'error': str(e),
                'traceback': traceback.format_exc() if settings.DEBUG else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """Simple health check endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """Check if the backend is running and orchestrator is available"""
        try:
            # Lazy-load the story orchestrator to prevent startup crashes
            from .pipelines.story_orchestrator import get_story_orchestrator
            
            # Check if orchestrator can be initialized
            orchestrator = get_story_orchestrator()
            if orchestrator:
                # Check if running in fallback mode
                has_ai_components = (
                    hasattr(orchestrator, 'story_generator') and 
                    orchestrator.story_generator and 
                    hasattr(orchestrator.story_generator, 'initialized') and 
                    orchestrator.story_generator.initialized
                )
                
                if has_ai_components:
                    return Response({
                        'status': 'healthy',
                        'message': 'Backend is running with full AI capabilities',
                        'mode': 'full_ai',
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return Response({
                        'status': 'healthy',
                        'message': 'Backend is running in fallback mode (AI components not available)',
                        'mode': 'fallback',
                        'timestamp': datetime.now().isoformat()
                    })
            else:
                return Response({
                    'status': 'unhealthy',
                    'message': 'Orchestrator not available',
                    'timestamp': datetime.now().isoformat()
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return Response({
                'status': 'unhealthy',
                'message': f'Health check failed: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StreamingStoryGenerationView(APIView):
    """API view for streaming story generation progress using Server-Sent Events"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.AllowAny]  # Allow anyone to test for now
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
    
    def post(self, request):
        """Handle streaming story generation requests"""
        try:
            # Lazy-load the story orchestrator to prevent startup crashes
            from .pipelines.story_orchestrator import get_story_orchestrator
            
            # Extract request data
            prompt_text = request.data.get('prompt_text', '')
            generation_type = request.data.get('generation_type', 'story')
            
            # Validate input based on generation type
            if generation_type == 'merge':
                # For merge, require two images
                image1 = request.FILES.get('image1')
                image2 = request.FILES.get('image2')
                if not image1 or not image2:
                    return Response({
                        'error': 'Both image1 and image2 are required for merge generation',
                        'timestamp': datetime.now().isoformat()
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # For other types, require prompt text
                if not prompt_text:
                    return Response({
                        'error': 'prompt_text is required for story generation',
                        'timestamp': datetime.now().isoformat()
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create session
            session = StorySession.objects.create(
                session_id=f"session_{uuid.uuid4().hex[:8]}",
                prompt_text=prompt_text or f"Merge images: {image1.name} + {image2.name}" if generation_type == 'merge' else prompt_text,
                status='in_progress'
            )
            
            # Get story orchestrator
            orchestrator = get_story_orchestrator()
            if not orchestrator:
                raise RuntimeError("Failed to initialize StoryOrchestrator")
            
            self.logger.info(f"Starting streaming {generation_type} generation for prompt: {prompt_text[:50]}...")
            
            # Return streaming response
            return StreamingHttpResponse(
                self._generate_stream(session, prompt_text, generation_type, request),
                content_type='text/event-stream'
            )
            
        except Exception as e:
            self.logger.error(f"Unexpected error in StreamingStoryGenerationView: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Unexpected error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_stream(self, session, prompt_text, generation_type, request):
        """Generate streaming response with real-time progress updates"""
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Initializing generation...', 'progress': 0})}\n\n"
            
            # Initialize StoryOrchestrator
            yield f"data: {json.dumps({'type': 'status', 'message': 'Initializing AI models...', 'progress': 10})}\n\n"
            
            orchestrator = get_story_orchestrator()
            if not orchestrator:
                raise RuntimeError("Failed to initialize StoryOrchestrator")
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'AI models ready, starting generation...', 'progress': 20})}\n\n"
            
            # Call orchestrator based on generation type with progress callbacks
            if generation_type == 'story':
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating story content...', 'progress': 30})}\n\n"
                result = orchestrator.generate_story_only(prompt_text, session.session_id)
            elif generation_type == 'character':
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating character image...', 'progress': 40})}\n\n"
                result = orchestrator.generate_character_only(prompt_text, session.session_id)
            elif generation_type == 'background':
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating background image...', 'progress': 50})}\n\n"
                result = orchestrator.generate_background_only(prompt_text, session.session_id)
            elif generation_type == 'merge':
                yield f"data: {json.dumps({'type': 'status', 'message': 'Processing images for merge...', 'progress': 30})}\n\n"
                # Handle image merge - you'll need to implement this in your orchestrator
                result = orchestrator.merge_images_only(prompt_text, session.session_id)
            else:
                # Full generation with detailed progress
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating story content...', 'progress': 30})}\n\n"
                yield f"data: {json.dumps({'type': 'status', 'message': 'Creating character image...', 'progress': 50})}\n\n"
                yield f"data: {json.dumps({'type': 'status', 'message': 'Creating background image...', 'progress': 70})}\n\n"
                yield f"data: {json.dumps({'type': 'status', 'message': 'Compositing final scene...', 'progress': 85})}\n\n"
                result = orchestrator.process_user_request(prompt_text, session.session_id)
            
            yield f"data: {json.dumps({'type': 'status', 'message': 'Finalizing results...', 'progress': 90})}\n\n"
            
            if result["status"] == "success":
                # Update session status
                session.status = 'completed'
                session.save()
                
                # Save results to GeneratedContent model
                try:
                    generated_content = self._save_generated_content(session, result)
                    self.logger.info(f"Generated content saved with ID: {generated_content.id}")
                except Exception as e:
                    self.logger.warning(f"Failed to save generated content: {e}")
                
                # Prepare response data
                try:
                    response_data = self._prepare_response_data(result, session, generation_type)
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Generation complete!', 'progress': 100})}\n\n"
                    yield f"data: {json.dumps({'type': 'complete', 'data': response_data})}\n\n"
                except Exception as e:
                    self.logger.error(f"Failed to prepare response data: {e}")
                    # Return basic success response
                    basic_response = {
                        'session_id': session.session_id,
                        'processing_status': 'completed',
                        'total_time_seconds': result.get('total_time_seconds', 0),
                        'timestamp': datetime.now().isoformat(),
                        'story_text': 'Generation completed successfully',
                        'character_description': '',
                        'background_description': '',
                        'image_urls': {}
                    }
                    yield f"data: {json.dumps({'type': 'complete', 'data': basic_response})}\n\n"
                
                self.logger.info(f"{generation_type} generation completed successfully for session {session.session_id}")
                
            else:
                # Handle failed generation
                error_msg = result.get('error', 'Unknown error occurred')
                self.logger.error(f"{generation_type} generation failed: {error_msg}")
                
                # Update session status
                session.status = 'failed'
                session.save()
                
                yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                
        except Exception as e:
            error_msg = f"Generation failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            session.status = 'failed'
            session.save()
            
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
    
    def _save_generated_content(self, session, result):
        """Save generated content to database"""
        try:
            # Extract file paths from result
            character_image_path = result['output_files'].get('character_image', '')
            background_image_path = result['output_files'].get('background_image', '')
            merged_image_path = result['output_files'].get('final_scene', '')
            
            # Create GeneratedContent record
            generated_content = GeneratedContent.objects.create(
                session=session,
                story_text=result.get('story_text', ''),
                character_description=result.get('character_description', ''),
                background_description=result.get('background_description', ''),
                character_image_path=character_image_path,
                background_image_path=background_image_path,
                merged_image_path=merged_image_path,
                generation_time_seconds=result.get('total_time_seconds', 0)
            )
            
            return generated_content
            
        except Exception as e:
            self.logger.error(f"Failed to save generated content: {e}")
            raise
    
    def _prepare_response_data(self, result, session, generation_type):
        """Prepare response data based on generation type"""
        try:
            # Build image URLs
            image_urls = {}
            if result.get('output_files'):
                base_url = f"/media/{session.session_id}/"
                if result['output_files'].get('character_image'):
                    image_urls['character_image'] = f"{base_url}character_image.png"
                if result['output_files'].get('background_image'):
                    image_urls['background_image'] = f"{base_url}background_image.png"
                if result['output_files'].get('final_scene'):
                    image_urls['merged_image'] = f"{base_url}final_scene.png"
            
            response_data = {
                'session_id': session.session_id,
                'processing_status': 'completed',
                'total_time_seconds': result.get('total_time_seconds', 0),
                'timestamp': datetime.now().isoformat(),
                'story_text': result.get('story_text', ''),
                'character_description': result.get('character_description', ''),
                'background_description': result.get('background_description', ''),
                'image_urls': image_urls
            }
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"Failed to prepare response data: {e}")
            raise


class TestView(APIView):
    """Simple test view to verify Django is working"""
    
    def get(self, request):
        return Response({
            'status': 'ok',
            'message': 'Django server is working',
            'timestamp': datetime.now().isoformat()
        })

from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Story, StoryGeneration
from .serializers import StorySerializer, StoryGenerationSerializer, StorySessionSerializer
from .pipelines.story_generator import StoryGeneratorPipeline
import uuid
from datetime import datetime


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
    """API view for generating stories with file uploads"""
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [permissions.AllowAny]  # Allow anyone to test for now
    
    def post(self, request):
        """Handle POST request for story generation"""
        try:
            # Extract data from request
            prompt_text = request.data.get('prompt_text', '')
            uploaded_files = request.FILES.getlist('uploaded_files', [])
            
            # Validate prompt text
            if not prompt_text or len(prompt_text.strip()) < 5:
                return Response(
                    {'error': 'Prompt text is required and must be at least 5 characters long'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate unique session ID
            session_id = str(uuid.uuid4())
            
            # Process uploaded files (for now, just collect info)
            file_info = []
            for file in uploaded_files:
                file_info.append({
                    'filename': file.name,
                    'file_size': file.size,
                    'file_type': getattr(file, 'content_type', 'unknown')
                })
            
            # For now, just echo back the received data (debugging)
            response_data = {
                'session_id': session_id,
                'message': 'Data received successfully - echo mode enabled',
                'data': {
                    'prompt_text': prompt_text,
                    'uploaded_files': file_info,
                    'files_count': len(uploaded_files),
                    'timestamp': datetime.now().isoformat(),
                    'status': 'echo_mode'
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'Unexpected error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

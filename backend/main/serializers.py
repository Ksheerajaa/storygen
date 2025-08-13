from rest_framework import serializers
from .models import Story, StoryGeneration
import uuid
from datetime import datetime


class StorySerializer(serializers.ModelSerializer):
    """Serializer for Story model"""
    author = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Story
        fields = ['id', 'title', 'content', 'author', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class StoryGenerationSerializer(serializers.ModelSerializer):
    """Serializer for StoryGeneration model"""
    generated_story = StorySerializer(read_only=True)
    
    class Meta:
        model = StoryGeneration
        fields = ['id', 'prompt', 'generated_story', 'status', 'created_at']
        read_only_fields = ['created_at']


class UploadedFileSerializer(serializers.Serializer):
    """Serializer for handling file uploads"""
    file = serializers.FileField(
        max_length=255,
        allow_empty_file=False,
        use_url=False
    )
    filename = serializers.CharField(max_length=255, read_only=True)
    file_size = serializers.IntegerField(read_only=True)
    file_type = serializers.CharField(max_length=100, read_only=True)
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        # Check file type (allow common image and text formats)
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'text/plain', 'text/markdown', 'application/pdf'
        ]
        if hasattr(value, 'content_type') and value.content_type not in allowed_types:
            raise serializers.ValidationError("File type not supported")
        
        return value
    
    def to_representation(self, instance):
        """Custom representation for file data"""
        if hasattr(instance, 'file'):
            return {
                'filename': instance.file.name,
                'file_size': instance.file.size,
                'file_type': getattr(instance.file, 'content_type', 'unknown')
            }
        return super().to_representation(instance)


class GeneratedContentSerializer(serializers.Serializer):
    """Serializer for generated story content"""
    story_text = serializers.CharField(max_length=10000)
    character_descriptions = serializers.JSONField(required=False)
    background_descriptions = serializers.JSONField(required=False)
    generation_metadata = serializers.JSONField(required=False)
    
    def validate_story_text(self, value):
        """Validate story text"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Story text must be at least 10 characters long")
        return value


class StorySessionSerializer(serializers.Serializer):
    """Serializer for story generation session"""
    session_id = serializers.CharField(max_length=100, read_only=True)
    prompt_text = serializers.CharField(max_length=1000, required=True)
    uploaded_files = UploadedFileSerializer(many=True, required=False)
    generated_content = GeneratedContentSerializer(required=False)
    status = serializers.CharField(max_length=50, default='pending')
    created_at = serializers.DateTimeField(read_only=True)
    
    def validate_prompt_text(self, value):
        """Validate prompt text"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Prompt text must be at least 5 characters long")
        return value.strip()
    
    def to_representation(self, instance):
        """Custom representation for session data"""
        data = super().to_representation(instance)
        
        # Add session_id if not present
        if 'session_id' not in data or not data['session_id']:
            data['session_id'] = f"session_{id(instance)}_{hash(str(instance))}"
        
        return data

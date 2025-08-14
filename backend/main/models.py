from django.db import models
from django.contrib.auth.models import User


class Story(models.Model):
    """Model for storing generated stories"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title


class StoryGeneration(models.Model):
    """Model for tracking story generation requests"""
    prompt = models.TextField()
    generated_story = models.ForeignKey(Story, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Generation {self.id}: {self.prompt[:50]}..."


class StorySession(models.Model):
    """Model for tracking story generation sessions"""
    session_id = models.CharField(max_length=100, unique=True)
    prompt_text = models.TextField()
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"Session {self.session_id}: {self.prompt_text[:50]}..."


class GeneratedContent(models.Model):
    """Model for storing generated content results"""
    session = models.ForeignKey(StorySession, on_delete=models.CASCADE, related_name='generated_content')
    story_text = models.TextField()
    character_description = models.TextField()
    background_description = models.TextField()
    character_image = models.ImageField(upload_to='characters/', null=True, blank=True)
    background_image = models.ImageField(upload_to='backgrounds/', null=True, blank=True)
    merged_image = models.ImageField(upload_to='merged/', null=True, blank=True)
    processing_status = models.CharField(max_length=50, default='completed')
    error_messages = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Content for Session {self.session.session_id}"
    
    @property
    def character_image_url(self):
        """Get the URL for character image"""
        if self.character_image:
            return self.character_image.url
        return None
    
    @property
    def background_image_url(self):
        """Get the URL for background image"""
        if self.background_image:
            return self.background_image.url
        return None
    
    @property
    def merged_image_url(self):
        """Get the URL for merged image"""
        if self.merged_image:
            return self.merged_image.url
        return None

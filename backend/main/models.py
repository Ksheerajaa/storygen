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

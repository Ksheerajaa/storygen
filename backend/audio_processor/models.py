from django.db import models
import uuid
from django.utils import timezone


class AudioTranscription(models.Model):
    """Model to track audio transcription requests"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audio_file = models.FileField(upload_to='audio_uploads/%Y/%m/%d/')
    transcription = models.TextField(blank=True)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True)
    processing_time = models.FloatField(null=True, blank=True)  # in seconds
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Audio Transcription'
        verbose_name_plural = 'Audio Transcriptions'
    
    def __str__(self):
        return f"Audio Transcription {self.id} - {self.processing_status}"
    
    @property
    def file_name(self):
        """Get the original filename"""
        return self.audio_file.name.split('/')[-1] if self.audio_file else ''
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.audio_file:
            return round(self.audio_file.size / (1024 * 1024), 2)
        return 0

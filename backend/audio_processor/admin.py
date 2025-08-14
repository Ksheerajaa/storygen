from django.contrib import admin
from .models import AudioTranscription


@admin.register(AudioTranscription)
class AudioTranscriptionAdmin(admin.ModelAdmin):
    """Admin interface for AudioTranscription model"""
    
    list_display = [
        'id', 'file_name', 'processing_status', 'processing_time', 
        'created_at', 'updated_at'
    ]
    
    list_filter = [
        'processing_status', 'created_at', 'updated_at'
    ]
    
    search_fields = [
        'id', 'file_name', 'transcription', 'error_message'
    ]
    
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'file_name', 'file_size_mb'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'audio_file', 'file_name', 'file_size_mb')
        }),
        ('Processing', {
            'fields': ('processing_status', 'processing_time', 'transcription')
        }),
        ('Error Handling', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        """Disable manual creation of transcription records"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow editing of processing status and transcription"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of transcription records"""
        return True

from rest_framework import serializers
from .models import AudioTranscription


class AudioTranscriptionSerializer(serializers.ModelSerializer):
    """Serializer for AudioTranscription model"""
    
    file_name = serializers.ReadOnlyField()
    file_size_mb = serializers.ReadOnlyField()
    
    class Meta:
        model = AudioTranscription
        fields = [
            'id', 'audio_file', 'transcription', 'processing_status',
            'error_message', 'processing_time', 'created_at', 'updated_at',
            'file_name', 'file_size_mb'
        ]
        read_only_fields = [
            'id', 'transcription', 'processing_status', 'error_message',
            'processing_time', 'created_at', 'updated_at', 'file_name', 'file_size_mb'
        ]


class AudioTranscriptionRequestSerializer(serializers.Serializer):
    """Serializer for audio transcription requests"""
    
    audio_file = serializers.FileField(
        max_length=255,
        allow_empty_file=False,
        use_url=False
    )
    
    def validate_audio_file(self, value):
        """Validate uploaded audio file"""
        # Check file size (max 25MB)
        if value.size > 25 * 1024 * 1024:
            raise serializers.ValidationError("File size must be less than 25MB")
        
        # Check file type
        allowed_types = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/wave']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Only .wav and .mp3 audio files are supported"
            )
        
        return value


class AudioTranscriptionResponseSerializer(serializers.Serializer):
    """Serializer for audio transcription responses"""
    
    success = serializers.BooleanField()
    transcription = serializers.CharField(allow_blank=True)
    error = serializers.CharField(allow_blank=True)
    processing_time = serializers.FloatField(required=False)
    transcription_id = serializers.UUIDField(required=False)

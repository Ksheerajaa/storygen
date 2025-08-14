from django.urls import path
from . import views

app_name = 'audio_processor'

urlpatterns = [
    # Audio transcription endpoint
    path('transcribe-audio/', views.AudioTranscriptionView.as_view(), name='transcribe_audio'),
    
    # Transcription status and management
    path('transcription-status/<uuid:transcription_id>/', views.transcription_status, name='transcription_status'),
    path('transcription-list/', views.transcription_list, name='transcription_list'),
]

# StoryGen Django API with StoryOrchestrator Integration

This document describes the updated Django API that integrates with the StoryOrchestrator for complete AI-powered story generation.

## Overview

The API now uses the `StoryOrchestrator` class to coordinate all AI pipelines:
1. **Story Generation** using LangChain
2. **Character Image Generation** using Stable Diffusion
3. **Background Image Generation** using Stable Diffusion
4. **Image Processing** (background removal, compositing)
5. **Database Storage** of all results

## API Endpoints

### POST /api/generate-story/

Generates a complete story with images using the StoryOrchestrator.

**Request:**
```json
{
    "prompt_text": "A brave knight discovers a magical forest where trees whisper ancient secrets"
}
```

**Response (Success - 201):**
```json
{
    "session_id": "abc123def456",
    "story_text": "Once upon a time, in a mystical forest...",
    "character_description": "A brave knight in shining armor...",
    "background_description": "A magical forest with ancient trees...",
    "image_urls": {
        "character_image": "/media/characters/knight_abc123.png",
        "background_image": "/media/backgrounds/forest_def456.png",
        "merged_image": "/media/merged/final_scene_ghi789.png"
    },
    "processing_status": "completed",
    "total_time_seconds": 1200.5,
    "timestamp": "2025-08-13T22:30:00"
}
```

**Response (Error - 500):**
```json
{
    "session_id": "abc123def456",
    "processing_status": "failed",
    "error_messages": ["Story generation failed: AI model error"],
    "timestamp": "2025-08-13T22:30:00"
}
```

## Database Models

### StorySession
Tracks each story generation request:
- `session_id`: Unique identifier for the session
- `prompt_text`: User's story prompt
- `status`: Processing status (pending, processing, completed, failed)
- `user`: Associated user (optional)
- `created_at`, `updated_at`: Timestamps

### GeneratedContent
Stores the generated content and images:
- `session`: Link to StorySession
- `story_text`: Generated story content
- `character_description`: Character descriptions
- `background_description`: Background descriptions
- `character_image`: Character image file
- `background_image`: Background image file
- `merged_image`: Final composited image
- `processing_status`: Status of content generation
- `error_messages`: Any error messages

## File Organization

Generated files are organized in the `media/` directory:
```
media/
├── characters/          # Character images
├── backgrounds/         # Background images
├── merged/             # Final composited images
└── sessions/           # Session-specific files (orchestrator)
    └── {session_id}/
        ├── story/
        ├── images/
        ├── processed/
        └── final/
```

## Error Handling

The API includes comprehensive error handling:

1. **Input Validation**: Ensures prompt text is provided and valid
2. **AI Model Failures**: Gracefully handles model initialization and generation errors
3. **File System Errors**: Handles permission and disk space issues
4. **Database Errors**: Manages transaction failures and data integrity
5. **Partial Failures**: Continues processing even if some steps fail

## Logging

Comprehensive logging is implemented throughout the process:
- **Request tracking**: Each API call is logged with session ID
- **Pipeline progress**: Logs each step of the AI pipeline
- **Error details**: Full error stack traces for debugging
- **Performance metrics**: Timing information for optimization

## Testing

### Start Django Server
```bash
cd backend
python manage.py runserver
```

### Test API
```bash
python test_api.py
```

### Check Admin Interface
Visit `http://localhost:8000/admin/` to view:
- StorySession records
- GeneratedContent records
- Generated images and files

## Performance Considerations

- **First Run**: Initial model loading may take 5-10 minutes
- **Story Generation**: 1-5 minutes depending on prompt complexity
- **Image Generation**: 15-30 minutes on CPU, 2-5 minutes on GPU
- **Total Pipeline**: 20-40 minutes for complete story with images

## Troubleshooting

### Common Issues

1. **"AI pipeline not initialized"**
   - Check that all dependencies are installed
   - Verify model files are downloaded
   - Check available memory (8GB+ recommended)

2. **"File permission denied"**
   - Ensure media/ directory is writable
   - Check Windows file permissions
   - Run as administrator if needed

3. **"Out of memory"**
   - Close other applications
   - Reduce model size in settings
   - Use CPU mode instead of GPU

4. **"Model download failed"**
   - Check internet connection
   - Verify Hugging Face access
   - Clear model cache and retry

### Debug Mode

Enable debug logging by setting `DEBUG = True` in `settings.py` and check the console output for detailed information.

## Next Steps

1. **Frontend Integration**: Build a React frontend to consume the API
2. **Progress Tracking**: Implement real-time progress updates
3. **User Authentication**: Add proper user management and permissions
4. **Caching**: Implement result caching for better performance
5. **Queue System**: Add background task processing for long-running operations

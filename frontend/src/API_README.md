# API Communication Module

This module handles all communication between the React frontend and Django backend.

## Overview

The `api.js` file provides a clean, error-handled interface for making HTTP requests to your Django backend. It's designed to work seamlessly with the `GenerateStoryView` endpoint and other Django API endpoints.

## Key Features

- **Centralized Configuration**: Single place to manage API settings
- **Comprehensive Error Handling**: User-friendly error messages for all failure scenarios
- **Request/Response Logging**: Development-time logging for debugging
- **Timeout Management**: 5-minute timeout for AI processing
- **Media URL Handling**: Automatic conversion of relative paths to full URLs
- **Health Checking**: Backend connectivity verification

## Configuration

### Base URL
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
```

**Environment Variable**: Set `REACT_APP_API_URL` to override the default localhost URL.

### Timeout
```javascript
timeout: 300000, // 5 minutes for AI story generation
```

## API Endpoints

### Story Generation
```javascript
POST /api/generate-story/
```

**Request Body:**
```json
{
    "prompt_text": "Your story prompt here"
}
```

**Response:**
```json
{
    "session_id": "abc123def456",
    "story_text": "Generated story content...",
    "character_description": "Character details...",
    "background_description": "Background details...",
    "image_urls": {
        "character_image": "/media/characters/knight.png",
        "background_image": "/media/backgrounds/forest.png",
        "merged_image": "/media/merged/final_scene.png"
    },
    "processing_status": "completed",
    "total_time_seconds": 1200.5,
    "timestamp": "2025-08-13T22:30:00"
}
```

### Other Endpoints
- `GET /api/stories/` - Fetch all stories
- `GET /api/stories/{id}/` - Fetch specific story
- `GET /api/story-generations/` - Fetch generation history

## Functions

### `generateStory(promptText)`
Generates a story using the Django backend.

```javascript
import { generateStory } from './api';

try {
    const result = await generateStory("A brave knight discovers a magical forest");
    console.log('Story:', result.story_text);
    console.log('Images:', result.image_urls);
} catch (error) {
    console.error('Failed:', error.message);
}
```

### `getMediaUrl(imagePath)`
Converts relative image paths to full URLs.

```javascript
import { getMediaUrl } from './api';

const characterUrl = getMediaUrl('characters/knight.png');
// Returns: 'http://127.0.0.1:8000/media/characters/knight.png'

const noImage = getMediaUrl(null);
// Returns: null
```

### `checkBackendHealth()`
Verifies backend connectivity.

```javascript
import { checkBackendHealth } from './api';

const isHealthy = await checkBackendHealth();
if (isHealthy) {
    console.log('Backend is running');
} else {
    console.log('Backend is not accessible');
}
```

## Error Handling

The module handles various error scenarios with user-friendly messages:

### Network Errors
- **Backend not running**: "Cannot connect to server. Please check if the Django backend is running."
- **Timeout**: "Request timed out. AI story generation can take several minutes."

### HTTP Status Errors
- **400**: "Invalid request. Please check your input."
- **500**: "Server error. Please try again later."
- **503**: "Service temporarily unavailable. AI models may be initializing."

### Input Validation
- **Empty prompt**: "Invalid prompt text provided"
- **Invalid type**: "Invalid prompt text provided"

## Development Features

### Request/Response Logging
In development mode, the module logs all API requests and responses:

```
🚀 API Request: POST /api/generate-story/
✅ API Response: 201 /api/generate-story/
❌ Response Error: 500 /api/generate-story/
```

### Error Interceptors
Automatic error transformation and logging for debugging.

## Usage Examples

### Basic Story Generation
```javascript
import { generateStory } from './api';

const handleSubmit = async (prompt) => {
    try {
        setIsLoading(true);
        const result = await generateStory(prompt);
        setStory(result);
    } catch (error) {
        setError(error.message);
    } finally {
        setIsLoading(false);
    }
};
```

### Image Display
```javascript
import { getMediaUrl } from './api';

const StoryImage = ({ imagePath, alt }) => {
    const imageUrl = getMediaUrl(imagePath);
    
    if (!imageUrl) {
        return <div>No image available</div>;
    }
    
    return <img src={imageUrl} alt={alt} />;
};
```

### Health Check Before Operations
```javascript
import { checkBackendHealth, generateStory } from './api';

const generateStoryWithHealthCheck = async (prompt) => {
    const isHealthy = await checkBackendHealth();
    
    if (!isHealthy) {
        throw new Error('Backend is not accessible');
    }
    
    return await generateStory(prompt);
};
```

## Testing

Use the included `api-test.js` file to test API functionality:

```javascript
// In browser console
import('./api-test.js').then(module => {
    window.apiTest.runAllTests();
});

// Or test individual functions
window.apiTest.testConnection();
window.apiTest.testStoryGeneration();
```

## Troubleshooting

### Common Issues

1. **"Cannot connect to server"**
   - Ensure Django backend is running on port 8000
   - Check if the port is correct in `API_BASE_URL`
   - Verify Django CORS settings

2. **"Request timed out"**
   - AI models may be initializing (first run)
   - Check available memory (8GB+ recommended)
   - Consider increasing timeout for slower systems

3. **"API endpoint not found"**
   - Verify the endpoint URL in Django URLs
   - Check if Django app is properly configured
   - Ensure migrations are applied

4. **CORS errors in browser**
   - Verify Django CORS settings
   - Check if proxy is working correctly
   - Ensure backend is accessible from frontend

### Debug Steps

1. **Check backend health:**
   ```javascript
   await checkBackendHealth();
   ```

2. **Test individual endpoints:**
   ```javascript
   await generateStory("test prompt");
   ```

3. **Check browser console** for detailed error logs

4. **Verify Django server** is running and accessible

## Production Considerations

### Environment Variables
```bash
# Production
REACT_APP_API_URL=https://your-production-domain.com

# Development
REACT_APP_API_URL=http://127.0.0.1:8000
```

### Error Handling
- Customize error messages for production
- Implement retry logic for failed requests
- Add request/response monitoring

### Security
- Implement proper authentication
- Use HTTPS in production
- Validate all inputs server-side

## Integration with Django

This module is designed to work with your Django backend:

- **GenerateStoryView**: Main story generation endpoint
- **Media files**: Automatic URL construction for generated images
- **Error responses**: Proper handling of Django error formats
- **CORS**: Compatible with Django CORS headers

The API module provides a robust foundation for frontend-backend communication in your StoryGen application.

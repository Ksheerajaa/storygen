import axios from 'axios';

/**
 * API Configuration
 * Base URL for Django backend - change this for production
 */
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

/**
 * Axios instance with default configuration
 * - 5 minute timeout for AI processing
 * - JSON content type
 * - Error handling interceptors
 */
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 300000, // 5 minutes for AI story generation
    headers: {
        'Content-Type': 'application/json',
    },
});

/**
 * API Endpoints
 * Centralized endpoint definitions for easy maintenance
 */
export const API_ENDPOINTS = {
    GENERATE_STORY: '/api/generate-story/',
    GET_STORIES: '/api/stories/',
    GET_STORY: (id) => `/api/stories/${id}/`,
    GET_STORY_GENERATIONS: '/api/story-generations/',
};

/**
 * Response timeout error message
 */
const TIMEOUT_MESSAGE = 'Request timed out. AI story generation can take several minutes.';

/**
 * Network error message
 */
const NETWORK_ERROR_MESSAGE = 'Cannot connect to server. Please check if the Django backend is running.';

/**
 * Generic error message
 */
const GENERIC_ERROR_MESSAGE = 'An unexpected error occurred. Please try again.';

/**
 * Error handler utility function
 * @param {Error} error - The error object from axios
 * @returns {string} User-friendly error message
 */
const handleApiError = (error) => {
    console.error('API Error:', error);

    // Handle timeout errors
    if (error.code === 'ECONNABORTED') {
        return TIMEOUT_MESSAGE;
    }

    // Handle network errors (backend not running)
    if (error.message === 'Network Error' || !error.response) {
        return NETWORK_ERROR_MESSAGE;
    }

    // Handle HTTP status errors
    const { status, data } = error.response;
    
    switch (status) {
        case 400:
            return data?.error || 'Invalid request. Please check your input.';
        case 401:
            return 'Authentication required. Please log in.';
        case 403:
            return 'Access denied. You do not have permission for this action.';
        case 404:
            return 'API endpoint not found. Please check the URL.';
        case 500:
            return data?.error || 'Server error. Please try again later.';
        case 503:
            return 'Service temporarily unavailable. AI models may be initializing.';
        default:
            return data?.error || GENERIC_ERROR_MESSAGE;
    }
};

/**
 * Generate a story using the Django backend
 * @param {string} promptText - The story prompt from user input
 * @returns {Promise<Object>} Story generation result
 * @throws {Error} If the API call fails
 * 
 * @example
 * try {
 *   const result = await generateStory("A brave knight discovers a magical forest");
 *   console.log('Generated story:', result.story_text);
 * } catch (error) {
 *   console.error('Story generation failed:', error.message);
 * }
 */
export const generateStory = async (promptText, generationType = 'full') => {
    try {
        // Validate input
        if (!promptText || typeof promptText !== 'string') {
            throw new Error('Invalid prompt text provided');
        }

        // Make API request to Django GenerateStoryView
        const response = await api.post(API_ENDPOINTS.GENERATE_STORY, {
            prompt_text: promptText.trim(),
            generation_type: generationType
        });

        // Return the response data
        return response.data;

    } catch (error) {
        // Handle and transform errors for user consumption
        const userMessage = handleApiError(error);
        throw new Error(userMessage);
    }
};

/**
 * Fetch all stories from the backend
 * @returns {Promise<Array>} Array of story objects
 * @throws {Error} If the API call fails
 * 
 * @example
 * try {
 *   const stories = await getStories();
 *   stories.forEach(story => console.log(story.title));
 * } catch (error) {
 *   console.error('Failed to fetch stories:', error.message);
 * }
 */
export const getStories = async () => {
    try {
        const response = await api.get(API_ENDPOINTS.GET_STORIES);
        return response.data;
    } catch (error) {
        const userMessage = handleApiError(error);
        throw new Error(userMessage);
    }
};

/**
 * Fetch a specific story by ID
 * @param {string|number} id - The story ID
 * @returns {Promise<Object>} Story object
 * @throws {Error} If the API call fails
 * 
 * @example
 * try {
 *   const story = await getStory(123);
 *   console.log('Story title:', story.title);
 * } catch (error) {
 *   console.error('Failed to fetch story:', error.message);
 * }
 */
export const getStory = async (id) => {
    try {
        if (!id) {
            throw new Error('Story ID is required');
        }

        const response = await api.get(API_ENDPOINTS.GET_STORY(id));
        return response.data;
    } catch (error) {
        const userMessage = handleApiError(error);
        throw new Error(userMessage);
    }
};

/**
 * Fetch story generation history
 * @returns {Promise<Array>} Array of generation records
 * @throws {Error} If the API call fails
 * 
 * @example
 * try {
 *   const generations = await getStoryGenerations();
 *   generations.forEach(gen => console.log(gen.status));
 * } catch (error) {
 *   console.error('Failed to fetch generations:', error.message);
 * }
 */
export const getStoryGenerations = async () => {
    try {
        const response = await api.get(API_ENDPOINTS.GET_STORY_GENERATIONS);
        return response.data;
    } catch (error) {
        const userMessage = handleApiError(error);
        throw new Error(userMessage);
    }
};

/**
 * Convert relative image path to full URL
 * @param {string} imagePath - Relative path from Django media
 * @returns {string|null} Full URL or null if no image
 * 
 * @example
 * const characterUrl = getMediaUrl('characters/knight_abc123.png');
 * // Returns: 'http://127.0.0.1:8000/media/characters/knight_abc123.png'
 * 
 * const noImage = getMediaUrl(null);
 * // Returns: null
 */
export const getMediaUrl = (imagePath) => {
    // Handle null/undefined/empty paths
    if (!imagePath || typeof imagePath !== 'string') {
        return null;
    }

    // If it's already a full URL, return as is
    if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
        return imagePath;
    }

    // Remove leading slash if present to avoid double slashes
    const cleanPath = imagePath.startsWith('/') ? imagePath.slice(1) : imagePath;
    
    // Construct full URL with media path
    return `${API_BASE_URL}/media/${cleanPath}`;
};

/**
 * Check if the backend is accessible
 * @returns {Promise<boolean>} True if backend is running
 * 
 * @example
 * const isBackendRunning = await checkBackendHealth();
 * if (!isBackendRunning) {
 *   console.log('Backend is not accessible');
 * }
 */
export const checkBackendHealth = async () => {
    try {
        // Try to access a simple endpoint
        await api.get('/');
        return true;
    } catch (error) {
        console.warn('Backend health check failed:', error.message);
        return false;
    }
};

/**
 * Cancel ongoing requests (useful when user navigates away)
 * @param {string} requestId - Unique identifier for the request
 */
export const cancelRequest = (requestId) => {
    // Implementation for request cancellation
    // This can be enhanced with AbortController if needed
    console.log(`Request ${requestId} cancellation requested`);
};

/**
 * Set authentication token for future requests
 * @param {string} token - JWT or session token
 */
export const setAuthToken = (token) => {
    if (token) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
        delete api.defaults.headers.common['Authorization'];
    }
};

/**
 * Clear authentication token
 */
export const clearAuthToken = () => {
    setAuthToken(null);
};

// Add request timing metadata
api.interceptors.request.use((config) => {
    config.metadata = { startTime: Date.now() };
    return config;
});

// Enhanced logging for development
if (process.env.NODE_ENV === 'development') {
    api.interceptors.request.use(
        (config) => {
            console.log('🚀 API Request:', {
                method: config.method?.toUpperCase(),
                url: config.url,
                data: config.data,
                headers: config.headers,
                timestamp: new Date().toISOString()
            });
            return config;
        },
        (error) => {
            console.error('❌ API Request Error:', error);
            return Promise.reject(error);
        }
    );

    // Response interceptor with timing
    api.interceptors.response.use(
        (response) => {
            const responseTime = Date.now() - response.config.metadata?.startTime;
            console.log('✅ API Response:', {
                status: response.status,
                url: response.config.url,
                data: response.data,
                responseTime: `${responseTime}ms`,
                timestamp: new Date().toISOString()
            });
            return response;
        },
        (error) => {
            const responseTime = error.config?.metadata?.startTime ? 
                Date.now() - error.config.metadata.startTime : 'unknown';
            console.error('❌ API Response Error:', {
                status: error.response?.status,
                url: error.config?.url,
                message: error.message,
                data: error.response?.data,
                responseTime: typeof responseTime === 'number' ? `${responseTime}ms` : responseTime,
                timestamp: new Date().toISOString()
            });
            return Promise.reject(error);
        }
    );
}

// Export the configured axios instance
export default api;

/**
 * API Test File
 * This file demonstrates how to use the API functions
 * Run this in browser console to test API connectivity
 */

import { 
    generateStory, 
    getStories, 
    getStory, 
    getMediaUrl, 
    checkBackendHealth,
    API_ENDPOINTS 
} from './api';

/**
 * Test API connectivity
 */
export const testApiConnection = async () => {
    console.log('🧪 Testing API Connection...');
    
    try {
        // Check if backend is running
        const isHealthy = await checkBackendHealth();
        console.log('✅ Backend health check:', isHealthy ? 'PASSED' : 'FAILED');
        
        if (!isHealthy) {
            console.error('❌ Backend is not accessible. Make sure Django is running on port 8000');
            return false;
        }
        
        console.log('🚀 Backend is accessible!');
        return true;
        
    } catch (error) {
        console.error('❌ Connection test failed:', error.message);
        return false;
    }
};

/**
 * Test story generation (small prompt for testing)
 */
export const testStoryGeneration = async () => {
    console.log('🧪 Testing Story Generation...');
    
    try {
        const testPrompt = "A cat finds a magical toy";
        console.log('📝 Test prompt:', testPrompt);
        
        const result = await generateStory(testPrompt);
        console.log('✅ Story generated successfully!');
        console.log('📖 Result:', result);
        
        return result;
        
    } catch (error) {
        console.error('❌ Story generation failed:', error.message);
        return null;
    }
};

/**
 * Test media URL generation
 */
export const testMediaUrls = () => {
    console.log('🧪 Testing Media URL Generation...');
    
    const testCases = [
        'characters/knight.png',
        '/backgrounds/forest.png',
        'merged/final_scene.png',
        null,
        '',
        'https://example.com/image.jpg'
    ];
    
    testCases.forEach(testCase => {
        const url = getMediaUrl(testCase);
        console.log(`📷 Input: "${testCase}" → Output: "${url}"`);
    });
    
    console.log('✅ Media URL tests completed');
};

/**
 * Test all API endpoints
 */
export const testAllEndpoints = async () => {
    console.log('🧪 Testing All API Endpoints...');
    
    try {
        // Test story generation
        const storyResult = await testStoryGeneration();
        if (storyResult) {
            console.log('✅ Story generation endpoint: PASSED');
        } else {
            console.log('❌ Story generation endpoint: FAILED');
        }
        
        // Test media URLs
        testMediaUrls();
        
        // Test other endpoints (these might not exist yet)
        try {
            const stories = await getStories();
            console.log('✅ Get stories endpoint: PASSED');
        } catch (error) {
            console.log('⚠️ Get stories endpoint: Not implemented yet');
        }
        
        console.log('🎉 API testing completed!');
        
    } catch (error) {
        console.error('❌ API testing failed:', error.message);
    }
};

/**
 * Run all tests
 */
export const runAllTests = async () => {
    console.log('🚀 Starting API Tests...');
    console.log('=' .repeat(50));
    
    // Test 1: Connection
    const isConnected = await testApiConnection();
    
    if (isConnected) {
        console.log('\n' + '=' .repeat(50));
        
        // Test 2: Story Generation
        await testStoryGeneration();
        
        console.log('\n' + '=' .repeat(50));
        
        // Test 3: Media URLs
        testMediaUrls();
        
        console.log('\n' + '=' .repeat(50));
        
        // Test 4: All endpoints
        await testAllEndpoints();
        
    } else {
        console.log('❌ Cannot run tests - backend not accessible');
        console.log('💡 Make sure to:');
        console.log('   1. Start Django backend: python manage.py runserver');
        console.log('   2. Check Django is running on port 8000');
        console.log('   3. Verify CORS settings in Django');
    }
    
    console.log('\n' + '=' .repeat(50));
    console.log('🏁 Testing completed!');
};

// Export for use in browser console
if (typeof window !== 'undefined') {
    window.apiTest = {
        testConnection: testApiConnection,
        testStoryGeneration: testStoryGeneration,
        testMediaUrls: testMediaUrls,
        testAllEndpoints: testAllEndpoints,
        runAllTests: runAllTests
    };
    
    console.log('🧪 API Test functions loaded!');
    console.log('💡 Run window.apiTest.runAllTests() to test everything');
    console.log('💡 Or test individual functions like window.apiTest.testConnection()');
}

export default {
    testConnection: testApiConnection,
    testStoryGeneration: testStoryGeneration,
    testMediaUrls: testMediaUrls,
    testAllEndpoints: testAllEndpoints,
    runAllTests: runAllTests
};

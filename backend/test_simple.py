#!/usr/bin/env python3
"""
Simple test script for basic endpoints
"""

import requests

def test_health():
    """Test the health endpoint"""
    try:
        response = requests.get('http://127.0.0.1:8000/api/health/')
        print(f"Health check - Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_character_generation():
    """Test character generation"""
    try:
        data = {
            'prompt_text': 'A brave knight with golden armor',
            'generation_type': 'character'
        }
        
        response = requests.post(
            'http://127.0.0.1:8000/api/generate-story/',
            json=data
        )
        
        print(f"Character generation - Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Session ID: {result.get('session_id')}")
            print(f"Character image URL: {result.get('image_urls', {}).get('character_image')}")
        else:
            print(f"Error: {response.json()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Character generation failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing basic endpoints...")
    print("=" * 40)
    
    health_ok = test_health()
    print()
    
    if health_ok:
        char_ok = test_character_generation()
        print()
        print(f"Overall status: {'✅ All tests passed' if char_ok else '❌ Some tests failed'}")
    else:
        print("❌ Health check failed, skipping other tests")

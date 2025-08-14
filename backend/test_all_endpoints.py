#!/usr/bin/env python3
"""
Comprehensive test script for all image generation endpoints
"""

import requests
import os
from pathlib import Path

def test_health_endpoint():
    """Test the health endpoint"""
    print("🔍 Testing Health Endpoint...")
    try:
        response = requests.get('http://127.0.0.1:8000/api/health/')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Health: {result['status']} - {result['message']}")
            return True
        else:
            print(f"❌ Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health error: {e}")
        return False

def test_character_generation():
    """Test character image generation"""
    print("\n🎭 Testing Character Image Generation...")
    try:
        data = {
            'prompt_text': 'A brave knight with golden armor and blue cape',
            'generation_type': 'character'
        }
        
        response = requests.post(
            'http://127.0.0.1:8000/api/generate-story/',
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Character generation successful")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Character image: {result.get('image_urls', {}).get('character_image')}")
            
            # Test image access
            img_url = result.get('image_urls', {}).get('character_image')
            if img_url:
                full_url = f"http://127.0.0.1:8000{img_url}"
                img_response = requests.get(full_url)
                print(f"   Image accessible: {img_response.status_code} ({len(img_response.content)} bytes)")
            
            return True
        else:
            print(f"❌ Character generation failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Character generation error: {e}")
        return False

def test_background_generation():
    """Test background image generation"""
    print("\n🌲 Testing Background Image Generation...")
    try:
        data = {
            'prompt_text': 'A magical forest with ancient trees and glowing mushrooms',
            'generation_type': 'background'
        }
        
        response = requests.post(
            'http://127.0.0.1:8000/api/generate-story/',
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Background generation successful")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Background image: {result.get('image_urls', {}).get('background_image')}")
            
            # Test image access
            img_url = result.get('image_urls', {}).get('background_image')
            if img_url:
                full_url = f"http://127.0.0.1:8000{img_url}"
                img_response = requests.get(full_url)
                print(f"   Image accessible: {img_response.status_code} ({len(img_response.content)} bytes)")
            
            return True
        else:
            print(f"❌ Background generation failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Background generation error: {e}")
        return False

def test_merge_images():
    """Test image merging functionality"""
    print("\n🔄 Testing Image Merging...")
    try:
        # Use existing test images
        image1_path = "test_char1.png"
        image2_path = "test_bg1.png"
        
        if not os.path.exists(image1_path) or not os.path.exists(image2_path):
            print(f"❌ Test images not found: {image1_path}, {image2_path}")
            return False
        
        files = {
            'image1': ('test_char1.png', open(image1_path, 'rb'), 'image/png'),
            'image2': ('test_bg1.png', open(image2_path, 'rb'), 'image/png')
        }
        
        data = {'generation_type': 'merge'}
        
        response = requests.post(
            'http://127.0.0.1:8000/api/generate-story/',
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Image merging successful")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Merged image: {result.get('image_urls', {}).get('merged_image')}")
            
            # Test merged image access
            img_url = result.get('image_urls', {}).get('merged_image')
            if img_url:
                full_url = f"http://127.0.0.1:8000{img_url}"
                img_response = requests.get(full_url)
                print(f"   Merged image accessible: {img_response.status_code} ({len(img_response.content)} bytes)")
            
            return True
        else:
            print(f"❌ Image merging failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Image merging error: {e}")
        return False
    finally:
        # Close files
        for file_obj in files.values():
            if hasattr(file_obj, 'close'):
                file_obj.close()

def test_story_generation():
    """Test full story generation"""
    print("\n📚 Testing Story Generation...")
    try:
        data = {
            'prompt_text': 'A young wizard discovers a magical library in the clouds',
            'generation_type': 'story'
        }
        
        response = requests.post(
            'http://127.0.0.1:8000/api/generate-story/',
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Story generation successful")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Story length: {len(result.get('story_text', ''))} characters")
            print(f"   Character description: {len(result.get('character_description', ''))} characters")
            print(f"   Background description: {len(result.get('background_description', ''))} characters")
            return True
        else:
            print(f"❌ Story generation failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Story generation error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("🧪 COMPREHENSIVE STORYGEN BACKEND TESTING")
    print("=" * 70)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Character Generation", test_character_generation),
        ("Background Generation", test_background_generation),
        ("Image Merging", test_merge_images),
        ("Story Generation", test_story_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Backend is working perfectly!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("=" * 70)

if __name__ == "__main__":
    main()

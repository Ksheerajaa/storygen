#!/usr/bin/env python3
"""
Detailed test script for merge images functionality
"""

import requests
import os
from pathlib import Path

def test_merge_images_detailed():
    """Test the merge images endpoint with detailed debugging"""
    
    # Test images
    image1_path = "test_char1.png"
    image2_path = "test_bg1.png"
    
    # Check if test images exist
    if not os.path.exists(image1_path):
        print(f"Error: {image1_path} not found")
        return False
    
    if not os.path.exists(image2_path):
        print(f"Error: {image2_path} not found")
        return False
    
    print(f"Test images found:")
    print(f"  Image 1: {image1_path} ({os.path.getsize(image1_path)} bytes)")
    print(f"  Image 2: {image2_path} ({os.path.getsize(image2_path)} bytes)")
    
    # Prepare the multipart form data
    files = {
        'image1': ('test_char1.png', open(image1_path, 'rb'), 'image/png'),
        'image2': ('test_bg1.png', open(image2_path, 'rb'), 'image/png')
    }
    
    data = {
        'generation_type': 'merge'
    }
    
    try:
        # Send the request
        print("\nTesting merge images endpoint...")
        print(f"URL: http://127.0.0.1:8000/api/generate-story/")
        print(f"Files: {list(files.keys())}")
        print(f"Data: {data}")
        
        response = requests.post(
            'http://127.0.0.1:8000/api/generate-story/',
            files=files,
            data=data,
            timeout=30
        )
        
        print(f"\nResponse received:")
        print(f"  Status Code: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Response JSON: {result}")
            
            if 'image_urls' in result and result['image_urls'].get('merged_image'):
                print("✅ Merge successful! Merged image URL:", result['image_urls']['merged_image'])
                
                # Test if the merged image is accessible
                merged_url = result['image_urls']['merged_image']
                if merged_url.startswith('/'):
                    merged_url = f"http://127.0.0.1:8000{merged_url}"
                
                print(f"Testing merged image access: {merged_url}")
                img_response = requests.get(merged_url)
                print(f"  Image access status: {img_response.status_code}")
                print(f"  Image size: {len(img_response.content)} bytes")
                
                return True
            else:
                print("⚠️ Merge completed but no merged image URL returned")
                print(f"  Available keys: {list(result.keys())}")
                if 'image_urls' in result:
                    print(f"  Image URLs: {result['image_urls']}")
                return False
        else:
            print("❌ Merge failed")
            try:
                error_response = response.json()
                print(f"  Error details: {error_response}")
            except:
                print(f"  Raw error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close the files
        for file_obj in files.values():
            if hasattr(file_obj, 'close'):
                file_obj.close()

if __name__ == "__main__":
    print("=" * 60)
    print("DETAILED MERGE IMAGES TEST")
    print("=" * 60)
    
    success = test_merge_images_detailed()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ MERGE TEST PASSED")
    else:
        print("❌ MERGE TEST FAILED")
    print("=" * 60)

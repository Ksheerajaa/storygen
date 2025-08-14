#!/usr/bin/env python3
"""
Test script for merge images functionality
"""

import requests
import os

def test_merge_images():
    """Test the merge images endpoint"""
    
    # Test images
    image1_path = "test_char1.png"
    image2_path = "test_bg1.png"
    
    # Check if test images exist
    if not os.path.exists(image1_path):
        print(f"Error: {image1_path} not found")
        return
    
    if not os.path.exists(image2_path):
        print(f"Error: {image2_path} not found")
        return
    
    # Prepare the multipart form data
    files = {
        'image1': open(image1_path, 'rb'),
        'image2': open(image2_path, 'rb')
    }
    
    data = {
        'generation_type': 'merge'
    }
    
    try:
        # Send the request
        print("Testing merge images endpoint...")
        response = requests.post(
            'http://127.0.0.1:8000/api/generate-story/',
            files=files,
            data=data
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if 'image_urls' in result and result['image_urls'].get('merged_image'):
                print("✅ Merge successful! Merged image URL:", result['image_urls']['merged_image'])
            else:
                print("⚠️ Merge completed but no merged image URL returned")
        else:
            print("❌ Merge failed")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the files
        files['image1'].close()
        files['image2'].close()

if __name__ == "__main__":
    test_merge_images()

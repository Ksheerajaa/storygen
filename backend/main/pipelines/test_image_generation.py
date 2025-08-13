"""
Test file for Image Generation and Processing Pipelines
Run this to verify that image generation and processing components are working correctly
"""

import sys
import os
import logging
from pathlib import Path

# Add the parent directory to the path so we can import Django modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storygen_web.settings')

import django
django.setup()

# Now we can import our modules
from main.pipelines.image_generator import ImageGenerator, initialize_image_generation
from main.pipelines.image_processor import ImageProcessor, initialize_image_processing

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_image_generator():
    """Test the image generation pipeline"""
    print("\n" + "="*50)
    print("TESTING IMAGE GENERATION PIPELINE")
    print("="*50)
    
    try:
        # Test initialization
        print("1. Testing ImageGenerator initialization...")
        generator = ImageGenerator()
        
        if generator.initialized:
            print("✅ ImageGenerator initialized successfully!")
            print(f"   Device: {generator.device}")
            print(f"   Model: {generator.model_name}")
        else:
            print("❌ ImageGenerator failed to initialize")
            return False
        
        # Test character image generation
        print("\n2. Testing character image generation...")
        test_desc = "A brave knight with silver armor and a red cape"
        test_output = "test_character.png"
        
        result = generator.generate_character_image(test_desc, test_output)
        
        if result["status"] == "success":
            print("✅ Character image generation successful!")
            print(f"   Output: {result['output_path']}")
            print(f"   Size: {result['image_size']}")
            print(f"   Prompt used: {result['prompt_used'][:100]}...")
        else:
            print(f"❌ Character generation failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test background image generation
        print("\n3. Testing background image generation...")
        test_bg_desc = "A medieval castle on a hill with storm clouds"
        test_bg_output = "test_background.png"
        
        result = generator.generate_background_image(test_bg_desc, test_bg_output)
        
        if result["status"] == "success":
            print("✅ Background image generation successful!")
            print(f"   Output: {result['output_path']}")
            print(f"   Size: {result['image_size']}")
            print(f"   Prompt used: {result['prompt_used'][:100]}...")
        else:
            print(f"❌ Background generation failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test pipeline test function
        print("\n4. Testing pipeline test function...")
        test_result = generator.test_pipeline()
        
        if test_result['status'] == 'success':
            print("✅ Pipeline test successful!")
        else:
            print(f"❌ Pipeline test failed: {test_result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Image generator test failed with error: {e}")
        logger.exception("Image generator test error")
        return False


def test_image_processor():
    """Test the image processing pipeline"""
    print("\n" + "="*50)
    print("TESTING IMAGE PROCESSING PIPELINE")
    print("="*50)
    
    try:
        # Test initialization
        print("1. Testing ImageProcessor initialization...")
        processor = ImageProcessor()
        
        if processor.initialized:
            print("✅ ImageProcessor initialized successfully!")
        else:
            print("❌ ImageProcessor failed to initialize")
            return False
        
        # Test thumbnail creation
        print("\n2. Testing thumbnail creation...")
        # Create a test image first
        from PIL import Image
        test_img = Image.new('RGB', (200, 200), color='blue')
        test_path = "test_processing.png"
        test_img.save(test_path)
        
        result = processor.create_thumbnail(test_path, "test_thumb.png", (100, 100))
        
        if result["status"] == "success":
            print("✅ Thumbnail creation successful!")
            print(f"   Output: {result['output_path']}")
            print(f"   Size: {result['thumbnail_size']}")
        else:
            print(f"❌ Thumbnail creation failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test image adjustments
        print("\n3. Testing image adjustments...")
        result = processor.adjust_image(
            test_path, "test_adjusted.png",
            brightness=1.2, contrast=1.1, saturation=0.8
        )
        
        if result["status"] == "success":
            print("✅ Image adjustments successful!")
            print(f"   Output: {result['output_path']}")
            print(f"   Adjustments: {result['adjustments']}")
        else:
            print(f"❌ Image adjustments failed: {result.get('error', 'Unknown error')}")
            return False
        
        # Test pipeline test function
        print("\n4. Testing pipeline test function...")
        test_result = processor.test_pipeline()
        
        if test_result['status'] == 'success':
            print("✅ Pipeline test successful!")
        else:
            print(f"❌ Pipeline test failed: {test_result.get('error', 'Unknown error')}")
            return False
        
        # Clean up test files
        cleanup_files = [test_path, "test_thumb.png", "test_adjusted.png"]
        for file_path in cleanup_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"   Cleaned up: {file_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Image processor test failed with error: {e}")
        logger.exception("Image processor test error")
        return False


def test_integration():
    """Test the integration between image generation and processing"""
    print("\n" + "="*50)
    print("TESTING INTEGRATION")
    print("="*50)
    
    try:
        print("1. Testing image generation initialization...")
        if not initialize_image_generation():
            print("❌ Image generation initialization failed")
            return False
        
        print("✅ Image generation initialization successful!")
        
        print("\n2. Testing image processing initialization...")
        if not initialize_image_processing():
            print("❌ Image processing initialization failed")
            return False
        
        print("✅ Image processing initialization successful!")
        
        print("\n3. Testing end-to-end image workflow...")
        generator = ImageGenerator()
        processor = ImageProcessor()
        
        if not generator.initialized or not processor.initialized:
            print("❌ Components not initialized")
            return False
        
        # Generate a character and background
        char_desc = "A wise wizard with a long white beard and blue robes"
        bg_desc = "A magical library with ancient books and floating candles"
        
        print(f"   Generating character: {char_desc}")
        char_result = generator.generate_character_image(char_desc, "integration_character.png")
        
        print(f"   Generating background: {bg_desc}")
        bg_result = generator.generate_background_image(bg_desc, "integration_background.png")
        
        if char_result["status"] == "success" and bg_result["status"] == "success":
            print("✅ End-to-end image generation successful!")
            print(f"   Character: {char_result['output_path']}")
            print(f"   Background: {bg_result['output_path']}")
        else:
            print("❌ End-to-end test failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        logger.exception("Integration test error")
        return False


def main():
    """Run all tests"""
    print("Starting Image Generation and Processing Tests...")
    print("This may take several minutes on first run as models are downloaded.")
    print("Note: Image generation requires significant memory and may be slow on CPU.")
    
    # Test results
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_image_generator():
        tests_passed += 1
        print("\n✅ Image Generator Test: PASSED")
    else:
        print("\n❌ Image Generator Test: FAILED")
    
    if test_image_processor():
        tests_passed += 1
        print("\n✅ Image Processor Test: PASSED")
    else:
        print("\n❌ Image Processor Test: FAILED")
    
    if test_integration():
        tests_passed += 1
        print("\n✅ Integration Test: PASSED")
    else:
        print("\n❌ Integration Test: FAILED")
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your image generation pipeline is working correctly.")
        print("\nNext steps:")
        print("1. Integrate with your Django views")
        print("2. Create image generation API endpoints")
        print("3. Build a frontend to test image generation")
        print("4. Consider adding image caching and optimization")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        print("\nCommon issues:")
        print("1. Insufficient memory for Stable Diffusion models")
        print("2. CUDA/GPU compatibility issues")
        print("3. Missing dependencies - check pip install")
        print("4. File permission issues on Windows")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

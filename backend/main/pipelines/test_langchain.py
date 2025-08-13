"""
Test file for LangChain pipeline functionality
Run this to verify that all components are working correctly
"""

import sys
import os
import logging

# Add the parent directory to the path so we can import Django modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storygen_web.settings')

import django
django.setup()

# Now we can import our modules
from main.pipelines.langchain_foundation import LangChainCore, initialize_langchain
from main.pipelines.story_generator import StoryGeneratorPipeline

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_langchain_core():
    """Test the LangChain core functionality"""
    print("\n" + "="*50)
    print("TESTING LANGCHAIN CORE")
    print("="*50)
    
    try:
        # Test initialization
        print("1. Testing LangChain core initialization...")
        core = LangChainCore()
        
        if core.initialized:
            print("✅ LangChain core initialized successfully!")
        else:
            print("❌ LangChain core failed to initialize")
            return False
        
        # Test story generation
        print("\n2. Testing story generation...")
        test_prompt = "A brave mouse who saves a lion"
        result = core.generate_story_content(test_prompt)
        
        if result and 'story' in result:
            print("✅ Story generation successful!")
            print(f"   Story length: {len(result['story'])} characters")
            print(f"   Character desc: {len(result['character_desc'])} characters")
            print(f"   Background desc: {len(result['background_desc'])} characters")
        else:
            print("❌ Story generation failed")
            return False
        
        # Test pipeline test function
        print("\n3. Testing pipeline test function...")
        test_result = core.test_pipeline()
        
        if test_result['status'] == 'success':
            print("✅ Pipeline test successful!")
        else:
            print(f"❌ Pipeline test failed: {test_result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ LangChain core test failed with error: {e}")
        logger.exception("LangChain core test error")
        return False


def test_story_generator():
    """Test the story generator pipeline"""
    print("\n" + "="*50)
    print("TESTING STORY GENERATOR PIPELINE")
    print("="*50)
    
    try:
        # Test initialization
        print("1. Testing StoryGeneratorPipeline initialization...")
        pipeline = StoryGeneratorPipeline()
        
        if pipeline.initialized:
            print("✅ StoryGeneratorPipeline initialized successfully!")
        else:
            print("❌ StoryGeneratorPipeline failed to initialize")
            return False
        
        # Test story generation
        print("\n2. Testing story generation...")
        test_prompt = "A wise owl who teaches other animals to read"
        result = pipeline.generate_story(test_prompt)
        
        if result['status'] == 'success':
            print("✅ Story generation successful!")
            print(f"   Title: {result['title']}")
            print(f"   Content length: {len(result['content'])} characters")
            print(f"   Character desc: {len(result['character_desc'])} characters")
            print(f"   Background desc: {len(result['background_desc'])} characters")
        else:
            print(f"❌ Story generation failed: {result.get('content', 'Unknown error')}")
            return False
        
        # Test description extraction
        print("\n3. Testing description extraction...")
        if result['status'] == 'success':
            descriptions = pipeline.extract_descriptions_from_story(result['content'])
            
            if descriptions and 'character_desc' in descriptions:
                print("✅ Description extraction successful!")
                print(f"   Character desc: {descriptions['character_desc'][:100]}...")
                print(f"   Background desc: {descriptions['background_desc'][:100]}...")
            else:
                print("❌ Description extraction failed")
                return False
        
        # Test story enhancement
        print("\n4. Testing story enhancement...")
        if result['status'] == 'success':
            enhanced = pipeline.enhance_story(result['content'])
            
            if enhanced['status'] == 'success':
                print("✅ Story enhancement successful!")
                print(f"   Enhanced length: {len(enhanced['content'])} characters")
            else:
                print(f"❌ Story enhancement failed: {enhanced.get('content', 'Unknown error')}")
                return False
        
        # Test pipeline test function
        print("\n5. Testing pipeline test function...")
        test_result = pipeline.test_pipeline()
        
        if test_result['status'] == 'success':
            print("✅ Pipeline test successful!")
        else:
            print(f"❌ Pipeline test failed: {test_result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Story generator test failed with error: {e}")
        logger.exception("Story generator test error")
        return False


def test_integration():
    """Test the integration between components"""
    print("\n" + "="*50)
    print("TESTING INTEGRATION")
    print("="*50)
    
    try:
        print("1. Testing LangChain initialization...")
        if not initialize_langchain():
            print("❌ LangChain initialization failed")
            return False
        
        print("✅ LangChain initialization successful!")
        
        print("\n2. Testing end-to-end story generation...")
        pipeline = StoryGeneratorPipeline()
        
        if not pipeline.initialized:
            print("❌ Pipeline not initialized")
            return False
        
        # Generate a complete story
        test_prompt = "A magical library where books come to life at night"
        result = pipeline.generate_story(test_prompt)
        
        if result['status'] == 'success':
            print("✅ End-to-end story generation successful!")
            print(f"   Generated story: {result['title']}")
            print(f"   Story preview: {result['content'][:200]}...")
        else:
            print(f"❌ End-to-end test failed: {result.get('content', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {e}")
        logger.exception("Integration test error")
        return False


def main():
    """Run all tests"""
    print("Starting LangChain Pipeline Tests...")
    print("This may take a few minutes on first run as models are downloaded.")
    
    # Test results
    tests_passed = 0
    total_tests = 3
    
    # Run tests
    if test_langchain_core():
        tests_passed += 1
        print("\n✅ LangChain Core Test: PASSED")
    else:
        print("\n❌ LangChain Core Test: FAILED")
    
    if test_story_generator():
        tests_passed += 1
        print("\n✅ Story Generator Test: PASSED")
    else:
        print("\n❌ Story Generator Test: FAILED")
    
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
        print("🎉 All tests passed! Your LangChain pipeline is working correctly.")
        print("\nNext steps:")
        print("1. Start your Django server: python manage.py runserver")
        print("2. Test the API endpoints")
        print("3. Create a React frontend to use the story generation")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
        print("\nCommon issues:")
        print("1. Missing dependencies - run: pip install -r requirements.txt")
        print("2. Model download issues - check internet connection")
        print("3. Memory issues - try reducing model size or max_length")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


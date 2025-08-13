#!/usr/bin/env python3
"""
Simple test script for LangChain pipeline
Run this from the backend directory: python test_langchain_simple.py
"""

import os
import sys
import django

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'storygen_web.settings')
django.setup()

from main.pipelines.langchain_core import LangChainCore
from main.pipelines.story_generator import StoryGeneratorPipeline


def test_basic_functionality():
    """Test basic LangChain functionality"""
    print("🧪 Testing LangChain Basic Functionality...")
    
    try:
        # Test LangChain core
        print("1. Initializing LangChain core...")
        core = LangChainCore()
        
        if core.initialized:
            print("✅ LangChain core initialized successfully!")
        else:
            print("❌ LangChain core failed to initialize")
            return False
        
        # Test story generation
        print("\n2. Testing story generation...")
        test_prompt = "A magical cat who can talk to plants"
        result = core.generate_story_content(test_prompt)
        
        if result and 'story' in result:
            print("✅ Story generation successful!")
            print(f"   Story: {result['story'][:100]}...")
            print(f"   Characters: {result['character_desc'][:100]}...")
            print(f"   Background: {result['background_desc'][:100]}...")
        else:
            print("❌ Story generation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def test_story_pipeline():
    """Test the story generator pipeline"""
    print("\n🧪 Testing Story Generator Pipeline...")
    
    try:
        # Test pipeline initialization
        print("1. Initializing story generator pipeline...")
        pipeline = StoryGeneratorPipeline()
        
        if pipeline.initialized:
            print("✅ Story generator pipeline initialized successfully!")
        else:
            print("❌ Story generator pipeline failed to initialize")
            return False
        
        # Test story generation
        print("\n2. Testing story generation...")
        test_prompt = "A wise old tree that grants wishes"
        result = pipeline.generate_story(test_prompt)
        
        if result['status'] == 'success':
            print("✅ Story generation successful!")
            print(f"   Title: {result['title']}")
            print(f"   Content: {result['content'][:150]}...")
        else:
            print(f"❌ Story generation failed: {result.get('content', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting LangChain Pipeline Tests...")
    print("=" * 60)
    
    # Test results
    tests_passed = 0
    total_tests = 2
    
    # Run tests
    if test_basic_functionality():
        tests_passed += 1
        print("\n✅ Basic Functionality Test: PASSED")
    else:
        print("\n❌ Basic Functionality Test: FAILED")
    
    if test_story_pipeline():
        tests_passed += 1
        print("\n✅ Story Pipeline Test: PASSED")
    else:
        print("\n❌ Story Pipeline Test: FAILED")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! Your LangChain pipeline is working correctly.")
        print("\nNext steps:")
        print("1. Start your Django server: python manage.py runserver")
        print("2. Test the API endpoints with story generation")
        print("3. Create a React frontend to use the story generation")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        print("\nCommon issues:")
        print("1. Missing dependencies - run: pip install -r requirements.txt")
        print("2. Model download issues - check internet connection")
        print("3. Memory issues - try reducing model size")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


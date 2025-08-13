"""
Test Script for Story Orchestrator
This script tests the complete orchestrator pipeline independently
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
from main.pipelines.story_orchestrator import get_story_orchestrator, test_orchestrator

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def quick_test():
    """Quick test of orchestrator initialization"""
    try:
        print("🧪 Quick Test: Initializing Story Orchestrator...")
        
        # Get orchestrator instance
        orchestrator = get_story_orchestrator()
        
        # Check initialization status
        print(f"Session ID: {orchestrator.session_id}")
        print(f"Session Directory: {orchestrator.session_dir}")
        
        # Check component status
        components = {
            "LangChain Core": orchestrator.langchain_core,
            "Story Generator": orchestrator.story_generator,
            "Image Generator": orchestrator.image_generator,
            "Image Processor": orchestrator.image_processor
        }
        
        print("\nComponent Status:")
        for name, component in components.items():
            status = "✅ Initialized" if component and getattr(component, 'initialized', False) else "❌ Not Available"
            print(f"  {name}: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        logger.exception("Quick test error")
        return False


def main():
    """Main test function"""
    print("Starting Story Orchestrator Tests...")
    print("=" * 60)
    
    # Quick initialization test
    if not quick_test():
        print("\n❌ Quick test failed. Cannot proceed with full test.")
        return False
    
    print("\n" + "=" * 60)
    print("Running Full Pipeline Test...")
    print("This will take several minutes and generate actual images.")
    print("=" * 60)
    
    # Run full pipeline test
    success = test_orchestrator()
    
    if success:
        print("\n🎉 All tests passed! Your story orchestrator is working correctly.")
        print("\nNext steps:")
        print("1. Integrate with Django views")
        print("2. Create API endpoints for story generation")
        print("3. Build a frontend interface")
        print("4. Add progress tracking and user feedback")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")
        print("\nCommon issues:")
        print("1. Missing dependencies")
        print("2. Insufficient memory for AI models")
        print("3. File permission issues")
        print("4. Network issues during model downloads")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

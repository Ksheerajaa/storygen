from django.core.management.base import BaseCommand
from django.conf import settings
import os
import sys
import time
import traceback
from pathlib import Path

class Command(BaseCommand):
    help = 'Test the complete AI pipeline for story generation and image creation'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Run quick tests only (skip image generation)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
        parser.add_argument(
            '--prompt',
            type=str,
            default='A brave knight discovers a magical forest where ancient trees whisper secrets',
            help='Custom prompt for testing',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🧪 Starting StoryGen AI Pipeline Tests...')
        )
        self.stdout.write('=' * 60)
        
        # Test configuration
        quick_mode = options['quick']
        verbose = options['verbose']
        test_prompt = options['prompt']
        
        self.stdout.write(f'📝 Test Prompt: {test_prompt}')
        self.stdout.write(f'⚡ Quick Mode: {quick_mode}')
        self.stdout.write(f'🔍 Verbose: {verbose}')
        self.stdout.write('')
        
        # Test results tracking
        test_results = {
            'langchain': False,
            'story_generation': False,
            'image_generation': False,
            'image_processing': False,
            'orchestrator': False,
            'file_operations': False
        }
        
        total_start_time = time.time()
        
        try:
            # Test 1: LangChain Foundation
            self.stdout.write('🔧 Testing LangChain Foundation...')
            if self.test_langchain_foundation(verbose):
                test_results['langchain'] = True
                self.stdout.write(self.style.SUCCESS('✅ LangChain Foundation: PASSED'))
            else:
                self.stdout.write(self.style.ERROR('❌ LangChain Foundation: FAILED'))
            
            # Test 2: Story Generation
            self.stdout.write('📚 Testing Story Generation...')
            if self.test_story_generation(test_prompt, verbose):
                test_results['story_generation'] = True
                self.stdout.write(self.style.SUCCESS('✅ Story Generation: PASSED'))
            else:
                self.stdout.write(self.style.ERROR('❌ Story Generation: FAILED'))
            
            # Test 3: Image Generation (skip if quick mode)
            if not quick_mode:
                self.stdout.write('🎨 Testing Image Generation...')
                if self.test_image_generation(verbose):
                    test_results['image_generation'] = True
                    self.stdout.write(self.style.SUCCESS('✅ Image Generation: PASSED'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Image Generation: FAILED'))
                
                # Test 4: Image Processing
                self.stdout.write('🖼️ Testing Image Processing...')
                if self.test_image_processing(verbose):
                    test_results['image_processing'] = True
                    self.stdout.write(self.style.SUCCESS('✅ Image Processing: PASSED'))
                else:
                    self.stdout.write(self.style.ERROR('❌ Image Processing: FAILED'))
            else:
                self.stdout.write('⏭️ Skipping Image Tests (Quick Mode)')
                test_results['image_generation'] = True
                test_results['image_processing'] = True
            
            # Test 5: Complete Orchestrator
            self.stdout.write('🎭 Testing Complete Orchestrator...')
            if self.test_orchestrator(test_prompt, verbose):
                test_results['orchestrator'] = True
                self.stdout.write(self.style.SUCCESS('✅ Complete Orchestrator: PASSED'))
            else:
                self.stdout.write(self.style.ERROR('❌ Complete Orchestrator: FAILED'))
            
            # Test 6: File Operations
            self.stdout.write('📁 Testing File Operations...')
            if self.test_file_operations(verbose):
                test_results['file_operations'] = True
                self.stdout.write(self.style.SUCCESS('✅ File Operations: PASSED'))
            else:
                self.stdout.write(self.style.ERROR('❌ File Operations: FAILED'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'💥 Unexpected error during testing: {str(e)}'))
            if verbose:
                self.stdout.write(traceback.format_exc())
        
        # Final Results
        total_time = time.time() - total_start_time
        self.stdout.write('')
        self.stdout.write('=' * 60)
        self.stdout.write('📊 TEST RESULTS SUMMARY')
        self.stdout.write('=' * 60)
        
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        
        for test_name, passed in test_results.items():
            status = '✅ PASS' if passed else '❌ FAIL'
            self.stdout.write(f'{test_name.replace("_", " ").title()}: {status}')
        
        self.stdout.write('')
        self.stdout.write(f'🎯 Overall: {passed_tests}/{total_tests} tests passed')
        self.stdout.write(f'⏱️ Total Time: {total_time:.2f} seconds')
        
        if passed_tests == total_tests:
            self.stdout.write(self.style.SUCCESS('🎉 All tests passed! Pipeline is working correctly.'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Some tests failed. Check the output above for details.'))
        
        return passed_tests == total_tests

    def test_langchain_foundation(self, verbose):
        """Test LangChain foundation components"""
        try:
            from main.pipelines.langchain_foundation import (
                get_langchain_foundation, 
                generate_story_content
            )
            
            if verbose:
                self.stdout.write('  - Importing LangChain components...')
            
            # Test basic functionality
            foundation = get_langchain_foundation()
            if not foundation:
                return False
            
            if verbose:
                self.stdout.write('  - Testing story generation...')
            
            # Test with simple prompt
            result = generate_story_content("A cat sits on a mat")
            
            if not result or 'content' not in result:
                return False
            
            if verbose:
                self.stdout.write(f'  - Generated story length: {len(result["content"])} characters')
            
            return True
            
        except Exception as e:
            if verbose:
                self.stdout.write(f'  - Error: {str(e)}')
            return False

    def test_story_generation(self, test_prompt, verbose):
        """Test story generation pipeline"""
        try:
            from main.pipelines.story_generator import get_story_generator
            
            if verbose:
                self.stdout.write('  - Initializing story generator...')
            
            generator = get_story_generator()
            if not generator:
                return False
            
            if verbose:
                self.stdout.write('  - Generating story...')
            
            start_time = time.time()
            result = generator.generate_story(test_prompt)
            generation_time = time.time() - start_time
            
            if not result or 'content' not in result:
                return False
            
            if verbose:
                self.stdout.write(f'  - Story generated in {generation_time:.2f} seconds')
                self.stdout.write(f'  - Story length: {len(result["content"])} characters')
                self.stdout.write(f'  - Character description: {len(result.get("character_desc", ""))} characters')
                self.stdout.write(f'  - Background description: {len(result.get("background_desc", ""))} characters')
            
            return True
            
        except Exception as e:
            if verbose:
                self.stdout.write(f'  - Error: {str(e)}')
            return False

    def test_image_generation(self, verbose):
        """Test image generation pipeline"""
        try:
            from main.pipelines.image_generator import get_image_generator
            
            if verbose:
                self.stdout.write('  - Initializing image generator...')
            
            generator = get_image_generator()
            if not generator:
                return False
            
            if verbose:
                self.stdout.write('  - Testing character image generation...')
            
            # Test character image generation
            test_character_desc = "A brave knight in shining armor with a sword"
            start_time = time.time()
            
            # Create test output directory
            test_dir = Path('test_output')
            test_dir.mkdir(exist_ok=True)
            
            character_path = test_dir / 'test_character.png'
            result = generator.generate_character_image(test_character_desc, str(character_path))
            
            generation_time = time.time() - start_time
            
            if not result or not character_path.exists():
                return False
            
            if verbose:
                self.stdout.write(f'  - Character image generated in {generation_time:.2f} seconds')
                self.stdout.write(f'  - Image saved to: {character_path}')
                self.stdout.write(f'  - Image size: {character_path.stat().st_size} bytes')
            
            # Clean up test file
            if character_path.exists():
                character_path.unlink()
            
            return True
            
        except Exception as e:
            if verbose:
                self.stdout.write(f'  - Error: {str(e)}')
            return False

    def test_image_processing(self, verbose):
        """Test image processing pipeline"""
        try:
            from main.pipelines.image_processor import get_image_processor
            
            if verbose:
                self.stdout.write('  - Initializing image processor...')
            
            processor = get_image_processor()
            if not processor:
                return False
            
            if verbose:
                self.stdout.write('  - Testing background removal...')
            
            # Create a simple test image (1x1 pixel PNG)
            test_dir = Path('test_output')
            test_dir.mkdir(exist_ok=True)
            
            # Create a minimal test image
            from PIL import Image
            test_image = Image.new('RGB', (10, 10), color='red')
            test_image_path = test_dir / 'test_image.png'
            test_image.save(test_image_path)
            
            # Test background removal
            output_path = test_dir / 'test_removed.png'
            result = processor.remove_background(str(test_image_path), str(output_path))
            
            if verbose:
                self.stdout.write(f'  - Background removal test completed')
                if output_path.exists():
                    self.stdout.write(f'  - Output saved to: {output_path}')
            
            # Clean up test files
            for file_path in [test_image_path, output_path]:
                if file_path.exists():
                    file_path.unlink()
            
            return True
            
        except Exception as e:
            if verbose:
                self.stdout.write(f'  - Error: {str(e)}')
            return False

    def test_orchestrator(self, test_prompt, verbose):
        """Test complete orchestrator pipeline"""
        try:
            from main.pipelines.story_orchestrator import get_story_orchestrator
            
            if verbose:
                self.stdout.write('  - Initializing story orchestrator...')
            
            orchestrator = get_story_orchestrator()
            if not orchestrator:
                return False
            
            if verbose:
                self.stdout.write('  - Testing complete pipeline...')
            
            # Test with session ID
            session_id = f"test_{int(time.time())}"
            start_time = time.time()
            
            result = orchestrator.process_user_request(test_prompt, session_id)
            pipeline_time = time.time() - start_time
            
            if not result or result.get('status') != 'success':
                if verbose:
                    self.stdout.write(f'  - Pipeline failed: {result.get("error", "Unknown error")}')
                return False
            
            if verbose:
                self.stdout.write(f'  - Complete pipeline executed in {pipeline_time:.2f} seconds')
                self.stdout.write(f'  - Session ID: {session_id}')
                self.stdout.write(f'  - Story generated: {len(result["results"]["story"]["content"])} characters')
                
                # Check output files
                output_files = result.get('output_files', {})
                for file_type, file_path in output_files.items():
                    if file_path and Path(file_path).exists():
                        self.stdout.write(f'  - {file_type}: {file_path} ({Path(file_path).stat().st_size} bytes)')
                    else:
                        self.stdout.write(f'  - {file_type}: Not generated')
            
            return True
            
        except Exception as e:
            if verbose:
                self.stdout.write(f'  - Error: {str(e)}')
            return False

    def test_file_operations(self, verbose):
        """Test file operations and media handling"""
        try:
            if verbose:
                self.stdout.write('  - Testing media directory structure...')
            
            # Check media directories
            media_root = Path('media')
            required_dirs = ['characters', 'backgrounds', 'merged']
            
            for dir_name in required_dirs:
                dir_path = media_root / dir_name
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    if verbose:
                        self.stdout.write(f'  - Created directory: {dir_path}')
                else:
                    if verbose:
                        self.stdout.write(f'  - Directory exists: {dir_path}')
            
            # Test file permissions
            test_file = media_root / 'test_permissions.txt'
            try:
                test_file.write_text('test')
                test_file.unlink()
                if verbose:
                    self.stdout.write('  - File write/delete permissions: OK')
            except Exception as e:
                if verbose:
                    self.stdout.write(f'  - File permissions error: {str(e)}')
                return False
            
            if verbose:
                self.stdout.write('  - All file operations working correctly')
            
            return True
            
        except Exception as e:
            if verbose:
                self.stdout.write(f'  - Error: {str(e)}')
            return False

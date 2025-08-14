"""
Master Story Orchestrator
This module coordinates all AI pipelines to create a complete story generation workflow:
1. Story generation using LangChain
2. Character and background image generation using Stable Diffusion
3. Image processing and compositing
4. Session management and file organization
"""

import os
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback

# Import all AI pipeline modules
try:
    from .langchain_foundation import get_langchain_core
    from .story_generator import get_story_generator
    from .image_generator import get_image_generator
    from .image_processor import get_image_processor
    AI_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some AI modules not available: {e}")
    AI_MODULES_AVAILABLE = False
    # Create dummy functions for fallback
    def get_langchain_core():
        return None
    def get_story_generator():
        return None
    def get_image_generator():
        return None
    def get_image_processor():
        return None

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StoryOrchestrator:
    """
    Master orchestrator that coordinates all AI pipelines for complete story generation
    Manages the entire workflow from user prompt to final images
    """
    
    def __init__(self):
        """Initialize all AI models and pipelines"""
        self.session_id = None
        self.workflow_status = {}
        self.start_time = None
        
        # Initialize AI components
        self.langchain_core = None
        self.story_generator = None
        self.image_generator = None
        self.image_processor = None
        
        # Session file paths
        self.session_dir = None
        self.output_files = {}
        
        # Initialize all pipelines
        self._initialize_pipelines()
    
    def _initialize_pipelines(self):
        """Initialize all AI pipeline components"""
        try:
            logger.info("Initializing AI pipeline components...")
            
            if not AI_MODULES_AVAILABLE:
                logger.warning("⚠️ AI modules not available - running in fallback mode")
                return
            
            # Initialize LangChain foundation
            logger.info("1. Initializing LangChain foundation...")
            try:
                self.langchain_core = get_langchain_core()
                if self.langchain_core and hasattr(self.langchain_core, 'initialized') and self.langchain_core.initialized:
                    logger.info("✅ LangChain foundation initialized successfully")
                else:
                    logger.warning("⚠️ LangChain foundation initialization incomplete")
            except Exception as e:
                logger.warning(f"⚠️ LangChain foundation failed to initialize: {e}")
            
            # Initialize story generator
            logger.info("2. Initializing story generator...")
            try:
                self.story_generator = get_story_generator()
                if self.story_generator and hasattr(self.story_generator, 'initialized') and self.story_generator.initialized:
                    logger.info("✅ Story generator initialized successfully")
                else:
                    logger.warning("⚠️ Story generator initialization incomplete")
            except Exception as e:
                logger.warning(f"⚠️ Story generator failed to initialize: {e}")
            
            # Initialize image generator
            logger.info("3. Initializing image generator...")
            try:
                self.image_generator = get_image_generator()
                if self.image_generator and hasattr(self.image_generator, 'initialized') and self.image_generator.initialized:
                    logger.info("✅ Image generator initialized successfully")
                else:
                    logger.warning("⚠️ Image generator initialization incomplete")
            except Exception as e:
                logger.warning(f"⚠️ Image generator failed to initialize: {e}")
            
            # Initialize image processor
            logger.info("4. Initializing image processor...")
            try:
                self.image_processor = get_image_processor()
                if self.image_processor and hasattr(self.image_processor, 'initialized') and self.image_processor.initialized:
                    logger.info("✅ Image processor initialized successfully")
                else:
                    logger.warning("⚠️ Image processor initialization incomplete")
            except Exception as e:
                logger.warning(f"⚠️ Image processor failed to initialize: {e}")
            
            logger.info("🎉 AI pipeline components initialization completed!")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI pipelines: {e}")
            logger.error(traceback.format_exc())
    
    def _create_session_directory(self, session_id: str) -> str:
        """Create session-specific directory for organizing files"""
        try:
            # Import Django settings to get MEDIA_ROOT
            from django.conf import settings
            
            # Create session directory in Django's media folder
            session_dir = Path(settings.MEDIA_ROOT) / "sessions" / session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories for different types of content
            (session_dir / "story").mkdir(exist_ok=True)
            (session_dir / "images").mkdir(exist_ok=True)
            (session_dir / "processed").mkdir(exist_ok=True)
            (session_dir / "final").mkdir(exist_ok=True)
            
            logger.info(f"Session directory created: {session_dir}")
            return str(session_dir)
            
        except ImportError:
            # Fallback if Django settings not available
            logger.warning("Django settings not available, using fallback directory")
            try:
                # Create in current directory with media subfolder
                fallback_dir = Path(".") / "media" / "sessions" / session_id
                fallback_dir.mkdir(parents=True, exist_ok=True)
                (fallback_dir / "story").mkdir(exist_ok=True)
                (fallback_dir / "images").mkdir(exist_ok=True)
                (fallback_dir / "processed").mkdir(exist_ok=True)
                (fallback_dir / "final").mkdir(exist_ok=True)
                logger.info(f"Fallback session directory created: {fallback_dir}")
                return str(fallback_dir)
            except Exception as fallback_error:
                logger.error(f"Failed to create fallback directory: {fallback_error}")
                # Last resort - use current directory
                return str(Path(".").resolve())
        except Exception as e:
            logger.error(f"Failed to create session directory: {e}")
            # Fallback to current directory with session subfolder
            try:
                fallback_dir = Path(".") / "media" / "sessions" / session_id
                fallback_dir.mkdir(parents=True, exist_ok=True)
                (fallback_dir / "story").mkdir(exist_ok=True)
                (fallback_dir / "images").mkdir(exist_ok=True)
                (fallback_dir / "processed").mkdir(exist_ok=True)
                (fallback_dir / "final").mkdir(exist_ok=True)
                logger.info(f"Fallback session directory created: {fallback_dir}")
                return str(fallback_dir)
            except Exception as fallback_error:
                logger.error(f"Failed to create fallback directory: {fallback_error}")
                # Last resort - use current directory
                return str(Path(".").resolve())
    
    def _update_workflow_status(self, step: str, status: str, details: str = "", error: str = ""):
        """Update workflow status tracking"""
        self.workflow_status[step] = {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "error": error
        }
        
        # Print progress to console
        status_symbol = "✅" if status == "completed" else "❌" if status == "failed" else "🔄"
        print(f"{status_symbol} {step}: {status}")
        if details:
            print(f"   Details: {details}")
        if error:
            print(f"   Error: {error}")
    
    def process_user_request(self, user_prompt: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main pipeline function that orchestrates the complete story generation workflow
        
        Args:
            user_prompt: User's story prompt/description
            session_id: Optional session ID, generates one if not provided
            
        Returns:
            Dictionary with complete workflow results and file paths
        """
        try:
            # Initialize session
            self.session_id = session_id or f"session_{uuid.uuid4().hex[:8]}"
            self.start_time = time.time()
            self.workflow_status = {}
            self.output_files = {}
            
            print(f"\n🚀 Starting Story Generation Pipeline")
            print(f"Session ID: {self.session_id}")
            print(f"User Prompt: {user_prompt}")
            print("=" * 60)
            
            # Create session directory
            self.session_dir = self._create_session_directory(self.session_id)
            
            # Step 1: Generate story and descriptions using LangChain
            story_result = self._generate_story_content(user_prompt)
            
            # Step 2: Generate character image
            character_result = self._generate_character_image(story_result)
            
            # Step 3: Generate background image
            background_result = self._generate_background_image(story_result)
            
            # Step 4: Remove background from character image
            processed_character = self._process_character_image(character_result)
            
            # Step 5: Merge character and background into final scene
            final_scene = self._create_final_scene(processed_character, background_result)
            
            # Step 6: Compile final results
            final_result = self._compile_final_results(
                story_result, character_result, background_result, 
                processed_character, final_scene
            )
            
            # Calculate total time
            total_time = time.time() - self.start_time
            
            print("\n" + "=" * 60)
            print(f"🎉 Story Generation Pipeline Completed!")
            print(f"Total Time: {total_time:.2f} seconds")
            print(f"Session ID: {self.session_id}")
            print("=" * 60)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            logger.error(traceback.format_exc())
            
            self._update_workflow_status(
                "pipeline_execution", "failed", 
                "Pipeline execution failed", str(e)
            )
            
            return {
                "status": "error",
                "session_id": self.session_id,
                "error": str(e),
                "workflow_status": self.workflow_status,
                "partial_results": self.output_files
            }
    
    def _generate_story_content(self, user_prompt: str) -> Dict[str, Any]:
        """Step 1: Generate story and descriptions using LangChain"""
        try:
            self._update_workflow_status("story_generation", "in_progress", "Generating story content...")
            
            if not self.story_generator or not self.story_generator.initialized:
                raise RuntimeError("Story generator not available")
            
            # Generate story content
            story_result = self.story_generator.generate_story(user_prompt)
            
            if story_result["status"] == "success":
                # Save story to file
                story_file = Path(self.session_dir) / "story" / "generated_story.txt"
                with open(story_file, 'w', encoding='utf-8') as f:
                    f.write(f"User Prompt: {user_prompt}\n\n")
                    f.write(f"Generated Story:\n{story_result['content']}\n\n")
                    f.write(f"Character Descriptions:\n{story_result['character_desc']}\n\n")
                    f.write(f"Background Descriptions:\n{story_result['background_desc']}")
                
                self.output_files["story"] = str(story_file)
                
                self._update_workflow_status(
                    "story_generation", "completed", 
                    f"Story generated successfully: {story_file.name}"
                )
                
                return story_result
            else:
                raise RuntimeError(f"Story generation failed: {story_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            self._update_workflow_status(
                "story_generation", "failed", 
                "Story generation failed", str(e)
            )
            raise

    def _generate_story(self, user_prompt: str) -> Dict[str, Any]:
        """Generate story text only (for story-only generation)"""
        try:
            # Ensure session directory is set
            if not self.session_dir:
                raise RuntimeError("Session directory not initialized")
            
            # Check if story generator is available
            if not self.story_generator or not hasattr(self.story_generator, 'initialized') or not self.story_generator.initialized:
                # Fallback: generate a simple story
                logger.warning("Story generator not available, using fallback mode")
                return self._generate_fallback_story(user_prompt)
            
            # Generate story content using AI
            story_result = self.story_generator.generate_story(user_prompt)
            
            if story_result["status"] == "success":
                # Save story to file
                story_file = Path(self.session_dir) / "story" / "generated_story.txt"
                story_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(story_file, 'w', encoding='utf-8') as f:
                    f.write(f"User Prompt: {user_prompt}\n\n")
                    f.write(f"Generated Story:\n{story_result['content']}\n\n")
                    f.write(f"Character Descriptions:\n{story_result['character_desc']}\n\n")
                    f.write(f"Background Descriptions:\n{story_result['background_desc']}")
                
                self.output_files["story"] = str(story_file)
                
                return story_result
            else:
                raise RuntimeError(f"Story generation failed: {story_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            raise
    
    def _generate_fallback_story(self, user_prompt: str) -> Dict[str, Any]:
        """Generate a simple fallback story when AI is not available"""
        try:
            # Create a simple story based on the prompt
            story_content = f"""Once upon a time, there was a world where {user_prompt}. 

The story begins with a sense of wonder and possibility. Characters move through this narrative landscape, each carrying their own hopes and dreams.

As the tale unfolds, we discover that every challenge is an opportunity for growth, and every moment holds the potential for magic.

The end of this story is not really an ending, but a new beginning - for stories live on in the hearts of those who hear them."""
            
            character_desc = f"A protagonist inspired by: {user_prompt}"
            background_desc = f"A setting that reflects: {user_prompt}"
            
            # Save story to file
            story_file = Path(self.session_dir) / "story" / "generated_story.txt"
            story_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(story_file, 'w', encoding='utf-8') as f:
                f.write(f"User Prompt: {user_prompt}\n\n")
                f.write(f"Generated Story:\n{story_content}\n\n")
                f.write(f"Character Descriptions:\n{character_desc}\n\n")
                f.write(f"Background Descriptions:\n{background_desc}")
            
            self.output_files["story"] = str(story_file)
            
            return {
                "status": "success",
                "content": story_content,
                "character_desc": character_desc,
                "background_desc": background_desc
            }
            
        except Exception as e:
            logger.error(f"Fallback story generation failed: {e}")
            raise
    
    def _generate_character_image(self, story_result: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Generate character image from character description"""
        try:
            self._update_workflow_status("character_generation", "in_progress", "Generating character image...")
            
            if not self.image_generator or not self.image_generator.initialized:
                raise RuntimeError("Image generator not available")
            
            # Extract character description
            character_desc = story_result.get("character_desc", "A mysterious character")
            
            # Generate character image
            character_file = Path(self.session_dir) / "images" / "character.png"
            character_result = self.image_generator.generate_character_image(
                character_desc, str(character_file)
            )
            
            if character_result["status"] == "success":
                self.output_files["character_image"] = str(character_file)
                
                self._update_workflow_status(
                    "character_generation", "completed", 
                    f"Character image generated: {character_file.name}"
                )
                
                return character_result
            else:
                raise RuntimeError(f"Character generation failed: {character_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Character generation failed: {e}")
            self._update_workflow_status(
                "character_generation", "failed", 
                "Character generation failed", str(e)
            )
            raise
    
    def _generate_background_image(self, story_result: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Generate background image from background description"""
        try:
            self._update_workflow_status("background_generation", "in_progress", "Generating background image...")
            
            if not self.image_generator or not self.image_generator.initialized:
                raise RuntimeError("Image generator not available")
            
            # Extract background description
            background_desc = story_result.get("background_desc", "A mysterious location")
            
            # Generate background image
            background_file = Path(self.session_dir) / "images" / "background.png"
            background_result = self.image_generator.generate_background_image(
                background_desc, str(background_file)
            )
            
            if background_result["status"] == "success":
                self.output_files["background_image"] = str(background_file)
                
                self._update_workflow_status(
                    "background_generation", "completed", 
                    f"Background image generated: {background_file.name}"
                )
                
                return background_result
            else:
                raise RuntimeError(f"Background generation failed: {background_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Background generation failed: {e}")
            self._update_workflow_status(
                "background_generation", "failed", 
                "Background generation failed", str(e)
            )
            raise
    
    def _process_character_image(self, character_result: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Remove background from character image"""
        try:
            self._update_workflow_status("character_processing", "in_progress", "Processing character image...")
            
            if not self.image_processor or not self.image_processor.initialized:
                raise RuntimeError("Image processor not available")
            
            # Remove background from character image
            character_path = character_result["output_path"]
            processed_file = Path(self.session_dir) / "processed" / "character_no_bg.png"
            
            process_result = self.image_processor.remove_background(
                character_path, str(processed_file)
            )
            
            if process_result["status"] == "success":
                self.output_files["processed_character"] = str(processed_file)
                
                self._update_workflow_status(
                    "character_processing", "completed", 
                    f"Character background removed: {processed_file.name}"
                )
                
                return process_result
            else:
                raise RuntimeError(f"Character processing failed: {process_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Character processing failed: {e}")
            self._update_workflow_status(
                "character_processing", "failed", 
                "Character processing failed", str(e)
            )
            raise
    
    def _create_final_scene(self, processed_character: Dict[str, Any], background_result: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Merge character and background into final scene"""
        try:
            self._update_workflow_status("scene_compositing", "in_progress", "Creating final scene...")
            
            if not self.image_processor or not self.image_processor.initialized:
                raise RuntimeError("Image processor not available")
            
            # Merge character and background
            character_path = processed_character["output_path"]
            background_path = background_result["output_path"]
            final_file = Path(self.session_dir) / "final" / "final_scene.png"
            
            merge_result = self.image_processor.merge_images(
                character_path, background_path, str(final_file)
            )
            
            if merge_result["status"] == "success":
                self.output_files["final_scene"] = str(final_file)
                
                self._update_workflow_status(
                    "scene_compositing", "completed", 
                    f"Final scene created: {final_file.name}"
                )
                
                return merge_result
            else:
                raise RuntimeError(f"Scene compositing failed: {merge_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Scene compositing failed: {e}")
            self._update_workflow_status(
                "scene_compositing", "failed", 
                "Scene compositing failed", str(e)
            )
            raise
    
    def _compile_final_results(self, story_result: Dict[str, Any], character_result: Dict[str, Any], 
                             background_result: Dict[str, Any], processed_character: Dict[str, Any], 
                             final_scene: Dict[str, Any]) -> Dict[str, Any]:
        """Step 6: Compile all results into final response"""
        try:
            self._update_workflow_status("result_compilation", "in_progress", "Compiling final results...")
            
            # Calculate total time
            total_time = time.time() - self.start_time
            
            # Create comprehensive result
            final_result = {
                "status": "success",
                "session_id": self.session_id,
                "total_time_seconds": round(total_time, 2),
                "workflow_status": self.workflow_status,
                "output_files": self.output_files,
                "results": {
                    "story": {
                        "content": story_result.get("content", ""),
                        "character_descriptions": story_result.get("character_desc", ""),
                        "background_descriptions": story_result.get("background_desc", ""),
                        "file_path": self.output_files.get("story", "")
                    },
                    "images": {
                        "character": {
                            "file_path": self.output_files.get("character_image", ""),
                            "generation_details": character_result
                        },
                        "background": {
                            "file_path": self.output_files.get("background_image", ""),
                            "generation_details": background_result
                        },
                        "processed_character": {
                            "file_path": self.output_files.get("processed_character", ""),
                            "processing_details": processed_character
                        },
                        "final_scene": {
                            "file_path": self.output_files.get("final_scene", ""),
                            "compositing_details": final_scene
                        }
                    }
                },
                "session_directory": self.session_dir,
                "timestamp": datetime.now().isoformat()
            }
            
            self._update_workflow_status(
                "result_compilation", "completed", 
                "Final results compiled successfully"
            )
            
            return final_result
            
        except Exception as e:
            logger.error(f"Result compilation failed: {e}")
            self._update_workflow_status(
                "result_compilation", "failed", 
                "Result compilation failed", str(e)
            )
            raise
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "session_id": self.session_id,
            "workflow_status": self.workflow_status,
            "output_files": self.output_files,
            "session_directory": self.session_dir
        }

    def generate_story_only(self, prompt_text: str, session_id: str) -> Dict[str, Any]:
        """Generate only the story text without images"""
        try:
            self.session_id = session_id
            self.start_time = time.time()
            
            # Create session directory and ensure it's set
            self.session_dir = self._create_session_directory(session_id)
            if not self.session_dir:
                raise RuntimeError("Failed to create session directory")
            
            logger.info(f"🚀 Starting Story-Only Generation Pipeline")
            logger.info(f"Session ID: {session_id}")
            logger.info(f"User Prompt: {prompt_text}")
            logger.info("=" * 60)
            
            # Generate story
            self._update_workflow_status("story_generation", "in_progress", "Generating story content...")
            story_result = self._generate_story(prompt_text)
            
            if not story_result:
                raise RuntimeError("Story generation failed")
            
            # Compile results
            final_result = {
                "status": "success",
                "session_id": session_id,
                "results": {
                    "story": story_result
                },
                "output_files": self.output_files,
                "total_time_seconds": time.time() - self.start_time,
                "workflow_status": self.workflow_status
            }
            
            logger.info("✅ Story-only generation completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"Story-only generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "session_id": session_id
            }

    def generate_character_only(self, prompt_text: str, session_id: str) -> Dict[str, Any]:
        """Generate only character image from prompt"""
        try:
            self.session_id = session_id
            self.start_time = time.time()
            
            # Create session directory and ensure it's set
            self.session_dir = self._create_session_directory(session_id)
            if not self.session_dir:
                raise RuntimeError("Failed to create session directory")
            
            logger.info(f"🚀 Starting Character-Only Generation Pipeline")
            logger.info(f"Session ID: {session_id}")
            logger.info(f"User Prompt: {prompt_text}")
            logger.info("=" * 60)
            
            # Generate character image
            self._update_workflow_status("character_generation", "in_progress", "Generating character image...")
            character_result = self._generate_character_image_from_prompt(prompt_text)
            
            if not character_result:
                raise RuntimeError("Character generation failed")
            
            # Compile results
            final_result = {
                "status": "success",
                "session_id": session_id,
                "results": {
                    "character": character_result
                },
                "output_files": {
                    "character_image": character_result.get("file_path", "")
                },
                "total_time_seconds": time.time() - self.start_time,
                "workflow_status": self.workflow_status
            }
            
            logger.info("✅ Character-only generation completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"Character-only generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "session_id": session_id
            }

    def generate_background_only(self, prompt_text: str, session_id: str) -> Dict[str, Any]:
        """Generate only background image from prompt"""
        try:
            self.session_id = session_id
            self.start_time = time.time()
            
            # Create session directory and ensure it's set
            self.session_dir = self._create_session_directory(session_id)
            if not self.session_dir:
                raise RuntimeError("Failed to create session directory")
            
            logger.info(f"🚀 Starting Background-Only Generation Pipeline")
            logger.info(f"Session ID: {session_id}")
            logger.info(f"User Prompt: {prompt_text}")
            logger.info("=" * 60)
            
            # Generate background image
            self._update_workflow_status("background_generation", "in_progress", "Generating background image...")
            background_result = self._generate_background_image_from_prompt(prompt_text)
            if not background_result:
                raise RuntimeError("Background generation failed")
            
            # Compile results
            final_result = {
                "status": "success",
                "session_id": session_id,
                "results": {
                    "background": background_result
                },
                "output_files": {
                    "background_image": background_result.get("file_path", "")
                },
                "total_time_seconds": time.time() - self.start_time,
                "workflow_status": self.workflow_status
            }
            
            logger.info("✅ Background-only generation completed successfully")
            return final_result
            
        except Exception as e:
            logger.error(f"Background-only generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "session_id": session_id
            }

    def merge_images_only(self, prompt_text: str, session_id: str, image1_path: str = None, image2_path: str = None) -> Dict[str, Any]:
        """Merge existing character and background images"""
        try:
            logger.info(f"merge_images_only called with:")
            logger.info(f"  prompt_text: {prompt_text}")
            logger.info(f"  session_id: {session_id}")
            logger.info(f"  image1_path: {image1_path}")
            logger.info(f"  image2_path: {image2_path}")
            
            self.session_id = session_id
            self.start_time = time.time()
            
            logger.info(f"Creating session directory for session_id: {session_id}")
            self._create_session_directory(session_id)
            
            logger.info(f"🚀 Starting Image Merging Pipeline")
            logger.info(f"Session ID: {session_id}")
            logger.info(f"User Prompt: {prompt_text}")
            logger.info("=" * 60)
            
            # Check if we have image paths
            if not image1_path or not image2_path:
                logger.warning("Image paths not provided for merging")
                return {
                    "status": "failed",
                    "error": "Both image1_path and image2_path are required for merging",
                    "session_id": session_id
                }
            
            # Check if images exist
            if not os.path.exists(image1_path) or not os.path.exists(image2_path):
                logger.warning("One or both images do not exist")
                return {
                    "status": "failed",
                    "error": "One or both images not found",
                    "session_id": session_id
                }
            
            # Create merged image path
            merged_path = Path(self.session_dir) / "images" / "merged.png"
            merged_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform image merging
            logger.info("Merging images...")
            merge_success = self._merge_two_images(image1_path, image2_path, str(merged_path))
            
            if merge_success and merged_path.exists():
                logger.info("✅ Image merging completed successfully")
                
                # Compile results
                final_result = {
                    "status": "success",
                    "session_id": session_id,
                    "results": {
                        "merge_info": f"Successfully merged {os.path.basename(image1_path)} and {os.path.basename(image2_path)}"
                    },
                    "output_files": {
                        "merged_image": str(merged_path)
                    },
                    "total_time_seconds": time.time() - self.start_time,
                    "workflow_status": self.workflow_status
                }
                
                return final_result
            else:
                logger.error("Image merging failed")
                return {
                    "status": "failed",
                    "error": "Failed to merge images",
                    "session_id": session_id
                }
                
        except Exception as e:
            logger.error(f"Image merging failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "session_id": session_id
            }
    
    def _merge_two_images(self, image1_path: str, image2_path: str, output_path: str) -> bool:
        """Merge two images side by side"""
        try:
            from PIL import Image
            
            # Open both images
            img1 = Image.open(image1_path)
            img2 = Image.open(image2_path)
            
            # Resize images to same height for better merging
            target_height = 512
            img1_resized = img1.resize((int(img1.width * target_height / img1.height), target_height), Image.Resampling.LANCZOS)
            img2_resized = img2.resize((int(img2.width * target_height / img2.height), target_height), Image.Resampling.LANCZOS)
            
            # Calculate total width
            total_width = img1_resized.width + img2_resized.width
            
            # Create new image with combined width
            merged_image = Image.new('RGB', (total_width, target_height), (255, 255, 255))
            
            # Paste images side by side
            merged_image.paste(img1_resized, (0, 0))
            merged_image.paste(img2_resized, (img1_resized.width, 0))
            
            # Save merged image
            merged_image.save(output_path, 'PNG')
            
            logger.info(f"Merged image saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to merge images: {e}")
            return False

    def _generate_character_image_from_prompt(self, prompt_text: str) -> Optional[Dict[str, Any]]:
        """Generate character image directly from prompt"""
        try:
            # Ensure session directory is set
            if not self.session_dir:
                raise RuntimeError("Session directory not initialized")
            
            # Check if image generator is available
            if not self.image_generator or not hasattr(self.image_generator, 'initialized') or not self.image_generator.initialized:
                # Fallback: create a placeholder image or return info
                logger.warning("Image generator not available, using fallback mode")
                return self._generate_fallback_character_image(prompt_text)
            
            # Create a simple character description from the prompt
            character_desc = f"Character: {prompt_text}"
            
            # Generate character image
            character_path = Path(self.session_dir) / "images" / "character.png"
            character_path.parent.mkdir(parents=True, exist_ok=True)
            
            result = self.image_generator.generate_character_image(character_desc, str(character_path))
            
            if result and character_path.exists():
                return {
                    "status": "success",
                    "file_path": str(character_path),
                    "description": character_desc
                }
            else:
                return {
                    "status": "failed",
                    "error": "Character image generation failed"
                }
                
        except Exception as e:
            logger.error(f"Character image generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _generate_fallback_character_image(self, prompt_text: str) -> Dict[str, Any]:
        """Generate a fallback character image when AI is not available"""
        try:
            # Create a placeholder text file instead of an image
            character_path = Path(self.session_dir) / "images" / "character_placeholder.txt"
            character_path.parent.mkdir(parents=True, exist_ok=True)
            
            placeholder_content = f"""Character Image Placeholder
Generated from prompt: {prompt_text}

This is a placeholder for a character image that would be generated using AI.
In a full implementation, this would be a PNG image file.

Character Description: {prompt_text}
Generated at: {datetime.now().isoformat()}
"""
            
            with open(character_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            
            return {
                "status": "success",
                "file_path": str(character_path),
                "description": f"Character: {prompt_text} (placeholder)",
                "is_placeholder": True
            }
            
        except Exception as e:
            logger.error(f"Fallback character image generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _generate_background_image_from_prompt(self, prompt_text: str) -> Optional[Dict[str, Any]]:
        """Generate background image directly from prompt"""
        try:
            # Ensure session directory is set
            if not self.session_dir:
                raise RuntimeError("Session directory not initialized")
            
            # Check if image generator is available
            if not self.image_generator or not hasattr(self.image_generator, 'initialized') or not self.image_generator.initialized:
                # Fallback: create a placeholder image or return info
                logger.warning("Image generator not available, using fallback mode")
                return self._generate_fallback_background_image(prompt_text)
            
            # Create a simple background description from the prompt
            background_desc = f"Background: {prompt_text}"
            
            # Generate background image
            background_path = Path(self.session_dir) / "images" / "background.png"
            background_path.parent.mkdir(parents=True, exist_ok=True)
            
            result = self.image_generator.generate_background_image(background_desc, str(background_path))
            
            if result and background_path.exists():
                return {
                    "status": "success",
                    "file_path": str(background_path),
                    "description": background_desc
                }
            else:
                return {
                    "status": "failed",
                    "error": "Background image generation failed"
                }
                
        except Exception as e:
            logger.error(f"Background image generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _generate_fallback_background_image(self, prompt_text: str) -> Dict[str, Any]:
        """Generate a fallback background image when AI is not available"""
        try:
            # Create a placeholder text file instead of an image
            background_path = Path(self.session_dir) / "images" / "background_placeholder.txt"
            background_path.parent.mkdir(parents=True, exist_ok=True)
            
            placeholder_content = f"""Background Image Placeholder
Generated from prompt: {prompt_text}

This is a placeholder for a background image that would be generated using AI.
In a full implementation, this would be a PNG image file.

Background Description: {prompt_text}
Generated at: {datetime.now().isoformat()}
"""
            
            with open(background_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            
            return {
                "status": "success",
                "file_path": str(background_path),
                "description": f"Background: {prompt_text} (placeholder)",
                "is_placeholder": True
            }
            
        except Exception as e:
            logger.error(f"Fallback background image generation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def cleanup_session(self):
        """Clean up session files (optional)"""
        try:
            if self.session_dir and os.path.exists(self.session_dir):
                import shutil
                shutil.rmtree(self.session_dir)
                logger.info(f"Session directory cleaned up: {self.session_dir}")
        except Exception as e:
            logger.error(f"Failed to cleanup session: {e}")


# Global instance for easy access
story_orchestrator = None

def get_story_orchestrator() -> StoryOrchestrator:
    """Get or create the global story orchestrator instance"""
    global story_orchestrator
    if story_orchestrator is None:
        story_orchestrator = StoryOrchestrator()
    return story_orchestrator


def test_orchestrator():
    """Test the complete orchestrator pipeline"""
    try:
        print("🧪 Testing Story Orchestrator Pipeline...")
        print("This will test the complete workflow from prompt to final images.")
        print("=" * 60)
        
        # Get orchestrator instance
        orchestrator = get_story_orchestrator()
        
        # Test prompt
        test_prompt = "A brave knight discovers a magical forest where trees whisper ancient secrets"
        
        # Run complete pipeline
        result = orchestrator.process_user_request(test_prompt, "test_session")
        
        if result["status"] == "success":
            print("\n🎉 Orchestrator test completed successfully!")
            print(f"Session ID: {result['session_id']}")
            print(f"Total Time: {result['total_time_seconds']} seconds")
            print(f"Session Directory: {result['session_directory']}")
            
            print("\nGenerated Files:")
            for file_type, file_path in result['output_files'].items():
                print(f"  {file_type}: {file_path}")
            
            return True
        else:
            print(f"\n❌ Orchestrator test failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Orchestrator test failed with error: {e}")
        logger.exception("Orchestrator test error")
        return False


if __name__ == "__main__":
    # Run test if executed directly
    success = test_orchestrator()
    if success:
        print("\n✅ All tests passed! Your story orchestrator is working correctly.")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")

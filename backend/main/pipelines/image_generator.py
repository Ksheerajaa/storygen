"""
Image Generation Pipeline using Stable Diffusion
This module provides AI-powered image generation for characters and backgrounds
using the free Stable Diffusion model from Hugging Face.
"""

import os
import logging
import torch
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image
import numpy as np

# Import diffusers components
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
from diffusers.utils import logging as diffusers_logging

# Set up logging
logger = logging.getLogger(__name__)

# Reduce diffusers logging verbosity
diffusers_logging.set_verbosity_error()


class ImageGenerator:
    """
    AI Image Generator using Stable Diffusion
    Generates character portraits and background scenes from text descriptions
    """
    
    def __init__(self):
        self.model_name = "runwayml/stable-diffusion-v1-5"  # Free, high-quality model
        self.pipeline = None
        self.device = None
        self.initialized = False
        
        # Initialize the pipeline
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize the Stable Diffusion pipeline"""
        try:
            logger.info(f"Initializing Stable Diffusion with model: {self.model_name}")
            
            # Detect device (CUDA GPU or CPU)
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info("Using CUDA GPU for image generation")
            else:
                self.device = "cpu"
                logger.info("Using CPU for image generation (slower but works on all systems)")
            
            # Load the pipeline with memory optimization
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                use_safetensors=True,
                low_cpu_mem_usage=True
            )
            
            # Optimize for the detected device
            if self.device == "cuda":
                self.pipeline = self.pipeline.to(self.device)
                # Enable memory efficient attention if available
                if hasattr(self.pipeline, "enable_attention_slicing"):
                    self.pipeline.enable_attention_slicing()
                if hasattr(self.pipeline, "enable_vae_slicing"):
                    self.pipeline.enable_vae_slicing()
            else:
                # CPU optimizations
                self.pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
                    self.pipeline.scheduler.config
                )
            
            self.initialized = True
            logger.info("Stable Diffusion pipeline initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize Stable Diffusion pipeline: {e}")
            self.initialized = False
            raise
    
    def _optimize_prompt(self, description: str, prompt_type: str = "character") -> str:
        """
        Optimize text description for better image generation
        
        Args:
            description: User's description
            prompt_type: Either 'character' or 'background'
            
        Returns:
            Optimized prompt for Stable Diffusion
        """
        # Clean and enhance the description
        clean_desc = description.strip().lower()
        
        if prompt_type == "character":
            # Character-specific prompt engineering
            enhanced_prompt = f"{clean_desc}, high quality, detailed character portrait, " \
                            f"professional photography, sharp focus, studio lighting, " \
                            f"8k resolution, masterpiece, trending on artstation"
        else:
            # Background-specific prompt engineering
            enhanced_prompt = f"{clean_desc}, detailed background scene, cinematic, " \
                            f"high quality, professional photography, wide shot, " \
                            f"atmospheric, 8k resolution, masterpiece"
        
        # Add negative prompts to avoid common issues
        negative_prompt = "blurry, low quality, distorted, deformed, ugly, " \
                         "bad anatomy, watermark, signature, text, error"
        
        return enhanced_prompt, negative_prompt
    
    def generate_character_image(self, character_description: str, output_path: str) -> Dict[str, Any]:
        """
        Generate a character portrait image from description
        
        Args:
            character_description: Text description of the character
            output_path: Where to save the generated image
            
        Returns:
            Dictionary with generation results and metadata
        """
        if not self.initialized:
            raise RuntimeError("Image generator not initialized")
        
        try:
            logger.info(f"Generating character image for: {character_description[:50]}...")
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Optimize the prompt for character generation
            enhanced_prompt, negative_prompt = self._optimize_prompt(
                character_description, "character"
            )
            
            # Generate the image
            logger.info("Starting image generation...")
            result = self.pipeline(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=20,  # Balance between quality and speed
                guidance_scale=7.5,      # How closely to follow the prompt
                width=512,               # Standard Stable Diffusion size
                height=512,              # Square aspect ratio for portraits
                generator=torch.Generator(device=self.device).manual_seed(42)  # Reproducible results
            )
            
            # Extract the generated image
            generated_image = result.images[0]
            
            # Save the image
            generated_image.save(output_path, "PNG", quality=95)
            
            logger.info(f"Character image generated successfully: {output_path}")
            
            return {
                "status": "success",
                "output_path": output_path,
                "prompt_used": enhanced_prompt,
                "image_size": generated_image.size,
                "generation_time": "completed"
            }
            
        except Exception as e:
            logger.error(f"Character image generation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "output_path": output_path
            }
    
    def generate_background_image(self, background_description: str, output_path: str) -> Dict[str, Any]:
        """
        Generate a background scene image from description
        
        Args:
            background_description: Text description of the background
            output_path: Where to save the generated image
            
        Returns:
            Dictionary with generation results and metadata
        """
        if not self.initialized:
            raise RuntimeError("Image generator not initialized")
        
        try:
            logger.info(f"Generating background image for: {background_description[:50]}...")
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Optimize the prompt for background generation
            enhanced_prompt, negative_prompt = self._optimize_prompt(
                background_description, "background"
            )
            
            # Generate the image with landscape orientation
            logger.info("Starting background generation...")
            result = self.pipeline(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=25,  # More steps for complex backgrounds
                guidance_scale=8.0,      # Slightly higher for backgrounds
                width=768,               # Wider for landscape scenes
                height=512,              # Landscape aspect ratio
                generator=torch.Generator(device=self.device).manual_seed(42)
            )
            
            # Extract the generated image
            generated_image = result.images[0]
            
            # Save the image
            generated_image.save(output_path, "PNG", quality=95)
            
            logger.info(f"Background image generated successfully: {output_path}")
            
            return {
                "status": "success",
                "output_path": output_path,
                "prompt_used": enhanced_prompt,
                "image_size": generated_image.size,
                "generation_time": "completed"
            }
            
        except Exception as e:
            logger.error(f"Background image generation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "output_path": output_path
            }
    
    def test_pipeline(self) -> Dict[str, Any]:
        """Test the image generation pipeline"""
        try:
            logger.info("Testing image generation pipeline...")
            
            # Test character generation
            test_desc = "A wise old wizard with a long white beard and blue robes"
            test_output = "test_character.png"
            
            result = self.generate_character_image(test_desc, test_output)
            
            if result["status"] == "success":
                logger.info("Pipeline test completed successfully")
                return {
                    "status": "success",
                    "test_result": result,
                    "message": "Image generation pipeline is working correctly"
                }
            else:
                return {
                    "status": "error",
                    "error": result.get("error", "Unknown error during test")
                }
                
        except Exception as e:
            logger.error(f"Pipeline test failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global instance for easy access
image_generator = None

def get_image_generator() -> ImageGenerator:
    """Get or create the global image generator instance"""
    global image_generator
    if image_generator is None:
        image_generator = ImageGenerator()
    return image_generator


def initialize_image_generation() -> bool:
    """Initialize the image generation system"""
    try:
        generator = get_image_generator()
        return generator.initialized
    except Exception as e:
        logger.error(f"Failed to initialize image generation: {e}")
        return False

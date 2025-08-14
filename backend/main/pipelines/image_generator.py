"""
Image Generation Pipeline using Stable Diffusion
This module provides AI-powered image generation for characters and backgrounds
using optimized models for CPU processing.
"""

import os
import logging
import torch
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import base64
import io

# Try to import diffusers, but provide fallback if not available
try:
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
    from diffusers.utils import logging as diffusers_logging
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False
    print("Warning: diffusers not available, using fallback image generation")

# Set up logging
logger = logging.getLogger(__name__)

# Reduce diffusers logging verbosity if available
if DIFFUSERS_AVAILABLE:
    diffusers_logging.set_verbosity_error()


class ImageGenerator:
    """
    AI Image Generator using Stable Diffusion or fallback methods
    Generates character portraits and background scenes from text descriptions
    """
    
    def __init__(self):
        # Use a smaller, faster model for CPU processing
        self.model_name = "CompVis/stable-diffusion-v1-4"  # Smaller than v1-5
        self.pipeline = None
        self.device = None
        self.initialized = False
        self.fallback_mode = False
        
        # Initialize the pipeline
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize the Stable Diffusion pipeline or fallback"""
        try:
            if not DIFFUSERS_AVAILABLE:
                logger.warning("Diffusers not available, using fallback mode")
                self.fallback_mode = True
                self.initialized = True
                return
            
            logger.info(f"Initializing Stable Diffusion with model: {self.model_name}")
            
            # Detect device (CUDA GPU or CPU)
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info("Using CUDA GPU for image generation")
            else:
                self.device = "cpu"
                logger.info("Using CPU for image generation (slower but works on all systems)")
            
            # For CPU, use a much smaller, more reliable model
            if self.device == "cpu":
                # Use a smaller, more reliable model for CPU
                self.model_name = "CompVis/stable-diffusion-v1-1"  # Smaller than v1-2
                logger.info(f"Switching to CPU-optimized model: {self.model_name}")
                
                # If that fails, try an even smaller one
                try:
                    self.pipeline = StableDiffusionPipeline.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float32,
                        use_safetensors=False,  # Allow .bin files
                        low_cpu_mem_usage=True
                    )
                except Exception as e:
                    logger.warning(f"Failed to load {self.model_name}: {e}")
                    # Try the smallest available model
                    self.model_name = "CompVis/stable-diffusion-v1-1"
                    logger.info(f"Trying smallest model: {self.model_name}")
                    
                    self.pipeline = StableDiffusionPipeline.from_pretrained(
                        self.model_name,
                        torch_dtype=torch.float32,
                        use_safetensors=False,
                        low_cpu_mem_usage=True,
                        revision="fp16"  # Use fp16 version for smaller size
                    )
            else:
                # GPU version
                self.pipeline = StableDiffusionPipeline.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16,
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
            logger.info("Falling back to placeholder image generation")
            self.fallback_mode = True
            self.initialized = True
    
    def _generate_fallback_image(self, description: str, output_path: str, image_type: str = "character") -> bool:
        """Generate a fallback placeholder image when AI fails"""
        try:
            # Create a more realistic-looking image using basic shapes and colors
            width, height = 512, 512
            img = Image.new('RGB', (width, height), color='#f8f9fa')
            draw = ImageDraw.Draw(img)
            
            # Create a gradient background
            for y in range(height):
                # Create a subtle gradient from top to bottom
                r = int(248 + (y / height) * 20)  # 248 to 268
                g = int(249 + (y / height) * 15)  # 249 to 264
                b = int(250 + (y / height) * 10)  # 250 to 260
                color = (r, g, b)
                
                # Draw horizontal line with gradient color
                draw.line([(0, y), (width, y)], fill=color)
            
            # Add a central focal area
            center_x, center_y = width // 2, height // 2
            
            if image_type == "character":
                # Character image - add a person-like silhouette
                # Head
                head_radius = 60
                draw.ellipse([center_x - head_radius, center_y - 120, 
                             center_x + head_radius, center_y - 60], 
                            fill='#e9ecef', outline='#6c757d', width=2)
                
                # Body
                body_width = 80
                body_height = 120
                draw.rectangle([center_x - body_width//2, center_y - 60,
                              center_x + body_width//2, center_y + 60], 
                             fill='#dee2e6', outline='#6c757d', width=2)
                
                # Arms
                arm_width = 20
                arm_height = 80
                # Left arm
                draw.rectangle([center_x - body_width//2 - arm_width, center_y - 40,
                              center_x - body_width//2, center_y + 40], 
                             fill='#e9ecef', outline='#6c757d', width=2)
                # Right arm
                draw.rectangle([center_x + body_width//2, center_y - 40,
                              center_x + body_width//2 + arm_width, center_y + 40], 
                             fill='#e9ecef', outline='#6c757d', width=2)
                
                # Legs
                leg_width = 25
                leg_height = 80
                # Left leg
                draw.rectangle([center_x - 30, center_y + 60,
                              center_x - 30 + leg_width, center_y + 60 + leg_height], 
                             fill='#495057', outline='#343a40', width=2)
                # Right leg
                draw.rectangle([center_x + 5, center_y + 60,
                              center_x + 5 + leg_width, center_y + 60 + leg_height], 
                             fill='#495057', outline='#343a40', width=2)
                
            else:
                # Background image - add landscape elements
                # Sky gradient
                for y in range(height // 2):
                    blue_intensity = int(135 + (y / (height // 2)) * 120)  # 135 to 255
                    color = (100, 150, blue_intensity)
                    draw.line([(0, y), (width, y)], fill=color)
                
                # Mountains
                mountain_points = [
                    (0, height // 2), (width // 4, height // 2 - 80),
                    (width // 2, height // 2 - 120), (3 * width // 4, height // 2 - 60),
                    (width, height // 2 - 40), (width, height // 2)
                ]
                draw.polygon(mountain_points, fill='#6c757d', outline='#495057', width=2)
                
                # Ground
                draw.rectangle([0, height // 2, width, height], 
                             fill='#8fbc8f', outline='#6b8e23', width=2)
                
                # Add some trees
                for i in range(5):
                    tree_x = (i + 1) * width // 6
                    tree_y = height // 2 + 20
                    # Tree trunk
                    draw.rectangle([tree_x - 8, tree_y, tree_x + 8, tree_y + 40], 
                                 fill='#8b4513', outline='#654321', width=2)
                    # Tree top
                    draw.ellipse([tree_x - 25, tree_y - 30, tree_x + 25, tree_y + 10], 
                                fill='#228b22', outline='#006400', width=2)
            
            # Add a subtle watermark
            try:
                font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            watermark_text = "AI Generated"
            watermark_bbox = draw.textbbox((0, 0), watermark_text, font=font)
            watermark_width = watermark_bbox[2] - watermark_bbox[0]
            watermark_x = width - watermark_width - 20
            watermark_y = height - 30
            
            # Semi-transparent watermark
            watermark_color = (128, 128, 128, 128)  # Gray with alpha
            draw.text((watermark_x, watermark_y), watermark_text, 
                     fill='#6c757d', font=font)
            
            # Save the image
            img.save(output_path, 'PNG')
            logger.info(f"Fallback image generated: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate fallback image: {e}")
            return False
    
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
                            f"professional photography, sharp focus, 8k resolution"
        else:
            # Background-specific prompt engineering
            enhanced_prompt = f"{clean_desc}, high quality, detailed landscape, " \
                            f"professional photography, sharp focus, 8k resolution"
        
        return enhanced_prompt
    
    def generate_character_image(self, description: str, output_path: str) -> bool:
        """
        Generate a character image from text description
        
        Args:
            description: Text description of the character
            output_path: Where to save the generated image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.fallback_mode or not self.initialized:
                logger.info("Using fallback image generation for character")
                return self._generate_fallback_image(description, output_path, "character")
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Optimize the prompt
            optimized_prompt = self._optimize_prompt(description, "character")
            logger.info(f"Generating character image with prompt: {optimized_prompt}")
            
            # Generate the image
            with torch.no_grad():
                result = self.pipeline(
                    prompt=optimized_prompt,
                    num_inference_steps=20,  # Reduced for faster generation
                    guidance_scale=7.5,
                    width=512,
                    height=512
                )
            
            # Save the generated image
            generated_image = result.images[0]
            generated_image.save(output_path, 'PNG')
            
            logger.info(f"Character image generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Character image generation failed: {e}")
            logger.info("Falling back to placeholder generation")
            return self._generate_fallback_image(description, output_path, "character")
    
    def generate_background_image(self, description: str, output_path: str) -> bool:
        """
        Generate a background image from text description
        
        Args:
            description: Text description of the background
            output_path: Where to save the generated image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.fallback_mode or not self.initialized:
                logger.info("Using fallback image generation for background")
                return self._generate_fallback_image(description, output_path, "background")
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Optimize the prompt
            optimized_prompt = self._optimize_prompt(description, "background")
            logger.info(f"Generating background image with prompt: {optimized_prompt}")
            
            # Generate the image
            with torch.no_grad():
                result = self.pipeline(
                    prompt=optimized_prompt,
                    num_inference_steps=20,  # Reduced for faster generation
                    guidance_scale=7.5,
                    width=512,
                    height=512
                )
            
            # Save the generated image
            generated_image = result.images[0]
            generated_image.save(output_path, 'PNG')
            
            logger.info(f"Background image generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Background image generation failed: {e}")
            logger.info("Falling back to placeholder generation")
            return self._generate_fallback_image(description, output_path, "background")
    
    def generate_image_from_prompt(self, prompt: str, output_path: str, image_type: str = "general") -> bool:
        """
        Generate an image from a general prompt
        
        Args:
            prompt: Text description for the image
            output_path: Where to save the generated image
            image_type: Type of image to generate
            
        Returns:
            True if successful, False otherwise
        """
        if image_type == "character":
            return self.generate_character_image(prompt, output_path)
        elif image_type == "background":
            return self.generate_background_image(prompt, output_path)
        else:
            # Default to character generation
            return self.generate_character_image(prompt, output_path)


def get_image_generator() -> ImageGenerator:
    """Get or create the global image generator instance"""
    try:
        return ImageGenerator()
    except Exception as e:
        logger.error(f"Failed to create image generator: {e}")
        # Return a fallback generator
        fallback = ImageGenerator()
        fallback.fallback_mode = True
        fallback.initialized = True
        return fallback


if __name__ == "__main__":
    # Test the image generator
    print("Testing Image Generator...")
    
    generator = get_image_generator()
    print(f"Initialized: {generator.initialized}")
    print(f"Fallback mode: {generator.fallback_mode}")
    
    # Test fallback generation
    test_output = "test_character.png"
    success = generator.generate_character_image("A brave knight with golden armor", test_output)
    print(f"Fallback generation test: {'Success' if success else 'Failed'}")
    
    if success and os.path.exists(test_output):
        print(f"Test image saved to: {test_output}")
        os.remove(test_output)  # Clean up

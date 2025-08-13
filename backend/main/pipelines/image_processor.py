"""
Image Processing Pipeline
This module handles image post-processing including background removal,
image compositing, and basic adjustments using rembg and PIL.
"""

import os
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import numpy as np

# Import image processing libraries
from PIL import Image, ImageEnhance, ImageFilter
import cv2
from rembg import remove

# Set up logging
logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Image processing utilities for post-processing generated images
    Includes background removal, compositing, and basic adjustments
    """
    
    def __init__(self):
        self.initialized = True
        logger.info("Image processor initialized successfully")
    
    def remove_background(self, input_image_path: str, output_path: str) -> Dict[str, Any]:
        """
        Remove background from an image using rembg
        
        Args:
            input_image_path: Path to input image
            output_path: Path to save transparent PNG
            
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Removing background from: {input_image_path}")
            
            # Ensure input file exists
            if not os.path.exists(input_image_path):
                raise FileNotFoundError(f"Input image not found: {input_image_path}")
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Read input image
            input_image = Image.open(input_image_path)
            logger.info(f"Input image size: {input_image.size}")
            
            # Remove background using rembg
            logger.info("Processing background removal...")
            output_image = remove(input_image)
            
            # Save as transparent PNG
            output_image.save(output_path, "PNG")
            
            logger.info(f"Background removed successfully: {output_path}")
            
            return {
                "status": "success",
                "input_path": input_image_path,
                "output_path": output_path,
                "original_size": input_image.size,
                "processed_size": output_image.size
            }
            
        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "input_path": input_image_path,
                "output_path": output_path
            }
    
    def merge_images(self, character_path: str, background_path: str, output_path: str) -> Dict[str, Any]:
        """
        Composite character image onto background image
        
        Args:
            character_path: Path to character image (preferably with transparent background)
            background_path: Path to background image
            output_path: Path to save merged result
            
        Returns:
            Dictionary with compositing results
        """
        try:
            logger.info(f"Merging character and background images...")
            
            # Check if input files exist
            if not os.path.exists(character_path):
                raise FileNotFoundError(f"Character image not found: {character_path}")
            if not os.path.exists(background_path):
                raise FileNotFoundError(f"Background image not found: {background_path}")
            
            # Ensure output directory exists
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Load images
            character_img = Image.open(character_path)
            background_img = Image.open(background_path)
            
            logger.info(f"Character size: {character_img.size}, Background size: {background_img.size}")
            
            # Convert character to RGBA if it isn't already
            if character_img.mode != 'RGBA':
                character_img = character_img.convert('RGBA')
            
            # Resize character to fit background proportionally
            # Keep character at about 1/3 of background height for good composition
            target_height = int(background_img.height * 0.4)
            aspect_ratio = character_img.width / character_img.height
            target_width = int(target_height * aspect_ratio)
            
            # Resize character
            character_img = character_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Create a new image with background size
            result_img = background_img.copy()
            
            # Calculate position to center character horizontally and place at bottom
            x_position = (background_img.width - target_width) // 2
            y_position = background_img.height - target_height - 50  # 50px from bottom
            
            # Composite character onto background
            result_img.paste(character_img, (x_position, y_position), character_img)
            
            # Save the result
            result_img.save(output_path, "PNG", quality=95)
            
            logger.info(f"Images merged successfully: {output_path}")
            
            return {
                "status": "success",
                "output_path": output_path,
                "character_size": character_img.size,
                "background_size": background_img.size,
                "final_size": result_img.size,
                "character_position": (x_position, y_position)
            }
            
        except Exception as e:
            logger.error(f"Image merging failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "character_path": character_path,
                "background_path": background_path,
                "output_path": output_path
            }
    
    def adjust_image(self, input_path: str, output_path: str, 
                    brightness: float = 1.0, contrast: float = 1.0, 
                    saturation: float = 1.0) -> Dict[str, Any]:
        """
        Apply basic image adjustments
        
        Args:
            input_path: Path to input image
            output_path: Path to save adjusted image
            brightness: Brightness multiplier (0.5 = darker, 1.5 = brighter)
            contrast: Contrast multiplier (0.5 = less contrast, 1.5 = more contrast)
            saturation: Saturation multiplier (0.0 = grayscale, 2.0 = very saturated)
            
        Returns:
            Dictionary with adjustment results
        """
        try:
            logger.info(f"Adjusting image: {input_path}")
            
            # Load image
            img = Image.open(input_path)
            
            # Apply adjustments
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)
            
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)
            
            if saturation != 1.0:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(saturation)
            
            # Save adjusted image
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            img.save(output_path, "PNG", quality=95)
            
            logger.info(f"Image adjustments applied successfully: {output_path}")
            
            return {
                "status": "success",
                "output_path": output_path,
                "adjustments": {
                    "brightness": brightness,
                    "contrast": contrast,
                    "saturation": saturation
                }
            }
            
        except Exception as e:
            logger.error(f"Image adjustment failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "input_path": input_path,
                "output_path": output_path
            }
    
    def create_thumbnail(self, input_path: str, output_path: str, 
                        size: Tuple[int, int] = (256, 256)) -> Dict[str, Any]:
        """
        Create a thumbnail version of an image
        
        Args:
            input_path: Path to input image
            output_path: Path to save thumbnail
            size: Desired thumbnail size (width, height)
            
        Returns:
            Dictionary with thumbnail creation results
        """
        try:
            logger.info(f"Creating thumbnail: {input_path}")
            
            # Load image
            img = Image.open(input_path)
            
            # Create thumbnail (maintains aspect ratio)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            img.save(output_path, "PNG", quality=90)
            
            logger.info(f"Thumbnail created successfully: {output_path}")
            
            return {
                "status": "success",
                "output_path": output_path,
                "original_size": img.size,
                "thumbnail_size": size
            }
            
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "input_path": input_path,
                "output_path": output_path
            }
    
    def test_pipeline(self) -> Dict[str, Any]:
        """Test the image processing pipeline"""
        try:
            logger.info("Testing image processing pipeline...")
            
            # Create a simple test image
            test_img = Image.new('RGB', (100, 100), color='red')
            test_path = "test_image.png"
            test_img.save(test_path)
            
            # Test thumbnail creation
            result = self.create_thumbnail(test_path, "test_thumbnail.png", (50, 50))
            
            # Clean up test files
            if os.path.exists(test_path):
                os.remove(test_path)
            if os.path.exists("test_thumbnail.png"):
                os.remove("test_thumbnail.png")
            
            if result["status"] == "success":
                logger.info("Image processing pipeline test completed successfully")
                return {
                    "status": "success",
                    "message": "Image processing pipeline is working correctly"
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
image_processor = None

def get_image_processor() -> ImageProcessor:
    """Get or create the global image processor instance"""
    global image_processor
    if image_processor is None:
        image_processor = ImageProcessor()
    return image_processor


def initialize_image_processing() -> bool:
    """Initialize the image processing system"""
    try:
        processor = get_image_processor()
        return processor.initialized
    except Exception as e:
        logger.error(f"Failed to initialize image processing: {e}")
        return False

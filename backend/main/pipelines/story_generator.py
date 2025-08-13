"""
AI Story Generation Pipeline
This module handles the AI-powered story generation logic using LangChain
"""

import logging
from typing import Dict, Optional, List
from .langchain_foundation import get_langchain_core, StoryOutput

logger = logging.getLogger(__name__)


class StoryGeneratorPipeline:
    """Pipeline for generating stories using LangChain and AI models"""
    
    def __init__(self):
        self.langchain_core = None
        self.initialized = False
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize the LangChain pipeline"""
        try:
            logger.info("Initializing StoryGeneratorPipeline...")
            self.langchain_core = get_langchain_core()
            self.initialized = self.langchain_core.initialized
            
            if self.initialized:
                logger.info("StoryGeneratorPipeline initialized successfully")
            else:
                logger.warning("StoryGeneratorPipeline initialization incomplete")
                
        except Exception as e:
            logger.error(f"Failed to initialize StoryGeneratorPipeline: {e}")
            self.initialized = False
    
    def generate_story(self, prompt: str, max_length: int = 500) -> Dict[str, str]:
        """
        Generate a story based on the given prompt using LangChain
        
        Args:
            prompt: The story prompt/seed
            max_length: Maximum length of generated story (not used with current model)
            
        Returns:
            Dictionary containing generated story data
        """
        if not self.initialized:
            logger.error("Pipeline not initialized")
            return {
                'title': 'Pipeline Error',
                'content': 'Story generation pipeline not initialized',
                'status': 'error'
            }
        
        try:
            logger.info(f"Generating story for prompt: {prompt[:50]}...")
            
            # Use LangChain to generate story content
            story_data = self.langchain_core.generate_story_content(prompt)
            
            # Create a title from the prompt
            title = f"Story: {prompt[:50]}{'...' if len(prompt) > 50 else ''}"
            
            return {
                'title': title,
                'content': story_data['story'],
                'character_desc': story_data['character_desc'],
                'background_desc': story_data['background_desc'],
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            return {
                'title': 'Generation Failed',
                'content': f'Error: {str(e)}',
                'status': 'error'
            }
    
    def extract_descriptions_from_story(self, story_text: str) -> Dict[str, str]:
        """
        Extract character and background descriptions from existing story text
        
        Args:
            story_text: The story text to analyze
            
        Returns:
            Dictionary containing character and background descriptions
        """
        if not self.initialized:
            logger.error("Pipeline not initialized")
            return {
                'character_desc': 'Pipeline not initialized',
                'background_desc': 'Pipeline not initialized'
            }
        
        try:
            logger.info("Extracting descriptions from story...")
            
            # Use LangChain to analyze the story
            character_result = self.langchain_core.character_chain.run(story_text=story_text)
            background_result = self.langchain_core.background_chain.run(story_text=story_text)
            
            return {
                'character_desc': character_result.strip(),
                'background_desc': background_result.strip()
            }
            
        except Exception as e:
            logger.error(f"Description extraction failed: {e}")
            return {
                'character_desc': f'Error extracting character descriptions: {str(e)}',
                'background_desc': f'Error extracting background descriptions: {str(e)}'
            }
    
    def enhance_story(self, story_content: str) -> Dict[str, str]:
        """
        Enhance an existing story with additional details using LangChain
        
        Args:
            story_content: The original story content
            
        Returns:
            Dictionary containing enhanced story data
        """
        if not self.initialized:
            logger.error("Pipeline not initialized")
            return {
                'title': 'Pipeline Error',
                'content': 'Story enhancement pipeline not initialized',
                'status': 'error'
            }
        
        try:
            logger.info("Enhancing story with additional details...")
            
            # Extract current descriptions
            descriptions = self.extract_descriptions_from_story(story_content)
            
            # Create enhancement prompt
            enhancement_prompt = f"""Enhance this story with more vivid details and descriptions.

Original story: {story_content}

Character information: {descriptions['character_desc']}
Setting information: {descriptions['background_desc']}

Please add:
- More sensory details (sights, sounds, smells)
- Deeper character motivations
- Richer environmental descriptions
- Enhanced dialogue and interactions

Enhanced story:"""
            
            # Generate enhanced story
            enhanced_result = self.langchain_core.story_chain.run(user_prompt=enhancement_prompt)
            enhanced_story = enhanced_result.strip()
            
            return {
                'title': 'Enhanced Story',
                'content': enhanced_story,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Story enhancement failed: {e}")
            return {
                'title': 'Enhancement Failed',
                'content': f'Error: {str(e)}',
                'status': 'error'
            }
    
    def test_pipeline(self) -> Dict[str, str]:
        """Test the entire pipeline to ensure it's working"""
        try:
            logger.info("Testing StoryGeneratorPipeline...")
            
            # Test basic story generation
            test_prompt = "A magical garden where flowers can talk"
            story_result = self.generate_story(test_prompt)
            
            # Test description extraction
            if story_result['status'] == 'success':
                descriptions = self.extract_descriptions_from_story(story_result['content'])
                
                return {
                    'status': 'success',
                    'test_prompt': test_prompt,
                    'generated_story': story_result,
                    'extracted_descriptions': descriptions
                }
            else:
                return {
                    'status': 'error',
                    'error': 'Story generation failed during test'
                }
                
        except Exception as e:
            logger.error(f"Pipeline test failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


# Global instance for easy access
story_generator = None

def get_story_generator() -> StoryGeneratorPipeline:
    """Get or create the global story generator instance"""
    global story_generator
    if story_generator is None:
        story_generator = StoryGeneratorPipeline()
    return story_generator


def initialize_story_generation() -> bool:
    """Initialize the story generation system"""
    try:
        generator = get_story_generator()
        return generator.initialized
    except Exception as e:
        logger.error(f"Failed to initialize story generation: {e}")
        return False

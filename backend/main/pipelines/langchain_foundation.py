"""
LangChain Core Foundation for Story Generation
This module provides the core LangChain components for AI-powered story generation
using free HuggingFace models.
"""

import logging
import os
from typing import Dict, Optional, List
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Set up logging
logger = logging.getLogger(__name__)

# Configure HuggingFace to use local cache and avoid downloading models repeatedly
os.environ["TRANSFORMERS_CACHE"] = "./models_cache"
os.environ["HF_HOME"] = "./models_cache"


class StoryOutput(BaseModel):
    """Structured output for story generation"""
    story: str = Field(description="The complete generated story")
    character_desc: str = Field(description="Description of main characters")
    background_desc: str = Field(description="Description of setting and background")


class LangChainCore:
    """
    Core LangChain setup for story generation using free HuggingFace models
    """
    
    def __init__(self):
        self.model_name = "microsoft/DialoGPT-medium"  # Free model, good for dialogue/story generation
        self.tokenizer = None
        self.model = None
        self.hf_pipeline = None
        self.llm = None
        self.story_chain = None
        self.analysis_chain = None
        self.initialized = False
        
        # Initialize the pipeline
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize the HuggingFace pipeline and LangChain components"""
        try:
            logger.info(f"Initializing LangChain with model: {self.model_name}")
            
            # Load tokenizer and model
            logger.info("Loading tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            logger.info("Loading model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                pad_token_id=self.tokenizer.eos_token_id,
                low_cpu_mem_usage=True  # Reduce memory usage
            )
            
            # Create HuggingFace pipeline
            logger.info("Creating HuggingFace pipeline...")
            self.hf_pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=512,  # Reasonable length for stories
                do_sample=True,
                temperature=0.7,  # Creative but not too random
                top_p=0.9,
                repetition_penalty=1.2,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Create LangChain LLM wrapper
            logger.info("Creating LangChain LLM wrapper...")
            self.llm = HuggingFacePipeline(
                pipeline=self.hf_pipeline,
                model_kwargs={"temperature": 0.7}
            )
            
            # Create story generation prompt template
            self._create_prompts()
            
            # Create LangChain chains
            self._create_chains()
            
            self.initialized = True
            logger.info("LangChain core initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain core: {e}")
            self.initialized = False
            raise
    
    def _create_prompts(self):
        """Create prompt templates for different tasks"""
        
        # Story generation prompt with examples
        self.story_prompt = PromptTemplate(
            input_variables=["user_prompt"],
            template="""You are a creative storyteller. Generate an engaging story based on the user's prompt.

User's prompt: {user_prompt}

Instructions:
- Create a complete, coherent story
- Include interesting characters and vivid descriptions
- Make it engaging and suitable for all ages
- Keep it between 200-400 words
- End with a satisfying conclusion

Story:"""
        )
        
        # Character analysis prompt
        self.character_prompt = PromptTemplate(
            input_variables=["story_text"],
            template="""Analyze the following story and extract character information.

Story: {story_text}

Please provide a brief description of the main characters, including:
- Their names (if mentioned)
- Physical descriptions
- Personality traits
- Role in the story

Character descriptions:"""
        )
        
        # Background analysis prompt
        self.background_prompt = PromptTemplate(
            input_variables=["story_text"],
            template="""Analyze the following story and extract setting/background information.

Story: {story_text}

Please provide a description of:
- The main setting/location
- Time period or era
- Atmosphere and mood
- Key environmental details

Background description:"""
        )
    
    def _create_chains(self):
        """Create LangChain chains for different tasks"""
        try:
            # Story generation chain
            self.story_chain = LLMChain(
                llm=self.llm,
                prompt=self.story_prompt,
                verbose=False
            )
            
            # Character analysis chain
            self.character_chain = LLMChain(
                llm=self.llm,
                prompt=self.character_prompt,
                verbose=False
            )
            
            # Background analysis chain
            self.background_chain = LLMChain(
                llm=self.llm,
                prompt=self.background_prompt,
                verbose=False
            )
            
            logger.info("LangChain chains created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create chains: {e}")
            raise
    
    def generate_story_content(self, user_prompt: str) -> Dict[str, str]:
        """
        Generate complete story content using LangChain
        
        Args:
            user_prompt: User's story prompt/idea
            
        Returns:
            Dictionary containing story, character descriptions, and background
        """
        if not self.initialized:
            raise RuntimeError("LangChain core not initialized")
        
        try:
            logger.info(f"Generating story for prompt: {user_prompt[:50]}...")
            
            # Generate the main story
            story_result = self.story_chain.run(user_prompt=user_prompt)
            story_text = story_result.strip()
            
            # Extract character descriptions
            character_result = self.character_chain.run(story_text=story_text)
            character_desc = character_result.strip()
            
            # Extract background descriptions
            background_result = self.background_chain.run(story_text=story_text)
            background_desc = background_result.strip()
            
            # Clean up the generated text
            story_text = self._clean_generated_text(story_text)
            character_desc = self._clean_generated_text(character_desc)
            background_desc = self._clean_generated_text(background_desc)
            
            logger.info("Story generation completed successfully")
            
            return {
                "story": story_text,
                "character_desc": character_desc,
                "background_desc": background_desc
            }
            
        except Exception as e:
            logger.error(f"Story generation failed: {e}")
            return {
                "story": f"Error generating story: {str(e)}",
                "character_desc": "Unable to analyze characters",
                "background_desc": "Unable to analyze background"
            }
    
    def _clean_generated_text(self, text: str) -> str:
        """Clean and format generated text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = " ".join(text.split())
        
        # Ensure proper sentence endings
        if text and not text.endswith(('.', '!', '?')):
            text += '.'
        
        return text
    
    def test_pipeline(self) -> Dict[str, str]:
        """Test function to verify the pipeline is working"""
        try:
            test_prompt = "A cat who learns to fly"
            result = self.generate_story_content(test_prompt)
            
            logger.info("Pipeline test completed successfully")
            return {
                "status": "success",
                "test_prompt": test_prompt,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Pipeline test failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


# Global instance for easy access
langchain_core = None

def get_langchain_core() -> LangChainCore:
    """Get or create the global LangChain core instance"""
    global langchain_core
    if langchain_core is None:
        langchain_core = LangChainCore()
    return langchain_core


def initialize_langchain() -> bool:
    """Initialize the LangChain system"""
    try:
        core = get_langchain_core()
        return core.initialized
    except Exception as e:
        logger.error(f"Failed to initialize LangChain: {e}")
        return False


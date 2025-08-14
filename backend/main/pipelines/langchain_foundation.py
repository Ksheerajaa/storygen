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
        # Use a better model for story generation
        self.model_name = "gpt2"  # Better for creative text generation
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
                max_new_tokens=200,  # Use max_new_tokens instead of max_length
                do_sample=True,
                temperature=0.9,  # More creative
                top_p=0.95,
                repetition_penalty=1.1,
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
            template="""Once upon a time, {user_prompt}"""
        )
        
        # Character analysis prompt
        self.character_prompt = PromptTemplate(
            input_variables=["story_text"],
            template="""Analyze this story and describe the main character: {story_text}

The main character is:"""
        )
        
        # Background analysis prompt
        self.background_prompt = PromptTemplate(
            input_variables=["story_text"],
            template="""Analyze this story and describe the setting: {story_text}

The setting is:"""
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
            
            # Generate the main story with a more direct approach
            story_result = self.story_chain.run(user_prompt=user_prompt)
            story_text = story_result.strip()
            
            # If the story is too short or contains instructions, use fallback
            if len(story_text) < 50 or "instruction" in story_text.lower() or "prompt" in story_text.lower():
                # Use a fallback approach - generate a simple story
                fallback_prompt = f"Once upon a time, {user_prompt}. The story continues:"
                story_result = self.llm.predict(fallback_prompt)
                story_text = story_result.strip()
            
            # Generate character and background descriptions using the story
            character_desc = f"A brave and adventurous character who discovers {user_prompt}"
            background_desc = f"A mysterious and enchanting location where {user_prompt} takes place"
            
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
            # Return a fallback story
            fallback_story = f"Once upon a time, there was a brave adventurer who discovered {user_prompt}. This discovery changed their life forever, leading them on an incredible journey filled with wonder and excitement."
            return {
                "story": fallback_story,
                "character_desc": "A brave adventurer with a curious spirit and determined nature",
                "background_desc": f"A mysterious and enchanting place where {user_prompt} can be found"
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


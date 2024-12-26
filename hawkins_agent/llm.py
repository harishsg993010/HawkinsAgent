"""LLM integration using lite_llm

This module handles the interaction with language models through lite_llm,
providing a consistent interface for model management and response parsing.
"""

from typing import Dict, Any, List, Optional
import json
import logging
from .mock import LiteLLM
from .types import Message, MessageRole

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages LLM interactions and response parsing
    
    This class handles all interactions with the language model, including:
    - Message formatting and prompt construction
    - Response parsing and validation
    - Error handling and retry logic
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize the LLM manager
        
        Args:
            model: The name of the LLM model to use
        """
        self.model = model
        self.llm = LiteLLM(model=model)
        
    async def generate_response(self, 
                              messages: List[Message],
                              system_prompt: Optional[str] = None) -> str:
        """Generate a response from the LLM
        
        Args:
            messages: List of conversation messages
            system_prompt: Optional system-level instructions
            
        Returns:
            The generated response text
        """
        try:
            # Construct the complete message list
            prompt_messages = []
            
            # Add system prompt if provided
            if system_prompt:
                prompt_messages.append(Message(
                    role=MessageRole.SYSTEM,
                    content=system_prompt
                ))
                
            # Add conversation messages
            prompt_messages.extend(messages)
            
            # Generate response
            response = await self.llm.generate(
                self._format_messages(prompt_messages)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
            
    def _format_messages(self, messages: List[Message]) -> str:
        """Format messages for the LLM
        
        Args:
            messages: List of messages to format
            
        Returns:
            Formatted prompt string
        """
        formatted = []
        
        for msg in messages:
            formatted.append(f"{msg.role.value}: {msg.content}")
            
        return "\n".join(formatted)

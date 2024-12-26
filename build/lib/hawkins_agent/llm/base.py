"""Base classes for LLM integration"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..types import Message

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers
    
    This class defines the interface that all LLM providers must implement.
    It handles the core functionality of interacting with language models.
    """
    
    def __init__(self, model: str, **kwargs):
        """Initialize the LLM provider
        
        Args:
            model: Name of the language model to use
            **kwargs: Additional provider-specific configuration
        """
        self.model = model
        self.config = kwargs
        
    @abstractmethod
    async def generate(self, messages: List[Message]) -> str:
        """Generate a response from the language model
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Generated response text
            
        Raises:
            LLMError: If there's an error during generation
        """
        pass
    
    @abstractmethod
    async def validate_response(self, response: str) -> bool:
        """Validate a response from the language model
        
        Args:
            response: Response text to validate
            
        Returns:
            True if response is valid, False otherwise
        """
        pass

"""LLM Manager implementation"""

from typing import List, Optional, Dict, Any
import logging
from .base import BaseLLMProvider
from .lite_llm import LiteLLMProvider
from ..types import Message, MessageRole

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages LLM interactions and providers

    This class provides a high-level interface for working with language
    models, handling provider selection, response management, and error handling.
    """

    def __init__(self, 
                 model: str = "gpt-3.5-turbo",
                 provider_class: Optional[type] = None,
                 **kwargs):
        """Initialize the LLM manager

        Args:
            model: Name of the model to use
            provider_class: Optional custom provider class
            **kwargs: Additional configuration for the provider
        """
        self.model = model
        provider_class = provider_class or LiteLLMProvider
        self.provider = provider_class(model=model, **kwargs)

    async def generate_response(self,
                              messages: List[Message],
                              system_prompt: Optional[str] = None) -> str:
        """Generate a response from the LLM

        Args:
            messages: List of conversation messages
            system_prompt: Optional system-level instructions

        Returns:
            Generated response text
        """
        try:
            # Add system prompt if provided
            if system_prompt:
                messages = [Message(
                    role=MessageRole.SYSTEM,
                    content=system_prompt
                )] + messages

            response = await self.provider.generate(messages)
            return response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
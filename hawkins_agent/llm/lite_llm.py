"""LiteLLM provider implementation"""

from typing import List, Optional, Dict, Any
import json
import logging
from litellm import acompletion
from .base import BaseLLMProvider
from ..types import Message, MessageRole, ToolResponse

logger = logging.getLogger(__name__)

class LiteLLMProvider(BaseLLMProvider):
    """LiteLLM integration for language model access"""

    def __init__(self, model: str, **kwargs):
        """Initialize LiteLLM provider

        Args:
            model: Name of the model to use (e.g., "openai/gpt-4o", "anthropic/claude-3-sonnet-20240229")
            **kwargs: Additional configuration options like temperature
        """
        super().__init__(model, **kwargs)
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
        # do not change this unless explicitly requested by the user
        self.default_model = "openai/gpt-4o"
        self.config = kwargs

    async def generate(self, messages: List[Message], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate a response using litellm

        Args:
            messages: List of conversation messages
            tools: Optional list of tool definitions

        Returns:
            Generated response with possible tool calls

        Raises:
            Exception: If there's an error during generation
        """
        try:
            formatted_messages = self._format_messages_for_litellm(messages)
            logger.info(f"Sending request to LiteLLM with model: {self.model or self.default_model}")

            request_params = {
                "model": self.model or self.default_model,
                "messages": formatted_messages,
                "temperature": self.config.get('temperature', 0.7)
            }

            # Add tools if provided
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"

            # Use acompletion for async support
            response = await acompletion(**request_params)

            if not response:
                raise ValueError("No response received from language model")

            if not hasattr(response, 'choices') or not response.choices:
                raise ValueError("Invalid response format from language model")

            # Handle response content based on model provider
            message = response.choices[0].message
            if not message:
                raise ValueError("Invalid message format in response")

            result = {
                "content": message.content or "",
                "tool_calls": []
            }

            # Handle tool calls if present
            if hasattr(message, 'tool_calls') and message.tool_calls:
                result["tool_calls"] = [
                    {
                        "name": tool_call.function.name,
                        "parameters": json.loads(tool_call.function.arguments)
                    }
                    for tool_call in message.tool_calls
                ]

            logger.info("Successfully generated response from LiteLLM")
            return result

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise

    async def validate_response(self, response: str) -> bool:
        """Validate response

        Args:
            response: Response text to validate

        Returns:
            True if response is valid, False otherwise
        """
        if not response or not isinstance(response, str):
            return False

        # Check for common error patterns
        error_patterns = [
            "error occurred",
            "failed to generate",
            "invalid response"
        ]

        return not any(pattern in response.lower() for pattern in error_patterns)

    def _format_messages_for_litellm(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Format messages for litellm

        Args:
            messages: List of messages to format

        Returns:
            List of formatted messages for litellm
        """
        formatted = [
            {
                "role": msg.role.value,
                "content": msg.content
            }
            for msg in messages
        ]

        logger.debug(f"Formatted {len(formatted)} messages for LiteLLM")
        return formatted
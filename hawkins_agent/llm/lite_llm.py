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
        """Initialize LiteLLM provider"""
        super().__init__(model, **kwargs)
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024
        # do not change this unless explicitly requested by the user
        self.default_model = "openai/gpt-4o"
        self.config = kwargs

    async def generate(self, messages: List[Message], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate a response using litellm"""
        try:
            formatted_messages = self._format_messages_for_litellm(messages)
            logger.info(f"Sending request to LiteLLM with model: {self.model or self.default_model}")

            request_params = {
                "model": self.model or self.default_model,
                "messages": formatted_messages,
                "temperature": self.config.get('temperature', 0.7)
            }

            # Format and add tools if provided
            if tools:
                formatted_tools = []
                for tool in tools:
                    formatted_tool = {
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool.get("description", ""),
                            "parameters": {
                                "type": "object",
                                "properties": tool.get("parameters", {}),
                                "required": tool.get("required", [])
                            }
                        }
                    }
                    formatted_tools.append(formatted_tool)

                request_params["tools"] = formatted_tools
                request_params["tool_choice"] = "auto"

            logger.debug(f"Request parameters: {json.dumps(request_params, indent=2)}")

            # Use acompletion for async support
            response = await acompletion(**request_params)

            if not response or not hasattr(response, 'choices') or not response.choices:
                raise ValueError("Invalid response from language model")

            message = response.choices[0].message
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
        """Validate response format"""
        if not response or not isinstance(response, str):
            return False
        return True

    def _format_messages_for_litellm(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Format messages for litellm"""
        formatted = []

        # Format system message if present
        system_messages = [msg for msg in messages if msg.role == MessageRole.SYSTEM]
        if system_messages:
            formatted.append({
                "role": "system",
                "content": system_messages[0].content
            })

        # Format remaining messages
        user_assistant_messages = [msg for msg in messages if msg.role != MessageRole.SYSTEM]
        for msg in user_assistant_messages:
            formatted.append({
                "role": msg.role.value,
                "content": msg.content
            })

        logger.debug(f"Formatted {len(formatted)} messages for LiteLLM")
        return formatted
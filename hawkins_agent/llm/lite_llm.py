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
        self.default_model = "openai/gpt-4o"
        self.config = kwargs
        self.supports_functions = not model.startswith("anthropic/")

    async def generate(self, messages: List[Message], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate a response using litellm"""
        try:
            formatted_messages = self._format_messages_for_litellm(messages)
            logger.info(f"Sending request to LiteLLM with model: {self.model or self.default_model}")
            logger.debug(f"Using tools: {tools}")

            request_params = {
                "model": self.model or self.default_model,
                "messages": formatted_messages,
                "temperature": self.config.get('temperature', 0.7)
            }

            # Only add function calling for supported models
            if tools and self.supports_functions:
                request_params["functions"] = tools
                request_params["function_call"] = "auto"

            logger.debug(f"Request parameters: {json.dumps(request_params, indent=2)}")

            # Use acompletion for async support
            response = await acompletion(**request_params)

            if not response or not hasattr(response, 'choices') or not response.choices:
                logger.error("Invalid response format from LiteLLM")
                return {"content": "Error: Invalid response format", "tool_calls": []}

            first_choice = response.choices[0]
            if not hasattr(first_choice, 'message'):
                logger.error("Response choice missing message attribute")
                return {"content": "Error: Invalid response format", "tool_calls": []}

            message = first_choice.message
            result = {
                "content": message.content if hasattr(message, 'content') else "",
                "tool_calls": []
            }

            # Handle function calls for supported models
            if self.supports_functions:
                if hasattr(message, 'function_call') and message.function_call:
                    try:
                        result["tool_calls"] = [{
                            "name": message.function_call.name,
                            "parameters": json.loads(message.function_call.arguments)
                        }]
                    except (AttributeError, json.JSONDecodeError) as e:
                        logger.error(f"Error parsing function call: {e}")

                elif hasattr(message, 'tool_calls') and message.tool_calls:
                    try:
                        result["tool_calls"] = [
                            {
                                "name": tool_call.function.name,
                                "parameters": json.loads(tool_call.function.arguments)
                            }
                            for tool_call in message.tool_calls
                            if hasattr(tool_call, 'function')
                        ]
                    except (AttributeError, json.JSONDecodeError) as e:
                        logger.error(f"Error parsing tool calls: {e}")

            logger.info("Successfully generated response from LiteLLM")
            logger.debug(f"Response: {json.dumps(result, indent=2)}")
            return result

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return {
                "content": f"Error generating response: {str(e)}",
                "tool_calls": []
            }

    async def validate_response(self, response: str) -> bool:
        """Validate response format"""
        if not response or not isinstance(response, str):
            return False
        return True

    def _format_messages_for_litellm(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Format messages for litellm"""
        try:
            formatted = []
            for msg in messages:
                formatted.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
            logger.debug(f"Formatted {len(formatted)} messages for LiteLLM")
            return formatted
        except Exception as e:
            logger.error(f"Error formatting messages: {e}")
            return [{"role": "user", "content": "Error formatting messages"}]
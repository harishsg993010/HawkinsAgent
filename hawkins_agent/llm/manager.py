"""LLM Manager implementation"""

from typing import List, Optional, Dict, Any
import logging
from .base import BaseLLMProvider
from .lite_llm import LiteLLMProvider
from ..types import Message, MessageRole

logger = logging.getLogger(__name__)

class LLMManager:
    """Manages LLM interactions and providers"""

    def __init__(self, 
                 model: str = "gpt-4o",
                 provider_class: Optional[type] = None,
                 **kwargs):
        """Initialize the LLM manager"""
        self.model = model
        provider_class = provider_class or LiteLLMProvider
        self.provider = provider_class(model=model, **kwargs)

    async def generate_response(self,
                             messages: List[Message],
                             tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Generate a response from the LLM with optional tool support"""
        try:
            # Format tools for OpenAI function calling format
            formatted_tools = None
            if tools:
                formatted_tools = []
                for tool in tools:
                    formatted_tool = {
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "query": {
                                        "type": "string",
                                        "description": tool.get("parameters", {}).get("query", {}).get("description", "Input query for the tool")
                                    }
                                },
                                "required": ["query"]
                            }
                        }
                    }
                    formatted_tools.append(formatted_tool)

            # Add system prompt if tools are provided
            if formatted_tools:
                tool_descriptions = "\n".join(
                    f"- {tool['function']['name']}: {tool['function']['description']}"
                    for tool in formatted_tools
                )
                system_content = f"""You have access to the following tools:
{tool_descriptions}

When you need to search for information, use the appropriate tool with a relevant query.
Summarize the results in a clear and concise way."""

                messages = [Message(
                    role=MessageRole.SYSTEM,
                    content=system_content
                )] + messages

            response = await self.provider.generate(
                messages=messages,
                tools=formatted_tools
            )

            return response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
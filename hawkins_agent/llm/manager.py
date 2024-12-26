"""LLM Manager implementation"""

from typing import List, Optional, Dict, Any
import logging
import json
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
            logger.info("Starting response generation")
            logger.debug(f"Input messages: {messages}")
            logger.debug(f"Available tools: {tools}")

            # Format tools for OpenAI function calling format
            formatted_tools = None
            if tools:
                formatted_tools = []
                for tool in tools:
                    formatted_tool = {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The query to be processed by the tool"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                    formatted_tools.append(formatted_tool)
                logger.debug(f"Formatted tools: {json.dumps(formatted_tools, indent=2)}")

            # Add system prompt if tools are provided
            if formatted_tools:
                tool_descriptions = "\n".join(
                    f"- {tool['name']}: {tool['description']}"
                    for tool in formatted_tools
                )
                system_content = f"""You have access to the following tools:
{tool_descriptions}

When you need to search for information or use a tool, choose the appropriate tool and provide a relevant query.
First analyze what tool would be most appropriate, then use it with a well-formulated query.
Always summarize the results in a clear and concise way.
To use a tool, include it in your response like this: <tool_call>{{"name": "tool_name", "parameters": {{"query": "your query"}}}}</tool_call>"""

                messages = [Message(
                    role=MessageRole.SYSTEM,
                    content=system_content
                )] + messages

            logger.info(f"Generating response with model: {self.model}")
            logger.debug(f"Final messages: {messages}")

            response = await self.provider.generate(
                messages=messages,
                tools=formatted_tools
            )

            logger.info("Response generated successfully")
            logger.debug(f"Raw response: {json.dumps(response, indent=2)}")

            return response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return {
                "content": f"Error generating response: {str(e)}",
                "tool_calls": []
            }
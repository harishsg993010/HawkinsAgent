"""Core Agent implementation"""

from typing import List, Optional, Dict, Any, Type, Union
from .llm import LLMManager, BaseLLMProvider, LiteLLMProvider
from .mock import Document, KnowledgeBase
from .memory import MemoryManager
from .tools.base import BaseTool
from .types import Message, AgentResponse, MessageRole, ToolResponse
import json
import re
import logging
from dataclasses import asdict

logger = logging.getLogger(__name__)

class Agent:
    """Main Agent class that handles interactions and tool usage

    This class represents an AI agent that can process messages, use tools,
    access knowledge bases, and maintain conversation memory.

    Attributes:
        name: The name of the agent
        llm: The language model manager
        knowledge_base: Optional knowledge base for information retrieval
        tools: List of available tools
        memory: Memory manager for conversation history
        system_prompt: Custom system-level instructions
    """

    def __init__(
        self,
        name: str,
        llm_model: str = "gpt-4o",
        llm_provider_class: Type[BaseLLMProvider] = LiteLLMProvider,
        llm_config: Optional[Dict[str, Any]] = None,
        knowledge_base: Optional[KnowledgeBase] = None,
        tools: Optional[List[BaseTool]] = None,
        memory_config: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ):
        self.name = name
        self.llm = LLMManager(model=llm_model, provider_class=llm_provider_class, config=llm_config)
        self.knowledge_base = knowledge_base
        self.tools = tools or []
        self.memory = MemoryManager(config=memory_config)
        self.system_prompt = system_prompt or self._get_default_system_prompt()

    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the agent"""
        return f"""You are {self.name}, an AI assistant that helps users with their tasks.
You have access to various tools and knowledge sources that you can use to help users.
When using tools, format your response with clear tool calls using the specified JSON format."""

    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a user message and return a response

        This method handles the complete flow of:
        1. Gathering context from memory and knowledge base
        2. Constructing the message list with context
        3. Getting and parsing the LLM response
        4. Executing any tool calls
        5. Updating memory with the interaction

        Args:
            message: The user's input message
            context: Optional additional context for processing

        Returns:
            AgentResponse containing the agent's response and any tool results
        """
        try:
            # Get context from memory and knowledge base
            combined_context = await self._gather_context(message)
            if context:
                combined_context.update(context)

            # Construct message list
            messages = self._construct_messages(message, combined_context)

            # Get LLM response
            response = await self.llm.generate_response(
                messages=messages,
                system_prompt=self.system_prompt
            )

            # Parse response and handle tool calls
            parsed_response = self._parse_response(response)

            # Execute tool calls if any
            if parsed_response.tool_calls:
                tool_results = await self._execute_tools(parsed_response.tool_calls)
                parsed_response.metadata["tool_results"] = tool_results

                # If tools were used, potentially follow up
                if any(result["success"] for result in tool_results):
                    follow_up = await self._handle_tool_results(tool_results, message, messages)
                    if follow_up:
                        parsed_response.message += f"\n\n{follow_up}"

            # Update memory
            await self.memory.add_interaction(message, parsed_response.message)

            return parsed_response

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return AgentResponse(
                message="I encountered an error processing your message. Please try again.",
                tool_calls=[],
                metadata={"error": str(e)}
            )

    async def _gather_context(self, message: str) -> Dict[str, Any]:
        """Gather relevant context from memory and knowledge base

        Args:
            message: The user's input message

        Returns:
            Dictionary containing relevant memories and knowledge
        """
        try:
            context = {
                "memory": await self.memory.get_relevant_memories(message),
                "knowledge": []
            }

            if self.knowledge_base:
                context["knowledge"] = await self.knowledge_base.query(message)

            return context
        except Exception as e:
            logger.error(f"Error gathering context: {str(e)}")
            return {"memory": [], "knowledge": []}

    def _construct_messages(self, message: str, context: Dict[str, Any]) -> List[Message]:
        """Construct the message list for the LLM

        Args:
            message: The user's input message
            context: Dictionary containing memory and knowledge context

        Returns:
            List of Message objects for the LLM
        """
        try:
            # Add context message
            messages = [Message(
                role=MessageRole.SYSTEM,
                content=self._format_context(context)
            )]

            # Add user message
            messages.append(Message(
                role=MessageRole.USER,
                content=message
            ))

            return messages

        except Exception as e:
            logger.error(f"Error constructing messages: {str(e)}")
            return [Message(role=MessageRole.USER, content=message)]

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context into a string for the LLM

        Args:
            context: Dictionary containing context information

        Returns:
            Formatted context string
        """
        try:
            tool_descriptions = "\n".join(
                f"- {tool.name}: {tool.description}" for tool in self.tools
            )

            return f"""Context from memory:
{json.dumps(context['memory'], indent=2)}

Relevant knowledge:
{json.dumps(context['knowledge'], indent=2)}

Available tools:
{tool_descriptions}

To use a tool, include a JSON block in your response:
<tool_call>
{{"name": "tool_name", "parameters": {{"param1": "value1"}}}}
</tool_call>"""

        except Exception as e:
            logger.error(f"Error formatting context: {str(e)}")
            return "Error retrieving context"

    async def _handle_tool_results(
        self,
        results: List[Dict[str, Any]],
        original_message: str,
        previous_messages: List[Message]
    ) -> Optional[str]:
        """Handle tool execution results and generate follow-up response if needed

        Args:
            results: List of tool execution results
            original_message: The original user message
            previous_messages: Previous conversation messages

        Returns:
            Optional follow-up response string
        """
        try:
            # Add tool results to message history
            tool_result_message = Message(
                role=MessageRole.SYSTEM,
                content=f"Tool execution results:\n{json.dumps(results, indent=2)}"
            )

            messages = previous_messages + [tool_result_message]

            # Generate follow-up response if needed
            if any(result["success"] for result in results):
                follow_up = await self.llm.generate_response(
                    messages=messages,
                    system_prompt="Review the tool results and provide a follow-up response if needed."
                )
                return follow_up.strip()

            return None

        except Exception as e:
            logger.error(f"Error handling tool results: {str(e)}")
            return None

    def _parse_response(self, response: str) -> AgentResponse:
        """Parse the LLM response and extract tool calls

        Args:
            response: Raw response from the LLM

        Returns:
            AgentResponse containing parsed message and tool calls
        """
        try:
            tool_calls = []
            message = response

            # Extract tool calls from response
            tool_pattern = r"<tool_call>(.*?)</tool_call>"
            matches = re.finditer(tool_pattern, response, re.DOTALL)

            for match in matches:
                try:
                    tool_json = json.loads(match.group(1))
                    if self._validate_tool_call(tool_json):
                        tool_calls.append(tool_json)
                    # Remove tool call from message
                    message = message.replace(match.group(0), "")
                except json.JSONDecodeError:
                    logger.warning(f"Invalid tool call JSON: {match.group(1)}")
                    continue

            message = message.strip()

            return AgentResponse(
                message=message,
                tool_calls=tool_calls,
                metadata={}
            )
        except Exception as e:
            logger.error(f"Error parsing response: {str(e)}")
            return AgentResponse(
                message=response,
                tool_calls=[],
                metadata={"error": str(e)}
            )

    def _validate_tool_call(self, tool_call: Dict[str, Any]) -> bool:
        """Validate a tool call format and parameters

        Args:
            tool_call: Dictionary containing the tool call information

        Returns:
            True if the tool call is valid, False otherwise
        """
        try:
            if not isinstance(tool_call, dict):
                return False

            required_keys = {"name", "parameters"}
            if not all(key in tool_call for key in required_keys):
                return False

            tool = next((t for t in self.tools if t.name == tool_call["name"]), None)
            if not tool:
                return False

            return tool.validate_params(tool_call["parameters"])
        except Exception:
            return False

    async def _execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute tool calls and return results

        Args:
            tool_calls: List of validated tool call dictionaries

        Returns:
            List of tool execution results
        """
        results = []

        for call in tool_calls:
            tool_name = call.get("name")
            parameters = call.get("parameters", {})

            tool = next((t for t in self.tools if t.name == tool_name), None)
            if tool:
                try:
                    result = await tool.execute(**parameters)
                    results.append({
                        "tool": tool_name,
                        "success": result.success,
                        "result": result.result,
                        "error": result.error
                    })
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {str(e)}")
                    results.append({
                        "tool": tool_name,
                        "success": False,
                        "result": None,
                        "error": str(e)
                    })

        return results

class AgentBuilder:
    """Builder class for creating agents with a fluent interface"""

    def __init__(self, name: str):
        self.name = name
        self.llm_model = "gpt-4o"  # Default to latest model
        self.llm_provider_class = LiteLLMProvider
        self.knowledge_base = None
        self.tools = []
        self.memory_config = {}
        self.llm_config = {}

    def with_model(self, model: str) -> "AgentBuilder":
        """Set the LLM model"""
        self.llm_model = model
        return self

    def with_provider(self, provider_class: Type[BaseLLMProvider], **config) -> "AgentBuilder":
        """Set custom LLM provider with configuration

        Args:
            provider_class: Custom LLM provider class
            **config: Provider-specific configuration
        """
        self.llm_provider_class = provider_class
        self.llm_config = config
        return self

    def with_knowledge_base(self, kb: KnowledgeBase) -> "AgentBuilder":
        """Add a knowledge base"""
        self.knowledge_base = kb
        return self

    def with_tool(self, tool: BaseTool) -> "AgentBuilder":
        """Add a tool"""
        self.tools.append(tool)
        return self

    def with_memory(self, config: Dict[str, Any]) -> "AgentBuilder":
        """Configure memory"""
        self.memory_config = config
        return self

    def build(self) -> Agent:
        """Create the agent instance"""
        return Agent(
            name=self.name,
            llm_model=self.llm_model,
            llm_provider_class=self.llm_provider_class,
            llm_config=self.llm_config,
            knowledge_base=self.knowledge_base,
            tools=self.tools,
            memory_config=self.memory_config
        )
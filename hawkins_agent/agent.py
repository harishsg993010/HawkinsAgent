"""Core Agent implementation"""

from typing import List, Optional, Dict, Any, Type, Union
from .mock import LiteLLM as lite_llm
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
        llm: The language model instance
        knowledge_base: Optional knowledge base for information retrieval
        tools: List of available tools
        memory: Memory manager for conversation history
    """

    def __init__(
        self,
        name: str,
        llm_model: str,
        knowledge_base: Optional[KnowledgeBase] = None,
        tools: Optional[List[BaseTool]] = None,
        memory_config: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.llm = lite_llm(model=llm_model)
        self.knowledge_base = knowledge_base
        self.tools = tools or []
        self.memory = MemoryManager(config=memory_config)

    async def process(self, message: str) -> AgentResponse:
        """Process a user message and return a response

        This method handles the complete flow of:
        1. Gathering context from memory and knowledge base
        2. Constructing the prompt for the LLM
        3. Getting and parsing the LLM response
        4. Executing any tool calls
        5. Updating memory with the interaction

        Args:
            message: The user's input message

        Returns:
            AgentResponse containing the agent's response and any tool results
        """
        try:
            # Get context from memory and knowledge base
            context = await self._gather_context(message)

            # Construct prompt with context
            prompt = self._construct_prompt(message, context)

            # Get LLM response
            response = await self.llm.generate(prompt)

            # Parse response and handle tool calls
            parsed_response = self._parse_response(response)

            # Execute tool calls if any
            if parsed_response.tool_calls:
                tool_results = await self._execute_tools(parsed_response.tool_calls)
                parsed_response.metadata["tool_results"] = tool_results

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

    def _construct_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """Construct the prompt for the LLM

        Args:
            message: The user's input message
            context: Dictionary containing memory and knowledge context

        Returns:
            Formatted prompt string for the LLM
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

User message: {message}

Respond naturally and use tools when necessary. To use a tool, include a JSON block in your response:
<tool_call>
{{"name": "tool_name", "parameters": {{"param1": "value1"}}}}
</tool_call>"""
        except Exception as e:
            logger.error(f"Error constructing prompt: {str(e)}")
            return message

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
        self.llm_model = "gpt-3.5-turbo"
        self.knowledge_base = None
        self.tools = []
        self.memory_config = {}

    def with_model(self, model: str) -> "AgentBuilder":
        """Set the LLM model"""
        self.llm_model = model
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
            knowledge_base=self.knowledge_base,
            tools=self.tools,
            memory_config=self.memory_config
        )
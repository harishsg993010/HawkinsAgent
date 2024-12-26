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
    """Main Agent class that handles interactions and tool usage"""

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
        self.llm = LLMManager(
            model=llm_model, 
            provider_class=llm_provider_class,
            **llm_config or {}
        )
        self.knowledge_base = knowledge_base
        self.tools = tools or []
        self.memory = MemoryManager(config=memory_config)
        self.system_prompt = system_prompt or self._get_default_system_prompt()

    async def _handle_tool_results(
        self,
        results: List[Dict[str, Any]],
        original_message: str
    ) -> Optional[str]:
        """Handle tool execution results"""
        try:
            # Create prompt with results
            result_prompt = "Based on the tool results:\n"
            for result in results:
                if result.get("success", False):
                    result_prompt += f"\n- {result.get('result', '')}"
                else:
                    result_prompt += f"\n- Error: {result.get('error', 'Unknown error')}"

            result_prompt += "\n\nPlease provide a concise summary of these findings."

            # Get follow-up response
            response = await self.llm.generate_response(
                messages=[Message(
                    role=MessageRole.USER,
                    content=result_prompt
                )]
            )

            return response.get("content", "").strip() if response else ""

        except Exception as e:
            logger.error(f"Error handling tool results: {str(e)}")
            return None

    async def process(self, message: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a user message"""
        try:
            # Get context and construct messages
            combined_context = await self._gather_context(message)
            if context:
                combined_context.update(context)

            # Format messages list with system prompt and context
            messages = [Message(role=MessageRole.SYSTEM, content=self.system_prompt)]

            # Add context if available
            if combined_context:
                context_msg = "Context:\n" + "\n".join([
                    f"- {k}: {v}" for k, v in combined_context.items()
                ])
                messages.append(Message(
                    role=MessageRole.SYSTEM,
                    content=context_msg
                ))

            messages.append(Message(role=MessageRole.USER, content=message))

            # Format tools for LLM
            formatted_tools = []
            if self.tools:
                for tool in self.tools:
                    formatted_tools.append({
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string", 
                                    "description": "The query or parameters for the tool"
                                }
                            },
                            "required": ["query"]
                        }
                    })

            # Get LLM response
            response = await self.llm.generate_response(
                messages=messages,
                tools=formatted_tools if self.tools else None
            )

            # Parse response and handle tool calls
            result = await self._process_response(response, message)

            # Update memory if we have a valid message
            if result and result.message:
                await self.memory.add_interaction(message, result.message)

            return result or AgentResponse(
                message="Error processing response",
                tool_calls=[],
                metadata={"error": "Failed to process response"}
            )

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return AgentResponse(
                message=f"I encountered an error processing your message: {str(e)}",
                tool_calls=[],
                metadata={"error": str(e)}
            )

    async def _process_response(self, response: Dict[str, Any], original_message: str) -> AgentResponse:
        """Process the LLM response and handle tool calls"""
        try:
            message = response.get("content", "") or ""
            tool_calls = []
            metadata = {}

            # Extract tool calls from the message for non-function-calling models
            if not self.llm.provider.supports_functions:
                tool_call_pattern = r'<tool_call>\s*({[^}]+})\s*</tool_call>'
                matches = re.finditer(tool_call_pattern, message)

                for match in matches:
                    try:
                        tool_call = json.loads(match.group(1))
                        tool_calls.append(tool_call)
                        # Remove the tool call from the message
                        message = message.replace(match.group(0), "")
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing tool call JSON: {e}")
            else:
                # Use standard function calling response format
                tool_calls = response.get("tool_calls", [])

            # Execute tools and get results if any tool calls present
            if tool_calls:
                tool_results = await self._execute_tools(tool_calls)
                metadata["tool_results"] = tool_results

                # Generate follow-up based on tool results
                if any(result.get("success", False) for result in tool_results):
                    follow_up = await self._handle_tool_results(
                        tool_results, 
                        message
                    )
                    if follow_up:
                        message = (message or "").strip() + "\n\n" + follow_up

            return AgentResponse(
                message=message.strip(),
                tool_calls=tool_calls,
                metadata=metadata
            )

        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return AgentResponse(
                message=str(response.get("content", "")),
                tool_calls=[],
                metadata={"error": str(e)}
            )

    async def _gather_context(self, message: str) -> Dict[str, Any]:
        """Gather context from memory and knowledge base"""
        context = {}

        try:
            # Get relevant memories if available
            memories = await self.memory.get_relevant_memories(message)
            if memories:
                context["memory"] = memories

            # Query knowledge base if available
            if self.knowledge_base:
                kb_results = await self.knowledge_base.query(message)
                if kb_results:
                    context["knowledge"] = kb_results

        except Exception as e:
            logger.error(f"Error gathering context: {str(e)}")

        return context

    async def _execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute tool calls and return results"""
        results = []

        for call in tool_calls:
            tool_name = call.get("name")
            parameters = call.get("parameters", {})

            # Find matching tool
            tool = next(
                (t for t in self.tools if t.name == tool_name), 
                None
            )

            if tool:
                try:
                    result = await tool.execute(**parameters)
                    if isinstance(result, ToolResponse):
                        results.append({
                            "tool": tool_name,
                            "success": result.success,
                            "result": result.result,
                            "error": result.error
                        })
                    else:
                        logger.warning(f"Tool {tool_name} returned invalid response type")
                        results.append({
                            "tool": tool_name,
                            "success": False,
                            "result": None,
                            "error": "Invalid tool response format"
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

    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the agent"""
        base_prompt = f"""You are {self.name}, an AI assistant that helps users with their tasks."""

        if not self.tools:
            return base_prompt

        tool_descriptions = "\n".join(
            f"- {tool.name}: {tool.description}" 
            for tool in self.tools
        )

        # Adjust prompt based on whether the model supports function calling
        if self.llm.provider.supports_functions:
            return f"{base_prompt}\n\nYou have access to the following tools:\n\n{tool_descriptions}"
        else:
            return f"""{base_prompt}

You have access to the following tools:

{tool_descriptions}

When you need to use a tool, use this format in your response:
<tool_call>
{{"name": "tool_name", "parameters": {{"query": "your query"}}}}
</tool_call>

After using a tool, summarize its results in a clear and helpful way."""

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
        """Set custom LLM provider with configuration"""
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
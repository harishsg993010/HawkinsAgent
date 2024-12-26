"""Type definitions for the Hawkins Agent Framework

This module contains the core type definitions used throughout the framework,
including message types, agent responses, and tool responses.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from enum import Enum

class MessageRole(str, Enum):
    """Defines the role of a message in a conversation

    Attributes:
        USER: Message from the user
        ASSISTANT: Message from the AI assistant
        SYSTEM: System-level message or instruction
    """
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

@dataclass
class Message:
    """Represents a message in the conversation

    Attributes:
        role: The role of the message sender (user, assistant, or system)
        content: The actual content of the message
        metadata: Optional metadata associated with the message
    """
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AgentResponse:
    """Represents an agent's response to a user message

    Attributes:
        message: The text response from the agent
        tool_calls: List of tool calls made during response generation
        metadata: Additional metadata about the response, including tool results
    """
    message: str
    tool_calls: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@dataclass
class ToolResponse:
    """Represents a tool's response after execution

    Attributes:
        success: Whether the tool execution was successful
        result: The result of the tool execution (if successful)
        error: Error message if the execution failed

    Example:
        >>> tool_response = ToolResponse(
        ...     success=True,
        ...     result="Email sent successfully",
        ...     error=None
        ... )
    """
    success: bool
    result: Any
    error: Optional[str] = None
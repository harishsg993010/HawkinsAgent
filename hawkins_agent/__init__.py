"""
Hawkins Agent Framework
A simple yet powerful framework for building AI agents
"""

from .agent import Agent, AgentBuilder
from .types import Message, AgentResponse
from .tools.base import BaseTool

__version__ = "0.1.0"
__all__ = ["Agent", "AgentBuilder", "Message", "AgentResponse", "BaseTool"]

"""
Hawkins Agent Framework
A simple yet powerful framework for building AI agents
"""

from .agent import Agent, AgentBuilder
from .types import Message, AgentResponse
from .tools.base import BaseTool
from .flow import FlowManager, FlowStep

__version__ = "0.1.4"
__all__ = ["Agent", "AgentBuilder", "Message", "AgentResponse", "BaseTool", 
           "FlowManager", "FlowStep"]
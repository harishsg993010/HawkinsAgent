"""
Hawkins Agent Tools
A collection of tools for use with Hawkins agents
"""

from .base import BaseTool
from .email import EmailTool
from .search import WebSearchTool
from .rag import RAGTool
from .summarize import SummarizationTool
from .code_interpreter import CodeInterpreterTool
from .weather import WeatherTool

__all__ = [
    "BaseTool",
    "EmailTool", 
    "WebSearchTool",
    "RAGTool",
    "SummarizationTool",
    "CodeInterpreterTool",
    "WeatherTool"
]
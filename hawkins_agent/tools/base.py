"""Base tool implementation for the Hawkins Agent Framework

This module provides the base class for implementing tools that can be used by agents.
Tools are the primary way to add capabilities to agents, such as sending emails,
performing web searches, or accessing external APIs.

Example:
    >>> class CustomTool(BaseTool):
    ...     @property
    ...     def description(self) -> str:
    ...         return "Description of what the tool does"
    ...
    ...     async def execute(self, **kwargs) -> ToolResponse:
    ...         result = await self._perform_operation(**kwargs)
    ...         return ToolResponse(success=True, result=result)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from ..types import ToolResponse

class BaseTool(ABC):
    """Abstract base class for all tools in the Hawkins Agent Framework

    All tools must inherit from this class and implement the required methods.
    The tool's name is automatically derived from the class name, but can be
    overridden if needed.

    Attributes:
        _name: Protected name attribute of the tool
    """

    def __init__(self, name: Optional[str] = None):
        """Initialize the tool with an optional custom name

        Args:
            name: Optional custom name for the tool. If not provided,
                 the class name will be used.
        """
        self._name = name or self.__class__.__name__

    @property
    def name(self) -> str:
        """Get the tool name"""
        return self._name

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description shown to the LLM

        This description should clearly explain what the tool does and how
        it should be used. The LLM will use this description to determine
        when to use the tool.

        Returns:
            A string describing the tool's functionality
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the tool with the provided parameters

        This method should implement the tool's core functionality. It receives
        keyword arguments from the LLM's tool call and should return a ToolResponse
        indicating success or failure.

        Args:
            **kwargs: Keyword arguments passed by the LLM

        Returns:
            ToolResponse indicating success/failure and containing results
        """
        pass

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate the parameters before execution

        Override this method to add custom parameter validation logic.
        The default implementation accepts all parameters.

        Args:
            params: Dictionary of parameters to validate

        Returns:
            True if parameters are valid, False otherwise
        """
        return True
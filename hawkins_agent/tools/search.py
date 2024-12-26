"""Web search tool implementation using Tavily API"""

from typing import Dict, Any, Optional
import logging
from tavily import TavilyClient
from .base import BaseTool
from ..types import ToolResponse

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    """Tool for web searching using Tavily AI

    This tool provides web search capabilities with:
    - High-quality, recent information
    - Smart filtering and ranking
    - Easy-to-parse responses
    """

    def __init__(self, api_key: str, name: Optional[str] = None):
        """Initialize the search tool

        Args:
            api_key: Tavily API key
            name: Optional custom name for the tool
        """
        super().__init__(name=name or "WebSearchTool")
        self.client = TavilyClient(api_key=api_key)

    @property 
    def description(self) -> str:
        """Get the tool description"""
        return "Search the web for recent and accurate information using Tavily AI"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate search parameters

        Args:
            params: Dictionary containing search parameters

        Returns:
            True if parameters are valid, False otherwise
        """
        if not isinstance(params, dict):
            logger.error("Parameters must be a dictionary")
            return False

        if "query" not in params:
            logger.error("Missing required 'query' parameter")
            return False

        query = params["query"]
        if not isinstance(query, str) or not query.strip():
            logger.error("Query must be a non-empty string")
            return False

        return True

    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the web search

        Args:
            **kwargs: Must include 'query' parameter

        Returns:
            ToolResponse containing search results or error
        """
        try:
            query = kwargs.get("query")
            if not query:
                return ToolResponse(
                    success=False,
                    result=None,
                    error="Missing required 'query' parameter"
                )

            # Validate parameters
            if not self.validate_params({"query": query}):
                return ToolResponse(
                    success=False,
                    result=None,
                    error="Invalid query parameter"
                )

            logger.info(f"Executing Tavily search for query: {query}")

            # Execute search with Tavily
            response = await self.client.search_async(query)

            # Format the results
            results = []
            for result in response.get("results", []):
                results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("content", ""),
                    "url": result.get("url", ""),
                    "score": result.get("score", 0)
                })

            return ToolResponse(
                success=True,
                result={"results": results},
                error=None
            )

        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return ToolResponse(
                success=False,
                result=None,
                error=f"Search failed: {str(e)}"
            )
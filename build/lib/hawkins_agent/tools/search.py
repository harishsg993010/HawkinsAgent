"""Web search tool implementation using Tavily API"""

from typing import Dict, Any, Optional
import logging
import json
from tavily import TavilyClient
from .base import BaseTool
from ..types import ToolResponse

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    """Tool for web searching using Tavily AI"""

    def __init__(self, api_key: str):
        """Initialize the search tool

        Args:
            api_key: Tavily API key for authentication
        """
        super().__init__(name="web_search")
        self.client = TavilyClient(api_key=api_key)

    @property 
    def description(self) -> str:
        """Get the tool description"""
        return "Search the web for recent and accurate information using Tavily AI"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate search parameters

        Args:
            params: Dictionary of parameters to validate

        Returns:
            True if parameters are valid, False otherwise
        """
        if 'query' not in params:
            logger.error("Missing required 'query' parameter")
            return False

        query = params.get('query')
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
            # Extract and validate query
            query = kwargs.get("query")
            if not self.validate_params({"query": query}):
                return ToolResponse(
                    success=False, 
                    error="Invalid or missing query parameter",
                    result=None
                )

            logger.info(f"Executing Tavily search for query: {query}")

            # Execute search with Tavily
            search_params = {
                "query": query,
                "search_depth": "advanced",
                "include_raw_content": False,
                "include_domains": [],
                "exclude_domains": [],
                "max_results": 3
            }

            # Use synchronous search since Tavily client doesn't support async
            response = self.client.search(query=query)

            if not response or "results" not in response:
                logger.error("Invalid response from Tavily API")
                return ToolResponse(
                    success=False,
                    error="Invalid API response",
                    result=None
                )

            # Format the results
            results = []
            for result in response.get("results", [])[:3]:  # Limit to top 3 results
                results.append({
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "url": result.get("url", ""),
                    "score": result.get("relevance_score", 0)
                })

            # Create a concise summary
            summary = f"Found {len(results)} relevant results:\n\n"
            for result in results:
                summary += f"- {result['content'][:250]}...\n"
                summary += f"  Source: {result['url']}\n\n"

            return ToolResponse(
                success=True,
                result=summary,
                error=None
            )

        except Exception as e:
            error_msg = f"Search failed: {str(e)}"
            logger.error(error_msg)
            return ToolResponse(
                success=False,
                result=None,
                error=error_msg
            )
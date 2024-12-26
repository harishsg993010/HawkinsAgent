"""Web search tool implementation using Tavily API"""

from typing import Dict, Any, Optional, List
import logging
from tavily import TavilyClient
from .base import BaseTool
from ..types import ToolResponse

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    """Tool for web searching using Tavily AI"""

    def __init__(self, api_key: str, name: Optional[str] = None):
        """Initialize the search tool"""
        super().__init__(name=name or "WebSearchTool")
        self.client = TavilyClient(api_key=api_key)

    @property 
    def description(self) -> str:
        """Get the tool description"""
        return "Search the web for recent and accurate information using Tavily AI"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate search parameters"""
        if 'query' not in params:
            logger.error("Missing required 'query' parameter")
            return False

        query = params.get('query')
        if not isinstance(query, str) or not query.strip():
            logger.error("Query must be a non-empty string")
            return False

        return True

    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the web search"""
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
            response = self.client.search(
                query=query,
                search_depth="advanced",
                include_raw_content=False
            )

            # Format the results
            results = []
            for result in response.get("results", [])[:3]:  # Limit to top 3 results
                results.append({
                    "title": result.get("title", ""),
                    "content": result.get("content", ""),
                    "score": result.get("score", 0)
                })

            # Create a concise summary
            summary = f"Found {len(results)} relevant results:\n\n" + "\n\n".join(
                f"- {result['content'][:250]}..." 
                for result in results
            )

            return ToolResponse(
                success=True,
                result=summary,
                error=None
            )

        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return ToolResponse(
                success=False,
                result=None,
                error=f"Search failed: {str(e)}"
            )
"""RAG tool implementation using HawkinsRAG"""

from typing import Dict, Any
from hawkins_rag import HawkinsRAG
from .base import BaseTool
from ..types import ToolResponse

class RAGTool(BaseTool):
    """Tool for retrieving information from knowledge base"""

    def __init__(self, knowledge_base: HawkinsRAG):
        super().__init__(name="RAGTool")
        self.kb = knowledge_base

    @property
    def description(self) -> str:
        return "Query the knowledge base for information"

    async def execute(self, **kwargs) -> ToolResponse:
        """Query the knowledge base"""
        try:
            query = kwargs.get('query', '')
            results = await self.kb.query(query)
            return ToolResponse(
                success=True,
                result=results,
                error=None
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                result=None,
                error=str(e)
            )
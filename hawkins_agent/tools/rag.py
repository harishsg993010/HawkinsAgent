"""RAG tool implementation using Hawkins_rag"""

from typing import Dict, Any
from ..mock import KnowledgeBase
from .base import BaseTool
from ..types import ToolResponse

class RAGTool(BaseTool):
    """Tool for retrieving information from knowledge base"""

    def __init__(self, knowledge_base: KnowledgeBase):
        super().__init__()
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
                result=results
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                result=None,
                error=str(e)
            )
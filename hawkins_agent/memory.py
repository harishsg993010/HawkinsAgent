"""Memory management using HawkinDB"""

from typing import Dict, List, Any, Optional
from .mock import HawkinDB
from .types import Message

class MemoryManager:
    """Manages agent memory using HawkinDB"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.db = HawkinDB(**self.config)
        
    async def add_interaction(self, user_message: str, agent_response: str):
        """Add an interaction to memory"""
        await self.db.insert({
            "type": "interaction",
            "user_message": user_message,
            "agent_response": agent_response,
            "timestamp": self.db.now()
        })
        
    async def get_relevant_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on the query"""
        return await self.db.search(
            collection="interactions",
            query=query,
            limit=limit
        )
        
    async def clear(self):
        """Clear all memories"""
        await self.db.clear()
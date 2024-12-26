"""Memory management using HawkinDB"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from .storage import HawkinDBStorage, StorageConfig

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages agent memory using HawkinDB

    This class provides sophisticated memory management including:
    - Short-term and long-term memory storage
    - Contextual memory retrieval
    - Memory pruning and organization
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize memory manager

        Args:
            config: Optional configuration for memory management
        """
        config = config or {}
        storage_config = StorageConfig(
            retention_days=config.get('retention_days'),
            max_entries=config.get('max_entries'),
            importance_threshold=config.get('importance_threshold', 0.0)
        )
        self.storage = HawkinDBStorage(config=storage_config)

    async def add_interaction(self, user_message: str, agent_response: str):
        """Add an interaction to memory

        Args:
            user_message: The user's message
            agent_response: The agent's response
        """
        try:
            # Convert interaction to HawkinsDB compatible format
            memory_data = {
                "column": "memory_type",
                "name": f"interaction_{datetime.now().timestamp()}",
                "properties": {
                    "user_message": user_message,
                    "agent_response": agent_response,
                    "timestamp": self.storage.now()
                },
                "metadata": {
                    "importance": self._calculate_importance(user_message)
                }
            }

            await self.storage.insert(memory_data)
            logger.info(f"Added interaction to memory: {user_message[:50]}...")

        except Exception as e:
            logger.error(f"Error adding interaction to memory: {str(e)}")

    async def get_relevant_memories(
        self,
        query: str,
        limit: int = 5,
        time_window: Optional[timedelta] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on the query

        Args:
            query: The query to search for relevant memories
            limit: Maximum number of memories to retrieve
            time_window: Optional time window to restrict search

        Returns:
            List of relevant memory entries
        """
        try:
            memories = await self.storage.search(
                query=query,
                collection="memories",
                limit=limit
            )

            # Filter by time window if specified
            if time_window and memories:
                current_time = datetime.fromisoformat(self.storage.now())
                memories = [
                    m for m in memories
                    if (current_time - datetime.fromisoformat(m.get('properties', {}).get('timestamp', ''))) <= time_window
                ]

            return memories

        except Exception as e:
            logger.error(f"Error retrieving memories: {str(e)}")
            return []

    def _calculate_importance(self, message: str) -> float:
        """Calculate the importance score of a message

        This implementation uses a simple length-based scoring system,
        but could be enhanced with more sophisticated importance calculation.

        Args:
            message: The message to evaluate

        Returns:
            Importance score between 0 and 1
        """
        # Simple length-based importance
        return min(len(message) / 1000, 1.0)

    async def add_knowledge(self, knowledge: Dict[str, Any]):
        """Add permanent knowledge to memory

        Args:
            knowledge: Knowledge to store
        """
        try:
            # Convert knowledge to HawkinsDB compatible format
            knowledge_data = {
                "column": "memory_type",
                "name": f"knowledge_{datetime.now().timestamp()}",
                "properties": {
                    "content": knowledge,
                    "timestamp": self.storage.now()
                }
            }

            await self.storage.insert(knowledge_data)

        except Exception as e:
            logger.error(f"Error adding knowledge to memory: {str(e)}")

    async def clear(self):
        """Clear all memories

        This should be used with caution as it removes all stored memories.
        """
        try:
            await self.storage.clear()
            logger.info("Cleared all memories")

        except Exception as e:
            logger.error(f"Error clearing memories: {str(e)}")
"""HawkinDB storage implementation"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from hawkinsdb import HawkinsDB
from .base import BaseStorage, StorageConfig

logger = logging.getLogger(__name__)

class HawkinDBStorage(BaseStorage):
    """Storage implementation using HawkinDB

    This class provides a concrete implementation of the BaseStorage
    interface using HawkinDB as the underlying storage engine.
    """

    def __init__(self, config: Optional[StorageConfig] = None, **kwargs):
        """Initialize HawkinDB storage

        Args:
            config: Storage configuration
            **kwargs: Additional HawkinDB configuration
        """
        super().__init__(config)
        self.db = HawkinsDB(storage_type='sqlite')

    async def insert(self, data: Dict[str, Any]) -> str:
        """Insert data into HawkinDB

        Args:
            data: Data to store

        Returns:
            ID of the stored data
        """
        try:
            result = self.db.add_entity(data)
            return str(result.get('id', datetime.now().timestamp()))
        except Exception as e:
            logger.error(f"Error inserting data: {str(e)}")
            raise

    async def search(self,
                    query: str,
                    collection: str,
                    limit: int = 10) -> List[Dict[str, Any]]:
        """Search for data in HawkinDB

        Args:
            query: Search query
            collection: Collection to search in
            limit: Maximum number of results

        Returns:
            List of matching entries
        """
        try:
            frames = self.db.query_frames(query)
            return frames[:limit] if frames else []
        except Exception as e:
            logger.error(f"Error searching data: {str(e)}")
            return []

    async def clear(self) -> None:
        """Clear all data from HawkinDB"""
        try:
            # Reset the database
            self.db = HawkinsDB(storage_type='sqlite')
            logger.info("Cleared all data from HawkinDB")
        except Exception as e:
            logger.error(f"Error clearing data: {str(e)}")
            raise

    def now(self) -> str:
        """Get current timestamp

        Returns:
            ISO formatted timestamp string
        """
        return datetime.now().isoformat()

    async def _prune_by_age(self, collection: str) -> None:
        """Remove old entries based on retention policy"""
        if not self.config.retention_days:
            return

        try:
            cutoff = datetime.now() - timedelta(days=self.config.retention_days)
            entities = self.db.list_entities()

            for entity in entities:
                frames = self.db.query_frames(entity)
                if frames and 'timestamp' in frames[0]:
                    if datetime.fromisoformat(frames[0]['timestamp']) < cutoff:
                        self.db.remove_entity(entity)

            logger.info(f"Pruned entries older than {cutoff}")
        except Exception as e:
            logger.error(f"Error pruning old data: {str(e)}")

    async def _prune_by_importance(self, collection: str) -> None:
        """Remove entries below importance threshold"""
        if not self.config.importance_threshold:
            return

        try:
            threshold = self.config.importance_threshold
            entities = self.db.list_entities()

            for entity in entities:
                frames = self.db.query_frames(entity)
                if frames and 'metadata' in frames[0]:
                    importance = frames[0].get('metadata', {}).get('importance', 0)
                    if importance < threshold:
                        self.db.remove_entity(entity)

            logger.info(f"Pruned entries below importance {threshold}")
        except Exception as e:
            logger.error(f"Error pruning low importance data: {str(e)}")
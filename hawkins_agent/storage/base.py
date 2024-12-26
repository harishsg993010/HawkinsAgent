"""Base storage interface definitions"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class StorageConfig:
    """Configuration for storage providers
    
    Attributes:
        retention_days: Number of days to retain memories
        max_entries: Maximum number of entries to store
        importance_threshold: Minimum importance score for retention
    """
    retention_days: Optional[int] = None
    max_entries: Optional[int] = None
    importance_threshold: float = 0.0

class BaseStorage(ABC):
    """Abstract base class for storage implementations
    
    This class defines the interface that all storage providers must implement,
    providing basic CRUD operations and memory management functionality.
    """
    
    def __init__(self, config: Optional[StorageConfig] = None):
        """Initialize storage with optional configuration
        
        Args:
            config: Storage configuration parameters
        """
        self.config = config or StorageConfig()
        
    @abstractmethod
    async def insert(self, data: Dict[str, Any]) -> str:
        """Insert data into storage
        
        Args:
            data: Data to store
            
        Returns:
            ID of the stored data
        """
        pass
        
    @abstractmethod
    async def search(self,
                    query: str,
                    collection: str,
                    limit: int = 10) -> List[Dict[str, Any]]:
        """Search for data in storage
        
        Args:
            query: Search query
            collection: Collection to search in
            limit: Maximum number of results
            
        Returns:
            List of matching entries
        """
        pass
        
    @abstractmethod
    async def clear(self) -> None:
        """Clear all data from storage"""
        pass
        
    @abstractmethod
    def now(self) -> str:
        """Get current timestamp in ISO format
        
        Returns:
            Current timestamp string
        """
        pass
        
    async def prune(self, collection: str) -> None:
        """Prune old or low-importance data
        
        Args:
            collection: Collection to prune
        """
        if self.config.retention_days:
            await self._prune_by_age(collection)
            
        if self.config.importance_threshold > 0:
            await self._prune_by_importance(collection)
            
    @abstractmethod
    async def _prune_by_age(self, collection: str) -> None:
        """Remove entries older than retention period"""
        pass
        
    @abstractmethod
    async def _prune_by_importance(self, collection: str) -> None:
        """Remove entries below importance threshold"""
        pass

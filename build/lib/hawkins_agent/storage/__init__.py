"""
Storage module for Hawkins Agent Framework

This module provides database integration and storage management capabilities,
including memory storage using HawkinDB and base interfaces for custom storage implementations.
"""

from .base import BaseStorage, StorageConfig
from .hawkindb import HawkinDBStorage

__all__ = ["BaseStorage", "StorageConfig", "HawkinDBStorage"]
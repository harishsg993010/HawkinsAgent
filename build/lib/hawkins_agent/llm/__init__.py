"""
LiteLLM integration module for Hawkins Agent Framework

This module provides integration with LiteLLM for language model interactions,
including response parsing, error handling, and prompt management.
"""

from .base import BaseLLMProvider
from .lite_llm import LiteLLMProvider
from .manager import LLMManager

__all__ = ["BaseLLMProvider", "LiteLLMProvider", "LLMManager"]

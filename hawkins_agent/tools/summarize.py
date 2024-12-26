"""Text summarization tool implementation"""

from typing import Dict, Any
import logging
from .base import BaseTool
from ..types import ToolResponse

logger = logging.getLogger(__name__)

class SummarizationTool(BaseTool):
    """Tool for summarizing long text content"""

    def __init__(self):
        """Initialize the summarization tool"""
        super().__init__(name="text_summarize")

    @property
    def description(self) -> str:
        """Get the tool description"""
        return "Summarize long text content into concise key points"

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate summarization parameters

        Args:
            params: Dictionary containing summarization parameters

        Returns:
            True if parameters are valid, False otherwise
        """
        if 'query' not in params:
            logger.error("Missing required 'query' parameter")
            return False

        text = params.get('query')
        if not isinstance(text, str) or not text.strip():
            logger.error("Text must be a non-empty string")
            return False

        return True

    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the summarization

        Args:
            **kwargs: Must include 'query' parameter containing the text to summarize

        Returns:
            ToolResponse containing the summarized text or error
        """
        try:
            # Extract and validate text
            text = kwargs.get("query", "")
            if not self.validate_params({"query": text}):
                return ToolResponse(
                    success=False,
                    error="Invalid or missing text parameter",
                    result=None
                )

            logger.info("Executing text summarization")
            logger.debug(f"Input text length: {len(text)}")

            # Handle empty or very short text
            if len(text.strip()) < 50:
                return ToolResponse(
                    success=True,
                    result=text.strip(),
                    error=None
                )

            # Split text into sentences (handling potential None case)
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            total_sentences = len(sentences)

            # For longer texts, extract key sentences
            if total_sentences > 5:
                # Extract important sentences - first, middle, and last
                key_sentences = [
                    sentences[0],  # Introduction
                    sentences[total_sentences // 2],  # Middle point
                    sentences[-1]  # Conclusion
                ]

                # Add additional important sentences based on length
                if total_sentences > 10:
                    key_sentences.insert(1, sentences[total_sentences // 4])
                    key_sentences.insert(-1, sentences[3 * total_sentences // 4])

                summary = '. '.join(sent for sent in key_sentences if sent) + '.'
            else:
                # For shorter texts, use all sentences
                summary = '. '.join(sentences) + '.'

            logger.info(f"Generated summary of length {len(summary)}")
            return ToolResponse(
                success=True,
                result=summary,
                error=None
            )

        except Exception as e:
            error_msg = f"Summarization failed: {str(e)}"
            logger.error(error_msg)
            return ToolResponse(
                success=False,
                result=None,
                error=error_msg
            )
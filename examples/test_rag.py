"""Test basic HawkinsRAG functionality"""

from hawkins_rag import HawkinsRAG
import asyncio
import logging
import tempfile
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Test basic RAG functionality"""
    try:
        # Initialize RAG system
        logger.info("Initializing RAG system...")
        rag = HawkinsRAG()

        # Test document content
        test_content = """
        Artificial Intelligence in 2024 has seen remarkable developments.
        Key trends include:
        1. Advanced language models
        2. Improved multimodal capabilities
        3. Focus on AI safety and ethics
        """

        # Create temporary file for test content
        logger.info("Creating test document...")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_path = temp_file.name

        try:
            # Load document
            logger.info("Loading test document...")
            rag.load_document(temp_path, source_type="text")

            # Test query
            logger.info("Testing query...")
            query = "What are the key trends in AI?"
            response = rag.query(query)

            logger.info("\nQuery Results:")
            logger.info("-" * 40)
            logger.info(f"Query: {query}")
            logger.info(f"Response: {response}")

        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            logger.info("Cleaned up temporary file")

    except Exception as e:
        logger.error(f"Error in RAG test: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
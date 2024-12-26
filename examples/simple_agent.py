"""Example of creating a simple agent"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import EmailTool, WebSearchTool
from hawkins_agent.mock import KnowledgeBase
from hawkins_agent.llm import LiteLLMProvider
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Demonstrate basic agent functionality"""
    try:
        # Create a knowledge base
        kb = KnowledgeBase()

        # Get Tavily API key
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            logger.error("TAVILY_API_KEY environment variable not set")
            return

        # Configure search tool with Tavily
        search_tool = WebSearchTool(api_key=tavily_api_key)

        # Create an agent with GPT-4o
        logger.info("Creating agent with GPT-4o...")
        agent = (AgentBuilder("assistant")
                .with_model("openai/gpt-4o")  # Use latest OpenAI model
                .with_provider(LiteLLMProvider, temperature=0.7)
                .with_knowledge_base(kb)
                .with_tool(search_tool)
                .with_tool(EmailTool())
                .build())

        # Test the agent with a search query
        logger.info("Testing agent with a search query...")
        response = await agent.process("Can you search for information about the latest AI developments?")

        # Print response details
        logger.info("\nAgent Response:")
        logger.info("-" * 40)
        logger.info(response.message)

        if response.tool_calls:
            logger.info("\nTool Calls Made:")
            logger.info("-" * 40)
            for call in response.tool_calls:
                logger.info(f"Tool: {call['name']}")
                logger.info(f"Parameters: {call['parameters']}")

    except Exception as e:
        logger.error(f"Error running simple agent: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
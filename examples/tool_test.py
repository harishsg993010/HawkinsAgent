"""Example demonstrating various tool capabilities"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import WebSearchTool, RAGTool, SummarizationTool, CodeInterpreterTool
from hawkins_agent.mock import KnowledgeBase
from hawkins_agent.llm import LiteLLMProvider
import logging
import os
import asyncio

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Demonstrate tool usage"""
    try:
        # Create a knowledge base
        kb = KnowledgeBase()

        # Get Tavily API key
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            logger.error("TAVILY_API_KEY environment variable not set")
            return

        # Configure tools
        search_tool = WebSearchTool(api_key=tavily_api_key)
        rag_tool = RAGTool(kb)
        summarize_tool = SummarizationTool()
        code_tool = CodeInterpreterTool(model="gpt-4o")

        # Create agent with tools
        logger.info("Creating agent with tools...")
        agent = (AgentBuilder("tool_tester")
                .with_model("openai/gpt-4o")
                .with_provider(LiteLLMProvider, temperature=0.7)
                .with_knowledge_base(kb)
                .with_tool(search_tool)
                .with_tool(rag_tool)
                .with_tool(summarize_tool)
                .with_tool(code_tool)
                .build())

        # Test queries
        queries = [
            "What are the latest developments in quantum computing?",
            "Could you summarize the findings from the quantum computing research?",
            "Write a Python function to calculate the Fibonacci sequence"
        ]

        for query in queries:
            logger.info(f"\nProcessing query: {query}")
            response = await agent.process(query)

            logger.info("\nResponse:")
            logger.info("-" * 40)
            logger.info(response.message)

            if response.tool_calls:
                logger.info("\nTool Calls Made:")
                logger.info("-" * 40)
                for call in response.tool_calls:
                    logger.info(f"Tool: {call['name']}")
                    logger.info(f"Parameters: {call['parameters']}")

            if "tool_results" in response.metadata:
                logger.info("\nTool Results:")
                logger.info("-" * 40)
                for result in response.metadata["tool_results"]:
                    if result["success"]:
                        logger.info(f"Success: {result['result']}")
                    else:
                        logger.error(f"Error: {result['error']}")

    except Exception as e:
        logger.error(f"Error in tool demonstration: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
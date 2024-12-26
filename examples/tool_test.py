"""Example demonstrating various tool capabilities"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import WeatherTool
from hawkins_agent.mock import KnowledgeBase
from hawkins_agent.llm import LiteLLMProvider
import logging
import os
import asyncio

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Test weather tool functionality"""
    try:
        # Create a knowledge base
        kb = KnowledgeBase()

        # Configure weather tool with API key
        logger.info("Initializing weather tool...")
        weather_tool = WeatherTool(api_key="1b73fe8fc5a03431a43f83fa899d0a4d")

        # Create agent with weather tool
        logger.info("Creating agent with weather tool...")
        agent = (AgentBuilder("weather_tester")
                .with_model("openai/gpt-4o")
                .with_provider(LiteLLMProvider, temperature=0.7)
                .with_knowledge_base(kb)
                .with_tool(weather_tool)
                .build())

        # Test queries
        queries = [
            "What's the current weather in London,GB?",
            "Tell me the weather in Tokyo,JP",
            "What's the weather like in New York,US?"
        ]

        for query in queries:
            logger.info(f"\nProcessing query: {query}")
            try:
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
                            weather_data = result["result"]
                            logger.info("Weather Information:")
                            logger.info(f"- Temperature: {weather_data['temperature']}°C")
                            logger.info(f"- Feels like: {weather_data['feels_like']}°C")
                            logger.info(f"- Description: {weather_data['description']}")
                            logger.info(f"- Humidity: {weather_data['humidity']}%")
                            logger.info(f"- Wind Speed: {weather_data['wind_speed']} m/s")
                            logger.info(f"- Pressure: {weather_data['pressure']} hPa")
                        else:
                            logger.error(f"Error: {result['error']}")

            except Exception as e:
                logger.error(f"Error processing query '{query}': {str(e)}", exc_info=True)

    except Exception as e:
        logger.error(f"Error in weather tool demonstration: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
"""Test different LLM models using LiteLLM integration"""

from hawkins_agent import AgentBuilder
from hawkins_agent.llm import LiteLLMProvider
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Test different LLM models"""
    try:
        # Create an OpenAI agent
        logger.info("Creating agent with GPT-4o...")
        openai_agent = (AgentBuilder("openai_assistant")
                     .with_model("openai/gpt-4o")  # Latest OpenAI model
                     .with_provider(LiteLLMProvider, temperature=0.7)
                     .build())

        # Create an Anthropic agent
        logger.info("Creating agent with Claude 3...")
        anthropic_agent = (AgentBuilder("anthropic_assistant")
                        .with_model("anthropic/claude-3-sonnet-20240229")  # Claude model
                        .with_provider(LiteLLMProvider, temperature=0.5)
                        .build())

        # Test both agents
        test_message = "What is the capital of France?"

        logger.info("\nTesting OpenAI agent...")
        openai_response = await openai_agent.process(test_message)
        logger.info(f"OpenAI Response: {openai_response.message}")

        logger.info("\nTesting Anthropic agent...")
        anthropic_response = await anthropic_agent.process(test_message)
        logger.info(f"Anthropic Response: {anthropic_response.message}")

    except Exception as e:
        logger.error(f"Error testing models: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())

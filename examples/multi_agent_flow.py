"""Example of creating multiple agents with flow control"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import RAGTool, WebSearchTool
from hawkins_agent.mock import KnowledgeBase, Document
from hawkins_agent.flow import FlowManager, FlowStep
from hawkins_agent.llm import LiteLLMProvider
import logging
import os
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Demonstrate multi-agent workflow with flow control"""
    try:
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        logger.info("Initializing knowledge bases...")
        research_kb = KnowledgeBase()
        support_kb = KnowledgeBase()

        # Create mock data instead of loading files
        logger.info("Creating mock knowledge base data...")

        # Create Document objects with content
        research_docs = [
            Document("AI is rapidly evolving with focus on multimodal models and efficient training"),
            Document("Enterprises are adopting AI for automation and decision support"),
            Document("Latest research focuses on making AI more reliable and explainable")
        ]

        support_docs = [
            Document("Follow industry standards for AI implementation"),
            Document("Ensure ethical AI usage and proper documentation"),
            Document("Provide comprehensive support for AI integration")
        ]

        # Add documents to knowledge bases
        for doc in research_docs:
            await research_kb.add_document(doc)
        for doc in support_docs:
            await support_kb.add_document(doc)

        # Get Tavily API key for web search
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            logger.error("TAVILY_API_KEY environment variable not set")
            return

        # Create research agent with GPT-4o for complex analysis
        logger.info("Creating research agent...")
        researcher = (AgentBuilder("researcher")
                     .with_model("openai/gpt-4o")  # Latest OpenAI model
                     .with_provider(LiteLLMProvider, temperature=0.7)
                     .with_knowledge_base(research_kb)
                     .with_tool(WebSearchTool(api_key=tavily_api_key))
                     .with_memory({"retention_days": 7})
                     .build())

        # Create support agent with Claude 3 Sonnet for summarization
        logger.info("Creating support agent...")
        support = (AgentBuilder("support")
                   .with_model("anthropic/claude-3-sonnet-20240229")  # Claude 3 for summaries
                   .with_provider(LiteLLMProvider, temperature=0.5)
                   .with_knowledge_base(support_kb)
                   .with_tool(RAGTool(support_kb))
                   .with_memory({"retention_days": 30})
                   .build())

        # Create flow steps
        async def research_step(data: dict) -> dict:
            """Execute research phase"""
            response = await researcher.process(
                "Analyze current AI trends and their impact on enterprise applications",
                context={"focus": data.get("focus", "enterprise applications")}
            )
            return {
                "research_findings": response.message,
                "tool_calls": response.tool_calls
            }

        async def summary_step(data: dict) -> dict:
            """Execute summary phase"""
            response = await support.process(
                f"Create a summary of: {data['research_findings']}",
                context={"format": "bullet points"}
            )
            return {
                "summary": response.message,
                "tool_calls": response.tool_calls
            }

        # Configure workflow
        flow = FlowManager()
        flow.add_step(FlowStep(
            name="research",
            agent=researcher,
            process=research_step
        ))
        flow.add_step(FlowStep(
            name="summarize",
            agent=support,
            process=summary_step,
            requires=["research"]  # Must wait for research to complete
        ))

        # Execute workflow
        logger.info("Executing workflow...")
        results = await flow.execute({
            "focus": "enterprise applications",
            "format": "concise bullet points"
        })

        # Display results
        logger.info("\n" + "="*50)
        logger.info("Research Findings:")
        logger.info("="*50)
        logger.info(results["research"]["research_findings"])

        logger.info("\n" + "="*50)
        logger.info("Summarized Insights:")
        logger.info("="*50)
        logger.info(results["summarize"]["summary"])

        # Log tool usage
        for step, data in results.items():
            if data.get("tool_calls"):
                logger.info(f"\nTools used in {step} phase:")
                for call in data["tool_calls"]:
                    logger.info(f"- {call['name']}: {call['parameters']}")

    except Exception as e:
        logger.error(f"Error in multi-agent workflow: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
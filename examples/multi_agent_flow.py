"""Example of creating multiple agents with flow logic"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import RAGTool, WebSearchTool
from hawkins_agent.mock import KnowledgeBase, HawkinDB
import logging

logger = logging.getLogger(__name__)

async def main():
    """Demonstrate multi-agent workflow with specialized agents"""
    try:
        # Create knowledge bases
        research_kb = KnowledgeBase()
        support_kb = KnowledgeBase()

        await research_kb.add_document("docs/research.pdf")
        await support_kb.add_document("docs/support.pdf")

        # Create specialized agents
        researcher = (AgentBuilder("researcher")
                     .with_model("gpt-4")  # Use more capable model for research
                     .with_knowledge_base(research_kb)
                     .with_tool(WebSearchTool())
                     .with_memory({"retention_days": 7})
                     .build())

        support = (AgentBuilder("support")
                  .with_model("gpt-3.5-turbo")  # Use faster model for support
                  .with_knowledge_base(support_kb)
                  .with_tool(RAGTool(support_kb))
                  .with_memory({"retention_days": 30})
                  .build())

        # Use agents in a workflow
        logger.info("Starting research phase...")
        research_response = await researcher.process(
            "Find latest AI trends",
            context={"focus": "enterprise applications"}
        )

        logger.info("Starting summary phase...")
        support_response = await support.process(
            f"Create a summary of: {research_response.message}",
            context={"format": "bullet points"}
        )

        print("\nResearch findings:")
        print(research_response.message)
        print("\nSummarized insights:")
        print(support_response.message)

    except Exception as e:
        logger.error(f"Error in multi-agent workflow: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
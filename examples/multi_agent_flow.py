"""Example of creating multiple agents with flow control"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import RAGTool, WebSearchTool
from hawkins_agent.mock import KnowledgeBase
from hawkins_agent.flow import FlowManager, FlowStep
import logging

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

        # Simulate loading documents
        logger.info("Loading knowledge base documents...")
        await research_kb.add_document("docs/research.pdf")
        await support_kb.add_document("docs/support.pdf")

        logger.info("Creating research agent...")
        researcher = (AgentBuilder("researcher")
                     .with_model("gpt-4")  # Use more capable model for research
                     .with_knowledge_base(research_kb)
                     .with_tool(WebSearchTool())
                     .with_memory({"retention_days": 7})
                     .build())

        logger.info("Creating support agent...")
        support = (AgentBuilder("support")
                  .with_model("gpt-3.5-turbo")  # Use faster model for support
                  .with_knowledge_base(support_kb)
                  .with_tool(RAGTool(support_kb))
                  .with_memory({"retention_days": 30})
                  .build())

        # Create flow steps
        async def research_step(data: dict) -> dict:
            """Execute research phase"""
            response = await researcher.process(
                "Find latest AI trends",
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
    import asyncio
    asyncio.run(main())
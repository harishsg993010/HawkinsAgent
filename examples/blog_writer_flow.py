"""Example of multi-agent blog writing system"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import RAGTool, WebSearchTool, SummarizationTool
from hawkins_agent.mock import KnowledgeBase
from hawkins_agent.flow import FlowManager, FlowStep
from hawkins_agent.llm import LiteLLMProvider
import logging
import os
import asyncio

# Setup logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Demonstrate blog writing with multiple specialized agents"""
    try:
        # Set up knowledge bases
        logger.info("Initializing knowledge bases...")
        research_kb = KnowledgeBase()
        writer_kb = KnowledgeBase()
        editor_kb = KnowledgeBase()

        # Get Tavily API key for research
        tavily_api_key = os.environ.get("TAVILY_API_KEY")
        if not tavily_api_key:
            logger.error("TAVILY_API_KEY environment variable not set")
            return

        # Create research agent with GPT-4o for gathering information
        logger.info("Creating research agent...")
        researcher = (AgentBuilder("researcher")
                     .with_model("openai/gpt-4o")
                     .with_provider(LiteLLMProvider, temperature=0.7)
                     .with_knowledge_base(research_kb)
                     .with_tool(WebSearchTool(api_key=tavily_api_key))
                     .with_memory({"retention_days": 7})
                     .build())

        # Create writer agent with GPT-4o for creative writing
        logger.info("Creating writer agent...")
        writer = (AgentBuilder("writer")
                  .with_model("openai/gpt-4o")
                  .with_provider(LiteLLMProvider, temperature=0.8)
                  .with_knowledge_base(writer_kb)
                  .with_tool(RAGTool(writer_kb))
                  .with_memory({"retention_days": 30})
                  .build())

        # Create editor agent with Claude 3 for refinement
        logger.info("Creating editor agent...")
        editor = (AgentBuilder("editor")
                  .with_model("anthropic/claude-3-sonnet-20240229")
                  .with_provider(LiteLLMProvider, temperature=0.3)
                  .with_knowledge_base(editor_kb)
                  .with_tool(SummarizationTool())
                  .with_memory({"retention_days": 30})
                  .build())

        # Define flow steps
        async def research_step(data: dict) -> dict:
            """Execute research phase"""
            topic = data.get("topic", "AI trends")
            logger.info(f"Researching topic: {topic}")

            response = await researcher.process(
                f"Research this topic thoroughly and gather key information: {topic}",
                context={"focus": "comprehensive, factual information"}
            )

            logger.info("Research phase completed")
            logger.info("\nResearch findings:")
            logger.info("-" * 40)
            logger.info(response.message)

            return {
                "research": response.message,
                "tool_calls": response.tool_calls
            }

        async def writing_step(data: dict) -> dict:
            """Execute writing phase"""
            research_results = data.get("research", "")
            style = data.get("style", "informative")
            logger.info("Writing initial draft...")

            response = await writer.process(
                "Write a blog post based on this research: " + research_results,
                context={
                    "style": style,
                    "tone": "professional yet engaging",
                    "format": "blog post"
                }
            )

            logger.info("Writing phase completed")
            logger.info("\nInitial draft:")
            logger.info("-" * 40)
            logger.info(response.message)

            return {
                "draft": response.message,
                "tool_calls": response.tool_calls
            }

        async def editing_step(data: dict) -> dict:
            """Execute editing phase"""
            draft = data.get("draft", "")
            logger.info("Editing and refining the draft...")

            response = await editor.process(
                "Edit and improve this blog post draft: " + draft,
                context={
                    "focus": "clarity, engagement, and professionalism",
                    "maintain_voice": True
                }
            )

            logger.info("Editing phase completed")
            logger.info("\nFinal edited version:")
            logger.info("-" * 40)
            logger.info(response.message)

            return {
                "final_post": response.message,
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
            name="write",
            agent=writer,
            process=writing_step,
            requires=["research"]
        ))
        flow.add_step(FlowStep(
            name="edit",
            agent=editor,
            process=editing_step,
            requires=["write"]
        ))

        # Execute workflow with sample topic
        logger.info("\nExecuting blog writing workflow...")
        logger.info("=" * 50)
        results = await flow.execute({
            "topic": "The Impact of AI on Software Development in 2024",
            "style": "informative and engaging",
        })

        # Display results
        logger.info("\n" + "="*50)
        logger.info("Final Blog Post Results:")
        logger.info("="*50)
        logger.info("\nResearch Findings:")
        logger.info("-"*40)
        logger.info(results["research"]["research"])

        logger.info("\nInitial Draft:")
        logger.info("-"*40)
        logger.info(results["write"]["draft"])

        logger.info("\nFinal Blog Post:")
        logger.info("-"*40)
        logger.info(results["edit"]["final_post"])

        # Log tool usage
        for step, data in results.items():
            if data.get("tool_calls"):
                logger.info(f"\nTools used in {step} phase:")
                for call in data["tool_calls"]:
                    logger.info(f"- {call['name']}: {call['parameters']}")

    except Exception as e:
        logger.error(f"Error in blog writing workflow: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
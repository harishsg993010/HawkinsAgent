"""Example of multi-agent blog writing system"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import RAGTool, WebSearchTool, SummarizationTool
from hawkins_rag import HawkinsRAG
from hawkins_agent.flow import FlowManager, FlowStep
from hawkins_agent.llm import LiteLLMProvider
import logging
import os
import asyncio
import tempfile

# Setup logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Demonstrate blog writing with multiple specialized agents"""
    try:
        # Initialize knowledge bases
        logger.info("Initializing knowledge bases...")
        research_rag = HawkinsRAG()
        writer_rag = HawkinsRAG()
        editor_rag = HawkinsRAG()

        # Create temp directory for document storage
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {temp_dir}")

        try:
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
                         .with_knowledge_base(research_rag)
                         .with_tool(WebSearchTool(api_key=tavily_api_key))
                         .with_memory({"retention_days": 7})
                         .build())

            # Create writer agent with GPT-4o for creative writing
            logger.info("Creating writer agent...")
            writer = (AgentBuilder("writer")
                      .with_model("openai/gpt-4o")
                      .with_provider(LiteLLMProvider, temperature=0.8)
                      .with_knowledge_base(writer_rag)
                      .with_tool(RAGTool(writer_rag))
                      .with_memory({"retention_days": 30})
                      .build())

            # Create editor agent with Claude 3 for refinement
            logger.info("Creating editor agent...")
            editor = (AgentBuilder("editor")
                      .with_model("anthropic/claude-3-sonnet-20240229")
                      .with_provider(LiteLLMProvider, temperature=0.3)
                      .with_knowledge_base(editor_rag)
                      .with_tool(SummarizationTool())
                      .with_memory({"retention_days": 30})
                      .build())

            # Define flow steps
            async def research_step(data: dict) -> dict:
                """Execute research phase"""
                topic = data.get("topic", "AI trends")
                logger.info(f"Researching topic: {topic}")

                # Store initial topic
                topic_file = os.path.join(temp_dir, "topic.txt")
                with open(topic_file, 'w') as f:
                    f.write(f"Research topic: {topic}")
                research_rag.load_document(topic_file, source_type="text")

                response = research_rag.query(
                    f"Research this topic thoroughly and gather key information: {topic}"
                )

                logger.info("Research phase completed")
                logger.info("\nResearch findings:")
                logger.info("-" * 40)
                logger.info(response)

                # Store research findings
                research_file = os.path.join(temp_dir, "research.txt")
                with open(research_file, 'w') as f:
                    f.write(response)
                research_rag.load_document(research_file, source_type="text")

                return {
                    "research": response,
                    "tool_calls": []  # Since we're using direct RAG query
                }

            async def writing_step(data: dict) -> dict:
                """Execute writing phase"""
                research_results = data.get("research", "")
                style = data.get("style", "informative")
                logger.info("Writing initial draft...")

                # Store research for writer
                research_file = os.path.join(temp_dir, "writer_research.txt")
                with open(research_file, 'w') as f:
                    f.write(research_results)
                writer_rag.load_document(research_file, source_type="text")

                response = writer_rag.query(
                    "Write a blog post based on this research: " + research_results
                )

                logger.info("Writing phase completed")
                logger.info("\nInitial draft:")
                logger.info("-" * 40)
                logger.info(response)

                # Store draft
                draft_file = os.path.join(temp_dir, "draft.txt")
                with open(draft_file, 'w') as f:
                    f.write(response)
                writer_rag.load_document(draft_file, source_type="text")

                return {
                    "draft": response,
                    "tool_calls": []  # Since we're using direct RAG query
                }

            async def editing_step(data: dict) -> dict:
                """Execute editing phase"""
                draft = data.get("draft", "")
                logger.info("Editing and refining the draft...")

                # Store draft for editor
                draft_file = os.path.join(temp_dir, "editor_draft.txt")
                with open(draft_file, 'w') as f:
                    f.write(draft)
                editor_rag.load_document(draft_file, source_type="text")

                response = editor_rag.query(
                    "Edit and improve this blog post draft: " + draft
                )

                logger.info("Editing phase completed")
                logger.info("\nFinal edited version:")
                logger.info("-" * 40)
                logger.info(response)

                # Store final version
                final_file = os.path.join(temp_dir, "final.txt")
                with open(final_file, 'w') as f:
                    f.write(response)
                editor_rag.load_document(final_file, source_type="text")

                return {
                    "final_post": response,
                    "tool_calls": []  # Since we're using direct RAG query
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

        finally:
            # Clean up temp directory
            import shutil
            shutil.rmtree(temp_dir)
            logger.info("Cleaned up temporary directory")

    except Exception as e:
        logger.error(f"Error in blog writing workflow: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
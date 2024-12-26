"""Example of multi-agent blog writing system"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import RAGTool, WebSearchTool, SummarizationTool
from hawkins_rag import HawkinsRAG
import logging
import os
import asyncio
import tempfile
import shutil

# Setup logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleFlow:
    """A simplified flow manager for RAG operations"""

    def __init__(self):
        self.steps = []

    def add_step(self, name, func, requires=None):
        self.steps.append({
            'name': name,
            'func': func,
            'requires': requires or []
        })

    async def execute(self, input_data):
        results = {}
        for step in self.steps:
            try:
                # Wait for required steps
                for req in step['requires']:
                    if req not in results:
                        raise Exception(f"Required step {req} not completed")

                # Execute step
                logger.info(f"Executing step: {step['name']}")
                result = await step['func'](input_data, results)
                results[step['name']] = result

            except Exception as e:
                logger.error(f"Error in step {step['name']}: {str(e)}")
                results[step['name']] = {'error': str(e)}

        return results

async def main():
    """Demonstrate blog writing with RAG system"""
    try:
        # Initialize knowledge bases
        logger.info("Initializing RAG systems...")
        research_rag = HawkinsRAG()
        writer_rag = HawkinsRAG()
        editor_rag = HawkinsRAG()

        # Create temp directory for document storage
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {temp_dir}")

        try:
            async def research_step(input_data, previous_results):
                """Execute research phase"""
                topic = input_data.get("topic", "AI trends")
                logger.info(f"Researching topic: {topic}")

                try:
                    # Store topic
                    topic_file = os.path.join(temp_dir, "topic.txt")
                    with open(topic_file, 'w') as f:
                        f.write(f"Research topic: {topic}")
                    research_rag.load_document(topic_file, source_type="text")

                    # Query RAG
                    response = research_rag.query(
                        f"Research this topic thoroughly and gather key information: {topic}"
                    )
                    research_text = str(response)

                    logger.info("Research completed successfully")
                    return {'content': research_text}

                except Exception as e:
                    logger.error(f"Research error: {str(e)}")
                    return {'error': str(e)}

            async def writing_step(input_data, previous_results):
                """Execute writing phase"""
                try:
                    research = previous_results['research']['content']
                    style = input_data.get("style", "informative")

                    logger.info("Writing draft based on research...")

                    # Store research for writer
                    research_file = os.path.join(temp_dir, "research.txt")
                    with open(research_file, 'w') as f:
                        f.write(research)
                    writer_rag.load_document(research_file, source_type="text")

                    # Generate draft
                    response = writer_rag.query(
                        f"Write a {style} blog post based on this research: {research}"
                    )
                    draft_text = str(response)

                    logger.info("Draft completed successfully")
                    return {'content': draft_text}

                except Exception as e:
                    logger.error(f"Writing error: {str(e)}")
                    return {'error': str(e)}

            async def editing_step(input_data, previous_results):
                """Execute editing phase"""
                try:
                    draft = previous_results['writing']['content']
                    logger.info("Editing draft...")

                    # Store draft for editor
                    draft_file = os.path.join(temp_dir, "draft.txt")
                    with open(draft_file, 'w') as f:
                        f.write(draft)
                    editor_rag.load_document(draft_file, source_type="text")

                    # Edit draft
                    response = editor_rag.query(
                        "Edit and improve this blog post draft for clarity, engagement and professionalism: " + draft
                    )
                    final_text = str(response)

                    logger.info("Editing completed successfully")
                    return {'content': final_text}

                except Exception as e:
                    logger.error(f"Editing error: {str(e)}")
                    return {'error': str(e)}

            # Configure flow
            flow = SimpleFlow()
            flow.add_step('research', research_step)
            flow.add_step('writing', writing_step, ['research'])
            flow.add_step('editing', editing_step, ['writing'])

            # Execute flow
            logger.info("\nExecuting blog writing workflow...")
            logger.info("=" * 50)

            input_data = {
                "topic": "The Impact of AI on Software Development in 2024",
                "style": "informative and engaging"
            }

            logger.info(f"Input: {input_data}")
            results = await flow.execute(input_data)

            # Display results
            logger.info("\nWorkflow Results:")
            logger.info("=" * 50)

            for step_name, result in results.items():
                logger.info(f"\n{step_name.upper()} OUTPUT:")
                logger.info("-" * 40)
                if 'error' in result:
                    logger.error(f"Error in {step_name}: {result['error']}")
                else:
                    logger.info(result['content'])

        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir)
            logger.info("Cleaned up temporary directory")

    except Exception as e:
        logger.error(f"Error in blog writing workflow: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
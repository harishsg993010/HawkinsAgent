"""
Demonstration of AI agent using a knowledge base to answer questions.
Shows how to load documents and query them using RAG capabilities.
"""
from hawkins_agent import Agent, AgentConfig
from hawkins_agent.tools import RAGTool
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Configure the agent
    config = AgentConfig(
        name="Knowledge Assistant",
        role="Document analysis and query assistant",
        goal="Help users interact with documents and answer questions",
        tools=[RAGTool()],
        db_path="knowledge_demo.db",
        knowledge_base_path="knowledge_base.db"
    )

    # Initialize agent
    agent = Agent(config)

    # Example documents
    documents = [
        {
            "content": """
            Artificial Intelligence (AI) is transforming how we live and work. 
            Machine learning, a subset of AI, enables systems to learn from data.
            Natural Language Processing (NLP) helps computers understand human language.
            Reinforcement Learning allows AI systems to learn through trial and error.
            """,
            "metadata": {"topic": "AI Overview", "source": "introduction.txt"}
        },
        {
            "content": """
            Python is a popular programming language known for its simplicity and readability.
            It's widely used in AI, web development, and data science.
            Key features include dynamic typing, automatic memory management, and extensive libraries.
            Popular frameworks include TensorFlow, PyTorch, and Django.
            """,
            "metadata": {"topic": "Python Programming", "source": "python_guide.txt"}
        }
    ]

    print("\nTesting AI agent with knowledge base capabilities...")

    # Load documents
    for doc in documents:
        print(f"\nLoading document about {doc['metadata']['topic']}...")
        result = await agent.execute(
            task=f"Load document about {doc['metadata']['topic']}",
            context={
                "knowledge_action": {
                    "operation": "load",
                    "content": doc["content"],
                    "source_type": "text",
                    "metadata": doc["metadata"]
                }
            }
        )
        if result.get("success"):
            print(f"✓ Successfully loaded document about {doc['metadata']['topic']}")
        else:
            print(f"✗ Failed to load document: {result.get('error')}")

    # Test queries
    test_queries = [
        "What is artificial intelligence and its subfields?",
        "What are the main features of Python?",
        "How is Python used in AI development?",
        "What is the relationship between Machine Learning and AI?"
    ]

    print("\nTesting knowledge base queries...")

    for query in test_queries:
        print(f"\nQuery: {query}")
        result = await agent.execute(
            task=query,
            context={
                "knowledge_action": {
                    "operation": "query",
                    "query": query
                }
            }
        )

        if result.get("success"):
            print("Answer:", result.get("answer"))
        else:
            print("Error:", result.get("error"))

        # Show relevant context from memory
        context = agent.memory.get_relevant_context(query)
        if context["episodic_memories"]:
            print("\nRelated previous interactions:")
            for memory in context["episodic_memories"][:2]:  # Show top 2 related memories
                print(f"- Previous query: {memory['properties'].get('task')}")
                print(f"  Answer: {memory['properties'].get('final_answer')}")

if __name__ == "__main__":
    asyncio.run(main())

"""Example of creating multiple agents with flow logic"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import RAGTool, WebSearchTool
from hawkins_agent.mock import KnowledgeBase

async def main():
    # Create knowledge bases
    research_kb = KnowledgeBase()
    support_kb = KnowledgeBase()
    
    # Create specialized agents
    researcher = (AgentBuilder("researcher")
                 .with_knowledge_base(research_kb)
                 .with_tool(WebSearchTool())
                 .build())
    
    support = (AgentBuilder("support")
              .with_knowledge_base(support_kb)
              .with_tool(RAGTool(support_kb))
              .build())
    
    # Use agents in a flow
    research_response = await researcher.process("Find latest AI trends")
    support_response = await support.process(
        f"Create a summary of: {research_response.message}"
    )
    
    print(support_response.message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
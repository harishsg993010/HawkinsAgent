"""Example of creating a simple agent"""

from hawkins_agent import AgentBuilder
from hawkins_agent.tools import EmailTool, WebSearchTool
from hawkins_agent.mock import KnowledgeBase

async def main():
    # Create a knowledge base
    kb = KnowledgeBase()
    await kb.add_document("docs/knowledge.pdf")
    
    # Create an agent with 4-5 lines of code
    agent = (AgentBuilder("assistant")
             .with_knowledge_base(kb)
             .with_tool(EmailTool())
             .with_tool(WebSearchTool())
             .build())
    
    # Use the agent
    response = await agent.process("Can you help me find information about AI?")
    print(response.message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
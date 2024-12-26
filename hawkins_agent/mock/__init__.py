"""Mock implementations of external dependencies for development"""

class LiteLLM:
    def __init__(self, model: str):
        self.model = model

    async def generate(self, prompt: str) -> str:
        """Generate a mock response that demonstrates tool usage"""
        # GPT-4 responses are more detailed and use more tools
        if self.model == "gpt-4":
            if "latest AI trends" in prompt.lower():
                return """Based on my research capabilities, let me gather comprehensive information about AI trends.

<tool_call>
{
    "name": "WebSearchTool",
    "parameters": {
        "query": "latest developments in enterprise AI and machine learning 2024"
    }
}
</tool_call>

The search results indicate several key trends in enterprise AI:
1. Large Language Models (LLMs) becoming more accessible
2. AI-powered automation in business processes
3. Enhanced focus on AI governance and ethics

Let me check our knowledge base for additional context.

<tool_call>
{
    "name": "RAGTool",
    "parameters": {
        "query": "enterprise AI applications case studies"
    }
}
</tool_call>

This comprehensive analysis should help inform strategic decisions about AI implementation."""

        # GPT-3.5 responses are more concise and focused
        if "summary" in prompt.lower():
            return """Here's a clear summary of the AI trends:

• Growing adoption of LLMs in enterprises
• Increased focus on AI automation
• Rising importance of AI governance
• Practical applications in various sectors

Would you like more specific details about any of these points?"""

        return "I understand your request and am ready to help with your specific needs."

class Document:
    def __init__(self, content: str):
        self.content = content

class KnowledgeBase:
    async def add_document(self, path: str):
        # Mock implementation - store document path
        self.last_added = path

    async def query(self, query: str):
        if "enterprise ai" in query.lower():
            return [
                "Enterprise AI adoption increased by 150% in 2024",
                "Major companies implementing AI governance frameworks",
                "Case studies show 40% efficiency improvements with AI automation"
            ]
        return []

class HawkinDB:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.storage = {}

    async def insert(self, data: dict):
        self.storage[data.get('name', str(len(self.storage)))] = data

    async def search(self, collection: str, query: str, limit: int):
        if "ai" in query.lower():
            return [{
                "type": "memory",
                "content": "Previous discussion about AI trends in enterprise",
                "timestamp": self.now(),
                "metadata": {
                    "importance": 0.8,
                    "source": "research_agent"
                }
            }]
        return []

    async def clear(self):
        self.storage.clear()

    def now(self):
        from datetime import datetime
        return datetime.now().isoformat()
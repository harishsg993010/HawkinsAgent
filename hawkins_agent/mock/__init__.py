"""Mock implementations of external dependencies for development"""

from typing import List, Dict, Any

class LiteLLM:
    def __init__(self, model: str):
        self.model = model
        self.supports_functions = not model.startswith("anthropic/")

    async def generate(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate a mock response that demonstrates tool usage"""
        prompt = messages[-1]["content"].lower()

        # GPT-4 responses are more detailed and use more tools
        if self.model.startswith("openai/"):
            if "trends" in prompt or "developments" in prompt:
                return {
                    "content": "Let me search for the latest information.\n",
                    "tool_calls": [{
                        "name": "web_search",
                        "parameters": {
                            "query": "latest AI trends and developments 2024"
                        }
                    }]
                }

            # Knowledge base query example
            if "context" in prompt or "previous" in prompt:
                return {
                    "content": "Let me check our knowledge base.\n",
                    "tool_calls": [{
                        "name": "RAGTool",
                        "parameters": {
                            "query": "AI trends and developments"
                        }
                    }]
                }

        # Anthropic models use text-based tool calls
        elif self.model.startswith("anthropic/"):
            if "trends" in prompt or "developments" in prompt:
                return {
                    "content": """Let me search for the latest information.

<tool_call>
{"name": "web_search", "parameters": {"query": "latest AI trends and developments 2024"}}
</tool_call>

Based on the search results:
1. Large Language Models are becoming more accessible
2. Focus on AI governance and ethics
3. Increased enterprise adoption"""
                }

            if "context" in prompt or "previous" in prompt:
                return {
                    "content": """I'll check our knowledge base for relevant information.

<tool_call>
{"name": "RAGTool", "parameters": {"query": "AI trends and developments"}}
</tool_call>

The knowledge base shows several key developments in AI technology."""
                }

        # Default response for other cases
        return {
            "content": "I understand your request and will help you with that. What specific information would you like to know?"
        }

class Document:
    """Mock document class for development"""
    def __init__(self, content: str):
        """Initialize document with content

        Args:
            content: The document content
        """
        self.content = content

class KnowledgeBase:
    """Mock knowledge base for development"""
    def __init__(self):
        """Initialize the knowledge base"""
        self.documents = []

    async def add_document(self, document: Document):
        """Add a document to the knowledge base

        Args:
            document: Document object to add
        """
        self.documents.append(document)

    async def query(self, query: str) -> list[str]:
        """Query the knowledge base

        Args:
            query: Query string

        Returns:
            List of relevant document contents
        """
        # Simple mock implementation - return content containing query terms
        results = []
        query_terms = query.lower().split()

        for doc in self.documents:
            content = doc.content.lower()
            if any(term in content for term in query_terms):
                results.append(doc.content)

        # If no exact matches, return some default insights
        if not results:
            if "enterprise" in query.lower():
                return [
                    "Enterprise AI adoption increased significantly",
                    "Major focus on AI governance frameworks",
                    "Efficiency improvements with AI automation"
                ]
            elif "ai" in query.lower():
                return [
                    "AI models becoming more sophisticated",
                    "Focus on responsible AI development",
                    "Increased adoption in various sectors"
                ]

        return results[:3]  # Limit results

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
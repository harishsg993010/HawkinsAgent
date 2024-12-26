"""Mock implementations of external dependencies for development"""

class LiteLLM:
    def __init__(self, model: str):
        self.model = model
        
    async def generate(self, prompt: str) -> str:
        return f"Mock response for prompt: {prompt}"

class Document:
    def __init__(self, content: str):
        self.content = content

class KnowledgeBase:
    async def add_document(self, path: str):
        pass
        
    async def query(self, query: str):
        return ["Mock result for query: " + query]

class HawkinDB:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        
    async def insert(self, data: dict):
        pass
        
    async def search(self, collection: str, query: str, limit: int):
        return [{"type": "mock_memory", "content": f"Mock memory for query: {query}"}]
        
    async def clear(self):
        pass
        
    def now(self):
        from datetime import datetime
        return datetime.now().isoformat()

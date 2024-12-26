# Hawkins Agent Framework API Reference

## Core Components

### AgentBuilder

The main class for creating AI agents.

```python
class AgentBuilder:
    def __init__(self, name: str)
    def with_model(self, model: str) -> AgentBuilder
    def with_provider(self, provider_class: type, **kwargs) -> AgentBuilder
    def with_tool(self, tool: BaseTool) -> AgentBuilder
    def with_knowledge_base(self, kb: Any) -> AgentBuilder
    def build(self) -> Agent
```

#### Methods

- `with_model(model: str)`: Set the LLM model
- `with_provider(provider_class: type, **kwargs)`: Set the LLM provider
- `with_tool(tool: BaseTool)`: Add a tool to the agent
- `with_knowledge_base(kb: Any)`: Set the knowledge base
- `build()`: Create the agent instance

### Agent

The main agent class that processes queries and manages tools.

```python
class Agent:
    async def process(self, query: str) -> AgentResponse
    async def execute_tool(self, tool_name: str, **params) -> ToolResponse
```

### Types

#### Message

```python
@dataclass
class Message:
    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None
```

#### AgentResponse

```python
@dataclass
class AgentResponse:
    message: str
    tool_calls: List[Dict[str, Any]]
    metadata: Dict[str, Any]
```

#### ToolResponse

```python
@dataclass
class ToolResponse:
    success: bool
    result: Any
    error: Optional[str] = None
```

## Tools

### BaseTool

Base class for all tools.

```python
class BaseTool:
    def __init__(self, name: str)
    
    @property
    def description(self) -> str
    
    def validate_params(self, params: Dict[str, Any]) -> bool
    
    async def execute(self, **kwargs) -> ToolResponse
```

### Built-in Tools

#### WebSearchTool

```python
class WebSearchTool(BaseTool):
    def __init__(self, api_key: str)
```

#### EmailTool

```python
class EmailTool(BaseTool):
    def __init__(self, smtp_config: Dict[str, Any])
```

#### WeatherTool

```python
class WeatherTool(BaseTool):
    def __init__(self, api_key: Optional[str] = None)
```

#### RAGTool

```python
class RAGTool(BaseTool):
    def __init__(self, knowledge_base: Any)
```

## LLM Integration

### LLMManager

Manages LLM interactions and providers.

```python
class LLMManager:
    def __init__(self, model: str = "gpt-4o",
                provider_class: Optional[type] = None,
                **kwargs)
    
    async def generate_response(self,
                            messages: List[Message],
                            tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]
```

### LiteLLMProvider

Default LLM provider implementation.

```python
class LiteLLMProvider:
    def __init__(self, model: str, **kwargs)
    
    async def generate(self,
                    messages: List[Message],
                    tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]
```

## Multi-Agent Flows

### FlowManager

Manages multi-agent workflows.

```python
class FlowManager:
    def add_step(self, step: FlowStep)
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]
```

### FlowStep

Represents a step in a multi-agent workflow.

```python
class FlowStep:
    def __init__(self,
                name: str,
                agent: Optional[Agent],
                process: Callable,
                requires: Optional[List[str]] = None)
```

## Environment Variables

Required environment variables for various features:

```python
# Core
OPENAI_API_KEY: str  # OpenAI API key for LLM integration

# Tool-specific
TAVILY_API_KEY: str      # For WebSearchTool
OPENWEATHERMAP_API_KEY: str  # For WeatherTool

# Optional
OPENAI_BASE_URL: str     # Custom OpenAI API endpoint
```

## Error Handling

Common exceptions and their meanings:

```python
class ToolExecutionError(Exception):
    """Raised when a tool execution fails"""

class InvalidParameterError(Exception):
    """Raised when invalid parameters are provided"""

class LLMError(Exception):
    """Raised when LLM interaction fails"""
```

## Logging

The framework uses Python's standard logging module:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Configuration

Example configuration structure:

```python
config = {
    "model": "openai/gpt-4o",
    "temperature": 0.7,
    "max_tokens": 1000,
    "tools": {
        "web_search": {
            "api_key": "your-api-key"
        },
        "weather": {
            "api_key": "your-api-key"
        }
    }
}
```

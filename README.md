# Hawkins Agent Framework

A Python SDK for building AI agents with minimal code using the Hawkins ecosystem. This framework integrates key tools and services for building functional AI agents.

![Version](https://img.shields.io/pypi/v/hawkins-agent)
![Python](https://img.shields.io/pypi/pyversions/hawkins-agent)
![License](https://img.shields.io/pypi/l/hawkins-agent)

## Features

- **Seamless LLM Integration**: Built-in support for LiteLLM, enabling easy integration with various language models
- **Web Search Capabilities**: Integrated Tavily search functionality for real-time information retrieval
- **Memory Management**: HawkinDB integration for efficient agent memory storage and retrieval
- **Multi-Agent Orchestration**: Advanced flow control system for coordinating multiple agents
- **Tool Integration**: Extensible tool system with pre-built tools for common tasks
- **Email Functionality**: Built-in email capabilities for agent communication
- **Asynchronous Design**: Built with modern async/await patterns for optimal performance

## Installation

```bash
pip install hawkins-agent
```

Requires Python 3.11 or higher.

## Quick Start

Here's a simple example to get you started:

```python
from hawkins_agent import AgentBuilder
from hawkins_agent.tools import WebSearchTool
from hawkins_agent.mock import KnowledgeBase

 search_tool = WebSearchTool(api_key=os.environ.get("TAVILY_API_KEY"))

async def main():
    # Create a knowledge base
    kb = KnowledgeBase()
    
    # Create agent with web search capabilities
    agent = (AgentBuilder("researcher")
            .with_model("gpt-4o")
            .with_knowledge_base(kb)
            .with_tool(search_tool)
            .build())
    
    # Process a query
    response = await agent.process("What are the latest developments in AI?")
    print(response.message)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## Advanced Usage

### Multi-Agent Workflow

Create complex workflows with multiple specialized agents:

```python
from hawkins_agent import AgentBuilder, FlowManager, FlowStep
from hawkins_agent.tools import WebSearchTool, WeatherTool

# Create specialized agents
research_agent = (AgentBuilder("researcher")
                .with_model("gpt-4o")
                .with_tool(WebSearchTool())
                .build())

writer_agent = (AgentBuilder("writer")
              .with_model("gpt-4o")
              .build())

# Create flow manager
flow = FlowManager()

# Define workflow steps
async def research_step(input_data, context):
    query = input_data.get("topic")
    result = await research_agent.process(f"Research this topic: {query}")
    return {"research": result.message}

async def writing_step(input_data, context):
    research = context.get("research", {}).get("research")
    result = await writer_agent.process(f"Write an article based on: {research}")
    return {"article": result.message}

# Add steps to flow
flow.add_step(FlowStep(
    name="research",
    agent=research_agent,
    process=research_step
))

flow.add_step(FlowStep(
    name="writing",
    agent=writer_agent,
    process=writing_step,
    requires=["research"]
))

# Execute flow
results = await flow.execute({"topic": "AI trends in 2024"})
```

### Using Custom Tools

Create your own tools by extending the BaseTool class:

```python
from hawkins_agent.tools.base import BaseTool
from hawkins_agent.types import ToolResponse

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "A custom tool for specific tasks"
    
    async def execute(self, query: str) -> ToolResponse:
        try:
            # Tool implementation here
            result = await self._process(query)
            return ToolResponse(success=True, result=result)
        except Exception as e:
            return ToolResponse(success=False, error=str(e))
```

## Documentation

For more detailed documentation, see:
- [Flow System Documentation](docs/flows.md)
- [Custom Tools Guide](docs/custom_tools.md)
- [Memory Management](docs/memory_management.md)
- [API Reference](docs/api_reference.md)

## Examples

The `examples/` directory contains several example implementations:
- `simple_agent.py`: Basic agent usage
- `multi_agent_flow.py`: Complex multi-agent workflow
- `tool_test.py`: Tool integration examples
- `blog_writer_flow.py`: Content generation workflow
- `maldives_trip_planner.py`: Travel planning agent system

## Development

To contribute to the project:

1. Clone the repository
2. Install development dependencies:
```bash
pip install -e .[dev]
```
3. Run tests:
```bash
pytest
```

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Built with ❤️ by the Harish and AI Agents

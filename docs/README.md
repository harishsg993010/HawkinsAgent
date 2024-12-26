# Hawkins AI Agent Framework

Hawkins is a Python framework for building AI agents with minimal code. It provides a flexible architecture for creating, customizing, and orchestrating AI agents that can leverage various tools and services.

## Key Features

- **Easy Agent Creation**: Build AI agents with a fluent builder interface
- **Tool Integration**: Pre-built tools for web search, email, weather data, and more
- **LLM Support**: Seamless integration with language models via LiteLLM
- **Multi-Agent Workflows**: Create complex workflows with multiple specialized agents
- **Extensible Architecture**: Easy to add custom tools and capabilities

## Quick Start

```python
from hawkins_agent import AgentBuilder
from hawkins_agent.tools import WebSearchTool

# Create an agent with web search capability
agent = (AgentBuilder("assistant")
        .with_model("openai/gpt-4o")
        .with_tool(WebSearchTool(api_key="your-api-key"))
        .build())

# Process a query
response = await agent.process("What are the latest AI developments?")
```

## Installation

```bash
pip install hawkins-agent
```

## Core Components

1. **AgentBuilder**: Main interface for creating agents
2. **Tools**: Built-in and custom tools for various capabilities
3. **LLM Integration**: Support for various language models
4. **Multi-Agent Flows**: Orchestrate multiple agents in workflows

## Environment Setup

Required environment variables:
- `OPENAI_API_KEY`: For LLM integration
- Other API keys based on tools used (e.g., `TAVILY_API_KEY` for web search)

## Examples

See the `examples/` directory for complete examples including:
- Simple agent usage
- Multi-agent workflows
- Custom tool integration
- Trip planning systems

## Documentation

- [Custom Tools Guide](custom_tools.md) - Create your own agent tools
- [API Reference](api_reference.md) - Detailed API documentation
- [Examples](../examples/) - Example implementations

## Contributing

Contributions are welcome! See our contributing guidelines for more information.

## License

[License details]

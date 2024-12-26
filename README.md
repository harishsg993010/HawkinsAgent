# Hawkins Agent Framework

A Python SDK for building AI agents with minimal code using the Hawkins ecosystem. This framework integrates key tools and services for building functional AI agents.

## Features

- **LiteLLM Integration**: Seamless support for multiple language models
- **Built-in Tools**:
  - Web Search capabilities using Tavily
  - Email functionality
  - Weather information
  - RAG (Retrieval-Augmented Generation)
  - Code interpretation
  - Text summarization
- **Memory Management**: Persistent memory system using HawkinDB
- **Multi-Agent Support**: Create and orchestrate multiple agents
- **Extensible Architecture**: Easy to add custom tools and capabilities

## Installation

```bash
pip install hawkins-agent
```

## Quick Start

```python
from hawkins_agent import AgentBuilder
from hawkins_agent.tools import WebSearchTool, RAGTool

# Create an agent with tools
agent = (AgentBuilder("research_assistant")
        .with_model("gpt-4o")
        .with_tool(WebSearchTool())
        .with_tool(RAGTool())
        .build())

# Process a query
response = await agent.process("Research the latest developments in AI")
print(response.message)
```

## Documentation

For detailed documentation, please visit:
- [API Reference](docs/api_reference.md)
- [Custom Tools Guide](docs/custom_tools.md)
- [Memory Management](docs/memory_management.md)

## Example Use Cases

- Research assistance
- Content generation
- Data analysis
- Task automation
- Multi-agent workflows

## Requirements

- Python 3.11 or higher
- Dependencies are automatically installed with the package

## License

MIT License

## Contributing

Contributions are welcome! Please check our contribution guidelines for more details.

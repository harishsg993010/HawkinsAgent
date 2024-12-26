# Memory Management in Hawkins AI Framework

The Hawkins AI Framework uses HawkinsDB for persistent memory management, allowing agents to maintain context and learn from past interactions. This document explains the memory system architecture and usage.

## Overview

HawkinsDB provides a SQLite-based storage system for maintaining agent memory across sessions. The memory system enables:
- Storage of past interactions
- Context retention
- Pattern recognition across conversations
- Long-term learning capabilities

## Memory Architecture

### Core Components

1. **Memory Storage**
```python
from hawkinsdb import HawkinDB

db = HawkinDB(
    storage_type="sqlite",
    db_path="hawkins_memory.db"
)
```

2. **Memory Types**
- Short-term memory (conversation context)
- Long-term memory (learned patterns)
- Episodic memory (specific interaction records)

## Using Memory in Agents

### Basic Memory Integration

```python
from hawkins_agent import AgentBuilder
from hawkinsdb import HawkinDB

# Initialize memory
memory_db = HawkinDB()

# Create agent with memory
agent = (AgentBuilder("assistant")
        .with_model("gpt-4o")
        .with_memory(memory_db)
        .build())
```

### Memory Operations

1. **Storing Interactions**
```python
# Automatically handled during agent.process()
response = await agent.process("What's the weather?")
# Interaction stored in memory with metadata
```

2. **Retrieving Context**
```python
# Recent interactions are automatically included in context
previous_interactions = await agent.memory.get_recent(limit=5)
```

3. **Memory Configuration**
```python
# Configure memory retention
agent = (AgentBuilder("assistant")
        .with_memory({
            "retention_days": 7,  # Keep memory for 7 days
            "max_entries": 1000   # Maximum memory entries
        })
        .build())
```

## Memory Search and Retrieval

The framework provides several ways to search and utilize stored memories:

### Semantic Search
```python
# Search for semantically similar interactions
similar_memories = await agent.memory.search(
    "weather forecast",
    limit=5
)
```

### Temporal Search
```python
# Get memories from a specific timeframe
recent_memories = await agent.memory.get_range(
    start_date="2024-01-01",
    end_date="2024-01-07"
)
```

## Memory Schemas

HawkinsDB uses the following schema for storing memories:

```sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    type TEXT NOT NULL,
    metadata JSON
);
```

Fields:
- `id`: Unique identifier for the memory
- `content`: The actual content of the interaction
- `timestamp`: When the memory was created
- `type`: Type of memory (conversation, learning, etc.)
- `metadata`: Additional structured data about the memory

## Example: Advanced Memory Usage

```python
from hawkins_agent import AgentBuilder
from hawkins_agent.tools import WebSearchTool
from hawkinsdb import HawkinDB

# Initialize memory with custom configuration
memory_db = HawkinDB(
    storage_type="sqlite",
    db_path="hawkins_memory.db",
    config={
        "retention_days": 30,
        "max_entries": 5000,
        "index_type": "semantic"  # Enable semantic search
    }
)

# Create agent with memory and tools
agent = (AgentBuilder("research_assistant")
        .with_model("gpt-4o")
        .with_memory(memory_db)
        .with_tool(WebSearchTool())
        .build())

# Memory will automatically store:
# - User queries
# - Agent responses
# - Tool usage and results
# - Context and metadata
```

## Best Practices

1. **Memory Maintenance**
   - Regularly clean up old memories using retention policies
   - Index frequently accessed memories for faster retrieval
   - Monitor memory storage size

2. **Context Management**
   - Use relevant memory retrieval for maintaining conversation context
   - Balance between too little and too much context
   - Prioritize recent and relevant memories

3. **Performance Optimization**
   - Use appropriate indexing strategies
   - Implement caching for frequently accessed memories
   - Configure retention policies based on use case

## Memory Limitations

1. **Storage Limits**
   - Default SQLite database size limits apply
   - Consider cleanup strategies for long-running agents

2. **Search Performance**
   - Large memory stores may impact search performance
   - Use appropriate indexing and limiting in queries

3. **Context Windows**
   - LLM token limits affect how much memory can be included in context
   - Implement smart context selection strategies

## Security Considerations

1. **Data Privacy**
   - Memory stores may contain sensitive information
   - Implement appropriate access controls
   - Consider data encryption for sensitive memories

2. **Data Retention**
   - Follow data retention policies
   - Implement secure deletion mechanisms
   - Handle user data according to privacy requirements

# Creating Custom Tools for Hawkins Agents

This guide explains how to create custom tools for your Hawkins agents. Custom tools allow you to extend agent capabilities with your own functionality.

## Tool Architecture

Tools in Hawkins follow a simple but powerful architecture:

1. Inherit from `BaseTool`
2. Implement required methods
3. Register with an agent

## Basic Structure

```python
from typing import Dict, Any
from hawkins_agent.tools import BaseTool
from hawkins_agent.types import ToolResponse

class CustomTool(BaseTool):
    """Your custom tool implementation"""
    
    def __init__(self):
        """Initialize your tool"""
        super().__init__(name="custom_tool_name")
        
    @property
    def description(self) -> str:
        """Tool description used by the agent"""
        return "Description of what your tool does"
        
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        return True
        
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute the tool's functionality"""
        try:
            # Your tool logic here
            result = "Tool execution result"
            return ToolResponse(
                success=True,
                result=result,
                error=None
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                result=None,
                error=str(e)
            )
```

## Step-by-Step Guide

### 1. Create Tool Class

Create a new class inheriting from `BaseTool`:

```python
from hawkins_agent.tools import BaseTool

class WeatherTool(BaseTool):
    def __init__(self, api_key: str):
        super().__init__(name="weather")
        self.api_key = api_key
```

### 2. Add Description

Implement the `description` property:

```python
@property
def description(self) -> str:
    return "Get weather information for a specified location"
```

### 3. Implement Parameter Validation

Add validation logic:

```python
def validate_params(self, params: Dict[str, Any]) -> bool:
    if 'query' not in params:
        return False
    if not isinstance(params['query'], str):
        return False
    return True
```

### 4. Implement Execute Method

Add the main tool functionality:

```python
async def execute(self, **kwargs) -> ToolResponse:
    try:
        query = kwargs.get('query', '')
        # Your tool logic here
        result = await self._fetch_weather(query)
        return ToolResponse(
            success=True,
            result=result,
            error=None
        )
    except Exception as e:
        return ToolResponse(
            success=False,
            result=None,
            error=str(e)
        )
```

## Using Custom Tools

Register your tool with an agent:

```python
from hawkins_agent import AgentBuilder

# Create your custom tool
custom_tool = CustomTool()

# Add to agent
agent = (AgentBuilder("assistant")
        .with_model("openai/gpt-4o")
        .with_tool(custom_tool)
        .build())
```

## Best Practices

1. **Error Handling**
   - Always use try-catch blocks
   - Return clear error messages
   - Log errors appropriately

2. **Parameter Validation**
   - Validate all required parameters
   - Check parameter types
   - Provide clear validation feedback

3. **Documentation**
   - Add docstrings to your tool class
   - Document parameters and return values
   - Include usage examples

4. **Async Support**
   - Use async/await for I/O operations
   - Handle async errors appropriately
   - Don't block the event loop

## Example: Custom Database Tool

Here's a complete example of a custom database query tool:

```python
from hawkins_agent.tools import BaseTool
from hawkins_agent.types import ToolResponse
import asyncpg

class DatabaseTool(BaseTool):
    """Tool for executing database queries"""
    
    def __init__(self, connection_string: str):
        super().__init__(name="database")
        self.conn_string = connection_string
        
    @property
    def description(self) -> str:
        return "Execute database queries and return results"
        
    def validate_params(self, params: Dict[str, Any]) -> bool:
        if 'query' not in params:
            return False
        if not isinstance(params['query'], str):
            return False
        return True
        
    async def execute(self, **kwargs) -> ToolResponse:
        try:
            query = kwargs.get('query', '')
            conn = await asyncpg.connect(self.conn_string)
            result = await conn.fetch(query)
            await conn.close()
            
            return ToolResponse(
                success=True,
                result=result,
                error=None
            )
        except Exception as e:
            return ToolResponse(
                success=False,
                result=None,
                error=str(e)
            )
```

## Testing Custom Tools

Always test your tools thoroughly:

```python
async def test_custom_tool():
    tool = CustomTool()
    response = await tool.execute(query="test input")
    assert response.success
    assert response.result is not None
```

## Common Patterns

1. **API Integration**
   - Handle API authentication
   - Implement rate limiting
   - Cache responses when appropriate

2. **Resource Management**
   - Clean up resources in try-finally blocks
   - Use context managers
   - Handle connection pooling

3. **Input Processing**
   - Sanitize inputs
   - Convert data types
   - Handle missing parameters

## Troubleshooting

Common issues and solutions:

1. **Tool Not Recognized**
   - Check tool name registration
   - Verify tool is properly added to agent

2. **Execution Errors**
   - Check parameter validation
   - Verify async/await usage
   - Review error handling

3. **Performance Issues**
   - Implement caching
   - Use connection pooling
   - Optimize resource usage

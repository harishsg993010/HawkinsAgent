# Flow System in Hawkins Agent Framework

The Flow system in Hawkins Agent Framework enables orchestration of complex multi-agent workflows. This guide explains how to create, manage, and optimize flows in your applications.

## Overview

Flows allow you to:
- Chain multiple agents together
- Coordinate complex tasks
- Share context between agents
- Handle dependencies between steps
- Manage state across the workflow

## Architecture

### Core Components

1. **FlowManager**
```python
class FlowManager:
    def add_step(self, step: FlowStep)
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]
```

2. **FlowStep**
```python
class FlowStep:
    def __init__(self,
                name: str,
                agent: Optional[Agent],
                process: Callable,
                requires: Optional[List[str]] = None)
```

## Creating Flows

### Basic Flow Example

```python
from hawkins_agent import AgentBuilder, FlowManager, FlowStep

# Create agents
research_agent = (AgentBuilder("researcher")
                .with_model("gpt-4o")
                .with_tool(WebSearchTool())
                .build())

writer_agent = (AgentBuilder("writer")
              .with_model("gpt-4o")
              .build())

# Create flow manager
flow = FlowManager()

# Define steps
async def research_step(input_data: Dict[str, Any], context: Dict[str, Any]):
    query = input_data.get("topic")
    result = await research_agent.process(f"Research this topic: {query}")
    return {"research": result.message}

async def writing_step(input_data: Dict[str, Any], context: Dict[str, Any]):
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
    requires=["research"]  # This step requires research to complete first
))

# Execute flow
results = await flow.execute({"topic": "AI trends in 2024"})
```

## Advanced Features

### 1. Parallel Execution

Steps without dependencies can run in parallel:

```python
# These steps will run concurrently
flow.add_step(FlowStep("market_research", market_agent, market_research))
flow.add_step(FlowStep("competitor_analysis", analysis_agent, analyze_competitors))

# This step waits for both above steps
flow.add_step(FlowStep(
    "strategy",
    strategy_agent,
    create_strategy,
    requires=["market_research", "competitor_analysis"]
))
```

### 2. Error Handling

```python
async def safe_step(input_data, context):
    try:
        result = await process_data(input_data)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

flow.add_step(FlowStep(
    "safe_operation",
    agent,
    safe_step,
    error_handler=handle_step_error
))
```

### 3. Context Sharing

```python
async def step_with_context(input_data, context):
    # Access results from previous steps
    previous_result = context.get("previous_step", {}).get("data")
    
    # Process with context
    result = await process_with_context(previous_result)
    
    return {"data": result}
```

## Best Practices

1. **Step Design**
   - Keep steps focused and single-purpose
   - Use clear, descriptive step names
   - Document dependencies explicitly
   - Handle errors gracefully

2. **Flow Structure**
   - Organize steps logically
   - Minimize dependencies where possible
   - Consider parallel execution opportunities
   - Use meaningful step names

3. **Context Management**
   - Pass only necessary data between steps
   - Clean up temporary data after use
   - Document context requirements
   - Handle missing context gracefully

4. **Error Handling**
   - Implement error handlers for critical steps
   - Log errors appropriately
   - Provide meaningful error messages
   - Consider recovery strategies

## Example: Document Processing Flow

```python
from hawkins_agent import AgentBuilder, FlowManager, FlowStep
from hawkins_agent.tools import RAGTool, SummarizationTool

async def extract_text(input_data, context):
    document = input_data["document"]
    text = await document_processor.extract_text(document)
    return {"text": text}

async def summarize_content(input_data, context):
    text = context["extract"]["text"]
    summary = await summarizer_agent.process(f"Summarize: {text}")
    return {"summary": summary.message}

async def generate_insights(input_data, context):
    summary = context["summarize"]["summary"]
    insights = await analyst_agent.process(f"Generate insights from: {summary}")
    return {"insights": insights.message}

# Create flow
doc_flow = FlowManager()

# Add steps
doc_flow.add_step(FlowStep("extract", None, extract_text))
doc_flow.add_step(FlowStep("summarize", summarizer_agent, summarize_content, ["extract"]))
doc_flow.add_step(FlowStep("analyze", analyst_agent, generate_insights, ["summarize"]))

# Execute
results = await doc_flow.execute({"document": document_path})
```

## Performance Considerations

1. **Memory Usage**
   - Monitor context size
   - Clean up large objects after use
   - Use streaming for large data

2. **Execution Time**
   - Optimize step order
   - Use parallel execution
   - Implement timeouts
   - Cache repeated operations

3. **Resource Management**
   - Close connections properly
   - Release resources after use
   - Implement proper cleanup

## Debugging Flows

1. **Logging**
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_step(input_data, context):
    logger.info(f"Starting step with input: {input_data}")
    try:
        result = await process_data(input_data)
        logger.info(f"Step completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Step failed: {e}")
        raise
```

2. **Step Visualization**
```python
def visualize_flow(flow: FlowManager):
    """Generate a visualization of the flow structure"""
    steps = flow.get_steps()
    for step in steps:
        print(f"Step: {step.name}")
        print(f"Dependencies: {step.requires or []}")
        print("---")
```

## Limitations and Considerations

1. **Memory Constraints**
   - Large context objects can impact performance
   - Consider implementing cleanup strategies

2. **Error Propagation**
   - Failed steps can affect dependent steps
   - Implement appropriate fallback mechanisms

3. **Scalability**
   - Complex flows may require additional monitoring
   - Consider breaking large flows into smaller sub-flows

4. **Testing**
   - Test steps individually
   - Validate flow execution paths
   - Mock long-running operations
   - Test error scenarios

## Conclusion

The Flow system in Hawkins Agent Framework provides a powerful way to orchestrate complex multi-agent workflows. By following these guidelines and best practices, you can create robust and efficient flows that handle complex tasks while maintaining code quality and performance.

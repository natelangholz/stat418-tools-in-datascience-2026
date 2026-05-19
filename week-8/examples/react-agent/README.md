# Simple ReAct Agent

A basic implementation of the ReAct (Reasoning + Acting) agent architecture.

## Overview

This example demonstrates:
- Basic ReAct loop implementation
- Tool calling with function schemas
- Reasoning and action steps
- Error handling and retries
- Testing agent behavior

## Files

- `agent.py` - Main ReAct agent implementation
- `tools.py` - Tool definitions and implementations
- `test_agent.py` - Unit tests for the agent
- `requirements.txt` - Python dependencies

## Setup

```bash
# Install dependencies
uv pip install -r requirements.txt

# Set your API key (use free tier)
export GOOGLE_API_KEY="your-free-gemini-key"
# OR
export OPENROUTER_API_KEY="your-free-openrouter-key"
```

**Note**: This example uses free-tier APIs from Google (Gemini) or OpenRouter. The code examples show the pattern - adapt for your chosen provider.

## Usage

```bash
# Run the agent
python agent.py

# Run tests
pytest test_agent.py
```

## Example Interaction

```
User: What's the weather in San Francisco and should I bring an umbrella?

Thought: I need to get the weather for San Francisco
Action: get_weather(location="San Francisco")
Observation: {"temp": 65, "conditions": "partly cloudy", "precipitation": 20}

Thought: The precipitation chance is 20%, which is relatively low
Final Answer: The weather in San Francisco is 65°F and partly cloudy with a 20% 
chance of rain. You probably don't need an umbrella, but you might want to bring 
a light jacket.
```

## Key Concepts

### ReAct Loop

The agent follows this pattern:
1. **Thought**: Reason about what to do next
2. **Action**: Call a tool
3. **Observation**: See the result
4. **Repeat** until ready to answer
5. **Final Answer**: Provide the response

### Tool Definitions

Tools are defined with JSON schemas:

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"}
            },
            "required": ["location"]
        }
    }
]
```

### Error Handling

The agent implements retry logic for failed tool calls:

```python
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def call_tool(tool_name: str, args: dict):
    # Tool execution with automatic retries
    pass
```

## Extending the Agent

Add new tools by:
1. Defining the tool schema in `tools.py`
2. Implementing the tool function
3. Registering it with the agent

Example:

```python
def search_database(query: str) -> list:
    """Search the database for items matching query"""
    # Implementation here
    pass

# Add to tools list
tools.append({
    "name": "search_database",
    "description": "Search the product database",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        }
    }
})
```

## Testing

The example includes comprehensive tests:

```python
def test_agent_basic_task():
    """Test agent can complete a simple task"""
    agent = ReActAgent(tools=mock_tools)
    result = agent.run("What's the weather?")
    assert "weather" in result.lower()

def test_agent_error_handling():
    """Test agent handles tool failures gracefully"""
    agent = ReActAgent(tools=failing_tools)
    result = agent.run("Get weather")
    assert agent.retry_count > 0
```

## Common Issues

**Agent loops infinitely**: Set `max_turns` parameter
**Tool calls fail**: Check tool schemas match implementation
**High costs**: Reduce `max_turns` or use cheaper model for tool selection

## Next Steps

- Add more tools for your use case
- Implement agent memory for context
- Add logging and monitoring
- Deploy as an API endpoint
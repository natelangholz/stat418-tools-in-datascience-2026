# MCP-Powered Agent

An AI agent that connects to MCP (Model Context Protocol) servers to dynamically discover and use tools.

## Overview

This example demonstrates:
- Connecting to MCP servers
- Dynamic tool discovery
- Using multiple MCP tools
- Handling tool responses
- Integration with Claude Desktop

## Files

- `mcp_agent.py` - Agent with MCP integration
- `mcp_server.py` - Example MCP server implementation
- `config.json` - MCP server configuration
- `requirements.txt` - Python dependencies

## Setup

```bash
# Install dependencies
uv pip install google-generativeai mcp
# OR
uv pip install openai mcp  # for OpenRouter

# Set your API key (use free tier)
export GOOGLE_API_KEY="your-free-gemini-key"
# OR
export OPENROUTER_API_KEY="your-free-openrouter-key"
```

**Note**: This example uses free-tier APIs from Google (Gemini) or OpenRouter. MCP works with any LLM provider.

## Running the MCP Server

```bash
# Start the MCP server
python mcp_server.py
```

The server exposes these tools:
- `search_database` - Search a product database
- `get_user_info` - Get user information
- `send_notification` - Send notifications

## Running the Agent

```bash
# Run the agent (connects to MCP server)
python mcp_agent.py
```

## Claude Desktop Integration

To use this MCP server with Claude Desktop:

1. Edit Claude Desktop config:
```bash
# macOS
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows
notepad %APPDATA%\Claude\claude_desktop_config.json
```

2. Add your MCP server:
```json
{
  "mcpServers": {
    "my-tools": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "env": {
        "DATABASE_URL": "sqlite:///data.db"
      }
    }
  }
}
```

3. Restart Claude Desktop

4. Tools will be automatically available in conversations

## MCP Server Implementation

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("my-tools")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_database",
            description="Search the product database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search_database":
        results = await search_db(arguments["query"], arguments.get("limit", 10))
        return [TextContent(type="text", text=json.dumps(results))]
    
    raise ValueError(f"Unknown tool: {name}")
```

## Agent Implementation

```python
import anthropic
from mcp.client import Client

# Connect to MCP server
mcp_client = Client("http://localhost:8000")

# Discover available tools
tools = await mcp_client.list_tools()

# Create agent with MCP tools
client = anthropic.Anthropic()

def run_agent(task: str):
    messages = [{"role": "user", "content": task}]
    
    while True:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        
        if response.stop_reason == "end_turn":
            return response.content[0].text
        
        # Execute MCP tool calls
        for tool_use in response.content:
            if tool_use.type == "tool_use":
                result = await mcp_client.call_tool(
                    tool_use.name,
                    tool_use.input
                )
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": result
                    }]
                })
```

## Key Concepts

### Tool Discovery

MCP servers expose their tools through a standard interface:

```python
# Agent automatically discovers tools
tools = await mcp_client.list_tools()

# Tools include name, description, and schema
for tool in tools:
    print(f"{tool.name}: {tool.description}")
```

### Tool Execution

The agent calls tools through the MCP protocol:

```python
# Agent decides to use a tool
result = await mcp_client.call_tool(
    name="search_database",
    arguments={"query": "laptop", "limit": 5}
)

# Result is returned to the agent
```

### Error Handling

Handle MCP connection and tool errors:

```python
try:
    result = await mcp_client.call_tool(name, args)
except MCPConnectionError:
    # MCP server is down
    logger.error("MCP server unavailable")
except MCPToolError as e:
    # Tool execution failed
    logger.error(f"Tool failed: {e}")
```

## Multiple MCP Servers

Connect to multiple MCP servers:

```python
# Connect to multiple servers
database_tools = await Client("http://localhost:8000").list_tools()
api_tools = await Client("http://localhost:8001").list_tools()

# Combine tools
all_tools = database_tools + api_tools

# Agent can use tools from all servers
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    tools=all_tools,
    messages=messages
)
```

## Security Considerations

- **Authentication**: Use API keys for MCP servers
- **Authorization**: Validate tool access per user
- **Input validation**: Sanitize all tool inputs
- **Rate limiting**: Prevent abuse of MCP tools
- **Logging**: Log all tool calls for audit

## Testing

Test MCP integration:

```python
def test_mcp_connection():
    """Test connection to MCP server"""
    client = Client("http://localhost:8000")
    tools = await client.list_tools()
    assert len(tools) > 0

def test_tool_execution():
    """Test tool execution through MCP"""
    client = Client("http://localhost:8000")
    result = await client.call_tool("search_database", {"query": "test"})
    assert result is not None
```

## Common Issues

**MCP server not found**: Check server is running and URL is correct
**Tool not available**: Verify tool is registered in MCP server
**Authentication failed**: Check API keys and credentials
**Timeout errors**: Increase timeout or optimize tool execution

## Next Steps

- Add authentication to your MCP server
- Implement more complex tools
- Deploy MCP server to production
- Monitor tool usage and performance
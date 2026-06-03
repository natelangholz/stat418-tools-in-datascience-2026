# MCP-Powered Agent

A runnable example of an LLM agent using a real FastMCP server, the Python MCP client library, and OpenRouter tool-calling.

## Overview

This example demonstrates:
- defining tools with FastMCP
- exposing those tools through a real MCP server over stdio
- discovering tools dynamically with the Python `mcp` client library
- using OpenRouter with the NVIDIA Nemotron free model by default
- combining local tools and external APIs in an MCP workflow
- interactive CLI usage for demos and experimentation
- a persistent MCP session in interactive mode
- verbose trace output showing the MCP tool calls made by the agent

## Files

- `mcp_server.py` - FastMCP server that exposes demo tools
- `mcp_agent.py` - LLM-driven MCP client agent using `ClientSession`
- `llm_client.py` - OpenRouter chat completion helper
- `config.json` - example MCP client configuration
- `requirements.txt` - Python dependencies

## Setup

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

Set your OpenRouter API key before running the agent:

```bash
export OPENROUTER_API_KEY=your_key_here
```

Optional model override:

```bash
export OPENROUTER_MODEL=nvidia/nemotron-3-super-120b-a12b:free
```

If you do not set `OPENROUTER_MODEL`, the code already defaults to the NVIDIA Nemotron model above.

## Running the MCP Server

You can run the FastMCP server directly:

```bash
python mcp_server.py
```

The server exposes these tools:
- `search_database`
- `get_user_info`
- `get_weather`
- `send_notification`

## Running the Agent

The agent launches the MCP server over stdio, initializes an MCP session, discovers the available tools, and lets the LLM decide when to call them.

Behavior differs slightly by mode:
- one-shot mode starts a temporary MCP server/session, runs the request, and exits
- interactive mode starts one MCP server/session and keeps it alive across turns
- interactive mode also preserves conversation context until you type `clear`

```bash
# Run the default demo task
python mcp_agent.py

# Run a one-off custom task
python mcp_agent.py --task "Look up alice, check the weather in her city, and send her a short notification."

# Show the MCP tool trace
python mcp_agent.py --task "Look up bob and summarize his account." --verbose

# Start an interactive CLI loop with one persistent MCP session
python mcp_agent.py --interactive

# Interactive mode with verbose MCP tool traces
python mcp_agent.py --interactive --verbose
```

The default task:
- looks up `alice`
- summarizes her account
- sends a notification

## Example Interaction

### One-shot run

```text
$ python mcp_agent.py --task "Look up alice, check the weather in her city, and send her a short notification." --verbose

Tool: get_user_info
Arguments: {"username": "alice"}
Result: {"name": "Alice", "plan": "premium", "email": "alice@example.com", "city": "Los Angeles"}

Tool: get_weather
Arguments: {"city": "Los Angeles"}
Result: {"city": "Los Angeles", "temperature_f": 68.2, "wind_speed_mph": 6.4, "conditions": "mainly clear"}

Tool: send_notification
Arguments: {"username": "alice", "message": "Hi Alice, it's currently mainly clear and 68.2°F in Los Angeles."}
Result: {"status": "sent", "username": "alice", "message": "Hi Alice, it's currently mainly clear and 68.2°F in Los Angeles.", "delivery_target": "alice@example.com"}

Final Answer: I looked up Alice, checked the current weather in Los Angeles, and sent her a short notification with the update.
```

### Interactive mode

```text
$ python mcp_agent.py --interactive
MCP agent interactive mode. Type 'exit' or 'quit' to stop. Type 'clear' to reset context.

Task> look up bob and summarize his account
Final Answer: Bob is a free-tier user based in San Francisco.

Task> check the weather in his city too
Final Answer: San Francisco is currently cool with light wind.

Task> clear
Context cleared.

Task> check the weather in his city too
Final Answer: I need to know which person you mean before I can check the weather in their city.

Task> quit
Exiting.
```

## Config File

`config.json` shows the same server registration pattern many MCP hosts use:

```json
{
  "mcpServers": {
    "demo-tools": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "."
    }
  }
}
```

## FastMCP Server Design

The server uses the `@mcp.tool` decorator to publish discoverable tool interfaces:

```python
from fastmcp import FastMCP

mcp = FastMCP("demo-tools")

@mcp.tool
def get_user_info(username: str) -> dict:
    ...
```

The tool layer includes:
- a small in-memory product database
- demo user account data
- live weather lookup through Open-Meteo
- a notification action that returns structured delivery metadata

## MCP Client Design

The agent uses the actual Python MCP client library:

- `StdioServerParameters`
- `stdio_client(...)`
- `ClientSession(...)`
- `session.initialize()`
- `session.list_tools()`
- `session.call_tool(...)`

That means the example is not pretending to be MCP-compatible. It is using the real protocol client flow.

## Why the CLI Mode Helps

The CLI makes the example easier to teach and explore because you can:
- run a single structured request with `--task`
- demonstrate actual MCP tool traffic with `--verbose`
- run multiple prompts in a row with `--interactive`
- preserve context across interactive turns
- reset the conversation deliberately with `clear`
- compare the same MCP server behavior across different user requests without editing source code

## Example Workflow

A representative multi-step request is:

```text
Look up alice, check the weather in her city, and send her a short notification.
```

A typical execution path is:
1. the LLM sees the available MCP tool schemas
2. it calls `get_user_info`
3. it calls `get_weather` with the returned city
4. it calls `send_notification`
5. it produces a final answer summarizing the completed workflow

## Why This Example Is Better Than the Earlier Version

This version now includes:
- a real external LLM API
- actual tool-calling
- a real MCP client session
- a real MCP server
- a real external weather API

That makes it much closer to how production agent systems are structured.

## Common Issues

**`fastmcp` or `mcp` import error**: install dependencies with `uv pip install -r requirements.txt` or sync the workspace environment so the editor can resolve those packages

**`OPENROUTER_API_KEY is not set`**: export the environment variable before running the agent

**Unknown user**: use `alice` or `bob` in demo prompts unless you extend `USERS`

**Weather lookup failed**: the Open-Meteo geocoding request may fail if the city is misspelled or the network is unavailable

**Server/client confusion**: `mcp_server.py` defines the tools and can be run directly, but `mcp_agent.py` also starts that server internally over stdio for the MCP session. In interactive mode it now keeps that same session alive until you exit.

**Follow-up prompts stopped making sense**: if you typed `clear`, context was intentionally reset. After a reset, underspecified follow-ups like "his city" should trigger a clarification question instead of guessing.

**Want to inspect what happened**: rerun with `--verbose` to see the MCP tool calls, arguments, and returned results


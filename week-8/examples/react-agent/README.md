# Simple ReAct Agent

A runnable implementation of a ReAct-style agent using a real LLM API, OpenRouter tool-calling, and a live weather tool backed by Open-Meteo.

## Overview

This example demonstrates:
- a ReAct-style tool loop driven by a real LLM
- function/tool calling through OpenRouter
- the NVIDIA Nemotron free model through OpenRouter by default
- live weather lookup through Open-Meteo
- local product search with structured tool schemas
- interactive CLI usage for classroom demos
- verbose trace output that shows tool calls and observations

## Files

- `agent.py` - main ReAct agent implementation and CLI entry point
- `tools.py` - tool definitions and implementations
- `llm_client.py` - OpenRouter chat completion helper
- `test_agent.py` - unit tests for helper behavior
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

## Usage

```bash
# Run the default demo task
python agent.py

# Run a one-off custom task
python agent.py --task "What's the weather in San Francisco and should I bring a jacket?"

# Show the tool trace along with the final answer
python agent.py --task "Find a laptop under $1500 and explain the tradeoffs" --verbose

# Start an interactive CLI loop
python agent.py --interactive

# Interactive mode with verbose tool traces
python agent.py --interactive --verbose

# Run tests
pytest test_agent.py
```

## Example Interaction

### One-shot run

```text
$ python agent.py --task "What's the weather in San Francisco and should I bring a jacket?" --verbose

Tool: get_weather
Arguments: {"location": "San Francisco"}
Result: {"location": "San Francisco", "region": "California", "country": "United States", "temp_f": 58.4, "conditions": "partly cloudy", "wind_speed_mph": 7.1}

Final Answer: San Francisco is currently cool and partly cloudy with a light breeze, so bringing a light jacket is a good idea.
```

### Interactive mode

```text
$ python agent.py --interactive
Interactive mode enabled. Type 'exit' or 'quit' to stop.

Task> compare phones under $1000
Final Answer: The Pixel 8 gives you the best camera value, while the iPhone 15 is a strong choice if you prefer Apple's ecosystem.

Task> what is the weather in Seattle right now?
Final Answer: Seattle is currently cool with light wind. A jacket makes sense.

Task> quit
Exiting.
```

## Supported Tools

### `get_weather`
Looks up live weather data using Open-Meteo:
- geocodes the requested city
- fetches the current forecast
- returns structured weather fields

### `search_database`
Searches a tiny in-memory product catalog for:
- laptops
- tablets
- phones

## Key Concepts

### ReAct-Style Tool Loop

The agent follows this pattern:
1. send the user request and tool schemas to the model
2. let the model decide whether to call a tool
3. execute the requested tool locally
4. append the tool result to the conversation
5. ask the model for the final answer or next tool call

### Why the CLI Mode Helps

The CLI makes the example more useful in class because you can:
- ask multiple questions without editing Python files
- demonstrate one-shot prompts with `--task`
- show the reasoning workflow indirectly through `--verbose`
- compare how the same agent behaves across different prompts live

### Tool Definitions

Tools are represented in `tools.py` with:
- Python functions
- OpenAI/OpenRouter-compatible function schemas

This lets the same tool definitions work naturally with LLM tool-calling APIs.

## Extending the Agent

Add new tools by:
1. creating a new function in `tools.py`
2. adding a schema entry to the tool list
3. registering the function in the tool dispatch map
4. letting the LLM decide when to use it

## Testing

The current test file focuses on deterministic helper logic such as:
- extracting text from model responses
- handling unknown tools
- failing cleanly when the API key is missing

Run:

```bash
pytest test_agent.py
```

## Common Issues

**`OPENROUTER_API_KEY is not set`**: export the environment variable before running the agent

**Network/API errors**: both OpenRouter and Open-Meteo require network access

**Import errors**: make sure you are running commands from inside `week-8/examples/react-agent/`

**Unexpected tool behavior**: rerun with `--verbose` and inspect the exact tool arguments and tool results returned during execution


# Week 8: AI Agents & Advanced MCP Integration

This week focuses on building and running tool-using agents with both a direct ReAct pattern and an MCP-based client/server pattern.

## Slides

- [Week 8 Slides (PDF)](./slides-week-8.pdf)

## Examples

### ReAct Agent
Location: `examples/react-agent/`

Files:
- `agent.py`
- `tools.py`
- `llm_client.py`
- `test_agent.py`
- `requirements.txt`

Run:

```bash
cd week-8/examples/react-agent
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
export OPENROUTER_API_KEY=your_key_here
python agent.py
pytest test_agent.py
```

### MCP Agent
Location: `examples/mcp-agent/`

Files:
- `mcp_server.py`
- `mcp_agent.py`
- `llm_client.py`
- `config.json`
- `requirements.txt`

Run:

```bash
cd week-8/examples/mcp-agent
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
export OPENROUTER_API_KEY=your_key_here
python mcp_agent.py
```

Optional server-only run:

```bash
cd week-8/examples/mcp-agent
source .venv/bin/activate
python mcp_server.py
```

## Resources

### ReAct and agent design
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)

### MCP
- [MCP Specification](https://modelcontextprotocol.io/)
- [Building MCP Servers](https://modelcontextprotocol.io/docs/building-servers)

### Python tooling
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Pytest Documentation](https://docs.pytest.org/)
- [OpenRouter Documentation](https://openrouter.ai/docs/quickstart)

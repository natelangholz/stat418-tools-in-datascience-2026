from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

from llm_client import LLMClientError, chat_completion
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SYSTEM_PROMPT = """You are an assistant that can use MCP tools exposed by an external server.
Use the available tools when they help answer the user accurately.
Do not invent tool outputs.
After tool results are available, produce a concise final answer.

Important conversation rules:
- If the user uses a reference like "his city", "her account", "that user", or "their weather", only resolve it from the current conversation history.
- If the relevant person or entity is not clearly available in the current conversation history, ask a brief clarifying question instead of guessing.
- Never infer a hidden user after the context has been reset or cleared.
- Do not call tools with placeholder values such as "user", "that user", or similar invented stand-ins.
"""


@dataclass
class MCPToolCall:
    tool_name: str
    arguments: dict[str, Any]
    result: Any


@dataclass
class MCPAgentResult:
    final_answer: str
    tool_calls: list[MCPToolCall] = field(default_factory=list)


class MCPReActAgent:
    def __init__(self, max_turns: int = 5) -> None:
        self.max_turns = max_turns

    async def run(self, task: str) -> MCPAgentResult:
        server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"],
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                llm_tools = [self._tool_to_openrouter_schema(tool) for tool in tools_result.tools]
                messages = self._initial_messages()
                return await self._run_with_session(
                    session=session,
                    llm_tools=llm_tools,
                    messages=messages,
                    task=task,
                )

    async def run_with_existing_session(
        self,
        *,
        session: ClientSession,
        llm_tools: list[dict[str, Any]],
        messages: list[dict[str, Any]],
        task: str,
    ) -> MCPAgentResult:
        return await self._run_with_session(
            session=session,
            llm_tools=llm_tools,
            messages=messages,
            task=task,
        )

    async def _run_with_session(
        self,
        *,
        session: ClientSession,
        llm_tools: list[dict[str, Any]],
        messages: list[dict[str, Any]],
        task: str,
    ) -> MCPAgentResult:
        if self._needs_missing_context_clarification(task, messages):
            final_answer = self._build_missing_context_message(task)
            messages.append({"role": "user", "content": task})
            messages.append({"role": "assistant", "content": final_answer})
            return MCPAgentResult(final_answer=final_answer, tool_calls=[])

        messages.append({"role": "user", "content": task})
        tool_calls: list[MCPToolCall] = []

        for _ in range(self.max_turns):
            assistant_message = chat_completion(
                messages=messages,
                tools=llm_tools,
                tool_choice="auto",
                temperature=0.0,
            )

            raw_content = assistant_message.get("content")
            raw_tool_calls = assistant_message.get("tool_calls", [])

            messages.append(
                {
                    "role": "assistant",
                    "content": raw_content or "",
                    **({"tool_calls": raw_tool_calls} if raw_tool_calls else {}),
                }
            )

            if not raw_tool_calls:
                final_answer = self._extract_text_content(raw_content)
                return MCPAgentResult(final_answer=final_answer, tool_calls=tool_calls)

            for tool_call in raw_tool_calls:
                function_data = tool_call["function"]
                tool_name = function_data["name"]
                arguments = json.loads(function_data.get("arguments", "{}"))

                if self._has_placeholder_arguments(arguments):
                    final_answer = (
                        "I need a specific username or clearer context before I can use that tool."
                    )
                    messages.append({"role": "assistant", "content": final_answer})
                    return MCPAgentResult(final_answer=final_answer, tool_calls=tool_calls)

                tool_result = await session.call_tool(tool_name, arguments=arguments)
                normalized_result = self._normalize_tool_result(tool_result)

                tool_calls.append(
                    MCPToolCall(
                        tool_name=tool_name,
                        arguments=arguments,
                        result=normalized_result,
                    )
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(normalized_result),
                    }
                )

        raise RuntimeError("Agent exceeded max_turns without producing a final answer.")

    @staticmethod
    def _needs_missing_context_clarification(task: str, messages: list[dict[str, Any]]) -> bool:
        normalized_task = task.strip().lower()
        reference_markers = [
            "his ",
            "her ",
            "their ",
            "that user",
            "that person",
            "this user",
            "this person",
        ]
        if not any(marker in normalized_task for marker in reference_markers):
            return False

        prior_user_messages = [
            message.get("content", "")
            for message in messages
            if message.get("role") == "user"
        ]
        return len(prior_user_messages) == 0

    @staticmethod
    def _build_missing_context_message(task: str) -> str:
        normalized_task = task.strip().lower()
        if "weather" in normalized_task:
            return "I need to know which person you mean before I can check the weather in their city."
        if "account" in normalized_task:
            return "I need to know which person you mean before I can summarize their account."
        return "I need a bit more context about which person or item you mean before I continue."

    @staticmethod
    def _has_placeholder_arguments(arguments: dict[str, Any]) -> bool:
        placeholder_values = {
            "user",
            "that user",
            "this user",
            "person",
            "that person",
            "this person",
            "their city",
            "his city",
            "her city",
        }
        for value in arguments.values():
            if isinstance(value, str) and value.strip().lower() in placeholder_values:
                return True
        return False

    @staticmethod
    def _initial_messages() -> list[dict[str, Any]]:
        return [{"role": "system", "content": SYSTEM_PROMPT}]

    @staticmethod
    def _tool_to_openrouter_schema(tool: Any) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema,
            },
        }

    @staticmethod
    def _normalize_tool_result(result: Any) -> Any:
        if hasattr(result, "content"):
            normalized_content = []
            for item in result.content:
                if hasattr(item, "text"):
                    normalized_content.append(item.text)
                else:
                    normalized_content.append(str(item))
            if len(normalized_content) == 1:
                try:
                    return json.loads(normalized_content[0])
                except json.JSONDecodeError:
                    return normalized_content[0]
            return normalized_content
        return str(result)

    @staticmethod
    def _extract_text_content(content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    parts.append(item.get("text", ""))
            return "\n".join(part for part in parts if part).strip()
        return str(content)


def print_result(result: MCPAgentResult, *, verbose: bool = False) -> None:
    if verbose:
        for call in result.tool_calls:
            print(f"Tool: {call.tool_name}")
            print(f"Arguments: {json.dumps(call.arguments)}")
            print(f"Result: {json.dumps(call.result)}")
            print()
    print(f"Final Answer: {result.final_answer}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the MCP agent example.")
    parser.add_argument("--task", type=str, help="Run a single task and exit.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print MCP tool calls and results in addition to the final answer.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start an interactive CLI loop.",
    )
    return parser


async def run_interactive(agent: MCPReActAgent, *, verbose: bool) -> None:
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools_result = await session.list_tools()
            llm_tools = [agent._tool_to_openrouter_schema(tool) for tool in tools_result.tools]
            messages = agent._initial_messages()

            print("MCP agent interactive mode. Type 'exit' or 'quit' to stop. Type 'clear' to reset context.")
            while True:
                user_task = input("\nTask> ").strip()
                if not user_task:
                    continue
                if user_task.lower() in {"exit", "quit"}:
                    print("Exiting.")
                    return
                if user_task.lower() == "clear":
                    messages = agent._initial_messages()
                    print("Context cleared.")
                    continue

                try:
                    result = await agent.run_with_existing_session(
                        session=session,
                        llm_tools=llm_tools,
                        messages=messages,
                        task=user_task,
                    )
                    print_result(result, verbose=verbose)
                except LLMClientError as exc:
                    print(f"LLM configuration error: {exc}")
                    return
                except Exception as exc:
                    print(f"Agent error: {exc}")


if __name__ == "__main__":
    args = build_parser().parse_args()
    agent = MCPReActAgent()

    try:
        if args.interactive:
            asyncio.run(run_interactive(agent, verbose=args.verbose))
        else:
            task = args.task or "Look up alice, summarize her account, and send her a notification."
            result = asyncio.run(agent.run(task))
            print_result(result, verbose=args.verbose)
    except LLMClientError as exc:
        print(f"LLM configuration error: {exc}")



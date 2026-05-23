from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from typing import Any

from llm_client import LLMClientError, chat_completion
from tools import TOOL_SCHEMAS, TOOLS


SYSTEM_PROMPT = """You are a ReAct-style assistant that can answer user requests by calling tools.
Use tools when they help you answer the question accurately.
If you call a tool, use the returned observation to produce a concise final answer.
Do not invent tool outputs.
"""


@dataclass
class Step:
    thought: str
    action: str | None = None
    action_input: dict[str, Any] | None = None
    observation: Any | None = None


@dataclass
class AgentResult:
    final_answer: str
    steps: list[Step] = field(default_factory=list)


class ReActAgent:
    def __init__(self, max_turns: int = 5) -> None:
        self.max_turns = max_turns

    def call_tool(self, tool_name: str, args: dict[str, Any]) -> Any:
        if tool_name not in TOOLS:
            raise ValueError(f"Unknown tool: {tool_name}")
        return TOOLS[tool_name](**args)

    def run(self, task: str) -> AgentResult:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task},
        ]
        steps: list[Step] = []

        for _ in range(self.max_turns):
            assistant_message = chat_completion(
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.0,
            )

            tool_calls = assistant_message.get("tool_calls", [])
            content = assistant_message.get("content")

            messages.append(
                {
                    "role": "assistant",
                    "content": content or "",
                    **({"tool_calls": tool_calls} if tool_calls else {}),
                }
            )

            if not tool_calls:
                final_answer = self._extract_text_content(content)
                return AgentResult(final_answer=final_answer, steps=steps)

            for tool_call in tool_calls:
                function_data = tool_call["function"]
                tool_name = function_data["name"]
                raw_arguments = function_data.get("arguments", "{}")
                parsed_arguments = json.loads(raw_arguments)

                thought = self._extract_text_content(content) or f"Calling tool {tool_name}."
                observation = self.call_tool(tool_name, parsed_arguments)

                steps.append(
                    Step(
                        thought=thought,
                        action=tool_name,
                        action_input=parsed_arguments,
                        observation=observation,
                    )
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(observation),
                    }
                )

        raise RuntimeError("Agent exceeded max_turns without producing a final answer.")

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


def print_result(result: AgentResult, *, verbose: bool = False) -> None:
    if verbose:
        for step in result.steps:
            print(f"Thought: {step.thought}")
            if step.action:
                print(f"Action: {step.action}({json.dumps(step.action_input)})")
            if step.observation is not None:
                print(f"Observation: {json.dumps(step.observation)}")
            print()
    print(f"Final Answer: {result.final_answer}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ReAct agent example.")
    parser.add_argument("--task", type=str, help="Run a single task and exit.")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print tool calls and observations in addition to the final answer.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start an interactive CLI loop.",
    )
    return parser


def run_interactive(agent: ReActAgent, *, verbose: bool) -> None:
    print("ReAct agent interactive mode. Type 'exit' or 'quit' to stop.")
    while True:
        user_task = input("\nTask> ").strip()
        if not user_task:
            continue
        if user_task.lower() in {"exit", "quit"}:
            print("Exiting.")
            return

        try:
            result = agent.run(user_task)
            print_result(result, verbose=verbose)
        except LLMClientError as exc:
            print(f"LLM configuration error: {exc}")
            return
        except Exception as exc:
            print(f"Agent error: {exc}")


if __name__ == "__main__":
    args = build_parser().parse_args()
    agent = ReActAgent()

    if args.interactive:
        run_interactive(agent, verbose=args.verbose)
    else:
        user_task = args.task or "What's the weather in San Francisco and should I bring an umbrella?"
        try:
            result = agent.run(user_task)
            print_result(result, verbose=args.verbose)
        except LLMClientError as exc:
            print(f"LLM configuration error: {exc}")



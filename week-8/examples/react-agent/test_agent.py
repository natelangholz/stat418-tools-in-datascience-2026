from agent import ReActAgent
from llm_client import LLMClientError


class FakeAgent(ReActAgent):
    def __init__(self) -> None:
        super().__init__(max_turns=3)
        self._messages_seen = []

    def run(self, task: str):  # type: ignore[override]
        return super().run(task)


def test_extract_text_content_from_string() -> None:
    assert ReActAgent._extract_text_content("hello") == "hello"


def test_extract_text_content_from_openrouter_content_list() -> None:
    content = [{"type": "text", "text": "first"}, {"type": "text", "text": "second"}]
    assert ReActAgent._extract_text_content(content) == "first\nsecond"


def test_call_tool_raises_for_unknown_tool() -> None:
    agent = ReActAgent()
    try:
        agent.call_tool("missing_tool", {})
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "Unknown tool" in str(exc)


def test_main_handles_llm_configuration_errors(monkeypatch, capsys) -> None:
    def fake_run(self, task: str):
        raise LLMClientError("OPENROUTER_API_KEY is not set.")

    monkeypatch.setattr(ReActAgent, "run", fake_run)

    agent = ReActAgent()
    try:
        agent.run("weather")
    except LLMClientError as exc:
        print(f"LLM configuration error: {exc}")

    captured = capsys.readouterr()
    assert "OPENROUTER_API_KEY is not set" in captured.out



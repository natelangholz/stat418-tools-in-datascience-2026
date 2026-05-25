from __future__ import annotations

import os
from typing import Any

import requests


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


class LLMClientError(RuntimeError):
    pass


def get_openrouter_api_key() -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise LLMClientError("OPENROUTER_API_KEY is not set.")
    return api_key


def get_model_name() -> str:
    return os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)


def chat_completion(
    *,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    tool_choice: str | dict[str, Any] | None = "auto",
    temperature: float = 0.0,
) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {get_openrouter_api_key()}",
        "Content-Type": "application/json",
    }

    payload: dict[str, Any] = {
        "model": get_model_name(),
        "messages": messages,
        "temperature": temperature,
    }

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice

    response = requests.post(
        OPENROUTER_BASE_URL,
        headers=headers,
        json=payload,
        timeout=60,
    )

    if not response.ok:
        raise LLMClientError(
            f"OpenRouter request failed with status {response.status_code}: {response.text}"
        )

    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise LLMClientError("OpenRouter response did not contain any choices.")

    return choices[0]["message"]

# Made with Bob

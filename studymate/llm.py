"""Thin OpenRouter client with streaming and friendly errors."""
from __future__ import annotations

from collections.abc import Iterator

import streamlit as st
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from .config import APP_NAME, OPENROUTER_BASE_URL


class LLMError(Exception):
    """Raised with a message that is safe to show to the user."""


@st.cache_resource(show_spinner=False)
def get_client(api_key: str) -> OpenAI:
    return OpenAI(
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
        default_headers={"X-Title": APP_NAME},
    )


def stream_reply(
    client: OpenAI, model: str, messages: list[dict], temperature: float
) -> Iterator[str]:
    """Yield the assistant reply token by token."""
    try:
        stream = client.chat.completions.create(
            model=model, messages=messages, temperature=temperature, stream=True
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except AuthenticationError as exc:
        raise LLMError("Invalid API key. Check OPENROUTER_API_KEY in your secrets.") from exc
    except RateLimitError as exc:
        raise LLMError("Rate limit reached. Wait a moment and try again.") from exc
    except APIConnectionError as exc:
        raise LLMError("Could not reach OpenRouter. Check your internet connection.") from exc
    except APIStatusError as exc:
        if exc.status_code == 402:
            raise LLMError("Your OpenRouter account is out of credits.") from exc
        raise LLMError(f"The model returned an error (status {exc.status_code}).") from exc

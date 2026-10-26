"""Central configuration. Change names, models and limits here."""
from __future__ import annotations

import os

import streamlit as st

APP_NAME = "StudyMate"
APP_TAGLINE = "Your AI study partner. Ask questions, upload notes, learn faster."
AUTHOR = "Avirup Roy"

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

MODELS: dict[str, str] = {
    "DeepSeek Chat (default)": "deepseek/deepseek-chat",
    "GPT-4o mini": "openai/gpt-4o-mini",
    "Llama 3.3 70B": "meta-llama/llama-3.3-70b-instruct",
    "Gemini 2.0 Flash": "google/gemini-2.0-flash-001",
}
DEFAULT_MODEL_LABEL = "DeepSeek Chat (default)"

MAX_HISTORY_MESSAGES = 12      
MAX_PDF_MB = 20                
CONTEXT_CHAR_BUDGET = 9000    


def get_secret(name: str, default: str | None = None) -> str | None:
    """Read from Streamlit secrets, falling back to environment variables."""
    try:
        return st.secrets[name]
    except Exception:
        return os.environ.get(name, default)

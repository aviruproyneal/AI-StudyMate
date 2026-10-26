# 📘 AI StudyMate

An AI study assistant that explains concepts, answers questions about your own PDFs, and turns notes into quizzes and flashcards. Built with **Streamlit** and **OpenRouter**.

<!-- Add a screenshot or GIF here: ![AI StudyMate demo](docs/demo.gif) -->

## Features

- **Streaming chat** with conversation memory
- **6 study modes**: Explain, ELI5, Summarize, Quiz me, Flashcards, Study plan
- **3 difficulty levels**: Beginner, Intermediate, Advanced
- **Chat with your PDF**: pages are chunked and the most relevant passages are retrieved per question (TF-IDF style, no heavy dependencies), with page-number citations
- **One-click actions** for uploaded documents: summarize, quiz, flashcards, key concepts
- **Switchable models** via OpenRouter (DeepSeek, GPT-4o mini, Llama, Gemini)
- **Export** any session as Markdown
- Friendly error handling (bad key, rate limits, scanned/encrypted PDFs)
- Light and dark mode friendly UI

## Project structure

```
ai-studymate/
├── app.py                 # Streamlit UI and chat flow
├── studymate/
│   ├── config.py          # App name, models, limits, secrets helper
│   ├── prompts.py         # System prompts, modes, levels
│   ├── pdf_utils.py       # PDF parsing, chunking, retrieval
│   ├── llm.py             # OpenRouter client + streaming + errors
│   └── styles.py          # CSS and header HTML
├── tests/                 # pytest unit tests
├── .streamlit/
│   ├── config.toml        # Theme and server settings
│   └── secrets.toml.example
└── requirements.txt
```

## Run locally

```bash
git clone https://github.com/<your-username>/ai-studymate.git
cd ai-studymate
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edit .streamlit/secrets.toml and paste your OpenRouter key

streamlit run app.py
```

## Deploy (free): Streamlit Community Cloud

1. Push this project to a **public GitHub repo** (`secrets.toml` is git-ignored, so your key stays private).
2. Go to <https://share.streamlit.io>, click **New app**, pick the repo, and set the main file to `app.py`.
3. Open **Advanced settings → Secrets** and paste:
   ```toml
   OPENROUTER_API_KEY = "sk-or-v1-..."
   ```
4. Deploy. You get a public `*.streamlit.app` link to share.

> **Why not Vercel?** Streamlit needs a long-running server with WebSockets, which Vercel's serverless functions do not support. Streamlit Community Cloud, Render, Railway or Hugging Face Spaces are the right homes for it.

> **Protect your credits:** a public app spends *your* OpenRouter balance. Set a spending limit on your OpenRouter key.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Roadmap

- OCR for scanned PDFs
- Multiple documents per session
- Saved study sets and spaced repetition

## License

MIT. Built by Avirup Roy.

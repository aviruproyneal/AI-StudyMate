"""AI StudyMate: main Streamlit app."""
from __future__ import annotations

import hashlib
from datetime import datetime

import streamlit as st

from studymate import config, prompts
from studymate.llm import LLMError, get_client, stream_reply
from studymate.pdf_utils import PDFError, build_context, build_index
from studymate.styles import CSS, HEADER_HTML

USER_AVATAR, BOT_AVATAR = "🧑‍🎓", "📘"

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS, unsafe_allow_html=True)


# State
def init_state() -> None:
    st.session_state.setdefault("messages", [])   
    st.session_state.setdefault("doc", None)      
    st.session_state.setdefault("doc_key", None)  
    st.session_state.setdefault("pending", None)  


def queue_prompt(text: str, broad: bool = False) -> None:
    st.session_state.pending = (text, broad)


def clear_chat() -> None:
    st.session_state.messages = []


def chat_as_markdown() -> str:
    lines = [f"# {config.APP_NAME} session", f"_Exported {datetime.now():%Y-%m-%d %H:%M}_", ""]
    for m in st.session_state.messages:
        who = "You" if m["role"] == "user" else config.APP_NAME
        lines += [f"### {who}", m["content"], ""]
    return "\n".join(lines)


init_state()


# Sidebar
with st.sidebar:
    st.markdown(f"### 📘 {config.APP_NAME}")

    st.markdown('<div class="section-label">Study mode</div>', unsafe_allow_html=True)
    mode = st.selectbox(
        "Study mode",
        list(prompts.MODES),
        index=list(prompts.MODES).index(prompts.DEFAULT_MODE),
        label_visibility="collapsed",
    )
    level = st.selectbox(
        "Explanation level",
        list(prompts.LEVELS),
        index=list(prompts.LEVELS).index(prompts.DEFAULT_LEVEL),
    )

    st.markdown('<div class="section-label">Study material</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload a PDF", type="pdf", label_visibility="collapsed",
        help=f"Text-based PDFs up to {config.MAX_PDF_MB} MB.",
    )

    if uploaded is None:
        st.session_state.doc, st.session_state.doc_key = None, None
    else:
        data = uploaded.getvalue()
        key = hashlib.sha256(data).hexdigest()
        if key != st.session_state.doc_key:
            if len(data) > config.MAX_PDF_MB * 1024 * 1024:
                st.error(f"File is larger than {config.MAX_PDF_MB} MB.")
            else:
                with st.spinner("Reading PDF..."):
                    try:
                        st.session_state.doc = build_index(uploaded.name, data)
                        st.session_state.doc_key = key
                        st.toast("PDF loaded", icon="📄")
                    except PDFError as err:
                        st.session_state.doc, st.session_state.doc_key = None, None
                        st.error(str(err))

    doc = st.session_state.doc
    if doc:
        st.markdown(
            f'<div class="doc-card">📄 <b>{doc.name}</b><br>'
            f'<span class="doc-meta">{doc.n_pages} pages · {doc.n_words:,} words</span></div>',
            unsafe_allow_html=True,
        )

    with st.expander("⚙️ Advanced"):
        model_label = st.selectbox("Model", list(config.MODELS))
        temperature = st.slider("Creativity", 0.0, 1.0, 0.4, 0.1,
                                help="Lower = more precise, higher = more creative.")

    st.markdown('<div class="section-label">Session</div>', unsafe_allow_html=True)
    st.button("🗑️ Clear chat", on_click=clear_chat, use_container_width=True)
    st.download_button(
        "⬇️ Export chat (.md)",
        data=chat_as_markdown(),
        file_name="studymate-session.md",
        mime="text/markdown",
        use_container_width=True,
        disabled=not st.session_state.messages,
    )
    st.caption(f"Built by {config.AUTHOR}. AI can make mistakes, so verify important facts.")


# Header
st.markdown(HEADER_HTML, unsafe_allow_html=True)

api_key = config.get_secret("OPENROUTER_API_KEY")
if not api_key:
    st.error("**OPENROUTER_API_KEY is missing.**")
    st.markdown(
        "Add it to `.streamlit/secrets.toml` (see `secrets.toml.example`) "
        "or set it as an environment variable, then reload."
    )
    st.stop()

model_id = config.get_secret("MODEL_NAME") or config.MODELS[model_label]
if model_label != config.DEFAULT_MODEL_LABEL:
    model_id = config.MODELS[model_label]


# Input
typed = st.chat_input("Ask a question, or upload a PDF in the sidebar...")
queued, st.session_state.pending = st.session_state.pending, None
prompt, broad = (queued if queued else (typed, False))


# Welcome / Quick actions
if not st.session_state.messages and not prompt:
    if doc:
        st.markdown("**What would you like to do with your document?**")
        cols = st.columns(2)
        for i, (label, text) in enumerate(prompts.QUICK_ACTIONS):
            cols[i % 2].button(label, key=f"qa_{i}", use_container_width=True,
                               on_click=queue_prompt, args=(text, True))
    else:
        st.markdown("**Try one of these, or type your own question:**")
        cols = st.columns(2)
        for i, text in enumerate(prompts.EXAMPLE_PROMPTS):
            cols[i % 2].button(text, key=f"ex_{i}", use_container_width=True,
                               on_click=queue_prompt, args=(text,))


# History
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=USER_AVATAR if m["role"] == "user" else BOT_AVATAR):
        st.markdown(m["content"])


# Generate
def build_messages(history: list[dict], broad_context: bool) -> list[dict]:
    messages = [{"role": "system", "content": prompts.build_system_prompt(mode, level)}]
    if doc:
        user_turns = [m["content"] for m in history if m["role"] == "user"]
        query = " ".join(user_turns[-2:])
        context = build_context(doc, query, config.CONTEXT_CHAR_BUDGET, broad=broad_context)
        messages.append({
            "role": "system",
            "content": prompts.DOC_CONTEXT_TEMPLATE.format(name=doc.name, context=context),
        })
    messages.extend(history[-config.MAX_HISTORY_MESSAGES:])
    return messages


if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        reply = None
        try:
            payload = build_messages(st.session_state.messages, broad)
            reply = st.write_stream(
                stream_reply(get_client(api_key), model_id, payload, temperature)
            )
        except LLMError as err:
            st.error(str(err))
        except Exception:
            st.error("Something went wrong. Please try again.")

    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()  
    else:
        st.session_state.messages.pop()  

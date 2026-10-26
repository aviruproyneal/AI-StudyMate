"""Custom CSS and HTML snippets. Works in light and dark themes."""
from .config import APP_NAME, APP_TAGLINE

CSS = """
<style>
#MainMenu, footer { visibility: hidden; }

.block-container { max-width: 860px; padding-top: 2rem; padding-bottom: 6rem; }

.hero { display: flex; align-items: center; gap: 14px; margin-bottom: 2px; }
.hero-logo {
    width: 46px; height: 46px; border-radius: 12px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    box-shadow: 0 6px 16px rgba(79, 70, 229, 0.35);
}
.hero-title {
    font-size: 2rem; font-weight: 700; letter-spacing: -0.02em;
    margin: 0; padding: 0; line-height: 1.1;
}
.hero-sub { opacity: 0.65; margin: 4px 0 1.25rem 0; font-size: 0.98rem; }

.doc-card {
    border: 1px solid rgba(128, 128, 128, 0.28); border-radius: 12px;
    padding: 10px 12px; font-size: 0.85rem; line-height: 1.4; margin-top: 6px;
}
.doc-card b { word-break: break-word; }
.doc-meta { opacity: 0.65; }

.section-label {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; opacity: 0.55; margin: 0.4rem 0 0.2rem 0;
}

.stButton > button { border-radius: 10px; }
section[data-testid="stSidebar"] { border-right: 1px solid rgba(128, 128, 128, 0.15); }
[data-testid="stChatMessage"] { border-radius: 14px; }
</style>
"""

HEADER_HTML = f"""
<div class="hero">
  <div class="hero-logo">
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
      <path d="M4 6C4 5 5 4 6 4H18C19 4 20 5 20 6V18C20 19 19 20 18 20H6C5 20 4 19 4 18V6Z"
            stroke="#fff" stroke-width="1.6"/>
      <path d="M8 8H16M8 12H14M8 16H12" stroke="#fff" stroke-width="1.6" stroke-linecap="round"/>
    </svg>
  </div>
  <p class="hero-title">{APP_NAME}</p>
</div>
<p class="hero-sub">{APP_TAGLINE}</p>
"""

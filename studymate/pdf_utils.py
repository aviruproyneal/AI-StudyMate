"""PDF reading, chunking and lightweight keyword retrieval (no extra deps)."""
from __future__ import annotations

import io
import math
import re
from collections import Counter
from dataclasses import dataclass, field

from pypdf import PdfReader


class PDFError(Exception):
    """Raised with a user-friendly message when a PDF cannot be used."""


STOPWORDS = frozenset(
    "the and for are but not you all any can had her was one our out has have "
    "this that with from they will would there their what about which when your "
    "been were said each she how its who into than them then these those some "
    "such only other also more most very just over does did doing being".split()
)


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-zA-Z0-9]{3,}", text.lower()) if w not in STOPWORDS]


@dataclass
class Chunk:
    page: int
    text: str
    tokens: list[str] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self.tokens = tokenize(self.text)


@dataclass
class DocumentIndex:
    name: str
    n_pages: int
    chunks: list[Chunk]

    @property
    def n_chars(self) -> int:
        return sum(len(c.text) for c in self.chunks)

    @property
    def n_words(self) -> int:
        return sum(len(c.text.split()) for c in self.chunks)


def chunk_text(text: str, page: int, max_chars: int = 1200) -> list[Chunk]:
    """Split one page of text into chunks of at most ``max_chars``."""
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[Chunk] = []
    buf = ""

    for para in paragraphs:
        while len(para) > max_chars:
            cut = para.rfind(" ", 0, max_chars)
            cut = cut if cut > 0 else max_chars
            if buf:
                chunks.append(Chunk(page, buf))
                buf = ""
            chunks.append(Chunk(page, para[:cut].strip()))
            para = para[cut:].strip()
        if not para:
            continue
        if len(buf) + len(para) + 2 <= max_chars:
            buf = f"{buf}\n\n{para}" if buf else para
        else:
            chunks.append(Chunk(page, buf))
            buf = para

    if buf:
        chunks.append(Chunk(page, buf))
    return chunks


def build_index(name: str, data: bytes) -> DocumentIndex:
    try:
        reader = PdfReader(io.BytesIO(data))
    except Exception as exc:  # corrupted / not a PDF
        raise PDFError("Could not open this file. It may be corrupted.") from exc

    if reader.is_encrypted:
        try:
            ok = reader.decrypt("")
        except Exception:
            ok = 0
        if not ok:
            raise PDFError("This PDF is password-protected. Please upload an unlocked copy.")

    chunks: list[Chunk] = []
    for number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        text = re.sub(r"[ \t]+", " ", text).strip()
        if text:
            chunks.extend(chunk_text(text, number))

    if not chunks:
        raise PDFError(
            "No readable text found. This looks like a scanned PDF (images only). "
            "Please upload a text-based PDF."
        )
    return DocumentIndex(name=name, n_pages=len(reader.pages), chunks=chunks)


def _spread(chunks: list[Chunk], budget: int) -> list[Chunk]:
    """Evenly sample chunks across the document to fit the budget."""
    total = sum(len(c.text) for c in chunks)
    if total <= budget:
        return list(chunks)
    avg = total / len(chunks)
    k = max(1, int(budget // avg))
    if k == 1:
        return [chunks[0]]
    idx = sorted({round(i * (len(chunks) - 1) / (k - 1)) for i in range(k)})
    return [chunks[i] for i in idx]


def retrieve(chunks: list[Chunk], query: str, budget: int) -> list[Chunk]:
    """Pick the chunks most relevant to ``query`` (TF-IDF style scoring)."""
    if sum(len(c.text) for c in chunks) <= budget:
        return list(chunks)

    q_terms = set(tokenize(query))
    if not q_terms:
        return _spread(chunks, budget)

    n = len(chunks)
    df: Counter[str] = Counter()
    for c in chunks:
        df.update(set(c.tokens))

    scored: list[tuple[float, int]] = []
    for i, c in enumerate(chunks):
        tf = Counter(c.tokens)
        score = sum(
            (1 + math.log(tf[t])) * math.log(1 + n / df[t]) for t in q_terms if t in tf
        )
        scored.append((score, i))
    scored.sort(reverse=True)

    picked: list[int] = []
    used = 0
    for score, i in scored:
        if score <= 0:
            break
        size = len(chunks[i].text)
        if used + size > budget:
            continue
        picked.append(i)
        used += size

    if not picked:
        return _spread(chunks, budget)
    return [chunks[i] for i in sorted(picked)]


def build_context(doc: DocumentIndex, query: str, budget: int, broad: bool = False) -> str:
    """Return labelled excerpts. ``broad=True`` samples the whole document."""
    selected = _spread(doc.chunks, budget) if broad else retrieve(doc.chunks, query, budget)
    return "\n\n".join(f"[Page {c.page}]\n{c.text}" for c in selected)

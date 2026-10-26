from studymate.pdf_utils import Chunk, build_context, build_index, chunk_text, retrieve, DocumentIndex, PDFError
import pytest


def test_chunk_text_respects_limit():
    text = ("word " * 600).strip()
    chunks = chunk_text(text, page=1, max_chars=500)
    assert len(chunks) > 1
    assert all(len(c.text) <= 500 for c in chunks)
    assert all(c.page == 1 for c in chunks)


def test_retrieve_returns_all_when_small():
    chunks = [Chunk(1, "short text about cells")]
    assert retrieve(chunks, "anything", budget=1000) == chunks


def test_retrieve_finds_relevant_chunk():
    chunks = [
        Chunk(1, "Mitochondria produce ATP in the cell. " * 20),
        Chunk(2, "The French Revolution began in 1789. " * 20),
        Chunk(3, "Photosynthesis happens in chloroplasts. " * 20),
    ]
    result = retrieve(chunks, "when did the french revolution begin", budget=800)
    assert result and result[0].page == 2


def test_build_context_labels_pages_and_broad_samples():
    chunks = [Chunk(i, f"content number {i} " * 30) for i in range(1, 11)]
    doc = DocumentIndex("x.pdf", 10, chunks)
    ctx = build_context(doc, "", budget=1500, broad=True)
    assert "[Page 1]" in ctx and "[Page 10]" in ctx


def test_build_index_rejects_garbage():
    with pytest.raises(PDFError):
        build_index("bad.pdf", b"not a pdf")

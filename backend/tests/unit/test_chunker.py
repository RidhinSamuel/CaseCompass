"""Unit tests for the chunker."""
import pytest

from app.services.chunker import chunk_text


@pytest.mark.unit
def test_chunk_empty_input_returns_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


@pytest.mark.unit
def test_chunk_short_text_returns_single_chunk():
    text = "A short document about a case."
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=10)
    assert len(chunks) == 1
    assert chunks[0].strip() == text


@pytest.mark.unit
def test_chunk_long_text_splits_into_multiple():
    text = ("Paragraph one. " * 50) + "\n\n" + ("Paragraph two. " * 50)
    chunks = chunk_text(text, chunk_size=200, chunk_overlap=20)
    assert len(chunks) >= 2
    for c in chunks:
        assert len(c) <= 300  # size + a small overlap slack

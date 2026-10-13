"""Unit tests for PDF text extraction."""
import fitz
import pytest

from app.services.pdf_extract import PdfExtractionError, extract_pdf_text


def _make_pdf(pages: list[str]) -> bytes:
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        if text:
            page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.mark.unit
def test_extracts_text_and_page_count():
    text, pages = extract_pdf_text(_make_pdf(["Hello judgment", "Second page"]))
    assert pages == 2
    assert "Hello judgment" in text
    assert "Second page" in text


@pytest.mark.unit
def test_blank_pdf_raises():
    with pytest.raises(PdfExtractionError, match="No extractable text"):
        extract_pdf_text(_make_pdf([""]))


@pytest.mark.unit
def test_random_bytes_raise():
    with pytest.raises(PdfExtractionError):
        extract_pdf_text(b"not a pdf at all \x00\x01\x02")

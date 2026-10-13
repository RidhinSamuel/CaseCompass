"""Extract plain text from PDF bytes using PyMuPDF."""
import fitz  # PyMuPDF


class PdfExtractionError(Exception):
    """Raised when a PDF cannot be turned into usable text."""


def extract_pdf_text(data: bytes) -> tuple[str, int]:
    """Return ``(text, page_count)`` for the given PDF bytes.

    Raises PdfExtractionError if the file is not a readable PDF, is
    encrypted, or contains no extractable text (e.g. a scanned PDF).
    """
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception as exc:  # noqa: BLE001
        raise PdfExtractionError("File is not a valid or readable PDF") from exc

    try:
        if doc.needs_pass:
            raise PdfExtractionError("Password-protected PDFs are not supported")
        page_count = doc.page_count
        try:
            pages = [page.get_text("text", sort=True) for page in doc]
        except Exception as exc:  # noqa: BLE001
            raise PdfExtractionError("Could not read text from PDF") from exc
    finally:
        doc.close()

    # Postgres TEXT columns reject NUL bytes, which some PDFs contain.
    pages = [p.replace("\x00", "") for p in pages]
    text = "\n\n".join(p.strip() for p in pages if p.strip())
    if not text:
        raise PdfExtractionError(
            "No extractable text found - scanned PDFs aren't supported yet"
        )
    return text, page_count

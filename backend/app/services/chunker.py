"""Text chunking with sensible defaults for legal documents.

Legal text is often long and dense. We use LangChain's recursive splitter,
which respects paragraph and sentence boundaries where possible.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Tuned for legal / case-file style prose: enough context per chunk without
# blowing past model context windows during retrieval.
DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 120


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split a document into overlapping chunks suitable for embedding."""
    if not text or not text.strip():
        return []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return [c for c in splitter.split_text(text) if c.strip()]

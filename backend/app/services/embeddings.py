"""Embedding service — Hugging Face Inference API via LangChain.

Uses the hosted `sentence-transformers/all-MiniLM-L6-v2` model, so no model
weights or torch are loaded locally. Requires `HF_TOKEN`.
"""
import logging
from functools import lru_cache

from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.core.config import settings

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_model() -> HuggingFaceEndpointEmbeddings:
    """Create and cache the Hugging Face endpoint embeddings client."""
    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is not set; it is required for embeddings.")

    log.info("Using Hugging Face endpoint embeddings: %s", settings.hf_embedding_model)
    embedding_model: HuggingFaceEndpointEmbeddings = HuggingFaceEndpointEmbeddings(
        model=settings.hf_embedding_model,
        task="feature-extraction",
        huggingfacehub_api_token=settings.hf_token,
    )
    return embedding_model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns a list of float vectors."""
    if not texts:
        return []
    return _get_model().embed_documents(texts)


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    return _get_model().embed_query(query)

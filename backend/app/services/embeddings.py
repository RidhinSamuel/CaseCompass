"""Embedding service — wraps a HuggingFace Sentence-Transformer model.

The model is loaded lazily on first use so the API can start quickly.
Free, open-source, and runs locally (CPU or GPU) with no paid tokens.
"""
import logging
from functools import lru_cache
from typing import cast

import numpy as np

from app.core.config import settings

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_model():
    """Lazy-load and cache the sentence-transformer model."""
    from sentence_transformers import SentenceTransformer  # local import: heavy

    log.info("Loading embedding model: %s", settings.hf_embedding_model)
    return SentenceTransformer(settings.hf_embedding_model)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns a list of float vectors."""
    if not texts:
        return []
    model = _get_model()
    vectors = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,  # cosine-friendly
    )
    return cast(np.ndarray, vectors).tolist()


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    return embed_texts([query])[0]

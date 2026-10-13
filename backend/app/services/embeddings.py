"""Embedding service for `sentence-transformers/all-MiniLM-L6-v2` (384 dims).

Two interchangeable backends, chosen with `EMBEDDING_BACKEND`:
- "local" (default): runs the model on this machine with fastembed (ONNX
  Runtime, no torch, no API credits). Set `EMBEDDING_DEVICE=cuda` to use an
  NVIDIA GPU (requires the `fastembed-gpu` package instead of `fastembed`).
- "hf": calls the Hugging Face Inference API via LangChain. Requires `HF_TOKEN`.

Both produce the same vectors, so stored chunks stay compatible when switching.
"""
import logging
from functools import lru_cache
from typing import Protocol

from app.core.config import settings

log = logging.getLogger(__name__)


class _Embedder(Protocol):
    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...


class _LocalEmbedder:
    """fastembed wrapper exposing the same interface as the LangChain client."""

    def __init__(self) -> None:
        from fastembed import TextEmbedding  # local import: loads ONNX Runtime

        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if settings.embedding_device == "cuda"
            else ["CPUExecutionProvider"]
        )
        log.info(
            "Loading local embedding model %s on %s",
            settings.hf_embedding_model,
            settings.embedding_device,
        )
        self._model = TextEmbedding(
            model_name=settings.hf_embedding_model,
            cache_dir=settings.embedding_cache_dir,
            providers=providers,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [vec.tolist() for vec in self._model.embed(texts, batch_size=32)]

    def embed_query(self, text: str) -> list[float]:
        return next(iter(self._model.query_embed(text))).tolist()


def _hf_embedder() -> _Embedder:
    from langchain_huggingface import HuggingFaceEndpointEmbeddings

    if not settings.hf_token:
        raise RuntimeError("HF_TOKEN is not set; it is required for embeddings.")

    log.info("Using Hugging Face endpoint embeddings: %s", settings.hf_embedding_model)
    return HuggingFaceEndpointEmbeddings(
        model=settings.hf_embedding_model,
        task="feature-extraction",
        huggingfacehub_api_token=settings.hf_token,
    )


@lru_cache(maxsize=1)
def _get_model() -> _Embedder:
    """Create the configured embedder once per process."""
    if settings.embedding_backend == "hf":
        return _hf_embedder()
    return _LocalEmbedder()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Returns a list of float vectors."""
    if not texts:
        return []
    return _get_model().embed_documents(texts)


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    return _get_model().embed_query(query)

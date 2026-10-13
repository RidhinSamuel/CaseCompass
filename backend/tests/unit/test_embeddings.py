"""Unit tests for the embedding backend selection (no model is loaded)."""
import pytest

from app.services import embeddings


@pytest.fixture(autouse=True)
def _clear_cache():
    embeddings._get_model.cache_clear()
    yield
    embeddings._get_model.cache_clear()


class _FakeEmbedder:
    def embed_documents(self, texts):
        return [[float(len(t))] for t in texts]

    def embed_query(self, text):
        return [float(len(text))]


def test_local_backend_is_default(monkeypatch):
    monkeypatch.setattr(embeddings, "_LocalEmbedder", _FakeEmbedder)
    monkeypatch.setattr(embeddings.settings, "embedding_backend", "local")
    assert embeddings.embed_texts(["ab", "abc"]) == [[2.0], [3.0]]
    assert embeddings.embed_query("abcd") == [4.0]


def test_hf_backend_requires_token(monkeypatch):
    monkeypatch.setattr(embeddings.settings, "embedding_backend", "hf")
    monkeypatch.setattr(embeddings.settings, "hf_token", None)
    with pytest.raises(RuntimeError, match="HF_TOKEN"):
        embeddings.embed_query("question")


def test_empty_batch_skips_model(monkeypatch):
    def _boom():
        raise AssertionError("model should not load for an empty batch")

    monkeypatch.setattr(embeddings, "_get_model", _boom)
    assert embeddings.embed_texts([]) == []

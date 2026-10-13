"""Route tests for deleting and retrying documents (DB and RabbitMQ mocked)."""
import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from app.api.deps import get_current_user
from app.api.routes import documents as documents_route
from app.db.session import get_db

OWNER = uuid.uuid4()


class FakeDb:
    def __init__(self, docs):
        self.docs = {d.id: d for d in docs}
        self.deleted = []

    def get(self, _model, doc_id):
        return self.docs.get(doc_id)

    def delete(self, obj):
        self.deleted.append(obj)
        self.docs.pop(obj.id, None)

    def commit(self):
        pass

    def refresh(self, obj):
        pass


def _doc(status: str, user_id=OWNER):
    return SimpleNamespace(
        id=uuid.uuid4(),
        user_id=user_id,
        case_id="CASE-1",
        title="A case",
        source_filename="case.pdf",
        status=status,
        chunk_count=0,
        created_at=datetime.now(UTC),
    )


@pytest.fixture()
def setup(app, client, monkeypatch):
    published = []

    async def fake_publish(msg):
        published.append(msg)

    monkeypatch.setattr(documents_route.rabbitmq, "publish", fake_publish)
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=OWNER)

    def _with(*docs):
        db = FakeDb(docs)
        app.dependency_overrides[get_db] = lambda: db
        return db

    yield client, _with, published
    app.dependency_overrides.clear()


def test_delete_own_document(setup):
    client, with_docs, _ = setup
    doc = _doc("ready")
    db = with_docs(doc)
    resp = client.delete(f"/api/documents/{doc.id}")
    assert resp.status_code == 204
    assert db.deleted == [doc]


def test_delete_other_users_document_is_404(setup):
    client, with_docs, _ = setup
    doc = _doc("ready", user_id=uuid.uuid4())
    db = with_docs(doc)
    assert client.delete(f"/api/documents/{doc.id}").status_code == 404
    assert db.deleted == []


def test_delete_missing_document_is_404(setup):
    client, with_docs, _ = setup
    with_docs()
    assert client.delete(f"/api/documents/{uuid.uuid4()}").status_code == 404


def test_retry_failed_document_requeues(setup):
    client, with_docs, published = setup
    doc = _doc("failed")
    with_docs(doc)
    resp = client.post(f"/api/documents/{doc.id}/retry")
    assert resp.status_code == 200
    assert resp.json()["status"] == "pending"
    assert published == [{"document_id": str(doc.id)}]


@pytest.mark.parametrize("status", ["pending", "processing", "ready"])
def test_retry_non_failed_document_is_409(setup, status):
    client, with_docs, published = setup
    doc = _doc(status)
    with_docs(doc)
    assert client.post(f"/api/documents/{doc.id}/retry").status_code == 409
    assert published == []


def test_retry_other_users_document_is_404(setup):
    client, with_docs, published = setup
    doc = _doc("failed", user_id=uuid.uuid4())
    with_docs(doc)
    assert client.post(f"/api/documents/{doc.id}/retry").status_code == 404
    assert published == []

"""Route tests for POST /api/documents/upload (DB and RabbitMQ mocked)."""
import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

import fitz
import pytest

from app.api.deps import get_current_user
from app.api.routes import documents as documents_route
from app.db.session import get_db


class FakeDb:
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        obj.id = uuid.uuid4()
        obj.chunk_count = 0
        obj.created_at = datetime.now(UTC)


def _pdf(text: str) -> bytes:
    doc = fitz.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture()
def upload(app, client, monkeypatch):
    db = FakeDb()
    published = []

    async def fake_publish(msg):
        published.append(msg)

    monkeypatch.setattr(documents_route.rabbitmq, "publish", fake_publish)
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=uuid.uuid4())

    def _post(content: bytes, filename="case.pdf", title="My case", **extra):
        return client.post(
            "/api/documents/upload",
            data={"title": title, **extra},
            files={"file": (filename, content, "application/pdf")},
        )

    _post.db = db
    _post.published = published
    yield _post
    app.dependency_overrides.clear()


@pytest.mark.unit
def test_upload_valid_pdf(upload):
    r = upload(_pdf("Some legal text"), case_id="C-1")
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "pending"
    assert body["source_filename"] == "case.pdf"
    assert body["case_id"] == "C-1"
    doc = upload.db.added[0]
    assert "Some legal text" in doc.raw_text
    assert doc.mime_type == "application/pdf"
    assert doc.doc_metadata == {"page_count": 1}
    assert len(upload.published) == 1


@pytest.mark.unit
def test_upload_non_pdf_content(upload):
    r = upload(b"just plain text", filename="fake.pdf")
    assert r.status_code == 415


@pytest.mark.unit
def test_upload_wrong_extension(upload):
    r = upload(_pdf("x"), filename="case.txt")
    assert r.status_code == 415


@pytest.mark.unit
def test_upload_blank_pdf(upload):
    r = upload(_pdf(""))
    assert r.status_code == 422
    assert "No extractable text" in r.json()["detail"]
    assert not upload.db.added


@pytest.mark.unit
def test_upload_too_large(upload):
    r = upload(b"%PDF-" + b"0" * (10 * 1024 * 1024))
    assert r.status_code == 413

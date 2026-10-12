"""Smoke: does the app boot and answer health probes?"""
import pytest
from sqlalchemy.exc import OperationalError

from app.api.routes import health


class _FakeConn:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, *args, **kwargs):
        return None


class _HealthyEngine:
    def connect(self):
        return _FakeConn()


class _DownEngine:
    def connect(self):
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))


@pytest.mark.smoke
def test_health_endpoint(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.smoke
def test_ready_endpoint(client, monkeypatch):
    monkeypatch.setattr(health, "engine", _HealthyEngine())
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ready"}


@pytest.mark.smoke
def test_ready_returns_503_when_db_down(client, monkeypatch):
    monkeypatch.setattr(health, "engine", _DownEngine())
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.json() == {"status": "unavailable"}


@pytest.mark.smoke
def test_openapi_available(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert schema["info"]["title"] == "Case Compass"

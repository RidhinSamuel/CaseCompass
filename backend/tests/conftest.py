"""Shared pytest fixtures.

Uses an in-memory-ish SQLite for unit tests that don't need pgvector.
Functional tests that need pgvector should skip when DATABASE_URL isn't a
reachable Postgres instance (see markers in `pyproject.toml`).
"""
import os

import pytest
from fastapi.testclient import TestClient

# Ensure predictable settings for tests before importing the app.
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from app.main import create_app  # noqa: E402


@pytest.fixture(scope="session")
def app():
    return create_app()


@pytest.fixture()
def client(app):
    with TestClient(app) as c:
        yield c

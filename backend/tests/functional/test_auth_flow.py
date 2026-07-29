"""Functional: register -> login -> /me happy path.

Skipped by default in CI unless a Postgres URL is available, because the
User model relies on the real DB. We mark it functional so the base test
suite (smoke + unit) still runs everywhere.
"""
import os

import pytest


needs_db = pytest.mark.skipif(
    os.getenv("RUN_FUNCTIONAL_TESTS") != "1",
    reason="Set RUN_FUNCTIONAL_TESTS=1 with a live Postgres to run.",
)


@pytest.mark.functional
@needs_db
def test_register_login_me(client):
    email = "alice@example.com"
    r = client.post(
        "/api/auth/register",
        json={"email": email, "password": "supersecret", "full_name": "Alice"},
    )
    assert r.status_code == 201

    r = client.post(
        "/api/auth/login",
        data={"username": email, "password": "supersecret"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == email

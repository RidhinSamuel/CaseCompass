"""Unit tests for password hashing and JWT round-trip."""
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


@pytest.mark.unit
def test_password_hash_verifies():
    h = hash_password("s3cret-pass!")
    assert verify_password("s3cret-pass!", h)
    assert not verify_password("wrong", h)


@pytest.mark.unit
def test_jwt_roundtrip():
    token = create_access_token(subject="user-123")
    assert decode_access_token(token) == "user-123"


@pytest.mark.unit
def test_jwt_bad_token_returns_none():
    assert decode_access_token("not-a-real-token") is None

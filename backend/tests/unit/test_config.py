"""Unit tests for settings loading."""
import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings

STRONG_SECRET = "x" * 48


@pytest.mark.unit
def test_settings_singleton():
    a = get_settings()
    b = get_settings()
    assert a is b


@pytest.mark.unit
def test_settings_defaults():
    s = get_settings()
    assert s.app_name == "Case Compass"
    assert s.embedding_dim == 384
    assert 0 <= s.hybrid_alpha <= 1


@pytest.mark.unit
def test_cors_origins_accepts_comma_separated(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://a.example.com, https://b.example.com")
    s = Settings()
    assert s.cors_origins == ["https://a.example.com", "https://b.example.com"]


@pytest.mark.unit
def test_cors_origins_accepts_json_list(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", '["https://a.example.com"]')
    assert Settings().cors_origins == ["https://a.example.com"]


@pytest.mark.unit
def test_production_rejects_weak_jwt_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("JWT_SECRET_KEY", "change-me-in-prod")
    with pytest.raises(ValidationError, match="JWT_SECRET_KEY"):
        Settings()


@pytest.mark.unit
def test_production_rejects_debug(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("JWT_SECRET_KEY", STRONG_SECRET)
    with pytest.raises(ValidationError, match="DEBUG"):
        Settings()


@pytest.mark.unit
def test_production_rejects_wildcard_cors(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("JWT_SECRET_KEY", STRONG_SECRET)
    monkeypatch.setenv("CORS_ORIGINS", "*")
    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        Settings()


@pytest.mark.unit
def test_production_accepts_safe_config(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("JWT_SECRET_KEY", STRONG_SECRET)
    monkeypatch.setenv("CORS_ORIGINS", "https://casecompass.example.com")
    s = Settings()
    assert s.is_production

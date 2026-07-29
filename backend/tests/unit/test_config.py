"""Unit tests for settings loading."""
import pytest

from app.core.config import get_settings


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

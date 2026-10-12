"""Unit tests for log-safety helpers."""
import pytest

from app.core.logging import redact_url


@pytest.mark.unit
def test_redact_url_hides_password():
    assert redact_url("amqp://user:s3cret@rabbitmq:5672/") == "amqp://user:***@rabbitmq:5672/"


@pytest.mark.unit
def test_redact_url_without_password_is_unchanged():
    assert redact_url("redis://redis:6379/0") == "redis://redis:6379/0"

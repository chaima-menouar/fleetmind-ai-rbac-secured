"""Tests for optional Bedrock Guardrails configuration."""

from app.core.config import settings
from app.services.bedrock_safety import guardrail_config, guardrail_enabled


def test_guardrail_disabled_in_free_tier_only_mode(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "aws_free_tier_only", True)
    monkeypatch.setattr(settings, "bedrock_guardrail_id", "guardrail-demo")
    monkeypatch.setattr(settings, "bedrock_guardrail_version", "2")
    assert guardrail_config() is None
    assert guardrail_enabled() is False


def test_guardrail_configuration_works_outside_free_tier_mode(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "aws_free_tier_only", False)
    monkeypatch.setattr(settings, "bedrock_guardrail_id", "guardrail-demo")
    monkeypatch.setattr(settings, "bedrock_guardrail_version", "2")
    assert guardrail_config() == {
        "guardrailIdentifier": "guardrail-demo",
        "guardrailVersion": "2",
        "trace": "enabled",
    }
    assert guardrail_enabled() is True

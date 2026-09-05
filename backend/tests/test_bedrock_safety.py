"""Tests for optional Bedrock Guardrails configuration."""

from app.services.bedrock_safety import guardrail_config, guardrail_enabled


def test_guardrail_disabled_without_identifier(monkeypatch) -> None:
    monkeypatch.delenv("BEDROCK_GUARDRAIL_ID", raising=False)
    monkeypatch.delenv("BEDROCK_GUARDRAIL_VERSION", raising=False)
    assert guardrail_config() is None
    assert guardrail_enabled() is False


def test_guardrail_configuration_uses_environment(monkeypatch) -> None:
    monkeypatch.setenv("BEDROCK_GUARDRAIL_ID", "guardrail-demo")
    monkeypatch.setenv("BEDROCK_GUARDRAIL_VERSION", "2")
    assert guardrail_config() == {
        "guardrailIdentifier": "guardrail-demo",
        "guardrailVersion": "2",
        "trace": "enabled",
    }
    assert guardrail_enabled() is True

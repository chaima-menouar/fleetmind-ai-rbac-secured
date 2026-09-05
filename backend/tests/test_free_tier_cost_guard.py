"""Regression tests for the AWS free-tier-only AI cost guard."""

from app.core.config import settings
from app.services.llm_gateway import LLMProvider, complete
from app.services.store import store


def test_free_tier_only_forces_demo_llm(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "aws_free_tier_only", True)
    monkeypatch.setattr(settings, "llm_provider", "bedrock")

    answer = complete(
        "Give me the fleet summary",
        system_prompt="You are FleetMind's manager assistant.",
        fleet=store.vehicles(),
        provider=LLMProvider.BEDROCK,
    )

    assert "FleetMind analysis:" in answer
    assert "Current fleet snapshot:" in answer


def test_effective_cloud_providers_are_local_in_free_tier_mode(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "aws_free_tier_only", True)
    monkeypatch.setattr(settings, "llm_provider", "bedrock")
    monkeypatch.setattr(settings, "rag_provider", "bedrock_kb")

    assert settings.effective_llm_provider == "demo"
    assert settings.effective_rag_provider == "local"
    assert settings.bedrock_kb_enabled is False
    assert settings.bedrock_guardrail_enabled is False

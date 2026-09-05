"""Tests for the local/Bedrock retrieval boundary."""

from app.core.config import settings
from app.rag import retrieval


def test_viewer_has_approved_local_context(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "aws_free_tier_only", True)
    monkeypatch.setattr(settings, "rag_provider", "local")
    context = retrieval.retrieve("viewer-assistant", "When is service scheduled?")
    assert context
    assert "fleet-maintenance-policy" in context[0]


def test_bedrock_failure_falls_back_to_local(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "aws_free_tier_only", False)
    monkeypatch.setattr(settings, "rag_provider", "bedrock_kb")
    monkeypatch.setattr(settings, "bedrock_knowledge_base_id", "kb-test")

    def fail_cloud(bot_id: str, query: str, top_k: int) -> list[str]:
        raise RuntimeError("cloud unavailable")

    monkeypatch.setattr(retrieval, "_bedrock_retrieve", fail_cloud)
    context = retrieval.retrieve("technician", "high voltage warning")
    assert context
    assert "ev-safety-guide" in context[0]


def test_free_tier_mode_never_calls_bedrock_retrieval(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "aws_free_tier_only", True)
    monkeypatch.setattr(settings, "rag_provider", "bedrock_kb")
    monkeypatch.setattr(settings, "bedrock_knowledge_base_id", "kb-test")

    def fail_if_called(bot_id: str, query: str, top_k: int) -> list[str]:
        raise AssertionError("Bedrock retrieval must not run in free-tier-only mode")

    monkeypatch.setattr(retrieval, "_bedrock_retrieve", fail_if_called)
    context = retrieval.retrieve("technician", "high voltage warning")
    assert context
    assert "ev-safety-guide" in context[0]


def test_local_top_k_is_bounded(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(settings, "aws_free_tier_only", True)
    monkeypatch.setattr(settings, "rag_provider", "local")
    context = retrieval.retrieve("technician", "maintenance safety warning", top_k=1)
    assert len(context) == 1

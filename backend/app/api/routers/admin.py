"""Admin analytics and deployment-readiness signals."""

from typing import Any

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import require_admin
from app.ml.predictor import get_model_card
from app.models.schemas import CurrentUser, UsageStatsResponse
from app.services.bedrock_safety import guardrail_enabled
from app.services.store import store

router = APIRouter()


@router.get("/usage", response_model=UsageStatsResponse)
def get_usage_stats(_: CurrentUser = Depends(require_admin)) -> UsageStatsResponse:
    return UsageStatsResponse.model_validate(store.usage())


@router.get("/readiness")
def get_readiness(_: CurrentUser = Depends(require_admin)) -> dict[str, Any]:
    """Expose non-secret runtime evidence for the governance dashboard."""
    try:
        model_card = get_model_card()
        model_status = "ready"
        model_version = str(model_card.get("model_version", "unknown"))
    except (FileNotFoundError, RuntimeError):
        model_status = "unavailable"
        model_version = "unavailable"

    persistent_tables = all(
        value
        for value in (
            settings.conversations_table,
            settings.bots_table,
            settings.tasks_table,
        )
    )
    retrieval_mode = (
        "bedrock knowledge base"
        if settings.bedrock_kb_enabled
        else "local approved corpus"
    )
    return {
        "environment": settings.environment,
        "demo_mode": settings.demo_mode,
        "aws_free_tier_only": settings.aws_free_tier_only,
        "cost_guard": (
            "metered generative AI blocked"
            if settings.aws_free_tier_only
            else "standard cloud mode"
        ),
        "llm_provider": settings.effective_llm_provider,
        "rag_provider": settings.effective_rag_provider,
        "retrieval_mode": retrieval_mode,
        "guardrails": "configured" if guardrail_enabled() else "not active",
        "grounding": "deterministic fleet analytics + approved retrieval context",
        "predictive_model_status": model_status,
        "predictive_model_version": model_version,
        "persistence": "dynamodb configured" if persistent_tables else "in-memory demo store",
        "authentication": "demo sessions + cognito capable",
        "cors_origins": len(settings.cors_origins),
    }

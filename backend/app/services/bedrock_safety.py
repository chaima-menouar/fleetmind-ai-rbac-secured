"""Optional Amazon Bedrock Guardrails configuration.

Paid Bedrock safety calls are disabled while AWS_FREE_TIER_ONLY=true. Outside that
mode, an existing Guardrail can be attached without changing chat API contracts.
"""

from __future__ import annotations

from typing import Any

from app.core.config import settings


def guardrail_config() -> dict[str, Any] | None:
    if not settings.bedrock_guardrail_enabled:
        return None
    return {
        "guardrailIdentifier": settings.bedrock_guardrail_id.strip(),
        "guardrailVersion": settings.bedrock_guardrail_version.strip() or "DRAFT",
        "trace": "enabled",
    }


def guardrail_enabled() -> bool:
    return guardrail_config() is not None

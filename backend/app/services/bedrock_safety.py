"""Optional Amazon Bedrock Guardrails configuration.

Guardrails stay disabled unless both environment variables are provided. This keeps
local and free demo paths credentialless while allowing production deployments to
apply an existing Bedrock Guardrail without changing chat API contracts.
"""

from __future__ import annotations

import os
from typing import Any


def guardrail_config() -> dict[str, Any] | None:
    guardrail_id = os.getenv("BEDROCK_GUARDRAIL_ID", "").strip()
    guardrail_version = os.getenv("BEDROCK_GUARDRAIL_VERSION", "DRAFT").strip() or "DRAFT"
    if not guardrail_id:
        return None
    return {
        "guardrailIdentifier": guardrail_id,
        "guardrailVersion": guardrail_version,
        "trace": "enabled",
    }


def guardrail_enabled() -> bool:
    return guardrail_config() is not None

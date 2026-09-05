"""Structured audit events for CloudWatch-compatible application logs."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("fleetmind.audit")


def emit(event: str, **fields: Any) -> None:
    """Write a compact JSON audit event without secrets or message bodies."""
    payload = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event,
        **fields,
    }
    logger.info(json.dumps(payload, separators=(",", ":"), default=str))

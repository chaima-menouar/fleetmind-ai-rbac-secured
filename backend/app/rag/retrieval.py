"""Role-aware retrieval with a credential-free local fallback and Bedrock KB adapter."""

from collections import defaultdict
from re import findall
from threading import RLock
from typing import Any

from app.core.config import settings

_lock = RLock()
_documents: dict[str, list[tuple[str, str]]] = defaultdict(list)
_documents.update(
    {
        "technician": [
            (
                "ev-safety-guide",
                "For high-voltage warnings, isolate the vehicle, stop charging, and have a "
                "qualified technician inspect the battery system before return to service.",
            ),
            (
                "service-playbook",
                "Maintenance triage prioritizes safety faults, braking, steering, thermal "
                "alerts, and vehicles whose scheduled service is overdue.",
            ),
        ],
        "fleet-manager": [
            (
                "fleet-maintenance-policy",
                "Fleet availability is reviewed daily. Vehicles due within seven days are "
                "scheduled by location and operational criticality.",
            )
        ],
        "viewer-assistant": [
            (
                "fleet-maintenance-policy",
                "Fleet availability is reviewed daily. Vehicles due within seven days are "
                "scheduled by location and operational criticality.",
            )
        ],
        "sales-copilot": [
            (
                "fleet-offers",
                "Enterprise proposals should capture fleet size, duty cycle, charging access, "
                "target deployment date, and service-level expectations.",
            )
        ],
    }
)


def add_chunks(bot_id: str, source_id: str, chunks: list[str]) -> None:
    with _lock:
        _documents[bot_id].extend((source_id, chunk) for chunk in chunks)


def _tokens(value: str) -> set[str]:
    return {token for token in findall(r"[a-zA-Z0-9À-ÿ]+", value.lower()) if len(token) > 2}


def _local_retrieve(bot_id: str, query: str, top_k: int) -> list[str]:
    query_tokens = _tokens(query)
    with _lock:
        candidates = list(_documents.get(bot_id, []))
    ranked = sorted(
        candidates,
        key=lambda item: len(query_tokens & _tokens(item[1])),
        reverse=True,
    )
    return [f"[{source_id}] {text}" for source_id, text in ranked[:top_k] if text]


def _bedrock_retrieve(bot_id: str, query: str, top_k: int) -> list[str]:
    import boto3

    client = boto3.client("bedrock-agent-runtime", region_name=settings.aws_region)
    request: dict[str, Any] = {
        "knowledgeBaseId": settings.bedrock_knowledge_base_id,
        "retrievalQuery": {"text": query},
        "retrievalConfiguration": {
            "vectorSearchConfiguration": {
                "numberOfResults": top_k,
                "filter": {"equals": {"key": "assistant_id", "value": bot_id}},
            }
        },
    }
    response = client.retrieve(**request)
    results: list[str] = []
    for index, item in enumerate(response.get("retrievalResults", []), start=1):
        content = item.get("content", {})
        text = str(content.get("text", "")).strip()
        if not text:
            continue
        location = item.get("location", {})
        source = "bedrock-kb"
        for value in location.values():
            if isinstance(value, dict):
                source = str(value.get("uri") or value.get("url") or source)
                break
        results.append(f"[{source}#{index}] {text}")
    return results


def retrieve(bot_id: str, query: str, top_k: int | None = None) -> list[str]:
    """Retrieve approved context without changing the chat API.

    Bedrock Knowledge Bases are opt-in. If the cloud adapter is unavailable at runtime,
    FleetMind falls back to the local approved corpus so the portfolio demo remains usable.
    """
    limit = top_k or settings.rag_top_k
    if settings.bedrock_kb_enabled:
        try:
            return _bedrock_retrieve(bot_id, query, limit)
        except Exception:
            return _local_retrieve(bot_id, query, limit)
    return _local_retrieve(bot_id, query, limit)

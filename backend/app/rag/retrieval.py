"""Small keyword retriever used by the local MVP.

Production deployments can replace this module with OpenSearch Serverless or a
Bedrock Knowledge Base without changing the chat API.
"""

from collections import defaultdict
from re import findall
from threading import RLock

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


def retrieve(bot_id: str, query: str, top_k: int = 5) -> list[str]:
    query_tokens = _tokens(query)
    with _lock:
        candidates = list(_documents.get(bot_id, []))

    ranked = sorted(
        candidates,
        key=lambda item: len(query_tokens & _tokens(item[1])),
        reverse=True,
    )
    return [f"[{source_id}] {text}" for source_id, text in ranked[:top_k] if text]

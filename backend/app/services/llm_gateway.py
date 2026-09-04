"""LLM gateway with a credential-free demo provider and Amazon Bedrock."""

from enum import Enum
from typing import Any

from app.core.config import settings
from app.models.schemas import VehicleResponse


class LLMProvider(str, Enum):
    DEMO = "demo"
    BEDROCK = "bedrock"


def _service_label(days: int) -> str:
    return "due now" if days == 0 else f"due in {days} days"


def _demo_completion(
    prompt: str,
    context: list[str],
    fleet: list[VehicleResponse],
) -> str:
    lowered = prompt.lower()
    if any(word in lowered for word in ("battery", "charge", "range")) and fleet:
        vehicle = min(fleet, key=lambda item: item.battery_percent)
        guidance = (
            f"{vehicle.id} has the lowest battery level at {vehicle.battery_percent}% and a "
            f"health score of {vehicle.health_score}%. Its status is {vehicle.status}, "
            "with service "
            f"{_service_label(vehicle.next_service_days)}.\n\n"
            "Recommended action: review battery alerts and charging history, then run maintenance "
            "triage before returning the vehicle to normal operations."
        )
    elif any(word in lowered for word in ("maintenance", "service", "alert", "fault")) and fleet:
        due = sorted(
            (vehicle for vehicle in fleet if vehicle.next_service_days <= 7),
            key=lambda item: item.next_service_days,
        )
        if due:
            rows = "\n".join(
                f"• {vehicle.id} — {vehicle.model}, health {vehicle.health_score}%, "
                f"{_service_label(vehicle.next_service_days)}, {vehicle.location}."
                for vehicle in due
            )
            guidance = (
                f"{len(due)} vehicles need maintenance within the next 7 days:\n{rows}\n\n"
                f"Prioritize {due[0].id} first, then group the remaining work by location."
            )
        else:
            guidance = "No demo vehicles have service due within the next 7 days."
    elif any(word in lowered for word in ("fleet", "vehicle", "availability")) and fleet:
        active = sum(vehicle.status == "active" for vehicle in fleet)
        exceptions = [vehicle for vehicle in fleet if vehicle.status != "active"]
        exception_ids = ", ".join(vehicle.id for vehicle in exceptions)
        guidance = (
            f"Fleet availability is {active}/{len(fleet)} vehicles. "
            f"The current exceptions are {exception_ids}. "
            "Review the maintenance vehicle first and keep the attention vehicle under observation."
        )
    else:
        guidance = (
            "Clarify the vehicle, time window, and operational goal. I can then turn the request "
            "into a prioritized fleet action plan."
        )

    evidence = f"\n\nKnowledge matched: {len(context)} approved source(s)." if context else ""
    return f"Demo analysis:\n{guidance}{evidence}\n\nThis answer uses fictional demo fleet data."


def complete(
    prompt: str,
    *,
    system_prompt: str,
    context: list[str] | None = None,
    fleet: list[VehicleResponse] | None = None,
    provider: LLMProvider | None = None,
    **_: Any,
) -> str:
    selected = provider or LLMProvider(settings.llm_provider)
    context = context or []
    if selected is LLMProvider.DEMO:
        return _demo_completion(prompt, context, fleet or [])

    import boto3

    client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
    context_block = "\n\n".join(context)
    user_text = prompt if not context_block else f"Context:\n{context_block}\n\nQuestion:\n{prompt}"
    response = client.converse(
        modelId=settings.bedrock_model_id,
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": user_text}]}],
        inferenceConfig={"maxTokens": 700, "temperature": 0.2, "topP": 0.9},
    )
    blocks = response["output"]["message"]["content"]
    return "\n".join(block["text"] for block in blocks if "text" in block).strip()

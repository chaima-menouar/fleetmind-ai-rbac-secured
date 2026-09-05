"""LLM gateway with a credential-free demo provider and Amazon Bedrock."""

from enum import Enum
from typing import Any

from app.core.config import settings
from app.models.schemas import VehicleResponse
from app.services.fleet_intelligence import fleet_kpis, grounding_block, ranked_risks


class LLMProvider(str, Enum):
    DEMO = "demo"
    BEDROCK = "bedrock"


def _service_label(days: int) -> str:
    return "due now" if days == 0 else f"due in {days} days"


def _role_mode(system_prompt: str) -> str:
    lowered = system_prompt.lower()
    if "read-only viewer" in lowered:
        return "viewer"
    if "technician assistant" in lowered:
        return "technician"
    return "manager"


def _mentioned_vehicle(prompt: str, fleet: list[VehicleResponse]) -> VehicleResponse | None:
    lowered = prompt.lower()
    return next((vehicle for vehicle in fleet if vehicle.id.lower() in lowered), None)


def _vehicle_snapshot(vehicle: VehicleResponse, role: str) -> str:
    core = (
        f"{vehicle.id} ({vehicle.model}) is in {vehicle.location}. Status: {vehicle.status}. "
        f"Health: {vehicle.health_score}%. Battery: {vehicle.battery_percent}%. "
        f"Service is {_service_label(vehicle.next_service_days)}."
    )
    if role == "technician":
        return core + " Use these observed fields as the starting point, then verify active alerts and service history before selecting a repair procedure."
    if role == "manager":
        return core + " Use this as an operational signal for availability, maintenance scheduling, and resource prioritization rather than as a remote diagnosis."
    return core + " This is a read-only explanation; operational changes must be handled by an authorized technician or manager."


def _demo_completion(
    prompt: str,
    context: list[str],
    fleet: list[VehicleResponse],
    system_prompt: str,
) -> str:
    lowered = prompt.lower()
    role = _role_mode(system_prompt)
    risks = ranked_risks(fleet)
    top_vehicle = risks[0][0] if risks else None
    mentioned = _mentioned_vehicle(prompt, fleet)

    if mentioned is not None:
        guidance = _vehicle_snapshot(mentioned, role)
    elif any(word in lowered for word in ("battery", "charge", "range")) and fleet:
        vehicle = min(fleet, key=lambda item: item.battery_percent)
        core = (
            f"{vehicle.id} has the lowest battery level at {vehicle.battery_percent}% with a "
            f"health score of {vehicle.health_score}%. Its status is {vehicle.status}, with service "
            f"{_service_label(vehicle.next_service_days)}."
        )
        if role == "technician":
            guidance = core + " Review charging history, battery alerts, thermal events, and service diagnostics before return to service."
        elif role == "manager":
            guidance = core + " Treat it as an availability risk and prioritize capacity coverage while maintenance validates the vehicle."
        else:
            guidance = core + " A technician should review the vehicle before any operational action is taken."
    elif any(word in lowered for word in ("maintenance", "service", "alert", "fault", "risk")) and fleet:
        due = sorted(
            (vehicle for vehicle in fleet if vehicle.next_service_days <= 7),
            key=lambda item: item.next_service_days,
        )
        rows = "\n".join(
            f"• {vehicle.id} — {vehicle.model}, health {vehicle.health_score}%, "
            f"{_service_label(vehicle.next_service_days)}, {vehicle.location}."
            for vehicle in due
        )
        if due:
            guidance = f"{len(due)} vehicles need service within seven days:\n{rows}"
            if role == "technician":
                guidance += f"\n\nStart technical triage with {due[0].id}; verify alerts and service history before choosing a repair path."
            elif role == "manager":
                guidance += f"\n\nPrioritize {due[0].id} first and plan coverage by location to protect fleet availability."
            else:
                guidance += "\n\nThese are read-only status signals; maintenance decisions belong to the technician or manager role."
        else:
            guidance = "No visible vehicles have service due within the next seven days."
    elif any(word in lowered for word in ("fleet", "vehicle", "availability", "kpi", "summary")) and fleet:
        kpis = fleet_kpis(fleet)
        lines = "\n".join(f"• {item.label}: {item.value}" for item in kpis)
        guidance = f"Current fleet snapshot:\n{lines}"
        if role == "manager" and top_vehicle is not None:
            guidance += f"\n\nHighest operational priority: {top_vehicle.id}."
        elif role == "viewer":
            guidance += "\n\nThis is a read-only explanation of the fleet data visible to your account."
    else:
        guidance = (
            "Give me a vehicle ID, fleet KPI, maintenance question, battery concern, or time window. "
            "I will answer using FleetMind's verified fleet data and approved knowledge sources."
        )

    evidence = f"\n\nGrounding: {len(context)} approved knowledge source(s) matched." if context else "\n\nGrounding: verified fleet telemetry only."
    return f"FleetMind analysis:\n{guidance}{evidence}\n\nDemo environment: fleet records are fictional portfolio data."


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
    fleet = fleet or []
    if selected is LLMProvider.DEMO:
        return _demo_completion(prompt, context, fleet, system_prompt)

    import boto3

    client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
    context_parts = [grounding_block(fleet), *context] if fleet else context
    context_block = "\n\n".join(part for part in context_parts if part)
    user_text = prompt if not context_block else f"Verified context:\n{context_block}\n\nQuestion:\n{prompt}"
    response = client.converse(
        modelId=settings.bedrock_model_id,
        system=[
            {
                "text": (
                    system_prompt
                    + " Use verified context for fleet-specific facts. Never invent telemetry, service status, "
                    "or operational events. Clearly say when the supplied evidence is insufficient."
                )
            }
        ],
        messages=[{"role": "user", "content": [{"text": user_text}]}],
        inferenceConfig={"maxTokens": 700, "temperature": 0.2, "topP": 0.9},
    )
    blocks = response["output"]["message"]["content"]
    return "\n".join(block["text"] for block in blocks if "text" in block).strip()

"""Deterministic fleet analytics used to ground FleetMind assistants.

The LLM is never asked to invent fleet KPIs. This module derives operational
signals from the authenticated fleet dataset first, then hands those facts to
the conversational layer for explanation and prioritization.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models.schemas import VehicleResponse


@dataclass(frozen=True)
class FleetInsight:
    label: str
    value: str
    detail: str


def _risk_score(vehicle: VehicleResponse) -> int:
    score = 0
    if vehicle.status == "maintenance":
        score += 50
    elif vehicle.status == "attention":
        score += 25
    if vehicle.health_score < 75:
        score += 25
    elif vehicle.health_score < 85:
        score += 10
    if vehicle.battery_percent < 20:
        score += 20
    elif vehicle.battery_percent < 35:
        score += 10
    if vehicle.next_service_days <= 0:
        score += 25
    elif vehicle.next_service_days <= 7:
        score += 15
    return score


def ranked_risks(fleet: list[VehicleResponse]) -> list[tuple[VehicleResponse, int]]:
    scored = ((vehicle, _risk_score(vehicle)) for vehicle in fleet)
    return sorted(scored, key=lambda item: item[1], reverse=True)


def fleet_kpis(fleet: list[VehicleResponse]) -> list[FleetInsight]:
    if not fleet:
        return []
    active = sum(vehicle.status == "active" for vehicle in fleet)
    due_soon = sum(vehicle.next_service_days <= 7 for vehicle in fleet)
    avg_health = round(sum(vehicle.health_score for vehicle in fleet) / len(fleet))
    avg_battery = round(sum(vehicle.battery_percent for vehicle in fleet) / len(fleet))
    critical = [vehicle.id for vehicle, score in ranked_risks(fleet) if score >= 60]
    return [
        FleetInsight(
            "Availability",
            f"{active}/{len(fleet)}",
            "Vehicles currently marked active.",
        ),
        FleetInsight(
            "Average health",
            f"{avg_health}%",
            "Mean health score across the visible fleet.",
        ),
        FleetInsight(
            "Average battery",
            f"{avg_battery}%",
            "Mean battery state across the visible fleet.",
        ),
        FleetInsight(
            "Service due <=7d",
            str(due_soon),
            "Vehicles requiring service within seven days.",
        ),
        FleetInsight(
            "Critical risk",
            ", ".join(critical) if critical else "None",
            "Vehicles with the highest composite operational risk.",
        ),
    ]


def grounding_block(fleet: list[VehicleResponse]) -> str:
    """Return compact, machine-generated facts for an LLM prompt."""
    kpis = fleet_kpis(fleet)
    risks = ranked_risks(fleet)[:3]
    lines = ["Verified FleetMind analytics:"]
    lines.extend(f"- {item.label}: {item.value} ({item.detail})" for item in kpis)
    if risks:
        lines.append("- Risk ranking:")
        for vehicle, score in risks:
            lines.append(
                f"  - {vehicle.id}: risk={score}, status={vehicle.status}, "
                f"health={vehicle.health_score}%, battery={vehicle.battery_percent}%, "
                f"service_days={vehicle.next_service_days}, location={vehicle.location}"
            )
    return "\n".join(lines)

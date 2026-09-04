"""Deterministic demo connectors used by the maintenance agent."""

from uuid import uuid4

from app.services.store import store


def get_vehicle_telemetry(vehicle_id: str) -> dict:
    vehicle = next((item for item in store.vehicles() if item.id == vehicle_id), None)
    if vehicle is None:
        raise ValueError(f"Vehicle '{vehicle_id}' was not found.")
    return {
        "vehicle_id": vehicle.id,
        "battery_percent": vehicle.battery_percent,
        "health_score": vehicle.health_score,
        "status": vehicle.status,
        "next_service_days": vehicle.next_service_days,
        "source": "demo-telemetry",
    }


def create_maintenance_ticket(vehicle_id: str, issue: str) -> dict:
    return {
        "ticket_id": f"MT-{uuid4().hex[:8].upper()}",
        "vehicle_id": vehicle_id,
        "issue": issue,
        "status": "open",
        "source": "demo-ticketing",
    }

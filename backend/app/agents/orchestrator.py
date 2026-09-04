"""Multi-step maintenance agent orchestration."""

from datetime import UTC, datetime
from uuid import uuid4

from app.agents.connectors import create_maintenance_ticket, get_vehicle_telemetry
from app.models.schemas import AgentTaskRequest, AgentTaskResponse, TaskStatus
from app.services.store import store


def run_task(request: AgentTaskRequest, owner_id: str) -> AgentTaskResponse:
    if request.task_type != "maintenance_triage":
        raise ValueError("The MVP currently supports only 'maintenance_triage'.")

    telemetry = get_vehicle_telemetry(request.vehicle_id)
    requires_ticket = (
        telemetry["health_score"] < 75
        or telemetry["next_service_days"] <= 3
        or telemetry["status"] in {"attention", "maintenance"}
    )
    issue = request.issue or (
        f"Automated triage: health {telemetry['health_score']}%, status "
        f"{telemetry['status']}, service due in {telemetry['next_service_days']} day(s)."
    )
    ticket = create_maintenance_ticket(request.vehicle_id, issue) if requires_ticket else None
    summary = (
        "Maintenance ticket created and assigned for review."
        if ticket
        else "Telemetry checked; no immediate maintenance ticket is required."
    )
    task = AgentTaskResponse(
        task_id=f"TASK-{uuid4().hex[:10].upper()}",
        status=TaskStatus.COMPLETED,
        summary=summary,
        output={"telemetry": telemetry, "ticket": ticket, "steps_completed": 2},
        created_at=datetime.now(UTC),
    )
    return store.save_task(task, owner_id)

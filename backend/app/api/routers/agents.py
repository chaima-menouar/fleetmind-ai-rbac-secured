"""Endpoints for observable multi-step agent tasks."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.orchestrator import run_task
from app.core.security import require_operator
from app.models.schemas import AgentTaskRequest, AgentTaskResponse, CurrentUser, UserRole
from app.services.audit import emit
from app.services.store import store

router = APIRouter()


@router.post("/run", response_model=AgentTaskResponse)
def run_agent_task(
    payload: AgentTaskRequest,
    user: CurrentUser = Depends(require_operator),
) -> AgentTaskResponse:
    try:
        task = run_task(payload, user.id)
    except ValueError as exc:
        emit(
            "agent_run_rejected",
            user_id=user.id,
            role=user.role.value,
            task_type=payload.task_type,
            vehicle_id=payload.vehicle_id,
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    emit(
        "agent_run_completed",
        user_id=user.id,
        role=user.role.value,
        task_type=payload.task_type,
        vehicle_id=payload.vehicle_id,
        task_id=task.task_id,
        task_status=task.status,
    )
    return task


@router.get("/tasks/{task_id}", response_model=AgentTaskResponse)
def get_task_status(
    task_id: str,
    user: CurrentUser = Depends(require_operator),
) -> AgentTaskResponse:
    try:
        task = store.get_task(task_id, user.id, allow_all=user.role is UserRole.ADMIN)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return task

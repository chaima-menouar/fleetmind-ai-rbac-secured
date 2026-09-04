"""Fleet overview endpoints."""

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.schemas import CurrentUser, FleetSummaryResponse
from app.services.store import store

router = APIRouter()


@router.get("/summary", response_model=FleetSummaryResponse)
def fleet_summary(_: CurrentUser = Depends(get_current_user)) -> FleetSummaryResponse:
    vehicles = store.vehicles()
    active = sum(vehicle.status == "active" for vehicle in vehicles)
    maintenance_due = sum(vehicle.next_service_days <= 7 for vehicle in vehicles)
    average_health = round(sum(vehicle.health_score for vehicle in vehicles) / len(vehicles), 1)
    return FleetSummaryResponse(
        total_vehicles=len(vehicles),
        active_vehicles=active,
        maintenance_due=maintenance_due,
        average_health=average_health,
        vehicles=vehicles,
    )

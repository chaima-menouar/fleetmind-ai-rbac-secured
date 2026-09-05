"""Fleet overview and deterministic intelligence endpoints."""

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.schemas import (
    CurrentUser,
    FleetIntelligenceResponse,
    FleetKpiResponse,
    FleetRiskResponse,
    FleetSummaryResponse,
)
from app.services.fleet_intelligence import fleet_kpis, ranked_risks
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


@router.get("/intelligence", response_model=FleetIntelligenceResponse)
def fleet_intelligence(_: CurrentUser = Depends(get_current_user)) -> FleetIntelligenceResponse:
    vehicles = store.vehicles()
    kpis = [FleetKpiResponse(label=item.label, value=item.value, detail=item.detail) for item in fleet_kpis(vehicles)]
    ranked = ranked_risks(vehicles)
    risks = [
        FleetRiskResponse(
            vehicle_id=vehicle.id,
            model=vehicle.model,
            location=vehicle.location,
            risk_score=score,
            status=vehicle.status,
            health_score=vehicle.health_score,
            battery_percent=vehicle.battery_percent,
            next_service_days=vehicle.next_service_days,
        )
        for vehicle, score in ranked
    ]
    return FleetIntelligenceResponse(
        kpis=kpis,
        risk_ranking=risks,
        critical_vehicle_ids=[vehicle.id for vehicle, score in ranked if score >= 60],
    )

"""Admin analytics for the MVP."""

from fastapi import APIRouter, Depends

from app.core.security import require_admin
from app.models.schemas import CurrentUser, UsageStatsResponse
from app.services.store import store

router = APIRouter()


@router.get("/usage", response_model=UsageStatsResponse)
def get_usage_stats(_: CurrentUser = Depends(require_admin)) -> UsageStatsResponse:
    return UsageStatsResponse.model_validate(store.usage())

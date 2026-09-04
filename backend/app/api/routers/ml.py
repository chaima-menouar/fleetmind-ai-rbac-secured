"""Predictive-maintenance model transparency and inference endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user, require_operator
from app.ml.predictor import get_model_card, list_evaluation_samples, predict_evaluation_sample
from app.models.schemas import (
    CurrentUser,
    ModelCardResponse,
    PredictionRequest,
    PredictionResponse,
    PredictionSampleResponse,
)

router = APIRouter()


def artifacts_unavailable() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="The predictive-maintenance model artifacts are unavailable.",
    )


@router.get("/model-card", response_model=ModelCardResponse)
def model_card(_: CurrentUser = Depends(get_current_user)) -> ModelCardResponse:
    try:
        return ModelCardResponse.model_validate(get_model_card())
    except (FileNotFoundError, RuntimeError) as exc:
        raise artifacts_unavailable() from exc


@router.get("/samples", response_model=list[PredictionSampleResponse])
def prediction_samples(
    _: CurrentUser = Depends(require_operator),
) -> list[PredictionSampleResponse]:
    try:
        return [PredictionSampleResponse.model_validate(item) for item in list_evaluation_samples()]
    except (FileNotFoundError, RuntimeError) as exc:
        raise artifacts_unavailable() from exc


@router.post("/predict", response_model=PredictionResponse)
def predict(
    request: PredictionRequest,
    _: CurrentUser = Depends(require_operator),
) -> PredictionResponse:
    try:
        prediction = predict_evaluation_sample(request.sample_id)
    except (FileNotFoundError, RuntimeError) as exc:
        raise artifacts_unavailable() from exc
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation sample not found.",
        ) from exc
    return PredictionResponse.model_validate(prediction)

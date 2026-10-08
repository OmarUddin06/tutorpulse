"""FastAPI routes for governed TutorPulse inference."""

from __future__ import annotations

import logging
from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from app.inference_schemas import (
    ModelHealthResponse,
    SupportRiskRequest,
    SupportRiskResponse,
)
from app.model_service import (
    ModelPredictionError,
    ModelRuntimeState,
    ModelUnavailableError,
    model_health_response,
    predict_support_risk,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Model inference"],
)


def get_model_runtime(
    request: Request,
) -> ModelRuntimeState:
    """Return the model state created during startup."""

    runtime = getattr(
        request.app.state,
        "model_runtime",
        None,
    )

    if not isinstance(
        runtime,
        ModelRuntimeState,
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model inference is unavailable",
        )

    return runtime


ModelRuntimeDependency = Annotated[
    ModelRuntimeState,
    Depends(get_model_runtime),
]


@router.get(
    "/model/health",
    response_model=ModelHealthResponse,
    summary="Check Model Health",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Model inference is unavailable",
        },
    },
)
def check_model_health(
    runtime: ModelRuntimeDependency,
) -> ModelHealthResponse:
    """Confirm that a validated model is ready."""

    try:
        return model_health_response(runtime)
    except ModelUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model inference is unavailable",
        ) from error


@router.post(
    "/predictions/support-risk",
    response_model=SupportRiskResponse,
    summary="Predict Support Risk",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Model inference is unavailable",
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Model prediction failed",
        },
    },
)
def predict_support_risk_route(
    payload: SupportRiskRequest,
    runtime: ModelRuntimeDependency,
) -> SupportRiskResponse:
    """Return one governed support-risk prediction."""

    request_id = str(uuid4())
    started_at = perf_counter()

    try:
        response = predict_support_risk(
            runtime,
            payload,
        )
    except ModelUnavailableError as error:
        duration_ms = (
            perf_counter() - started_at
        ) * 1000

        logger.warning(
            "prediction_unavailable "
            "request_id=%s duration_ms=%.3f",
            request_id,
            duration_ms,
        )

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model inference is unavailable",
        ) from error
    except ModelPredictionError as error:
        duration_ms = (
            perf_counter() - started_at
        ) * 1000

        logger.error(
            "prediction_failed "
            "request_id=%s error_category=%s "
            "duration_ms=%.3f",
            request_id,
            type(error).__name__,
            duration_ms,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Model prediction failed",
        ) from error

    duration_ms = (
        perf_counter() - started_at
    ) * 1000

    logger.info(
        "prediction_completed "
        "request_id=%s model_name=%s "
        "artifact_schema_version=%s "
        "decision_threshold=%.2f "
        "predicted_needs_support=%s "
        "duration_ms=%.3f",
        request_id,
        response.model_name,
        response.artifact_schema_version,
        response.decision_threshold,
        response.predicted_needs_support,
        duration_ms,
    )

    return response
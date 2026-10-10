"""TutorPulse FastAPI application."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI,
    Request,
    status,
)
from fastapi.responses import (
    JSONResponse,
    Response,
)

from app.config import settings
from app.database import engine
from app.demo_mode import enforce_demo_read_only
from app.model_service import (
    ModelRuntimeState,
    load_model_runtime,
)
from app.readiness import (
    ReadinessResponse,
    build_readiness_response,
    database_is_ready,
)
from app.routers.assessment_results import (
    router as assessment_results_router,
)
from app.routers.assessments import (
    router as assessments_router,
)
from app.routers.interventions import (
    router as interventions_router,
)
from app.routers.learners import (
    router as learners_router,
)
from app.routers.predictions import (
    router as predictions_router,
)
from app.routers.topics import (
    router as topics_router,
)


@asynccontextmanager
async def lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:
    """Load the trusted model once during startup."""

    application.state.model_runtime = (
        load_model_runtime(
            settings.model_artifact_directory
        )
    )

    yield


app = FastAPI(
    title="TutorPulse API",
    description=(
        "API for recording anonymised learner outcomes, "
        "managing tutor interventions and serving governed "
        "support-risk predictions."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

app.middleware("http")(
    enforce_demo_read_only
)

app.include_router(interventions_router)
app.include_router(assessment_results_router)
app.include_router(assessments_router)
app.include_router(learners_router)
app.include_router(topics_router)
app.include_router(predictions_router)


@app.get(
    "/health",
    tags=["Health"],
)
def health_check() -> dict[str, str]:
    """Confirm that the TutorPulse API is running."""

    return {"status": "ok"}


@app.get(
    "/ready",
    tags=["Health"],
    response_model=ReadinessResponse,
    summary="Check Deployment Readiness",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": (
                "One or more required dependencies "
                "are unavailable"
            ),
        },
    },
)
def readiness_check(
    request: Request,
) -> Response:
    """Check database connectivity and model readiness."""

    database_ready = database_is_ready(
        engine
    )

    runtime = getattr(
        request.app.state,
        "model_runtime",
        None,
    )

    model_ready = (
        isinstance(
            runtime,
            ModelRuntimeState,
        )
        and runtime.is_ready
    )

    readiness = build_readiness_response(
        database_ready=database_ready,
        model_ready=model_ready,
    )

    response_status = (
        status.HTTP_200_OK
        if readiness.status == "ready"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(
        status_code=response_status,
        content=readiness.model_dump(),
    )
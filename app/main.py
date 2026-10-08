"""TutorPulse FastAPI application."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.model_service import load_model_runtime
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
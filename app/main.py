from fastapi import FastAPI

from app.routers.learners import router as learners_router
from app.routers.topics import router as topics_router


app = FastAPI(
    title="TutorPulse API",
    description=(
        "API for recording anonymised learner outcomes "
        "and managing tutor interventions."
    ),
    version="0.1.0",
)

app.include_router(learners_router)
app.include_router(topics_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Confirm that the TutorPulse API is running."""
    return {"status": "ok"}
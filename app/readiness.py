"""Deployment-readiness checks for TutorPulse."""

from typing import Literal

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


class ReadinessResponse(BaseModel):
    """Public deployment-readiness response."""

    status: Literal["ready", "not_ready"]
    database: Literal["ready", "unavailable"]
    model: Literal["ready", "unavailable"]


def database_is_ready(
    database_engine: Engine,
) -> bool:
    """Check PostgreSQL without exposing connection details."""

    try:
        with database_engine.connect() as connection:
            result = connection.execute(
                text("SELECT 1")
            ).scalar_one()
    except (SQLAlchemyError, OSError):
        return False

    return result == 1


def build_readiness_response(
    *,
    database_ready: bool,
    model_ready: bool,
) -> ReadinessResponse:
    """Build a safe combined readiness response."""

    all_dependencies_ready = (
        database_ready and model_ready
    )

    return ReadinessResponse(
        status=(
            "ready"
            if all_dependencies_ready
            else "not_ready"
        ),
        database=(
            "ready"
            if database_ready
            else "unavailable"
        ),
        model=(
            "ready"
            if model_ready
            else "unavailable"
        ),
    )
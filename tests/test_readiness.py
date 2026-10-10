"""Tests for TutorPulse deployment readiness."""

from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.model_service import ModelRuntimeState
from app.readiness import database_is_ready


def make_ready_model_state() -> ModelRuntimeState:
    """Return a controlled ready model state."""

    return ModelRuntimeState(
        bundle=MagicMock(),
    )


def make_unavailable_model_state() -> ModelRuntimeState:
    """Return a controlled unavailable model state."""

    return ModelRuntimeState(
        bundle=None,
        load_error_category="ModelArtifactError",
    )


@contextmanager
def readiness_client(
    *,
    model_state: ModelRuntimeState,
    database_ready: bool,
) -> Iterator[TestClient]:
    """Start TutorPulse with controlled dependencies."""

    with (
        patch(
            "app.main.load_model_runtime",
            return_value=model_state,
        ),
        patch(
            "app.main.database_is_ready",
            return_value=database_ready,
        ),
    ):
        with TestClient(app) as client:
            yield client


def test_database_probe_executes_select_one() -> None:
    database_engine = MagicMock()
    connection = (
        database_engine.connect
        .return_value.__enter__
        .return_value
    )
    connection.execute.return_value.scalar_one.return_value = 1

    assert database_is_ready(
        database_engine
    ) is True

    statement = connection.execute.call_args.args[0]

    assert str(statement) == "SELECT 1"


def test_database_probe_handles_connection_failure() -> None:
    database_engine = MagicMock()
    database_engine.connect.side_effect = (
        SQLAlchemyError(
            "Controlled connection failure"
        )
    )

    assert database_is_ready(
        database_engine
    ) is False


def test_readiness_returns_200_when_dependencies_ready() -> None:
    with readiness_client(
        model_state=make_ready_model_state(),
        database_ready=True,
    ) as client:
        response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "ready",
        "model": "ready",
    }


def test_readiness_returns_503_when_database_unavailable() -> None:
    with readiness_client(
        model_state=make_ready_model_state(),
        database_ready=False,
    ) as client:
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "database": "unavailable",
        "model": "ready",
    }


def test_readiness_returns_503_when_model_unavailable() -> None:
    with readiness_client(
        model_state=make_unavailable_model_state(),
        database_ready=True,
    ) as client:
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready",
        "database": "ready",
        "model": "unavailable",
    }
from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import app
from app.models import Intervention, Learner


CREATED_AT = datetime(
    2026,
    10,
    5,
    12,
    0,
    tzinfo=timezone.utc,
)

COMPLETED_AT = datetime(
    2026,
    10,
    5,
    15,
    0,
    tzinfo=timezone.utc,
)


def make_intervention(
    intervention_id: int = 1,
    status: str = "planned",
    completed_at: datetime | None = None,
) -> Intervention:
    intervention = Intervention(
        learner_id=1,
        topic_id=1,
        summary="Provide weekly fractions practice.",
        status=status,
        completed_at=completed_at,
    )
    intervention.id = intervention_id
    intervention.created_at = CREATED_AT

    return intervention


@pytest.fixture
def database_session() -> MagicMock:
    return MagicMock(spec=Session)


@pytest.fixture
def client(
    database_session: MagicMock,
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[MagicMock, None, None]:
        yield database_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_intervention_returns_created_intervention(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.get.side_effect = lambda model, record_id: object()

    def add_generated_values(intervention: Intervention) -> None:
        intervention.id = 4
        intervention.created_at = CREATED_AT

    database_session.refresh.side_effect = add_generated_values

    response = client.post(
        "/interventions",
        json={
            "learner_id": 1,
            "topic_id": 1,
            "summary": "  Provide weekly fractions practice.  ",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 4
    assert response.json()["status"] == "planned"
    assert response.json()["summary"] == (
        "Provide weekly fractions practice."
    )


def test_missing_learner_returns_404(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.get.side_effect = (
        lambda model, record_id: None if model is Learner else object()
    )

    response = client.post(
        "/interventions",
        json={
            "learner_id": 999,
            "topic_id": 1,
            "summary": "Provide support.",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Learner not found"}


def test_blank_summary_is_rejected(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    response = client.post(
        "/interventions",
        json={
            "learner_id": 1,
            "summary": "   ",
        },
    )

    assert response.status_code == 422
    database_session.add.assert_not_called()


def test_list_interventions_returns_interventions(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.scalars.return_value.all.return_value = [
        make_intervention(1),
        make_intervention(2, "completed", COMPLETED_AT),
    ]

    response = client.get("/interventions")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_missing_intervention_returns_404(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.get.return_value = None

    response = client.get("/interventions/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Intervention not found"}


def test_complete_intervention_with_timestamp(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    intervention = make_intervention()
    database_session.get.return_value = intervention

    response = client.patch(
        "/interventions/1",
        json={
            "status": "completed",
            "completed_at": "2026-10-05T15:00:00Z",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert intervention.completed_at is not None
    database_session.commit.assert_called_once()


def test_active_intervention_cannot_keep_completion_time(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    intervention = make_intervention(
        status="completed",
        completed_at=COMPLETED_AT,
    )
    database_session.get.return_value = intervention

    response = client.patch(
        "/interventions/1",
        json={"status": "active"},
    )

    assert response.status_code == 422
    database_session.commit.assert_not_called()


def test_topic_can_be_cleared(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    intervention = make_intervention()
    database_session.get.return_value = intervention

    response = client.patch(
        "/interventions/1",
        json={"topic_id": None},
    )

    assert response.status_code == 200
    assert response.json()["topic_id"] is None
    assert intervention.topic_id is None


def test_delete_intervention_returns_204(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    intervention = make_intervention()
    database_session.get.return_value = intervention

    response = client.delete("/interventions/1")

    assert response.status_code == 204
    assert response.content == b""
    database_session.delete.assert_called_once_with(intervention)
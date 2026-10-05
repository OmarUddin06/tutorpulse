from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import app
from app.models import Learner


CREATED_AT = datetime(
    2026,
    10,
    5,
    12,
    0,
    tzinfo=timezone.utc,
)


def make_learner(
    learner_id: int = 1,
    display_name: str = "Learner 001",
) -> Learner:
    """Create a learner object for use in unit tests."""

    learner = Learner(display_name=display_name)
    learner.id = learner_id
    learner.created_at = CREATED_AT

    return learner


@pytest.fixture
def database_session() -> MagicMock:
    """Provide a mock instead of a real PostgreSQL session."""

    return MagicMock(spec=Session)


@pytest.fixture
def client(
    database_session: MagicMock,
) -> Generator[TestClient, None, None]:
    """Create an API client using the mock database session."""

    def override_get_db() -> Generator[MagicMock, None, None]:
        yield database_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_learner_returns_created_learner(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    def add_generated_values(learner: Learner) -> None:
        learner.id = 5
        learner.created_at = CREATED_AT

    database_session.refresh.side_effect = add_generated_values

    response = client.post(
        "/learners",
        json={"display_name": "  Learner 005  "},
    )

    assert response.status_code == 201
    assert response.json()["id"] == 5
    assert response.json()["display_name"] == "Learner 005"

    added_learner = database_session.add.call_args.args[0]
    assert added_learner.display_name == "Learner 005"

    database_session.commit.assert_called_once()
    database_session.refresh.assert_called_once_with(added_learner)


def test_list_learners_returns_ordered_results(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.scalars.return_value.all.return_value = [
        make_learner(1, "Learner 001"),
        make_learner(2, "Learner 002"),
    ]

    response = client.get("/learners")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [1, 2]
    assert [item["display_name"] for item in response.json()] == [
        "Learner 001",
        "Learner 002",
    ]


def test_get_existing_learner_returns_learner(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    learner = make_learner()
    database_session.get.return_value = learner

    response = client.get("/learners/1")

    assert response.status_code == 200
    assert response.json()["display_name"] == "Learner 001"
    database_session.get.assert_called_once_with(Learner, 1)


def test_get_missing_learner_returns_404(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.get.return_value = None

    response = client.get("/learners/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Learner not found"}


def test_non_positive_learner_id_is_rejected(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    response = client.get("/learners/0")

    assert response.status_code == 422
    database_session.get.assert_not_called()


def test_blank_learner_name_is_rejected_by_api(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    response = client.post(
        "/learners",
        json={"display_name": "   "},
    )

    assert response.status_code == 422
    database_session.add.assert_not_called()
    database_session.commit.assert_not_called()


def test_update_existing_learner_returns_updated_learner(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    learner = make_learner()
    database_session.get.return_value = learner

    response = client.patch(
        "/learners/1",
        json={"display_name": "Updated Learner"},
    )

    assert response.status_code == 200
    assert response.json()["display_name"] == "Updated Learner"
    assert learner.display_name == "Updated Learner"

    database_session.commit.assert_called_once()
    database_session.refresh.assert_called_once_with(learner)


def test_delete_existing_learner_returns_204(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    learner = make_learner()
    database_session.get.return_value = learner

    response = client.delete("/learners/1")

    assert response.status_code == 204
    assert response.content == b""

    database_session.delete.assert_called_once_with(learner)
    database_session.commit.assert_called_once()
from collections.abc import Generator
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import app
from app.models import Assessment, AssessmentResult, Learner, Topic


CREATED_AT = datetime(
    2026,
    10,
    5,
    12,
    0,
    tzinfo=timezone.utc,
)


def make_result(
    result_id: int = 1,
    score: Decimal = Decimal("15.00"),
    maximum_score: Decimal = Decimal("20.00"),
) -> AssessmentResult:
    result = AssessmentResult(
        learner_id=1,
        assessment_id=1,
        topic_id=1,
        score=score,
        maximum_score=maximum_score,
    )
    result.id = result_id
    result.created_at = CREATED_AT

    return result


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


def test_create_result_returns_created_result(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.get.side_effect = lambda model, record_id: object()

    def add_generated_values(result: AssessmentResult) -> None:
        result.id = 17
        result.created_at = CREATED_AT

    database_session.refresh.side_effect = add_generated_values

    response = client.post(
        "/assessment-results",
        json={
            "learner_id": 1,
            "assessment_id": 1,
            "topic_id": 1,
            "score": "15.00",
            "maximum_score": "20.00",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 17
    assert Decimal(response.json()["score"]) == Decimal("15.00")
    database_session.commit.assert_called_once()


def test_missing_learner_returns_404(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    def find_record(model: type, record_id: int) -> object | None:
        if model is Learner:
            return None

        return object()

    database_session.get.side_effect = find_record

    response = client.post(
        "/assessment-results",
        json={
            "learner_id": 999,
            "assessment_id": 1,
            "topic_id": 1,
            "score": "15.00",
            "maximum_score": "20.00",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Learner not found"}


def test_list_results_returns_results(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.scalars.return_value.all.return_value = [
        make_result(1),
        make_result(2, Decimal("18.00")),
    ]

    response = client.get("/assessment-results")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_missing_result_returns_404(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.get.return_value = None

    response = client.get("/assessment-results/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Assessment result not found"
    }


def test_score_above_maximum_is_rejected_by_api(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    response = client.post(
        "/assessment-results",
        json={
            "learner_id": 1,
            "assessment_id": 1,
            "topic_id": 1,
            "score": "25.00",
            "maximum_score": "20.00",
        },
    )

    assert response.status_code == 422
    database_session.add.assert_not_called()


def test_duplicate_result_returns_409(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.get.side_effect = lambda model, record_id: object()
    database_session.commit.side_effect = IntegrityError(
        None,
        None,
        Exception("duplicate result"),
    )

    response = client.post(
        "/assessment-results",
        json={
            "learner_id": 1,
            "assessment_id": 1,
            "topic_id": 1,
            "score": "15.00",
            "maximum_score": "20.00",
        },
    )

    assert response.status_code == 409
    database_session.rollback.assert_called_once()


def test_partial_update_cannot_exceed_existing_maximum(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.get.return_value = make_result()

    response = client.patch(
        "/assessment-results/1",
        json={"score": "25.00"},
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "score must not exceed maximum_score"
    }
    database_session.commit.assert_not_called()


def test_valid_result_update_returns_updated_result(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    result = make_result()
    database_session.get.return_value = result

    response = client.patch(
        "/assessment-results/1",
        json={
            "score": "18.00",
            "maximum_score": "25.00",
        },
    )

    assert response.status_code == 200
    assert Decimal(response.json()["score"]) == Decimal("18.00")
    assert result.maximum_score == Decimal("25.00")
    database_session.commit.assert_called_once()


def test_delete_result_returns_204(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    result = make_result()
    database_session.get.return_value = result

    response = client.delete("/assessment-results/1")

    assert response.status_code == 204
    assert response.content == b""
    database_session.delete.assert_called_once_with(result)
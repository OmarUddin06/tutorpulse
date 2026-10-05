from collections.abc import Generator
from datetime import date, datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import app
from app.models import Assessment


CREATED_AT = datetime(
    2026,
    10,
    5,
    12,
    0,
    tzinfo=timezone.utc,
)


def make_assessment(
    assessment_id: int = 1,
    title: str = "Autumn Diagnostic",
    assessment_date: date = date(2026, 9, 15),
) -> Assessment:
    assessment = Assessment(
        title=title,
        assessment_date=assessment_date,
    )
    assessment.id = assessment_id
    assessment.created_at = CREATED_AT

    return assessment


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


def test_create_assessment_returns_created_assessment(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    def add_generated_values(assessment: Assessment) -> None:
        assessment.id = 3
        assessment.created_at = CREATED_AT

    database_session.refresh.side_effect = add_generated_values

    response = client.post(
        "/assessments",
        json={
            "title": "  Winter Review  ",
            "assessment_date": "2026-12-10",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 3
    assert response.json()["title"] == "Winter Review"
    assert response.json()["assessment_date"] == "2026-12-10"
    database_session.commit.assert_called_once()


def test_list_assessments_returns_assessments(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.scalars.return_value.all.return_value = [
        make_assessment(),
        make_assessment(
            2,
            "Fractions Checkpoint",
            date(2026, 9, 29),
        ),
    ]

    response = client.get("/assessments")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Autumn Diagnostic"


def test_missing_assessment_returns_404(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.get.return_value = None

    response = client.get("/assessments/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Assessment not found"}


def test_blank_assessment_title_is_rejected_by_api(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    response = client.post(
        "/assessments",
        json={
            "title": "   ",
            "assessment_date": "2026-12-10",
        },
    )

    assert response.status_code == 422
    database_session.add.assert_not_called()


def test_empty_assessment_update_is_rejected(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    response = client.patch(
        "/assessments/1",
        json={},
    )

    assert response.status_code == 422
    database_session.get.assert_not_called()


def test_update_assessment_returns_updated_assessment(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    assessment = make_assessment()
    database_session.get.return_value = assessment

    response = client.patch(
        "/assessments/1",
        json={
            "title": "Updated Diagnostic",
            "assessment_date": "2026-10-01",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Diagnostic"
    assert response.json()["assessment_date"] == "2026-10-01"
    database_session.commit.assert_called_once()


def test_delete_assessment_returns_204(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    assessment = make_assessment()
    database_session.get.return_value = assessment

    response = client.delete("/assessments/1")

    assert response.status_code == 204
    assert response.content == b""
    database_session.delete.assert_called_once_with(assessment)
    database_session.commit.assert_called_once()
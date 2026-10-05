from collections.abc import Generator
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.main import app
from app.models import Topic


CREATED_AT = datetime(
    2026,
    10,
    5,
    12,
    0,
    tzinfo=timezone.utc,
)


def make_topic(
    topic_id: int = 1,
    name: str = "Algebra",
    description: str | None = "Algebra skills",
) -> Topic:
    topic = Topic(name=name, description=description)
    topic.id = topic_id
    topic.created_at = CREATED_AT

    return topic


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


def test_create_topic_returns_created_topic(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    def add_generated_values(topic: Topic) -> None:
        topic.id = 4
        topic.created_at = CREATED_AT

    database_session.refresh.side_effect = add_generated_values

    response = client.post(
        "/topics",
        json={
            "name": "  Statistics  ",
            "description": "Introductory statistics",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 4
    assert response.json()["name"] == "Statistics"
    database_session.commit.assert_called_once()


def test_list_topics_returns_topics(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.scalars.return_value.all.return_value = [
        make_topic(1, "Algebra"),
        make_topic(2, "Fractions"),
    ]

    response = client.get("/topics")

    assert response.status_code == 200
    assert [topic["name"] for topic in response.json()] == [
        "Algebra",
        "Fractions",
    ]


def test_missing_topic_returns_404(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.get.return_value = None

    response = client.get("/topics/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Topic not found"}


def test_blank_topic_name_is_rejected_by_api(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    response = client.post(
        "/topics",
        json={"name": "   "},
    )

    assert response.status_code == 422
    database_session.add.assert_not_called()


def test_duplicate_topic_returns_409(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    database_session.commit.side_effect = IntegrityError(
        None,
        None,
        Exception("duplicate topic"),
    )

    response = client.post(
        "/topics",
        json={"name": "Algebra"},
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "A topic with this name already exists"
    }
    database_session.rollback.assert_called_once()


def test_update_topic_returns_updated_topic(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    topic = make_topic()
    database_session.get.return_value = topic

    response = client.patch(
        "/topics/1",
        json={
            "name": "Advanced Algebra",
            "description": "Updated description",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Advanced Algebra"
    assert topic.description == "Updated description"
    database_session.commit.assert_called_once()


def test_delete_topic_returns_204(
    client: TestClient,
    database_session: MagicMock,
) -> None:
    topic = make_topic()
    database_session.get.return_value = topic

    response = client.delete("/topics/1")

    assert response.status_code == 204
    assert response.content == b""
    database_session.delete.assert_called_once_with(topic)
    database_session.commit.assert_called_once()
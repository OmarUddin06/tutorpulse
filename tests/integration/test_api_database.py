from decimal import Decimal

import pytest
from fastapi.testclient import TestClient


pytestmark = pytest.mark.integration


def create_result_dependencies(
    api_client: TestClient,
    suffix: str,
) -> dict[str, int]:
    """Create the learner, assessment and topic required by a result."""

    learner_response = api_client.post(
        "/learners",
        json={"display_name": f"API Integration Learner {suffix}"},
    )
    assessment_response = api_client.post(
        "/assessments",
        json={
            "title": f"API Integration Assessment {suffix}",
            "assessment_date": "2026-10-07",
        },
    )
    topic_response = api_client.post(
        "/topics",
        json={
            "name": f"API Integration Topic {suffix}",
            "description": "Created by a real database integration test.",
        },
    )

    assert learner_response.status_code == 201
    assert assessment_response.status_code == 201
    assert topic_response.status_code == 201

    return {
        "learner_id": learner_response.json()["id"],
        "assessment_id": assessment_response.json()["id"],
        "topic_id": topic_response.json()["id"],
    }


def test_real_api_performs_learner_crud(
    api_client: TestClient,
) -> None:
    """Create, read, update and delete through FastAPI and PostgreSQL."""

    create_response = api_client.post(
        "/learners",
        json={"display_name": "  Real API Learner  "},
    )

    assert create_response.status_code == 201

    learner_id = create_response.json()["id"]

    assert create_response.json()["display_name"] == "Real API Learner"

    read_response = api_client.get(f"/learners/{learner_id}")

    assert read_response.status_code == 200
    assert read_response.json()["id"] == learner_id

    update_response = api_client.patch(
        f"/learners/{learner_id}",
        json={"display_name": "Updated Real API Learner"},
    )

    assert update_response.status_code == 200
    assert (
        update_response.json()["display_name"]
        == "Updated Real API Learner"
    )

    delete_response = api_client.delete(f"/learners/{learner_id}")

    assert delete_response.status_code == 204

    missing_response = api_client.get(f"/learners/{learner_id}")

    assert missing_response.status_code == 404
    assert missing_response.json() == {"detail": "Learner not found"}


def test_real_api_creates_and_reads_assessment_result(
    api_client: TestClient,
) -> None:
    """A result should travel through the complete application stack."""

    related_ids = create_result_dependencies(api_client, "Result")

    create_response = api_client.post(
        "/assessment-results",
        json={
            **related_ids,
            "score": "16.00",
            "maximum_score": "20.00",
        },
    )

    assert create_response.status_code == 201

    result_id = create_response.json()["id"]

    assert Decimal(create_response.json()["score"]) == Decimal("16.00")
    assert (
        Decimal(create_response.json()["maximum_score"])
        == Decimal("20.00")
    )

    read_response = api_client.get(
        f"/assessment-results/{result_id}"
    )

    assert read_response.status_code == 200
    assert read_response.json()["learner_id"] == related_ids["learner_id"]
    assert (
        read_response.json()["assessment_id"]
        == related_ids["assessment_id"]
    )
    assert read_response.json()["topic_id"] == related_ids["topic_id"]


def test_real_api_returns_conflict_for_duplicate_result(
    api_client: TestClient,
) -> None:
    """The API must convert the real unique violation into HTTP 409."""

    related_ids = create_result_dependencies(api_client, "Duplicate")

    result_data = {
        **related_ids,
        "score": "15.00",
        "maximum_score": "20.00",
    }

    first_response = api_client.post(
        "/assessment-results",
        json=result_data,
    )
    duplicate_response = api_client.post(
        "/assessment-results",
        json=result_data,
    )

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": (
            "An assessment result already exists for this "
            "learner, assessment and topic"
        )
    }


def test_real_api_rejects_score_above_maximum(
    api_client: TestClient,
) -> None:
    """Pydantic must reject an invalid score before it reaches PostgreSQL."""

    related_ids = create_result_dependencies(api_client, "Invalid Score")

    response = api_client.post(
        "/assessment-results",
        json={
            **related_ids,
            "score": "25.00",
            "maximum_score": "20.00",
        },
    )

    assert response.status_code == 422


def test_real_api_learner_deletion_cascades(
    api_client: TestClient,
) -> None:
    """Deleting through the API must activate PostgreSQL cascades."""

    related_ids = create_result_dependencies(api_client, "Cascade")

    result_response = api_client.post(
        "/assessment-results",
        json={
            **related_ids,
            "score": "18.00",
            "maximum_score": "20.00",
        },
    )
    intervention_response = api_client.post(
        "/interventions",
        json={
            "learner_id": related_ids["learner_id"],
            "topic_id": related_ids["topic_id"],
            "summary": "Real API cascade test intervention",
        },
    )

    assert result_response.status_code == 201
    assert intervention_response.status_code == 201

    result_id = result_response.json()["id"]
    intervention_id = intervention_response.json()["id"]

    delete_response = api_client.delete(
        f"/learners/{related_ids['learner_id']}"
    )

    assert delete_response.status_code == 204
    assert (
        api_client.get(f"/assessment-results/{result_id}").status_code
        == 404
    )
    assert (
        api_client.get(f"/interventions/{intervention_id}").status_code
        == 404
    )
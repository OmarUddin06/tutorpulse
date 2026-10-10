"""Tests for the public portfolio demo safety boundary."""

from collections.abc import Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import settings
from app.demo_mode import (
    READ_ONLY_MESSAGE,
    enforce_demo_read_only,
)


@pytest.fixture
def demo_client() -> Generator[TestClient, None, None]:
    """Return a small application using the demo middleware."""

    test_app = FastAPI()

    test_app.middleware("http")(
        enforce_demo_read_only
    )

    @test_app.get("/learners")
    def list_learners() -> dict[str, str]:
        return {"operation": "read"}

    @test_app.post("/learners")
    def create_learner() -> dict[str, str]:
        return {"operation": "create"}

    @test_app.patch("/learners/1")
    def update_learner() -> dict[str, str]:
        return {"operation": "update"}

    @test_app.delete("/learners/1")
    def delete_learner() -> dict[str, str]:
        return {"operation": "delete"}

    @test_app.post(
        "/predictions/support-risk"
    )
    def predict_support_risk() -> dict[str, str]:
        return {"operation": "predict"}

    with TestClient(test_app) as client:
        yield client


def test_normal_mode_allows_database_write(
    demo_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "demo_read_only",
        False,
    )

    response = demo_client.post(
        "/learners"
    )

    assert response.status_code == 200
    assert response.json() == {
        "operation": "create",
    }


def test_demo_mode_blocks_database_writes(
    demo_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "demo_read_only",
        True,
    )

    requests = (
        ("POST", "/learners"),
        ("PATCH", "/learners/1"),
        ("DELETE", "/learners/1"),
    )

    for method, path in requests:
        response = demo_client.request(
            method,
            path,
        )

        assert response.status_code == 403
        assert response.json() == {
            "detail": READ_ONLY_MESSAGE,
        }


def test_demo_mode_allows_database_reads(
    demo_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "demo_read_only",
        True,
    )

    response = demo_client.get(
        "/learners"
    )

    assert response.status_code == 200
    assert response.json() == {
        "operation": "read",
    }


def test_demo_mode_allows_governed_prediction(
    demo_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "demo_read_only",
        True,
    )

    response = demo_client.post(
        "/predictions/support-risk/",
    )

    assert response.status_code == 200
    assert response.json() == {
        "operation": "predict",
    }
"""API tests for governed TutorPulse inference."""

from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from analysis.model_artifact import ModelBundle
from app.config import settings
from app.inference_schemas import SupportRiskResponse
from app.main import app
from app.model_service import (
    ModelPredictionError,
    ModelRuntimeState,
)


VALID_REQUEST = {
    "topic_name": "Algebra",
    "maximum_score": 20.0,
    "prior_assessment_count": 5,
    "prior_result_count": 18,
    "prior_average_percentage": 64.2,
    "prior_minimum_percentage": 42.0,
    "prior_maximum_percentage": 88.0,
    "prior_support_count": 6,
    "prior_support_rate": 0.3333,
    "previous_assessment_average_percentage": 61.5,
    "days_since_previous_assessment": 14,
    "prior_same_topic_count": 4,
    "prior_same_topic_average_percentage": 58.5,
    "prior_same_topic_latest_percentage": 62.0,
    "prior_same_topic_support_count": 2,
    "prior_intervention_count": 3,
    "prior_same_topic_intervention_count": 1,
    "prior_completed_intervention_count": 2,
}


def make_ready_state() -> ModelRuntimeState:
    """Return a controlled ready model state."""

    return ModelRuntimeState(
        bundle=ModelBundle(
            pipeline=MagicMock(),
            metadata={
                "model_name": "logistic_regression",
                "schema_version": 1,
                "decision_threshold": 0.38,
                "support_threshold": 60.0,
            },
        )
    )


def make_unavailable_state() -> ModelRuntimeState:
    """Return a controlled unavailable model state."""

    return ModelRuntimeState(
        bundle=None,
        load_error_category="ModelArtifactError",
    )


@contextmanager
def application_client(
    state: ModelRuntimeState,
) -> Iterator[tuple[TestClient, MagicMock]]:
    """Start the application with controlled model state."""

    with patch(
        "app.main.load_model_runtime",
        return_value=state,
    ) as load_runtime:
        with TestClient(app) as client:
            yield client, load_runtime


def prediction_response() -> SupportRiskResponse:
    """Return one controlled successful prediction."""

    return SupportRiskResponse(
        support_probability=0.7421,
        predicted_needs_support=True,
        decision_threshold=0.38,
        support_threshold=60.0,
        model_name="logistic_regression",
        artifact_schema_version=1,
    )


def test_lifespan_loads_configured_artifact_once() -> None:
    with application_client(
        make_ready_state()
    ) as (_, load_runtime):
        pass

    load_runtime.assert_called_once_with(
        settings.model_artifact_directory
    )


def test_model_health_returns_ready_metadata() -> None:
    with application_client(
        make_ready_state()
    ) as (client, _):
        response = client.get(
            "/model/health"
        )

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "model_name": "logistic_regression",
        "artifact_schema_version": 1,
        "decision_threshold": 0.38,
    }


def test_model_health_returns_503_when_unavailable() -> None:
    with application_client(
        make_unavailable_state()
    ) as (client, _):
        response = client.get(
            "/model/health"
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Model inference is unavailable"
    }


def test_valid_prediction_returns_governed_response() -> None:
    with application_client(
        make_ready_state()
    ) as (client, _):
        with patch(
            "app.routers.predictions."
            "predict_support_risk",
            return_value=prediction_response(),
        ) as predict:
            response = client.post(
                "/predictions/support-risk",
                json=VALID_REQUEST,
            )

    assert response.status_code == 200
    assert response.json() == {
        "support_probability": 0.7421,
        "predicted_needs_support": True,
        "decision_threshold": 0.38,
        "support_threshold": 60.0,
        "model_name": "logistic_regression",
        "artifact_schema_version": 1,
        "human_review_required": True,
    }

    predict.assert_called_once()


def test_prediction_returns_503_when_unavailable() -> None:
    with application_client(
        make_unavailable_state()
    ) as (client, _):
        response = client.post(
            "/predictions/support-risk",
            json=VALID_REQUEST,
        )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Model inference is unavailable"
    }


def test_prediction_failure_returns_generic_500() -> None:
    with application_client(
        make_ready_state()
    ) as (client, _):
        with patch(
            "app.routers.predictions."
            "predict_support_risk",
            side_effect=ModelPredictionError(
                "Sensitive internal detail"
            ),
        ):
            response = client.post(
                "/predictions/support-risk",
                json=VALID_REQUEST,
            )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Model prediction failed"
    }
    assert "Sensitive internal detail" not in response.text


def test_invalid_prediction_request_returns_422() -> None:
    invalid_request = {
        **VALID_REQUEST,
        "learner_id": 999,
    }

    with application_client(
        make_ready_state()
    ) as (client, _):
        with patch(
            "app.routers.predictions."
            "predict_support_risk",
        ) as predict:
            response = client.post(
                "/predictions/support-risk",
                json=invalid_request,
            )

    assert response.status_code == 422
    predict.assert_not_called()


def test_prediction_log_excludes_feature_payload(
    caplog: pytest.LogCaptureFixture,
) -> None:
    request_data = {
        **VALID_REQUEST,
        "topic_name": "PrivateTopicValue",
    }

    caplog.set_level(
        logging.INFO,
        logger="app.routers.predictions",
    )

    with application_client(
        make_ready_state()
    ) as (client, _):
        with patch(
            "app.routers.predictions."
            "predict_support_risk",
            return_value=prediction_response(),
        ):
            response = client.post(
                "/predictions/support-risk",
                json=request_data,
            )

    assert response.status_code == 200
    assert "prediction_completed" in caplog.text
    assert "PrivateTopicValue" not in caplog.text
    assert "prior_average_percentage" not in caplog.text


def test_basic_health_remains_available_without_model() -> None:
    with application_client(
        make_unavailable_state()
    ) as (client, _):
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_openapi_contains_model_endpoints() -> None:
    with application_client(
        make_ready_state()
    ) as (client, _):
        document = client.get(
            "/openapi.json"
        ).json()

    assert (
        "/predictions/support-risk"
        in document["paths"]
    )
    assert "/model/health" in document["paths"]
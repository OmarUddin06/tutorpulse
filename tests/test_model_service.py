"""Tests for the TutorPulse model runtime service."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from analysis.model_artifact import (
    ModelArtifactError,
    ModelBundle,
)
from analysis.modelling import MODEL_FEATURE_COLUMNS
from app.config import Settings
from app.inference_schemas import SupportRiskRequest
from app.model_service import (
    ModelPredictionError,
    ModelRuntimeState,
    ModelUnavailableError,
    build_feature_frame,
    load_model_runtime,
    model_health_response,
    predict_support_risk,
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


def make_request() -> SupportRiskRequest:
    """Return one valid governed inference request."""

    return SupportRiskRequest(**VALID_REQUEST)


def make_bundle() -> ModelBundle:
    """Return a controlled model bundle for service tests."""

    return ModelBundle(
        pipeline=MagicMock(),
        metadata={
            "model_name": "logistic_regression",
            "schema_version": 1,
            "decision_threshold": 0.38,
            "support_threshold": 60.0,
        },
    )


def test_settings_default_model_artifact_directory() -> None:
    configured = Settings(
        db_password="test_password",
        _env_file=None,
    )

    assert configured.model_artifact_directory == Path(
        "artifacts/models"
    )


def test_model_runtime_loads_valid_bundle() -> None:
    bundle = make_bundle()

    with patch(
        "app.model_service.load_model_artifact",
        return_value=bundle,
    ) as load_artifact:
        state = load_model_runtime(
            "controlled/artifacts"
        )

    assert state.is_ready is True
    assert state.bundle is bundle
    assert state.load_error_category is None

    load_artifact.assert_called_once_with(
        "controlled/artifacts"
    )


def test_model_runtime_records_unavailable_state(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with patch(
        "app.model_service.load_model_artifact",
        side_effect=ModelArtifactError(
            "Pipeline artifact does not exist"
        ),
    ):
        state = load_model_runtime(
            "missing/artifacts"
        )

    assert state.is_ready is False
    assert state.bundle is None
    assert (
        state.load_error_category
        == "ModelArtifactError"
    )
    assert "model artifact is unavailable" in caplog.text
    assert "missing/artifacts" not in caplog.text


def test_feature_frame_uses_frozen_feature_order() -> None:
    frame = build_feature_frame(
        make_request()
    )

    assert frame.shape == (
        1,
        len(MODEL_FEATURE_COLUMNS),
    )
    assert tuple(frame.columns) == tuple(
        MODEL_FEATURE_COLUMNS
    )
    assert frame.iloc[0]["topic_name"] == "Algebra"


def test_prediction_returns_governed_response() -> None:
    bundle = make_bundle()
    state = ModelRuntimeState(
        bundle=bundle,
    )

    prediction_table = pd.DataFrame(
        {
            "support_probability": [0.7421],
            "predicted_needs_support": [True],
        }
    )

    with patch(
        "app.model_service.predict_support",
        return_value=prediction_table,
    ) as predict:
        response = predict_support_risk(
            state,
            make_request(),
        )

    assert response.support_probability == pytest.approx(
        0.7421
    )
    assert response.predicted_needs_support is True
    assert response.decision_threshold == pytest.approx(
        0.38
    )
    assert response.support_threshold == pytest.approx(
        60.0
    )
    assert response.model_name == "logistic_regression"
    assert response.artifact_schema_version == 1
    assert response.human_review_required is True

    prediction_features = predict.call_args.args[1]

    assert tuple(
        prediction_features.columns
    ) == tuple(MODEL_FEATURE_COLUMNS)

    bundle.pipeline.fit.assert_not_called()


def test_unavailable_model_rejects_prediction() -> None:
    state = ModelRuntimeState(
        bundle=None,
        load_error_category="ModelArtifactError",
    )

    with pytest.raises(
        ModelUnavailableError,
        match="Model inference is unavailable",
    ):
        predict_support_risk(
            state,
            make_request(),
        )


def test_ready_model_returns_health_metadata() -> None:
    response = model_health_response(
        ModelRuntimeState(
            bundle=make_bundle(),
        )
    )

    assert response.status == "ready"
    assert response.model_name == "logistic_regression"
    assert response.artifact_schema_version == 1
    assert response.decision_threshold == pytest.approx(
        0.38
    )


def test_prediction_failure_is_wrapped(
    caplog: pytest.LogCaptureFixture,
) -> None:
    state = ModelRuntimeState(
        bundle=make_bundle(),
    )

    with patch(
        "app.model_service.predict_support",
        side_effect=ModelArtifactError(
            "Controlled prediction failure"
        ),
    ):
        with pytest.raises(
            ModelPredictionError,
            match="Model prediction failed",
        ):
            predict_support_risk(
                state,
                make_request(),
            )

    assert "model prediction failed" in caplog.text
    assert "Controlled prediction failure" not in caplog.text
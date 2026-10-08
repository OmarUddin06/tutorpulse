"""Tests for TutorPulse inference request and response schemas."""

from typing import Any

import pytest
from pydantic import ValidationError

from analysis.modelling import MODEL_FEATURE_COLUMNS
from app.inference_schemas import (
    ModelHealthResponse,
    SupportRiskRequest,
    SupportRiskResponse,
)


VALID_REQUEST: dict[str, Any] = {
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


def build_request(
    **overrides: Any,
) -> SupportRiskRequest:
    """Create a valid request with optional changed fields."""

    values = {
        **VALID_REQUEST,
        **overrides,
    }

    return SupportRiskRequest(**values)


def test_valid_support_risk_request_is_accepted() -> None:
    request = build_request(
        topic_name="  Algebra  ",
    )

    assert request.topic_name == "Algebra"
    assert request.prior_result_count == 18
    assert request.prior_support_rate == pytest.approx(
        0.3333
    )


def test_request_field_order_matches_model_contract() -> None:
    request = build_request()

    assert tuple(request.model_dump()) == tuple(
        MODEL_FEATURE_COLUMNS
    )


def test_nullable_history_values_are_accepted() -> None:
    request = build_request(
        previous_assessment_average_percentage=None,
        days_since_previous_assessment=None,
        prior_same_topic_count=0,
        prior_same_topic_average_percentage=None,
        prior_same_topic_latest_percentage=None,
        prior_same_topic_support_count=0,
    )

    assert (
        request.previous_assessment_average_percentage
        is None
    )
    assert request.days_since_previous_assessment is None


def test_extra_request_field_is_rejected() -> None:
    values = {
        **VALID_REQUEST,
        "learner_id": 42,
    }

    with pytest.raises(
        ValidationError,
        match="Extra inputs are not permitted",
    ):
        SupportRiskRequest(**values)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("maximum_score", 0),
        ("prior_assessment_count", -1),
        ("prior_result_count", -1),
        ("prior_average_percentage", -0.1),
        ("prior_minimum_percentage", 100.1),
        ("prior_maximum_percentage", 101),
        ("prior_support_count", -1),
        ("prior_support_rate", 1.1),
        (
            "previous_assessment_average_percentage",
            -1,
        ),
        ("days_since_previous_assessment", -1),
        ("prior_same_topic_count", -1),
        (
            "prior_same_topic_average_percentage",
            101,
        ),
        (
            "prior_same_topic_latest_percentage",
            -1,
        ),
        ("prior_same_topic_support_count", -1),
        ("prior_intervention_count", -1),
        (
            "prior_same_topic_intervention_count",
            -1,
        ),
        (
            "prior_completed_intervention_count",
            -1,
        ),
    ],
)
def test_invalid_numeric_bound_is_rejected(
    field_name: str,
    invalid_value: object,
) -> None:
    values = {
        **VALID_REQUEST,
        field_name: invalid_value,
    }

    with pytest.raises(ValidationError):
        SupportRiskRequest(**values)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        (
            {
                "prior_result_count": 2,
                "prior_support_count": 3,
            },
            (
                "prior_support_count must not exceed "
                "prior_result_count"
            ),
        ),
        (
            {
                "prior_result_count": 2,
                "prior_support_count": 2,
                "prior_same_topic_count": 3,
            },
            (
                "prior_same_topic_count must not exceed "
                "prior_result_count"
            ),
        ),
        (
            {
                "prior_same_topic_count": 2,
                "prior_same_topic_support_count": 3,
            },
            (
                "prior_same_topic_support_count must not "
                "exceed prior_same_topic_count"
            ),
        ),
        (
            {
                "prior_intervention_count": 1,
                "prior_same_topic_intervention_count": 2,
            },
            (
                "prior_same_topic_intervention_count must "
                "not exceed prior_intervention_count"
            ),
        ),
        (
            {
                "prior_intervention_count": 1,
                "prior_completed_intervention_count": 2,
            },
            (
                "prior_completed_intervention_count must "
                "not exceed prior_intervention_count"
            ),
        ),
    ],
)
def test_inconsistent_counts_are_rejected(
    overrides: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(
        ValidationError,
        match=message,
    ):
        build_request(**overrides)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        (
            {
                "prior_minimum_percentage": 80,
                "prior_maximum_percentage": 60,
            },
            (
                "prior_minimum_percentage must not exceed "
                "prior_maximum_percentage"
            ),
        ),
        (
            {
                "prior_minimum_percentage": 60,
                "prior_average_percentage": 50,
            },
            (
                "prior_average_percentage must not be below "
                "prior_minimum_percentage"
            ),
        ),
        (
            {
                "prior_maximum_percentage": 60,
                "prior_average_percentage": 70,
            },
            (
                "prior_average_percentage must not exceed "
                "prior_maximum_percentage"
            ),
        ),
    ],
)
def test_inconsistent_percentages_are_rejected(
    overrides: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(
        ValidationError,
        match=message,
    ):
        build_request(**overrides)


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        (
            "prior_same_topic_average_percentage",
            65.0,
        ),
        (
            "prior_same_topic_latest_percentage",
            70.0,
        ),
    ],
)
def test_same_topic_values_require_history(
    field_name: str,
    field_value: float,
) -> None:
    values = {
        **VALID_REQUEST,
        "prior_same_topic_count": 0,
        "prior_same_topic_support_count": 0,
        "prior_same_topic_average_percentage": None,
        "prior_same_topic_latest_percentage": None,
        field_name: field_value,
    }

    with pytest.raises(
        ValidationError,
        match="requires prior_same_topic_count",
    ):
        SupportRiskRequest(**values)


def test_consistent_prediction_response_is_accepted() -> None:
    response = SupportRiskResponse(
        support_probability=0.7421,
        predicted_needs_support=True,
        decision_threshold=0.38,
        support_threshold=60.0,
        model_name="logistic_regression",
        artifact_schema_version=1,
    )

    assert response.predicted_needs_support is True
    assert response.human_review_required is True


@pytest.mark.parametrize(
    (
        "probability",
        "decision",
    ),
    [
        (0.20, True),
        (0.80, False),
    ],
)
def test_inconsistent_prediction_response_is_rejected(
    probability: float,
    decision: bool,
) -> None:
    with pytest.raises(
        ValidationError,
        match=(
            "predicted_needs_support does not match"
        ),
    ):
        SupportRiskResponse(
            support_probability=probability,
            predicted_needs_support=decision,
            decision_threshold=0.38,
            support_threshold=60.0,
            model_name="logistic_regression",
            artifact_schema_version=1,
        )


def test_human_review_cannot_be_disabled() -> None:
    with pytest.raises(ValidationError):
        SupportRiskResponse(
            support_probability=0.20,
            predicted_needs_support=False,
            decision_threshold=0.38,
            support_threshold=60.0,
            model_name="logistic_regression",
            artifact_schema_version=1,
            human_review_required=False,
        )


def test_ready_model_health_response_is_valid() -> None:
    response = ModelHealthResponse(
        model_name="logistic_regression",
        artifact_schema_version=1,
        decision_threshold=0.38,
    )

    assert response.status == "ready"
    assert response.decision_threshold == pytest.approx(
        0.38
    )
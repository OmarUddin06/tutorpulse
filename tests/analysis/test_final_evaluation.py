from dataclasses import replace
from datetime import datetime

import pandas as pd
import pytest

from analysis.final_evaluation import (
    FINAL_DECISION_THRESHOLD,
    FINAL_MODEL_NAME,
    VALIDATION_PRECISION_FLOOR,
    final_comparison,
    run_final_evaluation,
)
from analysis.model_data import (
    ModelSplit,
    PreparedModelData,
)
from analysis.modelling import (
    MODEL_FEATURE_COLUMNS,
    MODEL_METADATA_COLUMNS,
)


def _feature_frame(
    row_count: int,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for index in range(row_count):
        lower_performance = index % 2 == 1
        historical_average = (
            48.0
            if lower_performance
            else 76.0
        )

        rows.append(
            {
                "topic_name": (
                    "Fractions"
                    if lower_performance
                    else "Algebra"
                ),
                "maximum_score": 20.0,
                "prior_assessment_count": index + 1,
                "prior_result_count": (index + 1) * 4,
                "prior_average_percentage": (
                    historical_average
                ),
                "prior_minimum_percentage": (
                    historical_average - 10.0
                ),
                "prior_maximum_percentage": (
                    historical_average + 10.0
                ),
                "prior_support_count": (
                    2
                    if lower_performance
                    else 0
                ),
                "prior_support_rate": (
                    0.6
                    if lower_performance
                    else 0.1
                ),
                "previous_assessment_average_percentage": (
                    historical_average
                ),
                "days_since_previous_assessment": 14,
                "prior_same_topic_count": index + 1,
                "prior_same_topic_average_percentage": (
                    historical_average
                ),
                "prior_same_topic_latest_percentage": (
                    historical_average - 2.0
                ),
                "prior_same_topic_support_count": (
                    1
                    if lower_performance
                    else 0
                ),
                "prior_intervention_count": (
                    2
                    if lower_performance
                    else 0
                ),
                "prior_same_topic_intervention_count": (
                    1
                    if lower_performance
                    else 0
                ),
                "prior_completed_intervention_count": (
                    1
                    if lower_performance
                    else 0
                ),
            }
        )

    return pd.DataFrame(
        rows,
        columns=MODEL_FEATURE_COLUMNS,
    )


def _model_split(
    *,
    name: str,
    first_result_id: int,
    assessment_date: str,
    target_values: list[int],
) -> ModelSplit:
    row_count = len(target_values)

    metadata = pd.DataFrame(
        {
            "result_id": range(
                first_result_id,
                first_result_id + row_count,
            ),
            "learner_id": range(
                first_result_id,
                first_result_id + row_count,
            ),
            "assessment_id": [
                first_result_id
            ]
            * row_count,
            "assessment_date": [
                datetime.fromisoformat(assessment_date)
            ]
            * row_count,
            "topic_id": [
                (index % 2) + 1
                for index in range(row_count)
            ],
            "result_percentage": [
                50.0
                if value
                else 75.0
                for value in target_values
            ],
        },
        columns=MODEL_METADATA_COLUMNS,
    )

    return ModelSplit(
        name=name,
        features=_feature_frame(row_count),
        target=pd.Series(
            target_values,
            name="needs_support",
            dtype="int8",
        ),
        metadata=metadata,
    )


def _prepared_data() -> PreparedModelData:
    return PreparedModelData(
        train=_model_split(
            name="train",
            first_result_id=1,
            assessment_date="2025-01-01",
            target_values=[
                0,
                1,
                0,
                1,
                0,
                1,
                0,
                0,
            ],
        ),
        validation=_model_split(
            name="validation",
            first_result_id=20,
            assessment_date="2025-02-01",
            target_values=[
                0,
                1,
                1,
                0,
            ],
        ),
        test=_model_split(
            name="test",
            first_result_id=30,
            assessment_date="2025-03-01",
            target_values=[
                1,
                0,
                1,
                0,
            ],
        ),
        manifest={},
    )


def test_final_decision_is_explicit() -> None:
    assert FINAL_MODEL_NAME == "logistic_regression"
    assert FINAL_DECISION_THRESHOLD == pytest.approx(0.38)
    assert VALIDATION_PRECISION_FLOOR == pytest.approx(0.60)


def test_final_evaluation_covers_every_test_row() -> None:
    prepared = _prepared_data()

    evaluation = run_final_evaluation(prepared)

    assert len(evaluation.test_predictions) == len(
        prepared.test.features
    )

    total_predictions = (
        evaluation.final_model_metrics.true_negatives
        + evaluation.final_model_metrics.false_positives
        + evaluation.final_model_metrics.false_negatives
        + evaluation.final_model_metrics.true_positives
    )

    assert total_predictions == len(
        prepared.test.features
    )


def test_prediction_table_is_auditable() -> None:
    prepared = _prepared_data()

    evaluation = run_final_evaluation(prepared)
    predictions = evaluation.test_predictions

    assert {
        "result_id",
        "learner_id",
        "assessment_id",
        "assessment_date",
        "topic_id",
        "result_percentage",
        "actual_needs_support",
        "support_probability",
        "predicted_needs_support",
        "prediction_correct",
    }.issubset(predictions.columns)

    assert predictions["support_probability"].between(
        0.0,
        1.0,
    ).all()

    expected_predictions = (
        predictions["support_probability"]
        >= FINAL_DECISION_THRESHOLD
    ).astype("int8")

    assert (
        predictions["predicted_needs_support"]
        == expected_predictions
    ).all()


def test_final_comparison_contains_both_models() -> None:
    prepared = _prepared_data()

    evaluation = run_final_evaluation(prepared)
    comparison = final_comparison(evaluation)

    assert list(comparison.index) == [
        "dummy_baseline",
        "logistic_regression",
    ]
    assert "recall" in comparison.columns
    assert "false_negatives" in comparison.columns
    assert "average_precision" in comparison.columns


def test_final_evaluation_does_not_use_validation_data() -> None:
    prepared = _prepared_data()

    unusable_validation = replace(
        prepared.validation,
        features=pd.DataFrame(
            {
                "not_a_model_feature": [1],
            }
        ),
    )
    prepared_with_unusable_validation = replace(
        prepared,
        validation=unusable_validation,
    )

    evaluation = run_final_evaluation(
        prepared_with_unusable_validation
    )

    assert len(evaluation.test_predictions) == len(
        prepared.test.features
    )
from dataclasses import replace
from datetime import datetime

import numpy as np
import pandas as pd

from analysis.model_comparison import (
    RANDOM_FOREST_ESTIMATORS,
    RANDOM_FOREST_MAX_DEPTH,
    RANDOM_FOREST_MIN_SAMPLES_LEAF,
    build_random_forest_pipeline,
    candidate_summary,
    compare_candidate_models,
    probability_calibration_table,
)
from analysis.model_data import (
    ModelSplit,
    PreparedModelData,
)
from analysis.modelling import (
    MODEL_FEATURE_COLUMNS,
    MODEL_METADATA_COLUMNS,
    NUMERIC_FEATURE_COLUMNS,
)


def _feature_frame(
    row_count: int,
) -> pd.DataFrame:
    index = np.arange(row_count)
    lower_performance = index % 2 == 1

    frame = pd.DataFrame(
        {
            column: index.astype(float) + 1.0
            for column in NUMERIC_FEATURE_COLUMNS
        }
    )

    frame["topic_name"] = np.where(
        lower_performance,
        "Fractions",
        "Algebra",
    )

    historical_average = np.where(
        lower_performance,
        45.0,
        78.0,
    )

    frame["maximum_score"] = 20.0
    frame["prior_average_percentage"] = (
        historical_average
    )
    frame["prior_minimum_percentage"] = (
        historical_average - 10.0
    )
    frame["prior_maximum_percentage"] = (
        historical_average + 10.0
    )
    frame[
        "previous_assessment_average_percentage"
    ] = historical_average
    frame[
        "prior_same_topic_average_percentage"
    ] = historical_average
    frame[
        "prior_same_topic_latest_percentage"
    ] = historical_average - 2.0
    frame["prior_support_rate"] = np.where(
        lower_performance,
        0.7,
        0.1,
    )
    frame["prior_support_count"] = np.where(
        lower_performance,
        3,
        0,
    )
    frame["prior_same_topic_support_count"] = np.where(
        lower_performance,
        2,
        0,
    )

    return frame.loc[
        :,
        MODEL_FEATURE_COLUMNS,
    ]


def _split(
    *,
    name: str,
    first_result_id: int,
    assessment_date: str,
    target: list[int],
) -> ModelSplit:
    row_count = len(target)

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
                (value % 2) + 1
                for value in range(row_count)
            ],
            "result_percentage": [
                50.0
                if value
                else 75.0
                for value in target
            ],
        },
        columns=MODEL_METADATA_COLUMNS,
    )

    return ModelSplit(
        name=name,
        features=_feature_frame(row_count),
        target=pd.Series(
            target,
            name="needs_support",
            dtype="int8",
        ),
        metadata=metadata,
    )


def _prepared_data() -> PreparedModelData:
    return PreparedModelData(
        train=_split(
            name="train",
            first_result_id=1,
            assessment_date="2025-01-01",
            target=[
                0,
                1,
            ]
            * 20,
        ),
        validation=_split(
            name="validation",
            first_result_id=100,
            assessment_date="2025-02-01",
            target=[
                0,
                1,
            ]
            * 10,
        ),
        test=_split(
            name="test",
            first_result_id=200,
            assessment_date="2025-03-01",
            target=[
                1,
                0,
                1,
                0,
            ],
        ),
        manifest={},
    )


def test_random_forest_configuration_is_fixed() -> None:
    pipeline = build_random_forest_pipeline()
    classifier = pipeline.named_steps["classifier"]

    assert classifier.n_estimators == (
        RANDOM_FOREST_ESTIMATORS
    )
    assert classifier.max_depth == (
        RANDOM_FOREST_MAX_DEPTH
    )
    assert classifier.min_samples_leaf == (
        RANDOM_FOREST_MIN_SAMPLES_LEAF
    )
    assert classifier.random_state == 42


def test_calibration_table_contains_valid_rates() -> None:
    target = pd.Series(
        [0, 0, 1, 1],
        name="needs_support",
    )
    probabilities = np.array(
        [0.1, 0.4, 0.6, 0.9]
    )

    table = probability_calibration_table(
        target,
        probabilities,
        bins=2,
    )

    assert {
        "bin",
        "mean_predicted_probability",
        "observed_support_rate",
        "absolute_calibration_gap",
    } == set(table.columns)

    assert table[
        "mean_predicted_probability"
    ].between(0.0, 1.0).all()

    assert table[
        "observed_support_rate"
    ].between(0.0, 1.0).all()


def test_candidate_comparison_contains_both_models() -> None:
    comparison = compare_candidate_models(
        _prepared_data()
    )
    summary = candidate_summary(comparison)

    assert list(summary.index) == [
        "logistic_regression",
        "random_forest",
    ]

    assert summary["brier_score"].between(
        0.0,
        1.0,
    ).all()

    assert (
        summary["precision"] >= 0.60
    ).all()


def test_candidate_comparison_does_not_access_test() -> None:
    prepared = _prepared_data()

    unusable_test = replace(
        prepared.test,
        features=pd.DataFrame(
            {
                "not_a_model_feature": [1],
            }
        ),
    )
    prepared_with_unusable_test = replace(
        prepared,
        test=unusable_test,
    )

    comparison = compare_candidate_models(
        prepared_with_unusable_test
    )

    assert comparison.logistic_regression.name == (
        "logistic_regression"
    )
    assert comparison.random_forest.name == (
        "random_forest"
    )


def test_random_forest_predictions_are_deterministic() -> None:
    prepared = _prepared_data()

    first = build_random_forest_pipeline()
    second = build_random_forest_pipeline()

    first.fit(
        prepared.train.features,
        prepared.train.target,
    )
    second.fit(
        prepared.train.features,
        prepared.train.target,
    )

    first_probabilities = first.predict_proba(
        prepared.validation.features
    )
    second_probabilities = second.predict_proba(
        prepared.validation.features
    )

    assert np.allclose(
        first_probabilities,
        second_probabilities,
    )
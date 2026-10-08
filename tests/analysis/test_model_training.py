from dataclasses import replace
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from analysis.model_data import (
    ModelSplit,
    PreparedModelData,
)
from analysis.model_training import (
    ModelTrainingError,
    build_logistic_pipeline,
    evaluate_probabilities,
    positive_class_probabilities,
    train_and_validate,
    validation_comparison,
)
from analysis.modelling import (
    MODEL_FEATURE_COLUMNS,
    MODEL_METADATA_COLUMNS,
)


def _feature_frame(
    *,
    row_count: int,
    include_unseen_topic: bool = False,
) -> pd.DataFrame:
    topics = [
        "Algebra",
        "Fractions",
    ]

    if include_unseen_topic:
        topics[0] = "Calculus"

    rows: list[dict[str, object]] = []

    for index in range(row_count):
        percentage_signal = (
            48.0
            if index % 2
            else 76.0
        )

        rows.append(
            {
                "topic_name": topics[index % len(topics)],
                "maximum_score": 20.0,
                "prior_assessment_count": index + 1,
                "prior_result_count": (index + 1) * 4,
                "prior_average_percentage": percentage_signal,
                "prior_minimum_percentage": (
                    percentage_signal - 10.0
                ),
                "prior_maximum_percentage": (
                    percentage_signal + 10.0
                ),
                "prior_support_count": (
                    2
                    if index % 2
                    else 0
                ),
                "prior_support_rate": (
                    0.6
                    if index % 2
                    else 0.1
                ),
                "previous_assessment_average_percentage": (
                    percentage_signal
                ),
                "days_since_previous_assessment": 14,
                "prior_same_topic_count": index + 1,
                "prior_same_topic_average_percentage": (
                    percentage_signal
                ),
                "prior_same_topic_latest_percentage": (
                    percentage_signal - 2.0
                ),
                "prior_same_topic_support_count": (
                    1
                    if index % 2
                    else 0
                ),
                "prior_intervention_count": (
                    2
                    if index % 2
                    else 0
                ),
                "prior_same_topic_intervention_count": (
                    1
                    if index % 2
                    else 0
                ),
                "prior_completed_intervention_count": (
                    1
                    if index % 2
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
    row_count: int,
    first_result_id: int,
    assessment_date: str,
    target_values: list[int],
    include_unseen_topic: bool = False,
) -> ModelSplit:
    features = _feature_frame(
        row_count=row_count,
        include_unseen_topic=include_unseen_topic,
    )

    target = pd.Series(
        target_values,
        name="needs_support",
        dtype="int8",
    )

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
            "assessment_id": [first_result_id] * row_count,
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
        features=features,
        target=target,
        metadata=metadata,
    )


def _prepared_data() -> PreparedModelData:
    train = _model_split(
        name="train",
        row_count=8,
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
    )

    validation = _model_split(
        name="validation",
        row_count=4,
        first_result_id=20,
        assessment_date="2025-02-01",
        target_values=[
            0,
            1,
            1,
            0,
        ],
        include_unseen_topic=True,
    )

    test = _model_split(
        name="test",
        row_count=4,
        first_result_id=30,
        assessment_date="2025-03-01",
        target_values=[
            1,
            0,
            1,
            0,
        ],
    )

    return PreparedModelData(
        train=train,
        validation=validation,
        test=test,
        manifest={},
    )


def test_probability_metrics_include_confusion_counts() -> None:
    target = pd.Series(
        [0, 0, 1, 1],
        name="needs_support",
    )
    probabilities = np.array(
        [0.1, 0.8, 0.4, 0.9]
    )

    metrics = evaluate_probabilities(
        target,
        probabilities,
        threshold=0.5,
    )

    assert metrics.true_negatives == 1
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 1
    assert metrics.true_positives == 1
    assert metrics.accuracy == pytest.approx(0.5)
    assert metrics.precision == pytest.approx(0.5)
    assert metrics.recall == pytest.approx(0.5)
    assert metrics.f1 == pytest.approx(0.5)


def test_invalid_decision_threshold_is_rejected() -> None:
    target = pd.Series(
        [0, 1],
        name="needs_support",
    )
    probabilities = np.array(
        [0.2, 0.8]
    )

    with pytest.raises(
        ModelTrainingError,
        match="between 0 and 1",
    ):
        evaluate_probabilities(
            target,
            probabilities,
            threshold=1.1,
        )


def test_invalid_probabilities_are_rejected() -> None:
    target = pd.Series(
        [0, 1],
        name="needs_support",
    )
    probabilities = np.array(
        [0.2, 1.2]
    )

    with pytest.raises(
        ModelTrainingError,
        match="between 0 and 1",
    ):
        evaluate_probabilities(
            target,
            probabilities,
        )


def test_logistic_pipeline_handles_unseen_topic() -> None:
    prepared = _prepared_data()
    model = build_logistic_pipeline()

    model.fit(
        prepared.train.features,
        prepared.train.target,
    )

    probabilities = positive_class_probabilities(
        model,
        prepared.validation.features,
    )

    assert probabilities.shape == (4,)
    assert (
        (probabilities >= 0.0)
        & (probabilities <= 1.0)
    ).all()


def test_dummy_baseline_predicts_training_majority() -> None:
    prepared = _prepared_data()
    run = train_and_validate(prepared)

    assert run.baseline_metrics.recall == pytest.approx(0.0)
    assert run.baseline_metrics.false_negatives == 2
    assert run.baseline_metrics.true_positives == 0


def test_validation_comparison_contains_both_models() -> None:
    prepared = _prepared_data()
    run = train_and_validate(prepared)

    comparison = validation_comparison(run)

    assert list(comparison.index) == [
        "dummy_baseline",
        "logistic_regression",
    ]
    assert "recall" in comparison.columns
    assert "false_negatives" in comparison.columns
    assert "roc_auc" in comparison.columns


def test_reordered_feature_contract_is_rejected() -> None:
    prepared = _prepared_data()
    reversed_features = prepared.train.features.loc[
        :,
        list(reversed(MODEL_FEATURE_COLUMNS)),
    ]

    invalid_train = replace(
        prepared.train,
        features=reversed_features,
    )
    invalid_data = replace(
        prepared,
        train=invalid_train,
    )

    with pytest.raises(
        ModelTrainingError,
        match="ordered feature contract",
    ):
        train_and_validate(invalid_data)


def test_preprocessor_is_fitted_on_training_topics_only() -> None:
    prepared = _prepared_data()
    run = train_and_validate(prepared)

    preprocessor = run.logistic_model.named_steps[
        "preprocessor"
    ]
    categorical_pipeline = (
        preprocessor.named_transformers_["categorical"]
    )
    encoder = categorical_pipeline.named_steps["one_hot"]

    learned_topics = set(encoder.categories_[0])

    assert learned_topics == {
        "Algebra",
        "Fractions",
    }
    assert "Calculus" not in learned_topics
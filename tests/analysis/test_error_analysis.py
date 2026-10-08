from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from analysis.error_analysis import (
    ErrorAnalysisError,
    assign_history_band,
    build_prediction_frame,
    error_count_table,
    performance_by_group,
    split_distribution_summary,
)
from analysis.model_data import (
    ModelSplit,
    PreparedModelData,
)


class FixedProbabilityModel:
    """Small deterministic classifier used by unit tests."""

    classes_ = np.array(
        [0, 1],
        dtype="int8",
    )

    def __init__(
        self,
        probabilities: list[float],
    ) -> None:
        self.probabilities = np.asarray(
            probabilities,
            dtype=float,
        )

    def predict_proba(
        self,
        features: pd.DataFrame,
    ) -> np.ndarray:
        if len(features) != len(self.probabilities):
            raise ValueError(
                "Feature and probability lengths differ."
            )

        return np.column_stack(
            [
                1.0 - self.probabilities,
                self.probabilities,
            ]
        )


def _split(
    *,
    name: str = "validation",
    date: str = "2025-02-01",
) -> ModelSplit:
    features = pd.DataFrame(
        {
            "topic_name": [
                "Algebra",
                "Algebra",
                "Fractions",
                "Fractions",
            ],
            "prior_result_count": [
                10,
                30,
                50,
                70,
            ],
        }
    )

    target = pd.Series(
        [0, 1, 1, 0],
        name="needs_support",
        dtype="int8",
    )

    metadata = pd.DataFrame(
        {
            "result_id": [1, 2, 3, 4],
            "learner_id": [1, 2, 3, 4],
            "assessment_id": [1, 1, 1, 1],
            "assessment_date": [
                datetime.fromisoformat(date)
            ]
            * 4,
            "topic_id": [1, 1, 2, 2],
            "result_percentage": [
                75.0,
                50.0,
                45.0,
                80.0,
            ],
        }
    )

    return ModelSplit(
        name=name,
        features=features,
        target=target,
        metadata=metadata,
    )


def test_history_bands_use_fixed_boundaries() -> None:
    counts = pd.Series(
        [0, 20, 21, 40, 41, 60, 61]
    )

    bands = assign_history_band(
        counts
    ).astype("string")

    assert bands.tolist() == [
        "limited_1_to_20",
        "limited_1_to_20",
        "developing_21_to_40",
        "developing_21_to_40",
        "established_41_to_60",
        "established_41_to_60",
        "extensive_61_plus",
    ]


def test_prediction_frame_labels_each_outcome() -> None:
    model = FixedProbabilityModel(
        [0.1, 0.2, 0.8, 0.9]
    )

    predictions = build_prediction_frame(
        model,
        _split(),
        threshold=0.5,
    )

    assert predictions["error_type"].tolist() == [
        "true_negative",
        "false_negative",
        "true_positive",
        "false_positive",
    ]


def test_error_counts_cover_every_prediction() -> None:
    model = FixedProbabilityModel(
        [0.1, 0.2, 0.8, 0.9]
    )
    predictions = build_prediction_frame(
        model,
        _split(),
        threshold=0.5,
    )

    counts = error_count_table(
        predictions
    )

    assert counts["rows"].sum() == 4
    assert counts["percentage"].sum() == pytest.approx(
        1.0
    )
    assert set(counts["rows"]) == {1}


def test_group_performance_reports_confusion_counts() -> None:
    model = FixedProbabilityModel(
        [0.1, 0.2, 0.8, 0.9]
    )
    predictions = build_prediction_frame(
        model,
        _split(),
        threshold=0.5,
    )

    grouped = performance_by_group(
        predictions,
        "topic_name",
    )

    algebra = grouped.loc[
        grouped["topic_name"] == "Algebra"
    ].iloc[0]

    fractions = grouped.loc[
        grouped["topic_name"] == "Fractions"
    ].iloc[0]

    assert algebra["true_negatives"] == 1
    assert algebra["false_negatives"] == 1
    assert fractions["true_positives"] == 1
    assert fractions["false_positives"] == 1


def test_split_distribution_reports_chronology() -> None:
    train = _split(
        name="train",
        date="2025-01-01",
    )
    validation = _split(
        name="validation",
        date="2025-02-01",
    )
    test = _split(
        name="test",
        date="2025-03-01",
    )

    prepared = PreparedModelData(
        train=train,
        validation=validation,
        test=test,
        manifest={},
    )

    summary = split_distribution_summary(
        prepared
    )

    assert list(summary.index) == [
        "train",
        "validation",
        "test",
    ]
    assert summary.loc[
        "train",
        "first_assessment_date",
    ] == "2025-01-01"
    assert summary.loc[
        "test",
        "last_assessment_date",
    ] == "2025-03-01"


def test_missing_group_column_is_rejected() -> None:
    model = FixedProbabilityModel(
        [0.1, 0.2, 0.8, 0.9]
    )
    predictions = build_prediction_frame(
        model,
        _split(),
        threshold=0.5,
    )

    with pytest.raises(
        ErrorAnalysisError,
        match="missing columns",
    ):
        performance_by_group(
            predictions,
            "unknown_group",
        )
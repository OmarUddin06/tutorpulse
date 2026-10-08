import numpy as np
import pandas as pd
import pytest

from analysis.threshold_selection import (
    ThresholdSelectionError,
    evaluate_threshold_candidates,
    select_threshold_from_table,
)


def _example_target() -> pd.Series:
    return pd.Series(
        [0, 0, 0, 1, 1],
        name="needs_support",
        dtype="int8",
    )


def _example_probabilities() -> np.ndarray:
    return np.array(
        [0.1, 0.3, 0.7, 0.4, 0.8],
        dtype=float,
    )


def _example_table() -> pd.DataFrame:
    return evaluate_threshold_candidates(
        _example_target(),
        _example_probabilities(),
        thresholds=[
            0.2,
            0.4,
            0.6,
        ],
    )


def test_candidate_table_contains_each_threshold() -> None:
    table = _example_table()

    assert table["threshold"].tolist() == [
        0.2,
        0.4,
        0.6,
    ]
    assert "precision" in table.columns
    assert "recall" in table.columns
    assert "false_negatives" in table.columns
    assert "false_positives" in table.columns


def test_selection_maximises_recall_with_precision_floor() -> None:
    table = _example_table()

    threshold, metrics = select_threshold_from_table(
        table,
        minimum_precision=0.60,
    )

    assert threshold == pytest.approx(0.4)
    assert metrics.threshold == pytest.approx(0.4)
    assert metrics.precision == pytest.approx(2 / 3)
    assert metrics.recall == pytest.approx(1.0)


def test_selected_metrics_include_confusion_counts() -> None:
    table = _example_table()

    _, metrics = select_threshold_from_table(
        table,
        minimum_precision=0.60,
    )

    assert metrics.true_negatives == 2
    assert metrics.false_positives == 1
    assert metrics.false_negatives == 0
    assert metrics.true_positives == 2


def test_impossible_precision_rule_is_rejected() -> None:
    table = _example_table()

    with pytest.raises(
        ThresholdSelectionError,
        match="No threshold satisfies",
    ):
        select_threshold_from_table(
            table,
            minimum_precision=0.90,
        )


def test_invalid_minimum_precision_is_rejected() -> None:
    table = _example_table()

    with pytest.raises(
        ThresholdSelectionError,
        match="between 0 and 1",
    ):
        select_threshold_from_table(
            table,
            minimum_precision=1.1,
        )


def test_invalid_threshold_candidates_are_rejected() -> None:
    with pytest.raises(
        ThresholdSelectionError,
        match="between 0 and 1",
    ):
        evaluate_threshold_candidates(
            _example_target(),
            _example_probabilities(),
            thresholds=[
                -0.1,
                0.5,
            ],
        )
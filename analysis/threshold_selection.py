"""Select a TutorPulse decision threshold using validation data only.

The test split must remain untouched while the threshold is selected.
The selection rule prioritises recall while requiring a minimum level
of precision.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from analysis.model_data import (
    ModelSplit,
    load_prepared_model_data,
)
from analysis.model_training import (
    BinaryClassificationMetrics,
    DEFAULT_DECISION_THRESHOLD,
    build_logistic_pipeline,
    evaluate_probabilities,
    positive_class_probabilities,
)


DEFAULT_MINIMUM_PRECISION = 0.60

DEFAULT_THRESHOLD_CANDIDATES = tuple(
    value / 100
    for value in range(5, 96)
)


class ThresholdSelectionError(ValueError):
    """Raised when a decision threshold cannot be selected."""


@dataclass(frozen=True)
class ThresholdSelection:
    """The selected threshold and supporting validation results."""

    minimum_precision: float
    threshold: float
    metrics: BinaryClassificationMetrics
    table: pd.DataFrame


def evaluate_threshold_candidates(
    target: pd.Series,
    positive_probabilities: np.ndarray,
    *,
    thresholds: Iterable[float] = (
        DEFAULT_THRESHOLD_CANDIDATES
    ),
) -> pd.DataFrame:
    """Evaluate validation predictions across candidate thresholds."""

    try:
        threshold_values = [
            float(value)
            for value in thresholds
        ]
    except (TypeError, ValueError) as error:
        raise ThresholdSelectionError(
            "Threshold candidates must be numeric."
        ) from error

    if not threshold_values:
        raise ThresholdSelectionError(
            "At least one threshold candidate is required."
        )

    if len(threshold_values) != len(set(threshold_values)):
        raise ThresholdSelectionError(
            "Threshold candidates must not contain duplicates."
        )

    if not all(
        0.0 <= value <= 1.0
        for value in threshold_values
    ):
        raise ThresholdSelectionError(
            "Threshold candidates must be between 0 and 1."
        )

    records: list[dict[str, float | int]] = []

    for threshold in sorted(threshold_values):
        metrics = evaluate_probabilities(
            target,
            positive_probabilities,
            threshold=threshold,
        )
        records.append(metrics.as_dict())

    return pd.DataFrame.from_records(records)


def select_threshold_from_table(
    table: pd.DataFrame,
    *,
    minimum_precision: float = DEFAULT_MINIMUM_PRECISION,
) -> tuple[float, BinaryClassificationMetrics]:
    """Select the highest-recall threshold meeting a precision floor."""

    if not 0.0 <= minimum_precision <= 1.0:
        raise ThresholdSelectionError(
            "Minimum precision must be between 0 and 1."
        )

    required_columns = {
        "threshold",
        "accuracy",
        "balanced_accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "average_precision",
        "specificity",
        "true_negatives",
        "false_positives",
        "false_negatives",
        "true_positives",
    }

    missing_columns = required_columns - set(table.columns)

    if missing_columns:
        names = ", ".join(sorted(missing_columns))
        raise ThresholdSelectionError(
            f"Threshold table is missing columns: {names}"
        )

    feasible = table.loc[
        table["precision"] >= minimum_precision
    ].copy()

    if feasible.empty:
        raise ThresholdSelectionError(
            "No threshold satisfies the minimum precision rule."
        )

    ranked = feasible.sort_values(
        by=[
            "recall",
            "f1",
            "precision",
            "threshold",
        ],
        ascending=[
            False,
            False,
            False,
            True,
        ],
        kind="stable",
    )

    selected_row = ranked.iloc[0]
    selected_threshold = float(
        selected_row["threshold"]
    )

    metrics = BinaryClassificationMetrics(
        threshold=selected_threshold,
        accuracy=float(selected_row["accuracy"]),
        balanced_accuracy=float(
            selected_row["balanced_accuracy"]
        ),
        precision=float(selected_row["precision"]),
        recall=float(selected_row["recall"]),
        f1=float(selected_row["f1"]),
        roc_auc=float(selected_row["roc_auc"]),
        average_precision=float(
            selected_row["average_precision"]
        ),
        specificity=float(selected_row["specificity"]),
        true_negatives=int(
            selected_row["true_negatives"]
        ),
        false_positives=int(
            selected_row["false_positives"]
        ),
        false_negatives=int(
            selected_row["false_negatives"]
        ),
        true_positives=int(
            selected_row["true_positives"]
        ),
    )

    return selected_threshold, metrics


def select_validation_threshold(
    model: Pipeline,
    validation_split: ModelSplit,
    *,
    minimum_precision: float = DEFAULT_MINIMUM_PRECISION,
    thresholds: Iterable[float] = (
        DEFAULT_THRESHOLD_CANDIDATES
    ),
) -> ThresholdSelection:
    """Select a threshold from validation predictions only."""

    probabilities = positive_class_probabilities(
        model,
        validation_split.features,
    )

    table = evaluate_threshold_candidates(
        validation_split.target,
        probabilities,
        thresholds=thresholds,
    )

    threshold, metrics = select_threshold_from_table(
        table,
        minimum_precision=minimum_precision,
    )

    return ThresholdSelection(
        minimum_precision=minimum_precision,
        threshold=threshold,
        metrics=metrics,
        table=table,
    )


def main() -> None:
    """Train logistic regression and select its validation threshold."""

    prepared_data = load_prepared_model_data()

    model = build_logistic_pipeline()
    model.fit(
        prepared_data.train.features,
        prepared_data.train.target,
    )

    validation_probabilities = (
        positive_class_probabilities(
            model,
            prepared_data.validation.features,
        )
    )

    default_metrics = evaluate_probabilities(
        prepared_data.validation.target,
        validation_probabilities,
        threshold=DEFAULT_DECISION_THRESHOLD,
    )

    selection = select_validation_threshold(
        model,
        prepared_data.validation,
    )

    comparison = pd.DataFrame.from_dict(
        {
            "default_0.50": default_metrics.as_dict(),
            "selected": selection.metrics.as_dict(),
        },
        orient="index",
    )

    display_columns = [
        "threshold",
        "precision",
        "recall",
        "f1",
        "balanced_accuracy",
        "false_negatives",
        "false_positives",
    ]

    print(
        "Validation-only threshold selection"
    )
    print(
        "Rule: maximise recall while maintaining precision "
        f">= {selection.minimum_precision:.0%}"
    )
    print()
    print(
        comparison.loc[:, display_columns]
        .round(3)
        .to_string()
    )
    print()
    print(
        "Selected threshold: "
        f"{selection.threshold:.2f}"
    )
    print(
        "The test split has not been evaluated. "
        "It remains reserved for final evaluation."
    )


if __name__ == "__main__":
    main()
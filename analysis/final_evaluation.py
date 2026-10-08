"""Perform the final TutorPulse test-period evaluation.

The model design and decision threshold have already been selected
using training and validation data. This module applies that fixed
decision to the untouched chronological test period.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.pipeline import Pipeline

from analysis.model_data import (
    ModelSplit,
    PreparedModelData,
    load_prepared_model_data,
)
from analysis.model_training import (
    BinaryClassificationMetrics,
    DEFAULT_DECISION_THRESHOLD,
    build_baseline_pipeline,
    build_logistic_pipeline,
    evaluate_model,
    positive_class_probabilities,
)


FINAL_MODEL_NAME = "logistic_regression"
FINAL_DECISION_THRESHOLD = 0.38
VALIDATION_PRECISION_FLOOR = 0.60


@dataclass(frozen=True)
class FinalEvaluation:
    """Models and results from the final test-period evaluation."""

    baseline_model: Pipeline
    final_model: Pipeline
    baseline_metrics: BinaryClassificationMetrics
    final_model_metrics: BinaryClassificationMetrics
    test_predictions: pd.DataFrame


def build_test_predictions(
    model: Pipeline,
    test_split: ModelSplit,
    *,
    threshold: float = FINAL_DECISION_THRESHOLD,
) -> pd.DataFrame:
    """Build an auditable test-prediction table."""

    probabilities = positive_class_probabilities(
        model,
        test_split.features,
    )
    predictions = (
        probabilities >= threshold
    ).astype("int8")

    output = test_split.metadata.copy()
    output["actual_needs_support"] = (
        test_split.target.to_numpy()
    )
    output["support_probability"] = probabilities
    output["predicted_needs_support"] = predictions
    output["prediction_correct"] = (
        output["actual_needs_support"]
        == output["predicted_needs_support"]
    )

    return output


def run_final_evaluation(
    prepared_data: PreparedModelData,
) -> FinalEvaluation:
    """Train fixed models and evaluate the untouched test period."""

    baseline_model = build_baseline_pipeline()
    baseline_model.fit(
        prepared_data.train.features,
        prepared_data.train.target,
    )

    final_model = build_logistic_pipeline()
    final_model.fit(
        prepared_data.train.features,
        prepared_data.train.target,
    )

    baseline_metrics = evaluate_model(
        baseline_model,
        prepared_data.test,
        threshold=DEFAULT_DECISION_THRESHOLD,
    )

    final_model_metrics = evaluate_model(
        final_model,
        prepared_data.test,
        threshold=FINAL_DECISION_THRESHOLD,
    )

    test_predictions = build_test_predictions(
        final_model,
        prepared_data.test,
        threshold=FINAL_DECISION_THRESHOLD,
    )

    return FinalEvaluation(
        baseline_model=baseline_model,
        final_model=final_model,
        baseline_metrics=baseline_metrics,
        final_model_metrics=final_model_metrics,
        test_predictions=test_predictions,
    )


def final_comparison(
    evaluation: FinalEvaluation,
) -> pd.DataFrame:
    """Return the final baseline and model comparison."""

    frame = pd.DataFrame.from_dict(
        {
            "dummy_baseline": (
                evaluation.baseline_metrics.as_dict()
            ),
            FINAL_MODEL_NAME: (
                evaluation.final_model_metrics.as_dict()
            ),
        },
        orient="index",
    )

    frame.index.name = "model"

    return frame


def main() -> None:
    """Run and print the final test-period evaluation."""

    prepared_data = load_prepared_model_data()
    evaluation = run_final_evaluation(prepared_data)
    comparison = final_comparison(evaluation)

    display_columns = [
        "threshold",
        "accuracy",
        "balanced_accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "average_precision",
        "specificity",
        "false_negatives",
        "false_positives",
    ]

    print("Final untouched test-period evaluation")
    print(
        comparison.loc[:, display_columns]
        .round(3)
        .to_string()
    )
    print()
    print(
        "Final model: "
        f"{FINAL_MODEL_NAME}"
    )
    print(
        "Fixed decision threshold: "
        f"{FINAL_DECISION_THRESHOLD:.2f}"
    )
    print(
        "Test rows evaluated: "
        f"{len(evaluation.test_predictions)}"
    )
    print()
    print(
        "These results describe performance on reproducible "
        "synthetic data. They do not establish effectiveness "
        "with real learners."
    )


if __name__ == "__main__":
    main()
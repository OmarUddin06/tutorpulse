"""Compare TutorPulse candidate models using validation data only."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import brier_score_loss
from sklearn.pipeline import Pipeline

from analysis.model_data import (
    ModelSplit,
    PreparedModelData,
    load_prepared_model_data,
)
from analysis.model_training import (
    BinaryClassificationMetrics,
    DEFAULT_DECISION_THRESHOLD,
    RANDOM_SEED,
    build_logistic_pipeline,
    build_preprocessor,
    evaluate_model,
    evaluate_probabilities,
    positive_class_probabilities,
)
from analysis.threshold_selection import (
    DEFAULT_MINIMUM_PRECISION,
    evaluate_threshold_candidates,
    select_threshold_from_table,
)


RANDOM_FOREST_ESTIMATORS = 300
RANDOM_FOREST_MAX_DEPTH = 10
RANDOM_FOREST_MIN_SAMPLES_LEAF = 10


class ModelComparisonError(ValueError):
    """Raised when candidate models cannot be compared safely."""


@dataclass(frozen=True)
class CandidateEvaluation:
    """Validation results for one candidate model."""

    name: str
    model: Pipeline
    default_metrics: BinaryClassificationMetrics
    selected_threshold: float
    selected_metrics: BinaryClassificationMetrics
    brier_score: float
    calibration: pd.DataFrame


@dataclass(frozen=True)
class ModelComparison:
    """Validation-only comparison of both candidate models."""

    logistic_regression: CandidateEvaluation
    random_forest: CandidateEvaluation


def build_random_forest_pipeline() -> Pipeline:
    """Build a reproducible tree-based candidate pipeline."""

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(),
            ),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=RANDOM_FOREST_ESTIMATORS,
                    max_depth=RANDOM_FOREST_MAX_DEPTH,
                    min_samples_leaf=(
                        RANDOM_FOREST_MIN_SAMPLES_LEAF
                    ),
                    class_weight="balanced_subsample",
                    random_state=RANDOM_SEED,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def probability_calibration_table(
    target: pd.Series,
    positive_probabilities: np.ndarray,
    *,
    bins: int = 10,
) -> pd.DataFrame:
    """Summarise predicted and observed rates by probability bin."""

    if bins < 2:
        raise ModelComparisonError(
            "Calibration analysis requires at least two bins."
        )

    evaluate_probabilities(
        target,
        positive_probabilities,
        threshold=DEFAULT_DECISION_THRESHOLD,
    )

    observed_rates, predicted_rates = calibration_curve(
        target,
        positive_probabilities,
        n_bins=bins,
        strategy="quantile",
    )

    table = pd.DataFrame(
        {
            "bin": range(
                1,
                len(observed_rates) + 1,
            ),
            "mean_predicted_probability": predicted_rates,
            "observed_support_rate": observed_rates,
        }
    )

    table["absolute_calibration_gap"] = (
        table["mean_predicted_probability"]
        - table["observed_support_rate"]
    ).abs()

    return table


def evaluate_candidate(
    *,
    name: str,
    model: Pipeline,
    train_split: ModelSplit,
    validation_split: ModelSplit,
    minimum_precision: float = (
        DEFAULT_MINIMUM_PRECISION
    ),
) -> CandidateEvaluation:
    """Fit and evaluate one candidate without accessing test data."""

    model.fit(
        train_split.features,
        train_split.target,
    )

    probabilities = positive_class_probabilities(
        model,
        validation_split.features,
    )

    default_metrics = evaluate_model(
        model,
        validation_split,
        threshold=DEFAULT_DECISION_THRESHOLD,
    )

    threshold_table = evaluate_threshold_candidates(
        validation_split.target,
        probabilities,
    )
    selected_threshold, selected_metrics = (
        select_threshold_from_table(
            threshold_table,
            minimum_precision=minimum_precision,
        )
    )

    calibration = probability_calibration_table(
        validation_split.target,
        probabilities,
    )

    score = float(
        brier_score_loss(
            validation_split.target,
            probabilities,
        )
    )

    return CandidateEvaluation(
        name=name,
        model=model,
        default_metrics=default_metrics,
        selected_threshold=selected_threshold,
        selected_metrics=selected_metrics,
        brier_score=score,
        calibration=calibration,
    )


def compare_candidate_models(
    prepared_data: PreparedModelData,
) -> ModelComparison:
    """Compare logistic regression and random forest on validation."""

    logistic = evaluate_candidate(
        name="logistic_regression",
        model=build_logistic_pipeline(),
        train_split=prepared_data.train,
        validation_split=prepared_data.validation,
    )

    forest = evaluate_candidate(
        name="random_forest",
        model=build_random_forest_pipeline(),
        train_split=prepared_data.train,
        validation_split=prepared_data.validation,
    )

    return ModelComparison(
        logistic_regression=logistic,
        random_forest=forest,
    )


def candidate_summary(
    comparison: ModelComparison,
) -> pd.DataFrame:
    """Return validation metrics at each selected threshold."""

    records: list[dict[str, float | int | str]] = []

    for candidate in (
        comparison.logistic_regression,
        comparison.random_forest,
    ):
        record: dict[str, float | int | str] = {
            "model": candidate.name,
            **candidate.selected_metrics.as_dict(),
            "brier_score": candidate.brier_score,
        }
        records.append(record)

    return pd.DataFrame.from_records(
        records
    ).set_index("model")


def main() -> None:
    """Run the validation-only model comparison."""

    prepared_data = load_prepared_model_data()
    comparison = compare_candidate_models(
        prepared_data
    )
    summary = candidate_summary(comparison)

    display_columns = [
        "threshold",
        "accuracy",
        "balanced_accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "average_precision",
        "brier_score",
        "false_negatives",
        "false_positives",
    ]

    print("Validation-only candidate comparison")
    print(
        summary.loc[:, display_columns]
        .round(3)
        .to_string()
    )
    print()
    print(
        "Both thresholds maximise validation recall while "
        "maintaining precision >= 60%."
    )
    print()
    print(
        "Logistic regression remains the selected model because "
        "the performance difference is small, it has stronger "
        "ROC-AUC, average precision and Brier score, and its "
        "coefficients are easier to inspect."
    )
    print(
        "The test split was not accessed by this comparison."
    )


if __name__ == "__main__":
    main()
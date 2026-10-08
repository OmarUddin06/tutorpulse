"""Analyse TutorPulse prediction errors and non-sensitive subgroups."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline

from analysis.final_evaluation import (
    FINAL_DECISION_THRESHOLD,
)
from analysis.model_data import (
    ModelSplit,
    PreparedModelData,
    load_prepared_model_data,
)
from analysis.model_training import (
    build_logistic_pipeline,
    positive_class_probabilities,
)


HISTORY_BINS = (
    float("-inf"),
    20,
    40,
    60,
    float("inf"),
)

HISTORY_LABELS = (
    "limited_1_to_20",
    "developing_21_to_40",
    "established_41_to_60",
    "extensive_61_plus",
)


class ErrorAnalysisError(ValueError):
    """Raised when prediction errors cannot be analysed."""


@dataclass(frozen=True)
class ErrorAnalysis:
    """Validation errors, subgroup results and split summaries."""

    predictions: pd.DataFrame
    error_counts: pd.DataFrame
    topic_performance: pd.DataFrame
    history_performance: pd.DataFrame
    split_distribution: pd.DataFrame


def assign_history_band(
    prior_result_count: pd.Series,
) -> pd.Series:
    """Assign fixed, interpretable learner-history bands."""

    try:
        numeric_counts = pd.to_numeric(
            prior_result_count,
            errors="raise",
        )
    except (TypeError, ValueError) as error:
        raise ErrorAnalysisError(
            "Prior-result counts must be numeric."
        ) from error

    if numeric_counts.isna().any():
        raise ErrorAnalysisError(
            "Prior-result counts must not be missing."
        )

    if (numeric_counts < 0).any():
        raise ErrorAnalysisError(
            "Prior-result counts must not be negative."
        )

    return pd.cut(
        numeric_counts,
        bins=HISTORY_BINS,
        labels=HISTORY_LABELS,
        right=True,
    )


def build_prediction_frame(
    model: Pipeline,
    split: ModelSplit,
    *,
    threshold: float = FINAL_DECISION_THRESHOLD,
) -> pd.DataFrame:
    """Create an auditable prediction and error table."""

    required_features = {
        "topic_name",
        "prior_result_count",
    }

    missing_features = (
        required_features
        - set(split.features.columns)
    )

    if missing_features:
        names = ", ".join(sorted(missing_features))
        raise ErrorAnalysisError(
            f"Prediction frame is missing features: {names}"
        )

    probabilities = positive_class_probabilities(
        model,
        split.features,
    )
    predictions = (
        probabilities >= threshold
    ).astype("int8")
    actual = split.target.to_numpy(dtype="int8")

    output = split.metadata.copy()
    output["topic_name"] = (
        split.features["topic_name"].to_numpy()
    )
    output["prior_result_count"] = (
        split.features[
            "prior_result_count"
        ].to_numpy()
    )
    output["history_band"] = assign_history_band(
        output["prior_result_count"]
    )
    output["actual_needs_support"] = actual
    output["support_probability"] = probabilities
    output["predicted_needs_support"] = predictions

    output["error_type"] = np.select(
        [
            (actual == 1) & (predictions == 0),
            (actual == 0) & (predictions == 1),
            (actual == 1) & (predictions == 1),
        ],
        [
            "false_negative",
            "false_positive",
            "true_positive",
        ],
        default="true_negative",
    )

    return output


def error_count_table(
    predictions: pd.DataFrame,
) -> pd.DataFrame:
    """Count each prediction outcome."""

    counts = (
        predictions["error_type"]
        .value_counts()
        .reindex(
            [
                "true_negative",
                "false_positive",
                "false_negative",
                "true_positive",
            ],
            fill_value=0,
        )
        .rename_axis("error_type")
        .reset_index(name="rows")
    )

    counts["percentage"] = (
        counts["rows"]
        / len(predictions)
    )

    return counts


def performance_by_group(
    predictions: pd.DataFrame,
    group_column: str,
) -> pd.DataFrame:
    """Calculate classification metrics for each supplied group."""

    required_columns = {
        group_column,
        "actual_needs_support",
        "predicted_needs_support",
        "support_probability",
    }

    missing_columns = (
        required_columns
        - set(predictions.columns)
    )

    if missing_columns:
        names = ", ".join(sorted(missing_columns))
        raise ErrorAnalysisError(
            f"Grouped analysis is missing columns: {names}"
        )

    records: list[dict[str, object]] = []

    grouped = predictions.groupby(
        group_column,
        observed=True,
        dropna=False,
        sort=False,
    )

    for group_value, group in grouped:
        actual = group[
            "actual_needs_support"
        ].to_numpy(dtype="int8")
        predicted = group[
            "predicted_needs_support"
        ].to_numpy(dtype="int8")
        probabilities = group[
            "support_probability"
        ].to_numpy(dtype=float)

        (
            true_negatives,
            false_positives,
            false_negatives,
            true_positives,
        ) = confusion_matrix(
            actual,
            predicted,
            labels=[0, 1],
        ).ravel()

        both_classes = (
            set(np.unique(actual)) == {0, 1}
        )

        record: dict[str, object] = {
            group_column: str(group_value),
            "rows": len(group),
            "support_rate": float(actual.mean()),
            "predicted_support_rate": float(
                predicted.mean()
            ),
            "precision": float(
                precision_score(
                    actual,
                    predicted,
                    zero_division=0,
                )
            ),
            "recall": float(
                recall_score(
                    actual,
                    predicted,
                    zero_division=0,
                )
            ),
            "f1": float(
                f1_score(
                    actual,
                    predicted,
                    zero_division=0,
                )
            ),
            "balanced_accuracy": (
                float(
                    balanced_accuracy_score(
                        actual,
                        predicted,
                    )
                )
                if both_classes
                else float("nan")
            ),
            "roc_auc": (
                float(
                    roc_auc_score(
                        actual,
                        probabilities,
                    )
                )
                if both_classes
                else float("nan")
            ),
            "average_precision": (
                float(
                    average_precision_score(
                        actual,
                        probabilities,
                    )
                )
                if both_classes
                else float("nan")
            ),
            "true_negatives": int(true_negatives),
            "false_positives": int(false_positives),
            "false_negatives": int(false_negatives),
            "true_positives": int(true_positives),
        }

        records.append(record)

    return pd.DataFrame.from_records(records)


def split_distribution_summary(
    prepared_data: PreparedModelData,
) -> pd.DataFrame:
    """Summarise chronological target and history changes."""

    records: list[dict[str, object]] = []

    for split in (
        prepared_data.train,
        prepared_data.validation,
        prepared_data.test,
    ):
        dates = split.metadata["assessment_date"]
        history = split.features["prior_result_count"]

        records.append(
            {
                "split": split.name,
                "rows": split.row_count,
                "first_assessment_date": (
                    dates.min().date().isoformat()
                ),
                "last_assessment_date": (
                    dates.max().date().isoformat()
                ),
                "support_rate": float(
                    split.target.mean()
                ),
                "mean_prior_result_count": float(
                    history.mean()
                ),
                "median_prior_result_count": float(
                    history.median()
                ),
            }
        )

    return pd.DataFrame.from_records(
        records
    ).set_index("split")


def run_validation_error_analysis(
    prepared_data: PreparedModelData,
) -> ErrorAnalysis:
    """Run error analysis without using test predictions."""

    model = build_logistic_pipeline()
    model.fit(
        prepared_data.train.features,
        prepared_data.train.target,
    )

    predictions = build_prediction_frame(
        model,
        prepared_data.validation,
        threshold=FINAL_DECISION_THRESHOLD,
    )

    return ErrorAnalysis(
        predictions=predictions,
        error_counts=error_count_table(
            predictions
        ),
        topic_performance=performance_by_group(
            predictions,
            "topic_name",
        ),
        history_performance=performance_by_group(
            predictions,
            "history_band",
        ),
        split_distribution=split_distribution_summary(
            prepared_data
        ),
    )


def _rounded_table(
    frame: pd.DataFrame,
) -> str:
    return frame.round(3).to_string(
        index=False
    )


def main() -> None:
    """Print validation errors and subgroup summaries."""

    prepared_data = load_prepared_model_data()
    analysis = run_validation_error_analysis(
        prepared_data
    )

    print("Validation prediction outcomes")
    print(_rounded_table(analysis.error_counts))
    print()

    topic_columns = [
        "topic_name",
        "rows",
        "support_rate",
        "precision",
        "recall",
        "f1",
        "false_negatives",
        "false_positives",
    ]

    print("Validation performance by topic")
    print(
        _rounded_table(
            analysis.topic_performance.loc[
                :,
                topic_columns,
            ]
        )
    )
    print()

    history_columns = [
        "history_band",
        "rows",
        "support_rate",
        "precision",
        "recall",
        "f1",
        "false_negatives",
        "false_positives",
    ]

    print("Validation performance by learner-history band")
    print(
        _rounded_table(
            analysis.history_performance.loc[
                :,
                history_columns,
            ]
        )
    )
    print()

    print("Chronological distribution summary")
    print(
        analysis.split_distribution
        .round(3)
        .to_string()
    )
    print()

    print(
        "Subgroup differences describe synthetic data and "
        "must not be presented as evidence about real learners."
    )


if __name__ == "__main__":
    main()
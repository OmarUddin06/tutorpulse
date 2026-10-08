"""Train and validate TutorPulse classification models.

Model selection uses the training and validation periods only. The test
period remains untouched until the final model and decision threshold
have been selected.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from analysis.model_data import (
    ModelSplit,
    PreparedModelData,
    load_prepared_model_data,
)
from analysis.modelling import (
    CATEGORICAL_FEATURE_COLUMNS,
    MODEL_FEATURE_COLUMNS,
    NUMERIC_FEATURE_COLUMNS,
)


DEFAULT_DECISION_THRESHOLD = 0.5
RANDOM_SEED = 42


class ModelTrainingError(ValueError):
    """Raised when data cannot safely be used for model training."""


@dataclass(frozen=True)
class BinaryClassificationMetrics:
    """Evaluation metrics for one model and decision threshold."""

    threshold: float
    accuracy: float
    balanced_accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    average_precision: float
    specificity: float
    true_negatives: int
    false_positives: int
    false_negatives: int
    true_positives: int

    def as_dict(self) -> dict[str, float | int]:
        """Return metrics in a table-friendly dictionary."""

        return asdict(self)


@dataclass(frozen=True)
class ValidationRun:
    """Fitted models and their validation-period results."""

    baseline_model: Pipeline
    logistic_model: Pipeline
    baseline_metrics: BinaryClassificationMetrics
    logistic_metrics: BinaryClassificationMetrics


def _validate_feature_columns(
    features: pd.DataFrame,
    split_name: str,
) -> None:
    actual_columns = tuple(features.columns)

    if actual_columns != MODEL_FEATURE_COLUMNS:
        raise ModelTrainingError(
            f"{split_name} does not follow the ordered feature contract."
        )


def _binary_target_values(
    target: pd.Series,
    context: str,
) -> np.ndarray:
    try:
        values = pd.to_numeric(
            target,
            errors="raise",
        ).to_numpy()
    except (TypeError, ValueError) as error:
        raise ModelTrainingError(
            f"{context} target must be numeric."
        ) from error

    if len(values) == 0:
        raise ModelTrainingError(
            f"{context} target must not be empty."
        )

    if not np.isfinite(values).all():
        raise ModelTrainingError(
            f"{context} target must contain finite values."
        )

    unexpected_values = set(np.unique(values)) - {0, 1}

    if unexpected_values:
        found = ", ".join(
            str(value)
            for value in sorted(unexpected_values)
        )
        raise ModelTrainingError(
            f"{context} target must be binary; found: {found}"
        )

    return values.astype("int8")


def build_preprocessor() -> ColumnTransformer:
    """Build preprocessing fitted only on training data."""

    numerical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "one_hot",
                OneHotEncoder(
                    handle_unknown="ignore",
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_pipeline,
                list(NUMERIC_FEATURE_COLUMNS),
            ),
            (
                "categorical",
                categorical_pipeline,
                list(CATEGORICAL_FEATURE_COLUMNS),
            ),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def build_baseline_pipeline() -> Pipeline:
    """Build a majority-class baseline with identical preprocessing."""

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(),
            ),
            (
                "classifier",
                DummyClassifier(
                    strategy="most_frequent",
                ),
            ),
        ]
    )


def build_logistic_pipeline() -> Pipeline:
    """Build the first interpretable predictive model."""

    return Pipeline(
        steps=[
            (
                "preprocessor",
                build_preprocessor(),
            ),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2_000,
                    random_state=RANDOM_SEED,
                    solver="lbfgs",
                ),
            ),
        ]
    )


def positive_class_probabilities(
    model: Pipeline,
    features: pd.DataFrame,
) -> np.ndarray:
    """Return probabilities for the positive support class."""

    probabilities = model.predict_proba(features)
    classes = np.asarray(model.classes_)

    positive_indexes = np.flatnonzero(classes == 1)

    if len(positive_indexes) != 1:
        raise ModelTrainingError(
            "The fitted model does not contain exactly one positive class."
        )

    return np.asarray(
        probabilities[:, positive_indexes[0]],
        dtype=float,
    )


def evaluate_probabilities(
    target: pd.Series,
    positive_probabilities: np.ndarray,
    *,
    threshold: float = DEFAULT_DECISION_THRESHOLD,
) -> BinaryClassificationMetrics:
    """Evaluate positive-class probabilities at one threshold."""

    if not 0.0 <= threshold <= 1.0:
        raise ModelTrainingError(
            "The decision threshold must be between 0 and 1."
        )

    target_values = _binary_target_values(
        target,
        "Evaluation",
    )

    if set(np.unique(target_values)) != {0, 1}:
        raise ModelTrainingError(
            "Evaluation data must contain both target classes."
        )

    probability_values = np.asarray(
        positive_probabilities,
        dtype=float,
    )

    if probability_values.ndim != 1:
        raise ModelTrainingError(
            "Positive-class probabilities must be one-dimensional."
        )

    if len(probability_values) != len(target_values):
        raise ModelTrainingError(
            "Probability and target lengths do not match."
        )

    if not np.isfinite(probability_values).all():
        raise ModelTrainingError(
            "Probabilities must contain finite values."
        )

    if not (
        (probability_values >= 0.0)
        & (probability_values <= 1.0)
    ).all():
        raise ModelTrainingError(
            "Probabilities must be between 0 and 1."
        )

    predictions = (
        probability_values >= threshold
    ).astype("int8")

    (
        true_negatives,
        false_positives,
        false_negatives,
        true_positives,
    ) = confusion_matrix(
        target_values,
        predictions,
        labels=[0, 1],
    ).ravel()

    negative_total = true_negatives + false_positives
    specificity = (
        true_negatives / negative_total
        if negative_total
        else 0.0
    )

    return BinaryClassificationMetrics(
        threshold=float(threshold),
        accuracy=float(
            accuracy_score(
                target_values,
                predictions,
            )
        ),
        balanced_accuracy=float(
            balanced_accuracy_score(
                target_values,
                predictions,
            )
        ),
        precision=float(
            precision_score(
                target_values,
                predictions,
                zero_division=0,
            )
        ),
        recall=float(
            recall_score(
                target_values,
                predictions,
                zero_division=0,
            )
        ),
        f1=float(
            f1_score(
                target_values,
                predictions,
                zero_division=0,
            )
        ),
        roc_auc=float(
            roc_auc_score(
                target_values,
                probability_values,
            )
        ),
        average_precision=float(
            average_precision_score(
                target_values,
                probability_values,
            )
        ),
        specificity=float(specificity),
        true_negatives=int(true_negatives),
        false_positives=int(false_positives),
        false_negatives=int(false_negatives),
        true_positives=int(true_positives),
    )


def evaluate_model(
    model: Pipeline,
    split: ModelSplit,
    *,
    threshold: float = DEFAULT_DECISION_THRESHOLD,
) -> BinaryClassificationMetrics:
    """Evaluate a fitted model on one supplied split."""

    _validate_feature_columns(
        split.features,
        split.name,
    )

    probabilities = positive_class_probabilities(
        model,
        split.features,
    )

    return evaluate_probabilities(
        split.target,
        probabilities,
        threshold=threshold,
    )


def train_and_validate(
    prepared_data: PreparedModelData,
    *,
    threshold: float = DEFAULT_DECISION_THRESHOLD,
) -> ValidationRun:
    """Train models and evaluate them on validation data only."""

    _validate_feature_columns(
        prepared_data.train.features,
        "train",
    )
    _validate_feature_columns(
        prepared_data.validation.features,
        "validation",
    )

    train_target = _binary_target_values(
        prepared_data.train.target,
        "Training",
    )

    if set(np.unique(train_target)) != {0, 1}:
        raise ModelTrainingError(
            "Training data must contain both target classes."
        )

    baseline_model = build_baseline_pipeline()
    baseline_model.fit(
        prepared_data.train.features,
        train_target,
    )

    logistic_model = build_logistic_pipeline()
    logistic_model.fit(
        prepared_data.train.features,
        train_target,
    )

    baseline_metrics = evaluate_model(
        baseline_model,
        prepared_data.validation,
        threshold=threshold,
    )
    logistic_metrics = evaluate_model(
        logistic_model,
        prepared_data.validation,
        threshold=threshold,
    )

    return ValidationRun(
        baseline_model=baseline_model,
        logistic_model=logistic_model,
        baseline_metrics=baseline_metrics,
        logistic_metrics=logistic_metrics,
    )


def validation_comparison(
    run: ValidationRun,
) -> pd.DataFrame:
    """Build a readable validation-metric comparison table."""

    frame = pd.DataFrame.from_dict(
        {
            "dummy_baseline": (
                run.baseline_metrics.as_dict()
            ),
            "logistic_regression": (
                run.logistic_metrics.as_dict()
            ),
        },
        orient="index",
    )

    frame.index.name = "model"

    return frame


def main() -> None:
    """Train both models and print validation results."""

    prepared_data = load_prepared_model_data()
    run = train_and_validate(prepared_data)
    comparison = validation_comparison(run)

    display_columns = [
        "accuracy",
        "balanced_accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
        "average_precision",
        "false_negatives",
        "false_positives",
    ]

    print(
        "Validation metrics at decision threshold "
        f"{DEFAULT_DECISION_THRESHOLD:.2f}"
    )
    print(
        comparison.loc[:, display_columns]
        .round(3)
        .to_string()
    )
    print()
    print(
        "The test split has not been evaluated. "
        "It remains reserved for final evaluation."
    )


if __name__ == "__main__":
    main()
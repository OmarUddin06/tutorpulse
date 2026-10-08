"""Save and reload the selected TutorPulse modelling pipeline.

Joblib files use Python pickle internally. Only load model artifacts
created by this trusted project; never load an untrusted artifact.
"""

from __future__ import annotations

import json
import platform
from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.pipeline import Pipeline

from analysis.final_evaluation import (
    FINAL_DECISION_THRESHOLD,
    FINAL_MODEL_NAME,
)
from analysis.model_data import (
    ModelSplit,
    PreparedModelData,
    load_prepared_model_data,
)
from analysis.model_training import (
    RANDOM_SEED,
    build_logistic_pipeline,
    evaluate_model,
    positive_class_probabilities,
)
from analysis.modelling import (
    CATEGORICAL_FEATURE_COLUMNS,
    MODEL_FEATURE_COLUMNS,
    NUMERIC_FEATURE_COLUMNS,
    SUPPORT_THRESHOLD,
    TARGET_COLUMN,
)


ARTIFACT_SCHEMA_VERSION = 1
DEFAULT_ARTIFACT_DIRECTORY = Path(
    "artifacts/models"
)
PIPELINE_FILENAME = "tutorpulse_pipeline.joblib"
METADATA_FILENAME = "tutorpulse_metadata.json"


class ModelArtifactError(ValueError):
    """Raised when a model artifact violates its contract."""


@dataclass(frozen=True)
class ModelBundle:
    """A trusted fitted pipeline and its validated metadata."""

    pipeline: Pipeline
    metadata: dict[str, object]


def _split_summary(
    split: ModelSplit,
) -> dict[str, object]:
    dates = split.metadata["assessment_date"]

    return {
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
    }


def _validate_metadata(
    metadata: object,
) -> dict[str, object]:
    if not isinstance(metadata, dict):
        raise ModelArtifactError(
            "Model metadata must contain a JSON object."
        )

    if metadata.get("schema_version") != (
        ARTIFACT_SCHEMA_VERSION
    ):
        raise ModelArtifactError(
            "Unsupported model-artifact schema version."
        )

    if metadata.get("model_name") != FINAL_MODEL_NAME:
        raise ModelArtifactError(
            "Model metadata contains an unexpected model name."
        )

    try:
        threshold = float(
            metadata["decision_threshold"]
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ModelArtifactError(
            "Model metadata decision threshold must be numeric."
        ) from error

    if not np.isclose(
        threshold,
        FINAL_DECISION_THRESHOLD,
    ):
        raise ModelArtifactError(
            "Model metadata decision threshold does not match "
            "the locked model decision."
        )

    if metadata.get("target_column") != TARGET_COLUMN:
        raise ModelArtifactError(
            "Model metadata target column does not match."
        )

    if metadata.get("feature_columns") != list(
        MODEL_FEATURE_COLUMNS
    ):
        raise ModelArtifactError(
            "Model metadata feature order does not match."
        )

    if metadata.get(
        "categorical_feature_columns"
    ) != list(CATEGORICAL_FEATURE_COLUMNS):
        raise ModelArtifactError(
            "Model metadata categorical features do not match."
        )

    if metadata.get(
        "numeric_feature_columns"
    ) != list(NUMERIC_FEATURE_COLUMNS):
        raise ModelArtifactError(
            "Model metadata numerical features do not match."
        )

    try:
        recorded_support_threshold = float(
            metadata["support_threshold"]
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ModelArtifactError(
            "Model metadata support threshold must be numeric."
        ) from error

    if not np.isclose(
        recorded_support_threshold,
        SUPPORT_THRESHOLD,
    ):
        raise ModelArtifactError(
            "Model metadata support threshold does not match."
        )

    required_evaluations = {
        "validation",
        "test",
    }

    evaluations = metadata.get("evaluation")

    if not isinstance(evaluations, dict):
        raise ModelArtifactError(
            "Model metadata evaluation must be an object."
        )

    if set(evaluations) != required_evaluations:
        raise ModelArtifactError(
            "Model metadata must contain validation and test "
            "evaluation information."
        )

    return metadata


def _validate_pipeline(
    pipeline: object,
) -> Pipeline:
    if not isinstance(pipeline, Pipeline):
        raise ModelArtifactError(
            "Saved model is not a scikit-learn Pipeline."
        )

    required_steps = {
        "preprocessor",
        "classifier",
    }

    if not required_steps.issubset(
        pipeline.named_steps
    ):
        raise ModelArtifactError(
            "Saved pipeline is missing required steps."
        )

    if not hasattr(
        pipeline.named_steps["classifier"],
        "classes_",
    ):
        raise ModelArtifactError(
            "Saved pipeline classifier is not fitted."
        )

    return pipeline


def _validate_prediction_features(
    features: pd.DataFrame,
) -> None:
    expected = tuple(MODEL_FEATURE_COLUMNS)
    actual = tuple(features.columns)

    if actual == expected:
        return

    missing = set(expected) - set(actual)
    unexpected = set(actual) - set(expected)

    if missing:
        names = ", ".join(sorted(missing))
        raise ModelArtifactError(
            f"Prediction data is missing required features: {names}"
        )

    if unexpected:
        names = ", ".join(sorted(unexpected))
        raise ModelArtifactError(
            f"Prediction data contains unexpected features: {names}"
        )

    raise ModelArtifactError(
        "Prediction features do not follow the required order."
    )


def build_model_metadata(
    pipeline: Pipeline,
    prepared_data: PreparedModelData,
) -> dict[str, object]:
    """Build reproducible metadata for the selected pipeline."""

    validation_metrics = evaluate_model(
        pipeline,
        prepared_data.validation,
        threshold=FINAL_DECISION_THRESHOLD,
    )
    test_metrics = evaluate_model(
        pipeline,
        prepared_data.test,
        threshold=FINAL_DECISION_THRESHOLD,
    )

    metadata: dict[str, object] = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "model_name": FINAL_MODEL_NAME,
        "decision_threshold": (
            FINAL_DECISION_THRESHOLD
        ),
        "support_threshold": SUPPORT_THRESHOLD,
        "target_column": TARGET_COLUMN,
        "feature_columns": list(
            MODEL_FEATURE_COLUMNS
        ),
        "categorical_feature_columns": list(
            CATEGORICAL_FEATURE_COLUMNS
        ),
        "numeric_feature_columns": list(
            NUMERIC_FEATURE_COLUMNS
        ),
        "random_seed": RANDOM_SEED,
        "training_data": _split_summary(
            prepared_data.train
        ),
        "validation_data": _split_summary(
            prepared_data.validation
        ),
        "test_data": _split_summary(
            prepared_data.test
        ),
        "evaluation": {
            "validation": (
                validation_metrics.as_dict()
            ),
            "test": test_metrics.as_dict(),
        },
        "runtime": {
            "python_version": (
                platform.python_version()
            ),
            "scikit_learn_version": (
                sklearn.__version__
            ),
        },
        "limitations": [
            "The pipeline was trained on synthetic data.",
            "Predictions require human review.",
            "The model must not make automatic support decisions.",
            "Performance does not establish educational effectiveness.",
        ],
    }

    return _validate_metadata(metadata)


def save_model_artifact(
    prepared_data: PreparedModelData,
    artifact_directory: str | Path = (
        DEFAULT_ARTIFACT_DIRECTORY
    ),
) -> ModelBundle:
    """Fit and save the complete selected modelling pipeline."""

    directory = Path(artifact_directory)
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    pipeline = build_logistic_pipeline()
    pipeline.fit(
        prepared_data.train.features,
        prepared_data.train.target,
    )

    metadata = build_model_metadata(
        pipeline,
        prepared_data,
    )

    pipeline_path = directory / PIPELINE_FILENAME
    metadata_path = directory / METADATA_FILENAME

    joblib.dump(
        pipeline,
        pipeline_path,
    )
    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    return ModelBundle(
        pipeline=pipeline,
        metadata=metadata,
    )


def load_model_artifact(
    artifact_directory: str | Path = (
        DEFAULT_ARTIFACT_DIRECTORY
    ),
) -> ModelBundle:
    """Load a trusted pipeline and validate its metadata."""

    directory = Path(artifact_directory)
    pipeline_path = directory / PIPELINE_FILENAME
    metadata_path = directory / METADATA_FILENAME

    if not pipeline_path.is_file():
        raise ModelArtifactError(
            f"Pipeline artifact does not exist: {pipeline_path}"
        )

    if not metadata_path.is_file():
        raise ModelArtifactError(
            f"Metadata artifact does not exist: {metadata_path}"
        )

    try:
        metadata = json.loads(
            metadata_path.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as error:
        raise ModelArtifactError(
            "Model metadata is not valid JSON."
        ) from error

    validated_metadata = _validate_metadata(
        metadata
    )

    try:
        pipeline = joblib.load(
            pipeline_path
        )
    except Exception as error:
        raise ModelArtifactError(
            "The trusted pipeline artifact could not be loaded."
        ) from error

    validated_pipeline = _validate_pipeline(
        pipeline
    )

    return ModelBundle(
        pipeline=validated_pipeline,
        metadata=validated_metadata,
    )


def predict_support(
    bundle: ModelBundle,
    features: pd.DataFrame,
) -> pd.DataFrame:
    """Return probabilities and binary decisions."""

    _validate_prediction_features(features)

    probabilities = positive_class_probabilities(
        bundle.pipeline,
        features,
    )

    threshold = float(
        bundle.metadata["decision_threshold"]
    )
    predictions = (
        probabilities >= threshold
    ).astype("int8")

    return pd.DataFrame(
        {
            "support_probability": probabilities,
            "predicted_needs_support": predictions,
        },
        index=features.index,
    )


def main() -> None:
    """Save, reload and verify the selected model artifact."""

    prepared_data = load_prepared_model_data()

    original_bundle = save_model_artifact(
        prepared_data
    )
    loaded_bundle = load_model_artifact()

    original_predictions = predict_support(
        original_bundle,
        prepared_data.validation.features,
    )
    loaded_predictions = predict_support(
        loaded_bundle,
        prepared_data.validation.features,
    )

    if not np.allclose(
        original_predictions["support_probability"],
        loaded_predictions["support_probability"],
    ):
        raise ModelArtifactError(
            "Reloaded probabilities do not match the original."
        )

    if not (
        original_predictions["predicted_needs_support"]
        == loaded_predictions["predicted_needs_support"]
    ).all():
        raise ModelArtifactError(
            "Reloaded predictions do not match the original."
        )

    print(
        "Pipeline saved to: "
        f"{DEFAULT_ARTIFACT_DIRECTORY / PIPELINE_FILENAME}"
    )
    print(
        "Metadata saved to: "
        f"{DEFAULT_ARTIFACT_DIRECTORY / METADATA_FILENAME}"
    )
    print(
        "Model name: "
        f"{loaded_bundle.metadata['model_name']}"
    )
    print(
        "Decision threshold: "
        f"{loaded_bundle.metadata['decision_threshold']}"
    )
    print(
        "Feature count: "
        f"{len(loaded_bundle.metadata['feature_columns'])}"
    )
    print(
        "Reloaded predictions match the original predictions."
    )


if __name__ == "__main__":
    main()
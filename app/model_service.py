"""Application service for governed TutorPulse inference."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from analysis.model_artifact import (
    DEFAULT_ARTIFACT_DIRECTORY,
    ModelArtifactError,
    ModelBundle,
    load_model_artifact,
    predict_support,
)
from analysis.modelling import MODEL_FEATURE_COLUMNS
from app.inference_schemas import (
    ModelHealthResponse,
    SupportRiskRequest,
    SupportRiskResponse,
)


logger = logging.getLogger(__name__)


class ModelUnavailableError(RuntimeError):
    """Raised when no validated model bundle is available."""


class ModelPredictionError(RuntimeError):
    """Raised when the loaded model cannot make a prediction."""


@dataclass(frozen=True)
class ModelRuntimeState:
    """The model state shared by application requests."""

    bundle: ModelBundle | None
    load_error_category: str | None = None

    @property
    def is_ready(self) -> bool:
        """Return whether a validated bundle is available."""

        return self.bundle is not None


def load_model_runtime(
    artifact_directory: str | Path = (
        DEFAULT_ARTIFACT_DIRECTORY
    ),
) -> ModelRuntimeState:
    """Load the trusted artifact into application state."""

    try:
        bundle = load_model_artifact(
            artifact_directory
        )
    except (ModelArtifactError, OSError) as error:
        error_category = type(error).__name__

        logger.warning(
            "TutorPulse model artifact is unavailable: "
            "error_category=%s",
            error_category,
        )

        return ModelRuntimeState(
            bundle=None,
            load_error_category=error_category,
        )

    logger.info(
        "TutorPulse model artifact loaded: "
        "model_name=%s artifact_schema_version=%s",
        bundle.metadata["model_name"],
        bundle.metadata["schema_version"],
    )

    return ModelRuntimeState(
        bundle=bundle,
    )


def require_model_bundle(
    state: ModelRuntimeState,
) -> ModelBundle:
    """Return the bundle or report model unavailability."""

    if state.bundle is None:
        raise ModelUnavailableError(
            "Model inference is unavailable"
        )

    return state.bundle


def build_feature_frame(
    request: SupportRiskRequest,
) -> pd.DataFrame:
    """Convert one validated request into model input."""

    feature_values = request.model_dump(
        mode="python"
    )

    return pd.DataFrame(
        [feature_values],
        columns=MODEL_FEATURE_COLUMNS,
    )


def model_health_response(
    state: ModelRuntimeState,
) -> ModelHealthResponse:
    """Return governed metadata for a ready model."""

    bundle = require_model_bundle(state)
    metadata = bundle.metadata

    return ModelHealthResponse(
        model_name=str(
            metadata["model_name"]
        ),
        artifact_schema_version=int(
            metadata["schema_version"]
        ),
        decision_threshold=float(
            metadata["decision_threshold"]
        ),
    )


def predict_support_risk(
    state: ModelRuntimeState,
    request: SupportRiskRequest,
) -> SupportRiskResponse:
    """Return one prediction from the loaded pipeline."""

    bundle = require_model_bundle(state)
    features = build_feature_frame(request)

    try:
        prediction_table = predict_support(
            bundle,
            features,
        )
    except Exception as error:
        error_category = type(error).__name__

        logger.error(
            "TutorPulse model prediction failed: "
            "error_category=%s",
            error_category,
        )

        raise ModelPredictionError(
            "Model prediction failed"
        ) from error

    if len(prediction_table) != 1:
        raise ModelPredictionError(
            "Model prediction returned an unexpected "
            "number of rows"
        )

    required_columns = {
        "support_probability",
        "predicted_needs_support",
    }

    if not required_columns.issubset(
        prediction_table.columns
    ):
        raise ModelPredictionError(
            "Model prediction returned unexpected columns"
        )

    prediction = prediction_table.iloc[0]
    metadata = bundle.metadata

    return SupportRiskResponse(
        support_probability=float(
            prediction["support_probability"]
        ),
        predicted_needs_support=bool(
            prediction["predicted_needs_support"]
        ),
        decision_threshold=float(
            metadata["decision_threshold"]
        ),
        support_threshold=float(
            metadata["support_threshold"]
        ),
        model_name=str(
            metadata["model_name"]
        ),
        artifact_schema_version=int(
            metadata["schema_version"]
        ),
    )
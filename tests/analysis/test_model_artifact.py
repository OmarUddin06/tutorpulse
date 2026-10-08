import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from analysis.model_artifact import (
    METADATA_FILENAME,
    PIPELINE_FILENAME,
    ModelArtifactError,
    load_model_artifact,
    predict_support,
    save_model_artifact,
)
from analysis.model_data import (
    ModelSplit,
    PreparedModelData,
)
from analysis.modelling import (
    MODEL_FEATURE_COLUMNS,
    MODEL_METADATA_COLUMNS,
    NUMERIC_FEATURE_COLUMNS,
)


def _features(
    row_count: int,
) -> pd.DataFrame:
    index = np.arange(row_count)
    lower_performance = index % 2 == 1

    frame = pd.DataFrame(
        {
            column: index.astype(float) + 1.0
            for column in NUMERIC_FEATURE_COLUMNS
        }
    )

    frame["topic_name"] = np.where(
        lower_performance,
        "Fractions",
        "Algebra",
    )

    historical_average = np.where(
        lower_performance,
        45.0,
        78.0,
    )

    frame["maximum_score"] = 20.0
    frame["prior_average_percentage"] = (
        historical_average
    )
    frame["prior_minimum_percentage"] = (
        historical_average - 10.0
    )
    frame["prior_maximum_percentage"] = (
        historical_average + 10.0
    )
    frame[
        "previous_assessment_average_percentage"
    ] = historical_average
    frame[
        "prior_same_topic_average_percentage"
    ] = historical_average
    frame[
        "prior_same_topic_latest_percentage"
    ] = historical_average - 2.0
    frame["prior_support_rate"] = np.where(
        lower_performance,
        0.7,
        0.1,
    )
    frame["prior_support_count"] = np.where(
        lower_performance,
        3,
        0,
    )
    frame["prior_same_topic_support_count"] = np.where(
        lower_performance,
        2,
        0,
    )

    return frame.loc[
        :,
        MODEL_FEATURE_COLUMNS,
    ]


def _split(
    *,
    name: str,
    first_result_id: int,
    date: str,
    target: list[int],
) -> ModelSplit:
    row_count = len(target)

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
            "assessment_id": [
                first_result_id
            ]
            * row_count,
            "assessment_date": [
                datetime.fromisoformat(date)
            ]
            * row_count,
            "topic_id": [
                (value % 2) + 1
                for value in range(row_count)
            ],
            "result_percentage": [
                50.0
                if value
                else 75.0
                for value in target
            ],
        },
        columns=MODEL_METADATA_COLUMNS,
    )

    return ModelSplit(
        name=name,
        features=_features(row_count),
        target=pd.Series(
            target,
            name="needs_support",
            dtype="int8",
        ),
        metadata=metadata,
    )


def _prepared_data() -> PreparedModelData:
    return PreparedModelData(
        train=_split(
            name="train",
            first_result_id=1,
            date="2025-01-01",
            target=[
                0,
                1,
            ]
            * 10,
        ),
        validation=_split(
            name="validation",
            first_result_id=100,
            date="2025-02-01",
            target=[
                0,
                1,
            ]
            * 4,
        ),
        test=_split(
            name="test",
            first_result_id=200,
            date="2025-03-01",
            target=[
                1,
                0,
                1,
                0,
                1,
                0,
                1,
                0,
            ],
        ),
        manifest={},
    )


def test_artifact_files_and_metadata_are_created(
    tmp_path: Path,
) -> None:
    save_model_artifact(
        _prepared_data(),
        tmp_path,
    )

    assert (
        tmp_path / PIPELINE_FILENAME
    ).is_file()
    assert (
        tmp_path / METADATA_FILENAME
    ).is_file()

    metadata = json.loads(
        (
            tmp_path / METADATA_FILENAME
        ).read_text(encoding="utf-8")
    )

    assert metadata["model_name"] == (
        "logistic_regression"
    )
    assert metadata["decision_threshold"] == pytest.approx(
        0.38
    )
    assert metadata["feature_columns"] == list(
        MODEL_FEATURE_COLUMNS
    )


def test_loaded_predictions_match_original(
    tmp_path: Path,
) -> None:
    prepared = _prepared_data()

    original = save_model_artifact(
        prepared,
        tmp_path,
    )
    loaded = load_model_artifact(
        tmp_path
    )

    original_predictions = predict_support(
        original,
        prepared.validation.features,
    )
    loaded_predictions = predict_support(
        loaded,
        prepared.validation.features,
    )

    assert np.allclose(
        original_predictions["support_probability"],
        loaded_predictions["support_probability"],
    )
    assert (
        original_predictions["predicted_needs_support"]
        == loaded_predictions["predicted_needs_support"]
    ).all()


def test_prediction_shape_and_probability_range(
    tmp_path: Path,
) -> None:
    prepared = _prepared_data()
    bundle = save_model_artifact(
        prepared,
        tmp_path,
    )

    predictions = predict_support(
        bundle,
        prepared.validation.features,
    )

    assert predictions.shape == (
        len(prepared.validation.features),
        2,
    )
    assert predictions[
        "support_probability"
    ].between(0.0, 1.0).all()
    assert set(
        predictions[
            "predicted_needs_support"
        ].unique()
    ).issubset({0, 1})


def test_missing_feature_is_rejected(
    tmp_path: Path,
) -> None:
    prepared = _prepared_data()
    bundle = save_model_artifact(
        prepared,
        tmp_path,
    )

    incomplete = (
        prepared.validation.features.drop(
            columns=["prior_result_count"]
        )
    )

    with pytest.raises(
        ModelArtifactError,
        match="missing required features",
    ):
        predict_support(
            bundle,
            incomplete,
        )


def test_reordered_features_are_rejected(
    tmp_path: Path,
) -> None:
    prepared = _prepared_data()
    bundle = save_model_artifact(
        prepared,
        tmp_path,
    )

    reordered = prepared.validation.features.loc[
        :,
        list(reversed(MODEL_FEATURE_COLUMNS)),
    ]

    with pytest.raises(
        ModelArtifactError,
        match="required order",
    ):
        predict_support(
            bundle,
            reordered,
        )


def test_unknown_topic_is_handled_safely(
    tmp_path: Path,
) -> None:
    prepared = _prepared_data()
    bundle = save_model_artifact(
        prepared,
        tmp_path,
    )

    unknown_topic = (
        prepared.validation.features.copy()
    )
    unknown_topic["topic_name"] = "Calculus"

    predictions = predict_support(
        bundle,
        unknown_topic,
    )

    assert len(predictions) == len(
        unknown_topic
    )
    assert predictions[
        "support_probability"
    ].between(0.0, 1.0).all()


def test_invalid_metadata_is_rejected(
    tmp_path: Path,
) -> None:
    save_model_artifact(
        _prepared_data(),
        tmp_path,
    )

    metadata_path = (
        tmp_path / METADATA_FILENAME
    )
    metadata = json.loads(
        metadata_path.read_text(
            encoding="utf-8"
        )
    )
    metadata["decision_threshold"] = 0.99
    metadata_path.write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    with pytest.raises(
        ModelArtifactError,
        match="decision threshold",
    ):
        load_model_artifact(
            tmp_path
        )
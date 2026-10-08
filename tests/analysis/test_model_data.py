import json
from pathlib import Path

import pandas as pd
import pytest

from analysis.model_data import (
    ModelDataError,
    load_prepared_model_data,
)
from analysis.modelling import (
    MODEL_FEATURE_COLUMNS,
    MODEL_METADATA_COLUMNS,
    PROHIBITED_MODEL_COLUMNS,
    SUPPORT_THRESHOLD,
    TARGET_COLUMN,
)


def _make_row(
    *,
    result_id: int,
    assessment_id: int,
    assessment_date: str,
    topic_id: int,
    topic_name: str,
    needs_support: int,
) -> dict[str, object]:
    result_percentage = (
        50.0
        if needs_support
        else 75.0
    )

    return {
        "result_id": result_id,
        "learner_id": result_id,
        "assessment_id": assessment_id,
        "assessment_date": assessment_date,
        "topic_id": topic_id,
        "topic_name": topic_name,
        "maximum_score": 20.0,
        "prior_assessment_count": 2,
        "prior_result_count": 8,
        "prior_average_percentage": 64.0,
        "prior_minimum_percentage": 45.0,
        "prior_maximum_percentage": 82.0,
        "prior_support_count": 3,
        "prior_support_rate": 0.375,
        "previous_assessment_average_percentage": 62.0,
        "days_since_previous_assessment": 14,
        "prior_same_topic_count": 2,
        "prior_same_topic_average_percentage": 60.0,
        "prior_same_topic_latest_percentage": 58.0,
        "prior_same_topic_support_count": 1,
        "prior_intervention_count": 1,
        "prior_same_topic_intervention_count": 1,
        "prior_completed_intervention_count": 0,
        "result_percentage": result_percentage,
        "needs_support": needs_support,
    }


def _make_split(
    *,
    first_result_id: int,
    assessment_id: int,
    assessment_date: str,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            _make_row(
                result_id=first_result_id,
                assessment_id=assessment_id,
                assessment_date=assessment_date,
                topic_id=1,
                topic_name="Algebra",
                needs_support=0,
            ),
            _make_row(
                result_id=first_result_id + 1,
                assessment_id=assessment_id,
                assessment_date=assessment_date,
                topic_id=2,
                topic_name="Fractions",
                needs_support=1,
            ),
        ]
    )


def _split_summary(
    frame: pd.DataFrame,
) -> dict[str, object]:
    dates = pd.to_datetime(frame["assessment_date"])

    return {
        "rows": len(frame),
        "first_assessment_date": dates.min().date().isoformat(),
        "last_assessment_date": dates.max().date().isoformat(),
        "support_rate": float(frame[TARGET_COLUMN].mean()),
    }


def _write_prepared_fixture(
    directory: Path,
) -> dict[str, pd.DataFrame]:
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    frames = {
        "train": _make_split(
            first_result_id=1,
            assessment_id=1,
            assessment_date="2025-01-01",
        ),
        "validation": _make_split(
            first_result_id=3,
            assessment_id=2,
            assessment_date="2025-02-01",
        ),
        "test": _make_split(
            first_result_id=5,
            assessment_id=3,
            assessment_date="2025-03-01",
        ),
    }

    for split_name, frame in frames.items():
        frame.to_csv(
            directory / f"{split_name}.csv",
            index=False,
        )

    manifest = {
        "rows": sum(len(frame) for frame in frames.values()),
        "support_threshold": SUPPORT_THRESHOLD,
        "feature_columns": list(MODEL_FEATURE_COLUMNS),
        "target_column": TARGET_COLUMN,
        "splits": {
            split_name: _split_summary(frame)
            for split_name, frame in frames.items()
        },
    }

    (directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    return frames


def _read_manifest(
    directory: Path,
) -> dict[str, object]:
    return json.loads(
        (directory / "manifest.json").read_text(
            encoding="utf-8"
        )
    )


def _write_manifest(
    directory: Path,
    manifest: dict[str, object],
) -> None:
    (directory / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


def test_loader_separates_features_target_and_metadata(
    tmp_path: Path,
) -> None:
    _write_prepared_fixture(tmp_path)

    prepared = load_prepared_model_data(tmp_path)

    assert list(prepared.train.features.columns) == list(
        MODEL_FEATURE_COLUMNS
    )
    assert prepared.train.target.name == TARGET_COLUMN
    assert list(prepared.train.metadata.columns) == list(
        MODEL_METADATA_COLUMNS
    )
    assert not (
        set(prepared.train.features.columns)
        & PROHIBITED_MODEL_COLUMNS
    )
    assert prepared.train.row_count == 2
    assert prepared.validation.row_count == 2
    assert prepared.test.row_count == 2


def test_manifest_feature_drift_is_rejected(
    tmp_path: Path,
) -> None:
    _write_prepared_fixture(tmp_path)
    manifest = _read_manifest(tmp_path)

    manifest["feature_columns"] = list(
        reversed(MODEL_FEATURE_COLUMNS)
    )
    _write_manifest(tmp_path, manifest)

    with pytest.raises(
        ModelDataError,
        match="feature_columns",
    ):
        load_prepared_model_data(tmp_path)


def test_missing_required_feature_is_rejected(
    tmp_path: Path,
) -> None:
    frames = _write_prepared_fixture(tmp_path)

    train = frames["train"].drop(
        columns=["prior_result_count"]
    )
    train.to_csv(
        tmp_path / "train.csv",
        index=False,
    )

    with pytest.raises(
        ModelDataError,
        match="missing required columns",
    ):
        load_prepared_model_data(tmp_path)


def test_non_binary_target_is_rejected(
    tmp_path: Path,
) -> None:
    frames = _write_prepared_fixture(tmp_path)

    train = frames["train"].copy()
    train.loc[0, TARGET_COLUMN] = 2
    train.to_csv(
        tmp_path / "train.csv",
        index=False,
    )

    with pytest.raises(
        ModelDataError,
        match="must be binary",
    ):
        load_prepared_model_data(tmp_path)


def test_overlapping_result_ids_are_rejected(
    tmp_path: Path,
) -> None:
    frames = _write_prepared_fixture(tmp_path)

    validation = frames["validation"].copy()
    validation.loc[0, "result_id"] = 1
    validation.to_csv(
        tmp_path / "validation.csv",
        index=False,
    )

    with pytest.raises(
        ModelDataError,
        match="result_id values overlap",
    ):
        load_prepared_model_data(tmp_path)


def test_non_chronological_splits_are_rejected(
    tmp_path: Path,
) -> None:
    frames = _write_prepared_fixture(tmp_path)

    validation = frames["validation"].copy()
    validation["assessment_date"] = "2025-01-01"
    validation.to_csv(
        tmp_path / "validation.csv",
        index=False,
    )

    manifest = _read_manifest(tmp_path)
    split_summaries = manifest["splits"]
    split_summaries["validation"] = _split_summary(validation)
    _write_manifest(tmp_path, manifest)

    with pytest.raises(
        ModelDataError,
        match="strictly earlier",
    ):
        load_prepared_model_data(tmp_path)


def test_manifest_row_count_mismatch_is_rejected(
    tmp_path: Path,
) -> None:
    _write_prepared_fixture(tmp_path)
    manifest = _read_manifest(tmp_path)

    split_summaries = manifest["splits"]
    split_summaries["train"]["rows"] = 999
    _write_manifest(tmp_path, manifest)

    with pytest.raises(
        ModelDataError,
        match="row count",
    ):
        load_prepared_model_data(tmp_path)


def test_blank_categorical_value_is_rejected(
    tmp_path: Path,
) -> None:
    frames = _write_prepared_fixture(tmp_path)

    train = frames["train"].copy()
    train.loc[0, "topic_name"] = "   "
    train.to_csv(
        tmp_path / "train.csv",
        index=False,
    )

    with pytest.raises(
        ModelDataError,
        match="must not contain blank values",
    ):
        load_prepared_model_data(tmp_path)
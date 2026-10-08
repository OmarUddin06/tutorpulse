"""Load and validate leakage-safe TutorPulse modelling data."""

from __future__ import annotations

import json
import math
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from analysis.modelling import (
    CATEGORICAL_FEATURE_COLUMNS,
    IDENTIFIER_COLUMNS,
    MODEL_FEATURE_COLUMNS,
    MODEL_METADATA_COLUMNS,
    NUMERIC_FEATURE_COLUMNS,
    PROHIBITED_MODEL_COLUMNS,
    SPLIT_NAMES,
    SUPPORT_THRESHOLD,
    TARGET_COLUMN,
)


DEFAULT_PREPARED_DIRECTORY = Path("data/prepared")


class ModelDataError(ValueError):
    """Raised when prepared modelling data violates its contract."""


@dataclass(frozen=True)
class ModelSplit:
    """Features, target and metadata for one chronological split."""

    name: str
    features: pd.DataFrame
    target: pd.Series
    metadata: pd.DataFrame

    @property
    def row_count(self) -> int:
        """Return the number of rows in the split."""

        return len(self.features)


@dataclass(frozen=True)
class PreparedModelData:
    """The complete validated TutorPulse modelling dataset."""

    train: ModelSplit
    validation: ModelSplit
    test: ModelSplit
    manifest: dict[str, object]

    def get_split(self, name: str) -> ModelSplit:
        """Return a named split."""

        if name not in SPLIT_NAMES:
            expected = ", ".join(SPLIT_NAMES)
            raise KeyError(
                f"Unknown split {name!r}; expected one of: {expected}"
            )

        return getattr(self, name)


def _read_manifest(
    prepared_directory: Path,
) -> dict[str, object]:
    manifest_path = prepared_directory / "manifest.json"

    if not manifest_path.is_file():
        raise ModelDataError(
            f"Prepared-data manifest does not exist: {manifest_path}"
        )

    try:
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as error:
        raise ModelDataError(
            f"Prepared-data manifest is not valid JSON: {error}"
        ) from error

    if not isinstance(manifest, dict):
        raise ModelDataError(
            "Prepared-data manifest must contain a JSON object."
        )

    return manifest


def _validate_manifest_contract(
    manifest: Mapping[str, object],
) -> Mapping[str, object]:
    feature_columns = manifest.get("feature_columns")

    if feature_columns != list(MODEL_FEATURE_COLUMNS):
        raise ModelDataError(
            "Manifest feature_columns do not match the Stage 6 "
            "modelling contract."
        )

    if manifest.get("target_column") != TARGET_COLUMN:
        raise ModelDataError(
            "Manifest target_column does not match the modelling "
            f"contract: {TARGET_COLUMN!r}."
        )

    try:
        manifest_threshold = float(manifest["support_threshold"])
    except (KeyError, TypeError, ValueError) as error:
        raise ModelDataError(
            "Manifest support_threshold must be numeric."
        ) from error

    if not math.isclose(
        manifest_threshold,
        SUPPORT_THRESHOLD,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ModelDataError(
            "Manifest support_threshold does not match the modelling "
            f"contract: {SUPPORT_THRESHOLD}."
        )

    split_summaries = manifest.get("splits")

    if not isinstance(split_summaries, Mapping):
        raise ModelDataError(
            "Manifest splits must contain an object."
        )

    if set(split_summaries) != set(SPLIT_NAMES):
        raise ModelDataError(
            "Manifest must contain exactly the train, validation and "
            "test splits."
        )

    return split_summaries


def _validate_expected_columns(
    frame: pd.DataFrame,
    split_name: str,
) -> None:
    expected_columns = (
        set(MODEL_FEATURE_COLUMNS)
        | set(MODEL_METADATA_COLUMNS)
        | {TARGET_COLUMN}
    )
    actual_columns = set(frame.columns)

    missing_columns = expected_columns - actual_columns
    if missing_columns:
        names = ", ".join(sorted(missing_columns))
        raise ModelDataError(
            f"{split_name} is missing required columns: {names}"
        )

    unexpected_columns = actual_columns - expected_columns
    if unexpected_columns:
        names = ", ".join(sorted(unexpected_columns))
        raise ModelDataError(
            f"{split_name} contains unexpected columns: {names}"
        )


def _validate_identifier_columns(
    frame: pd.DataFrame,
    split_name: str,
) -> None:
    for column in IDENTIFIER_COLUMNS:
        try:
            numeric_values = pd.to_numeric(
                frame[column],
                errors="raise",
            )
        except (TypeError, ValueError) as error:
            raise ModelDataError(
                f"{split_name}.{column} must contain numeric IDs."
            ) from error

        if numeric_values.isna().any():
            raise ModelDataError(
                f"{split_name}.{column} must not contain missing IDs."
            )

        if not (numeric_values % 1 == 0).all():
            raise ModelDataError(
                f"{split_name}.{column} must contain whole-number IDs."
            )

        if not (numeric_values > 0).all():
            raise ModelDataError(
                f"{split_name}.{column} must contain positive IDs."
            )

        frame[column] = numeric_values.astype("int64")


def _validate_feature_values(
    frame: pd.DataFrame,
    split_name: str,
) -> None:
    for column in NUMERIC_FEATURE_COLUMNS:
        try:
            frame[column] = pd.to_numeric(
                frame[column],
                errors="raise",
            )
        except (TypeError, ValueError) as error:
            raise ModelDataError(
                f"{split_name}.{column} must contain numeric values."
            ) from error

    for column in CATEGORICAL_FEATURE_COLUMNS:
        if frame[column].isna().any():
            raise ModelDataError(
                f"{split_name}.{column} must not contain missing values."
            )

        text_values = frame[column].astype("string").str.strip()

        if text_values.eq("").any():
            raise ModelDataError(
                f"{split_name}.{column} must not contain blank values."
            )

        frame[column] = text_values


def _validate_target(
    frame: pd.DataFrame,
    split_name: str,
) -> None:
    try:
        target = pd.to_numeric(
            frame[TARGET_COLUMN],
            errors="raise",
        )
    except (TypeError, ValueError) as error:
        raise ModelDataError(
            f"{split_name}.{TARGET_COLUMN} must be numeric."
        ) from error

    if target.isna().any():
        raise ModelDataError(
            f"{split_name}.{TARGET_COLUMN} must not contain "
            "missing values."
        )

    unexpected_values = set(target.unique()) - {0, 1}

    if unexpected_values:
        values = ", ".join(
            str(value)
            for value in sorted(unexpected_values)
        )
        raise ModelDataError(
            f"{split_name}.{TARGET_COLUMN} must be binary; "
            f"found: {values}"
        )

    frame[TARGET_COLUMN] = target.astype("int8")


def _validate_outcome_metadata(
    frame: pd.DataFrame,
    split_name: str,
) -> None:
    try:
        percentages = pd.to_numeric(
            frame["result_percentage"],
            errors="raise",
        )
    except (TypeError, ValueError) as error:
        raise ModelDataError(
            f"{split_name}.result_percentage must be numeric."
        ) from error

    if percentages.isna().any():
        raise ModelDataError(
            f"{split_name}.result_percentage must not contain "
            "missing values."
        )

    if not percentages.between(0.0, 100.0).all():
        raise ModelDataError(
            f"{split_name}.result_percentage must be between "
            "0 and 100."
        )

    frame["result_percentage"] = percentages


def _validate_split_manifest_summary(
    split: ModelSplit,
    summary: object,
) -> None:
    if not isinstance(summary, Mapping):
        raise ModelDataError(
            f"Manifest summary for {split.name} must be an object."
        )

    expected_rows = summary.get("rows")

    if not isinstance(expected_rows, int):
        raise ModelDataError(
            f"Manifest row count for {split.name} must be an integer."
        )

    if expected_rows != split.row_count:
        raise ModelDataError(
            f"Manifest row count for {split.name} is "
            f"{expected_rows}, but the CSV contains "
            f"{split.row_count} rows."
        )

    dates = split.metadata["assessment_date"]
    actual_first_date = dates.min().date().isoformat()
    actual_last_date = dates.max().date().isoformat()

    if summary.get("first_assessment_date") != actual_first_date:
        raise ModelDataError(
            f"Manifest first assessment date for {split.name} "
            "does not match its CSV."
        )

    if summary.get("last_assessment_date") != actual_last_date:
        raise ModelDataError(
            f"Manifest last assessment date for {split.name} "
            "does not match its CSV."
        )

    try:
        expected_support_rate = float(summary["support_rate"])
    except (KeyError, TypeError, ValueError) as error:
        raise ModelDataError(
            f"Manifest support rate for {split.name} must be numeric."
        ) from error

    actual_support_rate = float(split.target.mean())

    if not math.isclose(
        expected_support_rate,
        actual_support_rate,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ModelDataError(
            f"Manifest support rate for {split.name} does not "
            "match its CSV."
        )


def _load_split(
    prepared_directory: Path,
    split_name: str,
    summary: object,
) -> ModelSplit:
    split_path = prepared_directory / f"{split_name}.csv"

    if not split_path.is_file():
        raise ModelDataError(
            f"Prepared split does not exist: {split_path}"
        )

    frame = pd.read_csv(split_path)

    if frame.empty:
        raise ModelDataError(
            f"Prepared split is empty: {split_name}"
        )

    _validate_expected_columns(frame, split_name)

    try:
        frame["assessment_date"] = pd.to_datetime(
            frame["assessment_date"],
            errors="raise",
        )
    except (TypeError, ValueError) as error:
        raise ModelDataError(
            f"{split_name}.assessment_date contains invalid dates."
        ) from error

    if frame["assessment_date"].isna().any():
        raise ModelDataError(
            f"{split_name}.assessment_date must not contain "
            "missing values."
        )

    _validate_identifier_columns(frame, split_name)
    _validate_feature_values(frame, split_name)
    _validate_target(frame, split_name)
    _validate_outcome_metadata(frame, split_name)

    if frame["result_id"].duplicated().any():
        raise ModelDataError(
            f"{split_name} contains duplicate result_id values."
        )

    features = frame.loc[:, MODEL_FEATURE_COLUMNS].copy()
    target = frame.loc[:, TARGET_COLUMN].copy()
    metadata = frame.loc[:, MODEL_METADATA_COLUMNS].copy()

    if set(features.columns) & PROHIBITED_MODEL_COLUMNS:
        raise ModelDataError(
            f"{split_name} features contain prohibited model columns."
        )

    split = ModelSplit(
        name=split_name,
        features=features,
        target=target,
        metadata=metadata,
    )

    _validate_split_manifest_summary(split, summary)

    return split


def _validate_split_relationships(
    train: ModelSplit,
    validation: ModelSplit,
    test: ModelSplit,
    manifest: Mapping[str, object],
) -> None:
    splits = (train, validation, test)

    for index, left_split in enumerate(splits):
        left_ids = set(left_split.metadata["result_id"])

        for right_split in splits[index + 1 :]:
            right_ids = set(right_split.metadata["result_id"])
            overlap = left_ids & right_ids

            if overlap:
                raise ModelDataError(
                    "result_id values overlap between "
                    f"{left_split.name} and {right_split.name}."
                )

    train_last_date = train.metadata["assessment_date"].max()
    validation_first_date = (
        validation.metadata["assessment_date"].min()
    )
    validation_last_date = (
        validation.metadata["assessment_date"].max()
    )
    test_first_date = test.metadata["assessment_date"].min()

    if train_last_date >= validation_first_date:
        raise ModelDataError(
            "The final train date must be strictly earlier than "
            "the first validation date."
        )

    if validation_last_date >= test_first_date:
        raise ModelDataError(
            "The final validation date must be strictly earlier "
            "than the first test date."
        )

    expected_total_rows = manifest.get("rows")

    if not isinstance(expected_total_rows, int):
        raise ModelDataError(
            "Manifest total row count must be an integer."
        )

    actual_total_rows = sum(
        split.row_count
        for split in splits
    )

    if expected_total_rows != actual_total_rows:
        raise ModelDataError(
            "Manifest total row count does not match the combined "
            "train, validation and test CSV files."
        )


def load_prepared_model_data(
    prepared_directory: str | Path = DEFAULT_PREPARED_DIRECTORY,
) -> PreparedModelData:
    """Load and fully validate all prepared modelling splits."""

    directory = Path(prepared_directory)
    manifest = _read_manifest(directory)
    split_summaries = _validate_manifest_contract(manifest)

    train = _load_split(
        directory,
        "train",
        split_summaries["train"],
    )
    validation = _load_split(
        directory,
        "validation",
        split_summaries["validation"],
    )
    test = _load_split(
        directory,
        "test",
        split_summaries["test"],
    )

    _validate_split_relationships(
        train,
        validation,
        test,
        manifest,
    )

    return PreparedModelData(
        train=train,
        validation=validation,
        test=test,
        manifest=manifest,
    )
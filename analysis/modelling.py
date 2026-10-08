"""Shared modelling definitions for TutorPulse.

This module defines the exact columns that may be supplied to a model.
Keeping this contract in one place reduces the risk of accidental target
leakage or feature drift between training and evaluation.
"""

from analysis.modelling_dataset import (
    MODEL_FEATURE_COLUMNS as PREPARED_FEATURE_COLUMNS,
)
from analysis.modelling_dataset import (
    SUPPORT_THRESHOLD as PREPARED_SUPPORT_THRESHOLD,
)
from analysis.modelling_dataset import (
    TARGET_COLUMN as PREPARED_TARGET_COLUMN,
)


SUPPORT_THRESHOLD = float(PREPARED_SUPPORT_THRESHOLD)
TARGET_COLUMN = PREPARED_TARGET_COLUMN

MODEL_FEATURE_COLUMNS = tuple(PREPARED_FEATURE_COLUMNS)

CATEGORICAL_FEATURE_COLUMNS = (
    "topic_name",
)

NUMERIC_FEATURE_COLUMNS = tuple(
    column
    for column in MODEL_FEATURE_COLUMNS
    if column not in CATEGORICAL_FEATURE_COLUMNS
)

IDENTIFIER_COLUMNS = (
    "result_id",
    "learner_id",
    "assessment_id",
    "topic_id",
)

MODEL_METADATA_COLUMNS = (
    "result_id",
    "learner_id",
    "assessment_id",
    "assessment_date",
    "topic_id",
    "result_percentage",
)

SPLIT_NAMES = (
    "train",
    "validation",
    "test",
)

PROHIBITED_MODEL_COLUMNS = frozenset(
    {
        *IDENTIFIER_COLUMNS,
        "assessment_date",
        "result_percentage",
        TARGET_COLUMN,
        "score",
        "display_name",
        "summary",
        "status",
        "created_at",
        "completed_at",
    }
)

leaked_columns = (
    set(MODEL_FEATURE_COLUMNS)
    & PROHIBITED_MODEL_COLUMNS
)

if leaked_columns:
    names = ", ".join(sorted(leaked_columns))
    raise RuntimeError(
        "The modelling feature contract contains prohibited columns: "
        f"{names}"
    )
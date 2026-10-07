import json
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from analysis.modelling_dataset import (
    MODEL_FEATURE_COLUMNS,
    TARGET_COLUMN,
    build_modelling_dataset,
    chronological_split,
    write_prepared_dataset,
)


@pytest.fixture()
def small_tables() -> dict[str, pd.DataFrame]:
    """Create a small timeline with known expected history."""

    learners = pd.DataFrame(
        [
            {
                "id": 1,
                "display_name": "Synthetic Learner 001",
                "created_at": pd.Timestamp(
                    "2024-12-01 09:00",
                    tz="UTC",
                ),
            }
        ]
    )

    topics = pd.DataFrame(
        [
            {
                "id": 1,
                "name": "Algebra",
                "description": "Synthetic Algebra topic.",
                "created_at": pd.Timestamp(
                    "2024-12-01 09:00",
                    tz="UTC",
                ),
            },
            {
                "id": 2,
                "name": "Fractions",
                "description": "Synthetic Fractions topic.",
                "created_at": pd.Timestamp(
                    "2024-12-01 09:00",
                    tz="UTC",
                ),
            },
        ]
    )

    assessment_dates = [
        date(2025, 1, 1),
        date(2025, 1, 15),
        date(2025, 1, 29),
        date(2025, 2, 12),
    ]

    assessments = pd.DataFrame(
        [
            {
                "id": assessment_id,
                "title": f"Assessment {assessment_id}",
                "assessment_date": assessment_date,
                "created_at": pd.Timestamp(
                    assessment_date - pd.Timedelta(days=7),
                    tz="UTC",
                ),
            }
            for assessment_id, assessment_date in enumerate(
                assessment_dates,
                start=1,
            )
        ]
    )

    percentages_by_assessment = {
        1: {
            1: 50.0,
            2: 70.0,
        },
        2: {
            1: 60.0,
            2: 80.0,
        },
        3: {
            1: 40.0,
            2: 90.0,
        },
        4: {
            1: 75.0,
            2: 55.0,
        },
    }

    result_records = []
    result_id = 1

    for assessment_id, assessment_date in enumerate(
        assessment_dates,
        start=1,
    ):
        for topic_id in (1, 2):
            result_records.append(
                {
                    "id": result_id,
                    "learner_id": 1,
                    "assessment_id": assessment_id,
                    "topic_id": topic_id,
                    "score": (
                        percentages_by_assessment[
                            assessment_id
                        ][topic_id]
                    ),
                    "maximum_score": 100.0,
                    "created_at": pd.Timestamp(
                        assessment_date,
                        tz="UTC",
                    )
                    + pd.Timedelta(hours=17),
                }
            )

            result_id += 1

    assessment_results = pd.DataFrame(result_records)

    interventions = pd.DataFrame(
        [
            {
                "id": 1,
                "learner_id": 1,
                "topic_id": 1,
                "summary": "Completed Algebra support.",
                "status": "completed",
                "created_at": pd.Timestamp(
                    "2025-01-10 09:00",
                    tz="UTC",
                ),
                "completed_at": pd.Timestamp(
                    "2025-01-12 16:00",
                    tz="UTC",
                ),
            },
            {
                "id": 2,
                "learner_id": 1,
                "topic_id": 2,
                "summary": "Active Fractions support.",
                "status": "active",
                "created_at": pd.Timestamp(
                    "2025-01-15 09:00",
                    tz="UTC",
                ),
                "completed_at": pd.NaT,
            },
            {
                "id": 3,
                "learner_id": 1,
                "topic_id": 1,
                "summary": "Later Algebra support.",
                "status": "completed",
                "created_at": pd.Timestamp(
                    "2025-02-01 09:00",
                    tz="UTC",
                ),
                "completed_at": pd.Timestamp(
                    "2025-02-20 16:00",
                    tz="UTC",
                ),
            },
        ]
    )

    return {
        "learners": learners,
        "topics": topics,
        "assessments": assessments,
        "assessment_results": assessment_results,
        "interventions": interventions,
    }


def test_first_assessment_is_excluded_and_history_is_correct(
    small_tables: dict[str, pd.DataFrame],
) -> None:
    """Rows require an earlier assessment and correct aggregates."""

    dataset = build_modelling_dataset(small_tables)

    assert len(dataset) == 6
    assert dataset["assessment_date"].min() == date(
        2025,
        1,
        15,
    )

    target = dataset.loc[
        dataset["assessment_date"].eq(date(2025, 1, 15))
        & dataset["topic_name"].eq("Algebra")
    ].iloc[0]

    assert target["prior_assessment_count"] == 1
    assert target["prior_result_count"] == 2
    assert target["prior_average_percentage"] == pytest.approx(
        60.0
    )
    assert target["prior_minimum_percentage"] == 50.0
    assert target["prior_maximum_percentage"] == 70.0
    assert target["prior_support_count"] == 1
    assert target["prior_support_rate"] == pytest.approx(0.5)
    assert (
        target["previous_assessment_average_percentage"]
        == pytest.approx(60.0)
    )
    assert target["days_since_previous_assessment"] == 14
    assert target["prior_same_topic_count"] == 1
    assert (
        target["prior_same_topic_average_percentage"]
        == pytest.approx(50.0)
    )
    assert (
        target["prior_same_topic_latest_percentage"]
        == pytest.approx(50.0)
    )
    assert target["prior_same_topic_support_count"] == 1


def test_same_day_results_are_not_used_as_history(
    small_tables: dict[str, pd.DataFrame],
) -> None:
    """Topics from one assessment must not predict each other."""

    dataset = build_modelling_dataset(small_tables)

    same_day_rows = dataset.loc[
        dataset["assessment_date"].eq(date(2025, 1, 15))
    ]

    assert len(same_day_rows) == 2
    assert same_day_rows[
        "prior_result_count"
    ].eq(2).all()
    assert same_day_rows[
        "prior_average_percentage"
    ].eq(60.0).all()


def test_intervention_cutoff_and_completion_time_are_respected(
    small_tables: dict[str, pd.DataFrame],
) -> None:
    """Only interventions known before the target date may count."""

    dataset = build_modelling_dataset(small_tables)

    january_target = dataset.loc[
        dataset["assessment_date"].eq(date(2025, 1, 15))
        & dataset["topic_name"].eq("Algebra")
    ].iloc[0]

    assert january_target["prior_intervention_count"] == 1
    assert (
        january_target[
            "prior_same_topic_intervention_count"
        ]
        == 1
    )
    assert (
        january_target[
            "prior_completed_intervention_count"
        ]
        == 1
    )

    february_target = dataset.loc[
        dataset["assessment_date"].eq(date(2025, 2, 12))
        & dataset["topic_name"].eq("Algebra")
    ].iloc[0]

    assert february_target["prior_intervention_count"] == 3
    assert (
        february_target[
            "prior_same_topic_intervention_count"
        ]
        == 2
    )

    # The third intervention is not considered completed because
    # its completion timestamp falls after the target assessment.
    assert (
        february_target[
            "prior_completed_intervention_count"
        ]
        == 1
    )


def test_future_results_do_not_change_earlier_features(
    small_tables: dict[str, pd.DataFrame],
) -> None:
    """Changing a future result must not alter earlier rows."""

    original = build_modelling_dataset(small_tables)

    modified_tables = {
        table_name: frame.copy(deep=True)
        for table_name, frame in small_tables.items()
    }

    future_result = (
        modified_tables["assessment_results"][
            "assessment_id"
        ].eq(4)
    )

    modified_tables["assessment_results"].loc[
        future_result,
        "score",
    ] = 0.0

    modified = build_modelling_dataset(modified_tables)

    earlier_original = original.loc[
        original["assessment_date"].lt(date(2025, 2, 12))
    ].reset_index(drop=True)

    earlier_modified = modified.loc[
        modified["assessment_date"].lt(date(2025, 2, 12))
    ].reset_index(drop=True)

    pd.testing.assert_frame_equal(
        earlier_original,
        earlier_modified,
    )


def test_model_feature_list_excludes_direct_leakage(
    small_tables: dict[str, pd.DataFrame],
) -> None:
    """Outcome values and personal identifiers are not features."""

    dataset = build_modelling_dataset(small_tables)

    prohibited_features = {
        "score",
        "result_percentage",
        "needs_support",
        "result_id",
        "learner_id",
        "display_name",
        "created_at",
    }

    assert prohibited_features.isdisjoint(
        MODEL_FEATURE_COLUMNS
    )
    assert set(MODEL_FEATURE_COLUMNS).issubset(
        dataset.columns
    )
    assert TARGET_COLUMN in dataset.columns


def test_chronological_split_is_complete_and_non_overlapping(
    small_tables: dict[str, pd.DataFrame],
) -> None:
    """Whole assessment dates must remain in one split."""

    dataset = build_modelling_dataset(small_tables)
    splits = chronological_split(dataset)

    train_dates = set(splits["train"]["assessment_date"])
    validation_dates = set(
        splits["validation"]["assessment_date"]
    )
    test_dates = set(splits["test"]["assessment_date"])

    assert train_dates.isdisjoint(validation_dates)
    assert train_dates.isdisjoint(test_dates)
    assert validation_dates.isdisjoint(test_dates)

    assert max(train_dates) < min(validation_dates)
    assert max(validation_dates) < min(test_dates)

    total_split_rows = sum(
        len(split_frame)
        for split_frame in splits.values()
    )

    assert total_split_rows == len(dataset)


def test_prepared_files_and_threshold_manifest_are_written(
    tmp_path: Path,
    small_tables: dict[str, pd.DataFrame],
) -> None:
    """Prepared files must include accurate split metadata."""

    threshold = 55.0

    dataset = build_modelling_dataset(
        small_tables,
        support_threshold=threshold,
    )
    splits = chronological_split(dataset)

    write_prepared_dataset(
        dataset=dataset,
        splits=splits,
        output_directory=tmp_path,
        support_threshold=threshold,
    )

    expected_files = {
        "modelling_dataset.csv",
        "train.csv",
        "validation.csv",
        "test.csv",
        "manifest.json",
    }

    actual_files = {
        path.name
        for path in tmp_path.iterdir()
    }

    assert actual_files == expected_files

    manifest = json.loads(
        (tmp_path / "manifest.json").read_text(
            encoding="utf-8"
        )
    )

    assert manifest["support_threshold"] == threshold
    assert manifest["rows"] == len(dataset)
    assert manifest["target_column"] == TARGET_COLUMN
    assert (
        manifest["feature_columns"]
        == MODEL_FEATURE_COLUMNS
    )
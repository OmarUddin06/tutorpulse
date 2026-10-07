import json
from pathlib import Path

import pandas as pd
import pytest

from analysis.synthetic_data import (
    SyntheticDataConfig,
    generate_synthetic_tables,
    write_synthetic_tables,
)


@pytest.fixture(scope="module")
def synthetic_config() -> SyntheticDataConfig:
    """Return a smaller configuration suitable for fast tests."""

    return SyntheticDataConfig(
        seed=42,
        learner_count=40,
        assessment_count=8,
    )


@pytest.fixture(scope="module")
def synthetic_tables(
    synthetic_config: SyntheticDataConfig,
) -> dict[str, pd.DataFrame]:
    """Generate one shared dataset for the constraint tests."""

    return generate_synthetic_tables(synthetic_config)


def test_generation_is_reproducible() -> None:
    """The same seed and configuration must create identical tables."""

    config = SyntheticDataConfig(
        seed=123,
        learner_count=12,
        assessment_count=4,
    )

    first_generation = generate_synthetic_tables(config)
    second_generation = generate_synthetic_tables(config)

    assert first_generation.keys() == second_generation.keys()

    for table_name in first_generation:
        pd.testing.assert_frame_equal(
            first_generation[table_name],
            second_generation[table_name],
        )


def test_expected_tables_and_configured_counts_exist(
    synthetic_config: SyntheticDataConfig,
    synthetic_tables: dict[str, pd.DataFrame],
) -> None:
    """The generator must return the five relational tables."""

    assert set(synthetic_tables) == {
        "learners",
        "topics",
        "assessments",
        "assessment_results",
        "interventions",
    }

    assert (
        len(synthetic_tables["learners"])
        == synthetic_config.learner_count
    )
    assert len(synthetic_tables["topics"]) == 4
    assert (
        len(synthetic_tables["assessments"])
        == synthetic_config.assessment_count
    )

    assert not synthetic_tables["assessment_results"].empty
    assert not synthetic_tables["interventions"].empty


def test_learner_and_topic_values_respect_constraints(
    synthetic_tables: dict[str, pd.DataFrame],
) -> None:
    """Names must be non-blank and topic names must be unique."""

    learners = synthetic_tables["learners"]
    topics = synthetic_tables["topics"]

    assert learners["display_name"].str.strip().ne("").all()
    assert topics["name"].str.strip().ne("").all()
    assert topics["name"].is_unique


def test_results_respect_keys_and_score_constraints(
    synthetic_tables: dict[str, pd.DataFrame],
) -> None:
    """Assessment results must satisfy the PostgreSQL rules."""

    learners = synthetic_tables["learners"]
    topics = synthetic_tables["topics"]
    assessments = synthetic_tables["assessments"]
    results = synthetic_tables["assessment_results"]

    assert results["learner_id"].isin(learners["id"]).all()
    assert results["topic_id"].isin(topics["id"]).all()
    assert results["assessment_id"].isin(assessments["id"]).all()

    assert results["score"].ge(0).all()
    assert results["maximum_score"].gt(0).all()
    assert results["score"].le(results["maximum_score"]).all()

    duplicate_count = results.duplicated(
        subset=[
            "learner_id",
            "assessment_id",
            "topic_id",
        ]
    ).sum()

    assert duplicate_count == 0


def test_first_assessment_contains_a_baseline_for_every_learner(
    synthetic_tables: dict[str, pd.DataFrame],
) -> None:
    """Every learner must have an initial result for every topic."""

    learners = synthetic_tables["learners"]
    topics = synthetic_tables["topics"]
    assessments = synthetic_tables["assessments"]
    results = synthetic_tables["assessment_results"]

    first_assessment_id = assessments.sort_values(
        "assessment_date"
    ).iloc[0]["id"]

    first_assessment_results = results.loc[
        results["assessment_id"].eq(first_assessment_id)
    ]

    expected_result_count = len(learners) * len(topics)

    assert len(first_assessment_results) == expected_result_count


def test_interventions_respect_database_constraints(
    synthetic_tables: dict[str, pd.DataFrame],
) -> None:
    """Intervention values must match the database checks."""

    learners = synthetic_tables["learners"]
    topics = synthetic_tables["topics"]
    interventions = synthetic_tables["interventions"]

    assert not interventions.empty

    assert interventions["learner_id"].isin(learners["id"]).all()

    topic_values = interventions["topic_id"].dropna().astype(int)
    assert topic_values.isin(topics["id"]).all()

    assert interventions["summary"].str.strip().ne("").all()

    allowed_statuses = {
        "planned",
        "active",
        "completed",
    }

    assert set(interventions["status"]).issubset(
        allowed_statuses
    )

    completed = interventions["status"].eq("completed")
    not_completed = ~completed

    assert interventions.loc[
        completed,
        "completed_at",
    ].notna().all()

    assert interventions.loc[
        not_completed,
        "completed_at",
    ].isna().all()


def test_generated_target_contains_both_classes(
    synthetic_config: SyntheticDataConfig,
    synthetic_tables: dict[str, pd.DataFrame],
) -> None:
    """Generated results must contain support and non-support cases."""

    results = synthetic_tables["assessment_results"]

    percentages = (
        results["score"]
        / results["maximum_score"]
        * 100
    )

    needs_support = percentages.lt(
        synthetic_config.support_threshold
    )

    assert needs_support.any()
    assert (~needs_support).any()


def test_assessment_dates_support_chronological_splitting(
    synthetic_tables: dict[str, pd.DataFrame],
) -> None:
    """The data must contain multiple ordered assessment periods."""

    assessments = synthetic_tables["assessments"]

    assert assessments["assessment_date"].is_unique
    assert len(assessments) >= 3

    ordered_dates = assessments[
        "assessment_date"
    ].sort_values().tolist()

    assert assessments[
        "assessment_date"
    ].tolist() == ordered_dates


def test_tables_and_manifest_can_be_written(
    tmp_path: Path,
    synthetic_config: SyntheticDataConfig,
    synthetic_tables: dict[str, pd.DataFrame],
) -> None:
    """The writer must create every CSV and its manifest."""

    write_synthetic_tables(
        tables=synthetic_tables,
        config=synthetic_config,
        output_directory=tmp_path,
    )

    expected_files = {
        "learners.csv",
        "topics.csv",
        "assessments.csv",
        "assessment_results.csv",
        "interventions.csv",
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

    assert (
        manifest["configuration"]["seed"]
        == synthetic_config.seed
    )
    assert (
        manifest["row_counts"]["learners"]
        == synthetic_config.learner_count
    )
    assert (
        manifest["row_counts"]["assessments"]
        == synthetic_config.assessment_count
    )
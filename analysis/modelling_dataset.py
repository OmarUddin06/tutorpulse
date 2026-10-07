"""Build a leakage-safe TutorPulse modelling dataset.

Only information dated before each target assessment is used to create
historical features. Generated and prepared data remain reproducible
build outputs and are not committed to Git.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


SUPPORT_THRESHOLD = 60.0

MODEL_FEATURE_COLUMNS = [
    "topic_name",
    "maximum_score",
    "prior_assessment_count",
    "prior_result_count",
    "prior_average_percentage",
    "prior_minimum_percentage",
    "prior_maximum_percentage",
    "prior_support_count",
    "prior_support_rate",
    "previous_assessment_average_percentage",
    "days_since_previous_assessment",
    "prior_same_topic_count",
    "prior_same_topic_average_percentage",
    "prior_same_topic_latest_percentage",
    "prior_same_topic_support_count",
    "prior_intervention_count",
    "prior_same_topic_intervention_count",
    "prior_completed_intervention_count",
]

TARGET_COLUMN = "needs_support"

TABLE_NAMES = (
    "learners",
    "topics",
    "assessments",
    "assessment_results",
    "interventions",
)


def load_synthetic_tables(
    input_directory: Path,
) -> dict[str, pd.DataFrame]:
    """Load generated relational CSV files from disk."""

    tables: dict[str, pd.DataFrame] = {}

    for table_name in TABLE_NAMES:
        input_path = input_directory / f"{table_name}.csv"

        if not input_path.exists():
            raise FileNotFoundError(
                f"Required generated table does not exist: {input_path}"
            )

        tables[table_name] = pd.read_csv(input_path)

    tables["assessments"]["assessment_date"] = pd.to_datetime(
        tables["assessments"]["assessment_date"],
        errors="raise",
    ).dt.date

    for table_name in (
        "learners",
        "topics",
        "assessments",
        "assessment_results",
    ):
        tables[table_name]["created_at"] = pd.to_datetime(
            tables[table_name]["created_at"],
            utc=True,
            errors="raise",
        )

    tables["interventions"]["created_at"] = pd.to_datetime(
        tables["interventions"]["created_at"],
        utc=True,
        errors="raise",
    )

    tables["interventions"]["completed_at"] = pd.to_datetime(
        tables["interventions"]["completed_at"],
        utc=True,
        errors="coerce",
    )

    return tables


def _optional_float(value: object) -> float:
    """Convert an aggregate value while preserving missing data."""

    if pd.isna(value):
        return float("nan")

    return float(value)


def build_modelling_dataset(
    tables: dict[str, pd.DataFrame],
    support_threshold: float = SUPPORT_THRESHOLD,
) -> pd.DataFrame:
    """Create one leakage-safe row per predictable result.

    Rows without an earlier assessment are excluded because they do not
    have the historical information required by the modelling question.
    """

    if not 0 < support_threshold < 100:
        raise ValueError(
            "support_threshold must be between 0 and 100"
        )

    results = tables["assessment_results"].copy()
    assessments = tables["assessments"].copy()
    topics = tables["topics"].copy()
    interventions = tables["interventions"].copy()

    results = results.rename(columns={"id": "result_id"})

    results = results.merge(
        assessments[
            [
                "id",
                "assessment_date",
            ]
        ].rename(columns={"id": "assessment_id"}),
        on="assessment_id",
        how="left",
        validate="many_to_one",
    )

    results = results.merge(
        topics[
            [
                "id",
                "name",
            ]
        ].rename(
            columns={
                "id": "topic_id",
                "name": "topic_name",
            }
        ),
        on="topic_id",
        how="left",
        validate="many_to_one",
    )

    if results["assessment_date"].isna().any():
        raise ValueError(
            "Every result must reference a known assessment"
        )

    if results["topic_name"].isna().any():
        raise ValueError(
            "Every result must reference a known topic"
        )

    results["result_percentage"] = (
        results["score"]
        / results["maximum_score"]
        * 100
    )

    results["needs_support"] = (
        results["result_percentage"]
        .lt(support_threshold)
        .astype(int)
    )

    results = results.sort_values(
        [
            "learner_id",
            "assessment_date",
            "assessment_id",
            "topic_id",
        ]
    ).reset_index(drop=True)

    if interventions.empty:
        interventions_by_learner: dict[
            int,
            pd.DataFrame,
        ] = {}
    else:
        interventions["created_date"] = (
            pd.to_datetime(
                interventions["created_at"],
                utc=True,
                errors="raise",
            )
            .dt.date
        )

        interventions["completed_date"] = (
            pd.to_datetime(
                interventions["completed_at"],
                utc=True,
                errors="coerce",
            )
            .dt.date
        )

        interventions_by_learner = {
            int(learner_id): learner_interventions.copy()
            for learner_id, learner_interventions
            in interventions.groupby("learner_id")
        }

    modelling_records: list[dict[str, object]] = []

    for learner_id, learner_results in results.groupby(
        "learner_id",
        sort=True,
    ):
        learner_results = learner_results.sort_values(
            [
                "assessment_date",
                "assessment_id",
                "topic_id",
            ]
        )

        learner_interventions = interventions_by_learner.get(
            int(learner_id),
            pd.DataFrame(),
        )

        for target in learner_results.itertuples(index=False):
            target_date = target.assessment_date

            # Only results from an earlier calendar date are allowed.
            # Results from the same assessment date are excluded.
            history = learner_results.loc[
                learner_results["assessment_date"].lt(
                    target_date
                )
            ]

            if history.empty:
                continue

            previous_assessment_date = max(
                history["assessment_date"]
            )

            previous_assessment_results = history.loc[
                history["assessment_date"].eq(
                    previous_assessment_date
                )
            ]

            same_topic_history = history.loc[
                history["topic_id"].eq(target.topic_id)
            ]

            if same_topic_history.empty:
                same_topic_latest_percentage = float("nan")
                same_topic_average_percentage = float("nan")
                same_topic_support_count = 0
            else:
                latest_same_topic_date = max(
                    same_topic_history["assessment_date"]
                )

                latest_same_topic_results = (
                    same_topic_history.loc[
                        same_topic_history[
                            "assessment_date"
                        ].eq(latest_same_topic_date)
                    ]
                )

                same_topic_latest_percentage = float(
                    latest_same_topic_results[
                        "result_percentage"
                    ].mean()
                )

                same_topic_average_percentage = float(
                    same_topic_history[
                        "result_percentage"
                    ].mean()
                )

                same_topic_support_count = int(
                    same_topic_history[
                        "needs_support"
                    ].sum()
                )

            previous_assessment_dates = (
                history["assessment_date"].drop_duplicates()
            )

            prior_support_count = int(
                history["needs_support"].sum()
            )

            if learner_interventions.empty:
                prior_interventions = learner_interventions
            else:
                prior_interventions = (
                    learner_interventions.loc[
                        learner_interventions[
                            "created_date"
                        ].lt(target_date)
                    ]
                )

            if prior_interventions.empty:
                prior_intervention_count = 0
                prior_same_topic_intervention_count = 0
                prior_completed_intervention_count = 0
            else:
                prior_intervention_count = len(
                    prior_interventions
                )

                prior_same_topic_intervention_count = int(
                    prior_interventions["topic_id"]
                    .eq(target.topic_id)
                    .sum()
                )

                completed_before_target = (
                    prior_interventions[
                        "completed_date"
                    ].notna()
                    & prior_interventions[
                        "completed_date"
                    ].lt(target_date)
                )

                prior_completed_intervention_count = int(
                    completed_before_target.sum()
                )

            modelling_records.append(
                {
                    "result_id": int(target.result_id),
                    "learner_id": int(target.learner_id),
                    "assessment_id": int(
                        target.assessment_id
                    ),
                    "assessment_date": target_date,
                    "topic_id": int(target.topic_id),
                    "topic_name": str(target.topic_name),
                    "maximum_score": float(
                        target.maximum_score
                    ),
                    "prior_assessment_count": int(
                        len(previous_assessment_dates)
                    ),
                    "prior_result_count": int(len(history)),
                    "prior_average_percentage": float(
                        history[
                            "result_percentage"
                        ].mean()
                    ),
                    "prior_minimum_percentage": float(
                        history[
                            "result_percentage"
                        ].min()
                    ),
                    "prior_maximum_percentage": float(
                        history[
                            "result_percentage"
                        ].max()
                    ),
                    "prior_support_count": (
                        prior_support_count
                    ),
                    "prior_support_rate": float(
                        prior_support_count
                        / len(history)
                    ),
                    "previous_assessment_average_percentage": (
                        float(
                            previous_assessment_results[
                                "result_percentage"
                            ].mean()
                        )
                    ),
                    "days_since_previous_assessment": int(
                        (
                            target_date
                            - previous_assessment_date
                        ).days
                    ),
                    "prior_same_topic_count": int(
                        len(same_topic_history)
                    ),
                    "prior_same_topic_average_percentage": (
                        _optional_float(
                            same_topic_average_percentage
                        )
                    ),
                    "prior_same_topic_latest_percentage": (
                        _optional_float(
                            same_topic_latest_percentage
                        )
                    ),
                    "prior_same_topic_support_count": (
                        same_topic_support_count
                    ),
                    "prior_intervention_count": (
                        prior_intervention_count
                    ),
                    "prior_same_topic_intervention_count": (
                        prior_same_topic_intervention_count
                    ),
                    "prior_completed_intervention_count": (
                        prior_completed_intervention_count
                    ),
                    "result_percentage": float(
                        target.result_percentage
                    ),
                    "needs_support": int(
                        target.needs_support
                    ),
                }
            )

    dataset = pd.DataFrame(modelling_records)

    if dataset.empty:
        raise ValueError(
            "No modelling rows could be created from the supplied data"
        )

    return dataset.sort_values(
        [
            "assessment_date",
            "learner_id",
            "topic_id",
        ]
    ).reset_index(drop=True)


def chronological_split(
    dataset: pd.DataFrame,
    train_fraction: float = 0.60,
    validation_fraction: float = 0.20,
) -> dict[str, pd.DataFrame]:
    """Split complete assessment dates into train, validation and test."""

    if not 0 < train_fraction < 1:
        raise ValueError(
            "train_fraction must be between 0 and 1"
        )

    if not 0 < validation_fraction < 1:
        raise ValueError(
            "validation_fraction must be between 0 and 1"
        )

    if train_fraction + validation_fraction >= 1:
        raise ValueError(
            "train and validation fractions must total less than 1"
        )

    assessment_dates = sorted(
        dataset["assessment_date"].drop_duplicates()
    )

    if len(assessment_dates) < 3:
        raise ValueError(
            "At least three assessment dates are required"
        )

    train_end = max(
        1,
        int(len(assessment_dates) * train_fraction),
    )

    validation_end = max(
        train_end + 1,
        int(
            len(assessment_dates)
            * (train_fraction + validation_fraction)
        ),
    )

    if validation_end >= len(assessment_dates):
        validation_end = len(assessment_dates) - 1

    train_dates = set(assessment_dates[:train_end])

    validation_dates = set(
        assessment_dates[train_end:validation_end]
    )

    test_dates = set(
        assessment_dates[validation_end:]
    )

    return {
        "train": dataset.loc[
            dataset["assessment_date"].isin(train_dates)
        ].reset_index(drop=True),
        "validation": dataset.loc[
            dataset["assessment_date"].isin(
                validation_dates
            )
        ].reset_index(drop=True),
        "test": dataset.loc[
            dataset["assessment_date"].isin(test_dates)
        ].reset_index(drop=True),
    }


def write_prepared_dataset(
    dataset: pd.DataFrame,
    splits: dict[str, pd.DataFrame],
    output_directory: Path,
    support_threshold: float = SUPPORT_THRESHOLD,
) -> None:
    """Write the full dataset, chronological splits and manifest."""

    output_directory.mkdir(parents=True, exist_ok=True)

    dataset.to_csv(
        output_directory / "modelling_dataset.csv",
        index=False,
    )

    for split_name, split_frame in splits.items():
        split_frame.to_csv(
            output_directory / f"{split_name}.csv",
            index=False,
        )

    split_summary = {}

    for split_name, split_frame in splits.items():
        split_summary[split_name] = {
            "rows": len(split_frame),
            "first_assessment_date": str(
                split_frame["assessment_date"].min()
            ),
            "last_assessment_date": str(
                split_frame["assessment_date"].max()
            ),
            "support_rate": float(
                split_frame[TARGET_COLUMN].mean()
            ),
        }

    manifest = {
        "rows": len(dataset),
        "support_threshold": support_threshold,
        "feature_columns": MODEL_FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "splits": split_summary,
    }

    (
        output_directory / "manifest.json"
    ).write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description=(
            "Build the leakage-safe TutorPulse modelling dataset."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/generated"),
        help="Directory containing generated relational CSVs.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/prepared"),
        help="Directory receiving prepared datasets.",
    )

    parser.add_argument(
        "--support-threshold",
        type=float,
        default=SUPPORT_THRESHOLD,
        help="Percentage below which needs_support equals 1.",
    )

    return parser.parse_args()


def main() -> None:
    """Load, prepare, split and write the modelling dataset."""

    arguments = parse_arguments()

    tables = load_synthetic_tables(arguments.input)

    dataset = build_modelling_dataset(
        tables,
        support_threshold=arguments.support_threshold,
    )

    splits = chronological_split(dataset)

    write_prepared_dataset(
        dataset=dataset,
        splits=splits,
        output_directory=arguments.output,
        support_threshold=arguments.support_threshold,
    )

    print(
        "Prepared modelling data written to: "
        f"{arguments.output.resolve()}"
    )

    print(f"All modelling rows: {len(dataset)}")

    for split_name, split_frame in splits.items():
        print(
            f"{split_name}: {len(split_frame)} rows, "
            f"{split_frame['assessment_date'].min()} to "
            f"{split_frame['assessment_date'].max()}, "
            "support rate "
            f"{split_frame[TARGET_COLUMN].mean():.1%}"
        )


if __name__ == "__main__":
    main()
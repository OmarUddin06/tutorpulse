"""Generate reproducible fictional TutorPulse data for analysis.

The generated CSV files mirror the five TutorPulse PostgreSQL tables.
This module does not modify the development database.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd


TOPICS = (
    ("Algebra", "Expressions, equations and algebraic reasoning.", -3.0),
    ("Fractions", "Fractions, decimals, percentages and proportional reasoning.", -6.0),
    ("Geometry", "Shape, measure and spatial reasoning.", 1.0),
    ("Statistics", "Data interpretation, probability and statistics.", 3.0),
)


@dataclass(frozen=True)
class SyntheticDataConfig:
    """Configuration controlling the generated dataset."""

    seed: int = 42
    learner_count: int = 120
    assessment_count: int = 24
    attendance_rate: float = 0.90
    intervention_rate: float = 0.30
    support_threshold: float = 60.0
    first_assessment_date: date = date(2025, 1, 15)

    def __post_init__(self) -> None:
        if self.learner_count < 2:
            raise ValueError("learner_count must be at least 2")

        if self.assessment_count < 3:
            raise ValueError("assessment_count must be at least 3")

        if not 0 < self.attendance_rate <= 1:
            raise ValueError("attendance_rate must be greater than 0 and at most 1")

        if not 0 <= self.intervention_rate <= 1:
            raise ValueError("intervention_rate must be between 0 and 1")

        if not 0 < self.support_threshold < 100:
            raise ValueError("support_threshold must be between 0 and 100")


def _utc_timestamp(event_date: date, hour: int) -> datetime:
    """Return a timezone-aware UTC timestamp for a fictional event."""

    return datetime.combine(
        event_date,
        time(hour=hour),
        tzinfo=timezone.utc,
    )


def generate_synthetic_tables(
    config: SyntheticDataConfig,
) -> dict[str, pd.DataFrame]:
    """Create reproducible DataFrames that mirror the database tables."""

    rng = np.random.default_rng(config.seed)

    first_date = config.first_assessment_date
    system_created_date = first_date - timedelta(days=60)

    learner_ids = np.arange(1, config.learner_count + 1)

    # Every learner receives a fictional underlying ability and rate of progress.
    # These hidden values help create realistic patterns but are not exported as
    # modelling features.
    learner_abilities = rng.normal(
        loc=64.0,
        scale=12.0,
        size=config.learner_count,
    )
    learner_growth_rates = rng.normal(
        loc=0.30,
        scale=0.18,
        size=config.learner_count,
    )

    learners = pd.DataFrame(
        {
            "id": learner_ids,
            "display_name": [
                f"Synthetic Learner {learner_id:03d}"
                for learner_id in learner_ids
            ],
            "created_at": [
                _utc_timestamp(system_created_date, 9)
                for _ in learner_ids
            ],
        }
    )

    topics = pd.DataFrame(
        {
            "id": range(1, len(TOPICS) + 1),
            "name": [topic[0] for topic in TOPICS],
            "description": [topic[1] for topic in TOPICS],
            "created_at": [
                _utc_timestamp(system_created_date, 9)
                for _ in TOPICS
            ],
        }
    )

    assessment_dates = [
        first_date + timedelta(days=14 * assessment_index)
        for assessment_index in range(config.assessment_count)
    ]

    assessments = pd.DataFrame(
        {
            "id": range(1, config.assessment_count + 1),
            "title": [
                f"Synthetic Assessment {assessment_index:02d}"
                for assessment_index in range(1, config.assessment_count + 1)
            ],
            "assessment_date": assessment_dates,
            "created_at": [
                _utc_timestamp(
                    assessment_date - timedelta(days=14),
                    10,
                )
                for assessment_date in assessment_dates
            ],
        }
    )

    result_records: list[dict[str, object]] = []
    result_id = 1

    maximum_scores = (20.0, 25.0, 30.0)

    for assessment_index, assessment_date in enumerate(assessment_dates):
        assessment_id = assessment_index + 1
        maximum_score = maximum_scores[
            assessment_index % len(maximum_scores)
        ]

        for learner_index, learner_id in enumerate(learner_ids):
            # Everyone completes the first assessment. Later assessments
            # include some fictional absence to avoid a perfectly balanced
            # artificial dataset.
            learner_attended = (
                assessment_index == 0
                or rng.random() <= config.attendance_rate
            )

            if not learner_attended:
                continue

            for topic_id, (_, _, topic_effect) in enumerate(
                TOPICS,
                start=1,
            ):
                random_variation = rng.normal(loc=0.0, scale=7.5)
                progress = (
                    learner_growth_rates[learner_index]
                    * assessment_index
                )

                percentage = (
                    learner_abilities[learner_index]
                    + topic_effect
                    + progress
                    + random_variation
                )

                percentage = float(np.clip(percentage, 15.0, 98.0))

                score = round(
                    maximum_score * percentage / 100,
                    2,
                )

                result_records.append(
                    {
                        "id": result_id,
                        "learner_id": int(learner_id),
                        "assessment_id": assessment_id,
                        "topic_id": topic_id,
                        "score": score,
                        "maximum_score": maximum_score,
                        "created_at": _utc_timestamp(
                            assessment_date,
                            17,
                        ),
                    }
                )

                result_id += 1

    assessment_results = pd.DataFrame(result_records)

    assessment_date_by_id = {
        assessment_id: assessment_date
        for assessment_id, assessment_date in zip(
            assessments["id"],
            assessments["assessment_date"],
            strict=True,
        )
    }

    intervention_records: list[dict[str, object]] = []
    intervention_id = 1

    for result in result_records:
        percentage = (
            float(result["score"])
            / float(result["maximum_score"])
            * 100
        )

        if percentage >= config.support_threshold:
            continue

        if rng.random() > config.intervention_rate:
            continue

        assessment_date = assessment_date_by_id[
            int(result["assessment_id"])
        ]
        created_date = assessment_date + timedelta(days=1)

        status = str(
            rng.choice(
                ("planned", "active", "completed"),
                p=(0.20, 0.30, 0.50),
            )
        )

        if status == "completed":
            completion_delay = int(rng.integers(4, 11))
            completed_at: datetime | None = _utc_timestamp(
                created_date + timedelta(days=completion_delay),
                16,
            )
        else:
            completed_at = None

        topic_id: int | None

        if rng.random() < 0.10:
            topic_id = None
            topic_description = "general study support"
        else:
            topic_id = int(result["topic_id"])
            topic_description = TOPICS[topic_id - 1][0]

        intervention_records.append(
            {
                "id": intervention_id,
                "learner_id": int(result["learner_id"]),
                "topic_id": topic_id,
                "summary": (
                    "Synthetic support plan for "
                    f"{topic_description}."
                ),
                "status": status,
                "created_at": _utc_timestamp(created_date, 9),
                "completed_at": completed_at,
            }
        )

        intervention_id += 1

    interventions = pd.DataFrame(intervention_records)

    if not interventions.empty:
        interventions["topic_id"] = pd.array(
            interventions["topic_id"],
            dtype="Int64",
        )

    return {
        "learners": learners,
        "topics": topics,
        "assessments": assessments,
        "assessment_results": assessment_results,
        "interventions": interventions,
    }


def write_synthetic_tables(
    tables: dict[str, pd.DataFrame],
    config: SyntheticDataConfig,
    output_directory: Path,
) -> None:
    """Write generated tables and a reproducibility manifest to disk."""

    output_directory.mkdir(parents=True, exist_ok=True)

    for table_name, frame in tables.items():
        output_path = output_directory / f"{table_name}.csv"
        frame.to_csv(output_path, index=False)

    manifest = {
        "configuration": {
            **asdict(config),
            "first_assessment_date": (
                config.first_assessment_date.isoformat()
            ),
        },
        "row_counts": {
            table_name: len(frame)
            for table_name, frame in tables.items()
        },
    }

    manifest_path = output_directory / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line options for reproducible generation."""

    parser = argparse.ArgumentParser(
        description="Generate fictional TutorPulse analysis data.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed controlling reproducibility.",
    )
    parser.add_argument(
        "--learners",
        type=int,
        default=120,
        help="Number of fictional learners.",
    )
    parser.add_argument(
        "--assessments",
        type=int,
        default=24,
        help="Number of fortnightly assessments.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/generated"),
        help="Directory receiving the generated CSV files.",
    )

    return parser.parse_args()


def main() -> None:
    """Generate the dataset and report the resulting row counts."""

    arguments = parse_arguments()

    config = SyntheticDataConfig(
        seed=arguments.seed,
        learner_count=arguments.learners,
        assessment_count=arguments.assessments,
    )

    tables = generate_synthetic_tables(config)

    write_synthetic_tables(
        tables=tables,
        config=config,
        output_directory=arguments.output,
    )

    print(f"Synthetic data written to: {arguments.output.resolve()}")

    for table_name, frame in tables.items():
        print(f"{table_name}: {len(frame)} rows")


if __name__ == "__main__":
    main()
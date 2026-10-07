from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Assessment,
    AssessmentResult,
    Intervention,
    Learner,
    Topic,
)


pytestmark = pytest.mark.integration


def test_blank_learner_name_violates_database_constraint(
    db_session: Session,
) -> None:
    """PostgreSQL must reject a whitespace-only learner name."""

    db_session.add(Learner(display_name="   "))

    with pytest.raises(IntegrityError) as exception:
        db_session.flush()

    assert (
        exception.value.orig.diag.constraint_name
        == "learners_display_name_not_blank"
    )


def test_duplicate_topic_name_violates_unique_constraint(
    db_session: Session,
) -> None:
    """PostgreSQL must reject duplicate topic names."""

    db_session.add(Topic(name="Integration Test Algebra"))
    db_session.flush()

    db_session.add(Topic(name="Integration Test Algebra"))

    with pytest.raises(IntegrityError) as exception:
        db_session.flush()

    assert (
        exception.value.orig.diag.constraint_name
        == "topics_name_key"
    )


def test_score_above_maximum_violates_database_constraint(
    db_session: Session,
) -> None:
    """The database must reject a score above its maximum."""

    learner = Learner(display_name="Constraint Test Learner")
    assessment = Assessment(
        title="Constraint Test Assessment",
        assessment_date=date(2026, 10, 7),
    )
    topic = Topic(name="Constraint Test Fractions")

    db_session.add_all([learner, assessment, topic])
    db_session.flush()

    db_session.add(
        AssessmentResult(
            learner_id=learner.id,
            assessment_id=assessment.id,
            topic_id=topic.id,
            score=Decimal("25.00"),
            maximum_score=Decimal("20.00"),
        )
    )

    with pytest.raises(IntegrityError) as exception:
        db_session.flush()

    assert (
        exception.value.orig.diag.constraint_name
        == "assessment_results_score_within_maximum"
    )


def test_missing_learner_violates_foreign_key_constraint(
    db_session: Session,
) -> None:
    """A result cannot refer to a learner that does not exist."""

    assessment = Assessment(
        title="Foreign Key Test Assessment",
        assessment_date=date(2026, 10, 7),
    )
    topic = Topic(name="Foreign Key Test Geometry")

    db_session.add_all([assessment, topic])
    db_session.flush()

    db_session.add(
        AssessmentResult(
            learner_id=999999999,
            assessment_id=assessment.id,
            topic_id=topic.id,
            score=Decimal("15.00"),
            maximum_score=Decimal("20.00"),
        )
    )

    with pytest.raises(IntegrityError) as exception:
        db_session.flush()

    assert (
        exception.value.orig.diag.constraint_name
        == "assessment_results_learner_fk"
    )


def test_completed_intervention_requires_completion_time(
    db_session: Session,
) -> None:
    """A completed intervention must have a completion timestamp."""

    learner = Learner(display_name="Intervention Constraint Learner")
    db_session.add(learner)
    db_session.flush()

    db_session.add(
        Intervention(
            learner_id=learner.id,
            summary="Completed without a timestamp",
            status="completed",
            completed_at=None,
        )
    )

    with pytest.raises(IntegrityError) as exception:
        db_session.flush()

    assert (
        exception.value.orig.diag.constraint_name
        == "interventions_completion_consistent"
    )
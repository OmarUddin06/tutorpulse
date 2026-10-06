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


def test_deleting_learner_cascades_to_results_and_interventions(
    db_session: Session,
) -> None:
    """Deleting a learner must remove their dependent records."""

    learner = Learner(display_name="Cascade Test Learner")
    assessment = Assessment(
        title="Cascade Test Assessment",
        assessment_date=date(2026, 10, 7),
    )
    topic = Topic(name="Cascade Test Algebra")

    db_session.add_all([learner, assessment, topic])
    db_session.flush()

    result = AssessmentResult(
        learner_id=learner.id,
        assessment_id=assessment.id,
        topic_id=topic.id,
        score=Decimal("15.00"),
        maximum_score=Decimal("20.00"),
    )
    intervention = Intervention(
        learner_id=learner.id,
        topic_id=topic.id,
        summary="Cascade test intervention",
        status="planned",
    )

    db_session.add_all([result, intervention])
    db_session.flush()

    result_id = result.id
    intervention_id = intervention.id

    db_session.delete(learner)
    db_session.flush()
    db_session.expire_all()

    assert db_session.get(AssessmentResult, result_id) is None
    assert db_session.get(Intervention, intervention_id) is None


def test_deleting_assessment_cascades_to_results(
    db_session: Session,
) -> None:
    """Deleting an assessment must remove its dependent results."""

    learner = Learner(display_name="Assessment Cascade Learner")
    assessment = Assessment(
        title="Assessment Cascade Test",
        assessment_date=date(2026, 10, 7),
    )
    topic = Topic(name="Assessment Cascade Fractions")

    db_session.add_all([learner, assessment, topic])
    db_session.flush()

    result = AssessmentResult(
        learner_id=learner.id,
        assessment_id=assessment.id,
        topic_id=topic.id,
        score=Decimal("18.00"),
        maximum_score=Decimal("20.00"),
    )

    db_session.add(result)
    db_session.flush()

    result_id = result.id

    db_session.delete(assessment)
    db_session.flush()
    db_session.expire_all()

    assert db_session.get(AssessmentResult, result_id) is None


def test_deleting_topic_used_by_result_is_restricted(
    db_session: Session,
) -> None:
    """A topic used by an assessment result must not be deleted."""

    learner = Learner(display_name="Restricted Topic Learner")
    assessment = Assessment(
        title="Restricted Topic Assessment",
        assessment_date=date(2026, 10, 7),
    )
    topic = Topic(name="Restricted Topic Geometry")

    db_session.add_all([learner, assessment, topic])
    db_session.flush()

    db_session.add(
        AssessmentResult(
            learner_id=learner.id,
            assessment_id=assessment.id,
            topic_id=topic.id,
            score=Decimal("12.00"),
            maximum_score=Decimal("20.00"),
        )
    )
    db_session.flush()

    db_session.delete(topic)

    with pytest.raises(IntegrityError) as exception:
        db_session.flush()

    assert (
        exception.value.orig.diag.constraint_name
        == "assessment_results_topic_fk"
    )


def test_deleting_intervention_topic_sets_topic_id_to_null(
    db_session: Session,
) -> None:
    """Deleting a topic should preserve its intervention with no topic."""

    learner = Learner(display_name="Set Null Test Learner")
    topic = Topic(name="Set Null Test Algebra")

    db_session.add_all([learner, topic])
    db_session.flush()

    intervention = Intervention(
        learner_id=learner.id,
        topic_id=topic.id,
        summary="Intervention whose topic will be deleted",
        status="planned",
    )

    db_session.add(intervention)
    db_session.flush()

    intervention_id = intervention.id

    db_session.delete(topic)
    db_session.flush()
    db_session.expire_all()

    preserved_intervention = db_session.get(
        Intervention,
        intervention_id,
    )

    assert preserved_intervention is not None
    assert preserved_intervention.topic_id is None
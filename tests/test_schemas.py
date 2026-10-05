from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import (
    AssessmentCreate,
    AssessmentResultCreate,
    InterventionCreate,
    LearnerCreate,
    TopicCreate,
)


def test_learner_name_is_trimmed() -> None:
    learner = LearnerCreate(display_name="  Learner 005  ")

    assert learner.display_name == "Learner 005"


@pytest.mark.parametrize("display_name", ["", "   ", "\t"])
def test_blank_learner_name_is_rejected(display_name: str) -> None:
    with pytest.raises(ValidationError):
        LearnerCreate(display_name=display_name)


def test_assessment_title_is_trimmed() -> None:
    assessment = AssessmentCreate(
        title="  Spring Diagnostic  ",
        assessment_date=date(2026, 10, 5),
    )

    assert assessment.title == "Spring Diagnostic"


def test_blank_topic_name_is_rejected() -> None:
    with pytest.raises(ValidationError):
        TopicCreate(name="   ")


def test_valid_assessment_result_is_accepted() -> None:
    result = AssessmentResultCreate(
        learner_id=1,
        assessment_id=1,
        topic_id=1,
        score=Decimal("15.00"),
        maximum_score=Decimal("20.00"),
    )

    assert result.score == Decimal("15.00")
    assert result.maximum_score == Decimal("20.00")


def test_negative_score_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AssessmentResultCreate(
            learner_id=1,
            assessment_id=1,
            topic_id=1,
            score=Decimal("-1.00"),
            maximum_score=Decimal("20.00"),
        )


def test_zero_maximum_score_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AssessmentResultCreate(
            learner_id=1,
            assessment_id=1,
            topic_id=1,
            score=Decimal("0.00"),
            maximum_score=Decimal("0.00"),
        )


def test_score_above_maximum_is_rejected() -> None:
    with pytest.raises(
        ValidationError,
        match="score must not exceed maximum_score",
    ):
        AssessmentResultCreate(
            learner_id=1,
            assessment_id=1,
            topic_id=1,
            score=Decimal("25.00"),
            maximum_score=Decimal("20.00"),
        )


def test_non_positive_related_id_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AssessmentResultCreate(
            learner_id=0,
            assessment_id=1,
            topic_id=1,
            score=Decimal("15.00"),
            maximum_score=Decimal("20.00"),
        )


def test_intervention_defaults_to_planned() -> None:
    intervention = InterventionCreate(
        learner_id=1,
        topic_id=1,
        summary="Provide weekly fractions practice.",
    )

    assert intervention.status == "planned"
    assert intervention.completed_at is None


def test_invalid_intervention_status_is_rejected() -> None:
    with pytest.raises(ValidationError):
        InterventionCreate(
            learner_id=1,
            topic_id=1,
            summary="Provide weekly fractions practice.",
            status="cancelled",
        )


def test_completed_intervention_requires_completion_time() -> None:
    with pytest.raises(
        ValidationError,
        match="completed_at is required",
    ):
        InterventionCreate(
            learner_id=1,
            topic_id=1,
            summary="Provide weekly fractions practice.",
            status="completed",
        )


def test_non_completed_intervention_rejects_completion_time() -> None:
    with pytest.raises(
        ValidationError,
        match="completed_at must be empty",
    ):
        InterventionCreate(
            learner_id=1,
            topic_id=1,
            summary="Provide weekly fractions practice.",
            status="active",
            completed_at=datetime(
                2026,
                10,
                5,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )


def test_valid_completed_intervention_is_accepted() -> None:
    completed_at = datetime(
        2026,
        10,
        5,
        12,
        0,
        tzinfo=timezone.utc,
    )

    intervention = InterventionCreate(
        learner_id=1,
        topic_id=1,
        summary="Review completed work.",
        status="completed",
        completed_at=completed_at,
    )

    assert intervention.status == "completed"
    assert intervention.completed_at == completed_at
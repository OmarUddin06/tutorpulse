from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Assessment, AssessmentResult, Learner, Topic
from app.schemas import (
    AssessmentResultCreate,
    AssessmentResultRead,
    AssessmentResultUpdate,
)


router = APIRouter(
    prefix="/assessment-results",
    tags=["Assessment Results"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]
AssessmentResultId = Annotated[int, Path(gt=0)]


def get_result_or_404(
    result_id: int,
    database_session: Session,
) -> AssessmentResult:
    result = database_session.get(AssessmentResult, result_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment result not found",
        )

    return result


def verify_related_records(
    result_data: AssessmentResultCreate,
    database_session: Session,
) -> None:
    if database_session.get(Learner, result_data.learner_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner not found",
        )

    if database_session.get(
        Assessment,
        result_data.assessment_id,
    ) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    if database_session.get(Topic, result_data.topic_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )


def commit_result_change(
    database_session: Session,
) -> None:
    try:
        database_session.commit()
    except IntegrityError as error:
        database_session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An assessment result already exists for this "
                "learner, assessment and topic"
            ),
        ) from error


@router.post(
    "",
    response_model=AssessmentResultRead,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment_result(
    result_data: AssessmentResultCreate,
    database_session: DatabaseSession,
) -> AssessmentResult:
    verify_related_records(result_data, database_session)

    result = AssessmentResult(
        learner_id=result_data.learner_id,
        assessment_id=result_data.assessment_id,
        topic_id=result_data.topic_id,
        score=result_data.score,
        maximum_score=result_data.maximum_score,
    )

    database_session.add(result)
    commit_result_change(database_session)
    database_session.refresh(result)

    return result


@router.get(
    "",
    response_model=list[AssessmentResultRead],
)
def list_assessment_results(
    database_session: DatabaseSession,
) -> list[AssessmentResult]:
    statement = select(AssessmentResult).order_by(AssessmentResult.id)
    results = database_session.scalars(statement).all()

    return list(results)


@router.get(
    "/{result_id}",
    response_model=AssessmentResultRead,
)
def get_assessment_result(
    result_id: AssessmentResultId,
    database_session: DatabaseSession,
) -> AssessmentResult:
    return get_result_or_404(result_id, database_session)


@router.patch(
    "/{result_id}",
    response_model=AssessmentResultRead,
)
def update_assessment_result(
    result_id: AssessmentResultId,
    result_data: AssessmentResultUpdate,
    database_session: DatabaseSession,
) -> AssessmentResult:
    result = get_result_or_404(result_id, database_session)
    changes = result_data.model_dump(exclude_unset=True)

    updated_score = changes.get("score", result.score)
    updated_maximum = changes.get(
        "maximum_score",
        result.maximum_score,
    )

    if updated_score > updated_maximum:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="score must not exceed maximum_score",
        )

    for field_name, value in changes.items():
        setattr(result, field_name, value)

    commit_result_change(database_session)
    database_session.refresh(result)

    return result


@router.delete(
    "/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_assessment_result(
    result_id: AssessmentResultId,
    database_session: DatabaseSession,
) -> Response:
    result = get_result_or_404(result_id, database_session)

    database_session.delete(result)
    database_session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
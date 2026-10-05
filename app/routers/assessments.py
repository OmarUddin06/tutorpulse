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
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Assessment
from app.schemas import (
    AssessmentCreate,
    AssessmentRead,
    AssessmentUpdate,
)


router = APIRouter(
    prefix="/assessments",
    tags=["Assessments"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]
AssessmentId = Annotated[int, Path(gt=0)]


def get_assessment_or_404(
    assessment_id: int,
    database_session: Session,
) -> Assessment:
    """Return an assessment or raise an HTTP 404 response."""

    assessment = database_session.get(Assessment, assessment_id)

    if assessment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )

    return assessment


@router.post(
    "",
    response_model=AssessmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_assessment(
    assessment_data: AssessmentCreate,
    database_session: DatabaseSession,
) -> Assessment:
    """Create an assessment."""

    assessment = Assessment(
        title=assessment_data.title,
        assessment_date=assessment_data.assessment_date,
    )

    database_session.add(assessment)
    database_session.commit()
    database_session.refresh(assessment)

    return assessment


@router.get(
    "",
    response_model=list[AssessmentRead],
)
def list_assessments(
    database_session: DatabaseSession,
) -> list[Assessment]:
    """Return assessments ordered by date and ID."""

    statement = select(Assessment).order_by(
        Assessment.assessment_date,
        Assessment.id,
    )
    assessments = database_session.scalars(statement).all()

    return list(assessments)


@router.get(
    "/{assessment_id}",
    response_model=AssessmentRead,
)
def get_assessment(
    assessment_id: AssessmentId,
    database_session: DatabaseSession,
) -> Assessment:
    """Return one assessment by ID."""

    return get_assessment_or_404(
        assessment_id,
        database_session,
    )


@router.patch(
    "/{assessment_id}",
    response_model=AssessmentRead,
)
def update_assessment(
    assessment_id: AssessmentId,
    assessment_data: AssessmentUpdate,
    database_session: DatabaseSession,
) -> Assessment:
    """Update an assessment's supplied fields."""

    assessment = get_assessment_or_404(
        assessment_id,
        database_session,
    )
    changes = assessment_data.model_dump(exclude_unset=True)

    for field_name, value in changes.items():
        setattr(assessment, field_name, value)

    database_session.commit()
    database_session.refresh(assessment)

    return assessment


@router.delete(
    "/{assessment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_assessment(
    assessment_id: AssessmentId,
    database_session: DatabaseSession,
) -> Response:
    """Delete an assessment and its associated results."""

    assessment = get_assessment_or_404(
        assessment_id,
        database_session,
    )

    database_session.delete(assessment)
    database_session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
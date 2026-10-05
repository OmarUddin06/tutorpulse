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
from app.models import Learner
from app.schemas import LearnerCreate, LearnerRead, LearnerUpdate


router = APIRouter(
    prefix="/learners",
    tags=["Learners"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]
LearnerId = Annotated[int, Path(gt=0)]


def get_learner_or_404(
    learner_id: int,
    database_session: Session,
) -> Learner:
    """Return a learner or raise an HTTP 404 response."""

    learner = database_session.get(Learner, learner_id)

    if learner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner not found",
        )

    return learner


@router.post(
    "",
    response_model=LearnerRead,
    status_code=status.HTTP_201_CREATED,
)
def create_learner(
    learner_data: LearnerCreate,
    database_session: DatabaseSession,
) -> Learner:
    """Create an anonymised or fictional learner."""

    learner = Learner(display_name=learner_data.display_name)

    database_session.add(learner)
    database_session.commit()
    database_session.refresh(learner)

    return learner


@router.get(
    "",
    response_model=list[LearnerRead],
)
def list_learners(
    database_session: DatabaseSession,
) -> list[Learner]:
    """Return every learner ordered by ID."""

    statement = select(Learner).order_by(Learner.id)
    learners = database_session.scalars(statement).all()

    return list(learners)


@router.get(
    "/{learner_id}",
    response_model=LearnerRead,
)
def get_learner(
    learner_id: LearnerId,
    database_session: DatabaseSession,
) -> Learner:
    """Return one learner by ID."""

    return get_learner_or_404(learner_id, database_session)


@router.patch(
    "/{learner_id}",
    response_model=LearnerRead,
)
def update_learner(
    learner_id: LearnerId,
    learner_data: LearnerUpdate,
    database_session: DatabaseSession,
) -> Learner:
    """Update a learner's display name."""

    learner = get_learner_or_404(learner_id, database_session)
    learner.display_name = learner_data.display_name

    database_session.commit()
    database_session.refresh(learner)

    return learner


@router.delete(
    "/{learner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_learner(
    learner_id: LearnerId,
    database_session: DatabaseSession,
) -> Response:
    """Delete a learner and return an empty response."""

    learner = get_learner_or_404(learner_id, database_session)

    database_session.delete(learner)
    database_session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
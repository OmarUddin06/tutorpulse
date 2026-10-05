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
from app.models import Intervention, Learner, Topic
from app.schemas import (
    InterventionCreate,
    InterventionRead,
    InterventionUpdate,
)


router = APIRouter(
    prefix="/interventions",
    tags=["Interventions"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]
InterventionId = Annotated[int, Path(gt=0)]


def get_intervention_or_404(
    intervention_id: int,
    database_session: Session,
) -> Intervention:
    intervention = database_session.get(
        Intervention,
        intervention_id,
    )

    if intervention is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found",
        )

    return intervention


def verify_learner_exists(
    learner_id: int,
    database_session: Session,
) -> None:
    if database_session.get(Learner, learner_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner not found",
        )


def verify_topic_exists(
    topic_id: int | None,
    database_session: Session,
) -> None:
    if (
        topic_id is not None
        and database_session.get(Topic, topic_id) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )


def commit_intervention_change(
    database_session: Session,
) -> None:
    try:
        database_session.commit()
    except IntegrityError as error:
        database_session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The intervention conflicts with existing data",
        ) from error


def verify_completion_state(
    intervention_status: str,
    completed_at: object | None,
) -> None:
    if intervention_status == "completed" and completed_at is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "completed_at is required when status is completed"
            ),
        )

    if intervention_status != "completed" and completed_at is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "completed_at must be empty unless status is completed"
            ),
        )


@router.post(
    "",
    response_model=InterventionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_intervention(
    intervention_data: InterventionCreate,
    database_session: DatabaseSession,
) -> Intervention:
    verify_learner_exists(
        intervention_data.learner_id,
        database_session,
    )
    verify_topic_exists(
        intervention_data.topic_id,
        database_session,
    )

    intervention = Intervention(
        learner_id=intervention_data.learner_id,
        topic_id=intervention_data.topic_id,
        summary=intervention_data.summary,
        status=intervention_data.status,
        completed_at=intervention_data.completed_at,
    )

    database_session.add(intervention)
    commit_intervention_change(database_session)
    database_session.refresh(intervention)

    return intervention


@router.get(
    "",
    response_model=list[InterventionRead],
)
def list_interventions(
    database_session: DatabaseSession,
) -> list[Intervention]:
    statement = select(Intervention).order_by(Intervention.id)
    interventions = database_session.scalars(statement).all()

    return list(interventions)


@router.get(
    "/{intervention_id}",
    response_model=InterventionRead,
)
def get_intervention(
    intervention_id: InterventionId,
    database_session: DatabaseSession,
) -> Intervention:
    return get_intervention_or_404(
        intervention_id,
        database_session,
    )


@router.patch(
    "/{intervention_id}",
    response_model=InterventionRead,
)
def update_intervention(
    intervention_id: InterventionId,
    intervention_data: InterventionUpdate,
    database_session: DatabaseSession,
) -> Intervention:
    intervention = get_intervention_or_404(
        intervention_id,
        database_session,
    )
    changes = intervention_data.model_dump(exclude_unset=True)

    if "topic_id" in changes:
        verify_topic_exists(
            changes["topic_id"],
            database_session,
        )

    updated_status = changes.get("status", intervention.status)
    updated_completed_at = changes.get(
        "completed_at",
        intervention.completed_at,
    )

    verify_completion_state(
        updated_status,
        updated_completed_at,
    )

    for field_name, value in changes.items():
        setattr(intervention, field_name, value)

    commit_intervention_change(database_session)
    database_session.refresh(intervention)

    return intervention


@router.delete(
    "/{intervention_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_intervention(
    intervention_id: InterventionId,
    database_session: DatabaseSession,
) -> Response:
    intervention = get_intervention_or_404(
        intervention_id,
        database_session,
    )

    database_session.delete(intervention)
    database_session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
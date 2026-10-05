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
from app.models import Topic
from app.schemas import TopicCreate, TopicRead, TopicUpdate


router = APIRouter(
    prefix="/topics",
    tags=["Topics"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]
TopicId = Annotated[int, Path(gt=0)]


def get_topic_or_404(
    topic_id: int,
    database_session: Session,
) -> Topic:
    """Return a topic or raise an HTTP 404 response."""

    topic = database_session.get(Topic, topic_id)

    if topic is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    return topic


def commit_topic_change(
    database_session: Session,
    conflict_message: str,
) -> None:
    """Commit a topic change and convert constraint errors to HTTP 409."""

    try:
        database_session.commit()
    except IntegrityError as error:
        database_session.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=conflict_message,
        ) from error


@router.post(
    "",
    response_model=TopicRead,
    status_code=status.HTTP_201_CREATED,
)
def create_topic(
    topic_data: TopicCreate,
    database_session: DatabaseSession,
) -> Topic:
    """Create a curriculum topic."""

    topic = Topic(
        name=topic_data.name,
        description=topic_data.description,
    )

    database_session.add(topic)
    commit_topic_change(
        database_session,
        "A topic with this name already exists",
    )
    database_session.refresh(topic)

    return topic


@router.get(
    "",
    response_model=list[TopicRead],
)
def list_topics(
    database_session: DatabaseSession,
) -> list[Topic]:
    """Return every topic ordered by ID."""

    statement = select(Topic).order_by(Topic.id)
    topics = database_session.scalars(statement).all()

    return list(topics)


@router.get(
    "/{topic_id}",
    response_model=TopicRead,
)
def get_topic(
    topic_id: TopicId,
    database_session: DatabaseSession,
) -> Topic:
    """Return one topic by ID."""

    return get_topic_or_404(topic_id, database_session)


@router.patch(
    "/{topic_id}",
    response_model=TopicRead,
)
def update_topic(
    topic_id: TopicId,
    topic_data: TopicUpdate,
    database_session: DatabaseSession,
) -> Topic:
    """Update a topic's supplied fields."""

    topic = get_topic_or_404(topic_id, database_session)
    changes = topic_data.model_dump(exclude_unset=True)

    for field_name, value in changes.items():
        setattr(topic, field_name, value)

    commit_topic_change(
        database_session,
        "A topic with this name already exists",
    )
    database_session.refresh(topic)

    return topic


@router.delete(
    "/{topic_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_topic(
    topic_id: TopicId,
    database_session: DatabaseSession,
) -> Response:
    """Delete a topic unless assessment results still reference it."""

    topic = get_topic_or_404(topic_id, database_session)
    database_session.delete(topic)

    commit_topic_change(
        database_session,
        "This topic is used by assessment results and cannot be deleted",
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
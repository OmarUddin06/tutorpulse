"""TutorPulse database engine and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from app.config import settings


database_url = settings.sqlalchemy_database_url()

engine = create_engine(
    database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class inherited by TutorPulse database models."""


def get_db() -> Generator[Session, None, None]:
    """Provide one database session for an API request."""

    database_session = SessionLocal()

    try:
        yield database_session
    finally:
        database_session.close()
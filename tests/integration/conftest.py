from collections.abc import Generator

import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


class IntegrationTestSettings(BaseSettings):
    """Configuration for the separate PostgreSQL integration-test database."""

    db_host: str = "localhost"
    db_port: int = 5433
    db_name: str
    db_user: str
    db_password: str

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        env_prefix="TUTORPULSE_TEST_",
        case_sensitive=False,
        extra="ignore",
    )


@pytest.fixture(scope="session")
def integration_settings() -> IntegrationTestSettings:
    """Load test settings and refuse to use a non-test database."""

    settings = IntegrationTestSettings()

    if settings.db_name == "tutorpulse":
        pytest.exit(
            "Safety check failed: integration tests must not use "
            "the tutorpulse development database.",
            returncode=1,
        )

    if not settings.db_name.endswith("_test"):
        pytest.exit(
            "Safety check failed: the integration database name "
            "must end with '_test'.",
            returncode=1,
        )

    return settings


@pytest.fixture(scope="session")
def integration_engine(
    integration_settings: IntegrationTestSettings,
) -> Generator[Engine, None, None]:
    """Create an engine connected only to the protected test database."""

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=integration_settings.db_user,
        password=integration_settings.db_password,
        host=integration_settings.db_host,
        port=integration_settings.db_port,
        database=integration_settings.db_name,
    )

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 5},
    )

    with engine.connect() as connection:
        connected_database = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()

    if connected_database != integration_settings.db_name:
        engine.dispose()
        pytest.exit(
            "Safety check failed: PostgreSQL connected to an "
            "unexpected database.",
            returncode=1,
        )

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(
    integration_engine: Engine,
) -> Generator[Session, None, None]:
    """Provide an isolated database transaction for one test."""

    connection = integration_engine.connect()
    outer_transaction = connection.begin()

    session = Session(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()
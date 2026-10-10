"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    """Configuration loaded from environment variables."""

    database_url: str | None = None

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "tutorpulse"
    db_user: str = "postgres"
    db_password: str | None = None

    model_artifact_directory: Path = Path(
        "artifacts/models"
    )

    demo_read_only: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="TUTORPULSE_",
        case_sensitive=False,
        extra="ignore",
    )

    def sqlalchemy_database_url(self) -> URL:
        """Return the configured PostgreSQL connection URL.

        Hosted deployments use one complete connection string.
        Local development continues using the existing split database
        settings.
        """

        if self.database_url:
            raw_url = self.database_url.strip()

            if raw_url.startswith("postgres://"):
                raw_url = (
                    "postgresql+psycopg://"
                    + raw_url.removeprefix(
                        "postgres://"
                    )
                )
            elif raw_url.startswith("postgresql://"):
                raw_url = (
                    "postgresql+psycopg://"
                    + raw_url.removeprefix(
                        "postgresql://"
                    )
                )

            parsed_url = make_url(raw_url)

            if (
                parsed_url.drivername
                != "postgresql+psycopg"
            ):
                raise ValueError(
                    "TUTORPULSE_DATABASE_URL must use "
                    "PostgreSQL with the psycopg driver."
                )

            return parsed_url

        if not self.db_password:
            raise ValueError(
                "Set TUTORPULSE_DATABASE_URL or "
                "TUTORPULSE_DB_PASSWORD."
            )

        return URL.create(
            drivername="postgresql+psycopg",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        )


settings = Settings()
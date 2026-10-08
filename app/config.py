"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables."""

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "tutorpulse"
    db_user: str = "postgres"
    db_password: str

    model_artifact_directory: Path = Path(
        "artifacts/models"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="TUTORPULSE_",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
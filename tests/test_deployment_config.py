"""Tests for local and hosted deployment configuration."""

import pytest

from app.config import Settings


def test_local_database_settings_build_psycopg_url() -> None:
    configured = Settings(
        database_url=None,
        db_host="127.0.0.1",
        db_port=5433,
        db_name="tutorpulse_test",
        db_user="postgres",
        db_password="test_password",
        _env_file=None,
    )

    url = configured.sqlalchemy_database_url()

    assert url.drivername == "postgresql+psycopg"
    assert url.host == "127.0.0.1"
    assert url.port == 5433
    assert url.database == "tutorpulse_test"
    assert url.username == "postgres"
    assert url.password == "test_password"


def test_hosted_database_url_uses_psycopg_and_keeps_ssl() -> None:
    configured = Settings(
        database_url=(
            "postgresql://portfolio_user:"
            "portfolio_password@database.example/"
            "tutorpulse?sslmode=require"
        ),
        db_password=None,
        _env_file=None,
    )

    url = configured.sqlalchemy_database_url()

    assert url.drivername == "postgresql+psycopg"
    assert url.host == "database.example"
    assert url.database == "tutorpulse"
    assert url.username == "portfolio_user"
    assert url.password == "portfolio_password"
    assert url.query["sslmode"] == "require"


def test_unsupported_database_driver_is_rejected() -> None:
    configured = Settings(
        database_url="sqlite:///tutorpulse.db",
        db_password=None,
        _env_file=None,
    )

    with pytest.raises(
        ValueError,
        match="PostgreSQL with the psycopg driver",
    ):
        configured.sqlalchemy_database_url()


def test_demo_read_only_mode_defaults_to_false() -> None:
    configured = Settings(
        db_password="test_password",
        _env_file=None,
    )

    assert configured.demo_read_only is False
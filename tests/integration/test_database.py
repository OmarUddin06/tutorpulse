import pytest
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


pytestmark = pytest.mark.integration

EXPECTED_TABLES = {
    "learners",
    "assessments",
    "topics",
    "assessment_results",
    "interventions",
}


def test_connected_to_dedicated_test_database(
    integration_engine: Engine,
) -> None:
    """Integration tests must connect to tutorpulse_test."""

    with integration_engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database()")
        ).scalar_one()

    assert database_name == "tutorpulse_test"


def test_expected_schema_tables_exist(
    integration_engine: Engine,
) -> None:
    """The migration must create every TutorPulse table."""

    database_tables = set(
        inspect(integration_engine).get_table_names()
    )

    assert EXPECTED_TABLES.issubset(database_tables)


def test_integration_database_starts_without_seed_data(
    integration_engine: Engine,
) -> None:
    """The test database should not depend on development seed data."""

    with integration_engine.connect() as connection:
        table_counts = {
            table_name: connection.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).scalar_one()
            for table_name in EXPECTED_TABLES
        }

    assert all(count == 0 for count in table_counts.values())
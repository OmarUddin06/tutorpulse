import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models import Learner


pytestmark = pytest.mark.integration


def test_outer_transaction_removes_committed_test_data(
    integration_engine: Engine,
) -> None:
    """A test commit must still be removable by the outer transaction."""

    marker_name = "Transaction Rollback Probe"

    connection = integration_engine.connect()
    outer_transaction = connection.begin()

    session = Session(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        session.add(Learner(display_name=marker_name))
        session.commit()

        visible_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM learners
                WHERE display_name = :display_name
                """
            ),
            {"display_name": marker_name},
        ).scalar_one()

        assert visible_count == 1
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()

    with integration_engine.connect() as verification_connection:
        remaining_count = verification_connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM learners
                WHERE display_name = :display_name
                """
            ),
            {"display_name": marker_name},
        ).scalar_one()

    assert remaining_count == 0
"""Tests for the TutorPulse container server."""

import pytest

from app.server import (
    DEFAULT_PORT,
    configured_port,
)


def test_server_uses_local_default_port() -> None:
    assert configured_port({}) == DEFAULT_PORT
    assert DEFAULT_PORT == 8000


def test_server_uses_platform_port() -> None:
    assert configured_port(
        {"PORT": "10000"}
    ) == 10000


@pytest.mark.parametrize(
    "port",
    [
        "not-a-port",
        "0",
        "65536",
    ],
)
def test_server_rejects_invalid_port(
    port: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="between 1 and 65535",
    ):
        configured_port(
            {"PORT": port}
        )
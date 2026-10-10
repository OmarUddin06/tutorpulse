"""Start the TutorPulse HTTP server."""

from collections.abc import Mapping
import os

import uvicorn


DEFAULT_PORT = 8000


def configured_port(
    environment: Mapping[str, str] | None = None,
) -> int:
    """Return a validated hosting-platform port."""

    source = (
        os.environ
        if environment is None
        else environment
    )

    raw_port = source.get(
        "PORT",
        str(DEFAULT_PORT),
    )

    try:
        port = int(raw_port)
    except ValueError as error:
        raise ValueError(
            "PORT must be an integer between "
            "1 and 65535."
        ) from error

    if not 1 <= port <= 65535:
        raise ValueError(
            "PORT must be an integer between "
            "1 and 65535."
        )

    return port


def run() -> None:
    """Run TutorPulse on every container interface."""

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=configured_port(),
    )


if __name__ == "__main__":
    run()
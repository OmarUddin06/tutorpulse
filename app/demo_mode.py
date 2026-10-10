"""Safety boundary for the public TutorPulse portfolio demo."""

from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from app.config import settings


SAFE_HTTP_METHODS = frozenset(
    {
        "GET",
        "HEAD",
        "OPTIONS",
    }
)

ALLOWED_DEMO_WRITE_PATHS = frozenset(
    {
        "/predictions/support-risk",
    }
)

READ_ONLY_MESSAGE = (
    "TutorPulse is running as a read-only portfolio demo. "
    "Stored demonstration data cannot be changed."
)

NextHandler = Callable[
    [Request],
    Awaitable[Response],
]


def normalise_path(path: str) -> str:
    """Return a stable path for allow-list comparisons."""

    normalised = path.rstrip("/")

    return normalised or "/"


def should_block_demo_request(
    method: str,
    path: str,
    *,
    demo_read_only: bool,
) -> bool:
    """Return whether demo mode should reject a request."""

    if not demo_read_only:
        return False

    if method.upper() in SAFE_HTTP_METHODS:
        return False

    if (
        normalise_path(path)
        in ALLOWED_DEMO_WRITE_PATHS
    ):
        return False

    return True


async def enforce_demo_read_only(
    request: Request,
    call_next: NextHandler,
) -> Response:
    """Prevent public demo users from changing stored data."""

    if should_block_demo_request(
        request.method,
        request.url.path,
        demo_read_only=settings.demo_read_only,
    ):
        return JSONResponse(
            status_code=403,
            content={
                "detail": READ_ONLY_MESSAGE,
            },
        )

    return await call_next(request)
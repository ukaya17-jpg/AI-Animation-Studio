"""HTTP middleware used at the API boundary."""

from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response

from app.core.rate_limit import NoopRateLimiter
from app.core.request_context import reset_request_id, set_request_id

RequestHandler = Callable[[Request], Awaitable[Response]]
rate_limiter = NoopRateLimiter()


async def enforce_rate_limit(request: Request, call_next: RequestHandler) -> Response:
    """Run the configured rate-limit hook before API request processing."""
    await rate_limiter.check(request)
    return await call_next(request)


async def add_request_id(request: Request, call_next: RequestHandler) -> Response:
    """Attach a trusted request identifier to the request, response, and log context."""
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    token = set_request_id(request_id)
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    finally:
        reset_request_id(token)
    response.headers["X-Request-ID"] = request_id
    return response

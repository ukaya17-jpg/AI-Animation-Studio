"""HTTP middleware used at the API boundary."""

from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.core.exceptions import TooManyRequestsError
from app.core.rate_limit import NoopRateLimiter, RateLimiter, RedisRateLimiter
from app.core.request_context import reset_request_id, set_request_id
from app.database.redis import get_redis_client

RequestHandler = Callable[[Request], Awaitable[Response]]


def build_rate_limiter(settings: Settings) -> RateLimiter:
    """Choose the rate limiter implementation for the given configuration.

    Disabled by default (``rate_limit_enabled=False``) so local development,
    tests, and CI never need a live Redis connection just to serve a request.
    """
    if not settings.rate_limit_enabled:
        return NoopRateLimiter()
    return RedisRateLimiter(get_redis_client())


rate_limiter = build_rate_limiter(get_settings())


async def enforce_rate_limit(request: Request, call_next: RequestHandler) -> Response:
    """Run the configured rate-limit hook before API request processing.

    Exceptions raised here run outside the routing layer, so ``TooManyRequestsError``
    is handled directly rather than relying on ``app.add_exception_handler`` (which
    only observes exceptions raised while dispatching a route).
    """
    try:
        await rate_limiter.check(request)
    except TooManyRequestsError as error:
        return JSONResponse(status_code=429, content={"detail": str(error)})
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

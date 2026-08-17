"""Rate-limit extension points for authenticated and public API endpoints."""

import time
from typing import Protocol

from fastapi import Request
from redis.asyncio import Redis

from app.core.exceptions import TooManyRequestsError

# Fixed-window request budgets. Auth endpoints get a much tighter budget since
# they are the primary brute-force/credential-stuffing target.
DEFAULT_MAX_REQUESTS = 120
DEFAULT_WINDOW_SECONDS = 60
AUTH_MAX_REQUESTS = 10
AUTH_WINDOW_SECONDS = 60
_AUTH_PATH_PREFIXES = ("/auth/login", "/auth/register")


class RateLimiter(Protocol):
    """Contract for a pluggable request rate limiter."""

    async def check(self, request: Request) -> None:
        """Raise an application error when the request exceeds its allowed quota."""


class NoopRateLimiter:
    """Development-safe default until a Redis-backed policy is configured."""

    async def check(self, request: Request) -> None:
        """Allow the request without applying a quota."""
        del request


class RedisRateLimiter:
    """Fixed-window rate limiter backed by Redis, keyed by client IP and path.

    Each window is its own key (``<bucket>:<ip>:<window index>``), so a window
    naturally expires without needing a separate cleanup job; the first request
    in a window sets a TTL equal to the window length.
    """

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def check(self, request: Request) -> None:
        """Raise ``TooManyRequestsError`` once the caller exceeds its budget."""
        client_host = request.client.host if request.client else "unknown"
        if request.url.path.startswith(_AUTH_PATH_PREFIXES):
            bucket, max_requests, window_seconds = "auth", AUTH_MAX_REQUESTS, AUTH_WINDOW_SECONDS
        else:
            bucket, max_requests, window_seconds = (
                "default",
                DEFAULT_MAX_REQUESTS,
                DEFAULT_WINDOW_SECONDS,
            )
        window_index = int(time.time() // window_seconds)
        key = f"ratelimit:{bucket}:{client_host}:{window_index}"
        count = await self._redis.incr(key)
        if count == 1:
            await self._redis.expire(key, window_seconds)
        if count > max_requests:
            raise TooManyRequestsError("Too many requests. Please try again later.")

"""Rate-limit extension points for future authenticated API endpoints."""

from typing import Protocol

from fastapi import Request


class RateLimiter(Protocol):
    """Contract for a pluggable request rate limiter."""

    async def check(self, request: Request) -> None:
        """Raise an application error when the request exceeds its allowed quota."""


class NoopRateLimiter:
    """Development-safe default until a Redis-backed policy is configured."""

    async def check(self, request: Request) -> None:
        """Allow the request without applying a quota."""
        del request

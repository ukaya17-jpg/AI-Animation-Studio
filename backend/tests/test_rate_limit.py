import httpx
import pytest
from starlette.requests import Request

from app.api import middleware
from app.api.handlers import too_many_requests_handler
from app.core.config import Settings
from app.core.exceptions import TooManyRequestsError
from app.core.rate_limit import (
    AUTH_MAX_REQUESTS,
    DEFAULT_MAX_REQUESTS,
    NoopRateLimiter,
    RedisRateLimiter,
)
from app.main import app


class FakeRedis:
    """In-memory stand-in for the two redis-py async calls the limiter uses."""

    def __init__(self) -> None:
        self.counts: dict[str, int] = {}
        self.expired: list[tuple[str, int]] = []

    async def incr(self, name: str) -> int:
        self.counts[name] = self.counts.get(name, 0) + 1
        return self.counts[name]

    async def expire(self, name: str, time: int) -> bool:
        self.expired.append((name, time))
        return True


def _make_request(path: str, client_host: str | None = "1.2.3.4") -> Request:
    scope = {
        "type": "http",
        "path": path,
        "method": "GET",
        "headers": [],
        "client": (client_host, 12345) if client_host else None,
        "query_string": b"",
        "server": ("testserver", 80),
        "scheme": "http",
    }
    return Request(scope)


async def test_check_allows_requests_within_the_default_budget() -> None:
    limiter = RedisRateLimiter(FakeRedis())

    for _ in range(DEFAULT_MAX_REQUESTS):
        await limiter.check(_make_request("/episodes"))


async def test_check_raises_once_the_default_budget_is_exceeded() -> None:
    limiter = RedisRateLimiter(FakeRedis())
    for _ in range(DEFAULT_MAX_REQUESTS):
        await limiter.check(_make_request("/episodes"))

    with pytest.raises(TooManyRequestsError):
        await limiter.check(_make_request("/episodes"))


async def test_check_uses_a_tighter_budget_for_auth_paths() -> None:
    limiter = RedisRateLimiter(FakeRedis())
    for _ in range(AUTH_MAX_REQUESTS):
        await limiter.check(_make_request("/auth/login"))

    with pytest.raises(TooManyRequestsError):
        await limiter.check(_make_request("/auth/login"))


async def test_check_tracks_separate_budgets_per_client_ip() -> None:
    limiter = RedisRateLimiter(FakeRedis())
    for _ in range(AUTH_MAX_REQUESTS):
        await limiter.check(_make_request("/auth/login", client_host="1.1.1.1"))

    # A different IP still has its own untouched budget.
    await limiter.check(_make_request("/auth/login", client_host="2.2.2.2"))


async def test_check_treats_a_missing_client_as_a_single_shared_bucket() -> None:
    limiter = RedisRateLimiter(FakeRedis())

    await limiter.check(_make_request("/episodes", client_host=None))


def test_build_rate_limiter_defaults_to_noop() -> None:
    limiter = middleware.build_rate_limiter(Settings(rate_limit_enabled=False))

    assert isinstance(limiter, NoopRateLimiter)


def test_build_rate_limiter_returns_redis_backed_limiter_when_enabled() -> None:
    limiter = middleware.build_rate_limiter(Settings(rate_limit_enabled=True))

    assert isinstance(limiter, RedisRateLimiter)


async def test_too_many_requests_handler_returns_429_with_the_error_message() -> None:
    response = await too_many_requests_handler(
        _make_request("/auth/login"), TooManyRequestsError("slow down")
    )

    assert response.status_code == 429
    assert response.body == b'{"detail":"slow down"}'


async def test_enabled_rate_limiter_blocks_requests_end_to_end(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Swap in a Redis-backed limiter (against a fake client) and drive real
    requests through the actual middleware chain to prove the wiring works,
    not just the isolated unit."""
    monkeypatch.setattr(middleware, "rate_limiter", RedisRateLimiter(FakeRedis()))

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        responses = [await client.get("/episodes/themes") for _ in range(DEFAULT_MAX_REQUESTS + 1)]

    assert [r.status_code for r in responses[:DEFAULT_MAX_REQUESTS]] == [200] * DEFAULT_MAX_REQUESTS
    assert responses[-1].status_code == 429

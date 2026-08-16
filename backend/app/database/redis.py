from functools import lru_cache
from typing import cast

from redis.asyncio import Redis, from_url

from app.core.config import get_settings


@lru_cache
def get_redis_client() -> Redis:
    """Create the shared asynchronous Redis client lazily."""
    client = from_url(  # type: ignore[no-untyped-call]
        get_settings().redis_url, decode_responses=True
    )
    return cast(Redis, client)


async def redis_ping() -> bool:
    """Return whether Redis is reachable by the configured client."""
    return bool(await get_redis_client().ping())


async def close_redis_client() -> None:
    """Release the Redis connection pool during application shutdown."""
    await get_redis_client().aclose()
    get_redis_client.cache_clear()

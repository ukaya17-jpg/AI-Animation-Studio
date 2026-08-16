"""Services for liveness and infrastructure readiness reporting."""

from collections.abc import Awaitable, Callable

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.core.exceptions import ServiceUnavailableError
from app.schemas.health import HealthResponse

RedisPing = Callable[[], Awaitable[bool]]


class HealthService:
    """Build health responses without exposing infrastructure details to routes."""

    def __init__(
        self,
        settings: Settings,
        session_factory: async_sessionmaker[AsyncSession],
        redis_ping: RedisPing,
    ) -> None:
        self._settings = settings
        self._session_factory = session_factory
        self._redis_ping = redis_ping

    def liveness(self) -> HealthResponse:
        """Return process liveness; this intentionally has no external dependencies."""
        return HealthResponse(
            status="ok",
            service=self._settings.app_name,
            version=self._settings.app_version,
        )

    async def readiness(self) -> HealthResponse:
        """Check services required for normal request processing."""
        dependencies = {
            "database": await self._database_is_ready(),
            "redis": await self._redis_is_ready(),
        }
        if not all(dependencies.values()):
            raise ServiceUnavailableError("One or more required dependencies are unavailable.")
        return HealthResponse(
            status="ok",
            service=self._settings.app_name,
            version=self._settings.app_version,
            dependencies=dependencies,
        )

    async def _database_is_ready(self) -> bool:
        try:
            async with self._session_factory() as session:
                await session.execute(text("SELECT 1"))
        except Exception:
            return False
        return True

    async def _redis_is_ready(self) -> bool:
        try:
            return bool(await self._redis_ping())
        except Exception:
            return False

"""Dependency providers for API routes."""

from app.core.config import get_settings
from app.database.redis import redis_ping
from app.database.session import AsyncSessionLocal
from app.services.health import HealthService
from app.services.storyboard_service import StoryboardService


async def get_health_service() -> HealthService:
    """Construct the health service with the application's infrastructure clients."""
    return HealthService(get_settings(), AsyncSessionLocal, redis_ping)


async def get_storyboard_service() -> StoryboardService:
    """Construct the stateless storyboard use-case service for one request."""
    return StoryboardService()

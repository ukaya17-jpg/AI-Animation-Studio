"""Dependency providers for API routes."""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import InvalidTokenError, decode_access_token
from app.database.redis import redis_ping
from app.database.session import AsyncSessionLocal, get_db_session
from app.models.user import User
from app.repositories.generated_episode_repository import GeneratedEpisodeRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.episode_service import EpisodeService
from app.services.health import HealthService
from app.services.project_service import ProjectService
from app.services.storyboard_service import StoryboardService

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_health_service() -> HealthService:
    """Construct the health service with the application's infrastructure clients."""
    return HealthService(get_settings(), AsyncSessionLocal, redis_ping)


async def get_storyboard_service() -> StoryboardService:
    """Construct the stateless storyboard use-case service for one request."""
    return StoryboardService()


async def get_episode_service(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> EpisodeService:
    """Construct the episode use-case service backed by one request-scoped DB session."""
    return EpisodeService(repository=GeneratedEpisodeRepository(session))


async def get_auth_service(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> AuthService:
    """Construct the auth use-case service backed by one request-scoped DB session."""
    return AuthService(repository=UserRepository(session), settings=get_settings())


async def get_project_service(
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> ProjectService:
    """Construct the project use-case service backed by one request-scoped DB session."""
    return ProjectService(repository=ProjectRepository(session))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),  # noqa: B008
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> User:
    """Resolve the authenticated user from a bearer access token, or raise 401."""
    unauthorized = HTTPException(
        status_code=401,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        user_id = decode_access_token(credentials.credentials, get_settings())
    except InvalidTokenError as error:
        raise unauthorized from error
    user = await UserRepository(session).get_by_id(user_id)
    if user is None:
        raise unauthorized
    return user

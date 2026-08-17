"""Application service that exposes registration/login use cases to API adapters."""

from __future__ import annotations

from app.core.config import Settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class EmailAlreadyRegisteredError(Exception):
    """Raised when registration is attempted with an email already on file."""


class InvalidCredentialsError(Exception):
    """Raised when login fails because the email or password doesn't match."""


class AuthService:
    """Coordinate user registration and login."""

    def __init__(self, repository: UserRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    async def register(self, *, email: str, password: str) -> User:
        """Create a new user account, rejecting a duplicate email."""
        if await self._repository.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError(f"{email} is already registered.")
        return await self._repository.create(email=email, hashed_password=hash_password(password))

    async def login(self, *, email: str, password: str) -> str:
        """Validate credentials and return a signed access token."""
        user = await self._repository.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Incorrect email or password.")
        return create_access_token(user.id, self._settings)

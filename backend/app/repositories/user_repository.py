"""Persistence for user accounts."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """CRUD access to persisted users for one request-scoped session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, email: str, hashed_password: str) -> User:
        """Persist a new user and return the stored row."""
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Return one user by email, or ``None`` if no account uses it."""
        result = await self._session.scalars(select(User).where(User.email == email))
        return result.first()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Return one user by id, or ``None`` if it doesn't exist."""
        return await self._session.get(User, user_id)

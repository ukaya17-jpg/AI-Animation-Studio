"""Persistence for projects (a user's animation channels)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    """CRUD access to persisted projects for one request-scoped session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, *, owner_id: uuid.UUID, name: str) -> Project:
        """Persist a new project and return the stored row."""
        project = Project(owner_id=owner_id, name=name)
        self._session.add(project)
        await self._session.commit()
        await self._session.refresh(project)
        return project

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        """Return one project by id, or ``None`` if it doesn't exist."""
        return await self._session.get(Project, project_id)

    async def list_for_owner(self, owner_id: uuid.UUID) -> list[Project]:
        """Return every project owned by one user, oldest first."""
        result = await self._session.scalars(
            select(Project).where(Project.owner_id == owner_id).order_by(Project.created_at)
        )
        return list(result.all())

"""Application service that exposes project use cases to API adapters."""

from __future__ import annotations

import uuid

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository


class ProjectService:
    """Coordinate project creation and listing for one authenticated user."""

    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    async def create(self, *, owner_id: uuid.UUID, name: str) -> Project:
        """Create a new project owned by the given user."""
        return await self._repository.create(owner_id=owner_id, name=name)

    async def get_by_id(self, project_id: uuid.UUID) -> Project | None:
        """Return one project by id, or ``None`` if it doesn't exist."""
        return await self._repository.get_by_id(project_id)

    async def list_for_owner(self, owner_id: uuid.UUID) -> list[Project]:
        """Return every project owned by the given user."""
        return await self._repository.list_for_owner(owner_id)

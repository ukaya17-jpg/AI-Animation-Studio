"""Persistence for generated Neşeli Orman episodes."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generated_episode import GeneratedEpisode


class GeneratedEpisodeRepository:
    """CRUD access to persisted generated episodes for one request-scoped session."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        theme_id: str,
        theme_label: str,
        title: str,
        lead_character_id: str,
        support_character_id: str,
        location_id: str,
        lesson: str,
        scenes: list[dict[str, Any]],
        seo_package: dict[str, Any],
        shorts_plan: dict[str, Any],
        project_id: uuid.UUID | None = None,
    ) -> GeneratedEpisode:
        """Persist a newly generated episode and return the stored row."""
        record = GeneratedEpisode(
            project_id=project_id,
            theme_id=theme_id,
            theme_label=theme_label,
            title=title,
            lead_character_id=lead_character_id,
            support_character_id=support_character_id,
            location_id=location_id,
            lesson=lesson,
            scenes=scenes,
            seo_package=seo_package,
            shorts_plan=shorts_plan,
        )
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record

    async def get_by_id(self, episode_id: uuid.UUID) -> GeneratedEpisode | None:
        """Return one persisted episode by id, or ``None`` if it doesn't exist."""
        return await self._session.get(GeneratedEpisode, episode_id)

    async def list_paginated(
        self, *, page: int, page_size: int, project_id: uuid.UUID | None = None
    ) -> tuple[list[GeneratedEpisode], int]:
        """Return one newest-first page of episodes, alongside the total row count.

        When ``project_id`` is given, only episodes linked to that project are counted
        and returned; episodes generated without a project are otherwise unaffected.
        """
        count_query = select(func.count()).select_from(GeneratedEpisode)
        list_query = select(GeneratedEpisode)
        if project_id is not None:
            count_query = count_query.where(GeneratedEpisode.project_id == project_id)
            list_query = list_query.where(GeneratedEpisode.project_id == project_id)
        total = await self._session.scalar(count_query)
        rows = await self._session.scalars(
            list_query.order_by(GeneratedEpisode.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(rows.all()), total or 0

    async def list_theme_ids_for_project(self, project_id: uuid.UUID) -> set[str]:
        """Return the distinct theme ids that already have a generated episode in this project."""
        rows = await self._session.scalars(
            select(GeneratedEpisode.theme_id).where(GeneratedEpisode.project_id == project_id)
        )
        return set(rows.all())

    async def list_for_project(self, project_id: uuid.UUID) -> list[GeneratedEpisode]:
        """Return every episode generated under one project, oldest first."""
        rows = await self._session.scalars(
            select(GeneratedEpisode)
            .where(GeneratedEpisode.project_id == project_id)
            .order_by(GeneratedEpisode.created_at.asc())
        )
        return list(rows.all())

    async def delete(self, episode_id: uuid.UUID) -> bool:
        """Delete one persisted episode by id; return whether a row was removed."""
        record = await self.get_by_id(episode_id)
        if record is None:
            return False
        await self._session.delete(record)
        await self._session.commit()
        return True

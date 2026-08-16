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
    ) -> GeneratedEpisode:
        """Persist a newly generated episode and return the stored row."""
        record = GeneratedEpisode(
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
        self, *, page: int, page_size: int
    ) -> tuple[list[GeneratedEpisode], int]:
        """Return one newest-first page of episodes, alongside the total row count."""
        total = await self._session.scalar(select(func.count()).select_from(GeneratedEpisode))
        rows = await self._session.scalars(
            select(GeneratedEpisode)
            .order_by(GeneratedEpisode.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(rows.all()), total or 0

    async def delete(self, episode_id: uuid.UUID) -> bool:
        """Delete one persisted episode by id; return whether a row was removed."""
        record = await self.get_by_id(episode_id)
        if record is None:
            return False
        await self._session.delete(record)
        await self._session.commit()
        return True

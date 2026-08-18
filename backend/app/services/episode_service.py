"""Application service that exposes Neşeli Orman episode use cases to API adapters."""

from __future__ import annotations

import uuid
from dataclasses import asdict
from typing import Any

from app.models.generated_episode import GeneratedEpisode
from app.repositories.generated_episode_repository import GeneratedEpisodeRepository
from app.services.content_bank import ContentBank
from app.services.episode_generator import EpisodeGeneratorService
from app.services.episode_seo import EpisodeSeoService
from app.services.episode_shorts import EpisodeShortsService


class EpisodeService:
    """Coordinate episode, SEO, and Shorts generation for one theme, and persist the result."""

    def __init__(
        self,
        repository: GeneratedEpisodeRepository,
        generator: EpisodeGeneratorService | None = None,
        seo: EpisodeSeoService | None = None,
        shorts: EpisodeShortsService | None = None,
        content_bank: ContentBank | None = None,
    ) -> None:
        self._repository = repository
        self._generator = generator or EpisodeGeneratorService()
        self._seo = seo or EpisodeSeoService()
        self._shorts = shorts or EpisodeShortsService()
        self._content_bank = content_bank or ContentBank()

    def list_themes(self) -> list[dict[str, str]]:
        """Return every theme's id, label, and cast/location image URLs, in catalog order."""
        summaries = []
        for theme in self._generator.list_themes():
            lead = self._content_bank.get_character(theme.lead_character_id)
            support = self._content_bank.get_character(theme.support_character_id)
            location = self._content_bank.get_location(theme.location_id)
            summaries.append(
                {
                    "theme_id": theme.theme_id,
                    "label": theme.label,
                    "lead_character_name": lead.name,
                    "lead_character_image_url": lead.image_url,
                    "lead_character_voice_sample_url": lead.voice_sample_url,
                    "support_character_name": support.name,
                    "support_character_image_url": support.image_url,
                    "support_character_voice_sample_url": support.voice_sample_url,
                    "location_name": location.name,
                    "location_image_url": location.image_url,
                    "location_ambient_video_url": location.ambient_video_url,
                }
            )
        return summaries

    async def generate(self, theme_id: str, project_id: uuid.UUID | None = None) -> dict[str, Any]:
        """Generate an episode script plus its SEO/Shorts package, and persist it.

        ``project_id`` is optional: episodes may still be generated standalone,
        outside of any project.
        """
        episode = self._generator.generate(theme_id)
        seo = self._seo.generate(episode)
        shorts = self._shorts.generate(episode)
        record = await self._repository.create(
            project_id=project_id,
            theme_id=episode.theme_id,
            theme_label=episode.theme_label,
            title=episode.title,
            lead_character_id=episode.lead_character.character_id,
            support_character_id=episode.support_character.character_id,
            location_id=episode.location.location_id,
            lesson=episode.lesson,
            scenes=[asdict(scene) for scene in episode.scenes],
            seo_package=asdict(seo),
            shorts_plan={**asdict(shorts), "total_duration_seconds": shorts.total_duration_seconds},
        )
        return self._to_detail(record)

    async def generate_batch(self, project_id: uuid.UUID | None = None) -> dict[str, Any]:
        """Generate every theme's episode in one call, persisting each as it's built.

        With a ``project_id``, themes that project already has a generated
        episode for are skipped rather than re-generated, so re-clicking a
        "generate all" button stays idempotent instead of piling up duplicate
        episodes per theme. Without a ``project_id`` (anonymous), there is no
        owner to scope "already generated" against — a shared anonymous pool
        would make one caller's batch silently skip themes a *different*
        anonymous caller happened to generate earlier, so every theme is
        generated fresh each call there, matching the existing anonymous
        ``generate`` endpoint's stateless behavior.
        """
        existing_theme_ids = (
            await self._repository.list_theme_ids_for_project(project_id)
            if project_id is not None
            else set()
        )
        created: list[dict[str, Any]] = []
        skipped_theme_ids: list[str] = []
        for theme in self._generator.list_themes():
            if theme.theme_id in existing_theme_ids:
                skipped_theme_ids.append(theme.theme_id)
                continue
            created.append(await self.generate(theme.theme_id, project_id=project_id))
        return {
            "project_id": project_id,
            "created": created,
            "skipped_theme_ids": skipped_theme_ids,
        }

    async def list_all_generated_episodes(self, project_id: uuid.UUID) -> list[dict[str, Any]]:
        """Return every persisted episode's full detail for one project, oldest first."""
        records = await self._repository.list_for_project(project_id)
        return [self._to_detail(record) for record in records]

    async def list_generated_episodes(
        self, *, page: int, page_size: int, project_id: uuid.UUID | None = None
    ) -> dict[str, Any]:
        """Return one newest-first page of persisted episode summaries.

        When ``project_id`` is given, the page is scoped to that project only.
        """
        records, total = await self._repository.list_paginated(
            page=page, page_size=page_size, project_id=project_id
        )
        return {
            "items": [self._to_summary(record) for record in records],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    async def get_generated_episode(self, episode_id: uuid.UUID) -> dict[str, Any] | None:
        """Return one persisted episode's full detail, or ``None`` if it doesn't exist."""
        record = await self._repository.get_by_id(episode_id)
        if record is None:
            return None
        return self._to_detail(record)

    async def delete_generated_episode(self, episode_id: uuid.UUID) -> bool:
        """Delete one persisted episode; return whether a row was removed."""
        return await self._repository.delete(episode_id)

    def _to_detail(self, record: GeneratedEpisode) -> dict[str, Any]:
        """Rebuild the full episode/seo/shorts response shape from a persisted row."""
        lead = self._content_bank.get_character(record.lead_character_id)
        support = self._content_bank.get_character(record.support_character_id)
        location = self._content_bank.get_location(record.location_id)
        total_duration_seconds = sum(scene["duration_seconds"] for scene in record.scenes)
        return {
            "id": record.id,
            "project_id": record.project_id,
            "episode": {
                "theme_id": record.theme_id,
                "theme_label": record.theme_label,
                "title": record.title,
                "lead_character": asdict(lead),
                "support_character": asdict(support),
                "location": asdict(location),
                "lesson": record.lesson,
                "total_duration_seconds": total_duration_seconds,
                "scenes": record.scenes,
            },
            "seo": record.seo_package,
            "shorts": record.shorts_plan,
        }

    def _to_summary(self, record: GeneratedEpisode) -> dict[str, Any]:
        """Build the lightweight list-view representation of a persisted episode."""
        lead = self._content_bank.get_character(record.lead_character_id)
        support = self._content_bank.get_character(record.support_character_id)
        location = self._content_bank.get_location(record.location_id)
        return {
            "id": record.id,
            "project_id": record.project_id,
            "title": record.title,
            "theme_id": record.theme_id,
            "theme_label": record.theme_label,
            "lead_character_name": lead.name,
            "lead_character_image_url": lead.image_url,
            "lead_character_voice_sample_url": lead.voice_sample_url,
            "support_character_name": support.name,
            "support_character_image_url": support.image_url,
            "support_character_voice_sample_url": support.voice_sample_url,
            "location_name": location.name,
            "location_image_url": location.image_url,
            "location_ambient_video_url": location.ambient_video_url,
            "created_at": record.created_at,
        }

"""Application service that exposes Neşeli Orman episode use cases to API adapters."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.services.episode_generator import EpisodeGeneratorService
from app.services.episode_seo import EpisodeSeoService
from app.services.episode_shorts import EpisodeShortsService


class EpisodeService:
    """Coordinate episode, SEO, and Shorts generation for one theme."""

    def __init__(
        self,
        generator: EpisodeGeneratorService | None = None,
        seo: EpisodeSeoService | None = None,
        shorts: EpisodeShortsService | None = None,
    ) -> None:
        self._generator = generator or EpisodeGeneratorService()
        self._seo = seo or EpisodeSeoService()
        self._shorts = shorts or EpisodeShortsService()

    def list_themes(self) -> list[dict[str, str]]:
        """Return every theme's id and Turkish label, in catalog order."""
        return [
            {"theme_id": theme.theme_id, "label": theme.label}
            for theme in self._generator.list_themes()
        ]

    def generate(self, theme_id: str) -> dict[str, Any]:
        """Generate an episode script plus its SEO package and Shorts cut."""
        episode = self._generator.generate(theme_id)
        seo = self._seo.generate(episode)
        shorts = self._shorts.generate(episode)
        return {
            "episode": {
                **asdict(episode),
                "total_duration_seconds": episode.total_duration_seconds,
            },
            "seo": asdict(seo),
            "shorts": {
                **asdict(shorts),
                "total_duration_seconds": shorts.total_duration_seconds,
            },
        }

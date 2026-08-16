"""HTTP contracts for Neşeli Orman episode generation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EpisodeGenerateRequest(BaseModel):
    """Validated input accepted by the episode generation endpoint."""

    theme_id: str = Field(min_length=1, max_length=100)


class ThemeSummaryResponse(BaseModel):
    """A theme's id, Turkish label, and cast/location images, for a theme picker."""

    theme_id: str
    label: str
    lead_character_image_url: str
    support_character_image_url: str
    location_image_url: str


class EpisodeResponse(BaseModel):
    """Transport-safe representation of a generated episode script."""

    theme_id: str
    theme_label: str
    title: str
    lead_character: dict[str, Any]
    support_character: dict[str, Any]
    location: dict[str, Any]
    lesson: str
    total_duration_seconds: int
    scenes: list[dict[str, Any]]


class SeoPackageResponse(BaseModel):
    """Transport-safe representation of a generated SEO package."""

    titles: list[str]
    description: str
    tags: list[str]
    thumbnail_suggestion: str


class ShortsPlanResponse(BaseModel):
    """Transport-safe representation of a generated Shorts cut plan."""

    episode_theme_id: str
    total_duration_seconds: int
    segments: list[dict[str, Any]]


class EpisodeGenerationResponse(BaseModel):
    """Combined output of the episode, SEO, and Shorts generation services."""

    episode: EpisodeResponse
    seo: SeoPackageResponse
    shorts: ShortsPlanResponse

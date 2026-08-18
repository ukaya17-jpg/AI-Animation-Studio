"""HTTP contracts for Neşeli Orman episode generation."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EpisodeGenerateRequest(BaseModel):
    """Validated input accepted by the episode generation endpoint."""

    theme_id: str = Field(min_length=1, max_length=100)
    project_id: uuid.UUID | None = None


class EpisodeBatchGenerateRequest(BaseModel):
    """Validated input accepted by the batch episode generation endpoint."""

    project_id: uuid.UUID | None = None


class BatchGeneratedEpisodeItem(BaseModel):
    """One episode created by a batch-generate call."""

    id: uuid.UUID
    theme_id: str
    theme_label: str
    title: str


class EpisodeBatchGenerateResponse(BaseModel):
    """Result of generating every theme's episode for one project in one call."""

    project_id: uuid.UUID | None
    created: list[BatchGeneratedEpisodeItem]
    skipped_theme_ids: list[str]


class ThemeSummaryResponse(BaseModel):
    """A theme's id, Turkish label, and cast/location images, for a theme picker."""

    theme_id: str
    label: str
    lead_character_name: str
    lead_character_image_url: str
    lead_character_voice_sample_url: str
    support_character_name: str
    support_character_image_url: str
    support_character_voice_sample_url: str
    location_name: str
    location_image_url: str
    location_ambient_video_url: str


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

    id: uuid.UUID
    project_id: uuid.UUID | None
    episode: EpisodeResponse
    seo: SeoPackageResponse
    shorts: ShortsPlanResponse


class GeneratedEpisodeSummaryResponse(BaseModel):
    """One row of the persisted-episode history list."""

    id: uuid.UUID
    project_id: uuid.UUID | None
    title: str
    theme_id: str
    theme_label: str
    lead_character_name: str
    lead_character_image_url: str
    lead_character_voice_sample_url: str
    support_character_name: str
    support_character_image_url: str
    support_character_voice_sample_url: str
    location_name: str
    location_image_url: str
    location_ambient_video_url: str
    created_at: datetime


class GeneratedEpisodeListResponse(BaseModel):
    """One newest-first page of persisted episode summaries."""

    items: list[GeneratedEpisodeSummaryResponse]
    total: int
    page: int
    page_size: int

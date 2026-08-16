"""HTTP contracts for storyboard generation and export."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class StoryboardCreateRequest(BaseModel):
    """Validated input accepted by the storyboard generation endpoint."""

    script: str = Field(min_length=1, max_length=500_000)
    total_duration: float | None = Field(default=None, gt=0, le=86_400)
    title: str = Field(default="Untitled Storyboard", min_length=1, max_length=200)
    learning_objective: str = Field(default="", max_length=1_000)

    @field_validator("script")
    @classmethod
    def script_must_contain_text(cls, value: str) -> str:
        """Reject whitespace-only scripts before domain processing."""
        if not value.strip():
            raise ValueError("script must contain text")
        return value


class StoryboardResponse(BaseModel):
    """Transport-safe representation of a generated storyboard."""

    title: str
    scenes: list[dict[str, Any]]
    total_duration: float
    statistics: dict[str, int | float]
    metadata: dict[str, Any]

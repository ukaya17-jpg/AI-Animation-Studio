"""Application service that exposes storyboard use cases to API adapters."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from app.models.storyboard import Storyboard
from app.services.storyboard_builder import StoryboardBuilder
from app.services.storyboard_exporter import ExportFormat, StoryboardExporter


class StoryboardService:
    """Coordinate build and export operations without HTTP dependencies."""

    def __init__(
        self,
        builder: StoryboardBuilder | None = None,
        exporter: StoryboardExporter | None = None,
    ) -> None:
        self._builder = builder or StoryboardBuilder()
        self._exporter = exporter or StoryboardExporter()

    def create(
        self,
        script: str,
        *,
        total_duration: float | None = None,
        title: str = "Untitled Storyboard",
        learning_objective: str = "",
    ) -> Storyboard:
        """Generate a storyboard from a script."""
        return self._builder.build(
            script,
            total_duration=total_duration,
            title=title,
            learning_objective=learning_objective,
        )

    def as_dict(self, storyboard: Storyboard) -> dict[str, Any]:
        """Convert a domain aggregate into JSON-compatible primitive data."""
        return asdict(storyboard)

    def export(self, storyboard: Storyboard, format: ExportFormat | str) -> str:
        """Export a generated storyboard in the requested format."""
        return self._exporter.export(storyboard, format)

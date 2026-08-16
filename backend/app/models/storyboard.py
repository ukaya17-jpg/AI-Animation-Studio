"""Aggregate model for a generated storyboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.models.scene import Scene

SceneList = list[Scene]
TotalDuration = float
Statistics = dict[str, int | float]
Metadata = dict[str, Any]


@dataclass(slots=True)
class Storyboard:
    """An ordered collection of scenes and its derived production metadata."""

    title: str
    scenes: SceneList
    total_duration: TotalDuration
    statistics: Statistics = field(default_factory=dict)
    metadata: Metadata = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate that the declared duration agrees with the scene timeline."""
        if self.total_duration <= 0:
            raise ValueError("Storyboard total_duration must be greater than zero.")
        if not self.scenes:
            raise ValueError("Storyboard must contain at least one scene.")
        scene_duration = sum(scene.duration for scene in self.scenes)
        if abs(scene_duration - self.total_duration) > 0.01:
            raise ValueError("Storyboard total_duration must equal the sum of scene durations.")

    @property
    def scene_list(self) -> list[Scene]:
        """Provide the requested SceneList concept using Python naming conventions."""
        return self.scenes

    @property
    def end_time(self) -> float:
        """Return the end of the final scene."""
        return self.scenes[-1].end_time

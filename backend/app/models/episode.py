"""Generated Neşeli Orman episode script."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.episode_cast import EpisodeCharacter, EpisodeLocation


@dataclass(frozen=True, slots=True)
class EpisodeScene:
    """One beat of the fixed five-scene episode structure.

    ``speaker``/``dialogue`` are set only when the scene carries an actual
    quoted line, so a UI can render narration and character speech
    distinctly instead of parsing quotes out of free text.
    """

    name: str
    duration_seconds: int
    text: str
    speaker: str | None = None
    dialogue: str | None = None


@dataclass(frozen=True, slots=True)
class Episode:
    """A generated opening → problem → exploration → resolution → closing script."""

    theme_id: str
    theme_label: str
    title: str
    lead_character: EpisodeCharacter
    support_character: EpisodeCharacter
    location: EpisodeLocation
    lesson: str
    scenes: tuple[EpisodeScene, ...]

    @property
    def total_duration_seconds(self) -> int:
        """Return the sum of every scene's nominal duration."""
        return sum(scene.duration_seconds for scene in self.scenes)

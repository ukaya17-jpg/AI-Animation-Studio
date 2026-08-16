"""Distribution-ready outputs derived from a produced episode."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SeoPackage:
    """YouTube discovery metadata generated for one episode."""

    titles: tuple[str, ...]
    description: str
    tags: tuple[str, ...]
    thumbnail_suggestion: str


@dataclass(frozen=True, slots=True)
class ShortsSegment:
    """One beat of a condensed vertical-video cut."""

    name: str
    duration_seconds: int
    text: str


@dataclass(frozen=True, slots=True)
class ShortsPlan:
    """A 45-second hook → problem → interaction → resolution → CTA cut."""

    episode_theme_id: str
    segments: tuple[ShortsSegment, ...]

    @property
    def total_duration_seconds(self) -> int:
        """Return the sum of every segment's duration."""
        return sum(segment.duration_seconds for segment in self.segments)

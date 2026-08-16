"""Fixed-cast domain objects for the Neşeli Orman episode content module."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VoiceProfile:
    """Vocal delivery notes for one character."""

    pitch: str
    pace: str
    tone: str
    catchphrase: str


@dataclass(frozen=True, slots=True)
class EpisodeCharacter:
    """One member of the fixed Neşeli Orman cast."""

    character_id: str
    name: str
    species: str
    role: str
    core_value: str
    personality: tuple[str, ...]
    visual_description: str
    voice: VoiceProfile
    image_url: str


@dataclass(frozen=True, slots=True)
class EpisodeLocation:
    """One fixed location the cast can appear in."""

    location_id: str
    name: str
    type: str
    description: str
    image_url: str


@dataclass(frozen=True, slots=True)
class EpisodeTheme:
    """An educational theme pairing a lead and support character with a location."""

    theme_id: str
    label: str
    lead_character_id: str
    support_character_id: str
    location_id: str
    lesson: str

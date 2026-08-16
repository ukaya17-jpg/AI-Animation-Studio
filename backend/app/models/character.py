"""Reusable character definition for visual continuity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CharacterProfile:
    """Visual, vocal, and behavioral attributes of one story character."""

    character_id: str
    name: str
    age: int | None = None
    gender: str | None = None
    height: str = "average height"
    appearance: str = "distinctive, approachable appearance"
    hair: str = "unspecified hair"
    eyes: str = "unspecified eyes"
    clothes: str = "simple practical clothing"
    colors: tuple[str, ...] = ("#4A90E2", "#F5F1E8", "#2C3E50")
    voice: str = "clear, natural voice"
    personality: str = "curious and composed"
    expressions: tuple[str, ...] = ("neutral", "happy", "thoughtful")
    reference_images: tuple[str, ...] = ()

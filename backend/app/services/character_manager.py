"""In-memory character identity and visual-consistency management."""

from __future__ import annotations

import re
import uuid

from app.models.character import CharacterProfile
from app.models.scene import CharacterReference


class CharacterManager:
    """Own character profiles for one storyboard-production session."""

    def __init__(self) -> None:
        self._characters: dict[str, CharacterProfile] = {}
        self._ids_by_normalized_name: dict[str, str] = {}

    def create_character(self, name: str, **attributes: object) -> CharacterProfile:
        """Create a profile, or return the existing profile for the same name.

        A UUID5 makes IDs deterministic across independently generated scenes while
        the manager still remains free to hold different production-specific data.
        """
        normalized_name = self._normalize_name(name)
        existing_id = self._ids_by_normalized_name.get(normalized_name)
        if existing_id is not None:
            return self._characters[existing_id]
        character_id = str(
            uuid.uuid5(uuid.NAMESPACE_URL, f"ai-animation-studio/character/{normalized_name}")
        )
        allowed = set(CharacterProfile.__dataclass_fields__) - {"character_id", "name"}
        unsupported = set(attributes) - allowed
        if unsupported:
            raise ValueError(f"Unsupported character attributes: {', '.join(sorted(unsupported))}")
        profile = CharacterProfile(character_id=character_id, name=name.strip(), **attributes)  # type: ignore[arg-type]
        self._characters[character_id] = profile
        self._ids_by_normalized_name[normalized_name] = character_id
        return profile

    def get_character(self, character_id: str) -> CharacterProfile:
        """Return a profile by ID, with a clear error for an unknown reference."""
        try:
            return self._characters[character_id]
        except KeyError as error:
            raise KeyError(f"Unknown character ID: {character_id}") from error

    def get_or_create_reference(
        self, name: str, *, expression: str = "neutral", action: str = "present"
    ) -> CharacterReference:
        """Return a stable scene-level reference for a named character."""
        profile = self.create_character(name)
        return CharacterReference(profile.character_id, profile.name, expression, action)

    def list_characters(self) -> list[CharacterProfile]:
        """Return profiles in their creation order."""
        return list(self._characters.values())

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized = re.sub(r"\s+", " ", name.strip()).casefold()
        if not normalized:
            raise ValueError("Character name cannot be empty.")
        return normalized

"""English cinematic prompt generation with character consistency."""

from __future__ import annotations

from app.models.character import CharacterProfile
from app.models.scene import Scene


class PromptGenerator:
    """Generate provider-neutral image, animation, and thumbnail prompts."""

    def generate(
        self, scene: Scene, characters: dict[str, CharacterProfile] | None = None
    ) -> dict[str, str]:
        """Return all prompts required for one scene without mutating it."""
        character_detail = self._character_detail(scene, characters or {})
        setting = ", ".join(
            (
                scene.environment.location,
                scene.environment.lighting,
                f"{scene.environment.weather} weather",
            )
        )
        composition = (
            f"{scene.camera.angle} shot, {scene.camera.lens} lens, {scene.environment.perspective}"
        )
        image = " ".join(
            (
                f"Cinematic animated-film frame of {character_detail} in {setting}.",
                f"{scene.visual_description}.",
                f"{composition}.",
                "Rich color grading, highly detailed, consistent character design.",
            )
        )
        animation = " ".join(
            (
                "Animated cinematic sequence:",
                scene.animation.character_animation + ";",
                scene.animation.camera_animation + ";",
                scene.animation.background_animation + ".",
                scene.animation_description + ".",
                "Preserve identity, wardrobe, proportions, and color palette across frames.",
            )
        )
        thumbnail = " ".join(
            (
                f"High-impact animated-film thumbnail: {character_detail},",
                f"{scene.environment.location}, expressive focal moment,",
                f"{scene.camera.angle} composition, clean readable silhouette,",
                "cinematic lighting, no text.",
            )
        )
        return {"image_prompt": image, "animation_prompt": animation, "thumbnail_prompt": thumbnail}

    @staticmethod
    def _character_detail(scene: Scene, characters: dict[str, CharacterProfile]) -> str:
        details: list[str] = []
        for reference in scene.characters:
            profile = characters.get(reference.character_id)
            if profile is None:
                details.append(f"{reference.name}, {reference.expression} expression")
            else:
                colors = ", ".join(profile.colors)
                details.append(
                    ", ".join(
                        (
                            profile.name,
                            profile.appearance,
                            profile.hair,
                            f"wearing {profile.clothes} in {colors}",
                            f"{reference.expression} expression",
                        )
                    )
                )
        return "; ".join(details) or "the story setting"

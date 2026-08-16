"""Translate a scene into layered animation instructions."""

from __future__ import annotations

from app.models.scene import AnimationInstruction, Scene


class AnimationPlanner:
    """Produce renderer-agnostic motion instructions."""

    def plan(self, scene: Scene) -> AnimationInstruction:
        """Build subtle, composable motion that supports the scene narrative."""
        has_dialogue = bool(scene.dialogues)
        return AnimationInstruction(
            character_animation="Natural gestures and lip sync"
            if has_dialogue
            else "Purposeful natural movement",
            camera_animation=f"{scene.camera.movement} movement with gentle easing",
            object_animation="Relevant props respond naturally to character actions",
            background_animation="Subtle environmental ambience and parallax",
            effects=("soft depth of field", "cinematic motion blur"),
        )

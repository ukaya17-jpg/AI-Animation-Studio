"""Build a timed, production-ready storyboard from plain-text scripts."""

from __future__ import annotations

import logging
import math
import re
from collections.abc import Sequence

from app.models.scene import Dialogue, Narration, Scene
from app.models.storyboard import Storyboard
from app.services.animation_planner import AnimationPlanner
from app.services.background_manager import BackgroundManager
from app.services.camera_planner import CameraPlanner
from app.services.character_manager import CharacterManager
from app.services.prompt_generator import PromptGenerator

logger = logging.getLogger(__name__)


class StoryboardBuilder:
    """Coordinate domain services to convert a script into ordered scenes."""

    WORDS_PER_MINUTE = 150
    SCENES_PER_MINUTE = 4

    def __init__(
        self,
        character_manager: CharacterManager | None = None,
        background_manager: BackgroundManager | None = None,
        camera_planner: CameraPlanner | None = None,
        animation_planner: AnimationPlanner | None = None,
        prompt_generator: PromptGenerator | None = None,
    ) -> None:
        self.character_manager = character_manager or CharacterManager()
        self._background_manager = background_manager or BackgroundManager()
        self._camera_planner = camera_planner or CameraPlanner()
        self._animation_planner = animation_planner or AnimationPlanner()
        self._prompt_generator = prompt_generator or PromptGenerator()

    def build(
        self,
        script: str,
        *,
        total_duration: float | None = None,
        title: str = "Untitled Storyboard",
        learning_objective: str = "",
    ) -> Storyboard:
        """Build a storyboard while preserving the requested total duration.

        At the standard narration rate, a thirty-minute script produces 120
        scenes, comfortably inside the requested 100–150 scene range.
        """
        normalized = " ".join(script.split())
        if not normalized:
            raise ValueError("A storyboard requires a non-empty script.")
        duration = (
            total_duration if total_duration is not None else self._estimate_duration(normalized)
        )
        if duration <= 0:
            raise ValueError("total_duration must be greater than zero.")
        count = max(1, round((duration / 60) * self.SCENES_PER_MINUTE))
        segments = self._split_into_segments(normalized, count)
        durations = self._allocate_durations(segments, duration)
        scenes: list[Scene] = []
        cursor = 0.0
        for index, (segment, scene_duration) in enumerate(
            zip(segments, durations, strict=True), start=1
        ):
            scene = self._create_scene(
                index=index,
                text=segment,
                duration=scene_duration,
                start_time=cursor,
                learning_objective=learning_objective,
            )
            scene.animation = self._animation_planner.plan(scene)
            profiles = {
                profile.character_id: profile
                for profile in self.character_manager.list_characters()
            }
            scene.prompts = self._prompt_generator.generate(scene, profiles)
            scenes.append(scene)
            cursor = scene.end_time
        # Floating-point normalization keeps an exact timeline contract for exporters.
        scenes[-1].end_time = round(duration, 3)
        scenes[-1].duration = round(scenes[-1].end_time - scenes[-1].start_time, 3)
        storyboard = Storyboard(
            title=title,
            scenes=scenes,
            total_duration=round(duration, 3),
            statistics={
                "scene_count": len(scenes),
                "character_count": len(self.character_manager.list_characters()),
                "average_scene_duration": round(duration / len(scenes), 3),
            },
            metadata={"source_word_count": len(normalized.split()), "version": "sprint-2"},
        )
        logger.info("Built storyboard '%s' with %d scenes", title, len(scenes))
        return storyboard

    def _create_scene(
        self, *, index: int, text: str, duration: float, start_time: float, learning_objective: str
    ) -> Scene:
        dialogues, narration = self._extract_speech(text)
        character_names = [dialogue.character_name for dialogue in dialogues]
        characters = [
            self.character_manager.get_or_create_reference(name)
            for name in dict.fromkeys(character_names)
        ]
        end_time = round(start_time + duration, 3)
        return Scene(
            scene_id=f"scene-{index:04d}",
            title=self._title_for(text, index),
            duration=round(duration, 3),
            start_time=round(start_time, 3),
            end_time=end_time,
            camera=self._camera_planner.plan(index, text),
            environment=self._background_manager.create_environment(text, index),
            characters=characters,
            dialogues=dialogues,
            narration=narration,
            visual_description=text,
            animation_description="Motion follows the emotional beat and narration.",
            sound_effects=["subtle room tone"],
            background_music="gentle cinematic underscore",
            transition="Cut" if index == 1 else "Dissolve",
            learning_objective=learning_objective,
        )

    @classmethod
    def _estimate_duration(cls, script: str) -> float:
        return max(1.0, len(script.split()) / cls.WORDS_PER_MINUTE * 60)

    @staticmethod
    def _split_into_segments(script: str, count: int) -> list[str]:
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", script) if part.strip()]
        words = script.split()
        if count >= len(sentences):
            # Word chunks ensure a long requested duration can still be visualized
            # even when the source script contains only a few long paragraphs.
            chunk_size = max(1, math.ceil(len(words) / count))
            chunks = [
                " ".join(words[position : position + chunk_size])
                for position in range(0, len(words), chunk_size)
            ]
            return chunks + [chunks[-1]] * (count - len(chunks))
        groups: list[list[str]] = [[] for _ in range(count)]
        for index, sentence in enumerate(sentences):
            groups[min(count - 1, index * count // len(sentences))].append(sentence)
        return [" ".join(group) for group in groups]

    @staticmethod
    def _allocate_durations(segments: Sequence[str], total_duration: float) -> list[float]:
        weights = [max(1, len(segment.split())) for segment in segments]
        total_weight = sum(weights)
        allocated = [round(total_duration * weight / total_weight, 3) for weight in weights]
        allocated[-1] = round(total_duration - sum(allocated[:-1]), 3)
        return allocated

    def _extract_speech(self, text: str) -> tuple[list[Dialogue], Narration | None]:
        match = re.match(r"^([A-Z][\w -]{0,48}):\s*(.+)$", text)
        if match is None:
            return [], Narration(text=text)
        name, line = match.groups()
        reference = self.character_manager.get_or_create_reference(name)
        return [Dialogue(reference.character_id, reference.name, line)], None

    @staticmethod
    def _title_for(text: str, index: int) -> str:
        words = text.split()[:6]
        return " ".join(words).rstrip(".,!?;") or f"Scene {index}"

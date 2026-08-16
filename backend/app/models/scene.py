"""Typed domain objects for a single storyboard scene."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CharacterReference:
    """A stable reference to a character that appears in a scene."""

    character_id: str
    name: str
    expression: str = "neutral"
    action: str = "present"


@dataclass(frozen=True, slots=True)
class CameraSetting:
    """Composition and movement instructions for the camera."""

    angle: str = "Medium"
    movement: str = "Static"
    lens: str = "50mm"
    framing: str = "eye level"


@dataclass(frozen=True, slots=True)
class EnvironmentSetting:
    """Visual properties of a scene's background."""

    location: str = "Undetermined location"
    lighting: str = "soft natural light"
    weather: str = "clear"
    color_palette: tuple[str, ...] = ("#4A90E2", "#F5F1E8", "#2C3E50")
    perspective: str = "natural perspective"


@dataclass(frozen=True, slots=True)
class Dialogue:
    """A line spoken by a character."""

    character_id: str
    character_name: str
    text: str


@dataclass(frozen=True, slots=True)
class Narration:
    """Voice-over text associated with a scene."""

    text: str
    voice: str = "narrator"


@dataclass(frozen=True, slots=True)
class AnimationInstruction:
    """Motion directions produced by the animation planner."""

    character_animation: str = "Natural idle movement"
    camera_animation: str = "Static camera"
    object_animation: str = "No object movement"
    background_animation: str = "Subtle ambient movement"
    effects: tuple[str, ...] = ()


@dataclass(slots=True)
class Scene:
    """A time-bounded, renderable unit of a storyboard."""

    scene_id: str
    title: str
    duration: float
    start_time: float
    end_time: float
    camera: CameraSetting = field(default_factory=CameraSetting)
    environment: EnvironmentSetting = field(default_factory=EnvironmentSetting)
    characters: list[CharacterReference] = field(default_factory=list)
    dialogues: list[Dialogue] = field(default_factory=list)
    narration: Narration | None = None
    visual_description: str = ""
    animation_description: str = ""
    sound_effects: list[str] = field(default_factory=list)
    background_music: str = ""
    transition: str = "Cut"
    learning_objective: str = ""
    animation: AnimationInstruction = field(default_factory=AnimationInstruction)
    prompts: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Reject invalid time ranges before they reach an exporter or renderer."""
        if self.duration <= 0:
            raise ValueError("Scene duration must be greater than zero.")
        if self.start_time < 0:
            raise ValueError("Scene start_time cannot be negative.")
        if self.end_time < self.start_time:
            raise ValueError("Scene end_time cannot be earlier than start_time.")
        if abs((self.end_time - self.start_time) - self.duration) > 0.01:
            raise ValueError("Scene duration must match end_time minus start_time.")

from app.services.prompt_generator import PromptGenerator
from app.services.storyboard_builder import StoryboardBuilder


def test_prompt_generator_produces_all_english_cinematic_prompts() -> None:
    storyboard = StoryboardBuilder().build("Ada: Welcome to the forest lesson.", total_duration=5)
    prompts = PromptGenerator().generate(storyboard.scenes[0])

    assert set(prompts) == {"image_prompt", "animation_prompt", "thumbnail_prompt"}
    assert "Cinematic" in prompts["image_prompt"]
    assert "Preserve identity" in prompts["animation_prompt"]
    assert "no text" in prompts["thumbnail_prompt"]

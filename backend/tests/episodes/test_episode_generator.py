import pytest

from app.services.content_bank import ContentBank
from app.services.episode_generator import EpisodeGeneratorService

ALL_THEME_IDS = [theme.theme_id for theme in ContentBank().list_themes()]


def test_content_bank_holds_the_full_fixed_cast_and_theme_set() -> None:
    bank = ContentBank()
    assert len(bank.list_themes()) == 20
    assert len({theme.theme_id for theme in bank.list_themes()}) == 20


@pytest.mark.parametrize("theme_id", ALL_THEME_IDS)
def test_generate_builds_a_five_scene_episode_without_error(theme_id: str) -> None:
    episode = EpisodeGeneratorService().generate(theme_id)

    assert episode.theme_id == theme_id
    assert len(episode.scenes) == 5
    assert [scene.name for scene in episode.scenes] == [
        "Açılış",
        "Sorun",
        "Keşif",
        "Çözüm",
        "Kapanış",
    ]
    assert all(scene.text.strip() for scene in episode.scenes)
    assert episode.total_duration_seconds == sum(scene.duration_seconds for scene in episode.scenes)

    opening, _problem, _exploration, _resolution, closing = episode.scenes
    assert opening.speaker == episode.lead_character.name
    assert opening.dialogue == episode.lead_character.voice.catchphrase
    assert closing.speaker == episode.lead_character.name
    assert closing.dialogue is not None and episode.lesson in closing.dialogue


def test_list_themes_returns_all_twenty_in_catalog_order() -> None:
    themes = EpisodeGeneratorService().list_themes()

    assert [theme.theme_id for theme in themes] == ALL_THEME_IDS


def test_generate_rejects_an_unknown_theme_id() -> None:
    with pytest.raises(ValueError, match="Unknown theme id"):
        EpisodeGeneratorService().generate("does-not-exist")

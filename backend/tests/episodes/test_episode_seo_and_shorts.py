from app.services.episode_generator import EpisodeGeneratorService
from app.services.episode_seo import EpisodeSeoService
from app.services.episode_shorts import EpisodeShortsService


def test_seo_service_fills_every_field() -> None:
    episode = EpisodeGeneratorService().generate("cesaret")
    seo = EpisodeSeoService().generate(episode)

    assert len(seo.titles) == 5
    assert all(title.strip() for title in seo.titles)
    assert "00:00 - Açılış" in seo.description
    assert episode.lesson in seo.description
    assert 4 <= len(seo.tags) <= 6
    assert episode.theme_label in seo.thumbnail_suggestion


def test_shorts_service_produces_a_forty_five_second_cut() -> None:
    episode = EpisodeGeneratorService().generate("aile")
    shorts = EpisodeShortsService().generate(episode)

    assert shorts.episode_theme_id == "aile"
    assert [segment.name for segment in shorts.segments] == [
        "hook",
        "problem",
        "interaction",
        "resolution_and_lesson",
        "cta",
    ]
    assert shorts.total_duration_seconds == 45
    assert all(segment.text.strip() for segment in shorts.segments)

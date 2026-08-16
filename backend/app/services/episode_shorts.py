"""Cut a 45-second vertical Shorts plan from a produced episode."""

from __future__ import annotations

from app.models.episode import Episode
from app.models.episode_distribution import ShortsPlan, ShortsSegment


class EpisodeShortsService:
    """Compress an episode into a hook → problem → interaction → resolution+lesson → CTA cut."""

    HOOK_SECONDS = 5
    PROBLEM_SECONDS = 10
    INTERACTION_SECONDS = 10
    RESOLUTION_SECONDS = 15
    CTA_SECONDS = 5

    def generate(self, episode: Episode) -> ShortsPlan:
        """Build the 45-second Shorts cut plan for one generated episode."""
        _opening, problem, exploration, resolution, _closing = episode.scenes
        segments = (
            ShortsSegment(
                name="hook",
                duration_seconds=self.HOOK_SECONDS,
                text=f'{episode.lead_character.name}: "{episode.lead_character.voice.catchphrase}"',
            ),
            ShortsSegment(
                name="problem", duration_seconds=self.PROBLEM_SECONDS, text=problem.text
            ),
            ShortsSegment(
                name="interaction",
                duration_seconds=self.INTERACTION_SECONDS,
                text=exploration.text,
            ),
            ShortsSegment(
                name="resolution_and_lesson",
                duration_seconds=self.RESOLUTION_SECONDS,
                text=resolution.text,
            ),
            ShortsSegment(
                name="cta",
                duration_seconds=self.CTA_SECONDS,
                text="Neşeli Orman'a abone ol, yeni bölümü kaçırma!",
            ),
        )
        return ShortsPlan(episode_theme_id=episode.theme_id, segments=segments)

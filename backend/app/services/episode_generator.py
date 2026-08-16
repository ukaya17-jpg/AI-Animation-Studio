"""Generate a fixed five-scene Neşeli Orman episode script for one theme."""

from __future__ import annotations

from app.models.episode import Episode, EpisodeScene
from app.services.content_bank import ContentBank
from app.services.turkish_suffix import to_dative, to_genitive


class EpisodeGeneratorService:
    """Turn a theme id into an opening → problem → exploration → resolution → closing script."""

    OPENING_SECONDS = 30
    PROBLEM_SECONDS = 45
    EXPLORATION_SECONDS = 60
    RESOLUTION_SECONDS = 60
    CLOSING_SECONDS = 30

    def __init__(self, content_bank: ContentBank | None = None) -> None:
        self._content_bank = content_bank or ContentBank()

    def generate(self, theme_id: str) -> Episode:
        """Build the five-scene episode for the given theme id.

        Raises ``ValueError`` for an unrecognized theme id, matching the
        domain-error convention already used by the storyboard endpoints.
        """
        try:
            theme = self._content_bank.get_theme(theme_id)
        except KeyError as error:
            raise ValueError(str(error)) from error
        lead = self._content_bank.get_character(theme.lead_character_id)
        support = self._content_bank.get_character(theme.support_character_id)
        location = self._content_bank.get_location(theme.location_id)

        scenes = (
            EpisodeScene(
                name="Açılış",
                duration_seconds=self.OPENING_SECONDS,
                text=(
                    f"{lead.name}, güzel bir sabah {to_dative(location.name)} gelir ve "
                    f'arkadaşlarını selamlar. "{lead.voice.catchphrase}"'
                ),
            ),
            EpisodeScene(
                name="Sorun",
                duration_seconds=self.PROBLEM_SECONDS,
                text=(
                    f'{lead.name}, "{theme.label}" ile ilgili beklenmedik bir sorunla '
                    "karşılaşır ve ne yapacağını bilemez."
                ),
            ),
            EpisodeScene(
                name="Keşif",
                duration_seconds=self.EXPLORATION_SECONDS,
                text=(
                    f"{lead.name}, sorunu çözmek için etrafı keşfetmeye başlar. "
                    "Peki ya sen olsaydın, sen ne yapardın?"
                ),
            ),
            EpisodeScene(
                name="Çözüm",
                duration_seconds=self.RESOLUTION_SECONDS,
                text=(
                    f"Tam o sırada {support.name} yardıma gelir. {to_genitive(support.name)} "
                    f"önerisiyle {lead.name} sorunu çözer ve şunu öğrenir: {theme.lesson}"
                ),
            ),
            EpisodeScene(
                name="Kapanış",
                duration_seconds=self.CLOSING_SECONDS,
                text=(
                    f'{lead.name}: "{theme.lesson} Sence sen de bunu deneyebilir misin? '
                    "Bize yorumlarda anlat! Neşeli Orman'a abone olmayı ve zil simgesine "
                    'tıklamayı unutma!"'
                ),
            ),
        )
        return Episode(
            theme_id=theme.theme_id,
            theme_label=theme.label,
            title=f"Neşeli Orman: {theme.label}",
            lead_character=lead,
            support_character=support,
            location=location,
            lesson=theme.lesson,
            scenes=scenes,
        )

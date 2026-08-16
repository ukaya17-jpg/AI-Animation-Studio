"""Generate a YouTube discovery package for a produced episode."""

from __future__ import annotations

from app.models.episode import Episode
from app.models.episode_distribution import SeoPackage


class EpisodeSeoService:
    """Turn an episode into titles, a timestamped description, tags, and a thumbnail brief."""

    def generate(self, episode: Episode) -> SeoPackage:
        """Build the full SEO package for one generated episode."""
        return SeoPackage(
            titles=self._titles(episode),
            description=self._description(episode),
            tags=self._tags(episode),
            thumbnail_suggestion=self._thumbnail(episode),
        )

    @staticmethod
    def _titles(episode: Episode) -> tuple[str, ...]:
        lead = episode.lead_character.name
        support = episode.support_character.name
        label = episode.theme_label
        location = episode.location.name
        return (
            f"Neşeli Orman | {label} - {lead} ile Eğitici Çizgi Film",
            f"{lead} {label} Öğreniyor! | Neşeli Orman Çocuk Çizgi Filmi",
            f"{location} Bölümü: {label} | Neşeli Orman",
            f"{lead} ve {support} ile {label} Dersi | Neşeli Orman",
            f"Çocuklar İçin {label}: Neşeli Orman Bölümü",
        )

    @staticmethod
    def _description(episode: Episode) -> str:
        lines = [
            f"Bu bölümde {episode.lead_character.name}, {episode.theme_label} konusunu öğreniyor!",
            "",
            "Zaman Damgaları:",
        ]
        cursor = 0
        for scene in episode.scenes:
            minutes, seconds = divmod(cursor, 60)
            lines.append(f"{minutes:02d}:{seconds:02d} - {scene.name}")
            cursor += scene.duration_seconds
        lines.extend(("", episode.lesson, "", "Neşeli Orman'a abone olmayı unutmayın!"))
        return "\n".join(lines)

    @staticmethod
    def _tags(episode: Episode) -> tuple[str, ...]:
        return (
            "neşeli orman",
            episode.theme_label.lower(),
            f"{episode.lead_character.name.lower()} neşeli orman",
            "çocuk çizgi filmi",
            "eğitici çizgi film",
            "çocuklar için değerler eğitimi",
        )

    @staticmethod
    def _thumbnail(episode: Episode) -> str:
        return (
            f"{episode.lead_character.name}, {episode.location.name} önünde büyük ve "
            "okunaklı bir ifadeyle bakıyor; parlak renkler, kalın anahtar kelime metni: "
            f'"{episode.theme_label}".'
        )

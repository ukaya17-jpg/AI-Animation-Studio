"""Package one generated episode into a downloadable production ZIP.

The package bundles everything a non-technical creator needs to publish the
episode to YouTube in one click: the readable script, ready-to-paste SEO
text, the Shorts cut plan, and copies of the reference media (character
art, voice samples, location video) already generated for the episode.
"""

from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path
from typing import Any

_STATIC_ROOT = Path(__file__).resolve().parent.parent / "static"

_TURKISH_ASCII_MAP = str.maketrans(
    {
        "ç": "c",
        "Ç": "c",
        "ğ": "g",
        "Ğ": "g",
        "ı": "i",
        "İ": "i",
        "ö": "o",
        "Ö": "o",
        "ş": "s",
        "Ş": "s",
        "ü": "u",
        "Ü": "u",
    }
)

_README_TEXT = """\
NEŞELİ ORMAN — PRODÜKSİYON PAKETİ
==================================

Bu ZIP, bu bölümü YouTube'a yüklemek için ihtiyacın olan her şeyi içerir.
Dosyaları şu şekilde kullanabilirsin:

- senaryo.md
  Bölümün tam, okunabilir senaryosu (sahneler, diyaloglar, ders).
  Seslendirme veya animasyon için referans olarak kullan.

- youtube_baslik_secenekleri.txt
  Video başlığı için 5 hazır seçenek, her satırda bir tane. Birini seç
  ve YouTube Stüdyosu'ndaki "Başlık" alanına yapıştır.

- youtube_aciklama.txt
  Video açıklaması, zaman damgalarıyla birlikte kopyala-yapıştıra hazır.
  YouTube Stüdyosu'ndaki "Açıklama" alanına doğrudan yapıştırabilirsin.

- youtube_etiketler.txt
  Videonun etiketleri, virgülle ayrılmış tek bir satır. YouTube
  Stüdyosu'ndaki "Etiketler" alanına yapıştır.

- shorts_plani.md
  Bu bölümden kesilecek 45 saniyelik bir YouTube Shorts için kurgu
  adımları (kanca, sorun, etkileşim, çözüm+ders, çağrı).

- gorseller/
  Ana karakter, destek karakter ve mekanın referans görselleri.
  Küçük resim (thumbnail) hazırlarken kullanabilirsin.

- sesler/
  Ana ve destek karakterin kısa ses örnekleri. Seslendirmen için
  referans tonu göstermek amacıyla kullan.

- mekan_videosu/
  Bölümün geçtiği mekanın kısa, döngülü arka plan videosu (varsa).
  Kurguda arka plan/geçiş görüntüsü olarak kullanılabilir.

Kod bilmene gerek yok — dosyaları aç, ilgili metinleri kopyala/yapıştır,
görsel ve ses dosyalarını video düzenleme programına sürükle bırak.
"""


class EpisodeExportService:
    """Build the production package ZIP for one generated episode's detail payload."""

    def build(self, detail: dict[str, Any]) -> bytes:
        """Return the ZIP archive bytes for one episode's full detail dict.

        ``detail`` is the same shape ``EpisodeService.get_generated_episode``
        returns (``episode``/``seo``/``shorts`` keys), so the export always
        reflects exactly what the API already serves for that episode.
        """
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            self._write_episode(archive, "", detail)
        return buffer.getvalue()

    def build_batch(self, episodes: list[dict[str, Any]]) -> bytes:
        """Return one ZIP bundling every given episode's production package.

        Each episode gets its own numbered subfolder containing exactly the
        same file layout ``build`` produces for one episode, so a creator can
        also pull a single episode's folder out of the bundle and use it
        standalone.
        """
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            for index, detail in enumerate(episodes, start=1):
                folder = f"{index:02d}-{self._slug(detail['episode']['title'])}"
                self._write_episode(archive, f"{folder}/", detail)
        return buffer.getvalue()

    def filename_for(self, title: str) -> str:
        """Return a safe, ASCII .zip filename derived from an episode title."""
        return f"{self._slug(title)}-produksiyon-paketi.zip"

    def batch_filename_for(self, project_name: str) -> str:
        """Return a safe, ASCII .zip filename derived from a project name."""
        return f"{self._slug(project_name)}-tum-bolumler-paketi.zip"

    def _write_episode(self, archive: zipfile.ZipFile, prefix: str, detail: dict[str, Any]) -> None:
        """Write one episode's production package files, under an optional folder ``prefix``."""
        episode = detail["episode"]
        seo = detail["seo"]
        shorts = detail["shorts"]

        archive.writestr(f"{prefix}senaryo.md", self._script_markdown(episode))
        archive.writestr(f"{prefix}youtube_baslik_secenekleri.txt", "\n".join(seo["titles"]))
        archive.writestr(f"{prefix}youtube_aciklama.txt", seo["description"])
        archive.writestr(f"{prefix}youtube_etiketler.txt", ", ".join(seo["tags"]))
        archive.writestr(f"{prefix}shorts_plani.md", self._shorts_markdown(shorts))
        archive.writestr(f"{prefix}README.txt", _README_TEXT)

        lead = episode["lead_character"]
        support = episode["support_character"]
        location = episode["location"]
        self._add_static_file(archive, f"{prefix}gorseller", lead["image_url"])
        self._add_static_file(archive, f"{prefix}gorseller", support["image_url"])
        self._add_static_file(archive, f"{prefix}gorseller", location["image_url"])
        self._add_static_file(archive, f"{prefix}sesler", lead["voice_sample_url"])
        self._add_static_file(archive, f"{prefix}sesler", support["voice_sample_url"])
        self._add_static_file(archive, f"{prefix}mekan_videosu", location["ambient_video_url"])

    @staticmethod
    def _slug(title: str) -> str:
        """Return a safe, ASCII, lowercase-hyphenated slug derived from any title."""
        ascii_title = title.translate(_TURKISH_ASCII_MAP)
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_title).strip("-").lower()
        return slug or "bolum"

    @staticmethod
    def _script_markdown(episode: dict[str, Any]) -> str:
        lead = episode["lead_character"]
        support = episode["support_character"]
        location = episode["location"]
        lines = [
            f"# {episode['title']}",
            "",
            f"Tema: {episode['theme_label']}",
            f"Toplam süre: {episode['total_duration_seconds']} sn",
            "",
            "## Karakterler",
            f"- Ana Karakter: {lead['name']} ({lead['species']}, {lead['role']})",
            f"- Destek Karakter: {support['name']} ({support['species']}, {support['role']})",
            "",
            "## Mekan",
            f"{location['name']} — {location['description']}",
            "",
            "## Sahneler",
            "",
        ]
        for scene in episode["scenes"]:
            lines.append(f"### {scene['name']} ({scene['duration_seconds']} sn)")
            lines.append(scene["text"])
            if scene.get("speaker") and scene.get("dialogue"):
                lines.append(f'> {scene["speaker"]}: "{scene["dialogue"]}"')
            lines.append("")
        lines.extend(("## Ders", episode["lesson"]))
        return "\n".join(lines)

    @staticmethod
    def _shorts_markdown(shorts: dict[str, Any]) -> str:
        lines = [
            "# Shorts Kurgu Planı",
            "",
            f"Toplam süre: {shorts['total_duration_seconds']} sn",
            "",
        ]
        for segment in shorts["segments"]:
            lines.append(f"## {segment['name']} ({segment['duration_seconds']} sn)")
            lines.append(segment["text"])
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _add_static_file(archive: zipfile.ZipFile, folder: str, static_url: str) -> None:
        """Copy one ``/static/...``-served file into the archive, skipping it if missing."""
        relative_path = static_url.removeprefix("/static/")
        source = _STATIC_ROOT / relative_path
        if source.is_file():
            archive.write(source, f"{folder}/{source.name}")

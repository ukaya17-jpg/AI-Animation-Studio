"""Package one generated episode into a downloadable production ZIP.

The package bundles everything a non-technical creator needs to publish the
episode to YouTube in one click: the readable script, ready-to-paste SEO
text, the Shorts cut plan, and copies of the reference media (character
art, voice samples, location video) already generated for the episode.
"""

from __future__ import annotations

import io
import json
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any

_STATIC_ROOT = Path(__file__).resolve().parent.parent / "static"

# Standard YouTube 1080p30 target — the only spec this project has ever
# produced media at, so it's a fixed constant rather than a per-episode field.
_MANIFEST_FPS = 30
_MANIFEST_WIDTH = 1920
_MANIFEST_HEIGHT = 1080

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

_BATCH_README_TEMPLATE = """\
NEŞELİ ORMAN — PRODÜKSİYON PAKETİ ({title})
{underline}

Bu, çok bölümlü bir toplu pakettir: karakter/mekan görsel, ses ve video
dosyaları her bölümde tekrarlanmaz — ZIP'in kök dizinindeki paylaşılan
``medya/`` klasöründe TEK KOPYA olarak saklanır (aynı karakter/mekan
birden çok bölümde geçtiği için). Bu bölüme özel dosyalar:

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

Bu bölümün medya dosyaları (yollar bu klasöre göre görecelidir):
- Ana karakter ({lead_name}): {lead_image}, {lead_voice}
- Destek karakter ({support_name}): {support_image}, {support_voice}
- Mekan ({location_name}): {location_image}, {location_video}

Kod bilmene gerek yok — dosyaları aç, ilgili metinleri kopyala/yapıştır,
yukarıdaki yollardaki görsel/ses/video dosyalarını video düzenleme
programına sürükle bırak.
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

    def build_batch(self, episodes: list[dict[str, Any]]) -> Path:
        """Write one ZIP bundling every given episode's production package to a temp file.

        Unlike ``build`` (one episode, media embedded in its own folder), a
        batch spans many episodes that keep re-using the same fixed cast and
        locations — so character/location media is deduplicated: every
        unique image/voice/video used by any episode in ``episodes`` is
        written exactly once, under a shared top-level ``medya/`` folder,
        and each episode's numbered subfolder holds only its script/SEO/
        Shorts text plus a ``README.txt`` pointing at that shared media by
        relative path. Without this, a full-catalog export duplicated every
        character/location file once per episode that used it, so the ZIP
        grew roughly linearly with the theme count instead of with the
        (fixed) cast size.

        Written straight to disk (returning a path, not ``bytes``) rather
        than assembled in an in-memory buffer, since the deduplicated media
        set is still real, largely-incompressible binary data — building
        that as one in-process object was enough to exceed container memory
        and crash the whole server. The caller is responsible for deleting
        the returned file once it's been streamed back (e.g. via a
        ``BackgroundTask``).
        """
        descriptor, raw_path = tempfile.mkstemp(suffix=".zip")
        path = Path(raw_path)
        with open(descriptor, "wb") as file_obj:
            with zipfile.ZipFile(file_obj, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
                self._write_shared_media(archive, episodes)
                for index, detail in enumerate(episodes, start=1):
                    folder = f"{index:02d}-{self._slug(detail['episode']['title'])}"
                    self._write_batch_episode(archive, f"{folder}/", detail)
        return path

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
        manifest = self._build_assembly_manifest(detail, shared_media=False)
        archive.writestr(
            f"{prefix}assembly-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2)
        )

        lead = episode["lead_character"]
        support = episode["support_character"]
        location = episode["location"]
        self._add_static_file(archive, f"{prefix}gorseller", lead["image_url"])
        self._add_static_file(archive, f"{prefix}gorseller", support["image_url"])
        self._add_static_file(archive, f"{prefix}gorseller", location["image_url"])
        self._add_static_file(archive, f"{prefix}sesler", lead["voice_sample_url"])
        self._add_static_file(archive, f"{prefix}sesler", support["voice_sample_url"])
        self._add_static_file(archive, f"{prefix}mekan_videosu", location["ambient_video_url"])

    def _write_shared_media(self, archive: zipfile.ZipFile, episodes: list[dict[str, Any]]) -> None:
        """Write every character/location file used by ``episodes`` once, under ``medya/``."""
        characters: dict[str, dict[str, Any]] = {}
        locations: dict[str, dict[str, Any]] = {}
        for detail in episodes:
            episode = detail["episode"]
            for character in (episode["lead_character"], episode["support_character"]):
                characters[character["character_id"]] = character
            location = episode["location"]
            locations[location["location_id"]] = location

        for character in characters.values():
            self._add_static_file(archive, "medya/karakterler", character["image_url"])
            self._add_static_file(archive, "medya/karakterler", character["voice_sample_url"])
        for location in locations.values():
            self._add_static_file(archive, "medya/mekanlar", location["image_url"])
            self._add_static_file(archive, "medya/mekanlar", location["ambient_video_url"])

    def _write_batch_episode(
        self, archive: zipfile.ZipFile, prefix: str, detail: dict[str, Any]
    ) -> None:
        """Write one episode's text files into a batch export, referencing shared ``medya/``."""
        episode = detail["episode"]
        seo = detail["seo"]
        shorts = detail["shorts"]

        archive.writestr(f"{prefix}senaryo.md", self._script_markdown(episode))
        archive.writestr(f"{prefix}youtube_baslik_secenekleri.txt", "\n".join(seo["titles"]))
        archive.writestr(f"{prefix}youtube_aciklama.txt", seo["description"])
        archive.writestr(f"{prefix}youtube_etiketler.txt", ", ".join(seo["tags"]))
        archive.writestr(f"{prefix}shorts_plani.md", self._shorts_markdown(shorts))
        archive.writestr(f"{prefix}README.txt", self._batch_readme(episode))
        manifest = self._build_assembly_manifest(detail, shared_media=True)
        archive.writestr(
            f"{prefix}assembly-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2)
        )

    @classmethod
    def _batch_readme(cls, episode: dict[str, Any]) -> str:
        lead = episode["lead_character"]
        support = episode["support_character"]
        location = episode["location"]
        title = episode["title"]
        return _BATCH_README_TEMPLATE.format(
            title=title,
            underline="=" * (len("NEŞELİ ORMAN — PRODÜKSİYON PAKETİ ()") + len(title)),
            lead_name=lead["name"],
            lead_image=cls._media_relative_path("karakterler", lead["image_url"]),
            lead_voice=cls._media_relative_path("karakterler", lead["voice_sample_url"]),
            support_name=support["name"],
            support_image=cls._media_relative_path("karakterler", support["image_url"]),
            support_voice=cls._media_relative_path("karakterler", support["voice_sample_url"]),
            location_name=location["name"],
            location_image=cls._media_relative_path("mekanlar", location["image_url"]),
            location_video=cls._media_relative_path("mekanlar", location["ambient_video_url"]),
        )

    @classmethod
    def _build_assembly_manifest(
        cls, detail: dict[str, Any], *, shared_media: bool
    ) -> dict[str, Any]:
        """Build the machine-readable, scene-by-scene manifest for automated video assembly.

        Mirrors the same script/media data ``senaryo.md`` already renders as
        prose, but as a stable JSON contract an external tool (e.g. a DaVinci
        Resolve Python script) can parse without scraping Markdown. File
        paths follow the same two layouts the rest of this class already
        writes media under: local ``gorseller/``/``mekan_videosu/`` folders
        for a single export, or the shared ``../medya/`` tree a batch
        export's per-episode folder points its README at.

        ``audioFile`` names a per-scene narration clip this export does not
        itself generate or bundle — nothing in this codebase produces
        per-scene voiceover yet, only the short per-*character* voice
        samples already written to ``sesler/``. It's a deterministic naming
        convention (``<sceneNumber>-<sceneName-slug>-<speaker-slug>.mp3``)
        for wherever a separate voiceover pipeline drops its output, which
        is why ``audioDurationSeconds`` stays ``null`` rather than being
        computed here — the assembly script reads it from that file once it
        exists.
        """
        episode = detail["episode"]
        lead = episode["lead_character"]
        support = episode["support_character"]
        location = episode["location"]

        def media_path(url: str, local_folder: str, shared_folder: str) -> str:
            if shared_media:
                return f"../medya/{shared_folder}/{Path(url).name}"
            return f"{local_folder}/{Path(url).name}"

        background_file = media_path(location["ambient_video_url"], "mekan_videosu", "mekanlar")

        scenes: list[dict[str, Any]] = []
        for index, scene in enumerate(episode["scenes"], start=1):
            speaker = scene.get("speaker")
            if speaker == lead["name"]:
                character_image: str | None = media_path(
                    lead["image_url"], "gorseller", "karakterler"
                )
            elif speaker == support["name"]:
                character_image = media_path(support["image_url"], "gorseller", "karakterler")
            else:
                character_image = None
            speaker_slug = cls._slug(speaker) if speaker else "anlatici"
            scenes.append(
                {
                    "sceneNumber": index,
                    "sceneName": scene["name"],
                    "backgroundType": "video",
                    "backgroundFile": background_file,
                    "characterImage": character_image,
                    "audioFile": (
                        f"sesler/{index:02d}-{cls._slug(scene['name'])}-{speaker_slug}.mp3"
                    ),
                    "audioDurationSeconds": None,
                    "captionText": scene.get("dialogue") or scene["text"],
                    "speaker": speaker or "Anlatıcı",
                }
            )

        return {
            "episodeId": str(detail["id"]),
            "title": episode["title"],
            "themeKey": episode["theme_id"],
            "fps": _MANIFEST_FPS,
            "resolution": {"width": _MANIFEST_WIDTH, "height": _MANIFEST_HEIGHT},
            "scenes": scenes,
            "totalDurationSeconds": episode["total_duration_seconds"],
        }

    @staticmethod
    def _media_relative_path(subfolder: str, static_url: str) -> str:
        """Return the ``../medya/<subfolder>/<file>`` path an episode folder's README shows."""
        return f"../medya/{subfolder}/{Path(static_url).name}"

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

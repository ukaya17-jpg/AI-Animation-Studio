"""Render one generated episode into a downloadable MP4 using ffmpeg.

Only themes with real, per-scene narration audio already on disk (see
``EpisodeExportService.audio_filename_for_scene`` for the naming convention)
can be rendered — right now that's just "paylasma". Rendering a full episode
takes on the order of minutes, not seconds, so it always runs as a background
job: ``start_render`` returns immediately with a ``render_id`` a caller polls
via Redis-backed status until it can download the finished file.
"""

from __future__ import annotations

import asyncio
import json
import math
import shutil
import uuid
from pathlib import Path
from typing import Any, Final

from redis.asyncio import Redis

from app.services.episode_export import EpisodeExportService

_STATIC_ROOT = Path(__file__).resolve().parent.parent / "static"

_FPS = 30
_WIDTH = 1920
_HEIGHT = 1080
_CHARACTER_BOX = 650
_ZOOM_END = 1.05
# The character reference art this project generates all share a near-white
# cream background rather than real alpha transparency (confirmed by sampling
# findik.png's corners: ~(255,245,224)) — colorkey strips it so the overlay
# reads as the character standing in the scene, not a framed photo of them.
_CHARACTER_COLORKEY = "0xFFF5E0"
_CHARACTER_COLORKEY_SIMILARITY = "0.12"
_CHARACTER_COLORKEY_BLEND = "0.08"

_REDIS_KEY_PREFIX = "episode_render:"
_REDIS_TTL_SECONDS = 6 * 60 * 60

MISSING_AUDIO_MESSAGE: Final = "Bu bölüm için henüz tam seslendirme üretilmedi."

# A task not referenced anywhere is eligible for GC before it finishes, even
# while still running on the loop — this set keeps every in-flight render
# task alive until it completes, independent of the request that started it.
_background_tasks: set[asyncio.Task[None]] = set()


class EpisodeRenderService:
    """Turn one generated episode's script + reference media into a narrated MP4."""

    def __init__(self, redis: Redis, export_service: EpisodeExportService | None = None) -> None:
        self._redis = redis
        self._export_service = export_service or EpisodeExportService()

    def audio_dir_for_theme(self, theme_id: str) -> Path:
        """Return where this theme's per-scene narration clips are expected on disk."""
        return _STATIC_ROOT / "episodes" / theme_id / "sesler"

    def missing_audio_message(self, detail: dict[str, Any]) -> str | None:
        """Return a user-facing error if any scene's narration clip isn't on disk yet."""
        episode = detail["episode"]
        audio_dir = self.audio_dir_for_theme(episode["theme_id"])
        for index, scene in enumerate(episode["scenes"], start=1):
            filename = self._export_service.audio_filename_for_scene(
                index, scene["name"], scene.get("speaker")
            )
            if not (audio_dir / filename).is_file():
                return MISSING_AUDIO_MESSAGE
        return None

    async def start_render(self, detail: dict[str, Any]) -> str:
        """Start a background render and return its id; poll ``get_status`` for progress."""
        render_id = uuid.uuid4().hex
        await self._set_status(render_id, {"status": "pending"})
        task = asyncio.create_task(self._run_job(render_id, detail))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)
        return render_id

    async def get_status(self, render_id: str) -> dict[str, Any] | None:
        """Return one render job's status payload, or ``None`` if the id is unknown/expired."""
        raw = await self._redis.get(f"{_REDIS_KEY_PREFIX}{render_id}")
        return json.loads(raw) if raw else None

    async def _set_status(self, render_id: str, payload: dict[str, Any]) -> None:
        await self._redis.set(
            f"{_REDIS_KEY_PREFIX}{render_id}", json.dumps(payload), ex=_REDIS_TTL_SECONDS
        )

    async def _run_job(self, render_id: str, detail: dict[str, Any]) -> None:
        work_dir = Path(f"/tmp/episode-render-{render_id}")
        work_dir.mkdir(parents=True, exist_ok=True)
        try:
            final_path = await self.render(detail, work_dir)
            await self._set_status(render_id, {"status": "completed", "filePath": str(final_path)})
        except Exception as error:  # noqa: BLE001 -- surfaced via job status, not re-raised
            shutil.rmtree(work_dir, ignore_errors=True)
            await self._set_status(render_id, {"status": "failed", "error": str(error)})

    async def render(self, detail: dict[str, Any], work_dir: Path) -> Path:
        """Render every scene, concatenate them, and burn in subtitles; return the final MP4.

        Each scene's on-screen length is driven by its narration clip's real,
        ffprobe-measured duration — not the rough nominal ``duration_seconds``
        estimate in the theme content bank — so picture and voice stay in sync.
        """
        episode = detail["episode"]
        lead = episode["lead_character"]
        support = episode["support_character"]
        location = episode["location"]
        audio_dir = self.audio_dir_for_theme(episode["theme_id"])
        background_path = _resolve_static_path(location["ambient_video_url"])

        scene_paths: list[Path] = []
        subtitle_entries: list[tuple[float, float, str]] = []
        cursor = 0.0
        for index, scene in enumerate(episode["scenes"], start=1):
            speaker = scene.get("speaker")
            filename = self._export_service.audio_filename_for_scene(index, scene["name"], speaker)
            audio_path = audio_dir / filename
            duration = await _ffprobe_duration(audio_path)

            character_path: Path | None = None
            if speaker == lead["name"]:
                character_path = _resolve_static_path(lead["image_url"])
            elif speaker == support["name"]:
                character_path = _resolve_static_path(support["image_url"])

            scene_path = work_dir / f"scene-{index:02d}.mp4"
            await _render_scene(
                background_path=background_path,
                character_path=character_path,
                audio_path=audio_path,
                duration=duration,
                output_path=scene_path,
            )
            scene_paths.append(scene_path)

            caption = scene.get("dialogue") or scene["text"]
            subtitle_text = f"{speaker or 'Anlatıcı'}: {caption}"
            subtitle_entries.append((cursor, cursor + duration, subtitle_text))
            cursor += duration

        concat_path = work_dir / "concat.mp4"
        await _concat_scenes(scene_paths, work_dir / "concat_list.txt", concat_path)

        srt_path = work_dir / "subtitles.srt"
        _write_srt(subtitle_entries, srt_path)

        final_path = work_dir / "final.mp4"
        await _burn_subtitles(concat_path, srt_path, final_path)
        return final_path


def _resolve_static_path(static_url: str) -> Path:
    return _STATIC_ROOT / static_url.removeprefix("/static/")


async def _run_ffmpeg(args: list[str]) -> None:
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"ffmpeg failed ({args[0]}): {stderr.decode(errors='replace')[-2000:]}")


async def _ffprobe_duration(path: Path) -> float:
    args = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {stderr.decode(errors='replace')}")
    return float(stdout.decode().strip())


async def _render_scene(
    *,
    background_path: Path,
    character_path: Path | None,
    audio_path: Path,
    duration: float,
    output_path: Path,
) -> None:
    """Render one scene: looped/cropped background, optional zooming character, muxed audio."""
    background_filter = (
        f"scale={_WIDTH}:{_HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={_WIDTH}:{_HEIGHT},setsar=1,fps={_FPS}"
    )
    if character_path is not None:
        frames = max(1, math.ceil(duration * _FPS))
        increment = (_ZOOM_END - 1.0) / frames
        filter_complex = (
            f"[0:v]{background_filter}[bg];"
            f"[1:v]format=rgba,"
            f"colorkey={_CHARACTER_COLORKEY}:{_CHARACTER_COLORKEY_SIMILARITY}:"
            f"{_CHARACTER_COLORKEY_BLEND},"
            f"scale={_CHARACTER_BOX}:{_CHARACTER_BOX},"
            f"zoompan=z='min(zoom+{increment},{_ZOOM_END})':d={frames}:"
            f"s={_CHARACTER_BOX}x{_CHARACTER_BOX}:fps={_FPS}[char];"
            f"[bg][char]overlay=(W-w)/2:H-h-40:shortest=1[v]"
        )
        args = [
            "ffmpeg",
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(background_path),
            "-loop",
            "1",
            "-framerate",
            str(_FPS),
            "-i",
            str(character_path),
            "-i",
            str(audio_path),
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-map",
            "2:a",
        ]
    else:
        args = [
            "ffmpeg",
            "-y",
            "-stream_loop",
            "-1",
            "-i",
            str(background_path),
            "-i",
            str(audio_path),
            "-filter_complex",
            f"[0:v]{background_filter}[v]",
            "-map",
            "[v]",
            "-map",
            "1:a",
        ]
    args += [
        "-t",
        f"{duration:.3f}",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        str(output_path),
    ]
    await _run_ffmpeg(args)


async def _concat_scenes(scene_paths: list[Path], list_path: Path, output_path: Path) -> None:
    list_path.write_text(
        "\n".join(f"file '{path}'" for path in scene_paths) + "\n", encoding="utf-8"
    )
    await _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_path),
            "-c",
            "copy",
            str(output_path),
        ]
    )


async def _burn_subtitles(input_path: Path, srt_path: Path, output_path: Path) -> None:
    style = "FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=1,Outline=1"
    await _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vf",
            f"subtitles={srt_path}:force_style='{style}'",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "copy",
            str(output_path),
        ]
    )


def _write_srt(entries: list[tuple[float, float, str]], path: Path) -> None:
    def timestamp(seconds: float) -> str:
        millis = round(seconds * 1000)
        hours, remainder = divmod(millis, 3_600_000)
        minutes, remainder = divmod(remainder, 60_000)
        secs, ms = divmod(remainder, 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

    lines: list[str] = []
    for index, (start, end, text) in enumerate(entries, start=1):
        lines.append(str(index))
        lines.append(f"{timestamp(start)} --> {timestamp(end)}")
        lines.append(text)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")

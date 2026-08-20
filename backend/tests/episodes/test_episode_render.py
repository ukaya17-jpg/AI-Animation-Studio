"""Tests for EpisodeRenderService and its /episodes/{id}/render endpoints.

Most tests here inject a fake in-memory Redis (matching the pattern already
used in tests/test_rate_limit.py) and monkeypatch the actual ffmpeg pipeline
out, since CI provisions no real Redis service and the full pipeline takes
minutes, not seconds. ``test_render_produces_a_real_playable_mp4`` is the one
exception: it runs the real ffmpeg pipeline end-to-end (on a single real
scene, to stay fast) and inspects the output with ffprobe, so at least one
test proves the actual render — not just the job bookkeeping around it —
works.
"""

import asyncio
import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import httpx
import pytest

from app.api.dependencies import get_episode_render_service
from app.main import app
from app.services.episode_export import EpisodeExportService
from app.services.episode_render import MISSING_AUDIO_MESSAGE, EpisodeRenderService


class _FakeRedis:
    """In-memory stand-in for the two redis-py async calls the render service uses."""

    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        del ex
        self._store[key] = value


@pytest.fixture
def render_service() -> EpisodeRenderService:
    return EpisodeRenderService(redis=_FakeRedis())  # type: ignore[arg-type]


@pytest.fixture
def _override_render_service(render_service: EpisodeRenderService) -> Iterator[None]:
    app.dependency_overrides[get_episode_render_service] = lambda: render_service
    yield
    app.dependency_overrides.pop(get_episode_render_service, None)


async def _authorized_headers(client: httpx.AsyncClient, email: str) -> dict[str, str]:
    payload = {"email": email, "password": "correct-horse-1"}
    await client.post("/auth/register", json=payload)
    login_response = await client.post("/auth/login", json=payload)
    token: str = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _create_project(client: httpx.AsyncClient, email: str) -> tuple[str, dict[str, str]]:
    headers = await _authorized_headers(client, email)
    project_response = await client.post(
        "/projects", json={"name": "Neşeli Orman"}, headers=headers
    )
    project_id: str = project_response.json()["id"]
    return project_id, headers


async def _poll_status(
    client: httpx.AsyncClient, episode_id: str, render_id: str, *, timeout: float = 5.0
) -> dict[str, Any]:
    deadline = asyncio.get_event_loop().time() + timeout
    while True:
        response = await client.get(f"/episodes/{episode_id}/render/{render_id}/status")
        body: dict[str, Any] = response.json()
        if body["status"] != "pending" or asyncio.get_event_loop().time() > deadline:
            return body
        await asyncio.sleep(0.05)


async def test_render_endpoint_returns_409_when_theme_has_no_narration_audio(
    client: httpx.AsyncClient,
) -> None:
    """Only "paylasma" has real per-scene narration on disk right now — every other
    theme must fail fast and clearly instead of starting a job that can never finish."""
    generated = await client.post("/episodes/generate", json={"theme_id": "arkadaslik"})
    episode_id = generated.json()["id"]

    response = await client.post(f"/episodes/{episode_id}/render")

    assert response.status_code == 409
    assert response.json()["detail"] == MISSING_AUDIO_MESSAGE


async def test_render_endpoint_requires_authentication_for_a_project_episode(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "render-project-owner@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "paylasma", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]

    response = await client.post(f"/episodes/{episode_id}/render")

    assert response.status_code == 401


async def test_render_endpoint_rejects_a_non_owner(client: httpx.AsyncClient) -> None:
    project_id, headers = await _create_project(client, "render-real-owner@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "paylasma", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]
    other_headers = await _authorized_headers(client, "render-intruder@example.com")

    response = await client.post(f"/episodes/{episode_id}/render", headers=other_headers)

    assert response.status_code == 403


async def test_render_endpoint_returns_404_for_an_unknown_episode(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/episodes/00000000-0000-0000-0000-000000000000/render"
    )

    assert response.status_code == 404


async def test_render_status_endpoint_returns_404_for_an_unknown_render_id(
    client: httpx.AsyncClient, _override_render_service: None
) -> None:
    generated = await client.post("/episodes/generate", json={"theme_id": "paylasma"})
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}/render/does-not-exist/status")

    assert response.status_code == 404


async def test_render_download_endpoint_returns_404_before_completion(
    client: httpx.AsyncClient, _override_render_service: None
) -> None:
    generated = await client.post("/episodes/generate", json={"theme_id": "paylasma"})
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}/render/does-not-exist/download")

    assert response.status_code == 404


async def test_render_flow_reaches_completed_status_and_download_serves_the_file(
    client: httpx.AsyncClient,
    render_service: EpisodeRenderService,
    _override_render_service: None,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Exercises the full async job contract (start -> poll -> download) with the
    real ffmpeg pipeline swapped for a fast stub, so this stays a millisecond test
    while still proving the Redis-backed status bookkeeping and the download/cleanup
    endpoint work end to end."""
    stub_output = tmp_path / "final.mp4"
    stub_output.write_bytes(b"fake mp4 bytes")

    async def _fake_render(detail: dict[str, Any], work_dir: Path) -> Path:
        del detail, work_dir
        return stub_output

    monkeypatch.setattr(render_service, "render", _fake_render)

    generated = await client.post("/episodes/generate", json={"theme_id": "paylasma"})
    episode_id = generated.json()["id"]

    start_response = await client.post(f"/episodes/{episode_id}/render")
    assert start_response.status_code == 202
    render_id = start_response.json()["render_id"]

    status_body = await _poll_status(client, episode_id, render_id)
    assert status_body["status"] == "completed"

    download_response = await client.get(f"/episodes/{episode_id}/render/{render_id}/download")
    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "video/mp4"
    assert download_response.headers["content-disposition"].startswith('attachment; filename="')
    assert download_response.headers["content-disposition"].endswith('-video.mp4"')
    assert download_response.content == b"fake mp4 bytes"


async def test_render_flow_surfaces_a_failed_status_when_ffmpeg_errors(
    client: httpx.AsyncClient,
    render_service: EpisodeRenderService,
    _override_render_service: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _failing_render(detail: dict[str, Any], work_dir: Path) -> Path:
        del detail, work_dir
        raise RuntimeError("ffmpeg exploded")

    monkeypatch.setattr(render_service, "render", _failing_render)

    generated = await client.post("/episodes/generate", json={"theme_id": "paylasma"})
    episode_id = generated.json()["id"]

    start_response = await client.post(f"/episodes/{episode_id}/render")
    render_id = start_response.json()["render_id"]

    status_body = await _poll_status(client, episode_id, render_id)
    assert status_body["status"] == "failed"
    assert status_body["error"] == "ffmpeg exploded"


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg is not installed")
async def test_render_produces_a_real_playable_mp4(
    client: httpx.AsyncClient, tmp_path: Path
) -> None:
    """Runs the real ffmpeg pipeline (no mocking) on one real scene of the real
    "paylasma" episode, then inspects the output with ffprobe: this is the one test
    that proves the render actually works, not just the job bookkeeping around it."""
    generated = await client.post("/episodes/generate", json={"theme_id": "paylasma"})
    detail = generated.json()
    detail["episode"]["scenes"] = detail["episode"]["scenes"][:1]

    service = EpisodeRenderService(redis=_FakeRedis(), export_service=EpisodeExportService())  # type: ignore[arg-type]
    final_path = await service.render(detail, tmp_path)

    assert final_path.is_file()
    assert final_path.stat().st_size > 10_000

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-show_entries",
            "stream=codec_type,codec_name",
            "-of",
            "default=noprint_wrappers=1",
            str(final_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "codec_type=video" in probe.stdout
    assert "codec_type=audio" in probe.stdout
    assert "codec_name=h264" in probe.stdout
    assert "codec_name=aac" in probe.stdout

    duration_line = next(line for line in probe.stdout.splitlines() if line.startswith("duration="))
    duration = float(duration_line.split("=")[1])
    assert 1.5 < duration < 3.0

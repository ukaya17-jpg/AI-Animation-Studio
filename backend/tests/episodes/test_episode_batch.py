import io
import json
import os
import tempfile
import zipfile
from pathlib import Path

import httpx
import pytest

_LOW_MEMORY_THRESHOLD_MIB = 512


def _available_memory_mib() -> float | None:
    """Return free system memory in MiB, or ``None`` if it can't be read (non-Linux)."""
    try:
        with open("/proc/meminfo", encoding="utf-8") as meminfo:
            for line in meminfo:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) / 1024
    except OSError:
        return None
    return None


_available_mib = _available_memory_mib()
_skip_if_low_memory = pytest.mark.skipif(
    _available_mib is not None and _available_mib < _LOW_MEMORY_THRESHOLD_MIB,
    reason=(
        "A full-catalog batch export now writes each of the 8 characters' and "
        "6 locations' files exactly once under a shared medya/ folder instead "
        "of once per episode that uses them (see EpisodeExportService.build_batch "
        "and _write_shared_media), so the archive tracks the fixed ~130MB media "
        "set rather than growing with the theme count. httpx's in-process "
        "ASGITransport still has to buffer that response in this same test "
        "process to hand it back (unlike a real deployment, where build_batch "
        "already streams the ZIP from a temp file instead of holding it in "
        "memory), which needs more free RAM than this host currently has."
    ),
)


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


async def test_batch_generate_creates_all_twenty_eight_themes_for_a_project(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "batch-owner@example.com")

    response = await client.post(
        "/episodes/generate-batch", json={"project_id": project_id}, headers=headers
    )

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == project_id
    assert len(body["created"]) == 28
    assert body["skipped_theme_ids"] == []
    theme_ids = {item["theme_id"] for item in body["created"]}
    assert len(theme_ids) == 28
    for item in body["created"]:
        assert item["id"]
        assert item["title"]
        assert item["theme_label"]


async def test_batch_generate_without_project_id_defaults_to_anonymous(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/episodes/generate-batch", json={})

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] is None
    assert len(body["created"]) == 28
    assert body["skipped_theme_ids"] == []


async def test_batch_generate_is_idempotent_for_a_project(client: httpx.AsyncClient) -> None:
    project_id, headers = await _create_project(client, "batch-repeat@example.com")
    await client.post("/episodes/generate-batch", json={"project_id": project_id}, headers=headers)

    second = await client.post(
        "/episodes/generate-batch", json={"project_id": project_id}, headers=headers
    )

    assert second.status_code == 201
    body = second.json()
    assert body["created"] == []
    assert len(body["skipped_theme_ids"]) == 28

    listing = await client.get(
        "/episodes", params={"project_id": project_id, "page_size": 100}, headers=headers
    )
    assert listing.json()["total"] == 28


async def test_batch_generate_anonymous_calls_are_not_deduplicated_against_each_other(
    client: httpx.AsyncClient,
) -> None:
    """Unlike the project-scoped case, two anonymous batch calls both generate
    all 28 fresh — there is no owner to safely scope "already generated" to."""
    first = await client.post("/episodes/generate-batch", json={})
    second = await client.post("/episodes/generate-batch", json={})

    assert len(first.json()["created"]) == 28
    assert len(second.json()["created"]) == 28


async def test_batch_generate_with_project_id_requires_authentication(
    client: httpx.AsyncClient,
) -> None:
    project_id, _headers = await _create_project(client, "batch-unauth@example.com")

    response = await client.post("/episodes/generate-batch", json={"project_id": project_id})

    assert response.status_code == 401


async def test_batch_generate_with_project_id_rejects_a_non_owner(
    client: httpx.AsyncClient,
) -> None:
    project_id, _owner_headers = await _create_project(client, "batch-real-owner@example.com")
    other_headers = await _authorized_headers(client, "batch-intruder@example.com")

    response = await client.post(
        "/episodes/generate-batch", json={"project_id": project_id}, headers=other_headers
    )

    assert response.status_code == 403


async def test_batch_generate_with_project_id_rejects_an_unknown_project(
    client: httpx.AsyncClient,
) -> None:
    headers = await _authorized_headers(client, "batch-ghost-project@example.com")

    response = await client.post(
        "/episodes/generate-batch",
        json={"project_id": "00000000-0000-0000-0000-000000000000"},
        headers=headers,
    )

    assert response.status_code == 403


@_skip_if_low_memory
async def test_export_batch_bundles_every_project_episode_in_its_own_subfolder(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "batch-export-owner@example.com")
    generated = await client.post(
        "/episodes/generate-batch", json={"project_id": project_id}, headers=headers
    )
    created = generated.json()["created"]

    # A full-catalog batch bundles hundreds of MB of duplicated character/
    # location media (see EpisodeExportService.build_batch's docstring), so
    # this streams the response straight to disk and inspects it there —
    # buffering it all as one in-memory `response.content` blob would defeat
    # the point of the export endpoint itself streaming from a temp file
    # instead of holding the archive in process memory.
    descriptor, tmp_path = tempfile.mkstemp(suffix=".zip")
    try:
        async with client.stream(
            "GET", "/episodes/export-batch", params={"project_id": project_id}, headers=headers
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/zip"
            assert response.headers["content-disposition"].startswith('attachment; filename="')
            assert response.headers["content-disposition"].endswith('-tum-bolumler-paketi.zip"')
            with os.fdopen(descriptor, "wb") as file_obj:
                async for chunk in response.aiter_bytes():
                    file_obj.write(chunk)

        archive = zipfile.ZipFile(tmp_path)
        names = archive.namelist()

        episode_folders = {
            name.split("/", 1)[0] for name in names if not name.startswith("medya/")
        }
        assert len(episode_folders) == 28

        # Every folder is numbered 01.. 28 and mirrors the single-export text layout,
        # but no longer carries its own media copies — those live under medya/.
        numbered_prefixes = sorted(folder.split("-", 1)[0] for folder in episode_folders)
        assert numbered_prefixes == [f"{i:02d}" for i in range(1, 29)]
        for folder in episode_folders:
            assert f"{folder}/senaryo.md" in names
            assert f"{folder}/youtube_baslik_secenekleri.txt" in names
            assert f"{folder}/youtube_aciklama.txt" in names
            assert f"{folder}/youtube_etiketler.txt" in names
            assert f"{folder}/shorts_plani.md" in names
            assert f"{folder}/README.txt" in names
            assert not any(
                name.startswith(f"{folder}/") and name.endswith((".png", ".mp3", ".mp4"))
                for name in names
            )

            readme = archive.read(f"{folder}/README.txt").decode("utf-8")
            assert "../medya/karakterler/" in readme
            assert "../medya/mekanlar/" in readme

        # Shared media lives once, under the top-level medya/ tree.
        assert any(name.startswith("medya/karakterler/") for name in names)
        assert any(name.startswith("medya/mekanlar/") for name in names)

        first_folder = sorted(episode_folders)[0]
        script = archive.read(f"{first_folder}/senaryo.md").decode("utf-8")
        assert created[0]["title"] in script
    finally:
        os.remove(tmp_path)


async def test_export_batch_includes_a_valid_assembly_manifest_per_episode(
    client: httpx.AsyncClient,
) -> None:
    """Unlike the single-episode export, a batch episode's media isn't copied into its own
    folder — it lives once under the shared medya/ tree — so the manifest's image/video
    paths must point there (``../medya/...``) instead of the local gorseller/mekan_videosu/
    folders the single export uses. Uses one generated episode (not the full 28-theme
    batch) to stay fast and avoid the low-memory skip the full-catalog tests need."""
    project_id, headers = await _create_project(client, "batch-export-manifest@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "paylasma", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]
    episode = generated.json()["episode"]

    response = await client.get(
        "/episodes/export-batch", params={"project_id": project_id}, headers=headers
    )

    assert response.status_code == 200
    archive = zipfile.ZipFile(io.BytesIO(response.content))
    names = archive.namelist()
    manifest_names = [name for name in names if name.endswith("assembly-manifest.json")]
    assert len(manifest_names) == 1
    manifest = json.loads(archive.read(manifest_names[0]).decode("utf-8"))

    assert manifest["episodeId"] == episode_id
    assert len(manifest["scenes"]) == len(episode["scenes"])
    for manifest_scene in manifest["scenes"]:
        assert manifest_scene["backgroundFile"].startswith("../medya/mekanlar/")
        assert manifest_scene["audioFile"].startswith("sesler/")
        if manifest_scene["characterImage"] is not None:
            assert manifest_scene["characterImage"].startswith("../medya/karakterler/")


@_skip_if_low_memory
async def test_export_batch_deduplicates_shared_character_and_location_media(
    client: httpx.AsyncClient,
) -> None:
    """The fixed cast of 8 characters and 6 locations is reused across all 28
    themes, so each character/location file must land exactly once in the
    archive under medya/ — not once per episode that happens to use it. This
    is the core of the fix: before it, the batch ZIP duplicated every
    character/location file once per episode using it, so the ZIP grew
    roughly linearly with theme count instead of with the fixed cast size."""
    project_id, headers = await _create_project(client, "batch-export-dedup@example.com")
    await client.post("/episodes/generate-batch", json={"project_id": project_id}, headers=headers)

    descriptor, tmp_path = tempfile.mkstemp(suffix=".zip")
    try:
        async with client.stream(
            "GET", "/episodes/export-batch", params={"project_id": project_id}, headers=headers
        ) as response:
            assert response.status_code == 200
            with os.fdopen(descriptor, "wb") as file_obj:
                async for chunk in response.aiter_bytes():
                    file_obj.write(chunk)

        archive = zipfile.ZipFile(tmp_path)
        names = archive.namelist()

        character_media = [name for name in names if name.startswith("medya/karakterler/")]
        location_media = [name for name in names if name.startswith("medya/mekanlar/")]
        # 8 characters x (image + voice sample) = 16; 6 locations x (image + video) = 12.
        assert len(character_media) == 16
        assert len(location_media) == 12
        # Every entry name is unique, i.e. nothing was written into medya/ twice.
        assert len(set(character_media)) == len(character_media)
        assert len(set(location_media)) == len(location_media)

        # No binary media survives outside the shared medya/ tree.
        assert not any(
            name.endswith((".png", ".mp3", ".mp4")) and not name.startswith("medya/")
            for name in names
        )
    finally:
        os.remove(tmp_path)


@_skip_if_low_memory
async def test_export_batch_zip_stays_close_to_the_underlying_media_set_size(
    client: httpx.AsyncClient,
) -> None:
    """Regression guard for the size blow-up the dedup fix addresses: a
    28-theme batch used to duplicate every character/location file into each
    episode's own folder, so the ZIP grew ~linearly with theme count (605MB
    for 28 themes, up from 388MB at 20 themes). With shared media written
    once under medya/, the ZIP should stay close to the fixed underlying
    media set's total size plus the (comparatively tiny) per-episode text
    files, regardless of how many themes/episodes are bundled."""
    project_id, headers = await _create_project(client, "batch-export-size@example.com")
    await client.post("/episodes/generate-batch", json={"project_id": project_id}, headers=headers)

    static_media_root = Path(__file__).resolve().parents[2] / "app" / "static"
    total_media_bytes = sum(f.stat().st_size for f in static_media_root.rglob("*") if f.is_file())

    descriptor, tmp_path = tempfile.mkstemp(suffix=".zip")
    try:
        async with client.stream(
            "GET", "/episodes/export-batch", params={"project_id": project_id}, headers=headers
        ) as response:
            assert response.status_code == 200
            with os.fdopen(descriptor, "wb") as file_obj:
                async for chunk in response.aiter_bytes():
                    file_obj.write(chunk)

        zip_size = os.path.getsize(tmp_path)
        print(
            f"\n[batch export size] underlying media set = "
            f"{total_media_bytes / 1_048_576:.1f} MiB, 28-episode batch ZIP = "
            f"{zip_size / 1_048_576:.1f} MiB"
        )

        # Old per-episode-duplication design would land near 28x a single
        # episode's ~5MB media weight (~140MB) *on top of* itself for every
        # repeat use of a character/location — the deduplicated design must
        # stay within shouting distance of the fixed media set itself.
        assert zip_size < total_media_bytes * 1.5
    finally:
        os.remove(tmp_path)


async def test_export_batch_requires_project_id_query_param(client: httpx.AsyncClient) -> None:
    response = await client.get("/episodes/export-batch")

    assert response.status_code == 422


async def test_export_batch_requires_authentication(client: httpx.AsyncClient) -> None:
    project_id, headers = await _create_project(client, "batch-export-unauth@example.com")
    await client.post("/episodes/generate-batch", json={"project_id": project_id}, headers=headers)

    response = await client.get("/episodes/export-batch", params={"project_id": project_id})

    assert response.status_code == 401


async def test_export_batch_rejects_a_non_owner(client: httpx.AsyncClient) -> None:
    project_id, headers = await _create_project(client, "batch-export-real-owner@example.com")
    await client.post("/episodes/generate-batch", json={"project_id": project_id}, headers=headers)
    other_headers = await _authorized_headers(client, "batch-export-intruder@example.com")

    response = await client.get(
        "/episodes/export-batch", params={"project_id": project_id}, headers=other_headers
    )

    assert response.status_code == 403


async def test_export_batch_returns_404_for_a_project_with_no_generated_episodes(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "batch-export-empty@example.com")

    response = await client.get(
        "/episodes/export-batch", params={"project_id": project_id}, headers=headers
    )

    assert response.status_code == 404


async def test_export_batch_rejects_an_unknown_project(client: httpx.AsyncClient) -> None:
    headers = await _authorized_headers(client, "batch-export-ghost@example.com")

    response = await client.get(
        "/episodes/export-batch",
        params={"project_id": "00000000-0000-0000-0000-000000000000"},
        headers=headers,
    )

    assert response.status_code == 403

import os
import tempfile
import zipfile

import httpx
import pytest

_LOW_MEMORY_THRESHOLD_MIB = 1024


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
        "A full-catalog batch export bundles ~600MB of real character/location "
        "media (28 themes x their images/voices/video, duplicated per episode "
        "folder by design). httpx's in-process ASGITransport has to buffer that "
        "whole response in this same test process to hand it back (unlike a real "
        "deployment, where EpisodeExportService.build_batch already streams the "
        "ZIP from a temp file instead of holding it in memory — see its "
        "docstring), which needs more free RAM than this host currently has."
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

        top_level_folders = {name.split("/", 1)[0] for name in names}
        assert len(top_level_folders) == 28

        # Every folder is numbered 01.. 28 and mirrors the single-export layout.
        numbered_prefixes = sorted(folder.split("-", 1)[0] for folder in top_level_folders)
        assert numbered_prefixes == [f"{i:02d}" for i in range(1, 29)]
        for folder in top_level_folders:
            assert f"{folder}/senaryo.md" in names
            assert f"{folder}/youtube_baslik_secenekleri.txt" in names
            assert f"{folder}/youtube_aciklama.txt" in names
            assert f"{folder}/youtube_etiketler.txt" in names
            assert f"{folder}/shorts_plani.md" in names
            assert f"{folder}/README.txt" in names
            assert any(name.startswith(f"{folder}/gorseller/") for name in names)
            assert any(name.startswith(f"{folder}/sesler/") for name in names)
            assert any(name.startswith(f"{folder}/mekan_videosu/") for name in names)

        first_folder = sorted(top_level_folders)[0]
        script = archive.read(f"{first_folder}/senaryo.md").decode("utf-8")
        assert created[0]["title"] in script
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

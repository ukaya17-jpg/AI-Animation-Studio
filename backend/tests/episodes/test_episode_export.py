import io
import uuid
import zipfile

import httpx


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


async def test_export_endpoint_returns_a_zip_with_the_full_production_package(
    client: httpx.AsyncClient,
) -> None:
    generated = await client.post("/episodes/generate", json={"theme_id": "duygular"})
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}/export")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert response.headers["content-disposition"].startswith('attachment; filename="')
    assert response.headers["content-disposition"].endswith('-produksiyon-paketi.zip"')

    archive = zipfile.ZipFile(io.BytesIO(response.content))
    names = archive.namelist()

    assert "senaryo.md" in names
    assert "youtube_baslik_secenekleri.txt" in names
    assert "youtube_aciklama.txt" in names
    assert "youtube_etiketler.txt" in names
    assert "shorts_plani.md" in names
    assert "README.txt" in names
    assert any(name.startswith("gorseller/") and name.endswith(".png") for name in names)
    assert any(name.startswith("sesler/") and name.endswith(".mp3") for name in names)
    assert any(name.startswith("mekan_videosu/") and name.endswith(".mp4") for name in names)

    # Exactly the lead + support + location image, and the lead + support voice sample.
    assert sum(1 for name in names if name.startswith("gorseller/")) == 3
    assert sum(1 for name in names if name.startswith("sesler/")) == 2
    assert sum(1 for name in names if name.startswith("mekan_videosu/")) == 1

    episode = generated.json()["episode"]
    script = archive.read("senaryo.md").decode("utf-8")
    assert episode["title"] in script
    assert episode["lesson"] in script
    for scene in episode["scenes"]:
        assert scene["name"] in script

    titles = archive.read("youtube_baslik_secenekleri.txt").decode("utf-8").splitlines()
    assert len(titles) == 5
    for title in generated.json()["seo"]["titles"]:
        assert title in titles

    tags_line = archive.read("youtube_etiketler.txt").decode("utf-8")
    for tag in generated.json()["seo"]["tags"]:
        assert tag in tags_line


async def test_export_endpoint_bundles_a_new_character_and_location_correctly(
    client: httpx.AsyncClient,
) -> None:
    """The Görev-B content expansion added Kurnaz/Gizli Mağara; make sure their real
    downloaded image/voice/video files actually land in the export ZIP, not just the
    theme metadata (``_add_static_file`` silently skips a file that isn't on disk)."""
    generated = await client.post("/episodes/generate", json={"theme_id": "yaratici_dusunme"})
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}/export")

    assert response.status_code == 200
    archive = zipfile.ZipFile(io.BytesIO(response.content))
    names = archive.namelist()

    assert "gorseller/kurnaz.png" in names
    assert "sesler/kurnaz.mp3" in names
    assert "gorseller/gizli_magara.png" in names
    assert "mekan_videosu/gizli_magara.mp4" in names

    tags_line = archive.read("youtube_etiketler.txt").decode("utf-8")
    assert "kurnaz neşeli orman" in tags_line


async def test_export_endpoint_returns_404_for_an_unknown_id(client: httpx.AsyncClient) -> None:
    response = await client.get(f"/episodes/{uuid.uuid4()}/export")

    assert response.status_code == 404


async def test_export_endpoint_requires_authentication_for_a_project_episode(
    client: httpx.AsyncClient,
) -> None:
    project_id, headers = await _create_project(client, "export-project-owner@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}/export")

    assert response.status_code == 401


async def test_export_endpoint_rejects_a_non_owner(client: httpx.AsyncClient) -> None:
    project_id, headers = await _create_project(client, "export-real-owner@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]
    other_headers = await _authorized_headers(client, "export-intruder@example.com")

    response = await client.get(f"/episodes/{episode_id}/export", headers=other_headers)

    assert response.status_code == 403


async def test_export_endpoint_allows_the_owner(client: httpx.AsyncClient) -> None:
    project_id, headers = await _create_project(client, "export-owner-allowed@example.com")
    generated = await client.post(
        "/episodes/generate",
        json={"theme_id": "duygular", "project_id": project_id},
        headers=headers,
    )
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}/export", headers=headers)

    assert response.status_code == 200


async def test_export_endpoint_stays_open_for_a_project_less_episode(
    client: httpx.AsyncClient,
) -> None:
    generated = await client.post("/episodes/generate", json={"theme_id": "duygular"})
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}/export")

    assert response.status_code == 200

import uuid

import httpx


async def _create_project(client: httpx.AsyncClient, email: str) -> str:
    payload = {"email": email, "password": "correct-horse-1"}
    await client.post("/auth/register", json=payload)
    login_response = await client.post("/auth/login", json=payload)
    headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
    project_response = await client.post(
        "/projects", json={"name": "Neşeli Orman"}, headers=headers
    )
    project_id: str = project_response.json()["id"]
    return project_id


async def test_list_themes_endpoint_returns_all_twenty_themes(client: httpx.AsyncClient) -> None:
    response = await client.get("/episodes/themes")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 20
    paylasma = next(item for item in body if item["theme_id"] == "paylasma")
    assert paylasma["label"] == "Paylaşma"
    assert paylasma["lead_character_name"]
    assert paylasma["lead_character_image_url"] == "/static/characters/findik.png"
    assert paylasma["support_character_name"]
    assert paylasma["support_character_image_url"] == "/static/characters/boncuk.png"
    assert paylasma["location_name"]
    assert paylasma["location_image_url"] == "/static/locations/paylasim_bahcesi.png"


async def test_generate_episode_endpoint_returns_episode_seo_and_shorts(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/episodes/generate", json={"theme_id": "duygular"})

    assert response.status_code == 201
    body = response.json()
    assert uuid.UUID(body["id"])
    assert body["episode"]["theme_id"] == "duygular"
    assert len(body["episode"]["scenes"]) == 5
    assert len(body["seo"]["titles"]) == 5
    assert body["shorts"]["total_duration_seconds"] == 45


async def test_generate_episode_endpoint_returns_404_for_unknown_theme(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/episodes/generate", json={"theme_id": "does-not-exist"})

    assert response.status_code == 404


async def test_generated_episode_is_persisted_and_listed(client: httpx.AsyncClient) -> None:
    generated = await client.post("/episodes/generate", json={"theme_id": "cesaret"})
    episode_id = generated.json()["id"]

    response = await client.get("/episodes")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["page"] == 1
    assert body["page_size"] == 20
    [summary] = body["items"]
    assert summary["id"] == episode_id
    assert summary["theme_id"] == "cesaret"
    assert summary["title"] == "Neşeli Orman: Cesaret"
    assert summary["lead_character_name"]
    assert summary["lead_character_image_url"] == "/static/characters/minik.png"


async def test_generated_episodes_list_is_newest_first(client: httpx.AsyncClient) -> None:
    first = await client.post("/episodes/generate", json={"theme_id": "paylasma"})
    second = await client.post("/episodes/generate", json={"theme_id": "aile"})

    response = await client.get("/episodes")

    ids = [item["id"] for item in response.json()["items"]]
    assert ids == [second.json()["id"], first.json()["id"]]


async def test_get_generated_episode_endpoint_returns_full_detail(
    client: httpx.AsyncClient,
) -> None:
    generated = await client.post("/episodes/generate", json={"theme_id": "sayilar"})
    episode_id = generated.json()["id"]

    response = await client.get(f"/episodes/{episode_id}")

    assert response.status_code == 200
    assert response.json() == generated.json()


async def test_get_generated_episode_endpoint_returns_404_for_unknown_id(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get(f"/episodes/{uuid.uuid4()}")

    assert response.status_code == 404


async def test_generate_episode_endpoint_accepts_an_optional_project_id(
    client: httpx.AsyncClient,
) -> None:
    project_id = await _create_project(client, "project-owner@example.com")

    response = await client.post(
        "/episodes/generate", json={"theme_id": "duygular", "project_id": project_id}
    )

    assert response.status_code == 201
    assert response.json()["project_id"] == project_id


async def test_generate_episode_endpoint_defaults_project_id_to_null(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/episodes/generate", json={"theme_id": "duygular"})

    assert response.status_code == 201
    assert response.json()["project_id"] is None


async def test_list_generated_episodes_filters_by_project_id(client: httpx.AsyncClient) -> None:
    project_id = await _create_project(client, "filter-owner@example.com")
    in_project = await client.post(
        "/episodes/generate", json={"theme_id": "cesaret", "project_id": project_id}
    )
    await client.post("/episodes/generate", json={"theme_id": "aile"})

    response = await client.get("/episodes", params={"project_id": project_id})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == in_project.json()["id"]


async def test_delete_generated_episode_endpoint_removes_it(client: httpx.AsyncClient) -> None:
    generated = await client.post("/episodes/generate", json={"theme_id": "arkadaslik"})
    episode_id = generated.json()["id"]

    delete_response = await client.delete(f"/episodes/{episode_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/episodes/{episode_id}")
    assert get_response.status_code == 404

    second_delete_response = await client.delete(f"/episodes/{episode_id}")
    assert second_delete_response.status_code == 404

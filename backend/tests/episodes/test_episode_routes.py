import httpx

from app.main import app


async def test_list_themes_endpoint_returns_all_nine_themes() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.get("/episodes/themes")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 9
    assert {"theme_id": "paylasma", "label": "Paylaşma"} in body


async def test_generate_episode_endpoint_returns_episode_seo_and_shorts() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post("/episodes/generate", json={"theme_id": "duygular"})

    assert response.status_code == 201
    body = response.json()
    assert body["episode"]["theme_id"] == "duygular"
    assert len(body["episode"]["scenes"]) == 5
    assert len(body["seo"]["titles"]) == 5
    assert body["shorts"]["total_duration_seconds"] == 45


async def test_generate_episode_endpoint_returns_404_for_unknown_theme() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post("/episodes/generate", json={"theme_id": "does-not-exist"})

    assert response.status_code == 404

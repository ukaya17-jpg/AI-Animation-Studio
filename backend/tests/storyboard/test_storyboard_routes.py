import httpx

from app.main import app


async def test_create_storyboard_endpoint_returns_timed_scenes() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/storyboards",
            json={
                "script": "Ada: Welcome to the classroom. Ada: We will learn about light.",
                "total_duration": 30,
                "title": "Light lesson",
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Light lesson"
    assert body["total_duration"] == 30
    assert body["scenes"][0]["scene_id"] == "scene-0001"
    assert body["scenes"][-1]["end_time"] == 30


async def test_export_endpoint_returns_requested_text_format() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post(
            "/storyboards/export/markdown",
            json={"script": "A calm opening scene.", "total_duration": 5, "title": "Export test"},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "# Export test" in response.text


async def test_create_storyboard_endpoint_rejects_blank_script() -> None:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post("/storyboards", json={"script": "   "})

    assert response.status_code == 422

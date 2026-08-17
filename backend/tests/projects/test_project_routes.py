import httpx


async def _authorized_headers(client: httpx.AsyncClient, email: str) -> dict[str, str]:
    payload = {"email": email, "password": "correct-horse-1"}
    await client.post("/auth/register", json=payload)
    login_response = await client.post("/auth/login", json=payload)
    token: str = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_create_project_returns_it_owned_by_the_current_user(
    client: httpx.AsyncClient,
) -> None:
    headers = await _authorized_headers(client, "owner@example.com")

    response = await client.post("/projects", json={"name": "Neşeli Orman"}, headers=headers)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Neşeli Orman"
    assert body["owner_id"]


async def test_create_project_requires_authentication(client: httpx.AsyncClient) -> None:
    response = await client.post("/projects", json={"name": "Neşeli Orman"})

    assert response.status_code == 401


async def test_list_projects_returns_only_the_current_users_projects(
    client: httpx.AsyncClient,
) -> None:
    owner_headers = await _authorized_headers(client, "first@example.com")
    other_headers = await _authorized_headers(client, "second@example.com")
    await client.post("/projects", json={"name": "Owner Project"}, headers=owner_headers)
    await client.post("/projects", json={"name": "Other Project"}, headers=other_headers)

    response = await client.get("/projects", headers=owner_headers)

    assert response.status_code == 200
    names = [project["name"] for project in response.json()]
    assert names == ["Owner Project"]


async def test_create_project_rejects_blank_name(client: httpx.AsyncClient) -> None:
    headers = await _authorized_headers(client, "blank@example.com")

    response = await client.post("/projects", json={"name": ""}, headers=headers)

    assert response.status_code == 422


async def test_create_project_rejects_a_name_over_the_max_length(
    client: httpx.AsyncClient,
) -> None:
    headers = await _authorized_headers(client, "toolong@example.com")

    response = await client.post("/projects", json={"name": "x" * 201}, headers=headers)

    assert response.status_code == 422


async def test_create_project_rejects_malformed_json_body(client: httpx.AsyncClient) -> None:
    headers = await _authorized_headers(client, "malformed@example.com")

    response = await client.post(
        "/projects",
        content=b"{not valid json",
        headers={**headers, "Content-Type": "application/json"},
    )

    assert response.status_code == 422


async def test_create_project_stores_script_like_name_as_inert_data(
    client: httpx.AsyncClient,
) -> None:
    """A project name is never rendered as HTML server-side; this pins that a
    markup-shaped name round-trips as plain JSON text, never executed or stripped."""
    headers = await _authorized_headers(client, "xss@example.com")
    name = "<script>alert(1)</script>"

    response = await client.post("/projects", json={"name": name}, headers=headers)

    assert response.status_code == 201
    assert response.json()["name"] == name

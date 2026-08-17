import uuid

import httpx

from app.core.config import get_settings
from app.core.security import create_access_token


async def test_register_creates_a_user(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/auth/register", json={"email": "ayse@example.com", "password": "correct-horse-1"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "ayse@example.com"
    assert "password" not in body
    assert "hashed_password" not in body


async def test_register_rejects_duplicate_email(client: httpx.AsyncClient) -> None:
    payload = {"email": "dup@example.com", "password": "correct-horse-1"}
    first = await client.post("/auth/register", json=payload)
    second = await client.post("/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


async def test_register_rejects_short_password(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/auth/register", json={"email": "short@example.com", "password": "abc"}
    )

    assert response.status_code == 422


async def test_register_rejects_invalid_email(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/auth/register", json={"email": "not-an-email", "password": "correct-horse-1"}
    )

    assert response.status_code == 422


async def test_login_returns_access_token_for_correct_credentials(
    client: httpx.AsyncClient,
) -> None:
    payload = {"email": "login@example.com", "password": "correct-horse-1"}
    await client.post("/auth/register", json=payload)

    response = await client.post("/auth/login", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and body["access_token"]


async def test_login_rejects_wrong_password(client: httpx.AsyncClient) -> None:
    await client.post(
        "/auth/register", json={"email": "wrong@example.com", "password": "correct-horse-1"}
    )

    response = await client.post(
        "/auth/login", json={"email": "wrong@example.com", "password": "incorrect-password"}
    )

    assert response.status_code == 401


async def test_login_rejects_unknown_email(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/auth/login", json={"email": "ghost@example.com", "password": "correct-horse-1"}
    )

    assert response.status_code == 401


async def test_access_token_authenticates_a_protected_route(client: httpx.AsyncClient) -> None:
    payload = {"email": "protected@example.com", "password": "correct-horse-1"}
    await client.post("/auth/register", json=payload)
    login_response = await client.post("/auth/login", json=payload)
    token = login_response.json()["access_token"]

    response = await client.get("/projects", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200


async def test_protected_route_rejects_missing_token(client: httpx.AsyncClient) -> None:
    response = await client.get("/projects")

    assert response.status_code == 401


async def test_protected_route_rejects_malformed_token(client: httpx.AsyncClient) -> None:
    response = await client.get(
        "/projects", headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401


async def test_register_rejects_malformed_json_body(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/auth/register",
        content=b"{not valid json",
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422


async def test_protected_route_rejects_a_well_formed_token_for_a_deleted_user(
    client: httpx.AsyncClient,
) -> None:
    """A cryptographically valid token whose user no longer exists must still be
    rejected, not treated as authenticated with a missing user."""
    token = create_access_token(uuid.uuid4(), get_settings())

    response = await client.get("/projects", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


async def test_register_rejects_an_overlong_password(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/auth/register", json={"email": "toolong@example.com", "password": "x" * 201}
    )

    assert response.status_code == 422

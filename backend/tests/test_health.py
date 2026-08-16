import httpx

from app.api.dependencies import get_health_service
from app.core.exceptions import ServiceUnavailableError
from app.main import app


def _client() -> httpx.AsyncClient:
    """Create an in-process HTTP client without the platform TestClient portal."""
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver")


async def test_health_check_returns_service_metadata() -> None:
    async with _client() as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "AI Animation Studio API",
        "version": "0.1.0",
    }


async def test_readiness_check_returns_dependency_status() -> None:
    class ReadyHealthService:
        async def readiness(self):
            from app.schemas.health import HealthResponse

            return HealthResponse(
                status="ok",
                service="AI Animation Studio API",
                version="0.1.0",
                dependencies={"database": True, "redis": True},
            )

    async def get_ready_health_service() -> ReadyHealthService:
        return ReadyHealthService()

    app.dependency_overrides[get_health_service] = get_ready_health_service
    try:
        async with _client() as client:
            response = await client.get("/health/ready")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["dependencies"] == {"database": True, "redis": True}


async def test_readiness_check_returns_503_when_dependency_is_unavailable() -> None:
    class UnreadyHealthService:
        async def readiness(self):
            raise ServiceUnavailableError("One or more required dependencies are unavailable.")

    async def get_unready_health_service() -> UnreadyHealthService:
        return UnreadyHealthService()

    app.dependency_overrides[get_health_service] = get_unready_health_service
    try:
        async with _client() as client:
            response = await client.get("/health/ready")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 503
    assert response.json() == {"detail": "One or more required dependencies are unavailable."}


async def test_health_response_includes_security_headers() -> None:
    async with _client() as client:
        response = await client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert (
        response.headers["content-security-policy"] == "default-src 'none'; frame-ancestors 'none'"
    )


async def test_health_response_includes_request_id() -> None:
    async with _client() as client:
        response = await client.get("/health", headers={"X-Request-ID": "test-request-123"})
    assert response.headers["x-request-id"] == "test-request-123"

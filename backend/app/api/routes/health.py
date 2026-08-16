from fastapi import APIRouter, Depends

from app.api.dependencies import get_health_service
from app.schemas.health import HealthResponse
from app.services.health import HealthService

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    response_model_exclude_none=True,
    summary="Service health",
)
async def health_check(
    service: HealthService = Depends(get_health_service),  # noqa: B008
) -> HealthResponse:
    """Return lightweight service metadata without dependency checks."""
    return service.liveness()


@router.get(
    "/health/ready",
    response_model=HealthResponse,
    response_model_exclude_none=True,
    responses={503: {"description": "A required dependency is unavailable."}},
    summary="Service readiness",
)
async def readiness_check(
    service: HealthService = Depends(get_health_service),  # noqa: B008
) -> HealthResponse:
    """Verify database and Redis availability before accepting workload."""
    return await service.readiness()

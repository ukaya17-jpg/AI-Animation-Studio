"""Project (animation channel) HTTP endpoints, scoped to the authenticated user."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_project_service
from app.models.user import User
from app.schemas.project import ProjectCreateRequest, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects")


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=201,
    summary="Create a new project owned by the authenticated user",
)
async def create_project(
    payload: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: ProjectService = Depends(get_project_service),  # noqa: B008
) -> ProjectResponse:
    """Create a project under the current user's account."""
    project = await service.create(owner_id=current_user.id, name=payload.name)
    return ProjectResponse.model_validate(project)


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="List every project owned by the authenticated user",
)
async def list_projects(
    current_user: User = Depends(get_current_user),  # noqa: B008
    service: ProjectService = Depends(get_project_service),  # noqa: B008
) -> list[ProjectResponse]:
    """Return every project owned by the current user."""
    projects = await service.list_for_owner(current_user.id)
    return [ProjectResponse.model_validate(project) for project in projects]

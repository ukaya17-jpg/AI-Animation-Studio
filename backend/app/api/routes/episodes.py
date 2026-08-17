"""Neşeli Orman episode generation HTTP endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_episode_service
from app.schemas.episode import (
    EpisodeGenerateRequest,
    EpisodeGenerationResponse,
    GeneratedEpisodeListResponse,
    ThemeSummaryResponse,
)
from app.services.episode_service import EpisodeService

router = APIRouter(prefix="/episodes")


@router.get(
    "/themes",
    response_model=list[ThemeSummaryResponse],
    summary="List the fixed Neşeli Orman themes available for generation",
)
async def list_themes(
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
) -> list[ThemeSummaryResponse]:
    """Return every theme id and label the generation endpoint accepts."""
    return [ThemeSummaryResponse.model_validate(theme) for theme in service.list_themes()]


@router.get(
    "",
    response_model=GeneratedEpisodeListResponse,
    summary="List previously generated episodes, newest first",
)
async def list_generated_episodes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    project_id: uuid.UUID | None = Query(default=None),  # noqa: B008
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
) -> GeneratedEpisodeListResponse:
    """Return one newest-first page of previously generated episode summaries.

    Pass ``project_id`` to scope the page to episodes generated under that project.
    """
    result = await service.list_generated_episodes(
        page=page, page_size=page_size, project_id=project_id
    )
    return GeneratedEpisodeListResponse.model_validate(result)


@router.post(
    "/generate",
    response_model=EpisodeGenerationResponse,
    status_code=201,
    summary="Generate a Neşeli Orman episode with its SEO and Shorts package",
)
async def generate_episode(
    payload: EpisodeGenerateRequest,
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
) -> EpisodeGenerationResponse:
    """Turn a fixed theme id into a full episode script, SEO package, and Shorts cut."""
    try:
        result = await service.generate(payload.theme_id, project_id=payload.project_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return EpisodeGenerationResponse.model_validate(result)


@router.get(
    "/{episode_id}",
    response_model=EpisodeGenerationResponse,
    summary="Get one previously generated episode's full script, SEO, and Shorts package",
)
async def get_generated_episode(
    episode_id: uuid.UUID,
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
) -> EpisodeGenerationResponse:
    """Return one persisted episode by id, or 404 if it doesn't exist."""
    result = await service.get_generated_episode(episode_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Generated episode not found.")
    return EpisodeGenerationResponse.model_validate(result)


@router.delete(
    "/{episode_id}",
    status_code=204,
    summary="Delete one previously generated episode",
)
async def delete_generated_episode(
    episode_id: uuid.UUID,
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
) -> None:
    """Delete one persisted episode by id, or 404 if it doesn't exist."""
    deleted = await service.delete_generated_episode(episode_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Generated episode not found.")

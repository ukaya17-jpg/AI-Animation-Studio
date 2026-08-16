"""Neşeli Orman episode generation HTTP endpoints."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_episode_service
from app.schemas.episode import EpisodeGenerateRequest, EpisodeGenerationResponse
from app.services.episode_service import EpisodeService

router = APIRouter(prefix="/episodes")


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
        result = service.generate(payload.theme_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return EpisodeGenerationResponse.model_validate(result)

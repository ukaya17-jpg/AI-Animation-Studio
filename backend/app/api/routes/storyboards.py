"""Storyboard generation HTTP endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from app.api.dependencies import get_storyboard_service
from app.schemas.storyboard import StoryboardCreateRequest, StoryboardResponse
from app.services.storyboard_exporter import ExportFormat
from app.services.storyboard_service import StoryboardService

router = APIRouter(prefix="/storyboards")


@router.post(
    "", response_model=StoryboardResponse, status_code=201, summary="Generate a storyboard"
)
async def create_storyboard(
    payload: StoryboardCreateRequest,
    service: StoryboardService = Depends(get_storyboard_service),  # noqa: B008
) -> StoryboardResponse:
    """Turn a script into an unsaved storyboard payload."""
    try:
        storyboard = service.create(
            payload.script,
            total_duration=payload.total_duration,
            title=payload.title,
            learning_objective=payload.learning_objective,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return StoryboardResponse.model_validate(service.as_dict(storyboard))


@router.post(
    "/export/{format}", response_class=PlainTextResponse, summary="Generate and export a storyboard"
)
async def export_storyboard(
    format: ExportFormat,
    payload: StoryboardCreateRequest,
    service: StoryboardService = Depends(get_storyboard_service),  # noqa: B008
) -> PlainTextResponse:
    """Generate a storyboard and return a portable plain-text representation."""
    try:
        storyboard = service.create(
            payload.script,
            total_duration=payload.total_duration,
            title=payload.title,
            learning_objective=payload.learning_objective,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    media_type = "application/json" if format is ExportFormat.JSON else "text/plain"
    return PlainTextResponse(service.export(storyboard, format), media_type=media_type)

"""Neşeli Orman episode generation HTTP endpoints."""

import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.api.dependencies import (
    get_episode_export_service,
    get_episode_render_service,
    get_episode_service,
    get_optional_current_user,
    get_project_service,
)
from app.models.user import User
from app.schemas.episode import (
    BatchGeneratedEpisodeItem,
    EpisodeBatchGenerateRequest,
    EpisodeBatchGenerateResponse,
    EpisodeGenerateRequest,
    EpisodeGenerationResponse,
    GeneratedEpisodeListResponse,
    RenderStartResponse,
    RenderStatusResponse,
    ThemeSummaryResponse,
)
from app.services.episode_export import EpisodeExportService
from app.services.episode_render import EpisodeRenderService
from app.services.episode_service import EpisodeService
from app.services.project_service import ProjectService

router = APIRouter(prefix="/episodes")


async def _authorize_project_access(
    project_id: uuid.UUID, current_user: User | None, project_service: ProjectService
) -> None:
    """Raise 401/403 unless the caller owns ``project_id``.

    A missing/invalid token is 401 ("who are you"); a valid token for a
    project the caller doesn't own is 403 ("not yours") — and a project_id
    that doesn't exist at all is folded into the same 403 rather than 404,
    so an unauthorized caller can't use the response to probe which
    project ids exist.
    """
    if current_user is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication is required to use project_id.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    project = await project_service.get_by_id(project_id)
    if project is None or project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have access to this project.")


async def _get_authorized_episode(
    episode_id: uuid.UUID,
    current_user: User | None,
    project_service: ProjectService,
    service: EpisodeService,
) -> dict[str, Any]:
    """Return one episode's full detail, enforcing the same 404/401/403 visibility
    rule ``GET``/``export`` already use: project-linked episodes require that
    project's owner, project-less episodes stay open."""
    result = await service.get_generated_episode(episode_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Generated episode not found.")
    if result["project_id"] is not None:
        await _authorize_project_access(result["project_id"], current_user, project_service)
    return result


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
    current_user: User | None = Depends(get_optional_current_user),  # noqa: B008
    project_service: ProjectService = Depends(get_project_service),  # noqa: B008
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
) -> GeneratedEpisodeListResponse:
    """Return one newest-first page of previously generated episode summaries.

    Pass ``project_id`` to scope the page to episodes generated under that
    project; doing so requires a bearer token for that project's owner.
    Omitting ``project_id`` keeps the existing anonymous, unscoped listing.
    """
    if project_id is not None:
        await _authorize_project_access(project_id, current_user, project_service)
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
    current_user: User | None = Depends(get_optional_current_user),  # noqa: B008
    project_service: ProjectService = Depends(get_project_service),  # noqa: B008
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
) -> EpisodeGenerationResponse:
    """Turn a fixed theme id into a full episode script, SEO package, and Shorts cut.

    Passing ``project_id`` requires a bearer token for that project's owner;
    omitting it keeps the existing anonymous generation flow unchanged.
    """
    if payload.project_id is not None:
        await _authorize_project_access(payload.project_id, current_user, project_service)
    try:
        result = await service.generate(payload.theme_id, project_id=payload.project_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return EpisodeGenerationResponse.model_validate(result)


@router.post(
    "/generate-batch",
    response_model=EpisodeBatchGenerateResponse,
    status_code=201,
    summary="Generate every Neşeli Orman theme's episode in one call",
)
async def generate_episodes_batch(
    payload: EpisodeBatchGenerateRequest,
    current_user: User | None = Depends(get_optional_current_user),  # noqa: B008
    project_service: ProjectService = Depends(get_project_service),  # noqa: B008
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
) -> EpisodeBatchGenerateResponse:
    """Generate an episode for every theme, skipping ones the project already has.

    Same visibility rule as ``POST /generate``: passing ``project_id`` requires
    a bearer token for that project's owner. Re-clicking this is safe to
    repeat — themes the project already has a generated episode for are
    reported in ``skipped_theme_ids`` rather than re-generated.
    """
    if payload.project_id is not None:
        await _authorize_project_access(payload.project_id, current_user, project_service)
    result = await service.generate_batch(project_id=payload.project_id)
    created_items = [
        BatchGeneratedEpisodeItem(
            id=detail["id"],
            theme_id=detail["episode"]["theme_id"],
            theme_label=detail["episode"]["theme_label"],
            title=detail["episode"]["title"],
        )
        for detail in result["created"]
    ]
    return EpisodeBatchGenerateResponse(
        project_id=result["project_id"],
        created=created_items,
        skipped_theme_ids=result["skipped_theme_ids"],
    )


@router.get(
    "/export-batch",
    summary="Download every generated episode in one project as one bundled production ZIP",
)
async def export_batch_generated_episodes(
    project_id: uuid.UUID = Query(...),  # noqa: B008
    current_user: User | None = Depends(get_optional_current_user),  # noqa: B008
    project_service: ProjectService = Depends(get_project_service),  # noqa: B008
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
    export_service: EpisodeExportService = Depends(get_episode_export_service),  # noqa: B008
) -> Response:
    """Bundle every episode generated under one project into a single ZIP.

    Requires a bearer token for that project's owner, same rule as ``GET
    /episodes`` scoped by ``project_id`` — there is no anonymous variant,
    since an unbounded "every anonymous episode ever generated" export
    wouldn't be a meaningful or safe thing to hand out. Each episode gets its
    own numbered subfolder, in the same layout ``GET /episodes/{id}/export``
    produces for one episode.
    """
    await _authorize_project_access(project_id, current_user, project_service)
    project = await project_service.get_by_id(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found.")
    episodes = await service.list_all_generated_episodes(project_id=project_id)
    if not episodes:
        raise HTTPException(status_code=404, detail="This project has no generated episodes yet.")
    archive_path = export_service.build_batch(episodes)
    filename = export_service.batch_filename_for(project.name)
    return FileResponse(
        archive_path,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        background=BackgroundTask(archive_path.unlink),
    )


@router.get(
    "/{episode_id}",
    response_model=EpisodeGenerationResponse,
    summary="Get one previously generated episode's full script, SEO, and Shorts package",
)
async def get_generated_episode(
    episode_id: uuid.UUID,
    current_user: User | None = Depends(get_optional_current_user),  # noqa: B008
    project_service: ProjectService = Depends(get_project_service),  # noqa: B008
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
) -> EpisodeGenerationResponse:
    """Return one persisted episode by id, or 404 if it doesn't exist.

    Episodes linked to a project (``project_id`` is not null) are only
    readable by that project's owner; standalone/anonymous episodes are
    unaffected and stay openly readable.
    """
    result = await service.get_generated_episode(episode_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Generated episode not found.")
    if result["project_id"] is not None:
        await _authorize_project_access(result["project_id"], current_user, project_service)
    return EpisodeGenerationResponse.model_validate(result)


@router.get(
    "/{episode_id}/export",
    summary="Download one previously generated episode as a YouTube-ready production ZIP",
)
async def export_generated_episode(
    episode_id: uuid.UUID,
    current_user: User | None = Depends(get_optional_current_user),  # noqa: B008
    project_service: ProjectService = Depends(get_project_service),  # noqa: B008
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
    export_service: EpisodeExportService = Depends(get_episode_export_service),  # noqa: B008
) -> Response:
    """Bundle one persisted episode's script, SEO/Shorts text, and reference media into a ZIP.

    Same visibility rule as ``GET /episodes/{episode_id}``: episodes linked to
    a project are only downloadable by that project's owner (401/403);
    project-less episodes stay openly downloadable.
    """
    result = await service.get_generated_episode(episode_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Generated episode not found.")
    if result["project_id"] is not None:
        await _authorize_project_access(result["project_id"], current_user, project_service)
    archive_bytes = export_service.build(result)
    filename = export_service.filename_for(result["episode"]["title"])
    return Response(
        content=archive_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post(
    "/{episode_id}/render",
    response_model=RenderStartResponse,
    status_code=202,
    summary="Start rendering one generated episode into a narrated MP4",
)
async def render_generated_episode(
    episode_id: uuid.UUID,
    current_user: User | None = Depends(get_optional_current_user),  # noqa: B008
    project_service: ProjectService = Depends(get_project_service),  # noqa: B008
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
    render_service: EpisodeRenderService = Depends(get_episode_render_service),  # noqa: B008
) -> RenderStartResponse:
    """Start a background ffmpeg render and return a render id to poll for progress.

    Same visibility rule as ``export``. Rendering takes on the order of
    minutes, so this always returns immediately with a job id rather than
    the finished video — poll ``.../render/{render_id}/status`` for
    ``completed``/``failed``, then ``.../download``. Only themes with real
    per-scene narration audio already on disk can render; everything else
    returns 409 immediately instead of starting a job that can never
    succeed.
    """
    result = await _get_authorized_episode(episode_id, current_user, project_service, service)
    missing = render_service.missing_audio_message(result)
    if missing is not None:
        raise HTTPException(status_code=409, detail=missing)
    render_id = await render_service.start_render(result)
    return RenderStartResponse(render_id=render_id)


@router.get(
    "/{episode_id}/render/{render_id}/status",
    response_model=RenderStatusResponse,
    summary="Check one render job's status",
)
async def get_render_status(
    episode_id: uuid.UUID,
    render_id: str,
    current_user: User | None = Depends(get_optional_current_user),  # noqa: B008
    project_service: ProjectService = Depends(get_project_service),  # noqa: B008
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
    render_service: EpisodeRenderService = Depends(get_episode_render_service),  # noqa: B008
) -> RenderStatusResponse:
    """Return whether a render job is still pending, has completed, or failed."""
    await _get_authorized_episode(episode_id, current_user, project_service, service)
    status = await render_service.get_status(render_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Render job not found.")
    return RenderStatusResponse(status=status["status"], error=status.get("error"))


@router.get(
    "/{episode_id}/render/{render_id}/download",
    summary="Download one completed render's MP4",
)
async def download_rendered_episode(
    episode_id: uuid.UUID,
    render_id: str,
    current_user: User | None = Depends(get_optional_current_user),  # noqa: B008
    project_service: ProjectService = Depends(get_project_service),  # noqa: B008
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
    export_service: EpisodeExportService = Depends(get_episode_export_service),  # noqa: B008
    render_service: EpisodeRenderService = Depends(get_episode_render_service),  # noqa: B008
) -> Response:
    """Stream a completed render's MP4, then delete its temporary work directory.

    404s for an unknown render id, a job that hasn't completed (or failed)
    yet, or a file that's already been downloaded and cleaned up once.
    """
    result = await _get_authorized_episode(episode_id, current_user, project_service, service)
    status = await render_service.get_status(render_id)
    if status is None or status["status"] != "completed":
        raise HTTPException(status_code=404, detail="Render is not ready or does not exist.")
    file_path = Path(status["filePath"])
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Rendered file is no longer available.")
    filename = export_service.video_filename_for(result["episode"]["title"])
    return FileResponse(
        file_path,
        media_type="video/mp4",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        background=BackgroundTask(shutil.rmtree, file_path.parent, ignore_errors=True),
    )


@router.delete(
    "/{episode_id}",
    status_code=204,
    summary="Delete one previously generated episode",
)
async def delete_generated_episode(
    episode_id: uuid.UUID,
    current_user: User | None = Depends(get_optional_current_user),  # noqa: B008
    project_service: ProjectService = Depends(get_project_service),  # noqa: B008
    service: EpisodeService = Depends(get_episode_service),  # noqa: B008
) -> None:
    """Delete one persisted episode by id, or 404 if it doesn't exist.

    Episodes linked to a project can only be deleted by that project's
    owner; standalone/anonymous episodes stay openly deletable, unchanged.
    """
    result = await service.get_generated_episode(episode_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Generated episode not found.")
    if result["project_id"] is not None:
        await _authorize_project_access(result["project_id"], current_user, project_service)
    deleted = await service.delete_generated_episode(episode_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Generated episode not found.")

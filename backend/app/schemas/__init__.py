"""API request and response schemas."""

from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.schemas.episode import (
    EpisodeGenerateRequest,
    EpisodeGenerationResponse,
    EpisodeResponse,
    GeneratedEpisodeListResponse,
    GeneratedEpisodeSummaryResponse,
    SeoPackageResponse,
    ShortsPlanResponse,
    ThemeSummaryResponse,
)
from app.schemas.project import ProjectCreateRequest, ProjectResponse
from app.schemas.storyboard import StoryboardCreateRequest, StoryboardResponse

__all__ = [
    "EpisodeGenerateRequest",
    "EpisodeGenerationResponse",
    "EpisodeResponse",
    "GeneratedEpisodeListResponse",
    "GeneratedEpisodeSummaryResponse",
    "ProjectCreateRequest",
    "ProjectResponse",
    "SeoPackageResponse",
    "ShortsPlanResponse",
    "StoryboardCreateRequest",
    "StoryboardResponse",
    "ThemeSummaryResponse",
    "TokenResponse",
    "UserLoginRequest",
    "UserRegisterRequest",
    "UserResponse",
]

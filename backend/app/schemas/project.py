"""HTTP contracts for the Sprint 2 project foundation."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreateRequest(BaseModel):
    """Validated input accepted by the project-creation endpoint."""

    name: str = Field(min_length=1, max_length=200)


class ProjectResponse(BaseModel):
    """Transport-safe representation of a project."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    created_at: datetime

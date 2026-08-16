from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Public service status returned by liveness and readiness endpoints."""

    status: Literal["ok"]
    service: str
    version: str
    dependencies: dict[str, bool] | None = Field(default=None)

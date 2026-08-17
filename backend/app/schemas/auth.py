"""HTTP contracts for the Sprint 2 auth foundation."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """Validated input accepted by the registration endpoint."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=200)


class UserLoginRequest(BaseModel):
    """Validated input accepted by the login endpoint."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class UserResponse(BaseModel):
    """Transport-safe representation of a registered user; never includes the hash."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    """A signed access token issued after a successful login."""

    access_token: str
    token_type: str = "bearer"

"""Password hashing and JWT access-token helpers for the Sprint 2 auth foundation."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import Settings

ACCESS_TOKEN_EXPIRE_MINUTES = 60
JWT_ALGORITHM = "HS256"


class InvalidTokenError(Exception):
    """Raised when an access token is missing, malformed, expired, or forged."""


def hash_password(password: str) -> str:
    """Hash a plaintext password for storage."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Check a plaintext password against a previously hashed one."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: uuid.UUID, settings: Settings) -> str:
    """Issue a signed, time-limited access token identifying one user."""
    expires_at = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, settings.app_secret_key.get_secret_value(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str, settings: Settings) -> uuid.UUID:
    """Return the user id carried by a valid access token.

    Raises ``InvalidTokenError`` for anything malformed, expired, or forged, so
    callers have one exception type to translate into an HTTP 401.
    """
    try:
        payload = jwt.decode(
            token, settings.app_secret_key.get_secret_value(), algorithms=[JWT_ALGORITHM]
        )
        return uuid.UUID(str(payload["sub"]))
    except (jwt.PyJWTError, ValueError, KeyError) as error:
        raise InvalidTokenError("Invalid or expired access token.") from error

"""Persisted record of a generated Neşeli Orman episode."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

_JSONVariant = JSON().with_variant(JSONB, "postgresql")


class GeneratedEpisode(Base):
    """One generated episode script plus its SEO and Shorts package.

    Character/location full detail is intentionally not duplicated here: the
    id columns are resolved back through ``ContentBank`` at read time, since
    that fixed registry is the single source of truth for cast/location data.
    """

    __tablename__ = "generated_episodes"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    theme_id: Mapped[str] = mapped_column(Text, nullable=False)
    theme_label: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    lead_character_id: Mapped[str] = mapped_column(Text, nullable=False)
    support_character_id: Mapped[str] = mapped_column(Text, nullable=False)
    location_id: Mapped[str] = mapped_column(Text, nullable=False)
    lesson: Mapped[str] = mapped_column(Text, nullable=False)
    scenes: Mapped[list[dict[str, Any]]] = mapped_column(_JSONVariant, nullable=False)
    seo_package: Mapped[dict[str, Any]] = mapped_column(_JSONVariant, nullable=False)
    shorts_plan: Mapped[dict[str, Any]] = mapped_column(_JSONVariant, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

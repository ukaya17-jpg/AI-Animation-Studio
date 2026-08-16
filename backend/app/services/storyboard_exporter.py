"""Serialization of storyboard aggregates into portable production formats."""

from __future__ import annotations

import json
from dataclasses import asdict
from enum import StrEnum
from typing import Any

from app.models.storyboard import Storyboard


class ExportFormat(StrEnum):
    """Supported export representations."""

    JSON = "json"
    MARKDOWN = "markdown"
    YAML = "yaml"


class StoryboardExporter:
    """Export storyboards without adding a serialization dependency."""

    def export(self, storyboard: Storyboard, format: ExportFormat | str) -> str:
        """Return JSON, Markdown, or YAML for the supplied storyboard."""
        selected = ExportFormat(format.lower())
        if selected is ExportFormat.JSON:
            return json.dumps(asdict(storyboard), ensure_ascii=False, indent=2)
        if selected is ExportFormat.MARKDOWN:
            return self._to_markdown(storyboard)
        return self._to_yaml(asdict(storyboard))

    @staticmethod
    def _to_markdown(storyboard: Storyboard) -> str:
        lines = [
            f"# {storyboard.title}",
            "",
            f"Total duration: {storyboard.total_duration:.3f}s",
            "",
        ]
        for scene in storyboard.scenes:
            lines.extend(
                (
                    f"## {scene.scene_id}: {scene.title}",
                    (
                        f"- Timing: {scene.start_time:.3f}s–{scene.end_time:.3f}s "
                        f"({scene.duration:.3f}s)"
                    ),
                    f"- Camera: {scene.camera.angle} / {scene.camera.movement}",
                    f"- Environment: {scene.environment.location}",
                    f"- Visual: {scene.visual_description}",
                    "",
                )
            )
        return "\n".join(lines)

    @classmethod
    def _to_yaml(cls, value: Any, indent: int = 0) -> str:
        """Serialize the simple dataclass payload safely without PyYAML."""
        prefix = " " * indent
        if isinstance(value, dict):
            lines: list[str] = []
            for key, item in value.items():
                if isinstance(item, (dict, list)):
                    lines.append(f"{prefix}{key}:")
                    lines.append(cls._to_yaml(item, indent + 2))
                else:
                    lines.append(f"{prefix}{key}: {cls._yaml_scalar(item)}")
            return "\n".join(lines)
        if isinstance(value, (list, tuple)):
            if not value:
                return f"{prefix}[]"
            lines = []
            for item in value:
                if isinstance(item, dict):
                    nested = cls._to_yaml(item, indent + 2)
                    first, *rest = nested.splitlines()
                    lines.append(f"{prefix}- {first.strip()}")
                    lines.extend(rest)
                else:
                    lines.append(f"{prefix}- {cls._yaml_scalar(item)}")
            return "\n".join(lines)
        return f"{prefix}{cls._yaml_scalar(value)}"

    @staticmethod
    def _yaml_scalar(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, str):
            return json.dumps(value, ensure_ascii=False)
        return str(value).lower()

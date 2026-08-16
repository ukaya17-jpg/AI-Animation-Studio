import json
import logging
from typing import Any

from app.core.config import Settings
from app.core.request_context import request_id_context


class JsonFormatter(logging.Formatter):
    """Format log records as machine-readable JSON with request correlation."""

    def format(self, record: logging.LogRecord) -> str:
        """Serialize the standard record fields required for operational logs."""
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if request_id := request_id_context.get():
            payload["request_id"] = request_id
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(settings: Settings) -> None:
    """Configure application-wide logging."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=settings.log_level.upper(), handlers=[handler], force=True)

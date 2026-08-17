"""HTTP exception handlers shared by the API."""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def service_unavailable_handler(_: Request, exception: Exception) -> JSONResponse:
    """Expose a safe, actionable response for failed dependency checks."""
    return JSONResponse(status_code=503, content={"detail": str(exception)})


async def unhandled_exception_handler(_: Request, exception: Exception) -> JSONResponse:
    """Log unexpected failures without disclosing internal implementation details."""
    logger.exception("Unhandled API exception", exc_info=exception)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


async def too_many_requests_handler(_: Request, exception: Exception) -> JSONResponse:
    """Expose a safe, actionable response when a client exceeds its rate-limit quota."""
    return JSONResponse(status_code=429, content={"detail": str(exception)})

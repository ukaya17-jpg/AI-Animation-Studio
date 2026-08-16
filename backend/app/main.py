from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.handlers import service_unavailable_handler, unhandled_exception_handler
from app.api.middleware import RequestHandler, add_request_id, enforce_rate_limit
from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import ServiceUnavailableError
from app.core.logging import configure_logging
from app.database.redis import close_redis_client
from app.database.session import close_database

settings = get_settings()
configure_logging(settings)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        await close_database()
        await close_redis_client()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)
if settings.force_https:
    app.add_middleware(HTTPSRedirectMiddleware)
app.add_exception_handler(ServiceUnavailableError, service_unavailable_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.include_router(api_router)


@app.middleware("http")
async def add_security_headers(request: Request, call_next: RequestHandler) -> Response:
    """Add baseline browser security headers to every response."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    if settings.force_https:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


app.middleware("http")(add_request_id)
app.middleware("http")(enforce_rate_limit)

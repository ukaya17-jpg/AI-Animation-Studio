"""Request-scoped context used by logging and HTTP middleware."""

from contextvars import ContextVar, Token

request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str) -> Token[str | None]:
    """Store a request identifier for the duration of a request."""
    return request_id_context.set(request_id)


def reset_request_id(token: Token[str | None]) -> None:
    """Clear the request identifier after a request is complete."""
    request_id_context.reset(token)

"""Application exceptions that have stable HTTP representations."""


class ServiceUnavailableError(Exception):
    """Raised when a required infrastructure dependency cannot serve requests."""

    def __init__(self, message: str = "A required service is unavailable.") -> None:
        super().__init__(message)

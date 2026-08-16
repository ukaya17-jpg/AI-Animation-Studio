import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_settings_reject_default_database_password() -> None:
    with pytest.raises(ValidationError, match="default password"):
        Settings(app_env="production", force_https=True)


def test_production_settings_reject_debug_mode() -> None:
    with pytest.raises(ValidationError, match="DEBUG must be false"):
        Settings(
            app_env="production",
            debug=True,
            database_url="postgresql+asyncpg://app_user:secure@db:5432/app",
        )


def test_production_settings_require_https() -> None:
    with pytest.raises(ValidationError, match="FORCE_HTTPS"):
        Settings(
            app_env="production",
            database_url="postgresql+asyncpg://app_user:secure@db:5432/app",
            app_secret_key="secure-secret",
        )

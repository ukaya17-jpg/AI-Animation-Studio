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


def test_production_settings_reject_default_secret_key() -> None:
    with pytest.raises(ValidationError, match="APP_SECRET_KEY"):
        Settings(
            app_env="production",
            force_https=True,
            database_url="postgresql+asyncpg://app_user:secure@db:5432/app",
            app_secret_key="development-only-secret-change-me",
        )


def test_production_settings_reject_wildcard_cors_origin() -> None:
    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        Settings(
            app_env="production",
            force_https=True,
            database_url="postgresql+asyncpg://app_user:secure@db:5432/app",
            app_secret_key="secure-secret",
            cors_origins="*",
        )


def test_production_settings_reject_wildcard_trusted_host() -> None:
    with pytest.raises(ValidationError, match="TRUSTED_HOSTS must not contain a wildcard"):
        Settings(
            app_env="production",
            force_https=True,
            database_url="postgresql+asyncpg://app_user:secure@db:5432/app",
            app_secret_key="secure-secret",
            trusted_hosts="*",
        )


def test_production_settings_accept_a_fully_hardened_configuration() -> None:
    settings = Settings(
        app_env="production",
        force_https=True,
        database_url="postgresql+asyncpg://app_user:secure@db:5432/app",
        app_secret_key="secure-secret",
        cors_origins="https://app.example.com",
        trusted_hosts="app.example.com",
    )

    assert settings.app_env == "production"


def test_trusted_hosts_rejects_a_blank_value() -> None:
    with pytest.raises(ValidationError, match="TRUSTED_HOSTS must contain at least one host"):
        Settings(trusted_hosts="   ")

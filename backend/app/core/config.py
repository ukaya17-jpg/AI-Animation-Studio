from functools import lru_cache

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Animation Studio API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173"
    trusted_hosts: str = "localhost,127.0.0.1,testserver,backend"
    force_https: bool = False
    app_secret_key: SecretStr = SecretStr("development-only-secret-change-me")
    database_url: str = "postgresql+asyncpg://app_user:change-me@localhost:5432/ai_animation_studio"
    redis_url: str = "redis://localhost:6379/0"
    database_pool_size: int = 5
    database_max_overflow: int = 10

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Prevent known development defaults from being used in production."""
        if self.app_env.lower() != "production":
            return self
        if self.debug:
            raise ValueError("DEBUG must be false when APP_ENV is production.")
        if not self.force_https:
            raise ValueError("FORCE_HTTPS must be true when APP_ENV is production.")
        if "change-me" in self.database_url:
            raise ValueError("DATABASE_URL must not use the default password in production.")
        if "development-only" in self.app_secret_key.get_secret_value():
            raise ValueError("APP_SECRET_KEY must not use the development default in production.")
        if "*" in self.cors_origin_list:
            raise ValueError("CORS_ORIGINS must not contain a wildcard in production.")
        if "*" in self.trusted_host_list:
            raise ValueError("TRUSTED_HOSTS must not contain a wildcard in production.")
        return self

    @field_validator("trusted_hosts")
    @classmethod
    def validate_trusted_hosts(cls, value: str) -> str:
        """Require at least one host to protect against Host-header attacks."""
        if not value.strip():
            raise ValueError("TRUSTED_HOSTS must contain at least one host.")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def trusted_host_list(self) -> list[str]:
        return [host.strip() for host in self.trusted_hosts.split(",") if host.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

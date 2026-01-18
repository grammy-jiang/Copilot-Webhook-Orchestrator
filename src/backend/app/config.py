"""Application configuration using Pydantic Settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Copilot Webhook Orchestrator"
    debug: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = Field(
        default="sqlite:///./orchestrator.db",
        description="Database connection URL",
    )

    # GitHub App
    github_app_id: str = Field(default="", description="GitHub App ID")
    github_client_id: str = Field(default="", description="GitHub OAuth Client ID")
    github_client_secret: str = Field(
        default="", description="GitHub OAuth Client Secret"
    )
    github_webhook_secret: str = Field(
        default="", description="GitHub Webhook Secret for HMAC verification"
    )
    github_private_key: str = Field(
        default="", description="GitHub App Private Key (PEM format)"
    )
    github_app_slug: str = Field(
        default="copilot-workflow-orchestrator",
        description="GitHub App slug for installation URL",
    )

    # Session
    session_secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for session token hashing",
    )
    session_expiry_hours: int = Field(default=24, description="Session expiry in hours")

    # Security
    allowed_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="CORS allowed origins",
    )

    # Frontend
    frontend_url: str = Field(
        default="http://localhost:5173",
        description="Frontend URL for redirects after authentication",
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


def clear_settings_cache() -> None:
    """Clear the settings cache. Useful for testing."""
    get_settings.cache_clear()

"""Pydantic schemas for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


# Health schemas
class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Service health status")
    version: str = Field(description="Application version")
    timestamp: datetime = Field(description="Current server time")


# Auth schemas
class UserResponse(BaseModel):
    """User response schema."""

    id: int
    github_id: int
    github_login: str
    github_name: str | None
    github_email: str | None
    github_avatar_url: str | None
    last_login_at: datetime | None
    created_at: datetime


class SessionResponse(BaseModel):
    """Session creation response."""

    token: str = Field(description="Session token for authentication")
    expires_at: datetime = Field(description="Token expiration time")
    user: UserResponse


class AuthErrorResponse(BaseModel):
    """Authentication error response."""

    error: str
    error_description: str | None = None


# Installation schemas
class InstallationResponse(BaseModel):
    """Installation response schema."""

    id: int
    github_installation_id: int
    account_type: str
    account_login: str
    status: str
    created_at: datetime


class InstallationListResponse(BaseModel):
    """List of installations response."""

    installations: list[InstallationResponse]
    total: int


# Repository schemas
class RepositoryResponse(BaseModel):
    """Repository response schema."""

    id: int
    github_repo_id: int
    installation_id: int
    full_name: str
    owner: str
    name: str
    private: bool
    default_branch: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_event_at: datetime | None = None


class RepositoryListResponse(BaseModel):
    """Paginated list of repositories response."""

    items: list[RepositoryResponse]
    total: int
    page: int
    per_page: int
    pages: int


# Event schemas
class EventResponse(BaseModel):
    """Event response schema."""

    id: int
    delivery_id: str
    event_type: str
    action: str | None
    repository_id: int | None
    processed: bool
    created_at: datetime


class EventListResponse(BaseModel):
    """Paginated list of events response."""

    events: list[EventResponse]
    total: int
    limit: int
    offset: int


class EventQueryParams(BaseModel):
    """Query parameters for event listing."""

    event_type: str | None = None
    repository_id: int | None = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


# Webhook schemas
class WebhookResponse(BaseModel):
    """Webhook processing response."""

    status: str = Field(description="Processing status")
    delivery_id: str = Field(description="GitHub delivery ID")
    event_type: str = Field(description="Event type")


class WebhookErrorResponse(BaseModel):
    """Webhook error response."""

    error: str
    delivery_id: str | None = None

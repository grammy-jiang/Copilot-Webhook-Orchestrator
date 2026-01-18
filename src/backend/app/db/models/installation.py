"""Installation model for GitHub App installations."""

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.db.models.base import TimestampMixin


class Installation(SQLModel, TimestampMixin, table=True):
    """Installation model for GitHub App installations."""

    __tablename__ = "installations"

    id: int | None = Field(default=None, primary_key=True)
    github_installation_id: int = Field(
        unique=True, index=True, description="GitHub App installation ID"
    )
    user_id: int = Field(foreign_key="users.id", index=True)
    account_type: str = Field(description="Account type: 'User' or 'Organization'")
    account_login: str = Field(description="GitHub account login name")
    account_id: int = Field(description="GitHub account ID")
    target_type: str = Field(
        default="all", description="Target type: 'all' or 'selected'"
    )
    permissions: str = Field(
        default="{}", description="JSON string of granted permissions"
    )
    events: str = Field(default="[]", description="JSON string of subscribed events")
    status: str = Field(
        default="active", description="Installation status: active, suspended, deleted"
    )
    suspended_at: datetime | None = Field(
        default=None, description="Timestamp when installation was suspended"
    )
    suspended_by: str | None = Field(
        default=None, description="Who suspended the installation"
    )

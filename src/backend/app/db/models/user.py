"""User model for GitHub OAuth users."""

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.db.models.base import TimestampMixin


class User(SQLModel, TimestampMixin, table=True):
    """User model representing a GitHub user who has authenticated."""

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    github_id: int = Field(unique=True, index=True, description="GitHub user ID")
    github_login: str = Field(index=True, description="GitHub username")
    github_name: str | None = Field(default=None, description="GitHub display name")
    github_email: str | None = Field(default=None, description="GitHub email")
    github_avatar_url: str | None = Field(default=None, description="GitHub avatar URL")
    access_token_hash: str = Field(description="Hashed GitHub access token")
    last_login_at: datetime | None = Field(
        default=None, description="Last login timestamp"
    )

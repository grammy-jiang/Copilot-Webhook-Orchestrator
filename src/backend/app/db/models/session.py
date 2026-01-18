"""Session model for user authentication sessions."""

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.db.models.base import TimestampMixin


class Session(SQLModel, TimestampMixin, table=True):
    """Session model for tracking authenticated user sessions."""

    __tablename__ = "sessions"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    token_hash: str = Field(unique=True, index=True, description="Hashed session token")
    expires_at: datetime = Field(description="Session expiration timestamp")
    user_agent: str | None = Field(default=None, description="Client user agent")
    ip_address: str | None = Field(default=None, description="Client IP address")
    is_active: bool = Field(default=True, description="Whether session is active")

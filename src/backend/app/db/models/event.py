"""Event model for storing webhook events."""

from datetime import datetime

from sqlmodel import Field, SQLModel

from app.db.models.base import TimestampMixin


class Event(SQLModel, TimestampMixin, table=True):
    """Event model for storing GitHub webhook events."""

    __tablename__ = "events"

    id: int | None = Field(default=None, primary_key=True)
    delivery_id: str = Field(
        unique=True, index=True, description="GitHub delivery ID (X-GitHub-Delivery)"
    )
    event_type: str = Field(index=True, description="GitHub event type")
    action: str | None = Field(default=None, description="Event action (if applicable)")
    repository_id: int | None = Field(
        default=None, foreign_key="repositories.id", index=True
    )
    installation_id: int | None = Field(
        default=None, foreign_key="installations.id", index=True
    )
    user_id: int | None = Field(default=None, foreign_key="users.id", index=True)
    payload: str = Field(description="JSON string of the webhook payload")
    processed: bool = Field(
        default=False, description="Whether event has been processed"
    )
    processed_at: datetime | None = Field(
        default=None, description="When the event was processed"
    )
    error: str | None = Field(
        default=None, description="Error message if processing failed"
    )

"""Base model mixin with timestamp fields."""

from datetime import UTC, datetime

from sqlmodel import Field


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp when the record was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column_kwargs={"onupdate": lambda: datetime.now(UTC)},
        description="Timestamp when the record was last updated",
    )

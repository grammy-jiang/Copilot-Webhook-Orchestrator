# Phase 1 Data Model — SQLModel Entities

**Agent:** @arch-spec-author

**Date:** January 18, 2026

______________________________________________________________________

## Overview

This document defines the SQLModel entities for Phase 1 of the Copilot Workflow
Orchestrator. All models are designed to work with both SQLite (development) and
PostgreSQL (production).

______________________________________________________________________

## 1. User

Represents an authenticated user (via GitHub OAuth).

```python
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    """GitHub-authenticated user."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    github_id: int = Field(unique=True, index=True)
    username: str = Field(max_length=255, index=True)
    email: Optional[str] = Field(default=None, max_length=255)
    avatar_url: Optional[str] = Field(default=None, max_length=512)
    access_token: Optional[str] = Field(default=None, max_length=255)
    access_token_expires_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    sessions: list["UserSession"] = Relationship(back_populates="user")
    installations: list["Installation"] = Relationship(back_populates="user")
```

### Indexes

- `github_id` (unique) — lookup by GitHub user ID
- `username` — display and search

### Notes

- `access_token` is encrypted at rest (application-level encryption)
- `access_token_expires_at` is nullable (GitHub OAuth tokens are long-lived)

______________________________________________________________________

## 2. UserSession

Tracks active user sessions for authentication.

```python
class UserSession(SQLModel, table=True):
    """User authentication session."""

    __tablename__ = "user_sessions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    session_token: str = Field(max_length=255, unique=True, index=True)
    expires_at: datetime = Field(index=True)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = Field(default=None, max_length=45)  # IPv6
    user_agent: Optional[str] = Field(default=None, max_length=512)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="sessions")
```

### Indexes

- `session_token` (unique) — session lookup
- `user_id` — find all sessions for a user
- `expires_at` — cleanup expired sessions

### Notes

- `session_token` is hashed (bcrypt or SHA-256)
- Session expiry: 30 days (configurable)
- Sliding expiration: update `last_activity_at` on each request

______________________________________________________________________

## 3. Installation

Represents a GitHub App installation (per user in Phase 1).

```python
from typing import Any


class Installation(SQLModel, table=True):
    """GitHub App installation."""

    __tablename__ = "installations"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    installation_id: int = Field(unique=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    account_login: str = Field(max_length=255)
    account_type: str = Field(max_length=50)  # "User" or "Organization"
    target_type: str = Field(max_length=50)  # "User" or "Organization"
    permissions: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    events: list[str] = Field(default_factory=list, sa_type=JSON)
    is_suspended: bool = Field(default=False)
    suspended_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="installations")
    installation_repositories: list["InstallationRepository"] = Relationship(
        back_populates="installation"
    )
```

### Indexes

- `installation_id` (unique) — lookup by GitHub installation ID
- `user_id` — find installations for a user

### Notes

- Phase 1: Single installation per user
- `permissions` stores the granted GitHub App permissions snapshot
- `events` stores the subscribed webhook event types

______________________________________________________________________

## 4. Repository

Represents a GitHub repository accessible via an installation.

```python
class Repository(SQLModel, table=True):
    """GitHub repository."""

    __tablename__ = "repositories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    github_id: int = Field(unique=True, index=True)
    owner: str = Field(max_length=255, index=True)
    name: str = Field(max_length=255)
    full_name: str = Field(max_length=512, index=True)
    description: Optional[str] = Field(default=None, max_length=1024)
    url: str = Field(max_length=512)
    is_private: bool = Field(default=False)
    default_branch: str = Field(default="main", max_length=255)
    last_event_at: Optional[datetime] = Field(default=None, index=True)
    event_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    installation_repositories: list["InstallationRepository"] = Relationship(
        back_populates="repository"
    )
    events: list["EventReceipt"] = Relationship(back_populates="repository")
```

### Indexes

- `github_id` (unique) — lookup by GitHub repo ID
- `full_name` — search by owner/repo
- `owner` — filter by owner
- `last_event_at` — health indicators

### Notes

- `event_count` is a cached counter (updated on event insert)
- `last_event_at` is updated on each new event

______________________________________________________________________

## 5. InstallationRepository

Junction table linking installations to repositories.

```python
class InstallationRepository(SQLModel, table=True):
    """Links installations to repositories (many-to-many)."""

    __tablename__ = "installation_repositories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    installation_id: UUID = Field(foreign_key="installations.id", index=True)
    repository_id: UUID = Field(foreign_key="repositories.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    installation: Installation = Relationship(
        back_populates="installation_repositories"
    )
    repository: Repository = Relationship(
        back_populates="installation_repositories"
    )

    class Config:
        # Unique constraint on (installation_id, repository_id)
        table_args = (
            UniqueConstraint("installation_id", "repository_id"),
        )
```

### Indexes

- `installation_id` — find repos for an installation
- `repository_id` — find installations for a repo
- Composite unique constraint on `(installation_id, repository_id)`

______________________________________________________________________

## 6. EventReceipt

Stores received GitHub webhook events.

```python
from enum import Enum


class ProcessingStatus(str, Enum):
    """Event processing status."""

    RECEIVED = "received"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class EventReceipt(SQLModel, table=True):
    """GitHub webhook event record."""

    __tablename__ = "event_receipts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    delivery_id: str = Field(max_length=255, unique=True, index=True)
    installation_id: UUID = Field(foreign_key="installations.id", index=True)
    repository_id: UUID = Field(foreign_key="repositories.id", index=True)
    event_type: str = Field(max_length=100, index=True)
    event_action: Optional[str] = Field(default=None, max_length=100, index=True)
    actor: Optional[str] = Field(default=None, max_length=255)
    target_object_ids: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    received_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    github_timestamp: Optional[datetime] = Field(default=None)
    raw_payload: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    payload_storage: Optional[str] = Field(default=None, max_length=512)
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.RECEIVED)
    error_message: Optional[str] = Field(default=None)
    retry_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    repository: Repository = Relationship(back_populates="events")
```

### Indexes

- `delivery_id` (unique) — deduplication
- `repository_id` — filter events by repo
- `installation_id` — filter events by installation
- `event_type` — filter by event type
- `event_action` — filter by action
- `received_at` — time-range queries (newest first)

### Partitioning Strategy (PostgreSQL)

For production with high event volume, consider:

```sql
-- Partition by month
CREATE TABLE event_receipts (
    ...
) PARTITION BY RANGE (received_at);

CREATE TABLE event_receipts_2026_01 PARTITION OF event_receipts
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

### Notes

- `raw_payload` stores the full webhook JSON (JSONB in PostgreSQL)
- `payload_storage` is for external storage URL if payload > 1MB
- `target_object_ids` example: `{"issue_number": 5, "pr_number": 10}`

______________________________________________________________________

## 7. Database Configuration

### Development (SQLite)

```python
DATABASE_URL = "sqlite:///./dev.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True,  # SQL logging
)
```

### Production (PostgreSQL)

```python
DATABASE_URL = "postgresql://user:pass@localhost:5432/orchestrator"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=False,
)
```

### Migrations (Alembic)

```bash
# Initialize Alembic
alembic init migrations

# Generate migration
alembic revision --autogenerate -m "Initial Phase 1 schema"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

______________________________________________________________________

## 8. Model Relationships Summary

```
User (1) ──────< (N) UserSession
  │
  └──< (1) Installation (Phase 1: 1 per user)
              │
              └──< (N) InstallationRepository >──(1) Repository
                                                      │
                                                      └──< (N) EventReceipt
```

______________________________________________________________________

## 9. Pydantic Schemas (API Layer)

SQLModel models can be used directly as Pydantic schemas, but we also define
explicit read/create schemas for API clarity:

```python
class UserRead(SQLModel):
    """User response schema."""

    id: UUID
    github_id: int
    username: str
    email: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime


class RepositoryRead(SQLModel):
    """Repository response schema."""

    id: UUID
    github_id: int
    owner: str
    name: str
    full_name: str
    description: Optional[str]
    is_private: bool
    last_event_at: Optional[datetime]
    event_count: int


class EventReceiptRead(SQLModel):
    """Event response schema."""

    id: UUID
    delivery_id: str
    event_type: str
    event_action: Optional[str]
    actor: Optional[str]
    target_object_ids: dict[str, Any]
    received_at: datetime
    github_timestamp: Optional[datetime]
    processing_status: ProcessingStatus


class EventReceiptDetail(EventReceiptRead):
    """Event detail with raw payload."""

    raw_payload: dict[str, Any]
```

______________________________________________________________________

**Document generated by:** @arch-spec-author agent

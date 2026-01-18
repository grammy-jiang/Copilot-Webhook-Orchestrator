"""Pytest configuration and shared fixtures for all tests."""

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# These imports will fail until implementation exists (TDD Red phase)
# from copilot_orchestrator.app import create_app
# from copilot_orchestrator.db import get_session
# from copilot_orchestrator.models import User, UserSession, Installation


# =============================================================================
# Database Fixtures
# =============================================================================


@pytest.fixture(name="engine")
def fixture_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def fixture_session(engine):
    """Create a database session for testing."""
    with Session(engine) as session:
        yield session


# =============================================================================
# Application Fixtures
# =============================================================================


@pytest.fixture(name="app")
def fixture_app(session):
    """Create a test FastAPI application with test database.

    This fixture will fail until the app is implemented (TDD Red phase).
    """
    # TODO: Uncomment when app is implemented
    # from copilot_orchestrator.app import create_app
    # from copilot_orchestrator.db import get_session
    #
    # app = create_app()
    #
    # def get_session_override():
    #     return session
    #
    # app.dependency_overrides[get_session] = get_session_override
    # return app
    pytest.skip("App not implemented yet (TDD Red phase)")


@pytest.fixture(name="client")
async def fixture_client(app) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing API endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client


# =============================================================================
# User & Session Fixtures
# =============================================================================


@pytest.fixture(name="test_user_data")
def fixture_test_user_data() -> dict[str, Any]:
    """Test user data matching GitHub OAuth response."""
    return {
        "id": uuid4(),
        "github_id": 12345678,
        "username": "testuser",
        "email": "testuser@example.com",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


@pytest.fixture(name="test_session_data")
def fixture_test_session_data(test_user_data) -> dict[str, Any]:
    """Test session data for authenticated requests."""
    return {
        "id": uuid4(),
        "user_id": test_user_data["id"],
        "session_token": "test_session_token_abc123",
        "expires_at": datetime.now(UTC) + timedelta(days=30),
        "last_activity_at": datetime.now(UTC),
        "ip_address": "127.0.0.1",
        "user_agent": "pytest-test-client",
        "created_at": datetime.now(UTC),
    }


@pytest.fixture(name="expired_session_data")
def fixture_expired_session_data(test_user_data) -> dict[str, Any]:
    """Expired session data for testing session expiration."""
    return {
        "id": uuid4(),
        "user_id": test_user_data["id"],
        "session_token": "expired_session_token_xyz789",
        "expires_at": datetime.now(UTC) - timedelta(days=1),  # Expired
        "last_activity_at": datetime.now(UTC) - timedelta(days=31),
        "ip_address": "127.0.0.1",
        "user_agent": "pytest-test-client",
        "created_at": datetime.now(UTC) - timedelta(days=31),
    }


# =============================================================================
# Installation Fixtures
# =============================================================================


@pytest.fixture(name="test_installation_data")
def fixture_test_installation_data(test_user_data) -> dict[str, Any]:
    """Test installation data for GitHub App."""
    return {
        "id": uuid4(),
        "installation_id": 12345,
        "user_id": test_user_data["id"],
        "account_login": "testuser",
        "account_type": "User",
        "target_type": "User",
        "permissions": {
            "issues": "write",
            "pull_requests": "write",
            "contents": "read",
        },
        "events": ["issues", "pull_request", "push"],
        "is_suspended": False,
        "suspended_at": None,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


# =============================================================================
# Repository Fixtures
# =============================================================================


@pytest.fixture(name="test_repository_data")
def fixture_test_repository_data() -> dict[str, Any]:
    """Test repository data."""
    return {
        "id": uuid4(),
        "github_id": 123456789,
        "owner": "testuser",
        "name": "test-repo",
        "full_name": "testuser/test-repo",
        "description": "A test repository",
        "url": "https://github.com/testuser/test-repo",
        "is_private": False,
        "default_branch": "main",
        "last_event_at": None,
        "event_count": 0,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


# =============================================================================
# Webhook Fixtures
# =============================================================================


@pytest.fixture(name="valid_webhook_payload")
def fixture_valid_webhook_payload() -> dict[str, Any]:
    """Valid GitHub webhook payload (pull_request opened)."""
    return {
        "action": "opened",
        "number": 42,
        "pull_request": {
            "id": 987654321,
            "number": 42,
            "title": "Add new feature",
            "user": {"login": "testuser", "id": 12345678},
            "head": {"ref": "feature-branch", "sha": "abc123"},
            "base": {"ref": "main", "sha": "def456"},
            "created_at": "2026-01-18T10:00:00Z",
            "updated_at": "2026-01-18T10:00:00Z",
        },
        "repository": {
            "id": 123456789,
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "owner": {"login": "testuser"},
        },
        "sender": {"login": "testuser", "id": 12345678},
        "installation": {"id": 12345},
    }


@pytest.fixture(name="webhook_secret")
def fixture_webhook_secret() -> str:
    """Test webhook secret for HMAC verification."""
    return "test_webhook_secret_for_hmac_verification"


@pytest.fixture(name="valid_webhook_signature")
def fixture_valid_webhook_signature(
    valid_webhook_payload: dict[str, Any],
    webhook_secret: str,
) -> str:
    """Generate a valid HMAC-SHA256 signature for webhook testing."""
    import hashlib
    import hmac
    import json

    payload_bytes = json.dumps(valid_webhook_payload, separators=(",", ":")).encode()
    signature = hmac.new(
        webhook_secret.encode(),
        payload_bytes,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={signature}"


@pytest.fixture(name="invalid_webhook_signature")
def fixture_invalid_webhook_signature() -> str:
    """Invalid HMAC signature for testing rejection."""
    return "sha256=invalid_signature_that_should_be_rejected"


# =============================================================================
# Event Fixtures
# =============================================================================


@pytest.fixture(name="test_event_data")
def fixture_test_event_data(
    test_installation_data,
    test_repository_data,
) -> dict[str, Any]:
    """Test event data for storage tests."""
    return {
        "id": uuid4(),
        "delivery_id": "abc123-def456-ghi789",
        "installation_id": test_installation_data["id"],
        "repository_id": test_repository_data["id"],
        "event_type": "pull_request",
        "event_action": "opened",
        "actor": "testuser",
        "target_object_ids": {"pr_number": 42},
        "received_at": datetime.now(UTC),
        "github_timestamp": datetime.now(UTC) - timedelta(seconds=2),
        "raw_payload": {"action": "opened", "number": 42},
        "payload_storage": None,
        "processing_status": "received",
        "error_message": None,
        "retry_count": 0,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


# =============================================================================
# Mock Fixtures
# =============================================================================


@pytest.fixture(name="mock_github_oauth")
def fixture_mock_github_oauth() -> AsyncMock:
    """Mock GitHub OAuth API responses."""
    mock = AsyncMock()
    mock.exchange_code_for_token.return_value = {
        "access_token": "gho_test_access_token",
        "token_type": "bearer",
        "scope": "user:email,read:user",
    }
    mock.get_user.return_value = {
        "id": 12345678,
        "login": "testuser",
        "email": "testuser@example.com",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
    }
    return mock


@pytest.fixture(name="mock_github_api")
def fixture_mock_github_api() -> AsyncMock:
    """Mock GitHub API for installation and repository operations."""
    mock = AsyncMock()
    mock.get_installation_repositories.return_value = {
        "total_count": 2,
        "repositories": [
            {
                "id": 123456789,
                "name": "test-repo",
                "full_name": "testuser/test-repo",
                "description": "A test repository",
                "private": False,
                "default_branch": "main",
            },
            {
                "id": 987654321,
                "name": "another-repo",
                "full_name": "testuser/another-repo",
                "description": "Another test repository",
                "private": True,
                "default_branch": "main",
            },
        ],
    }
    return mock


# =============================================================================
# Time Fixtures
# =============================================================================


@pytest.fixture(name="frozen_time")
def fixture_frozen_time():
    """Freeze time for deterministic testing.

    Usage:
        def test_something(frozen_time):
            # All datetime.now() calls return 2026-01-18T12:00:00Z
            ...
    """
    # TODO: Use freezegun or similar when implemented
    return datetime(2026, 1, 18, 12, 0, 0, tzinfo=UTC)

"""Pytest configuration and shared fixtures for all tests."""

import hashlib
import hmac
import json
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db.engine import get_session
from app.db.models.event import Event
from app.db.models.installation import Installation
from app.db.models.repository import Repository
from app.db.models.session import Session as UserSession
from app.db.models.user import User
from app.main import create_app
from app.services.crypto import generate_session_token, hash_token

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
def fixture_app(engine, webhook_secret):
    """Create a test FastAPI application with test database."""
    from app.config import Settings, get_settings

    app = create_app()

    # Create test settings with webhook secret
    test_settings = Settings(
        github_webhook_secret=webhook_secret,
        database_url="sqlite://",
    )

    def get_session_override():
        with Session(engine) as session:
            yield session

    def get_settings_override() -> Settings:
        return test_settings

    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_settings] = get_settings_override
    return app


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


@pytest.fixture(name="test_user")
def fixture_test_user(session) -> User:
    """Create a test user in the database."""
    user = User(
        github_id=12345678,
        github_login="testuser",
        github_name="Test User",
        github_email="testuser@example.com",
        github_avatar_url="https://avatars.githubusercontent.com/u/12345678",
        access_token_hash=hash_token("gho_test_access_token"),
        last_login_at=datetime.now(UTC),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_user_data")
def fixture_test_user_data() -> dict[str, Any]:
    """Test user data matching GitHub OAuth response."""
    return {
        "github_id": 12345678,
        "github_login": "testuser",
        "github_name": "Test User",
        "github_email": "testuser@example.com",
        "github_avatar_url": "https://avatars.githubusercontent.com/u/12345678",
    }


@pytest.fixture(name="test_session_token")
def fixture_test_session_token() -> str:
    """Generate a test session token."""
    return generate_session_token()


@pytest.fixture(name="test_session")
def fixture_test_session(
    session, test_user, test_session_token
) -> tuple[UserSession, str]:
    """Create a test session in the database. Returns (session, raw_token)."""
    user_session = UserSession(
        user_id=test_user.id,
        token_hash=hash_token(test_session_token),
        expires_at=datetime.now(UTC) + timedelta(hours=24),
        user_agent="pytest-test-client",
        ip_address="127.0.0.1",
    )
    session.add(user_session)
    session.commit()
    session.refresh(user_session)
    return user_session, test_session_token


@pytest.fixture(name="authenticated_client")
async def fixture_authenticated_client(
    app, test_session
) -> AsyncGenerator[AsyncClient, None]:
    """Create an authenticated HTTP client with session cookie."""
    _, token = test_session
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies={"session_token": token},
    ) as client:
        yield client


@pytest.fixture(name="expired_session")
def fixture_expired_session(session, test_user) -> tuple[UserSession, str]:
    """Create an expired session in the database."""
    token = generate_session_token()
    user_session = UserSession(
        user_id=test_user.id,
        token_hash=hash_token(token),
        expires_at=datetime.now(UTC) - timedelta(hours=1),  # Expired
        user_agent="pytest-test-client",
        ip_address="127.0.0.1",
    )
    session.add(user_session)
    session.commit()
    session.refresh(user_session)
    return user_session, token


# =============================================================================
# Installation Fixtures
# =============================================================================


@pytest.fixture(name="test_installation")
def fixture_test_installation(session, test_user) -> Installation:
    """Create a test installation in the database."""
    installation = Installation(
        github_installation_id=12345,
        user_id=test_user.id,
        account_type="User",
        account_login="testuser",
        account_id=12345678,
        target_type="all",
        permissions=json.dumps({"issues": "write", "pull_requests": "write"}),
        events=json.dumps(["issues", "pull_request", "push"]),
        status="active",
    )
    session.add(installation)
    session.commit()
    session.refresh(installation)
    return installation


@pytest.fixture(name="test_installation_data")
def fixture_test_installation_data(test_user) -> dict[str, Any]:
    """Test installation data for GitHub App."""
    return {
        "github_installation_id": 12345,
        "user_id": test_user.id if hasattr(test_user, "id") else 1,
        "account_type": "User",
        "account_login": "testuser",
        "account_id": 12345678,
        "target_type": "all",
        "permissions": {"issues": "write", "pull_requests": "write"},
        "events": ["issues", "pull_request", "push"],
    }


# =============================================================================
# Repository Fixtures
# =============================================================================


@pytest.fixture(name="test_repository")
def fixture_test_repository(session, test_installation) -> Repository:
    """Create a test repository in the database."""
    repo = Repository(
        github_repo_id=123456789,
        installation_id=test_installation.id,
        full_name="testuser/test-repo",
        owner="testuser",
        name="test-repo",
        private=False,
        default_branch="main",
    )
    session.add(repo)
    session.commit()
    session.refresh(repo)
    return repo


@pytest.fixture(name="test_repository_data")
def fixture_test_repository_data() -> dict[str, Any]:
    """Test repository data."""
    return {
        "github_repo_id": 123456789,
        "full_name": "testuser/test-repo",
        "owner": "testuser",
        "name": "test-repo",
        "private": False,
        "default_branch": "main",
    }


# =============================================================================
# Event Fixtures
# =============================================================================


@pytest.fixture(name="test_event")
def fixture_test_event(session, test_installation, test_repository, test_user) -> Event:
    """Create a test event in the database."""
    event = Event(
        delivery_id="abc123-def456-ghi789",
        event_type="pull_request",
        action="opened",
        repository_id=test_repository.id,
        installation_id=test_installation.id,
        user_id=test_user.id,
        payload=json.dumps({"action": "opened", "number": 42}),
        processed=False,
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


@pytest.fixture(name="test_event_data")
def fixture_test_event_data() -> dict[str, Any]:
    """Test event data for storage tests."""
    return {
        "delivery_id": "abc123-def456-ghi789",
        "event_type": "pull_request",
        "action": "opened",
        "payload": {"action": "opened", "number": 42},
    }


# =============================================================================
# Webhook Fixtures
# =============================================================================


@pytest.fixture(name="webhook_secret")
def fixture_webhook_secret() -> str:
    """Test webhook secret for HMAC verification."""
    return "test_webhook_secret_for_hmac_verification"


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


@pytest.fixture(name="valid_webhook_signature")
def fixture_valid_webhook_signature(
    valid_webhook_payload: dict[str, Any],
    webhook_secret: str,
) -> str:
    """Generate a valid HMAC-SHA256 signature for webhook testing."""
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
    """Freeze time for deterministic testing."""
    return datetime(2026, 1, 18, 12, 0, 0, tzinfo=UTC)

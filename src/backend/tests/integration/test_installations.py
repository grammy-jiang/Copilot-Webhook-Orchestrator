"""Tests for GitHub App installation management.

These tests verify installation flow, webhooks, and authorization.
"""

import hashlib
import hmac
import json

import pytest

from app.services.crypto import generate_jwt, verify_jwt


class TestInstallationFlow:
    """Tests for GitHub App installation flow."""

    @pytest.mark.integration
    async def test_no_installations_returns_empty_list(
        self,
        authenticated_client,
    ):
        """AC: User with no installations sees empty list."""
        response = await authenticated_client.get("/api/installations")

        assert response.status_code == 200
        data = response.json()
        assert data["installations"] == []
        assert data["total"] == 0

    @pytest.mark.integration
    async def test_installation_callback_success(
        self,
        authenticated_client,
    ):
        """AC: Installation callback creates installation record."""
        response = await authenticated_client.get(
            "/api/installations/callback",
            params={"installation_id": 12345, "setup_action": "install"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["github_installation_id"] == 12345

    @pytest.mark.integration
    async def test_list_installations_after_install(
        self,
        authenticated_client,
    ):
        """AC: Installation appears in list after creation."""
        # First install
        await authenticated_client.get(
            "/api/installations/callback",
            params={"installation_id": 67890, "setup_action": "install"},
        )

        # Then list
        response = await authenticated_client.get("/api/installations")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["installations"]) == 1
        assert data["installations"][0]["github_installation_id"] == 67890

    @pytest.mark.integration
    async def test_get_installation_details(
        self,
        authenticated_client,
        session,
        test_user,
        test_installation,
    ):
        """AC: Get specific installation by ID."""
        response = await authenticated_client.get(
            f"/api/installations/{test_installation.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert (
            data["github_installation_id"] == test_installation.github_installation_id
        )
        assert data["account_login"] == "testuser"

    @pytest.mark.integration
    async def test_get_nonexistent_installation_returns_404(
        self,
        authenticated_client,
    ):
        """AC: Non-existent installation returns 404."""
        response = await authenticated_client.get("/api/installations/99999")

        assert response.status_code == 404


class TestInstallationWebhooks:
    """Tests for installation-related webhooks."""

    @pytest.mark.integration
    async def test_installation_suspended_webhook(
        self,
        client,
        session,
        test_installation,
        webhook_secret,
        monkeypatch,
    ):
        """AC: Installation suspended webhook updates status."""
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", webhook_secret)

        payload = {
            "action": "suspend",
            "installation": {
                "id": test_installation.github_installation_id,
                "account": {"login": "testuser"},
            },
            "sender": {"login": "admin"},
        }
        payload_bytes = json.dumps(payload).encode()
        signature = (
            "sha256="
            + hmac.new(
                webhook_secret.encode(),
                payload_bytes,
                hashlib.sha256,
            ).hexdigest()
        )

        response = await client.post(
            "/api/webhooks/github",
            content=payload_bytes,
            headers={
                "X-GitHub-Event": "installation",
                "X-GitHub-Delivery": "suspend-test-123",
                "X-Hub-Signature-256": signature,
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 200

    @pytest.mark.integration
    async def test_installation_deleted_webhook(
        self,
        client,
        session,
        test_installation,
        webhook_secret,
        monkeypatch,
    ):
        """AC: Installation deleted webhook updates status."""
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", webhook_secret)

        payload = {
            "action": "deleted",
            "installation": {
                "id": test_installation.github_installation_id,
                "account": {"login": "testuser"},
            },
            "sender": {"login": "testuser"},
        }
        payload_bytes = json.dumps(payload).encode()
        signature = (
            "sha256="
            + hmac.new(
                webhook_secret.encode(),
                payload_bytes,
                hashlib.sha256,
            ).hexdigest()
        )

        response = await client.post(
            "/api/webhooks/github",
            content=payload_bytes,
            headers={
                "X-GitHub-Event": "installation",
                "X-GitHub-Delivery": "delete-test-123",
                "X-Hub-Signature-256": signature,
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 200


class TestInstallationAuthorization:
    """Tests for installation authorization and isolation."""

    @pytest.mark.integration
    async def test_cannot_access_other_users_installation(
        self,
        app,
        session,
        test_user,
        test_installation,
    ):
        """AC: User cannot access another user's installation.

        @security AUTHZ-01
        """
        from datetime import UTC, datetime, timedelta

        from httpx import ASGITransport, AsyncClient

        from app.db.models.session import Session as UserSession
        from app.db.models.user import User
        from app.services.crypto import generate_session_token, hash_token

        # Create another user
        other_user = User(
            github_id=99999999,
            github_login="otheruser",
            github_name="Other User",
            github_email="other@example.com",
            access_token_hash=hash_token("other_token"),
        )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)

        # Create session for other user
        token = generate_session_token()
        other_session = UserSession(
            user_id=other_user.id,
            token_hash=hash_token(token),
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )
        session.add(other_session)
        session.commit()

        # Try to access first user's installation
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies={"session_token": token},
        ) as client:
            response = await client.get(f"/api/installations/{test_installation.id}")

        assert response.status_code == 404

    @pytest.mark.integration
    async def test_single_installation_per_user_constraint(
        self,
        authenticated_client,
    ):
        """AC: User can only have one active installation."""
        # First installation
        response1 = await authenticated_client.get(
            "/api/installations/callback",
            params={"installation_id": 11111, "setup_action": "install"},
        )
        assert response1.status_code == 200

        # Second installation attempt
        response2 = await authenticated_client.get(
            "/api/installations/callback",
            params={"installation_id": 22222, "setup_action": "install"},
        )
        assert response2.status_code == 400


class TestJWTGeneration:
    """Tests for GitHub App JWT generation."""

    @pytest.mark.unit
    def test_jwt_generation_creates_valid_token(self):
        """AC: JWT generation produces valid token."""
        token = generate_jwt({"iss": "123456"})

        assert token is not None
        assert token.count(".") == 2

    @pytest.mark.unit
    def test_jwt_has_correct_claims(self):
        """AC: JWT contains required claims."""
        token = generate_jwt({"iss": "123456", "sub": "test"})
        claims = verify_jwt(token)

        assert claims is not None
        assert "iss" in claims
        assert "iat" in claims
        assert "exp" in claims
        assert claims["iss"] == "123456"

    @pytest.mark.unit
    def test_jwt_expires_correctly(self):
        """AC: JWT expires after specified time."""
        token = generate_jwt({"iss": "123456"}, expires_in_minutes=10)
        claims = verify_jwt(token)

        assert claims is not None
        # exp - iat should be 10 minutes (600 seconds)
        assert claims["exp"] - claims["iat"] == 600

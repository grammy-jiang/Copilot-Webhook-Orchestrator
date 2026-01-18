"""Tests for OAuth authentication flow.

These tests verify GitHub OAuth login, session management, and logout.
"""

import pytest
import respx
from httpx import Response


class TestOAuthFlow:
    """Tests for GitHub OAuth authentication flow."""

    @pytest.mark.integration
    async def test_oauth_login_redirect_to_github(self, client):
        """AC: GET /auth/login redirects to GitHub OAuth.

        @security AUTH-01
        """
        response = await client.get("/api/auth/login", follow_redirects=False)

        assert response.status_code == 302
        location = response.headers["location"]
        assert "github.com/login/oauth/authorize" in location
        assert "client_id=" in location
        assert "state=" in location

    @pytest.mark.integration
    @respx.mock
    async def test_oauth_callback_success_creates_session(
        self,
        client,
        mock_github_oauth,
    ):
        """AC: Valid OAuth callback creates session and redirects.

        @security AUTH-02
        """
        # Mock GitHub token exchange
        respx.post("https://github.com/login/oauth/access_token").mock(
            return_value=Response(
                200,
                json={
                    "access_token": "gho_test_token",
                    "token_type": "bearer",
                    "scope": "user:email",
                },
            )
        )

        # Mock GitHub user API
        respx.get("https://api.github.com/user").mock(
            return_value=Response(
                200,
                json={
                    "id": 12345678,
                    "login": "testuser",
                    "name": "Test User",
                    "email": "testuser@example.com",
                    "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
                },
            )
        )

        response = await client.get(
            "/api/auth/callback",
            params={"code": "test_auth_code", "state": "test_state"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        # Check set-cookie header for session_token
        cookie_header = response.headers.get("set-cookie", "")
        assert "session_token=" in cookie_header

    @pytest.mark.integration
    @respx.mock
    async def test_oauth_callback_sets_secure_cookie_flags(
        self,
        client,
        mock_github_oauth,
    ):
        """AC: Session cookie has proper security flags.

        @security AUTH-02
        """
        respx.post("https://github.com/login/oauth/access_token").mock(
            return_value=Response(
                200,
                json={"access_token": "gho_test_token", "token_type": "bearer"},
            )
        )
        respx.get("https://api.github.com/user").mock(
            return_value=Response(
                200,
                json={
                    "id": 12345678,
                    "login": "testuser",
                    "email": "test@example.com",
                },
            )
        )

        response = await client.get(
            "/api/auth/callback",
            params={"code": "test_auth_code", "state": "test_state"},
            follow_redirects=False,
        )

        # Check cookie is set with httponly flag
        cookie_header = response.headers.get("set-cookie", "")
        assert "httponly" in cookie_header.lower()

    @pytest.mark.integration
    @respx.mock
    async def test_oauth_token_exchange_failure(self, client):
        """AC: OAuth token exchange failure returns error.

        @security AUTH-03
        """
        respx.post("https://github.com/login/oauth/access_token").mock(
            return_value=Response(400, json={"error": "bad_verification_code"})
        )

        response = await client.get(
            "/api/auth/callback",
            params={"code": "invalid_code", "state": "test_state"},
            follow_redirects=False,
        )

        assert response.status_code == 400


class TestSessionManagement:
    """Tests for session creation and validation."""

    @pytest.mark.integration
    async def test_authenticated_user_can_access_protected_routes(
        self,
        authenticated_client,
    ):
        """AC: Valid session grants access to protected routes.

        @security AUTH-04
        """
        response = await authenticated_client.get("/api/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert "github_login" in data

    @pytest.mark.integration
    async def test_expired_session_returns_401(
        self,
        app,
        expired_session,
    ):
        """AC: Expired session token returns 401."""
        from httpx import ASGITransport, AsyncClient

        _, token = expired_session

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies={"session_token": token},
        ) as client:
            response = await client.get("/api/auth/me")

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_logout_invalidates_session(
        self,
        authenticated_client,
    ):
        """AC: GET /auth/logout invalidates session and clears cookie."""
        response = await authenticated_client.get(
            "/api/auth/logout", follow_redirects=False
        )

        assert response.status_code == 302
        # Cookie should be deleted
        cookie_header = response.headers.get("set-cookie", "")
        assert "session_token" in cookie_header

    @pytest.mark.integration
    async def test_get_current_user_returns_user_info(
        self,
        authenticated_client,
    ):
        """AC: GET /auth/me returns current user information."""
        response = await authenticated_client.get("/api/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "github_id" in data
        assert "github_login" in data
        assert data["github_login"] == "testuser"


class TestUnauthenticatedAccess:
    """Tests for unauthenticated access handling."""

    @pytest.mark.integration
    async def test_unauthenticated_access_returns_401(self, client):
        """AC: Protected routes return 401 without session.

        @security AUTH-04
        """
        response = await client.get("/api/auth/me")

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_invalid_session_token_returns_401(self, client):
        """AC: Invalid session token returns 401.

        @security AUTH-04
        """
        response = await client.get(
            "/api/auth/me",
            cookies={"session_token": "invalid_token"},
        )

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_health_endpoint_accessible_without_auth(self, client):
        """AC: Health endpoint doesn't require authentication."""
        response = await client.get("/health")

        assert response.status_code == 200

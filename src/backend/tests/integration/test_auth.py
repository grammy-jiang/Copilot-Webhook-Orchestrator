"""Tests for authentication (OAuth flow, sessions, logout).

Story 0: User Authentication (OAuth Login)

These tests define expected behavior for the OAuth authentication flow.
Tests are written BEFORE implementation (TDD Red phase).
"""

import pytest


class TestOAuthFlow:
    """Tests for GitHub OAuth authentication flow."""

    @pytest.mark.integration
    async def test_unauthenticated_redirect_to_login(self, client):
        """
        AC: Given I have not logged in before
            When I visit the home page
            Then I am redirected to the login page

        @story Story 0: User Authentication
        """
        response = await client.get("/", follow_redirects=False)

        assert response.status_code == 302
        assert "/auth/login" in response.headers["location"]

    @pytest.mark.integration
    async def test_oauth_login_redirect_to_github(self, client):
        """
        AC: Given I am on the login page
            When I click "Login with GitHub"
            Then I am redirected to GitHub OAuth authorization page
            And the URL includes: client_id, redirect_uri, scope

        @story Story 0: User Authentication
        """
        response = await client.get("/api/auth/login", follow_redirects=False)

        assert response.status_code == 302
        location = response.headers["location"]

        # Verify GitHub OAuth URL structure
        assert "github.com/login/oauth/authorize" in location
        assert "client_id=" in location
        assert "redirect_uri=" in location
        assert "scope=" in location
        assert "state=" in location  # CSRF protection

    @pytest.mark.integration
    async def test_oauth_callback_success_creates_session(
        self,
        client,
        mock_github_oauth,
        mocker,
    ):
        """
        AC: When I authorize the app on GitHub
            Then I am redirected back to the callback URL
            And the tool exchanges the code for a user access token
            And a session is created for me
            And I am redirected to the dashboard

        @story Story 0: User Authentication
        """
        # Mock GitHub OAuth token exchange
        mocker.patch(
            "copilot_orchestrator.services.github_oauth.exchange_code_for_token",
            return_value=mock_github_oauth.exchange_code_for_token.return_value,
        )
        mocker.patch(
            "copilot_orchestrator.services.github_oauth.get_user",
            return_value=mock_github_oauth.get_user.return_value,
        )

        # Simulate OAuth callback with valid code and state
        response = await client.get(
            "/api/auth/callback",
            params={"code": "valid_auth_code", "state": "valid_state_token"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/dashboard" in response.headers["location"]

        # Verify session cookie is set
        assert "session" in response.cookies
        session_cookie = response.cookies["session"]
        assert session_cookie is not None

    @pytest.mark.integration
    async def test_oauth_callback_sets_secure_cookie_flags(
        self,
        client,
        mock_github_oauth,
        mocker,
    ):
        """
        AC: Session cookie has HttpOnly, Secure, SameSite flags

        @story Story 0: User Authentication
        @security AUTH-02
        """
        mocker.patch(
            "copilot_orchestrator.services.github_oauth.exchange_code_for_token",
            return_value=mock_github_oauth.exchange_code_for_token.return_value,
        )
        mocker.patch(
            "copilot_orchestrator.services.github_oauth.get_user",
            return_value=mock_github_oauth.get_user.return_value,
        )

        response = await client.get(
            "/api/auth/callback",
            params={"code": "valid_auth_code", "state": "valid_state_token"},
            follow_redirects=False,
        )

        # Check cookie attributes in Set-Cookie header
        set_cookie = response.headers.get("set-cookie", "")
        assert "HttpOnly" in set_cookie
        # Note: Secure flag only in production (HTTPS)
        assert "SameSite=Lax" in set_cookie or "SameSite=Strict" in set_cookie

    @pytest.mark.integration
    async def test_oauth_callback_with_invalid_state_rejected(self, client):
        """
        AC: When GitHub returns with an invalid state token
            Then I am redirected to the login page
            And an error message is displayed

        @story Story 0: User Authentication
        @security AUTH-03
        """
        response = await client.get(
            "/api/auth/callback",
            params={"code": "valid_code", "state": "invalid_state_token"},
            follow_redirects=False,
        )

        assert response.status_code in (302, 400)
        if response.status_code == 302:
            assert "/auth/login" in response.headers["location"]
            assert "error" in response.headers["location"]

    @pytest.mark.integration
    async def test_oauth_callback_with_error_from_github(self, client):
        """
        AC: When GitHub returns an error (e.g., user denies authorization)
            Then I am redirected to the login page
            And an error message is displayed

        @story Story 0: User Authentication
        """
        response = await client.get(
            "/api/auth/callback",
            params={
                "error": "access_denied",
                "error_description": "The user denied access",
            },
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/auth/login" in response.headers["location"]

    @pytest.mark.integration
    async def test_oauth_token_exchange_failure(
        self,
        client,
        mocker,
    ):
        """
        AC: When the tool attempts to exchange the code for a token
            And the GitHub API returns an error
            Then I see an error message
            And I am not logged in

        @story Story 0: User Authentication
        """
        # Mock failed token exchange
        mocker.patch(
            "copilot_orchestrator.services.github_oauth.exchange_code_for_token",
            side_effect=Exception("GitHub API error"),
        )

        response = await client.get(
            "/api/auth/callback",
            params={"code": "valid_code", "state": "valid_state"},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/auth/login" in response.headers["location"]
        # Should not have session cookie
        assert "session" not in response.cookies


class TestSessionManagement:
    """Tests for session management and expiration."""

    @pytest.mark.integration
    async def test_authenticated_user_can_access_protected_routes(
        self,
        client,
        test_session_data,
        session,
    ):
        """
        AC: Given I have logged in previously
            And my session is still valid
            When I visit the home page
            Then I see the dashboard directly

        @story Story 0: User Authentication
        """
        # Create user and session in test DB
        # TODO: Insert test_user_data and test_session_data into session

        # Make request with session cookie
        response = await client.get(
            "/api/dashboard",
            cookies={"session": test_session_data["session_token"]},
        )

        assert response.status_code == 200

    @pytest.mark.integration
    async def test_expired_session_redirects_to_login(
        self,
        client,
        expired_session_data,
        session,
    ):
        """
        AC: Given my session has expired (>30 days old)
            When I visit the home page
            Then I am redirected to the login page

        @story Story 0: User Authentication
        @reliability REL-03
        """
        # Create expired session in test DB
        # TODO: Insert expired_session_data into session

        response = await client.get(
            "/api/dashboard",
            cookies={"session": expired_session_data["session_token"]},
            follow_redirects=False,
        )

        assert response.status_code in (302, 401)
        if response.status_code == 302:
            assert "/auth/login" in response.headers["location"]

    @pytest.mark.integration
    async def test_logout_destroys_session(
        self,
        client,
        test_session_data,
        session,
    ):
        """
        AC: Given I am logged in
            When I click "Logout"
            Then my session is destroyed
            And I am redirected to the login page

        @story Story 0: User Authentication
        """
        response = await client.post(
            "/api/auth/logout",
            cookies={"session": test_session_data["session_token"]},
            follow_redirects=False,
        )

        assert response.status_code in (200, 302)

        # Session cookie should be cleared
        if "set-cookie" in response.headers:
            set_cookie = response.headers["set-cookie"]
            # Cookie should be expired or empty
            assert "session=" in set_cookie
            assert "expires=" in set_cookie.lower() or "max-age=0" in set_cookie.lower()

    @pytest.mark.integration
    async def test_get_current_user(
        self,
        client,
        test_user_data,
        test_session_data,
        session,
    ):
        """
        AC: Given I am logged in
            When I visit the user menu
            Then I see my GitHub username and avatar

        @story Story 0: User Authentication
        """
        # TODO: Insert test_user_data and test_session_data into session

        response = await client.get(
            "/api/auth/me",
            cookies={"session": test_session_data["session_token"]},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == test_user_data["username"]
        assert data["github_id"] == test_user_data["github_id"]
        assert "avatar_url" in data


class TestUnauthenticatedAccess:
    """Tests for unauthenticated access to protected resources."""

    @pytest.mark.integration
    @pytest.mark.security
    async def test_unauthenticated_access_returns_401(self, client):
        """
        Verify unauthenticated access to protected endpoints returns 401.

        @security AUTH-01
        """
        protected_endpoints = [
            "/api/auth/me",
            "/api/installations",
            "/api/repos",
            "/api/dashboard",
            "/api/events/recent",
        ]

        for endpoint in protected_endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 401, f"Expected 401 for {endpoint}"

    @pytest.mark.integration
    @pytest.mark.security
    async def test_invalid_session_token_returns_401(self, client):
        """
        Verify invalid session token is rejected.

        @security AUTH-01
        """
        response = await client.get(
            "/api/auth/me",
            cookies={"session": "completely_invalid_token"},
        )

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_health_endpoint_accessible_without_auth(self, client):
        """
        Verify health endpoint is accessible without authentication.

        This is required for load balancer health checks.
        """
        response = await client.get("/api/health")

        assert response.status_code in (200, 503)
        data = response.json()
        assert "status" in data

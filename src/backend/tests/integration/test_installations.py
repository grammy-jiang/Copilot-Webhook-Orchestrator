"""Tests for GitHub App installation and repository access.

Story 0b: App Installation & Repository Access

These tests define expected behavior for the GitHub App installation flow.
Tests are written BEFORE implementation (TDD Red phase).
"""

from uuid import uuid4

import pytest


class TestInstallationFlow:
    """Tests for GitHub App installation and callback handling."""

    @pytest.mark.integration
    async def test_no_installations_returns_empty_list(
        self,
        client,
        test_session_data,
    ):
        """
        AC: Given I am logged in
            And I have not installed the GitHub App yet
            When I query installations
            Then I see an empty list

        @story Story 0b: App Installation
        """
        response = await client.get(
            "/api/installations",
            cookies={"session": test_session_data["session_token"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert "installations" in data
        assert data["installations"] == []

    @pytest.mark.integration
    async def test_installation_redirect_to_github(
        self,
        client,
        test_session_data,
    ):
        """
        AC: When I click "Connect Repositories"
            Then I am redirected to GitHub App installation page

        @story Story 0b: App Installation
        """
        response = await client.get(
            "/api/installations/new",
            cookies={"session": test_session_data["session_token"]},
            follow_redirects=False,
        )

        assert response.status_code == 302
        location = response.headers["location"]
        assert "github.com/apps/" in location
        assert "/installations/new" in location

    @pytest.mark.integration
    async def test_installation_callback_success(
        self,
        client,
        test_session_data,
        mock_github_api,
        mocker,
    ):
        """
        AC: When I complete installation on GitHub
            Then GitHub redirects back to the callback URL
            And the tool fetches the list of repositories
            And I am redirected to the dashboard

        @story Story 0b: App Installation
        """
        # Mock GitHub API calls
        mocker.patch(
            "copilot_orchestrator.services.github_api.get_installation_repositories",
            return_value=mock_github_api.get_installation_repositories.return_value,
        )

        response = await client.get(
            "/api/installations/callback",
            params={
                "installation_id": "12345",
                "setup_action": "install",
            },
            cookies={"session": test_session_data["session_token"]},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert "/dashboard" in response.headers["location"]

    @pytest.mark.integration
    async def test_installation_callback_update(
        self,
        client,
        test_session_data,
        test_installation_data,
        mock_github_api,
        mocker,
        session,
    ):
        """
        AC: When I add or remove repositories on GitHub
            Then the tool re-fetches the repository list
            And my dashboard is updated

        @story Story 0b: App Installation
        """
        # Insert existing installation
        # TODO: Insert test_installation_data into session

        mocker.patch(
            "copilot_orchestrator.services.github_api.get_installation_repositories",
            return_value=mock_github_api.get_installation_repositories.return_value,
        )

        response = await client.get(
            "/api/installations/callback",
            params={
                "installation_id": str(test_installation_data["installation_id"]),
                "setup_action": "install",  # GitHub sends 'install' for updates too
            },
            cookies={"session": test_session_data["session_token"]},
            follow_redirects=False,
        )

        assert response.status_code == 302

    @pytest.mark.integration
    async def test_get_installation_details(
        self,
        client,
        test_session_data,
        test_installation_data,
        session,
    ):
        """
        AC: When I view installation details
            Then I see the installation info and repositories

        @story Story 0b: App Installation
        """
        # TODO: Insert test_installation_data into session

        response = await client.get(
            f"/api/installations/{test_installation_data['id']}",
            cookies={"session": test_session_data["session_token"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["installation_id"] == test_installation_data["installation_id"]
        assert data["account_login"] == test_installation_data["account_login"]
        assert "repositories" in data

    @pytest.mark.integration
    async def test_installation_callback_failure_shows_error(
        self,
        client,
        test_session_data,
        mocker,
    ):
        """
        AC: When the GitHub API fails to return repository details
            Then I see an error message

        @story Story 0b: App Installation
        """
        mocker.patch(
            "copilot_orchestrator.services.github_api.get_installation_repositories",
            side_effect=Exception("GitHub API error"),
        )

        response = await client.get(
            "/api/installations/callback",
            params={
                "installation_id": "12345",
                "setup_action": "install",
            },
            cookies={"session": test_session_data["session_token"]},
            follow_redirects=False,
        )

        # Should redirect with error or return error response
        assert response.status_code in (302, 500)


class TestInstallationWebhooks:
    """Tests for installation-related webhook events."""

    @pytest.mark.integration
    async def test_installation_suspended_webhook(
        self,
        client,
        test_installation_data,
        webhook_secret,
        session,
    ):
        """
        AC: When I suspend the installation on GitHub
            Then GitHub sends a webhook: installation.suspended
            And the tool marks the installation as suspended

        @story Story 0b: App Installation
        """
        import hashlib
        import hmac
        import json

        payload = {
            "action": "suspend",
            "installation": {
                "id": test_installation_data["installation_id"],
                "account": {"login": test_installation_data["account_login"]},
            },
            "sender": {"login": "testuser"},
        }

        payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
        signature = hmac.new(
            webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        response = await client.post(
            "/api/webhooks/github",
            json=payload,
            headers={
                "X-Hub-Signature-256": f"sha256={signature}",
                "X-GitHub-Delivery": "test-delivery-suspend",
                "X-GitHub-Event": "installation",
            },
        )

        assert response.status_code == 200

    @pytest.mark.integration
    async def test_installation_deleted_webhook(
        self,
        client,
        test_installation_data,
        webhook_secret,
        session,
    ):
        """
        AC: When I uninstall the app on GitHub
            Then GitHub sends a webhook: installation.deleted
            And the tool marks the installation as deleted

        @story Story 0b: App Installation
        """
        import hashlib
        import hmac
        import json

        payload = {
            "action": "deleted",
            "installation": {
                "id": test_installation_data["installation_id"],
                "account": {"login": test_installation_data["account_login"]},
            },
            "sender": {"login": "testuser"},
        }

        payload_bytes = json.dumps(payload, separators=(",", ":")).encode()
        signature = hmac.new(
            webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        response = await client.post(
            "/api/webhooks/github",
            json=payload,
            headers={
                "X-Hub-Signature-256": f"sha256={signature}",
                "X-GitHub-Delivery": "test-delivery-delete",
                "X-GitHub-Event": "installation",
            },
        )

        assert response.status_code == 200


class TestInstallationAuthorization:
    """Tests for installation access control."""

    @pytest.mark.integration
    @pytest.mark.security
    async def test_cannot_access_other_users_installation(
        self,
        client,
        test_session_data,
        session,
    ):
        """
        AC: User cannot access another user's installations.

        @security AUTHZ-01
        """
        # Create installation belonging to a different user
        other_user_installation_id = uuid4()
        # TODO: Insert installation for a different user

        response = await client.get(
            f"/api/installations/{other_user_installation_id}",
            cookies={"session": test_session_data["session_token"]},
        )

        # Should return 404 (not 403, to avoid enumeration)
        assert response.status_code == 404

    @pytest.mark.integration
    async def test_single_installation_per_user_constraint(
        self,
        client,
        test_session_data,
        test_installation_data,
        mock_github_api,
        mocker,
        session,
    ):
        """
        AC: Given I have one installation already
            When I attempt to create a second installation
            Then I am redirected to manage my existing installation

        @story Story 0b: App Installation
        """
        # Insert existing installation for user
        # TODO: Insert test_installation_data into session

        mocker.patch(
            "copilot_orchestrator.services.github_api.get_installation_repositories",
            return_value=mock_github_api.get_installation_repositories.return_value,
        )

        # Try to create another installation
        response = await client.get(
            "/api/installations/callback",
            params={
                "installation_id": "99999",  # Different installation
                "setup_action": "install",
            },
            cookies={"session": test_session_data["session_token"]},
            follow_redirects=False,
        )

        # Should redirect or return error about single installation limit
        assert response.status_code in (302, 400, 409)


class TestJWTGeneration:
    """Unit tests for JWT generation for GitHub App authentication."""

    @pytest.mark.unit
    def test_jwt_generation_creates_valid_token(self):
        """
        AC: The tool generates a JWT signed with GitHub App private key.

        @story Story 0b: App Installation
        """
        # TODO: Import and test JWT generation function
        # from copilot_orchestrator.services.github_api import generate_jwt
        #
        # jwt_token = generate_jwt(
        #     app_id="123456",
        #     private_key_pem="<PEM-encoded-key>",
        # )
        #
        # assert jwt_token is not None
        # assert jwt_token.count(".") == 2  # JWT has 3 parts

        pytest.skip("JWT generation not implemented yet (TDD Red phase)")

    @pytest.mark.unit
    def test_jwt_has_correct_claims(self):
        """
        Verify JWT contains required claims (iss, iat, exp).

        @story Story 0b: App Installation
        """
        # TODO: Verify JWT claims
        pytest.skip("JWT generation not implemented yet (TDD Red phase)")

    @pytest.mark.unit
    def test_jwt_expires_in_10_minutes(self):
        """
        Verify JWT expiration is set correctly (max 10 minutes per GitHub).

        @story Story 0b: App Installation
        """
        # TODO: Verify JWT expiration
        pytest.skip("JWT generation not implemented yet (TDD Red phase)")

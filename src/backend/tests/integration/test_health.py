"""Tests for health check endpoint.

These tests verify the health endpoint behavior for load balancer checks.
Tests are written BEFORE implementation (TDD Red phase).
"""

import pytest


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    @pytest.mark.integration
    async def test_health_endpoint_accessible_without_auth(self, client):
        """
        Verify health endpoint is accessible without authentication.

        This is required for load balancer and Kubernetes probes.
        """
        response = await client.get("/api/health")

        assert response.status_code in (200, 503)

    @pytest.mark.integration
    async def test_health_endpoint_returns_status(self, client):
        """
        Verify health endpoint returns expected fields.
        """
        response = await client.get("/api/health")
        data = response.json()

        assert "status" in data
        assert data["status"] in ("healthy", "unhealthy")
        assert "version" in data
        assert "database" in data
        assert "timestamp" in data

    @pytest.mark.integration
    async def test_health_returns_200_when_healthy(
        self,
        client,
        session,  # Ensures DB is connected
    ):
        """
        AC: When database is connected
            Then /health returns 200 OK

        @reliability REL-01
        """
        response = await client.get("/api/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    @pytest.mark.integration
    async def test_health_returns_503_when_db_unavailable(
        self,
        client,
        mocker,
    ):
        """
        AC: When database is unavailable
            Then /health returns 503 Service Unavailable

        @reliability REL-01
        """
        # Mock database connection failure
        mocker.patch(
            "copilot_orchestrator.db.check_database_connection",
            side_effect=Exception("Database connection failed"),
        )

        response = await client.get("/api/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"] == "disconnected"

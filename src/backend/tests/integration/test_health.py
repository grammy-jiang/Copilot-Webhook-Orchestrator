"""Tests for health check endpoint.

These tests verify the health endpoint behavior for load balancer checks.
"""

import pytest

from app import __version__


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    @pytest.mark.integration
    async def test_health_endpoint_accessible_without_auth(self, client):
        """Verify health endpoint is accessible without authentication.

        This is required for load balancer and Kubernetes probes.
        """
        response = await client.get("/health")

        assert response.status_code == 200

    @pytest.mark.integration
    async def test_health_endpoint_returns_status(self, client):
        """Verify health endpoint returns expected fields."""
        response = await client.get("/health")
        data = response.json()

        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    @pytest.mark.integration
    async def test_health_returns_200_when_healthy(self, client):
        """AC: When database is connected, /health returns 200 OK.

        @reliability REL-01
        """
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == __version__

    @pytest.mark.integration
    async def test_health_returns_correct_version(self, client):
        """Verify health endpoint returns correct application version."""
        response = await client.get("/health")
        data = response.json()

        assert data["version"] == __version__

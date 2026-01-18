"""Tests for GitHub webhook handling.

These tests verify webhook signature verification, idempotency, and event processing.
"""

import hashlib
import hmac
import inspect
import json

import pytest

from app.services.crypto import verify_webhook_signature


class TestWebhookSignatureVerification:
    """Tests for HMAC-SHA256 webhook signature verification."""

    @pytest.mark.integration
    @pytest.mark.security
    async def test_valid_webhook_signature_accepted(
        self,
        client,
        valid_webhook_payload,
        webhook_secret,
        monkeypatch,
    ):
        """AC: Webhook with valid signature is accepted.

        @security WEBHOOK-01
        """
        # Set the webhook secret in config
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", webhook_secret)

        payload_bytes = json.dumps(valid_webhook_payload).encode()
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
                "X-GitHub-Event": "pull_request",
                "X-GitHub-Delivery": "test-delivery-123",
                "X-Hub-Signature-256": signature,
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("accepted", "duplicate")

    @pytest.mark.integration
    @pytest.mark.security
    async def test_invalid_webhook_signature_rejected(
        self,
        client,
        valid_webhook_payload,
        webhook_secret,
        monkeypatch,
    ):
        """AC: Webhook with invalid signature returns 401.

        @security WEBHOOK-01
        """
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", webhook_secret)

        payload_bytes = json.dumps(valid_webhook_payload).encode()

        response = await client.post(
            "/api/webhooks/github",
            content=payload_bytes,
            headers={
                "X-GitHub-Event": "pull_request",
                "X-GitHub-Delivery": "test-delivery-456",
                "X-Hub-Signature-256": "sha256=invalid_signature",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 401

    @pytest.mark.integration
    @pytest.mark.security
    async def test_missing_signature_header_rejected(
        self,
        client,
        valid_webhook_payload,
        webhook_secret,
        monkeypatch,
    ):
        """AC: Missing signature header returns 401.

        @security WEBHOOK-02
        """
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", webhook_secret)

        payload_bytes = json.dumps(valid_webhook_payload).encode()

        response = await client.post(
            "/api/webhooks/github",
            content=payload_bytes,
            headers={
                "X-GitHub-Event": "pull_request",
                "X-GitHub-Delivery": "test-delivery-789",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_missing_delivery_id_rejected(
        self,
        client,
        valid_webhook_payload,
        webhook_secret,
        valid_webhook_signature,
    ):
        """AC: Missing X-GitHub-Delivery header returns 422."""
        payload_bytes = json.dumps(valid_webhook_payload).encode()

        response = await client.post(
            "/api/webhooks/github",
            content=payload_bytes,
            headers={
                "X-GitHub-Event": "pull_request",
                "X-Hub-Signature-256": valid_webhook_signature,
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 422

    @pytest.mark.integration
    async def test_missing_event_type_rejected(
        self,
        client,
        valid_webhook_payload,
        webhook_secret,
        valid_webhook_signature,
    ):
        """AC: Missing X-GitHub-Event header returns 422."""
        payload_bytes = json.dumps(valid_webhook_payload).encode()

        response = await client.post(
            "/api/webhooks/github",
            content=payload_bytes,
            headers={
                "X-GitHub-Delivery": "test-delivery-missing-event",
                "X-Hub-Signature-256": valid_webhook_signature,
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 422


class TestWebhookIdempotency:
    """Tests for webhook idempotency handling."""

    @pytest.mark.integration
    async def test_duplicate_delivery_id_handled_idempotently(
        self,
        client,
        valid_webhook_payload,
        webhook_secret,
        monkeypatch,
    ):
        """AC: Duplicate delivery ID returns success without reprocessing.

        @security WEBHOOK-03 (prevents replay attacks)
        """
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", webhook_secret)

        payload_bytes = json.dumps(valid_webhook_payload).encode()
        signature = (
            "sha256="
            + hmac.new(
                webhook_secret.encode(),
                payload_bytes,
                hashlib.sha256,
            ).hexdigest()
        )
        delivery_id = "idempotency-test-delivery-123"

        headers = {
            "X-GitHub-Event": "pull_request",
            "X-GitHub-Delivery": delivery_id,
            "X-Hub-Signature-256": signature,
            "Content-Type": "application/json",
        }

        # First request
        response1 = await client.post(
            "/api/webhooks/github",
            content=payload_bytes,
            headers=headers,
        )
        assert response1.status_code == 200

        # Second request with same delivery ID
        response2 = await client.post(
            "/api/webhooks/github",
            content=payload_bytes,
            headers=headers,
        )
        assert response2.status_code == 200
        data = response2.json()
        assert data["status"] == "duplicate"


class TestWebhookPayloadValidation:
    """Tests for webhook payload validation."""

    @pytest.mark.integration
    async def test_malformed_json_rejected(
        self,
        client,
        webhook_secret,
        monkeypatch,
    ):
        """AC: Malformed JSON payload returns 400."""
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", webhook_secret)

        malformed_payload = b'{"invalid json'
        signature = (
            "sha256="
            + hmac.new(
                webhook_secret.encode(),
                malformed_payload,
                hashlib.sha256,
            ).hexdigest()
        )

        response = await client.post(
            "/api/webhooks/github",
            content=malformed_payload,
            headers={
                "X-GitHub-Event": "pull_request",
                "X-GitHub-Delivery": "malformed-json-test",
                "X-Hub-Signature-256": signature,
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 400


class TestWebhookEventTypes:
    """Tests for supported webhook event types."""

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "event_type,action",
        [
            ("issues", "opened"),
            ("issues", "closed"),
            ("pull_request", "opened"),
            ("pull_request", "closed"),
            ("pull_request", "synchronize"),
            ("push", None),
            ("check_suite", "completed"),
            ("check_run", "completed"),
        ],
    )
    async def test_supported_event_types_accepted(
        self,
        client,
        webhook_secret,
        monkeypatch,
        event_type,
        action,
    ):
        """AC: Supported event types are accepted and stored."""
        monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", webhook_secret)

        payload = {"action": action} if action else {}
        payload["repository"] = {"id": 123456789, "full_name": "testuser/test-repo"}
        payload["sender"] = {"login": "testuser", "id": 12345678}

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
                "X-GitHub-Event": event_type,
                "X-GitHub-Delivery": f"event-type-test-{event_type}-{action}",
                "X-Hub-Signature-256": signature,
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 200


class TestHMACVerificationUnit:
    """Unit-level tests for HMAC verification function."""

    @pytest.mark.unit
    def test_hmac_verification_valid_signature(self, webhook_secret):
        """Verify valid HMAC signature is accepted."""
        payload = b'{"test": "data"}'
        signature = (
            "sha256="
            + hmac.new(
                webhook_secret.encode(),
                payload,
                hashlib.sha256,
            ).hexdigest()
        )

        assert verify_webhook_signature(payload, signature, webhook_secret) is True

    @pytest.mark.unit
    def test_hmac_verification_invalid_signature(self, webhook_secret):
        """Verify invalid HMAC signature is rejected."""
        payload = b'{"test": "data"}'

        assert (
            verify_webhook_signature(payload, "sha256=invalid", webhook_secret) is False
        )

    @pytest.mark.unit
    @pytest.mark.security
    def test_hmac_uses_constant_time_comparison(self):
        """Verify HMAC uses hmac.compare_digest (constant-time).

        @security Prevents timing attacks
        """
        source = inspect.getsource(verify_webhook_signature)
        assert "compare_digest" in source

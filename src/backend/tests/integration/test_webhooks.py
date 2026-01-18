"""Tests for GitHub webhook receiver and signature verification.

Story 1: GitHub App Webhook Receiver

These tests define expected behavior for webhook receiving and verification.
Tests are written BEFORE implementation (TDD Red phase).
"""

import hashlib
import hmac
import json
from typing import Any

import pytest


class TestWebhookSignatureVerification:
    """Tests for HMAC-SHA256 signature verification."""

    @pytest.mark.integration
    async def test_valid_webhook_signature_accepted(
        self,
        client,
        valid_webhook_payload,
        valid_webhook_signature,
    ):
        """
        AC: Given a webhook with a valid HMAC-SHA256 signature
            When the webhook is received
            Then the tool returns HTTP 200 OK

        @story Story 1: Webhook Receiver
        """
        response = await client.post(
            "/api/webhooks/github",
            json=valid_webhook_payload,
            headers={
                "X-Hub-Signature-256": valid_webhook_signature,
                "X-GitHub-Delivery": "test-delivery-001",
                "X-GitHub-Event": "pull_request",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert data["delivery_id"] == "test-delivery-001"

    @pytest.mark.integration
    @pytest.mark.security
    async def test_invalid_webhook_signature_rejected(
        self,
        client,
        valid_webhook_payload,
        invalid_webhook_signature,
    ):
        """
        AC: Given a webhook with an invalid signature
            When the webhook is received
            Then the tool returns HTTP 401 Unauthorized
            And the event is NOT processed

        @story Story 1: Webhook Receiver
        @security WEBHOOK-01
        """
        response = await client.post(
            "/api/webhooks/github",
            json=valid_webhook_payload,
            headers={
                "X-Hub-Signature-256": invalid_webhook_signature,
                "X-GitHub-Delivery": "test-delivery-invalid-sig",
                "X-GitHub-Event": "pull_request",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert data["error"]["code"] == "UNAUTHORIZED"

    @pytest.mark.integration
    @pytest.mark.security
    async def test_missing_signature_header_rejected(
        self,
        client,
        valid_webhook_payload,
    ):
        """
        AC: Given a webhook without a signature header
            When the webhook is received
            Then the tool returns HTTP 401 Unauthorized

        @story Story 1: Webhook Receiver
        @security WEBHOOK-02
        """
        response = await client.post(
            "/api/webhooks/github",
            json=valid_webhook_payload,
            headers={
                # Missing X-Hub-Signature-256
                "X-GitHub-Delivery": "test-delivery-no-sig",
                "X-GitHub-Event": "pull_request",
            },
        )

        assert response.status_code == 401

    @pytest.mark.integration
    async def test_missing_delivery_id_rejected(
        self,
        client,
        valid_webhook_payload,
        valid_webhook_signature,
    ):
        """
        AC: Given a webhook without a delivery ID
            When the webhook is received
            Then the tool returns HTTP 400 Bad Request

        @story Story 1: Webhook Receiver
        """
        response = await client.post(
            "/api/webhooks/github",
            json=valid_webhook_payload,
            headers={
                "X-Hub-Signature-256": valid_webhook_signature,
                # Missing X-GitHub-Delivery
                "X-GitHub-Event": "pull_request",
            },
        )

        assert response.status_code == 400

    @pytest.mark.integration
    async def test_missing_event_type_rejected(
        self,
        client,
        valid_webhook_payload,
        valid_webhook_signature,
    ):
        """
        AC: Given a webhook without an event type header
            When the webhook is received
            Then the tool returns HTTP 400 Bad Request

        @story Story 1: Webhook Receiver
        """
        response = await client.post(
            "/api/webhooks/github",
            json=valid_webhook_payload,
            headers={
                "X-Hub-Signature-256": valid_webhook_signature,
                "X-GitHub-Delivery": "test-delivery-no-event",
                # Missing X-GitHub-Event
            },
        )

        assert response.status_code == 400


class TestWebhookIdempotency:
    """Tests for duplicate webhook handling (idempotency)."""

    @pytest.mark.integration
    @pytest.mark.security
    async def test_duplicate_delivery_id_handled_idempotently(
        self,
        client,
        valid_webhook_payload,
        valid_webhook_signature,
        session,
    ):
        """
        AC: Given a webhook event has been processed successfully
            When GitHub redelivers the same event (same delivery ID)
            Then the tool returns HTTP 200 OK
            And the event is NOT reprocessed

        @story Story 1: Webhook Receiver
        @security WEBHOOK-03
        @reliability REL-02
        """
        delivery_id = "test-delivery-duplicate"

        # First request
        response1 = await client.post(
            "/api/webhooks/github",
            json=valid_webhook_payload,
            headers={
                "X-Hub-Signature-256": valid_webhook_signature,
                "X-GitHub-Delivery": delivery_id,
                "X-GitHub-Event": "pull_request",
            },
        )
        assert response1.status_code == 200

        # Second request with same delivery ID
        response2 = await client.post(
            "/api/webhooks/github",
            json=valid_webhook_payload,
            headers={
                "X-Hub-Signature-256": valid_webhook_signature,
                "X-GitHub-Delivery": delivery_id,
                "X-GitHub-Event": "pull_request",
            },
        )

        # Should still return 200 (idempotent)
        assert response2.status_code == 200
        # TODO: Verify event was not processed twice (check DB)


class TestWebhookPayloadValidation:
    """Tests for webhook payload validation."""

    @pytest.mark.integration
    async def test_malformed_json_rejected(
        self,
        client,
        webhook_secret,
    ):
        """
        AC: Given a webhook with invalid JSON payload
            When the webhook is received
            Then the tool returns HTTP 400 Bad Request

        @story Story 1: Webhook Receiver
        @validation VAL-02
        """
        malformed_payload = b"{ invalid json }"
        signature = hmac.new(
            webhook_secret.encode(),
            malformed_payload,
            hashlib.sha256,
        ).hexdigest()

        response = await client.post(
            "/api/webhooks/github",
            content=malformed_payload,
            headers={
                "X-Hub-Signature-256": f"sha256={signature}",
                "X-GitHub-Delivery": "test-delivery-malformed",
                "X-GitHub-Event": "push",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 400

    @pytest.mark.integration
    async def test_oversized_payload_rejected(
        self,
        client,
        webhook_secret,
    ):
        """
        AC: Given a webhook payload exceeding 10MB
            When the webhook is received
            Then the tool returns HTTP 413 Payload Too Large

        @story Story 1: Webhook Receiver
        @validation VAL-01
        """
        # Create a payload larger than 10MB
        large_payload = {"data": "x" * (10 * 1024 * 1024 + 1)}
        payload_bytes = json.dumps(large_payload).encode()
        signature = hmac.new(
            webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        response = await client.post(
            "/api/webhooks/github",
            content=payload_bytes,
            headers={
                "X-Hub-Signature-256": f"sha256={signature}",
                "X-GitHub-Delivery": "test-delivery-large",
                "X-GitHub-Event": "push",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 413


class TestWebhookEventFiltering:
    """Tests for filtering webhooks by repository connection status."""

    @pytest.mark.integration
    async def test_unconnected_repository_webhook_ignored(
        self,
        client,
        webhook_secret,
    ):
        """
        AC: Given a repository is NOT connected to the tool
            When GitHub sends a webhook for that repository
            Then the tool returns HTTP 200 OK (to avoid GitHub retries)
            And the event is logged but NOT processed

        @story Story 1: Webhook Receiver
        """
        # Webhook from a repository not in our database
        unconnected_payload = {
            "action": "opened",
            "number": 1,
            "repository": {
                "id": 999999999,  # Unknown repo ID
                "name": "unknown-repo",
                "full_name": "stranger/unknown-repo",
            },
            "sender": {"login": "stranger"},
            "installation": {"id": 99999},  # Unknown installation
        }

        payload_bytes = json.dumps(unconnected_payload, separators=(",", ":")).encode()
        signature = hmac.new(
            webhook_secret.encode(),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()

        response = await client.post(
            "/api/webhooks/github",
            json=unconnected_payload,
            headers={
                "X-Hub-Signature-256": f"sha256={signature}",
                "X-GitHub-Delivery": "test-delivery-unconnected",
                "X-GitHub-Event": "issues",
            },
        )

        # Should still return 200 to prevent GitHub retries
        assert response.status_code == 200


class TestWebhookEventTypes:
    """Tests for different webhook event types."""

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
        test_installation_data,
        test_repository_data,
        event_type: str,
        action: str | None,
    ):
        """
        Verify all supported event types are accepted.

        @story Story 1: Webhook Receiver
        """
        payload: dict[str, Any] = {
            "repository": {
                "id": test_repository_data["github_id"],
                "name": test_repository_data["name"],
                "full_name": test_repository_data["full_name"],
            },
            "sender": {"login": "testuser"},
            "installation": {"id": test_installation_data["installation_id"]},
        }

        if action:
            payload["action"] = action

        # Add event-specific fields
        if event_type == "issues":
            payload["issue"] = {"number": 1, "title": "Test Issue"}
        elif event_type == "pull_request":
            payload["number"] = 42
            payload["pull_request"] = {"number": 42, "title": "Test PR"}
        elif event_type == "push":
            payload["ref"] = "refs/heads/main"
            payload["commits"] = []

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
                "X-GitHub-Delivery": f"test-{event_type}-{action or 'none'}",
                "X-GitHub-Event": event_type,
            },
        )

        assert response.status_code in (200, 202)


class TestHMACVerificationUnit:
    """Unit tests for HMAC signature verification logic."""

    @pytest.mark.unit
    def test_hmac_verification_valid_signature(self, webhook_secret):
        """
        Verify HMAC verification function accepts valid signatures.

        @story Story 1: Webhook Receiver
        """
        # TODO: Import verification function
        # from copilot_orchestrator.services.webhooks import verify_signature
        #
        # payload = b'{"test": "data"}'
        # expected_sig = hmac.new(
        #     webhook_secret.encode(),
        #     payload,
        #     hashlib.sha256,
        # ).hexdigest()
        #
        # assert verify_signature(
        #     payload=payload,
        #     signature=f"sha256={expected_sig}",
        #     secret=webhook_secret,
        # )

        pytest.skip("HMAC verification not implemented yet (TDD Red phase)")

    @pytest.mark.unit
    def test_hmac_verification_invalid_signature(self, webhook_secret):
        """
        Verify HMAC verification function rejects invalid signatures.

        @story Story 1: Webhook Receiver
        """
        pytest.skip("HMAC verification not implemented yet (TDD Red phase)")

    @pytest.mark.unit
    @pytest.mark.security
    def test_hmac_uses_constant_time_comparison(self, webhook_secret):
        """
        Verify HMAC comparison uses constant-time algorithm (timing attack prevention).

        @security Recommendation #4 from risk review
        """
        # TODO: Verify hmac.compare_digest is used
        pytest.skip("HMAC verification not implemented yet (TDD Red phase)")

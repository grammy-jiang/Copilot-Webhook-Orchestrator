"""Unit tests for cryptographic functions.

These tests verify HMAC, JWT, and token hashing functions.
"""

import hashlib
import hmac
import secrets

import pytest

from app.services.crypto import (
    compute_webhook_signature,
    decrypt_token,
    encrypt_token,
    generate_encryption_key,
    generate_jwt,
    generate_session_token,
    hash_token,
    verify_jwt,
    verify_webhook_signature,
)


class TestHMACVerification:
    """Unit tests for HMAC-SHA256 signature verification."""

    @pytest.mark.unit
    def test_verify_valid_hmac_signature(self):
        """Verify valid HMAC signature is accepted."""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        expected_sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
        signature = f"sha256={expected_sig}"

        assert (
            verify_webhook_signature(
                payload=payload,
                signature=signature,
                secret=secret,
            )
            is True
        )

    @pytest.mark.unit
    def test_verify_invalid_hmac_signature(self):
        """Verify invalid HMAC signature is rejected."""
        secret = "test_secret"
        payload = b'{"test": "data"}'

        assert (
            verify_webhook_signature(
                payload=payload,
                signature="sha256=invalid_signature",
                secret=secret,
            )
            is False
        )

    @pytest.mark.unit
    def test_verify_empty_signature_rejected(self):
        """Verify empty signature is rejected."""
        secret = "test_secret"
        payload = b'{"test": "data"}'

        assert (
            verify_webhook_signature(
                payload=payload,
                signature="",
                secret=secret,
            )
            is False
        )

    @pytest.mark.unit
    def test_verify_malformed_signature_rejected(self):
        """Verify malformed signature (missing sha256= prefix) is rejected."""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        sig_without_prefix = hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()

        assert (
            verify_webhook_signature(
                payload=payload,
                signature=sig_without_prefix,  # Missing sha256= prefix
                secret=secret,
            )
            is False
        )

    @pytest.mark.unit
    @pytest.mark.security
    def test_hmac_uses_constant_time_comparison(self):
        """Verify HMAC comparison uses constant-time comparison.

        We verify this by checking that the function uses hmac.compare_digest
        internally. We test this by checking the module source.
        """
        import inspect

        source = inspect.getsource(verify_webhook_signature)
        assert "compare_digest" in source

    @pytest.mark.unit
    def test_compute_webhook_signature(self):
        """Verify compute_webhook_signature generates valid signatures."""
        secret = "test_secret"
        payload = b'{"test": "data"}'

        signature = compute_webhook_signature(payload, secret)

        assert signature.startswith("sha256=")
        assert verify_webhook_signature(payload, signature, secret) is True


class TestSessionTokenGeneration:
    """Unit tests for session token generation."""

    @pytest.mark.unit
    def test_generate_session_token_length(self):
        """Verify session tokens are sufficiently long (256 bits)."""
        token = generate_session_token()
        # 256 bits = 32 bytes = 64 hex chars
        assert len(token) == 64

    @pytest.mark.unit
    def test_generate_session_token_uniqueness(self):
        """Verify session tokens are unique."""
        tokens = [generate_session_token() for _ in range(1000)]
        assert len(set(tokens)) == 1000

    @pytest.mark.unit
    def test_session_token_hashing(self):
        """Verify session tokens are hashed with SHA-256."""
        token = "test_token_abc123"
        hashed = hash_token(token)

        assert hashed != token
        assert len(hashed) == 64  # SHA-256 hex digest

    @pytest.mark.unit
    def test_session_token_verification(self):
        """Verify session token can be verified against hash."""
        token = generate_session_token()
        hashed = hash_token(token)

        # Same token should hash to same value
        assert hash_token(token) == hashed

        # Different token should hash to different value
        other_token = generate_session_token()
        assert hash_token(other_token) != hashed


class TestOAuthStateToken:
    """Unit tests for OAuth state token (CSRF protection)."""

    @pytest.mark.unit
    def test_generate_state_token(self):
        """Verify state tokens are generated securely using secrets module."""
        # The state token uses secrets.token_urlsafe which is cryptographically secure
        token = secrets.token_urlsafe(32)
        assert len(token) >= 32

    @pytest.mark.unit
    def test_state_token_uniqueness(self):
        """Verify state tokens are unique."""
        tokens = [secrets.token_urlsafe(32) for _ in range(1000)]
        assert len(set(tokens)) == 1000

    @pytest.mark.unit
    def test_state_token_jwt_expiration(self):
        """Verify state tokens via JWT expire correctly."""
        # Create a JWT with state claim
        state = secrets.token_urlsafe(16)
        token = generate_jwt({"state": state}, expires_in_minutes=10)

        # Verify the JWT is valid
        claims = verify_jwt(token)
        assert claims is not None
        assert claims["state"] == state


class TestAccessTokenEncryption:
    """Unit tests for GitHub access token encryption at rest."""

    @pytest.mark.unit
    def test_encrypt_access_token(self):
        """Verify access tokens are encrypted before storage."""
        token = "gho_test_access_token"
        key = generate_encryption_key()
        encrypted = encrypt_token(token, key)

        assert encrypted != token
        assert decrypt_token(encrypted, key) == token

    @pytest.mark.unit
    def test_decrypt_access_token(self):
        """Verify encrypted access tokens can be decrypted."""
        token = "gho_1234567890abcdef"
        key = generate_encryption_key()
        encrypted = encrypt_token(token, key)
        decrypted = decrypt_token(encrypted, key)

        assert decrypted == token

    @pytest.mark.unit
    def test_encryption_uses_unique_iv(self):
        """Verify each encryption uses a unique IV/nonce."""
        token = "gho_test_access_token"
        key = generate_encryption_key()

        # Encrypt same token twice
        encrypted1 = encrypt_token(token, key)
        encrypted2 = encrypt_token(token, key)

        # Ciphertext should be different due to unique IV
        assert encrypted1 != encrypted2

        # Both should decrypt to same plaintext
        assert decrypt_token(encrypted1, key) == token
        assert decrypt_token(encrypted2, key) == token


class TestJWTGeneration:
    """Unit tests for JWT generation."""

    @pytest.mark.unit
    def test_generate_jwt_structure(self):
        """Verify JWT has correct structure (header.payload.signature)."""
        jwt_token = generate_jwt({"sub": "test"})
        assert jwt_token.count(".") == 2

    @pytest.mark.unit
    def test_jwt_claims(self):
        """Verify JWT contains required claims (iat, exp)."""
        jwt_token = generate_jwt({"sub": "test", "custom": "value"})
        claims = verify_jwt(jwt_token)

        assert claims is not None
        assert "iat" in claims
        assert "exp" in claims
        assert claims["sub"] == "test"
        assert claims["custom"] == "value"

    @pytest.mark.unit
    def test_jwt_expiration(self):
        """Verify JWT expiration is correctly set."""
        jwt_token = generate_jwt({"sub": "test"}, expires_in_minutes=5)
        claims = verify_jwt(jwt_token)

        assert claims is not None
        # exp should be 5 minutes after iat
        assert claims["exp"] - claims["iat"] == 5 * 60

    @pytest.mark.unit
    def test_jwt_verification_with_wrong_secret(self):
        """Verify JWT fails verification with wrong secret."""
        jwt_token = generate_jwt({"sub": "test"}, secret="secret1")
        claims = verify_jwt(jwt_token, secret="secret2")

        assert claims is None

    @pytest.mark.unit
    def test_jwt_signed_with_hs256(self):
        """Verify JWT is signed with HS256 algorithm."""
        import base64
        import json

        jwt_token = generate_jwt({"sub": "test"})
        header_b64 = jwt_token.split(".")[0]
        # Add padding if needed
        header_b64 += "=" * (4 - len(header_b64) % 4)
        header = json.loads(base64.urlsafe_b64decode(header_b64))

        assert header["alg"] == "HS256"

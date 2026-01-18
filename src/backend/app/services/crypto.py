"""Cryptographic utilities for secure token handling."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from cryptography.fernet import Fernet

from app.config import get_settings


def generate_session_token() -> str:
    """Generate a cryptographically secure session token.

    Returns:
        A 32-byte hex-encoded token (64 characters).
    """
    return secrets.token_hex(32)


def hash_token(token: str) -> str:
    """Hash a token using SHA-256 for secure storage.

    Args:
        token: The token to hash.

    Returns:
        The SHA-256 hash of the token as a hex string.
    """
    return hashlib.sha256(token.encode()).hexdigest()


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook HMAC-SHA256 signature.

    Uses constant-time comparison to prevent timing attacks.

    Args:
        payload: The raw request body bytes.
        signature: The X-Hub-Signature-256 header value (sha256=...).
        secret: The webhook secret key.

    Returns:
        True if signature is valid, False otherwise.
    """
    if not signature.startswith("sha256="):
        return False

    expected_signature = (
        "sha256="
        + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
    )

    return hmac.compare_digest(signature, expected_signature)


def compute_webhook_signature(payload: bytes, secret: str) -> str:
    """Compute HMAC-SHA256 signature for a webhook payload.

    Args:
        payload: The raw request body bytes.
        secret: The webhook secret key.

    Returns:
        The signature in format 'sha256=<hex_digest>'.
    """
    return (
        "sha256="
        + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
    )


def generate_jwt(
    payload: dict,
    secret: str | None = None,
    expires_in_minutes: int = 10,
) -> str:
    """Generate a JWT token.

    Args:
        payload: The claims to include in the token.
        secret: The secret key for signing. Defaults to session_secret_key.
        expires_in_minutes: Token expiry in minutes.

    Returns:
        The encoded JWT string.
    """
    if secret is None:
        secret = get_settings().session_secret_key

    now = datetime.now(UTC)
    claims = {
        **payload,
        "iat": now,
        "exp": now + timedelta(minutes=expires_in_minutes),
    }
    return jwt.encode(claims, secret, algorithm="HS256")


def verify_jwt(token: str, secret: str | None = None) -> dict | None:
    """Verify and decode a JWT token.

    Args:
        token: The JWT token to verify.
        secret: The secret key for verification. Defaults to session_secret_key.

    Returns:
        The decoded payload if valid, None if invalid or expired.
    """
    if secret is None:
        secret = get_settings().session_secret_key

    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return None


def generate_encryption_key() -> bytes:
    """Generate a new Fernet encryption key.

    Returns:
        A URL-safe base64-encoded 32-byte key.
    """
    return Fernet.generate_key()


def encrypt_token(token: str, key: bytes) -> str:
    """Encrypt a token using Fernet symmetric encryption.

    Args:
        token: The plaintext token to encrypt.
        key: The Fernet encryption key.

    Returns:
        The encrypted token as a UTF-8 string.
    """
    f = Fernet(key)
    return f.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str, key: bytes) -> str:
    """Decrypt a Fernet-encrypted token.

    Args:
        encrypted_token: The encrypted token string.
        key: The Fernet encryption key.

    Returns:
        The decrypted plaintext token.

    Raises:
        cryptography.fernet.InvalidToken: If decryption fails.
    """
    f = Fernet(key)
    return f.decrypt(encrypted_token.encode()).decode()

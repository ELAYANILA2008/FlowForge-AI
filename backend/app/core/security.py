"""Security, authentication, and cryptographic utility functions.

Implements:
1. NIST-approved PBKDF2-HMAC-SHA256 password hashing with random salt.
2. Production-safe HMAC-SHA256 JWT access token creation and decoding.
3. Cryptographically secure random identifier and reference token generation.
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.exceptions import AuthenticationException


# ── Password Hashing (PBKDF2-HMAC-SHA256) ──────────────────────────────────

PBKDF2_ITERATIONS = 200_000
SALT_BYTES = 16


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using PBKDF2-HMAC-SHA256 with a unique random salt."""
    salt = secrets.token_hex(SALT_BYTES)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt}${derived_key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify that a plaintext password matches the stored PBKDF2 hash."""
    if not hashed_password or not plain_password:
        return False

    parts = hashed_password.split("$")
    if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
        return False

    try:
        iterations = int(parts[1])
        salt = parts[2]
        expected_hex = parts[3]

        actual_key = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return secrets.compare_digest(actual_key.hex(), expected_hex)
    except Exception:
        return False


# ── JWT Token Generation & Verification (HS256) ────────────────────────────

def _b64url_encode(data: bytes) -> str:
    """Encode bytes to base64url string without trailing padding '='."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    """Decode base64url string with automatic padding restoration."""
    padding = len(data) % 4
    if padding > 0:
        data += "=" * (4 - padding)
    return base64.urlsafe_b64decode(data.encode("utf-8"))


def create_access_token(
    subject: str,
    claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token for authentication."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if claims:
        payload.update(claims)

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    return f"{header_b64}.{payload_b64}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> Dict[str, Any]:
    """Validate and decode a signed JWT token.
    
    Raises:
        AuthenticationException if token is malformed, has invalid signature, or is expired.
    """
    if not token or not isinstance(token, str):
        raise AuthenticationException("Invalid or missing token")

    parts = token.split(".")
    if len(parts) != 3:
        raise AuthenticationException("Malformed authorization token structure")

    header_b64, payload_b64, signature_b64 = parts

    # Verify signature
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    try:
        provided_sig = _b64url_decode(signature_b64)
    except Exception:
        raise AuthenticationException("Invalid token signature encoding")

    if not secrets.compare_digest(provided_sig, expected_sig):
        raise AuthenticationException("Token signature verification failed")

    # Decode and check claims
    try:
        payload_bytes = _b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        raise AuthenticationException("Unable to parse token claims")

    exp = payload.get("exp")
    if exp is not None:
        if int(time.time()) > int(exp):
            raise AuthenticationException("Authorization token has expired")

    return payload


# ── Idempotency & Reference Generators ──────────────────────────────────────

def generate_reference_id(prefix: str = "TXN") -> str:
    """Generate a high-entropy, human-readable reference identifier."""
    random_part = secrets.token_hex(4).upper()
    timestamp_part = int(time.time() * 1000) % 1_000_000
    return f"{prefix}-{timestamp_part}-{random_part}"


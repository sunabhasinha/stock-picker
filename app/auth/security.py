"""
Security primitives (ADR-0006). Small on purpose: argon2id for passwords,
os-random opaque tokens hashed with sha256 at rest, and a dummy hash so
login latency does not reveal whether an email exists.
"""

from __future__ import annotations

import hashlib
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

_hasher = PasswordHasher()  # argon2id with library-maintained parameters

#: verified against when the email is UNKNOWN, so unknown-vs-wrong-password
#: take the same time (no user-enumeration timing oracle - spec clause 6).
_DUMMY_HASH = _hasher.hash("timing-uniformity-dummy-password")

MIN_PASSWORD_LENGTH = 10  # length over composition rules (NIST 800-63B)


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """False on any failure; ALWAYS performs one argon2 verification."""
    try:
        return _hasher.verify(password_hash or _DUMMY_HASH, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def generate_token() -> tuple[str, str]:
    """(cleartext-for-the-user, sha256-hex-for-the-database). 256-bit."""
    token = secrets.token_urlsafe(32)
    return token, hash_token(token)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def password_policy_error(password: str) -> str | None:
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"password must be at least {MIN_PASSWORD_LENGTH} characters"
    return None

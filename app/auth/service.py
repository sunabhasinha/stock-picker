"""
The auth flows (spec: docs/specs/auth-layer.md; ADR-0006).

Every public method returns a uniform result: AuthError carries one
generic, non-oracular message - callers (the HTTP layer) map ANY failure
to the same 401 shape. Specific reasons exist only in this module's
control flow, never in responses or logs.

Runs as the owner role (pre-authentication code path); user-DATA access
elsewhere runs under the app_rls role + SET LOCAL app.user_id (see
app/db/session.py::rls_transaction).
"""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.emailer import EmailTransport
from app.auth.security import (
    generate_token,
    hash_password,
    hash_token,
    password_policy_error,
    verify_password,
)
from app.db.models import AuthSession, AuthToken, LoginAttempt, User, utcnow

# Documented tunables (spec leaves them to the implementer; recorded here
# and in app/MODULE.md):
SESSION_TTL = dt.timedelta(days=7)
VERIFY_TOKEN_TTL = dt.timedelta(hours=24)
RESET_TOKEN_TTL = dt.timedelta(hours=1)
THROTTLE_WINDOW = dt.timedelta(minutes=15)
MAX_FAILURES_PER_EMAIL = 5
MAX_FAILURES_PER_IP = 20

GENERIC_AUTH_FAILURE = "authentication failed"
GENERIC_FLOW_RESPONSE = (
    "if that email is registered, a link has been sent to it"
)


class AuthError(Exception):
    """Single generic error for every authentication failure path."""

    def __init__(self, message: str = GENERIC_AUTH_FAILURE):
        super().__init__(message)


def _as_utc(value: dt.datetime) -> dt.datetime:
    """SQLite returns naive datetimes; they were stored as UTC."""
    return value if value.tzinfo else value.replace(tzinfo=dt.timezone.utc)


class AuthService:
    def __init__(self, session: Session, emailer: EmailTransport,
                 base_url: str = "http://127.0.0.1:8000"):
        self.db = session
        self.emailer = emailer
        self.base_url = base_url.rstrip("/")

    # -- registration and verification ----------------------------------

    def register(self, email: str, password: str) -> None:
        """Uniform outcome by design: whether the email is new or already
        registered, the caller sees the same acceptance (no enumeration).
        A policy-violating password is the only distinguishable error -
        that reveals nothing about accounts."""
        email = email.strip().lower()
        if (error := password_policy_error(password)) is not None:
            raise ValueError(error)

        existing = self.db.scalar(select(User).where(User.email == email))
        if existing is not None:
            return  # same 202 upstream; no second account, no hint

        user = User(email=email, password_hash=hash_password(password))
        self.db.add(user)
        self.db.flush()
        self._send_flow_token(
            user, "verify_email", VERIFY_TOKEN_TTL,
            subject="Verify your email",
            path="/verify",  # the SPA page (it calls the API); friendlier
            # landing than raw JSON - falls back gracefully via SPA routing
        )

    def verify_email(self, token: str) -> None:
        record = self._consume_token(token, "verify_email")
        user = self.db.get(User, record.user_id)
        user.email_verified_at = utcnow()
        self.db.flush()

    # -- login / logout ---------------------------------------------------

    def login(self, email: str, password: str, ip: str) -> str:
        """Returns the cleartext session token for the cookie. Every
        failure - unknown email, wrong password, unverified account,
        throttled - raises the SAME AuthError, and the argon2 verification
        always runs (timing uniformity)."""
        email = email.strip().lower()
        throttled = self._is_throttled(email, ip)

        user = self.db.scalar(select(User).where(User.email == email))
        password_ok = verify_password(
            password, user.password_hash if user else None
        )
        success = (
            not throttled
            and user is not None
            and password_ok
            and user.email_verified_at is not None
        )

        self.db.add(LoginAttempt(email=email, ip=ip, success=success))
        self.db.flush()
        if not success:
            # COMMIT before raising: the caller's transaction management
            # rolls back on error, and a rolled-back attempt would mean
            # failed logins never accumulate - throttling would be dead
            # code. The ledger must survive the very failures it counts.
            self.db.commit()
            raise AuthError()

        token, token_hash = generate_token()
        self.db.add(AuthSession(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=utcnow() + SESSION_TTL,
        ))
        self.db.flush()
        return token

    def logout(self, token: str) -> None:
        """Server-side revocation - the dying cookie is not the mechanism."""
        record = self.db.scalar(
            select(AuthSession).where(AuthSession.token_hash == hash_token(token))
        )
        if record is not None and record.revoked_at is None:
            record.revoked_at = utcnow()
            self.db.flush()

    def user_for_session(self, token: str) -> User:
        """The ONLY way a request acquires an identity (spec clause 3)."""
        record = self.db.scalar(
            select(AuthSession).where(AuthSession.token_hash == hash_token(token))
        )
        now = utcnow()
        if (
            record is None
            or record.revoked_at is not None
            or _as_utc(record.expires_at) <= now
        ):
            raise AuthError()
        user = self.db.get(User, record.user_id)
        if user is None or user.email_verified_at is None:
            raise AuthError()
        return user

    # -- password reset ----------------------------------------------------

    def request_password_reset(self, email: str) -> None:
        """Uniform outcome whether or not the account exists."""
        email = email.strip().lower()
        user = self.db.scalar(select(User).where(User.email == email))
        if user is None or user.password_hash is None:
            return
        self._send_flow_token(
            user, "reset_password", RESET_TOKEN_TTL,
            subject="Reset your password",
            path="/reset",  # SPA page with the new-password form
        )

    def confirm_password_reset(self, token: str, new_password: str) -> None:
        if (error := password_policy_error(new_password)) is not None:
            raise ValueError(error)
        record = self._consume_token(token, "reset_password")
        user = self.db.get(User, record.user_id)
        user.password_hash = hash_password(new_password)
        self._revoke_all_sessions(user.id)  # spec: reset kills every session
        self.db.flush()

    def change_password(self, user: User, current: str, new_password: str) -> None:
        if not verify_password(current, user.password_hash):
            raise AuthError()
        if (error := password_policy_error(new_password)) is not None:
            raise ValueError(error)
        user.password_hash = hash_password(new_password)
        self._revoke_all_sessions(user.id)
        self.db.flush()

    # -- internals ----------------------------------------------------------

    def _send_flow_token(self, user: User, purpose: str, ttl: dt.timedelta,
                         subject: str, path: str) -> None:
        token, token_hash = generate_token()
        self.db.add(AuthToken(
            user_id=user.id, purpose=purpose, token_hash=token_hash,
            expires_at=utcnow() + ttl,
        ))
        self.db.flush()
        self.emailer.send(
            to=user.email,
            subject=subject,
            body=f"Open this link: {self.base_url}{path}?token={token}",
        )

    def _consume_token(self, token: str, purpose: str) -> AuthToken:
        """Single-use enforcement: valid exactly once, then used_at set."""
        record = self.db.scalar(
            select(AuthToken).where(AuthToken.token_hash == hash_token(token))
        )
        if (
            record is None
            or record.purpose != purpose
            or record.used_at is not None
            or _as_utc(record.expires_at) <= utcnow()
        ):
            raise AuthError()
        record.used_at = utcnow()
        self.db.flush()
        return record

    def _revoke_all_sessions(self, user_id: uuid.UUID) -> None:
        for record in self.db.scalars(
            select(AuthSession).where(
                AuthSession.user_id == user_id,
                AuthSession.revoked_at.is_(None),
            )
        ):
            record.revoked_at = utcnow()

    def _is_throttled(self, email: str, ip: str) -> bool:
        cutoff = utcnow() - THROTTLE_WINDOW
        email_failures = self.db.scalar(
            select(func.count()).select_from(LoginAttempt).where(
                LoginAttempt.email == email,
                LoginAttempt.success.is_(False),
                LoginAttempt.created_at > cutoff,
            )
        )
        ip_failures = self.db.scalar(
            select(func.count()).select_from(LoginAttempt).where(
                LoginAttempt.ip == ip,
                LoginAttempt.success.is_(False),
                LoginAttempt.created_at > cutoff,
            )
        )
        return (email_failures >= MAX_FAILURES_PER_EMAIL
                or ip_failures >= MAX_FAILURES_PER_IP)

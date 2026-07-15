"""
Tests for the M2 auth layer (spec: docs/specs/auth-layer.md; ADR-0006).

Every acceptance criterion in the spec's security model appears here as
an automated gate: the full register->verify->login lifecycle, uniform
401s, single-use tokens, server-side revocation, throttling lockout,
cookie flags, origin checks, and the CROSS-USER test at the API layer.
The RLS (database) layer of the cross-user test requires real Postgres
and is gated on TEST_DATABASE_URL (runs locally against Supabase; skips
on SQLite/CI - same unit-vs-live layering as the rest of the suite).

Flow tokens are captured from the ConsoleEmailTransport outbox - the
pluggable dev transport exists precisely so these flows are testable
with no email vendor.
"""

import re
import unittest

try:
    import sqlalchemy  # noqa: F401
    import fastapi  # noqa: F401
    import httpx  # noqa: F401
    import argon2  # noqa: F401
    HAS_SHELL_DEPS = True
except ImportError:
    HAS_SHELL_DEPS = False


def make_client_and_outbox():
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.auth.emailer import ConsoleEmailTransport
    from app.db.models import Base
    from app.server import create_app

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    emailer = ConsoleEmailTransport()
    app = create_app(session_factory=factory, emailer=emailer)
    return TestClient(app), emailer, factory


def last_token(emailer) -> str:
    body = emailer.outbox[-1][2]
    return re.search(r"token=([A-Za-z0-9_\-]+)", body).group(1)


@unittest.skipUnless(HAS_SHELL_DEPS, "shell deps not installed (app/requirements.txt)")
class AuthTestCase(unittest.TestCase):
    EMAIL = "user@example.com"
    PASSWORD = "correct-horse-battery"

    def setUp(self):
        self.client, self.emailer, self.factory = make_client_and_outbox()

    def register_and_verify(self, email=None, password=None):
        email, password = email or self.EMAIL, password or self.PASSWORD
        response = self.client.post("/auth/register",
                                    json={"email": email, "password": password})
        self.assertEqual(response.status_code, 202)
        response = self.client.get(f"/auth/verify?token={last_token(self.emailer)}")
        self.assertEqual(response.status_code, 200)

    def login(self, email=None, password=None):
        return self.client.post("/auth/login", json={
            "email": email or self.EMAIL, "password": password or self.PASSWORD,
        })


class TestRegistrationAndLogin(AuthTestCase):
    def test_full_lifecycle_register_verify_login_me(self):
        self.client.post("/auth/register",
                         json={"email": self.EMAIL, "password": self.PASSWORD})
        # Spec: unverified users cannot log in
        self.assertEqual(self.login().status_code, 401)

        self.client.get(f"/auth/verify?token={last_token(self.emailer)}")
        response = self.login()
        self.assertEqual(response.status_code, 204)
        me = self.client.get("/api/me")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], self.EMAIL)

    def test_session_cookie_flags(self):
        self.register_and_verify()
        set_cookie = self.login().headers["set-cookie"].lower()
        self.assertIn("httponly", set_cookie)
        self.assertIn("samesite=lax", set_cookie)

    def test_duplicate_registration_is_indistinguishable(self):
        # Enumeration resistance: same 202, and no second email goes out.
        self.register_and_verify()
        sent_before = len(self.emailer.outbox)
        response = self.client.post(
            "/auth/register",
            json={"email": self.EMAIL, "password": "another-password-1"})
        self.assertEqual(response.status_code, 202)
        self.assertEqual(len(self.emailer.outbox), sent_before)

    def test_password_policy_is_the_only_distinguishable_error(self):
        response = self.client.post("/auth/register",
                                    json={"email": "x@y.com", "password": "short"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("at least", response.json()["detail"])

    def test_uniform_401_for_every_failure_mode(self):
        # Unknown email, wrong password, unverified account: identical
        # status AND identical body - no oracle (spec clause 6).
        self.client.post("/auth/register",
                         json={"email": "unverified@example.com",
                               "password": self.PASSWORD})
        self.register_and_verify()
        responses = [
            self.login(email="nobody@example.com"),
            self.login(password="wrong-password-123"),
            self.login(email="unverified@example.com"),
        ]
        self.assertEqual([r.status_code for r in responses], [401, 401, 401])
        self.assertEqual(len({r.text for r in responses}), 1)


class TestSessions(AuthTestCase):
    def test_logout_revokes_server_side(self):
        self.register_and_verify()
        self.login()
        self.assertEqual(self.client.get("/api/me").status_code, 200)
        self.client.post("/auth/logout")
        self.assertEqual(self.client.get("/api/me").status_code, 401)

    def test_password_change_revokes_every_session(self):
        self.register_and_verify()
        self.login()
        response = self.client.post("/api/password", json={
            "current_password": self.PASSWORD,
            "new_password": "a-brand-new-password",
        })
        self.assertEqual(response.status_code, 204)
        # The session that made the change is dead too
        self.assertEqual(self.client.get("/api/me").status_code, 401)
        # And the new password is the one that works
        self.assertEqual(self.login().status_code, 401)
        self.assertEqual(self.login(password="a-brand-new-password").status_code, 204)

    def test_unauthenticated_api_is_a_single_shape_401(self):
        for path in ("/api/me", "/api/portfolios"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json(), {"detail": "authentication failed"})


class TestFlowTokens(AuthTestCase):
    def test_verification_token_is_single_use(self):
        self.client.post("/auth/register",
                         json={"email": self.EMAIL, "password": self.PASSWORD})
        token = last_token(self.emailer)
        self.assertEqual(self.client.get(f"/auth/verify?token={token}").status_code, 200)
        self.assertEqual(self.client.get(f"/auth/verify?token={token}").status_code, 401)

    def test_password_reset_flow_and_session_revocation(self):
        self.register_and_verify()
        self.login()
        # Unknown email gets the same 202 (no enumeration)
        unknown = self.client.post("/auth/password-reset/request",
                                   json={"email": "ghost@example.com"})
        known = self.client.post("/auth/password-reset/request",
                                 json={"email": self.EMAIL})
        self.assertEqual((unknown.status_code, known.status_code), (202, 202))
        self.assertEqual(unknown.json(), known.json())

        token = last_token(self.emailer)
        response = self.client.post("/auth/password-reset/confirm", json={
            "token": token, "new_password": "after-reset-password",
        })
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get("/api/me").status_code, 401)  # revoked
        self.assertEqual(self.login(password="after-reset-password").status_code, 204)
        # Reset token is single-use too
        retry = self.client.post("/auth/password-reset/confirm", json={
            "token": token, "new_password": "yet-another-password",
        })
        self.assertEqual(retry.status_code, 401)


class TestThrottling(AuthTestCase):
    def test_lockout_after_repeated_failures_with_uniform_response(self):
        from app.auth.service import MAX_FAILURES_PER_EMAIL

        self.register_and_verify()
        for _ in range(MAX_FAILURES_PER_EMAIL):
            self.assertEqual(self.login(password="wrong-password-123").status_code, 401)
        # Now even the CORRECT password fails, with the same body
        locked = self.login()
        self.assertEqual(locked.status_code, 401)
        self.assertEqual(locked.json(), {"detail": "authentication failed"})


class TestCrossUserIsolation(AuthTestCase):
    def test_users_cannot_see_each_others_portfolios_via_api(self):
        # THE acceptance gate (spec): two users, cross-access must fail.
        self.register_and_verify("alice@example.com", "alice-password-1")
        self.login("alice@example.com", "alice-password-1")
        created = self.client.post("/api/portfolios", json={
            "name": "alice-main", "category_key": "category_2",
        })
        self.assertEqual(created.status_code, 201)

        self.client.post("/auth/logout")
        self.register_and_verify("bob@example.com", "bob-password-12")
        self.login("bob@example.com", "bob-password-12")
        bobs_view = self.client.get("/api/portfolios").json()
        self.assertEqual(bobs_view, [])  # layer 1: app-level scoping

    def test_portfolio_category_must_be_a_real_preset(self):
        self.register_and_verify()
        self.login()
        response = self.client.post("/api/portfolios", json={
            "name": "x", "category_key": "category_99",
        })
        self.assertEqual(response.status_code, 400)


class TestOriginCheck(AuthTestCase):
    def test_cross_origin_state_change_is_rejected(self):
        response = self.client.post(
            "/auth/login",
            json={"email": self.EMAIL, "password": self.PASSWORD},
            headers={"Origin": "https://evil.example.com"},
        )
        self.assertEqual(response.status_code, 403)

    def test_same_origin_is_allowed(self):
        self.register_and_verify()
        response = self.client.post(
            "/auth/login",
            json={"email": self.EMAIL, "password": self.PASSWORD},
            headers={"Origin": "http://127.0.0.1:8000"},
        )
        self.assertEqual(response.status_code, 204)

    def test_localhost_and_loopback_are_the_same_origin(self):
        # Found live: base_url says 127.0.0.1 but users legitimately browse
        # localhost - same machine, same port, must not be 403'd.
        self.register_and_verify()
        response = self.client.post(
            "/auth/login",
            json={"email": self.EMAIL, "password": self.PASSWORD},
            headers={"Origin": "http://localhost:8000"},
        )
        self.assertEqual(response.status_code, 204)


class TestNoSecretsInResponses(AuthTestCase):
    def test_no_hash_or_token_material_leaks_through_the_api(self):
        self.register_and_verify()
        self.login()
        me = self.client.get("/api/me")
        text = me.text.lower()
        self.assertNotIn("password", text)
        self.assertNotIn("hash", text)
        self.assertNotIn("$argon2", me.text)


@unittest.skipUnless(HAS_SHELL_DEPS, "shell deps not installed")
class TestSPAServing(AuthTestCase):
    """ADR-0007: FastAPI serves the built React app same-origin. Skips
    when frontend/dist hasn't been built (CI's frontend job builds it)."""

    def setUp(self):
        from app.server import FRONTEND_DIST
        if not FRONTEND_DIST.exists():
            self.skipTest("frontend/dist not built (run: cd frontend && npm run build)")
        super().setUp()

    def test_spa_routes_serve_index_html(self):
        for path in ("/", "/login", "/register", "/verify", "/reset"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn("text/html", response.headers["content-type"])
            self.assertIn(b'<div id="root">', response.content)

    def test_unknown_api_paths_stay_json_404(self):
        response = self.client.get("/api/definitely-not-a-route")
        self.assertEqual(response.status_code, 404)
        self.assertIn("application/json", response.headers["content-type"])


@unittest.skipUnless(HAS_SHELL_DEPS, "shell deps not installed")
class TestRLSLayerOnPostgres(unittest.TestCase):
    """Layer 2 of the cross-user gate: RLS itself, under the app_rls role.
    Needs a real Postgres with migrations applied - gated on
    TEST_DATABASE_URL; skips on CI/SQLite by design."""

    def test_rls_blocks_cross_user_reads_under_app_role(self):
        import os
        url = os.environ.get("TEST_DATABASE_URL")
        if not url:
            self.skipTest("TEST_DATABASE_URL not set (run locally vs Postgres)")

        import uuid
        from sqlalchemy import select

        from app.db.models import Portfolio, User
        from app.db.repository import Repository
        from app.db.session import make_session_factory, rls_transaction

        factory = make_session_factory(url)
        setup = factory()
        alice = User(email=f"rls-alice-{uuid.uuid4().hex[:8]}@t.local")
        bob = User(email=f"rls-bob-{uuid.uuid4().hex[:8]}@t.local")
        setup.add_all([alice, bob])
        setup.flush()
        Repository(setup).create_portfolio(alice.id, "alice-p", "category_1")
        setup.commit()

        try:
            with rls_transaction(factory, bob.id) as session:
                visible = session.scalars(select(Portfolio)).all()
                self.assertTrue(all(p.user_id != alice.id for p in visible),
                                "RLS must hide alice's rows from bob")
            with rls_transaction(factory, alice.id) as session:
                names = [p.name for p in session.scalars(select(Portfolio))]
                self.assertIn("alice-p", names)
        finally:
            cleanup = factory()
            for user in (alice, bob):
                cleanup.execute(
                    Portfolio.__table__.delete().where(Portfolio.user_id == user.id))
                cleanup.execute(User.__table__.delete().where(User.id == user.id))
            cleanup.commit()


if __name__ == "__main__":
    unittest.main()

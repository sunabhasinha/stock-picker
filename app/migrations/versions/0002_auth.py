"""M2 auth: password/verification columns, sessions, flow tokens,
throttling ledger, and the RLS-bound application role.

Role model (ADR-0006 clause 4, refined): `app_rls` is a NOLOGIN role - it
has no password to manage or leak. The shell connects with its normal
credentials and assumes the role per transaction via SET LOCAL ROLE,
which auto-reverts at transaction end. Because app_rls does not own the
tables, the M1 RLS policies BIND for it; least-privilege grants below
give it exactly the user-data tables and nothing else. The auth flow
tables (sessions/auth_tokens/login_attempts) get RLS enabled with NO
policies for app_rls - deny-all: only the owner-role auth service (pre-
authentication code paths) touches them.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

USER_DATA_TABLES = ("users", "portfolios", "holdings", "signal_events",
                    "scan_runs", "shadow_signals")
AUTH_TABLES = ("sessions", "auth_tokens", "login_attempts")


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(256)))
    op.add_column("users", sa.Column("email_verified_at",
                                     sa.DateTime(timezone=True)))

    op.create_table(
        "sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True),
                  sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )

    op.create_table(
        "auth_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True),
                  sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("purpose", sa.String(20), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("purpose IN ('verify_email', 'reset_password')",
                           name="auth_tokens_purpose_valid"),
    )

    op.create_table(
        "login_attempts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("ip", sa.String(64), nullable=False),
        sa.Column("success", sa.Boolean, nullable=False,
                  server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("ix_login_attempts_email_created", "login_attempts",
                    ["email", "created_at"])
    op.create_index("ix_login_attempts_ip_created", "login_attempts",
                    ["ip", "created_at"])

    # --- the RLS-bound application role (no password: NOLOGIN, assumed
    # per transaction with SET LOCAL ROLE) ------------------------------
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_rls') THEN
                CREATE ROLE app_rls NOLOGIN;
            END IF;
        END $$
    """)
    # Guarded: on Supabase the bare GRANT was observed to drop the pooled
    # connection (its role-management layer reacts to membership changes on
    # the postgres role). Idempotent + skipped when membership already
    # exists (e.g. granted once via the dashboard SQL editor).
    op.execute("""
        DO $$ BEGIN
            IF NOT pg_has_role(CURRENT_USER, 'app_rls', 'MEMBER') THEN
                GRANT app_rls TO CURRENT_USER;
            END IF;
        END $$
    """)
    op.execute("GRANT USAGE ON SCHEMA public TO app_rls")
    for table in USER_DATA_TABLES:
        op.execute(
            f"GRANT SELECT, INSERT, UPDATE, DELETE ON {table} TO app_rls"
        )

    # Auth tables: RLS on, and deliberately NO policies for app_rls ->
    # deny-all. Only the owner-role auth service reads/writes these.
    for table in AUTH_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    for table in ("login_attempts", "auth_tokens", "sessions"):
        op.drop_table(table)
    op.drop_column("users", "email_verified_at")
    op.drop_column("users", "password_hash")
    op.execute("DROP ROLE IF EXISTS app_rls")

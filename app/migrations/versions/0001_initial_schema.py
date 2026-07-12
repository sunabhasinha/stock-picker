"""Initial schema: users, portfolios, holdings, signal_events, scan_runs,
shadow_signals — with row-level security from day one and the single
seeded local user (spec: docs/specs/user-data-layer.md; ADR-0005).

RLS note: policies key off `current_setting('app.user_id', true)` so they
work on ANY Postgres (local dev included), not only Supabase. When M2
introduces Supabase Auth, a follow-up migration swaps the predicate to
`auth.uid()` — recorded here so nobody mistakes the current form for the
final one. Until then the application sets `app.user_id` per connection.

Revision ID: 0001
Revises:
Create Date: 2026-07-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

LOCAL_USER_ID = "00000000-0000-4000-8000-000000000001"

#: table -> SQL predicate identifying the owning user for RLS
_OWNERSHIP = {
    "portfolios": "user_id = current_setting('app.user_id', true)::uuid",
    "holdings": (
        "portfolio_id IN (SELECT id FROM portfolios "
        "WHERE user_id = current_setting('app.user_id', true)::uuid)"
    ),
    "signal_events": (
        "portfolio_id IN (SELECT id FROM portfolios "
        "WHERE user_id = current_setting('app.user_id', true)::uuid)"
    ),
    "scan_runs": (
        "portfolio_id IN (SELECT id FROM portfolios "
        "WHERE user_id = current_setting('app.user_id', true)::uuid)"
    ),
    "shadow_signals": (
        "portfolio_id IN (SELECT id FROM portfolios "
        "WHERE user_id = current_setting('app.user_id', true)::uuid)"
    ),
}


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(320), unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    op.create_table(
        "portfolios",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True),
                  sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("category_key", sa.String(40), nullable=False),
        sa.Column("commitment_started_on", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.UniqueConstraint("user_id", "name"),
    )

    op.create_table(
        "holdings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("portfolio_id", UUID(as_uuid=True),
                  sa.ForeignKey("portfolios.id"), nullable=False, index=True),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("average_cost", sa.Float, nullable=False),
        sa.Column("open_trades", JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.UniqueConstraint("portfolio_id", "symbol"),
    )

    op.create_table(
        "scan_runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("portfolio_id", UUID(as_uuid=True),
                  sa.ForeignKey("portfolios.id"), nullable=False, index=True),
        sa.Column("category_key", sa.String(40), nullable=False),
        sa.Column("as_of", sa.Date, nullable=False),
        sa.Column("scanned_symbols", JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("errors", JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )

    op.create_table(
        "signal_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("portfolio_id", UUID(as_uuid=True),
                  sa.ForeignKey("portfolios.id"), nullable=False, index=True),
        sa.Column("scan_run_id", UUID(as_uuid=True), sa.ForeignKey("scan_runs.id")),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("strategy", sa.String(80), nullable=False),
        sa.Column("action", sa.String(16), nullable=False),
        sa.Column("signal", JSONB, nullable=False),
        sa.Column("response", sa.String(16), nullable=False,
                  server_default="pending"),
        sa.Column("responded_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.CheckConstraint("response IN ('pending', 'confirmed', 'dismissed')",
                           name="signal_events_response_valid"),
    )
    op.create_index("ix_signal_events_portfolio_created", "signal_events",
                    ["portfolio_id", "created_at"])

    op.create_table(
        "shadow_signals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("portfolio_id", UUID(as_uuid=True),
                  sa.ForeignKey("portfolios.id"), nullable=False, index=True),
        sa.Column("category_key", sa.String(40), nullable=False),
        sa.Column("as_of", sa.Date, nullable=False),
        sa.Column("signals", JSONB, nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
    )
    op.create_index("ix_shadow_signals_portfolio_asof", "shadow_signals",
                    ["portfolio_id", "as_of"])

    # --- Row-level security from day one (spec invariant) -------------------
    for table, predicate in _OWNERSHIP.items():
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY {table}_owner ON {table} "
            f"USING ({predicate}) WITH CHECK ({predicate})"
        )
    # users: a user sees only their own row
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.execute(
        "CREATE POLICY users_self ON users "
        "USING (id = current_setting('app.user_id', true)::uuid)"
    )

    # --- The M1 seeded single user (spec: RLS bound to one local user) ------
    op.execute(
        f"INSERT INTO users (id, email) "
        f"VALUES ('{LOCAL_USER_ID}', 'local@localhost')"
    )


def downgrade() -> None:
    for table in ("shadow_signals", "signal_events", "scan_runs",
                  "holdings", "portfolios", "users"):
        op.drop_table(table)

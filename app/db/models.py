"""
ORM models for the user data layer (spec: docs/specs/user-data-layer.md).

Shapes come from the course rules, not generic SaaS patterns:
- a portfolio carries exactly ONE category key + commitment start date
  (KB Section 6.3's pick-one-for-a-year rule made structural); a user may
  hold several portfolios, each sized independently (Section 6.4);
- signal_events make the ADR-0003 human-confirmation boundary structural:
  the engine's signal is stored as an immutable snapshot, and the user's
  response (pending/confirmed/dismissed) is the ONLY thing that changes;
- shadow_signals persist what the non-selected categories would have
  signalled (Section 6.3's recommended comparison feature).

JSON columns are declared as generic JSON with a JSONB variant on
Postgres - the spec mandates JSONB in production while the test suite
runs against in-memory SQLite (see tests/test_app_db.py for why).
"""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Uuid,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON

JSONType = JSON().with_variant(JSONB(), "postgresql")

#: The single seeded user of milestone 1 (spec: RLS exists from day one,
#: bound to one local user until M2 brings real auth). Fixed UUID so the
#: migration seed and the repository agree without coordination.
LOCAL_USER_ID = uuid.UUID("00000000-0000-4000-8000-000000000001")

SIGNAL_RESPONSES = ("pending", "confirmed", "dismissed")


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str | None] = mapped_column(String(320), unique=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Portfolio(Base):
    __tablename__ = "portfolios"
    __table_args__ = (UniqueConstraint("user_id", "name"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    #: exactly one committed category (Section 6.3) - switching categories
    #: is a new value + new commitment date, reviewed by a human, never a
    #: side effect.
    category_key: Mapped[str] = mapped_column(String(40))
    commitment_started_on: Mapped[dt.date] = mapped_column(Date)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Holding(Base):
    __tablename__ = "holdings"
    __table_args__ = (UniqueConstraint("portfolio_id", "symbol"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("portfolios.id"), index=True)
    symbol: Mapped[str] = mapped_column(String(32))
    average_cost: Mapped[float] = mapped_column(Float)
    #: open trades in the EXISTING positions-JSON trade shape
    #: (scan.positions_from_dict is the contract; storing the same dicts is
    #: what makes the round-trip lossless - recorded judgment call: trades
    #: are strategy-owned snapshots, so JSON, not a fourth table).
    open_trades: Mapped[list] = mapped_column(JSONType, default=list)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class SignalEvent(Base):
    __tablename__ = "signal_events"
    __table_args__ = (
        CheckConstraint(
            "response IN ('pending', 'confirmed', 'dismissed')",
            name="signal_events_response_valid",
        ),
        Index("ix_signal_events_portfolio_created", "portfolio_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("portfolios.id"), index=True)
    scan_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("scan_runs.id"))
    symbol: Mapped[str] = mapped_column(String(32))
    strategy: Mapped[str] = mapped_column(String(80))
    action: Mapped[str] = mapped_column(String(16))  # BUY / AVERAGE / SELL
    #: the full signal dict (web.signal_to_dict shape) - IMMUTABLE snapshot;
    #: only `response`/`responded_at` may ever change on this row.
    signal: Mapped[dict] = mapped_column(JSONType)
    response: Mapped[str] = mapped_column(String(16), default="pending")
    responded_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("portfolios.id"), index=True)
    category_key: Mapped[str] = mapped_column(String(40))
    as_of: Mapped[dt.date] = mapped_column(Date)
    scanned_symbols: Mapped[list] = mapped_column(JSONType, default=list)
    errors: Mapped[list] = mapped_column(JSONType, default=list)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ShadowSignal(Base):
    __tablename__ = "shadow_signals"
    __table_args__ = (
        Index("ix_shadow_signals_portfolio_asof", "portfolio_id", "as_of"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    portfolio_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("portfolios.id"), index=True)
    #: a NON-selected category and what it would have signalled that day -
    #: hypothetical by definition, never executable (Section 6.3).
    category_key: Mapped[str] = mapped_column(String(40))
    as_of: Mapped[dt.date] = mapped_column(Date)
    signals: Mapped[list] = mapped_column(JSONType, default=list)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

"""
The repository layer: the ONLY place the application shell touches the
database, and the only vocabulary the rest of the product uses to talk
about persistence.

Direction of dependency (ADR-0005): this module imports the engine's
types (Position, ScanReport, signal serialization) - the engine never
imports this. The positions-JSON shape (scan.positions_from_dict) is the
holdings contract; holdings round-trip through it losslessly (tested).

signal_events are append-only in spirit: the signal snapshot written at
insert time is immutable; respond_to_signal() touches only the response
and responded_at columns.
"""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    LOCAL_USER_ID,
    SIGNAL_RESPONSES,
    Holding,
    Portfolio,
    ScanRun,
    ShadowSignal,
    SignalEvent,
    User,
)
from sunabha_agent.data.models import Signal
from sunabha_agent.scan import Position, ScanReport
from sunabha_agent.web import signal_to_dict


class Repository:
    def __init__(self, session: Session):
        self.session = session

    # -- users / portfolios -------------------------------------------------

    def get_or_create_local_user(self) -> User:
        """Milestone 1 runs single-user: the fixed seeded identity that M2's
        real auth will replace (spec: RLS bound to one local user for now)."""
        user = self.session.get(User, LOCAL_USER_ID)
        if user is None:
            user = User(id=LOCAL_USER_ID, email="local@localhost")
            self.session.add(user)
            self.session.flush()
        return user

    def portfolios_for_user(self, user_id: uuid.UUID) -> list[Portfolio]:
        """Explicitly filtered by user_id (layer 1) even though RLS (layer
        2) would filter identically under app_rls - defense in depth means
        neither layer assumes the other."""
        return list(
            self.session.scalars(
                select(Portfolio)
                .where(Portfolio.user_id == user_id)
                .order_by(Portfolio.created_at)
            )
        )

    def create_portfolio(
        self,
        user_id: uuid.UUID,
        name: str,
        category_key: str,
        commitment_started_on: dt.date | None = None,
    ) -> Portfolio:
        portfolio = Portfolio(
            user_id=user_id,
            name=name,
            category_key=category_key,
            commitment_started_on=commitment_started_on or dt.date.today(),
        )
        self.session.add(portfolio)
        self.session.flush()
        return portfolio

    # -- holdings (positions-JSON contract) ---------------------------------

    def replace_holdings_from_positions(
        self, portfolio_id: uuid.UUID, positions: dict[str, Position]
    ) -> None:
        """Full sync from the existing in-memory Position shape. Trades are
        stored as the same dicts positions_from_dict consumes."""
        existing = {
            h.symbol: h
            for h in self.session.scalars(
                select(Holding).where(Holding.portfolio_id == portfolio_id)
            )
        }
        for symbol, position in positions.items():
            row = existing.pop(symbol.upper(), None)
            trades = [_trade_to_dict(t) for t in position.open_trades]
            if row is None:
                self.session.add(
                    Holding(
                        portfolio_id=portfolio_id,
                        symbol=symbol.upper(),
                        average_cost=position.average_cost,
                        open_trades=trades,
                    )
                )
            else:
                row.average_cost = position.average_cost
                row.open_trades = trades
        for stale in existing.values():
            self.session.delete(stale)
        self.session.flush()

    def positions_for(self, portfolio_id: uuid.UUID) -> dict[str, Position]:
        """The inverse: rows -> the exact dict scan.positions_from_dict
        produces, so DailyScanner consumes DB holdings unchanged."""
        from sunabha_agent.scan import positions_from_dict

        raw = {
            h.symbol: {"average_cost": h.average_cost, "open_trades": h.open_trades}
            for h in self.session.scalars(
                select(Holding).where(Holding.portfolio_id == portfolio_id)
            )
        }
        return positions_from_dict(raw)

    # -- scans and signals ---------------------------------------------------

    def record_scan(self, portfolio_id: uuid.UUID, report: ScanReport) -> ScanRun:
        """Persist a ScanReport: one scan_runs row + one signal_events row
        per signal (exits and candidates alike), response=pending."""
        run = ScanRun(
            portfolio_id=portfolio_id,
            category_key=report.category_key,
            as_of=report.as_of,
            scanned_symbols=list(report.scanned_symbols),
            errors=list(report.errors),
        )
        self.session.add(run)
        self.session.flush()

        for signal in [s for s, _ in report.ranked_candidates] + report.exit_signals:
            self.session.add(
                SignalEvent(
                    portfolio_id=portfolio_id,
                    scan_run_id=run.id,
                    symbol=signal.symbol,
                    strategy=signal.strategy_name,
                    action=signal.action,
                    signal=signal_to_dict(signal),
                )
            )
        self.session.flush()
        return run

    def respond_to_signal(self, event_id: uuid.UUID, response: str) -> SignalEvent:
        """The human-confirmation boundary (ADR-0003), structural: the ONLY
        mutation this layer permits on a signal event."""
        if response not in SIGNAL_RESPONSES:
            raise ValueError(f"response must be one of {SIGNAL_RESPONSES}")
        event = self.session.get(SignalEvent, event_id)
        if event is None:
            raise LookupError(f"no signal event {event_id}")
        event.response = response
        event.responded_at = dt.datetime.now(dt.timezone.utc)
        self.session.flush()
        return event

    def pending_signals(self, portfolio_id: uuid.UUID) -> list[SignalEvent]:
        return list(
            self.session.scalars(
                select(SignalEvent)
                .where(
                    SignalEvent.portfolio_id == portfolio_id,
                    SignalEvent.response == "pending",
                )
                .order_by(SignalEvent.created_at)
            )
        )

    # -- shadow tracking (Section 6.3) ---------------------------------------

    def record_shadow_signals(
        self,
        portfolio_id: uuid.UUID,
        as_of: dt.date,
        signals_by_category: dict[str, list[Signal]],
    ) -> None:
        for category_key, signals in signals_by_category.items():
            self.session.add(
                ShadowSignal(
                    portfolio_id=portfolio_id,
                    category_key=category_key,
                    as_of=as_of,
                    signals=[signal_to_dict(s) for s in signals],
                )
            )
        self.session.flush()


def _trade_to_dict(trade: Signal) -> dict:
    """A Signal representing an open trade -> the positions-JSON trade shape
    (the keys positions_from_dict reads back)."""
    return {
        "strategy_name": trade.strategy_name,
        "action": trade.action,
        "entry_price": trade.signal_price,
        "entry_date": trade.trigger_date.isoformat(),
        "target_price": trade.target_price,
        "metadata": dict(trade.metadata),
    }

# Module: strategies (the 8 course strategies)

Purpose: one file per strategy, all implementing the `Strategy` ABC
(base.py): evaluate(prices, fundamentals, universe, open_trades) ->
signals. Every threshold traces to a KB section number.

Provides: SMAStrategy, KnoxvilleStrategy, V20Strategy, RHSStrategy,
CWHStrategy, V10Strategy, TurnaroundStrategy, LifetimeHighStrategy;
shared geometry in pattern_common.py.

Depends on: data.models; research.turnaround_checklist (Strategy 7 only).

Invariants:
- `uses_stop_loss=False` on all — foundational course rule (AGENTS.md #1).
- RHS/CWH/V10/Turnaround signals: `requires_human_confirmation=True`,
  including SELLs (ADR-0003).
- SELL checks must NEVER depend on the originating pattern/range being
  re-detectable — exits key off levels tagged on the trade at entry
  (learned the hard way twice: V20 exit bug PR #7, stale necklines PR #8).
- Strategies see only their OWN open trades — except V10, which needs ALL
  trades to find its parent RHS/CWH position (routing is the engine's job).
- Pattern tolerances in pattern_common.py are OUR defaults, not course
  rules (ADR-0003) — tune there, nowhere else.

Blast radius: contained — strategies are leaves. But signal semantics
(actions, metadata keys like `range_upper`/`closes_all_open_trades`) are
consumed by the portfolio engine, scan, and web UI.

Tests: one file per strategy under tests/, docstrings cite KB sections.

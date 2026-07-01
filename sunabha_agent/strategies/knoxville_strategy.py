"""
Strategy 2: Knoxville Divergence Strategy.

Source: master_strategy_kb.md Section 2.3 (strategy rules) and the
Consolidated Agent-Ready Rules pseudocode.

The course delegates signal detection to the TradingView indicator
"Knoxville Divergence" (Rob Booker) with custom settings: bars back = 200,
RSI period = 14, momentum period = 20. Rob Booker's TradingView build is
closed-source, so the detection logic here is replicated from two matching
open-source ports of the same indicator (both by Paul Herrera / Avanti
Servicios Financieros):

  - MQL4:    github.com/pauljherrera/expert_advisors/blob/master/knoxville_divergence.mq4
  - cTrader: github.com/pauljherrera/expert_advisors/blob/master/Knoxville%20Divergence.cs

Both implementations agree on the divergence definition. At the current
bar t, scanning each lookback i from MIN_LOOKBACK (4) up to bars_back:

  BULLISH ("end point of a downtrend line" -> BUY):
    momentum(t) > momentum(t-i)      # momentum turning up...
    AND close(t) < close(t-i)        # ...while price is still falling
    AND low(t) <= min(low over the i bars before t)   # price at a window low
    AND RSI dipped <= 30 somewhere in the last i bars # oversold confirmation

  BEARISH ("end point of an uptrend line" -> SELL): exact mirror,
    momentum falling, price rising, high at a window high, RSI >= 70.

Momentum is the ratio form close / close[n bars ago] * 100 - that is what
BOTH reference implementations use (MQL4 iMomentum and cTrader
MomentumOscillator), so we match them rather than the difference form.

Strategy rules on top of the indicator (Section 2.3): V40 only, daily
candles, buy on bullish divergence, sell ALL open trades on the FIRST
bearish divergence after entry. Averaging allowed once, only if the new
signal is at least 5% below the first entry price - max 2 concurrent
trades (3% + 3% = 6% max allocation). No stop-loss. Next-day-open
execution is the execution layer's job, as with SMA.
"""

from __future__ import annotations

from dataclasses import dataclass

from sunabha_agent.data.models import Candle, Fundamentals, PriceSeries, Signal, Universe
from sunabha_agent.strategies.base import Strategy

# Course-mandated indicator settings (Section 2.3 settings table).
KD_BARS_BACK = 200
KD_RSI_PERIOD = 14
KD_MOMENTUM_PERIOD = 20
# From the reference implementations, not the course: the minimum lookback
# distance for a divergence pair (MinPeriod = 4 in both ports). A divergence
# against a bar only 1-3 bars ago is noise, not a trend line.
KD_MIN_LOOKBACK = 4
KD_RSI_OVERSOLD = 30.0
KD_RSI_OVERBOUGHT = 70.0

# Strategy-level rules (Section 2.3).
KD_AVERAGING_MIN_GAP_PCT = 5.0
KD_MAX_CONCURRENT_TRADES = 2


def wilder_rsi(closes: list[float], period: int = KD_RSI_PERIOD) -> list[float | None]:
    """
    Standard Wilder-smoothed RSI, one value per close (None during warmup).
    Both reference implementations use their platform's built-in RSI, which
    is Wilder's original smoothing - not a plain SMA of gains/losses.
    """
    n = len(closes)
    rsi: list[float | None] = [None] * n
    if n <= period:
        return rsi

    gains = [max(closes[i] - closes[i - 1], 0.0) for i in range(1, n)]
    losses = [max(closes[i - 1] - closes[i], 0.0) for i in range(1, n)]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    rsi[period] = _rsi_from_averages(avg_gain, avg_loss)

    for i in range(period + 1, n):
        avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
        rsi[i] = _rsi_from_averages(avg_gain, avg_loss)
    return rsi


def _rsi_from_averages(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 100.0
    return 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)


def ratio_momentum(closes: list[float], period: int = KD_MOMENTUM_PERIOD) -> list[float | None]:
    """close / close[period bars ago] * 100 - see module docstring for why
    the ratio form and not the difference form."""
    out: list[float | None] = [None] * len(closes)
    for i in range(period, len(closes)):
        past = closes[i - period]
        if past > 0:
            out[i] = closes[i] / past * 100.0
    return out


@dataclass(frozen=True)
class KnoxvilleDivergence:
    """A divergence confirmed at the LATEST bar of the series examined."""

    kind: str  # "BULLISH" or "BEARISH"
    lookback_bars: int  # the i at which the divergence pair was found
    rsi_extreme: float  # the qualifying oversold/overbought RSI value in the window


def detect_knoxville_divergence(
    candles: list[Candle],
    bars_back: int = KD_BARS_BACK,
    rsi_period: int = KD_RSI_PERIOD,
    momentum_period: int = KD_MOMENTUM_PERIOD,
) -> KnoxvilleDivergence | None:
    """
    Check whether a Knoxville Divergence is confirmed on the LAST candle.

    Scans lookbacks in ascending order and returns the first hit, matching
    the reference MQL4 implementation's scan order. Returns None when there
    is no divergence OR simply not enough history to evaluate one - callers
    treat both the same way (no signal), per the base-class contract that
    missing data must never raise.
    """
    t = len(candles) - 1
    closes = [c.close for c in candles]
    rsi = wilder_rsi(closes, rsi_period)
    mom = ratio_momentum(closes, momentum_period)

    if t < 0 or mom[t] is None:
        return None

    for i in range(KD_MIN_LOOKBACK, bars_back + 1):
        past = t - i
        if past < 0 or mom[past] is None:
            break  # lookbacks only get older from here; nothing more to scan

        window = candles[past:t]  # the i bars before the current one
        rsi_window = [r for r in rsi[past : t + 1] if r is not None]
        if not rsi_window:
            continue

        if (
            mom[t] > mom[past]
            and closes[t] < closes[past]
            and candles[t].low <= min(c.low for c in window)
            and min(rsi_window) <= KD_RSI_OVERSOLD
        ):
            return KnoxvilleDivergence(
                kind="BULLISH", lookback_bars=i, rsi_extreme=min(rsi_window)
            )

        if (
            mom[t] < mom[past]
            and closes[t] > closes[past]
            and candles[t].high >= max(c.high for c in window)
            and max(rsi_window) >= KD_RSI_OVERBOUGHT
        ):
            return KnoxvilleDivergence(
                kind="BEARISH", lookback_bars=i, rsi_extreme=max(rsi_window)
            )

    return None


class KnoxvilleStrategy(Strategy):
    name = "Knoxville Divergence Strategy"
    allowed_universes = (Universe.V40,)
    max_concurrent_trades_per_stock = KD_MAX_CONCURRENT_TRADES
    max_allocation_pct_per_stock = 6.0  # 3% initial + 3% averaged (Section 2.3)
    uses_stop_loss = False

    def evaluate(
        self,
        prices: PriceSeries,
        fundamentals: Fundamentals | None,
        universe: Universe,
        open_trades_on_this_stock: list[Signal],
    ) -> list[Signal]:
        if not self.can_run_on(universe):
            return []

        divergence = detect_knoxville_divergence(prices.candles)
        if divergence is None:
            return []

        close = prices.latest.close
        trigger_date = prices.latest.date
        open_buys = [s for s in open_trades_on_this_stock if s.action in ("BUY", "AVERAGE")]

        # --- SELL: first bearish divergence (uptrend-line end point) after
        # entry closes EVERYTHING - initial and averaged trade exit together
        # at this same point (Section 2.3). Because a position is closed the
        # moment its first exit signal fires (Section 6.4 Q&A), any bearish
        # divergence seen while trades are open IS the first one since entry.
        if divergence.kind == "BEARISH" and open_buys:
            return [
                Signal(
                    symbol=prices.symbol,
                    strategy_name=self.name,
                    universe_at_signal_time=universe,
                    action="SELL",
                    trigger_date=trigger_date,
                    signal_price=close,
                    rationale=(
                        f"Knoxville uptrend line end point confirmed at "
                        f"{close:.2f} (divergence vs {divergence.lookback_bars} "
                        f"bars back, RSI peaked at {divergence.rsi_extreme:.1f}). "
                        f"First exit signal since entry - closing ALL "
                        f"{len(open_buys)} open trade(s) together per Section 2.3."
                    ),
                    metadata={
                        "closes_all_open_trades": True,
                        "lookback_bars": divergence.lookback_bars,
                    },
                )
            ]

        if divergence.kind != "BULLISH":
            return []

        # --- BUY / AVERAGE on a bullish divergence (downtrend-line end point).
        if len(open_buys) >= self.max_concurrent_trades_per_stock:
            return []  # practical ceiling of 2 trades per V40 stock

        is_first_trade = not open_buys
        if not is_first_trade:
            first_entry_price = open_buys[0].signal_price
            if close > first_entry_price * (1 - KD_AVERAGING_MIN_GAP_PCT / 100):
                return []  # signal exists but the 5% averaging gap isn't met - skip

        return [
            Signal(
                symbol=prices.symbol,
                strategy_name=self.name,
                universe_at_signal_time=universe,
                action="BUY" if is_first_trade else "AVERAGE",
                trigger_date=trigger_date,
                signal_price=close,
                target_price=None,  # exit is the next uptrend-line end point,
                # an event, not a price level knowable in advance
                suggested_position_pct=3.0,
                rationale=(
                    f"Knoxville downtrend line end point confirmed at {close:.2f} "
                    f"(divergence vs {divergence.lookback_bars} bars back, RSI "
                    f"bottomed at {divergence.rsi_extreme:.1f})."
                    + (
                        ""
                        if is_first_trade
                        else f" Averaging: >= {KD_AVERAGING_MIN_GAP_PCT:.0f}% below "
                        f"first entry at {open_buys[0].signal_price:.2f}."
                    )
                ),
                metadata={"lookback_bars": divergence.lookback_bars},
            )
        ]

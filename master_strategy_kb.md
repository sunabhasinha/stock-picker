# Vivek Singhal Trading Strategy Knowledge Base
### Master Reference Document — Built incrementally from source YouTube videos

**Purpose of this document:** This is the single source of truth for an AI trading-research agent being built by the user. The agent's eventual job: take the strategies and stock-selection rules documented here, pull live data from TradingView and Screener.in, and recommend stocks to buy/watch — replicating the decision process taught across this video series.

**How this document is structured:** Each video is logged as its own numbered section, in the instructor's own stated terms (definitions, thresholds, formulas kept exact — not reinterpreted). A running **Consolidated Rules** section at the end aggregates everything into agent-ready logic so far. As new videos are added, the consolidated section gets revised to merge new strategies in without contradicting earlier ones (any conflicts will be explicitly flagged, not silently resolved).

**Status as of last update:** 6 source videos processed — this is now the COMPLETE course. Video 1 = stock-universe filtering layer (V40, V40 Next, V200). Video 2 = first 3 of 7-8 technical strategies (SMA, Knoxville Divergence, V20). Video 3 = 3 more chart-pattern strategies (RHS, Cup with Handle, V10), bringing the running total to 6. Video 4 (Parts 1+2) = fundamental/financial analysis deep-dive refining the V200/general quality gate. Video 5 = the 7th strategy, "Three Times in Three Years" — turnaround-stock strategy applicable to the entire NSE universe. Video 6 (final session) = introduces an 8th and final strategy ("Lifetime High Strategy," applicable specifically to V40/V40Next), AND — critically — provides the missing portfolio-construction layer: four named "categories" defining which strategy/strategies + which stock universe(s) a user should commit to using, since the course's repeated guidance is that a user should pick ONE of these four categories and stick with it rather than mixing freely. All 8 strategies and both the per-strategy AND portfolio-level logic are now fully documented.

---//---

# VIDEO 1 — Stock Selection Framework (V40 / V40 Next / V200)

**Source:** Class 1 of Vivek's Online Stock Market Course (English), YouTube (https://youtu.be/4HAcUG-3Sgg)
**Content type:** Defines the stock universe / eligibility filters. No chart-based entry/exit rules yet — those come in later videos.

## 1.1 Core Concept: Three Stock Categories

A stock must qualify into one of these three groups before any technical strategy is applied to it. Strategies in later videos will specify which category(ies) they apply to.

1. **V40** — Large cap + Mid cap companies meeting 6 conditions (Section 1.2)
2. **V40 Next** — Mid cap + Small cap companies meeting the *same* 6 conditions as V40 (Section 1.2)
3. **V200** — Companies meeting 3 separate financial conditions, different from V40/V40 Next (Section 1.3)

SEBI market-cap classification referenced: Top 100 companies by market cap = Large Cap. Rank 101–250 = Mid Cap. All others = Small Cap.

## 1.2 V40 / V40 Next — Six Qualifying Conditions (identical for both lists)

The only difference between V40 and V40 Next is market-cap band; the 6 qualifying conditions are the same.

| # | Condition | Rule (exact) |
|---|-----------|--------------|
| 1 | Market leader of sector | Rank #1, #2, or max #3 in its sector, by **both sales and net profit** |
| 2 | Long business history | In business 15–20 years (operating history, not necessarily listing history) |
| 3 | (Almost) debt-free | No significant borrowing/loan |
| 4 | Good future growth prospect | Low penetration of product/service; clear runway over next 10–20 years |
| 5 | Pricing power | Can raise prices when input costs rise, without losing unit volume — defined as "= brand value" |
| 6 | Not a PSU/government company | Excluded regardless of quality, since PSU mandate ≠ profit maximization |

**Condition detail — Market Leader (#1):** Examples given — Banking: HDFC Bank > ICICI Bank > Kotak Mahindra Bank. IT: TCS > Infosys > HCL Technologies. Note: broad sectors (e.g., FMCG) can have multiple "leaders" since sub-categories differ (Colgate ≠ Nestlé).

**Condition detail — Business History (#2):** Listing date irrelevant; operating history is what's counted. Example: HDFC Life incorporated 2000, listed only ~3-4 yrs ago — still qualifies. Explicitly excluded as too new: Zomato, Paytm, Nykaa.

**Condition detail — Debt-Free (#3):** Logic chain: market leader + 20yr survival + debt-free ⇒ implies strong management and good products (a company can't survive debt-free for 20 years as a leader with bad products/management).

**Condition detail — Growth Prospect / Low Penetration (#4):**
- Primary metric: penetration rate of the product/service in the population, with expectation it rises.
- Example cited: cars per 1,000 people — India ~22 vs USA ~980 (cited as Economic Times, Dec 2018 data); India was ~7 per 1,000 in 2001 (tripled in ~20 yrs).
- Growth can also come from **premiumization** even at high penetration (e.g. consumer trading up from entry-level to premium shampoo, or from ₹6-7L car to ₹12-20L car).
- Linked/second-order growth logic: more cars → more paint, steel, tires, batteries, mandatory car insurance.
- Example: SIS Limited (Security & Intelligence Services) — largest security services company in India; demand tied to office/factory/hospital/school/high-rise growth.
- Example: AC penetration in India cited as <5% of households — large runway; links to higher electricity demand → power sector profitability.
- Counter-example (high penetration, still investable): telecom — penetration is high, but ARPU expected to rise as price wars end.

**Condition detail — Pricing Power (#5):**
- Definition: ability to raise prices without losing volume when costs rise.
- Numeric example: sells 1,00,000 units @ ₹100 (cost ₹80, profit ₹20/unit). If cost rises 10% to ₹88, company must raise price 10% and still sell 1,00,000+ units.
- No pricing power example: telecom (price-sensitive switching, "no brand value" — utility companies generally lack pricing power).
- Has pricing power example: Colgate (most buyers don't check price — strong brand loyalty); BMW 3-Series (~₹30L→~₹60L over ~10 yrs) vs Maruti Zen/Santro (flat pricing over decades); Apple iPhone pricing growth vs budget Android makers.
- Direct quote-equivalent rule stated by instructor: **pricing power = brand value.**

**Condition detail — Not PSU (#6):**
- PSU mandate = serve citizens / maintain competitive market checks (e.g., SBI checks private bank fees; LIC checks private insurance premiums) — not profit maximization.
- If a PSU's main customer is the government itself (e.g., Bharat Electronics Ltd supplying defense), profit upside is inherently capped.
- Explicitly stated: no Adani Group stock appears in V40 or V40 Next (used as example of exclusion, not a quality judgment).

### V40 vs V40 Next — sole distinguishing factor
- V40: Large Cap + Mid Cap (per SEBI ranking)
- V40 Next: Mid Cap + Small Cap
- A small-cap can absolutely be a sector "market leader" — size alone never disqualifies.

### Related concept: "Multibagger" candidate logic (insight, not a full strategy)
Per the instructor, real multibaggers are typically small-cap sector leaders with a large market-cap *gap* vs. the #1 player in their sector — implying convergence potential over time. Examples (illustrative only, not a buy signal yet):
- Britannia (~₹91,000 cr) vs Mrs. Bector's Food (~₹2,000 cr) — ~45x gap; similar category, Mrs. Bector's supplies bread to QSR chains (Pizza Hut, McDonald's, Burger King, Domino's/Jubilant Foods).
- Asian Paints (~₹3 lakh cr) vs Indigo Paints (~₹7,000 cr) — ~42x gap.
- Angel One (~₹13,000 cr) vs 5Paisa (~₹1,000 cr) — ~13x gap.

**Flag for agent design:** this multibagger logic (market-cap ratio vs. sector leader) could become a quantifiable screening signal later, but the instructor has not yet turned it into a formal repeatable rule with thresholds. Treat as descriptive insight only until/unless a later video operationalizes it.

## 1.3 V200 — Three Qualifying Conditions (separate criteria from V40/V40 Next)

V200 does **not** use the "market leader / pricing power / brand" qualitative conditions — it's purely financial-metric based.

### Standard companies (non-banking, non-NBFC)
| # | Condition | Threshold |
|---|-----------|-----------|
| 1 | Net profit | > ₹200 crore, **trailing 12 months** (not last FY, not last quarter) |
| 2 | Return on Capital Employed (ROCE) | > 20% |
| 3 | Debt-to-Equity ratio | < 0.25 |

Exact screener.in query as given by instructor:
```
Net profit preceding 12 months > 200 AND
Return on capital employed > 20 AND
Debt to equity < 0.25
```

### Exception: Banks and NBFCs use different conditions
Reasoning: debt is core to the banking/NBFC business model (borrow low via deposits, lend high), so D/E and ROCE thresholds above don't apply meaningfully.

| # | Condition | Threshold |
|---|-----------|-----------|
| 1 | Net profit | > ₹200 crore, trailing 12 months |
| 2 | Return on Equity (ROE) — *not ROCE* | > 10% |

**Screener.in workflow for Banks/NBFCs (as demonstrated):**
1. Open any bank's screener.in page (e.g., HDFC Bank) → scroll to "Peer Comparison" → click sector "Banks" → returns full list of listed banks (37 at time of recording).
2. Filter/sort for ROE > 10%.
3. Cross-check Net profit (TTM) > ₹200cr; exclude failures.
4. Repeat for NBFCs via sector = "Finance" peer comparison, same 2 conditions.
5. Combine: qualifying non-BFSI (~154 in live demo) + qualifying banks (~10) + qualifying NBFCs (~50ish) ≈ ~200 total → "V200."

**V200 examples cited in the live screen run:** TCS, Infosys, Hindustan Unilever, ITC, Asian Paints, HCL Technologies, Nestlé, Coal India, Hindustan Zinc, Bajaj Auto, Ambuja Cement. (Coal India flagged by instructor as "good company, not necessarily good stock" — profitable but not expanding, distributes profit as dividend instead of growth capex — a useful nuance: passing the financial screen ≠ automatic buy.)

**V200 full ticker list:** Not yet compiled — to be built by user running the live screener.in query (V40/V40 Next static lists were user-supplied; V200 requires live screening since the instructor didn't hand over a static list in this video). Will be added to Section "Reference Data" below once available.

## 1.4 Tools / Platforms Referenced
- **Screener.in** — primary fundamental screening tool for all of the above (net profit, ROCE, ROE, D/E, peer comparison by sector, market cap sort).
- **TradingView** — for maintaining watchlists of V40/V40 Next/V200 once built (instructor mentions a free-tier method for 3 separate watchlists).

## 1.5 Explicitly NOT Yet Covered (per instructor, coming in future videos)
- No technical/chart-based entry or exit rules yet.
- No timeframes, indicators (RSI, moving averages, etc.), explicit stop-loss rules, or position sizing given yet.
- Instructor gave a **mindset/contrarian narrative** around stop-loss (claims "strong hands" — promoters/FIIs/DIIs/HNIs — don't use stop-loss, while "weak hands"/retail do, and that operators intentionally trigger retail stop-losses to accumulate shares cheaply). **This is NOT an operational trading rule** — it's market-structure philosophy. Do not encode "never use stop-loss" as an agent rule unless/until a later video gives a concrete, specific replacement risk-management mechanism.
- Three concrete strategies were explicitly promised for the next session.

## 1.6 Open Questions / Build Flags from Video 1
1. Exact screener.in field name for "Net profit preceding 12 months" (TTM) needs confirming when wiring up actual API/scraping logic.
2. No stated refresh cadence for V40/V40 Next/V200 membership (quarterly? annually?) — ask if a later video clarifies.
3. "Market leader = top 3 by sales & profit" is qualitative/manual — not purely automatable via a quant screener query. Likely needs to remain a maintained/static reference list (as user has done for V40/V40 Next) rather than live-derived each run.

---//---

# VIDEO 2 — Three Core Technical Strategies (Simple Moving Average, Knoxville Divergence, V20)

**Source:** Class 2 (live session, Q&A included) of Vivek's Online Stock Market Course (English), YouTube
**Content type:** First concrete, codeable technical entry/exit strategies. All three use **daily candlestick charts only**. Position sizing, averaging rules, and applicable stock universe (V40 / V40 Next / V200) are explicitly specified per strategy — they differ between strategies, so the agent must NOT apply one strategy's rules to another.

## 2.1 Preliminary Concepts (context before the strategies)

### Four things in a trader's control vs. two things not in control
**In control:**
1. Finding a good business (low penetration, ~10+ year growth runway)
2. Finding a good (market-leading) company within that business
3. Deciding the buying price (via technical analysis)
4. Deciding the selling price / target (via technical analysis)

**NOT in control:**
1. Market volatility / price fluctuation
2. Holding period (some trades resolve in weeks, others take 1-2+ years)

**Operational implication:** the agent should not treat "holding period" or "volatility" as inputs it can optimize — only entry price, exit price, business quality, and company quality are decision levers.

### Realistic return expectations (explicitly stated, not a strategy rule, but useful as a sanity-check / reporting baseline)
- Investing (buy & hold) historically: ~20% CAGR is considered a strong long-term ceiling (Warren Buffett cited as compounding at ~19% CAGR over decades).
- Trading (using these strategies, buying/selling based on technical signals rather than pure buy-and-hold) is claimed to average ~40% CAGR over time, though any single year can vary significantly (some years 10-15%, other years 50-60%+).
- This is presented as a multi-year average, NOT a fixed annual return — explicitly stated that returns will never be consistent year-to-year ("not like a fixed deposit").
- **Flag for agent:** Do not hard-code "40% annual return" as an assumption/projection in any user-facing output — this is the instructor's own long-run claim/anecdote, not a guaranteed or verifiable parameter. Useful only as background context, not as a forecasting input.

### Portfolio constraint (stated philosophy carried into Video 2)
- Trade only within V40 and V40 Next companies as the preferred universe ("these 80 companies are the best companies") for general trading discipline — though as shown below, the V20 strategy specifically extends to V200 as well.

---

## 2.2 Strategy 1 — Simple Moving Average (SMA) Strategy

**Applicable universe:** **V40 ONLY.** Explicitly NOT to be used on V40 Next or V200 — reasoning given: the strategy's logic depends on large, "great" companies attracting long-term institutional buyers (pension funds, sovereign funds) at oversold levels; this dynamic is asserted not to reliably exist in smaller/lower-quality companies.

**Chart timeframe:** Daily candlestick chart only.

**Indicators required:** Three Simple Moving Averages (SMA) — NOT exponential, NOT weighted. Must be:
| Period | Color (for consistency/communication) |
|---|---|
| 200-day SMA | Black |
| 50-day SMA | Red |
| 20-day SMA | Green |

(Color choices are a personal convention for clarity when discussing charts, not a functional requirement — but should be kept consistent in any UI the agent builds.)

### Buy condition (all must be true simultaneously, based on closing price)
Ordered top-to-bottom on the chart:
1. 200-day SMA (black) is on **top** (highest value of the three)
2. 50-day SMA (red) is **below** the 200-day SMA
3. 20-day SMA (green) is **below** the 50-day SMA
4. Closing price is the **lowest** of all four (below all three SMAs)

In short: `200SMA > 50SMA > 20SMA > Close`

### Sell condition (exact inverse)
1. 200-day SMA (black) is on the **bottom** (lowest value of the three)
2. 50-day SMA (red) is **above** the 200-day SMA
3. 20-day SMA (green) is **above** the 50-day SMA
4. Closing price is the **highest** of all four (above all three SMAs)

In short: `Close > 20SMA > 50SMA > 200SMA`

### Execution timing
- Signals are evaluated using the **daily closing price** (i.e., after market close).
- Actual buy/sell order is placed at the **next day's market open** (~9:15 AM), not at the close itself.

### Position sizing
- **3% of total portfolio per trade**, per stock.
- No averaging at all under this strategy ("we will not average anything... only one trade").
- No stop-loss is used in this strategy.

### Underlying rationale (as explicitly explained by instructor — useful for agent documentation/UX, not a separate rule)
- 200-day SMA ≈ ~10 months average price (long-term trader cohort)
- 50-day SMA ≈ ~2.5 months average price (medium-term trader cohort)
- 20-day SMA ≈ ~1 month average price (short-term trader cohort)
- When price is below all three SMAs in descending order (200>50>20>Close), it implies long-term, medium-term, AND short-term traders are all underwater on average simultaneously → maximum pessimism → large patient capital (pension/sovereign funds) tends to step in here, providing a floor → considered the statistically best entry zone.
- The inverse (price above all three, ascending) implies broad-based optimism/profit-taking conditions → considered the best exit zone.
- Instructor explicitly contrasts this with textbook "Golden Cross" (buy when 50SMA crosses above 200SMA) and "Death Cross" (sell when 50SMA crosses below 200SMA) — he states he back-tested these classical rules and found they underperformed, and that doing the **opposite** of Golden/Death Cross conventions produced better results historically. This is asserted, not provided with statistical backing in the transcript — log as an unverified claim, not a proven backtest result the agent should assume true without its own validation.

### Worked examples cited in video (for reference/validation, not extracted as separate rules)
- HDFC Bank: one cycle yielded ~4% gain over ~7 months (called out explicitly as a "bad market" period example, since Nifty had been flat for ~1 year); other HDFC Bank cycles yielded 41%, 7%, 16.81%, ~9.5%, 17.77% over varying multi-month windows.
- Bajaj Finserv: cycles of 17% (131 days), 65% (~5 months), 18% (36 days), 28.45% (~3 months).
- General takeaway stated: returns vary widely per trade/per stock/per period — no fixed expected percentage per trade.

---

## 2.3 Strategy 2 — Knoxville Divergence Strategy

**Applicable universe:** **V40 ONLY** (same restriction as SMA strategy).

**Chart timeframe:** Daily candlestick chart only.

**Indicator:** TradingView built-in indicator named "Knoxville Divergence." Required custom settings (deviating from default):
| Setting | Default | Required value |
|---|---|---|
| Bars back (input) | 150 | **200** |
| RSI period | 21 | **14** |
| Momentum period | 20 | 20 (unchanged) |
| Line color (style) | — | Blue (cosmetic only) |

### How the indicator's lines work (mechanical description, important for any custom implementation)
- The indicator draws straight (non-curved) lines connecting two confirmed points — NOT a continuously updating line like a moving average.
- **Uptrend lines** connect the **top of one candle to the top of another candle**.
- **Downtrend lines** connect the **bottom of one candle to the bottom of another candle**.
- A line only appears once BOTH its starting point and ending point are confirmed by the underlying algorithm (RSI oversold/overbought + momentum conditions) — it does not appear incrementally; it appears suddenly once both points are validated.
- The **starting point of a line is irrelevant** to the strategy. Only the **ending point** matters.
- The **length/size of a line is irrelevant** — a very short line and a very long line carry equal weight/validity.
- Per Q&A clarification: the end point of a downtrend line is considered confirmed because (a) RSI has reached oversold territory, and (b) momentum (per the momentum period setting) shows the price attempting to reverse upward — i.e., the algorithm's own internal logic (RSI + momentum) is what defines a valid end point, not a separately-applied manual rule.

### Buy condition
- **Buy at the end point of a downtrend line** (i.e., when a Knoxville downtrend line's confirmed ending point appears).

### Sell condition
- **Sell at the end point of the FIRST uptrend line** that appears after the buy. If multiple uptrend lines exist/appear over time, only the first one (chronologically, after entry) is used as the exit signal — do not wait for a later/higher uptrend line endpoint.

### Execution timing
- Same as SMA strategy: evaluate at end of day (close), execute next day at market open (~9:15 AM). Both buy and sell follow this next-day-open execution rule.

### Position sizing & averaging
- **3% of total portfolio per initial trade.**
- **Averaging IS allowed**, under one condition: a second downtrend-line buy signal may be taken **only if its end point is at least 5% lower than the first trade's entry price.** If the second signal's end point is less than 5% below the first entry, do NOT average — skip it.
- Maximum of **2 total trades** (1 initial + 1 average) per stock under this strategy — per explicit Q&A answer, a third averaging opportunity essentially doesn't occur in V40 stocks because they don't typically fall far enough to trigger a third valid signal (this is empirical/practical, not a hard programmatic cap — but the instructor states 2x is the practical ceiling for V40 stocks specifically).
- If averaging occurs, total allocation to that stock becomes 3% + 3% = **6%** of portfolio.
- Both the original and averaged trade share the **same exit point** — the first uptrend line endpoint after the (most recent) entry.
- No stop-loss used.

### Worked examples cited (for reference only)
- Bajaj Finance: single trade 37.63% gain in 59 days; an earlier averaged pair: first trade 14.47% (40 days), second (averaged, >5% lower) combined exit for 37.63% gain in 59 days from the second entry.
- Another cycle: 42% gain in 122 days.
- A pandemic-period example: two trades averaged (gap >5%, specifically described as a substantial double-digit gap) yielding 61% (146 days) on the first and 85% (95 days) on the second, both exiting at the same uptrend endpoint.
- A case where the second signal was only ~2.25% below the first (less than the required 5%) — explicitly NOT averaged; only one trade taken, yielding 84% gain over 203 days.

---

## 2.4 Strategy 3 — V20 Strategy

**Applicable universe:** **V40, V40 Next, AND V200** — the only one of the three strategies in this video usable across all three stock categories.

**Chart timeframe:** Daily candlestick chart only.

**No indicator required** — this strategy is based purely on identifying specific candlestick patterns and price ranges, not a plotted technical indicator.

### Step-by-step definition
1. **Identify a consecutive run of green (bullish) candles** — one or more candles, with **zero red candles interrupting the sequence**. If a red candle appears in between, the sequence is void and must restart.
2. **Measure the total move** from the **lowest point (bottom) of the lowest green candle in the run** to the **highest point (top) of the highest green candle in the run.** This top candle need not be the last candle in the sequence — it can be any candle within the green run.
3. **This total move must be ≥ 20%** (the "V20" name refers to this 20% threshold). If the move is under 20%, the pattern does not qualify.
4. Once qualified, **draw a horizontal range**: a lower line at the bottom of the lowest green candle, and an upper line at the top of the highest green candle in that run.
5. **Buy when price subsequently falls back down and touches/hits the lower line** of this established range.
6. **Sell when price rises back up and touches/hits the upper line** of the SAME range (not a higher target, not waiting for a new high — exit strictly at the upper boundary of the range that was used for entry).

### Critical clarification — ranges are single-use ("don't reuse the coffee cup")
- Once a range has been used for one full buy-sell cycle (price touched lower line, then touched upper line, trade closed), that exact range is "spent" and CANNOT be reused for a future trade, even if price falls back down to the same lower line again.
- A fresh trade requires a **new, separate 20%+ green-candle-run range** to be identified before buying again at that level.
- If multiple distinct qualifying ranges exist (e.g., overlapping or sequential ranges from different green runs), each is tracked and traded independently using its own lower/upper boundaries — buying and selling always happens within the SAME range that was used for entry, never mixing a buy from one range with a sell target from a different (e.g., higher/larger) range.

### Position sizing & averaging
- **3% of total portfolio per trade.**
- **Averaging allowed, condition: a new valid trade signal (price touching the lower line of a DIFFERENT, separate qualifying range) can be taken only if that range's lower line is at least 10% below the first trade's entry price.** (Note: this is a larger required gap than the Knoxville strategy's 5% — V20 applies to a broader universe including smaller/more volatile V200 stocks, hence the wider averaging buffer.)
- **Maximum of 3 total trades per stock** at any given time under this strategy (vs. Knoxville's practical max of 2). Reasoning given: V200 stocks (smaller than V40) have more room to fall further, making a third valid lower entry more plausible than in large, more stable V40 names.
- If all 3 trades are taken, total allocation to that stock = 3% × 3 = **9%** of portfolio.
- If a position is exited (profit booked) while only 1 or 2 of the 3 available "slots" were used, the freed-up slot can be used again if a new qualifying range/signal appears (i.e., it's a rolling cap of 3 concurrent trades per stock, not a lifetime limit of 3 trades ever).
- No stop-loss used.

### Execution timing — DIFFERENT from the other two strategies
- Unlike SMA and Knoxville (which use end-of-day close signals executed next-day-open), V20 entries/exits can trigger **intraday**, as soon as price touches the lower or upper line during market hours — it is not dependent on the daily close.
- Because the exact target (upper line) and entry (lower line) levels are known in advance, the instructor recommends using a **GTT (Good Till Triggered) order** for both buy and sell, so the trader doesn't need to continuously monitor the chart intraday.

### Worked examples cited (for reference only)
- Bajaj Holdings: 32.95% qualifying green-candle move; trade yielded 33.19% gain in 125 days.
- Bajaj Auto: 20.83% qualifying move (8 green candles); trade yielded 20.91% gain in 63 days.
- Angel One: two sequential ranges/trades, yielding ~23-24% (5 months) and ~30% (5 months) respectively.
- IRCTC (a V200 company — confirmed in video to meet V200's 3 conditions: net profit >₹200cr, ROCE 51% [>20% threshold], debt/equity <0.25): demonstrated 3 simultaneous averaged trades within different ranges, plus an additional same-range re-entry after a fresh 20%+ move appeared post-exit; example gains cited: ~27% (52 days), ~24% (56 days) on different range cycles.
- Angel One fundamentals double-checked live on screener.in: ROCE 35%, net profit ₹685cr, debt/equity 1.61 — instructor clarifies Angel One is functionally an NBFC (provides margin trading loans, charges interest) even though not formally licensed as one, so it qualifies via the NBFC V200 rule (net profit >₹200cr AND ROE >10%) rather than the standard rule — in this case ROE was 46%, comfortably passing.

---

## 2.5 Cross-Strategy Comparison Table

| Aspect | SMA Strategy | Knoxville Divergence | V20 Strategy |
|---|---|---|---|
| Applicable universe | V40 only | V40 only | V40 + V40 Next + V200 |
| Indicator | 3x SMA (200/50/20) | Knoxville Divergence (custom settings) | None (pure price action) |
| Entry signal | Close below all 3 SMAs, in order 200>50>20>Close | End point of a downtrend line | Price touches lower line of a 20%+ green-candle range |
| Exit signal | Close above all 3 SMAs, in order Close>20>50>200 | End point of FIRST uptrend line after entry | Price touches upper line of the SAME range used for entry |
| Execution timing | Next day open, after prior day's close confirms signal | Next day open, after prior day's close confirms signal | Intraday, as soon as price hits the line (GTT order recommended) |
| Position size (initial) | 3% of portfolio | 3% of portfolio | 3% of portfolio |
| Averaging allowed? | No | Yes, if new signal ≥5% below first entry | Yes, if new (different) range's lower line ≥10% below first entry |
| Max trades per stock | 1 | 2 (practical ceiling for V40) | 3 (rolling, can reopen after exit) |
| Max allocation per stock | 3% | 6% | 9% |
| Stop-loss used? | No | No | No |
| Range/signal reusable after one trade cycle? | N/A (single trade only) | N/A | No — each range is single-use; must wait for a fresh qualifying pattern |

## 2.6 General Operating Rules Stated Across Both Sessions (Video 1 + Video 2)

- **One strategy per trade** — do not combine signals from multiple strategies to justify a single trade decision (explicit Q&A answer: "we should not try to apply more than one strategy on one trade").
- **No stop-loss in any of these three strategies.** (Consistent with the philosophical framing in Video 1, but now given as a literal, repeated rule across all three concrete strategies — this raises this point from "philosophy" to an **actual operating rule**, superseding the earlier caution in Video 1 Section 1.5. Risk control instead comes from: position sizing caps (3%/6%/9% per stock), strict adherence to the V40/V40 Next/V200 quality filter, and the averaging-gap rules above.)
- **Existing portfolio reconciliation logic** (explicit Q&A answer, useful for the agent's "what do I do with stocks I already hold" logic):
  - If a strategy IS applicable/active on a held stock → exit at that strategy's defined target price.
  - If NO strategy is applicable AND the stock is currently in profit → exit immediately (since there's no defined target to wait for).
  - If NO strategy is applicable AND the stock is currently at a loss → hold and wait; do not sell at a loss in the absence of a strategy signal, **provided** the underlying business still meets the V40/V40 Next/V200 quality criteria (this is conditional on quality, not unconditional "never sell at a loss").
- **FIFO accounting caveat (operational, not strategic):** When averaging into a position, brokerage/tax accounting will apply FIFO (first-in-first-out) on exit, which may not match the trader's own per-trade strategy logic/profit tracking. The instructor recommends maintaining a **separate manual spreadsheet** to track per-trade entries, exits, and P&L according to the strategy logic, independent of what the broker's FIFO-based statement shows.
- **Minimum trade size floor:** if 3% of available capital is too small in absolute terms (e.g., early in a SIP-style monthly investment plan), do not invest less than ₹10,000 in a single stock/trade — wait until enough capital has accumulated instead of under-sizing a position.
- **Capital that shouldn't be invested:** Do not invest money that may be needed within 3 years (e.g., working capital for a separate business, emergency funds beyond ~3 months of expenses). Keep ~3 months of expenses in a bank account; the rest can be deployed if not needed in the short-to-medium term. This is risk-management/capital-allocation guidance, not a chart-based rule.
- **Do not take loans to invest** — explicitly discouraged regardless of comparative interest rates.
- A separate, more aggressive strategy ("three times in three years") was referenced as coming in a later session (day 5) — not yet detailed. Flag for future video.
- Total number of strategies to be taught across the full course: 7–8 (confirmed again in this video). 3 of 7-8 are now documented (this video). Remainder pending future videos.
- A review/rebalance cadence question was asked about V40/V40 Next list membership — instructor's answer: not very frequent; he personally changed only ~4 stocks in the lists over the past 2 years, and updates the user community when changes occur. (Useful as a real-world data point, though still no fixed cadence rule — treat V40/V40 Next as a low-turnover, manually-curated list rather than something to re-derive frequently.)

## 2.7 Open Questions / Build Flags from Video 2
1. **Stop-loss rule has now hardened from "philosophy" (Video 1) to "explicit operating rule" (Video 2)** — confirmed: none of the 3 strategies taught so far use a stop-loss. This should now be encoded directly into agent logic for these 3 strategies specifically. Re-verify this remains true as more strategies are added — note if any later strategy introduces an actual stop-loss mechanism (would be a deviation worth flagging explicitly).
2. Knoxville Divergence's underlying confirmation logic (RSI oversold + momentum reversal) is being delegated entirely to a third-party TradingView built-in indicator. For a custom-built tool (not running on TradingView), this indicator's exact calculation logic (the specific RSI/momentum formula and thresholds that define a valid "end point") would need to be reverse-engineered or replicated — this is a meaningful technical dependency to flag for the build phase. The named indicator on TradingView is literally called "Knoxville Divergence" (note: a well-known public indicator by this name exists; worth checking its open-source/Pine Script formula directly when we get to implementation, rather than re-deriving from the video alone).
3. "3 times in 3 years" strategy mentioned but not yet defined — pending a later video.
4. No explicit guidance yet on what happens if TWO or more of the 3 documented strategies generate signals on the same stock simultaneously (e.g., SMA and Knoxville both fire a buy on the same V40 stock on the same day) beyond the general "one strategy per trade" rule — unclear if this means trader's choice, or some other priority logic. Flag as ambiguous; revisit if a later video clarifies.
5. The instructor mentions a personal "3x in 3 years" account being separate from the account used for these other strategies — implies the agent/tool may eventually need to support **multiple parallel strategy "books"** per user rather than a single unified portfolio view.

---//---

# VIDEO 3 — Three Chart-Pattern-Based Strategies (Reverse Head & Shoulder, Cup with Handle, V10)

**Source:** Class 3 (live session, Q&A included) of Vivek's Online Stock Market Course (English), YouTube
**Content type:** Three more concrete strategies, bringing the running total to 6 of 7-8. Key distinction from Video 2: these are **chart-pattern-based** (geometric price-shape recognition), not **indicator-based** (no SMA, no Knoxville-style plotted indicator). This is an important categorical distinction for the eventual tool's architecture — pattern-recognition logic is fundamentally different to implement than indicator-threshold logic.

## 3.0 Important Framing Notes (apply across all 3 strategies in this video)

- All three strategies in this video require the underlying stock to first pass the **same business-quality reasoning** from Video 1 (low penetration, good future growth prospect) and be within the V40/V40 Next/V200 universe — explicitly restated: "any technical strategy will not work if the company is not a good company."
- A 4th session (next video in the series) will cover fundamental/financial analysis in full detail — referenced here but not yet documented (pending future video).
- General operator psychology theme (carried from Videos 1 & 2, reinforced here): retail traders place stop-losses below visible support levels or at fixed percentage losses; operators deliberately push price below these levels to trigger mass retail selling, then accumulate shares at the resulting lower price. This is presented as the causal mechanism behind why chart patterns form the way they do — useful as documentation/rationale but not itself a separate coded rule (the actual coded rule is "we don't use stop-loss," already captured in Video 2).
- Restated explicitly: do not try to find/assign a "reason" for why a stock's price fell before applying a chart-pattern strategy. A valid news-based reason may or may not exist; either way it does not change whether the pattern/strategy criteria are met. The agent should NOT incorporate news-sentiment or "reason-for-decline" as a filter — only the chart-pattern geometry and fundamental quality gate matter.
- Real anecdotal performance reference (context only, not a rule): a course participant reportedly turned ₹5.5 lakh into ₹21 lakh over ~2 years trading exclusively the Knoxville strategy from Video 2 — cited as evidence that even a single strategy used with discipline is sufficient; the agent need not weight multiple simultaneous strategies as inherently better than one used consistently.

---

## 3.1 Strategy 4 — Reverse Head & Shoulder Pattern (RHS)

**Applicable universe:** **V40 and V40 Next only.**

**Chart timeframe:** Daily candlestick chart (implied consistent with other strategies; not separately re-stated in this video but no contrary instruction given).

**No indicator required** — pure chart-pattern/price-geometry recognition, similar in nature to V20.

### Critical clarification: REVERSE pattern only, never the standard pattern
- Standard "Head & Shoulder" pattern (predicts price decline) is explicitly and permanently excluded from use — the strategy never shorts, never trades F&O, never trades intraday, so there is no mechanism to act on a bearish pattern. Only the **Reverse Head & Shoulder** (a.k.a. "Inverse Head & Shoulder") — which predicts a price increase — is ever used.

### Geometric definition
1. **Three connecting points required:** (a) the start of the left shoulder, (b) the point where the left shoulder ends and the head begins, (c) the point where the head ends and the right shoulder begins.
2. **These three connecting points MUST lie on a perfectly horizontal (180°) line** — this horizontal line is called the "neckline." This is stated as a strict, non-negotiable rule, and the instructor explicitly contradicts common technical-analysis textbook teaching that allows an upward- or downward-sloped neckline — he states (based on his own experience/backtesting) that only a horizontal neckline gives reliable results; sloped necklines are explicitly rejected as producing "mediocre results."
   - Rationale given for requiring horizontal: if the three connecting points are at different price levels, it implies different sellers/operators may be active at each point. If all three are at the same horizontal level, it implies the same operator/seller is defending that exact price level each time — a stronger, more deliberate signal.
3. **Multiple shoulders are allowed on either side** (left and/or right) — not limited to exactly one shoulder per side. A pattern with more than one shoulder on a given side is called a **"Complex Reverse Head & Shoulder Pattern"** and is considered MORE reliable than a simple (single-shoulder-per-side) pattern. At least one shoulder must exist on each side for the complex variant to apply — both sides need not have multiple shoulders simultaneously (one side can have one shoulder, the other can have two or more, and it still qualifies as "complex").
4. **Shoulders can vary in shape, depth, and width relative to each other and relative to the head** — no symmetry is required between left/right shoulders. The only hard constraint: **no shoulder's depth (lowest point) may be deeper/lower than the head's lowest point.** The head must always be the deepest point in the entire pattern.
5. **Drawing tolerance for the neckline:** while drawing the horizontal neckline connecting the points, **wicks (candle shadows/tails) may be crossed/ignored**, and **the body of a red candle may be crossed**, but **the body of a green candle must NEVER be crossed** by the neckline. This is a precise rule for where exactly to draw the line when real-world price data doesn't land the connecting points at exactly identical price levels.
6. **Charts must be in NORMAL (linear) scale, not logarithmic scale**, when measuring patterns and targets — explicitly instructed to deselect/disable the "log" toggle on the charting platform.

### Buy condition (entry logic — distinct from where many textbooks teach to buy)
- The instructor explicitly departs from the common textbook rule of "buy only on breakout above the neckline." Instead:
- **Buy at the breakout from the RIGHT SHOULDER's own base formation** — i.e., as soon as the right shoulder itself (the first right shoulder, if there are multiple) completes its own mini base-and-breakout, BEFORE price has even reached/broken the neckline.
- The "right shoulder breakout" requires the same 3-part confirmation used in the V20-adjacent logic: (a) a recognizable **base formation** (price comes down, consolidates sideways in a range, like a "U-turn" or wheel motion: down → flat → turning up), (b) a **breakout above that base range**, (c) the breakout candle must be **green**, and (d) confirmed **on a closing basis** (not just intraday wick movement above the range).
- If there is more than one shoulder on the right side, the buy decision is made at the **first right shoulder's base/breakout**, since it's unknown in advance whether a second right shoulder will form.
- Rationale for buying early (at right-shoulder breakout) rather than waiting for neckline breakout: buying earlier captures significantly more potential gain (example given: 58% potential gain buying at right-shoulder breakout vs. only 40% potential gain if waiting for the neckline breakout) and results in a smaller potential drawdown if the pattern fails, since there's no stop-loss used.
- **Execution timing:** can buy same-day if monitoring the chart late in the session (e.g., around 3:15–3:25 PM market close), but next-day-morning execution is recommended as the practical default for those not watching markets live.

### Target / sell condition (two-part rule — important and easy to mis-implement)
1. **Technical Target calculation:** measure the vertical distance ("depth") from the **lowest point of the head** up to the **neckline** (the horizontal connecting line). Take that exact distance and project/plot it **upward starting from the neckline** — the resulting price level is the "Technical Target."
2. **Compare Technical Target against the stock's lifetime high price.** Apply this exact rule:
   - **IF Technical Target < Lifetime High → the actual sell target becomes the Lifetime High** (not the lower technical target).
   - **IF Technical Target > Lifetime High → the actual sell target remains the Technical Target** (since it's already higher than the lifetime high).
   - In short: **always sell at whichever of (Technical Target, Lifetime High) is HIGHER.**
3. Rationale given: an operator only commits to accumulating a large quantity of shares (large enough to create this kind of multi-month/multi-year pattern) if their own internal conviction/target is at least the lifetime high — otherwise the scale of accumulation wouldn't make sense. This is offered as the reasoning for why RHS is considered (by the instructor) one of the most reliable patterns when applied to fundamentally good companies.

### Position sizing
- **3% of total portfolio per trade.**
- No stop-loss.
- Averaging behavior for RHS is not separately defined in this section (no explicit "average if X% lower" rule given for RHS itself, unlike V20/Knoxville) — however, see Strategy 6 (V10) below, which is explicitly built on top of RHS/CWH signals and provides the averaging mechanism for these two pattern-based strategies.

### Optional secondary rule — minimum potential gain threshold (recommended, not mandatory)
- **Recommended (optional) filter:** only take an RHS trade if the calculated potential gain (from buy price to technical target) is **≥ 40%.** This is explicitly framed as optional/recommended rather than a hard requirement — useful for traders with limited time who want fewer, higher-conviction, higher-reward trades (e.g., 10 such trades/year, each ~40%+, can meaningfully compound a portfolio without frequent monitoring). Traders with more time available can use the strategy on any qualifying setup regardless of potential-gain size.
- **A related explicit special-case rule given in Q&A:** if the pattern's connecting points (the neckline) are forming AT or near the stock's all-time/lifetime high (i.e., the entire pattern is being built at a new high rather than as a recovery/basing pattern after a decline), then the minimum potential gain requirement should be treated as a hard 40% minimum, not just a recommendation — i.e., be more selective specifically when the pattern occurs at lifetime highs. (Applies to both RHS and Cup with Handle, per the instructor's explicit generalization in Q&A.)

### Holding period reality-check (explicitly emphasized, not a separate rule, but important UX/expectation-setting for the agent's output)
- Multiple real, named worked examples given (Reliance Industries, HAL, Godrej Consumer, Oracle Financial Services/OFSS, Axis Bank) where holding periods to reach target varied from ~105 days up to 600+ days (over a year), and where price action stayed flat/sideways for many months (sometimes 6-7+ months) before resolving. The explicit point made: the agent/tool's output should NOT imply a fixed expected holding period — RHS setups in particular can take a long time to play out, and flat/sideways price action after entry is normal, not a signal of failure, as long as the pattern/quality criteria remain valid.

---

## 3.2 Strategy 5 — Cup with Handle Pattern (CWH)

**Applicable universe:** **V40 and V40 Next only** (same universe as RHS).

**Chart timeframe:** Daily candlestick chart.

**No indicator required** — pure chart-pattern recognition.

### Relationship to RHS (important structural definition)
- **A Cup with Handle pattern is structurally defined as "a Reverse Head & Shoulder pattern without the left shoulder."** That is: the pattern starts directly with the head/cup formation (no left-shoulder run-up before it), proceeds to a downward dip (the "cup," analogous to the head), and then forms a "handle" (analogous to the right shoulder).
- All shape/geometry rules inherited from RHS apply with adjusted terminology:
  - "Cup" = analogous to "head" — must be the deepest point in the pattern.
  - "Handle" = analogous to "shoulder" — **the handle's depth must always be LESS than (shallower than) the cup's depth.** A "handle" that is as deep or deeper than the cup is explicitly invalid and does not qualify as a Cup with Handle pattern.
  - **Multiple handles are allowed** (analogous to multiple shoulders) — a pattern with more than one handle is called a **"Complex Cup with Handle Pattern"** and, as with complex RHS, is considered MORE reliable than a single-handle version (rationale: more handles = operator taking more time/making more attempts to accumulate additional quantity = stronger conviction).
  - Cup shape itself has no required symmetry — can be U-shaped, V-shaped, or irregular/jagged ("tough" shaped, per transcript) — shape variability does not invalidate the pattern.
  - When drawing the connecting/neckline for a Cup with Handle, **wicks (intraday candle shadows) may always be ignored/crossed** when establishing the base-formation range — this is stated specifically in the context of base-formation boxes for this strategy (consistent with the general "don't cross a green candle body" rule from RHS, though the video specifically emphasizes wick-ignoring here for the base box).
- **Invalid edge case explicitly called out:** if the "handle" portion is actually larger/deeper than the "cup," this is NOT a valid Cup with Handle pattern.

### Buy condition (identical mechanism to RHS's right-shoulder buy logic)
- Buy at the **first handle's base formation breakout**: (a) base formation (range consolidation) within the handle, (b) breakout above that range, (c) breakout candle is green, (d) confirmed on closing basis.
- If multiple handles exist, the buy decision happens at the **first handle**, since it isn't known in advance whether further handles will form.

### Target / sell condition — KEY DIFFERENCE from RHS
- **Calculate the Technical Target the same way as RHS:** measure the depth from the lowest point of the cup up to the neckline, then project that same distance upward from the neckline.
- **CRITICAL DIFFERENCE FROM RHS: for Cup with Handle, the Technical Target IS the final sell target — it is NOT compared against or raised to the lifetime high.** Unlike RHS (which sells at the higher of Technical Target vs. Lifetime High), CWH always sells at the Technical Target itself, even if the lifetime high is higher. This is explicitly flagged by the instructor as the main distinguishing rule between the two strategies — do not conflate this with RHS's logic.

### Position sizing
- **3% of total portfolio per trade.**
- No stop-loss.
- (As with RHS, no separate stand-alone averaging rule is given for CWH directly — averaging on top of a CWH entry is handled via the V10 strategy below.)

### Psychological/operator rationale given (context, not a separate coded rule)
- Because there is no left shoulder (no prior decline-and-support-break sequence), the operator building a Cup with Handle pattern is NOT triggering retail stop-losses via a support breakdown in the same way as in RHS — instead, price is simply being capped/repelled at a resistance level repeatedly (without ever breaking a "support" below the most recent low) while the operator accumulates. This is explanatory context for why the pattern looks the way it does, not an independent trading rule.

### Same optional 40%-minimum-gain guidance as RHS
- Same recommended (optional) 40%+ potential gain filter applies, and same hard-40%-minimum override applies specifically when the pattern's connecting points are forming at/near the lifetime high (explicitly generalized by the instructor to apply to both RHS and CWH).

---

## 3.3 Strategy 6 — V10 Strategy

**Applicable universe:** Indirectly **V40 and V40 Next only** — because V10 is explicitly defined as a derivative/extension of RHS and CWH (both of which are restricted to V40/V40 Next), V10 inherits that same universe restriction. V10 cannot be used independently of an active RHS or CWH setup.

**Core definition:** V10 is NOT a standalone pattern-detection strategy. It is an **averaging mechanism that only becomes active during the life of an existing RHS or CWH trade** — specifically, V10 governs additional buy opportunities that occur via simple percentage pullbacks, while the original RHS/CWH trade's entry, target, and exit logic remain governed by their own rules (Sections 3.1 and 3.2 above).

### When V10 is "active" (window of applicability)
- V10 only applies **between the original RHS/CWH buy signal (the right-shoulder or handle breakout point) and that same trade's eventual sell/target point.**
- Before the RHS/CWH buy signal occurs: V10 is not applicable.
- After the RHS/CWH target is hit (trade closed): V10 is no longer applicable for that completed cycle — UNLESS/UNTIL a brand new RHS or CWH signal forms again later on the same stock, which would re-open a new V10 eligibility window.
- Two-stage qualification for any V10 trade: **(1)** the stock must first have an active, currently-open RHS or CWH signal/trade, **AND (2)** the specific V10 entry condition (10% pullback, defined below) must also be met within that active window.

### V10 entry condition
- **Once inside an active RHS/CWH window:** any time price **falls back (retraces/pulls back) by 10% or more from any local high/peak it has reached since the window opened**, this constitutes a V10 buy signal.
- This 10% pullback can occur from ANY peak within the window — not just from the original entry price or only from the very first peak; it's evaluated on a rolling basis against the most recent relevant local high.
- Buy is taken at the point where the 10% retracement level is hit (i.e., as soon as price is down 10% from whatever the relevant recent peak was).

### V10 exit / target condition
- Sell when price returns back up to **the same peak/level from which the 10% pullback was originally measured** (i.e., the level it retraced down from). This is a fixed, short-distance round-trip target — not the original RHS/CWH technical target.

### Averaging within V10 itself
- Multiple V10 trades can be taken sequentially/concurrently within a single active RHS/CWH window, subject to:
  - **A new V10 entry must be at least 5% lower than the previous (currently open) V10 entry** to qualify as a valid additional V10 trade (same 5%-gap structure as the Knoxville averaging rule from Video 2).
  - **Maximum of 2 concurrent open V10 trades at any one time** (separate and in addition to the original RHS/CWH trade itself).

### Combined position sizing across RHS/CWH + V10
- Each individual trade (the original RHS/CWH entry, plus each V10 entry) is sized at **3% of portfolio.**
- Maximum total concurrent trades per stock across BOTH the originating RHS/CWH trade and V10 averaging: **3 trades total** (1 RHS/CWH + up to 2 V10) → maximum **9% of portfolio** allocated to one stock at any point in time, mirroring the V20 strategy's same 9% ceiling (though arrived at via a different combination of underlying strategies).
- No stop-loss anywhere in this structure.
- No partial profit-booking — each individual trade (whether the original RHS/CWH or a specific V10 trade) is closed in full when its own specific target is hit; partial exits are explicitly described as unnecessary/not used.

### Worked example characteristics (for reference/validation only)
- Demonstrated on a live multi-cycle example (unnamed stock chart walkthrough) showing repeated V10 entries/exits within a single ongoing CWH window, with individual V10 trade gains clustered around 11-14% per cycle and holding periods ranging from about 8 days up to roughly 4.5 months per individual V10 trade.
- Stated average holding period for V10 trades specifically: **under 2 months** on average — notably shorter than typical RHS/CWH holding periods (which, per Section 3.1, can run from a few months to 1.5+ years for the overarching pattern's own target).
- Demonstrated example with Bajaj Finance simultaneously showing one open CWH trade and one open V10 trade at the same time, each with its own distinct target — illustrating that V10 and its parent RHS/CWH trade run as independent, separately-tracked positions even though they originate from the same stock and the same qualifying window.

---

## 3.4 Cross-Strategy Comparison Update (Strategies 4-6 added to the running comparison)

| Aspect | RHS (Strategy 4) | Cup with Handle (Strategy 5) | V10 (Strategy 6) |
|---|---|---|---|
| Applicable universe | V40 + V40 Next | V40 + V40 Next | V40 + V40 Next (inherited from RHS/CWH) |
| Type | Chart pattern | Chart pattern | Derivative/averaging mechanism on RHS or CWH |
| Indicator required | None | None | None |
| Entry signal | Breakout (green candle, closing basis) from FIRST right shoulder's base formation | Breakout (green candle, closing basis) from FIRST handle's base formation | 10%+ pullback from any local peak, during an active RHS/CWH window |
| Exit signal | Higher of (Technical Target, Lifetime High) | Technical Target only (never raised to lifetime high) | Return to the peak level the 10% pullback was measured from |
| Execution timing | Same-day (late session) or next-day open | Same-day (late session) or next-day open | Not separately specified; presumably same as RHS/CWH (intraday-aware, next-day default) |
| Position size (initial) | 3% of portfolio | 3% of portfolio | 3% of portfolio per V10 entry |
| Averaging allowed? | Not separately defined (handled via V10) | Not separately defined (handled via V10) | Yes — new V10 entry must be ≥5% lower than prior open V10 entry |
| Max trades per stock | 1 (own trade) + up to 2 via V10 | 1 (own trade) + up to 2 via V10 | Max 2 concurrent V10 trades, on top of 1 RHS/CWH trade = 3 total |
| Max allocation per stock | Up to 9% when combined with V10 (3% RHS/CWH + 3%+3% V10) | Same as RHS — up to 9% combined with V10 | Counted within the same 9% combined ceiling |
| Stop-loss used? | No | No | No |
| Optional gain filter | ≥40% potential gain recommended; MANDATORY if pattern forms at lifetime high | Same as RHS | N/A (target is fixed at 10% round-trip, not a percentage filter on setup quality) |

## 3.5 General Operating Rules Added/Reinforced in Video 3

- **Pattern validity requires geometry, not narrative:** a chart pattern's validity depends only on its geometric/candle-based confirmation (base formation, green candle, closing-basis breakout) — NOT on whether a "reason" for the preceding price decline can be identified or justified. The agent should never use news sentiment, headlines, or "why did this stock fall" reasoning as an input to whether a pattern is valid.
- **Patience / no fixed holding period (reiterated and strengthened):** explicitly restated that holding periods and volatility remain outside the trader's control, with several real multi-month examples of flat/sideways price action before pattern resolution. This is the same "4 things in control / 2 things not in control" framework from Video 2, reinforced here with concrete pattern-specific examples.
- **No partial profit booking:** confirmed explicitly in Q&A — each trade (regardless of which of the 6 strategies it belongs to) is held until its full defined target is hit, then exited completely; no scaling out partially.
- **Position-count discipline reaffirmed:** never exceed the per-strategy maximum concurrent trade count (1 for SMA; 2 for Knoxville; 3 for V20; and now, combined across RHS/CWH+V10, 3 total for that pattern-pair) and never exceed the resulting max portfolio allocation per stock (3% / 6% / 9% depending on strategy, as established in Video 2 and now confirmed to also apply to the RHS/CWH/V10 trio).
- **No outsourcing of pattern discovery to a group/community chat** — explicit Q&A answer: the instructor declined a participant's suggestion to create a shared alert group for spotting patterns collaboratively, reasoning that people who rely on others' signals rather than their own independently-verified analysis become dependent and don't develop genuine skill, and that anyone who has built significant wealth in markets has done so through independent decision-making rather than crowdsourced/relayed signals. **Flag for agent design:** this suggests the tool's UX should support a single user's independent decision-making (presenting clear signals/reasoning for that user to verify) rather than a multi-user social/sharing feature, per the instructor's own stated philosophy — worth keeping in mind if the product direction ever considers a community/social layer.
- **Strategy selection is personal/flexible, not mandatory to use all of them:** reaffirmed that a trader does not need to use all 7-8 strategies — picking even just 1-2 strategies and using them with discipline is described as sufficient (reinforced via the real ₹5.5L→₹21L anecdote using only the Knoxville strategy). The agent should be designed to let a user select/configure which subset of strategies to actively run, rather than assuming all strategies must always be active simultaneously.
- **Recommended reading (context, not a rule):** Zerodha Varsity (free educational site) for foundational concepts; books by Peter Lynch in this specific order — "Learn to Earn," "One Up On Wall Street," "Beating the Street"; "The Secret" (mentioned previously in Video 1) and "Stock Market Wizards"/"Trade Like a Champion"/"Momentum Masters" by/about Mark Minervini (cited, with a caveat — see next point). Not agent logic, but potentially useful as a "further reading" feature if the eventual product includes educational content.
- **Notable caution/nuance about purely technical/indicator-based trading without fundamental quality filtering:** the instructor specifically critiques Mark Minervini (a well-known, publicly-documented technical trader) as an example of someone who has made significant money using pure technical analysis but has been unable to "retain" or consistently compound it over the long run, attributing this to reliance on stop-losses and lack of fundamental-quality filtering causing losses during down/sideways markets. This is presented as supporting evidence for this course's combined approach (fundamental quality gate + technical entry/exit, no stop-loss) rather than pure technicals alone. **Flag for agent design:** reinforces that the V40/V40Next/V200 fundamental gate is not optional context — it's treated by the instructor as the primary reason these strategies are claimed to work better than generic technical trading.

## 3.6 Open Questions / Build Flags from Video 3

1. **Pattern-recognition is a fundamentally different engineering problem than indicator-threshold logic.** SMA, Knoxville, and V20 (Video 2) can be expressed as relatively clean, deterministic rules over OHLC data. RHS and Cup with Handle (this video) require geometric/visual pattern recognition (identifying shoulders, heads, cups, handles, base formations, horizontal neckline tolerance, etc.) which is inherently fuzzier and more subjective — the instructor himself relies on visual judgment ("with practice you will be able to do it instantly," "we can consider this as a base even though there's a doubt"). This will likely require either (a) a custom pattern-detection algorithm with tunable tolerance parameters, or (b) a human-in-the-loop review step where the tool flags candidate patterns for manual confirmation rather than fully automating entry signals. Recommend the latter as a safer initial architecture given the subjectivity described in the source material itself.
2. The "base formation" concept (used in RHS, CWH, and indirectly V10) is repeatedly described qualitatively ("3 candles can be enough, or it might need more, depending on the size of the overall move") without a precise minimum-candle-count or range-tightness threshold. This is a parameter the agent will likely need to either ask the user to tune, or default to a conservative heuristic (e.g., minimum N candles with price range under X% of the move's depth) pending further clarification from later videos.
3. No explicit rule was given for what happens if an RHS pattern and a CWH pattern both appear to be forming on the same stock simultaneously (since CWH is structurally "RHS without the left shoulder," ambiguity could arise in real data about which classification applies, especially in early stages of pattern formation before it's clear whether a left shoulder will appear). Flag as an edge case requiring either a tie-breaking rule or dual-tracking until disambiguated.
4. The "complex pattern more reliable than simple pattern" claims (for both RHS and CWH) are asserted without a quantified reliability metric (e.g., no stated win-rate difference between simple vs. complex patterns) — log as a qualitative heuristic only, not something to hard-code as a scoring weight without further data/validation.
5. Fundamental/financial analysis session (referenced as "tomorrow's session," i.e., the next video chronologically) is still pending — V200's exact qualifying metrics were given in Video 1, but a deeper "how to read a balance sheet for this purpose" methodology is expected next and should be cross-checked against/integrated with the V200 criteria once received.

---//---

# VIDEO 4 — Fundamental / Financial Analysis Deep Dive

**Source:** Class 4 (live session) of Vivek's Online Stock Market Course (English), YouTube
**Content type:** This video contains **no new trading strategies** — it is the promised fundamental/financial analysis session referenced at the end of Video 3. It teaches HOW to read and interpret financial ratios/figures for the purpose of stock selection, deliberately staying shallow on accounting mechanics ("we don't need to become a chartered accountant") and focused only on the handful of metrics that actually matter for filtering good companies. This content directly refines and extends the V200 criteria and general "good company" qualitative gate established in Video 1, and should be treated as an elaboration layer on top of that existing gate — not a replacement for it.

## 4.0 Framing: Three Dimensions of Analysis (restated/clarified from earlier videos)
The instructor explicitly separates "fundamental analysis" into two distinct sub-components, and adds technical analysis as the third pillar overall:
1. **Business analysis** (covered in Video 1) — low penetration, future growth runway, Google-research-driven qualitative judgment.
2. **Financial analysis** (this video) — balance sheet and P&L ratio interpretation.
3. **Technical analysis** (covered in Videos 2-3) — chart-based entry/exit timing.

Explicit warning given: many experienced market practitioners (including some who teach/write books) skip business analysis entirely and focus only on financial/technical analysis — this is called out as a mistake. **Sequencing implied for the agent's decision pipeline: business-quality filter → financial-ratio filter → technical entry/exit signal**, not the reverse, and not financial/technical alone without the business-quality layer.

## 4.1 Two Forms of Every Financial Metric — Per-Share vs. Whole-Company
Foundational framing rule, applies to nearly every metric below: almost all financial data exists in two parallel forms, and the agent must always know which form it's looking at and convert correctly between them when comparing companies.
- **Per-share form:** e.g., current market price (share price).
- **Whole-company form:** e.g., market capitalization.
- Formula: `market_capitalization = total_number_of_shares * current_market_price`
- **Critical clarification on "total number of shares":** this means the literal total share count outstanding for the company — NOT shares held only by promoters, or only by FIIs/DIIs, or only by retail. It is the full share count, used to scale per-share price up to whole-company value.

## 4.2 Market Capitalization — "the most important number to look at, always"

### Why it matters more than current share price
- Comparing companies by **share price alone is meaningless** (e.g., a ₹91,000 share price does not imply a "bigger" or "more expensive" company than a ₹600 share price) — only market capitalization tells you the actual size of the company.
- Worked example: LIC (share price ₹628) vs. MRF (share price ₹91,000) — despite MRF's far higher per-share price, MRF's market cap (~₹38,000 cr) is roughly 1/10th of LIC's (~₹3,97,000+ cr).

### Core technique: Market-cap ratio between a smaller company and the category/sector leader = multibagger potential indicator
This is the same logic introduced informally in Video 1 (Britannia vs. Mrs. Bector's, Asian Paints vs. Indigo Paints) but is now generalized into an explicit, repeatable analytical technique:
```
gap_multiple = leader_market_cap / smaller_company_market_cap
```
- If `gap_multiple` is large (e.g., 10x, 40x, 100x) AND the smaller company has comparable brand reputation / product overlap / similar growth trajectory potential to the leader, this is read as a signal that the smaller company has room to "catch up" in valuation over time (NOT a guarantee, and NOT a short-term signal — explicitly described as potentially taking 10+ years to play out).
- **Important nuance/caveat added in this video (refines the Video 1 framing):** a market-cap gap alone is NOT sufficient — it must be checked against **revenue gap** as a sanity check. Worked example: Page Industries (~₹55,000 cr market cap) vs. Lux Industries (~₹5,000 cr market cap) = 11x valuation gap, but their actual revenue gap is only ~2x (Page ~₹4,700 cr/year vs. Lux ~₹2,400 cr/year). This means Page Industries is "extremely overvalued" relative to Lux on a revenue basis — i.e., **the market-cap multiple should be checked against the revenue multiple; a large divergence between the two ratios signals potential over/under-valuation, not necessarily catch-up opportunity.**
  - **Codify this as an explicit, reusable check:** `valuation_gap_ratio = leader_market_cap / smaller_market_cap` vs. `revenue_gap_ratio = leader_revenue / smaller_revenue`. If `valuation_gap_ratio >> revenue_gap_ratio` for the SAME pair (i.e., the market is pricing a much bigger gap than the actual business-size gap justifies), flag the larger company as potentially overvalued / smaller company as potentially undervalued, all else (brand quality, business quality gate) being equal.
- Companion example given showing two companies with near-identical market caps and near-identical revenue (Bata ~₹23,000 cr market cap & similar revenue scale vs. Relaxo ~₹23,000 cr market cap, revenue ~₹2,779 cr vs. Bata ~₹3,000 cr, <10% difference) — used to illustrate that when market-cap ratio and revenue ratio roughly AGREE, that is a sign of fair/consistent relative valuation, not a mispricing signal — reinforcing the check above by showing the "no flag" case.
- **Explicit causal investigation example (Lux Industries case):** when a valuation gap suddenly opens up between two previously-comparable companies, the agent's reasoning should ask "did this gap emerge from a fundamentals change, or from an external/non-business event?" In the worked example, Lux Industries' stock fell ~55% over one year due to a SEBI insider-trading penalty on a management-adjacent individual (not a business or financial deterioration) — explicitly flagged as a *temporary, sentiment/reputational* event rather than a fundamentals problem, and therefore presented as a buying opportunity rather than a red flag. **This reinforces the same principle from Video 3 (don't filter on "reason for decline") but adds a more specific test: did the news event affect the BUSINESS/FINANCIALS, or only the STOCK PRICE/sentiment? If only the latter, it doesn't invalidate the company for the quality gate.**

### Worked examples logged for reference (not separate rules, just supporting data points)
- Britannia (~₹91,000 cr) vs. Mrs. Bector's Food (~₹2,200 cr): ~40x+ gap; Britannia itself returned ~73x (~7,300%) over the 20 years to time of recording — used as evidence that large compounding multiples are realistic over long (10-20 year) horizons for category leaders, lending plausibility to the smaller comparable's catch-up thesis.
- Punjab National Bank (~₹46,000 cr market cap) vs. Kotak Mahindra Bank (~₹3,77,000 cr market cap): ~8x gap — but here the instructor explicitly notes PNB's underlying lendable capital base (own funds + borrowings, ~₹13 lakh cr) is actually LARGER than Kotak's (~₹4.5 lakh cr), meaning the valuation gap is disconnected from balance-sheet capacity, attributed to historical NPA/scam-driven profitability suppression rather than current capacity — flagged by the instructor as a gap he expects to narrow as legacy NPA issues (all originating pre-2014, per the instructor) finish working through the system. **Flag for agent: this is a thesis specific to PSU banks and a particular macro/cleanup narrative — treat as illustrative reasoning, not a generalizable rule with a programmable trigger condition (no clean quantitative threshold was given for "how much NPA cleanup before this re-rates").**
- 5paisa (~₹981 cr market cap) vs. Angel One (~₹13,000 cr market cap): ~13x gap, tied to India's low stockbroking penetration (~2% of population participating vs. ~65% cited for the US) as the growth-runway justification.
- Indigo Paints (~₹7,338 cr) vs. Asian Paints (~₹3,00,000+ cr): ~40x gap; Asian Paints itself returned ~99-100x over ~20 years (2003 to time of recording) — same "category leader's own long-run multiple" supporting logic as the Britannia example.
- Dabur book value (~₹9,000 cr) vs. market cap (~₹98,000 cr) — ~10x premium to book, attributed explicitly to brand value not captured in book value (see Section 4.4 below for the general book-value rule this exemplifies).

## 4.3 PE Ratio (Price-to-Earnings) — Explicitly Downgraded to "Not Relevant" for This Strategy Framework

### Definition and calculation (simplified, whole-company basis preferred over per-share)
```
PE = market_capitalization / net_profit (annual)
```
(Per-share equivalent: share_price / earnings_per_share — same ratio, instructor explicitly prefers the whole-company framing for intuition.)

### Core interpretation: PE = "payback period" in years
- PE is reframed as: **how many years it would take to recoup the full purchase price of the company via its current (unchanging) net profit.**
- Worked example: Asian Paints, market cap ~₹3,05,000 cr ÷ net profit ~₹3,500 cr/year ≈ 81-year payback period at that snapshot.
- **Critical caveat that breaks the naive interpretation:** net profit is not static — it grows. Worked example: HDFC Bank traded at ~PE 30 roughly 10 years prior (per the video's timeline) when net profit was ~₹5,200 cr/year; by compounding net profit growth, cumulative profit over the following ~8 years alone exceeded the original ~₹1,50,000 cr market cap, meaning the "30-year payback" thesis was wrong because profit growth compressed the real payback period to roughly 8 years.

### Resulting rule for this framework
- **A high PE is NOT inherently bad, and a low PE is NOT inherently good** — explicitly stated as the core takeaway: "if PE is low, this is good; if PE is high, this is NOT bad." The determining factor is the company's net profit GROWTH RATE, not the static PE snapshot.
- Companion example: Coal India's PE is low (~6.5x) but its net profit has been essentially flat for ~9 years (₹17,000 cr in March 2013 vs. similar in March 2022) — used to show that a low PE accompanied by flat/no profit growth is NOT actually a bargain; it's correctly priced for a non-growing business. Most PSU companies are cited as falling into this low-PE/low-growth pattern.
- **Explicit conclusion for the agent's logic:** PE ratio should be treated as **largely irrelevant for stock selection/screening purposes within this framework** ("totally irrelevant... we just need to ignore it"), EXCEPT in the specific case of deliberately seeking deep-value/ultra-cheap stocks — which is explicitly stated to be outside the scope of this trading approach ("we are traders, not long-term value investors hunting for cheap stocks"). **Agent implication: do NOT use PE as a primary or even secondary screening filter for any of the 6 documented strategies or the V40/V40Next/V200 gate.** It can optionally be surfaced as informational/contextual data in a UI, but should carry no decision weight.

## 4.4 Book Value, Face Value, Equity, and Share Capital — Definitions and Relationships

### Core definitions (precise, foundational — get these exactly right in any data model)
```
share_capital = total_number_of_shares * face_value
```
- **Face value** = the original/initial per-share investment amount when the company was first capitalized (per-share form of share capital).
- **Share capital** = face value, expressed as a whole-company total (i.e., the initial capital injected to start the company).
- **Reserve** = cumulative retained net profit/earnings accumulated over the company's life (i.e., profit that was made and kept inside the company rather than distributed).
```
book_value (whole company) = share_capital + reserve
equity = book_value (the terms are used interchangeably for the whole-company figure)
book_value_per_share = (share_capital + reserve) / total_number_of_shares
```
- **Critical distinction to keep straight:** face_value is ALWAYS the per-share view of the ORIGINAL capital only (never includes reserve). Book_value/equity always includes BOTH the original capital AND all accumulated reserve.

### Why book value can dramatically understate true company worth (a real-asset blind spot)
- Land and other fixed assets are recorded on the balance sheet at **historical purchase cost** and are explicitly stated to **never get revalued** upward over time on the books, regardless of actual current market value.
- Worked example: Mawana Sugar — book-recorded land value ~₹19 crore for an ~800-acre site across two large sugar mills, while the instructor estimates real current market value of comparable land at "at least ₹5 crore per acre," implying a real value of roughly ₹4,000 crore — vastly higher than the ~₹19 crore book figure. **Agent implication: book value (and therefore any book-value-based ratio) can substantially UNDERSTATE true asset backing for asset-heavy/old-economy businesses (sugar, paper, similar land/factory-heavy industries) — this is a known limitation of the book value metric, not a flaw in the company.**
- Related industry-structure insight (context, not a separate numeric rule): industries requiring large contiguous tracts of specific land (e.g., sugar — must be near sugarcane fields; paper — must be near forest/plantation land) have a natural **entry barrier** for new competitors, since replicating the land footprint today would cost far more than what incumbents paid historically — used as supporting qualitative reasoning for durable competitive position/pricing power (ties back to the Video 1 "pricing power" business-quality condition), not as a new standalone screening rule.

### Resulting interpretation rule for Book Value vs. Share Price
- **If share price < book value → this is GOOD** (stock trading below its accounting net worth).
- **If share price > book value → this is NOT BAD, i.e., neutral/acceptable, NOT a red flag** — explicitly because strong brands carry value (brand equity, customer loyalty, market position) that is never reflected in book value at all. Worked example: Dabur trading at ~10x book value (book value ~₹9,000 cr vs. market cap ~₹98,000 cr) attributed entirely to brand value from decades-old product lines, explicitly NOT a sign of overvaluation by itself.
- Real M&A datapoint supporting the "brand value isn't in the book" point: Hindustan Unilever's acquisition of the Horlicks brand for a price (~₹40,000+ cr per the video, paid substantially via share issuance) that was roughly 5x HUL's ENTIRE pre-acquisition book value (~₹8,000 cr reserve) for a SINGLE BRAND — used to argue that brand value is real and economically large even though it never appears on a standalone basis in the acquirer's or target's book value figures pre-transaction.
- **Agent implication: like PE, book-value-vs-price comparison should NOT be used as a disqualifying filter.** A stock trading well above book value should not be penalized in scoring; a stock trading below book value can be treated as a mild positive signal but is not required.

## 4.5 Dividend Yield — Explicitly Downgraded to "Not Important At All"
- High dividend yield is reframed as a **negative-leaning signal about growth**, not a positive one: a company paying out a large share of profit as dividend is, by definition, NOT reinvesting that capital into expanding the business — interpreted as a sign of limited growth opportunity rather than shareholder generosity.
- Worked example: Coal India dividend yield ~6.9% (~10% in some framing) but stock price has been flat-to-down over a ~12-year window (listed ~₹348, trading ~₹246 at time of recording) — used to show that high yield does not compensate for lack of capital appreciation in this trading framework.
- Explicit guidance: **"we should never buy any stock just for the sake of dividend"** — if dividend income is the actual goal, a fixed deposit is described as a more appropriate (principal-safe) instrument than equities. **Agent implication: do NOT use dividend yield as a positive screening factor anywhere in this framework. It may be surfaced as informational data but should carry zero positive scoring weight, and a very high yield combined with stagnant price history could optionally be flagged as a mild caution signal (low growth reinvestment) rather than an attractive feature.**

## 4.6 Return on Capital Employed (ROCE) — Confirmed as One of the Most Important Metrics

### Definition (conceptual, as explained — not a new formula beyond what's already standard)
- Measures how efficiently a company converts its total available capital (own funds + borrowed funds) into profit — described as reflecting both product/market quality AND management capability simultaneously. Explicitly stated that even excellent management cannot produce a high ROCE if the underlying product/market lacks pricing power or competitive strength (worked examples: Bharti Airtel — "excellent management" but debt-heavy balance sheet and profit-constrained due to lack of telecom pricing power/brand differentiation versus Reliance Jio; Vodafone Idea — same management group that successfully runs UltraTech Cement, yet unable to make the telecom business profitable, attributed to the product/competitive position rather than management skill).

### Explicit tiered interpretation scale (directly usable as a scoring/filter function)
| ROCE | Rating |
|---|---|
| > 30% | **Best** |
| 20%–30% | **Very good** |
| < 20% | Below the acceptable threshold for this framework — explicitly stated: "we are not trading in that company" if ROCE is below 15-20%, language was slightly inconsistent between "15%" and "20%" in different parts of the transcript, but the V200 hard rule from Video 1 (ROCE > 20%) should be treated as the operative numeric floor; treat any ROCE 15-20% mention in this video as softer/conversational rather than overriding the hard 20% threshold already established |

- **Explicit rarity claim:** sustaining >30% ROCE consistently is described as rare globally, not just in India ("very few companies in the world... this is beyond capabilities") — reinforces that the >30% tier should be treated as a strong positive differentiator/ranking signal when multiple qualifying candidates are being compared against each other, not merely a pass/fail cutoff.
- **Explicit tie-breaking rule given:** when choosing between multiple stocks that all otherwise qualify (pass the V40/V40Next/V200 + strategy signal gates), **preference should be given to the stock with the higher ROCE tier** (>30% preferred over 20-30%, when a choice must be made due to limited capital/opportunity slots). This is a usable, concrete portfolio-construction tie-breaker rule for the agent.
- **Reconfirms (does not change) the Video 1 V200 rule:** ROCE > 20% for non-BFSI companies remains the hard qualifying threshold; this video adds the qualitative tiering ABOVE that threshold (20-30% "very good" vs. >30% "best") as a refinement for ranking/prioritization among already-qualifying candidates, not a change to the qualification bar itself.

## 4.7 Return on Equity (ROE) — Relevant Only for Banking/Financial Companies
- Explicitly stated as **not relevant/ignorable for non-financial companies** — ROE is only used as a metric in this framework for banks and NBFCs (consistent with the Video 1 V200 exception rule: ROE > 10% replaces the ROCE > 20% test specifically for banks/NBFCs, since ROCE doesn't translate meaningfully for lending-based business models). No new threshold given here beyond what Video 1 already established (>10%) — this video simply reconfirms the same number and clarifies its scope is limited to BFSI-type companies only, mirroring the ROCE-not-applicable logic in reverse.

## 4.8 Debt-to-Equity Ratio — Tiered Interpretation (refines the Video 1 single threshold)

### Formula reconfirmed
```
debt_to_equity = total_borrowings / equity
```
where `equity = share_capital + reserve` (same as book value, per Section 4.4).

### Explicit tiered interpretation scale (refines/extends the Video 1 single "< 0.25" V200 threshold into a ranked scale)
| Debt/Equity | Rating |
|---|---|
| < 0.10 (i.e., <10%) | **Best** |
| 0.10–0.25 (10%–25%) | **Very good** |
| > 0.25 (>25%) | **"Lakshman Rekha"** — an explicit line that should not be crossed; treated as the hard disqualifying ceiling |

- This directly matches and refines the Video 1 V200 rule (`debt_to_equity < 0.25`) by adding an internal "best vs. very good" tier below that ceiling, exactly mirroring the ROCE tiering pattern in Section 4.6 — **use the same tie-breaking logic: when multiple candidates qualify, prefer the lower debt/equity tier.**
- **Explicit exception, reconfirmed and broadened from Video 1:** debt/equity is **NOT applicable/relevant at all for banks and NBFCs** (their business model IS lending/borrowing, so high leverage is structurally normal, not a risk signal in the same sense). **New clarification added in this video:** this exception should be extended to any company that is **functionally** in the lending business even if not formally classified as a bank/NBFC — explicit example given: stockbrokers (e.g., for providing margin trading facilities and charging interest) should also be exempted from the debt/equity ceiling, for the same structural reason. This generalizes/reinforces the Angel One precedent already noted in Video 2 (Section 2.4) where Angel One was treated as functionally an NBFC despite not being formally licensed as one.

## 4.9 Promoter Holding Percentage — Explicitly Downgraded; Replaced by "Strong Hands vs. Weak Hands" Framework

### Core claim: raw promoter-holding percentage is NOT a useful quality signal on its own
- Directly contradicts a common popular heuristic ("more promoter holding = better, less = worse"). Multiple paired examples given showing both high- and low-promoter-holding companies that are equally high-quality: Dabur (67% promoter) vs. TCS (72%) vs. HCL (60%) vs. Infosys (15%) vs. Kotak Mahindra Bank (26%) vs. ICICI Bank (~0%, no promoter at all). **Agent implication: do NOT use raw promoter holding percentage as a standalone screening or scoring input.**

### Replacement framework: Strong Hands vs. Weak Hands (first introduced conceptually in Video 1, now given a precise computable formula)
```
strong_hands_pct = promoter_pct + FII_pct + DII_pct + HNI_pct
weak_hands_pct = retail_public_pct   (i.e., total public_pct MINUS HNI_pct)
```
- Recall from Video 1: HNI = any shareholder individually holding >1% of the company who is not classified as a promoter or institution.
- **New explicit screening rule given in this video:** `retail_public_pct` (the weak-hands-only figure) **should not exceed 30%** of total shareholding. Rationale: if more than 30% of a company is held by retail public (who have no direct voice with the board of directors, unlike large institutional/HNI holders who can engage management directly), this is read as a mild governance/quality concern — there's no clear reason why "smart money" (strong hands) wouldn't want a larger stake in a genuinely good company, so unusually high retail concentration is treated as a soft caution flag rather than a hard disqualifier (note: this is presented as a heuristic filter the instructor uses, with one real counter-example given — Karnataka Bank, >70% retail public, trading at roughly half its book value — used to illustrate the heuristic's predictive direction, not to claim it always holds with statistical certainty).
- Worked supporting examples: Axis Bank retail-public-only ~7-8% vs. HDFC Bank ~14% — used in the video to illustrate a relative comparison between two otherwise-similar banks (presented as directional/comparative color commentary on relative institutional conviction, not as a hard pass/fail claim that either bank fails or passes a specific numeric test in isolation).
- **Codify as an agent rule:** `IF retail_public_pct (weak hands only, excluding HNI) > 30%: flag as a soft caution / lower-priority candidate`, but do not treat this as an automatic disqualification given the explicit caveat that it's a heuristic, not an absolute rule.

## 4.10 Promoter Pledging Percentage — Precise Definition and a New Hard Disqualifying Formula

### Critical definitional clarification (commonly misunderstood, per the Q&A in this video)
- **"Pledging percentage" refers EXCLUSIVELY to shares pledged by PROMOTERS, not by any other shareholder class, and not by the company itself.** The company does not pledge shares (since shares are owned by shareholders, not held as a company asset); when a company itself needs a loan, it pledges its own ASSETS (property, equipment, etc.), not shares. Pledging activity refers strictly to a promoter using their personal shareholding as loan collateral in their own personal/entity capacity, separate from the company's own balance sheet.
- **Pledging percentage is expressed as a percentage OF THE PROMOTER'S OWN HOLDING, not of the company's total shares.** E.g., if a promoter owns 30% of a company and pledges 1% of THEIR OWN holding, the reported "pledging percentage" reflects that 1%-of-30% slice — it does not mean 1% of the whole company is pledged. (This distinction matters for correctly computing the disqualifying formula below.)

### Why pledging matters (risk mechanism)
- If a promoter cannot repay a loan that was collateralized with pledged shares, the lending bank has the right to sell those pledged shares on the open market to recover the loan — and large forced sales of this kind can crash the stock price independent of the underlying business's actual health. Two real-world examples cited as cautionary precedents: Zee Entertainment (founder Subhash Chandra's pledged shares triggering forced selling/price collapse despite the company itself not being especially over-leveraged) and the broader Reliance ADAG group collapse (Reliance Communication, Reliance Power, Reliance Capital, Reliance Infra) attributed to inter-company loan/pledging chains where delays in one business (Reliance Power) cascaded into inability to service debt secured against shares of other group companies.
- A separate, NOT-inherently-bad example of legitimate pledging activity was also given (Vedanta/Twin Star Holdings increasing promoter stake from ~50% to ~69-70% over time by borrowing against pledged shares to buy more shares on the open market, partly funded by high dividend payouts used to service that debt) — included to show that pledging itself is not automatically a red flag; the RISK materializes specifically when repayment becomes uncertain, e.g., if a side-business or expansion plan funded this way underperforms.

### Explicit, computable disqualifying formula
```
IF (promoter_holding_pct * pledging_pct_of_promoter_holding) >= 10%:
    AVOID this stock entirely
```
- Plain-language restatement of the formula's meaning: if the pledged shares, when expressed as a percentage of the COMPANY'S TOTAL shares (not just the promoter's own holding), would amount to 10% or more of the whole company, treat this as a hard disqualifying condition. **This is a genuinely new, hard, computable screening rule — distinct from and additional to the existing V40/V40Next/V200 gate and the 6 trading strategies' own rules.** It should be applied as an ADDITIONAL filter layer that can disqualify an otherwise-V40/V40Next/V200-qualifying stock.
- Rationale restated directly: "we are managing our own money... there is no need to take any risk... never compromise in selection of a company." Framed as a zero-tolerance risk-avoidance rule rather than a soft preference.

## 4.11 Consolidated vs. Standalone Financial Statements — Reporting Convention Rule
- **Definitional distinction:** "Standalone" = the parent company's own financials only. "Consolidated" = parent company's financials PLUS all subsidiary companies it owns/controls, combined. Worked examples: Tata Motors + Jaguar Land Rover (JLR) as a subsidiary — Tata Motors' true business performance should be evaluated via consolidated figures (which include JLR), not standalone-only figures that would omit JLR entirely.
- **Explicit rule: always use CONSOLIDATED figures when available; only fall back to standalone if no consolidated option exists** (i.e., the company has no subsidiaries).
- **Important UI/data-source gotcha flagged explicitly (specific to Screener.in's interface, worth encoding as a parsing/scraping rule if the agent automates data pulls):** Screener.in's toggle button is labeled with the OPPOSITE of what's currently being displayed — i.e., if the button visibly reads "View Consolidated," the data CURRENTLY on screen is actually STANDALONE (clicking the button switches you in to consolidated view); conversely if the button reads "View Standalone," the data currently on screen is actually CONSOLIDATED. **This is a non-obvious, easy-to-invert parsing trap if building any automated scraper/integration against Screener.in's UI or any HTML structure that mirrors this same button-labeling convention — must be handled correctly to avoid silently pulling the wrong statement type.**

## 4.12 Quarterly Results — Year-over-Year Comparison Rule (not quarter-over-previous-quarter)
- **Explicit, hard rule: quarterly revenue and quarterly net profit must always be compared against the SAME QUARTER from the PREVIOUS YEAR** (e.g., compare this September quarter to last year's September quarter), **never against the immediately preceding quarter** (e.g., never compare September quarter to the prior June quarter in isolation).
- **Rationale: most businesses have seasonal demand patterns**, so sequential-quarter comparisons would be misleading. Worked examples: Asian Paints sells more in the September quarter (monsoon/festive prep) than in the March quarter; Titan sells more in the December and September quarters (wedding season, festive season) than in the March quarter. Comparing across different quarters within the same year would incorrectly read normal seasonality as business deterioration or acceleration.
- **Agent implication: any automated quarter-over-quarter growth calculation used for screening or signal generation must default to YoY (same quarter, prior year) comparison, not sequential QoQ comparison**, unless a specific strategy/use case explicitly calls for sequential comparison for a different stated purpose.

## 4.13 "Other Income" — A Quality/Consistency Check, Not a Separate Screening Metric
- **Definitional split within total revenue reporting:** "Sales" = revenue directly from the company's core/main business operations. "Other income" = income that may be recurring but is NOT from the core business (e.g., interest earned on fixed deposits, dividends received from investments in other companies, rental income from a property not used in core operations).
- **Quality check to apply:** Other income should be examined for **consistency/normalcy across quarters** — large, irregular spikes or troughs in the "other income" line (worked example given showing one quarter with a large negative other-income figure, the next quarter showing an unusually large positive figure, before returning to a more typical, smaller, consistent baseline in subsequent quarters) can indicate **timing manipulation of revenue/profit recognition** (i.e., a sale that should logically belong to one quarter being deliberately booked a few days into the next quarter, or vice versa, to influence how a given quarter's results appear) rather than a real change in business performance.
- **This is presented as a "be aware of this possibility" due-diligence note, not a hard quantitative rule with a specific numeric threshold for what counts as "abnormal."** No specific percentage-variance trigger was given (e.g., no stated rule like "flag if other income varies more than X% quarter to quarter"). **Flag for agent design:** if implemented, this would need either a human-review flag for unusually volatile other-income line items, or an arbitrarily-chosen variance threshold pending further guidance from the instructor — do not silently invent a specific numeric cutoff that wasn't actually stated.
- **[Part 2 update — worked example confirms and sharpens this rule]:** A real example was walked through (an unnamed company) where net profit dropped from ~₹11,000cr (Dec 2019 quarter) to ~₹6,500cr (March 2020 quarter) even though operating revenue/operating profit were barely affected — the entire gap was attributable to an "other income" item being deliberately deferred into the following quarter. Stated motive: it was acceptable to let that quarter's headline profit look weaker because the whole market was falling anyway (pandemic onset) and no one would scrutinize it closely; deferring the income to the following quarter (when a private placement/stake-sale-type event involving Facebook/Microsoft and other investors was expected) allowed that later quarter to show a profit "run-up" that would support the stock price at a more opportune time. **This is now confirmed (not merely hypothesized) as a real, intentional operator/promoter tactic** — not just a theoretical possibility. **Concrete agent rule that can now be derived from this confirmed example:** flag any quarter where (a) operating revenue and operating profit are roughly flat/normal YoY, but (b) net profit moves sharply, AND (c) the swing is concentrated in the "other income" line specifically — this combination is a stronger, more specific manipulation signal than "other income varies" alone. Still does not warrant an auto-reject; treat as a flag to discount that specific quarter's headline net-profit figure when evaluating the stock, not a reason to exit a position or disqualify the company itself.

## 4.14 Stock-Selection Priority Principle (explicit, repeated framing point — useful as an agent design philosophy statement)
- **Explicit instructor statement, worth preserving verbatim in spirit:** company/stock selection (via business + financial analysis) is more important than technical analysis/entry timing. A good company bought at a slightly suboptimal technical price will likely still work out over time; a bad/mediocre company bought at a technically "perfect" price is much more likely to fail. **Agent implication: if forced to choose where to apply stricter automated rigor vs. allow more flexibility/human judgment, the fundamental-quality gate (V40/V40Next/V200 + the ratio thresholds in this video + the pledging disqualifier) should be treated as the LESS negotiable layer, and technical entry-timing as the comparatively MORE negotiable layer** (consistent with multiple worked examples across Videos 3-4 showing successful trades despite "imperfect" technical entries, but no successful examples shown anywhere in the source material of a fundamentally weak company working out well).

## 4.15 [NEW — Part 2] "One Bad Quarter Doesn't Matter" Rule — Important Filter for Reacting to Quarterly Results

### The core rule
- **Explicit, repeated rule: once a company has an established track record of 10+ years of solid stock-price performance AND solid underlying business/revenue/profit growth, a single quarter of weak results should NOT be treated as a meaningful negative signal.** Neither the product nor the management has "failed" on the basis of one weak quarter — these are described as essentially noise relative to the long-run trend.
- **Direct agent implication — this REFINES (does not contradict) the YoY quarterly comparison rule in Section 4.12:** the YoY comparison methodology is still correct and should still be computed, but the agent must NOT treat a single quarter's YoY decline as a sell/avoid signal in isolation for a stock that already otherwise passes the V40/V40Next/V200 + ratio-based fundamental gate. A weak quarter on an already-qualified, long-track-record stock should be treated as **a potential BUYING opportunity (price weakness on temporary/non-structural grounds) rather than a warning sign**, consistent with the broader "operators trigger retail selling at exactly these moments" theme already established in Videos 3-4.
- **Sector-wide context check (reinforces and extends the ACC/Ambuja/Shree Cement example already logged under Section 4.x material from Part 1):** when evaluating a single weak quarter, check whether OTHER companies in the same sector/peer group are also reporting weak numbers in the same period. If the whole sector is down together (e.g., a commodity-input-cost spike hitting all cement makers simultaneously), this confirms the weakness is cyclical/sector-wide rather than company-specific — reinforcing that it's not a red flag on the specific company's management or product. If a company's results are weak while peers are NOT also weak, that would warrant more scrutiny (this directional comparison logic was already established in Part 1 and is reconfirmed/reused here for the same purpose).

### Two new worked examples reinforcing this rule
- **Relaxo Footwears & Havells:** both posted a YoY decline in the most recent quarter discussed, but when viewed against each company's multi-year net profit trend (with the same "other income" abnormality-detection lens from Section 4.13 applied to clean up some of the historical comparison points), the long-run trajectory is consistently upward. Conclusion drawn: a stock price decline driven by this kind of single weak quarter is "just an opportunity, nothing else."
- **Reliance Industries — accounting/tax-timing example (also ties into Section 4.13's manipulation-detection logic, but specifically via the TAX LINE rather than the other-income line):** a detailed walk-through showing Reliance's reported net profit swinging dramatically across consecutive quarters NOT because of changes in actual sales or operating profit, but because of deliberate, legal changes in how much advance tax was paid in a given quarter (ranging from a reported ~2% effective tax rate in one quarter up to ~29% in another, despite the standard rate being ~25%). Explicit clarification: **deferring advance tax payment (and paying it later with interest) is completely legal**, but it can be used to make a given quarter's net profit look artificially better or worse than the underlying sales/operating-profit trend would suggest, in order to control market/media narrative around results day. **New, generalizable agent-design implication: when evaluating a quarter's results, the agent should examine the EFFECTIVE TAX RATE for that quarter and compare it to the company's typical/historical effective tax rate. A large, unexplained deviation in tax rate (not just in "other income") is a second specific, checkable signal of potential headline-profit manipulation, separate from and additional to the other-income check in Section 4.13.**

## 4.16 [NEW — Part 2] Depreciation, Fixed Assets, and CWIP (Capital Work in Progress) — Core Mechanics

### Why this matters for the agent
This is foundational accounting context needed to correctly interpret net profit/net loss figures, especially for distressed or turnaround-candidate companies, and to correctly forecast future revenue growth from already-disclosed capital expenditure.

### Core definitions and relationships
```
Fixed Assets  = the value of operational, already-functioning long-term assets (factories, equipment, etc.)
CWIP          = "Capital Work In Progress" — assets currently under construction/installation,
                NOT YET operational, and therefore NOT YET contributing to revenue
Depreciation  = the accounting mechanism that spreads the cost of an already-paid-for fixed asset
                over its expected useful life, as a non-cash expense in each period's P&L
```
- **Critical clarification on depreciation's cash nature: the cash for a depreciated asset was already paid out IN FULL at the time of purchase/installation.** The depreciation expense shown in later periods' P&L statements is a PURE ACCOUNTING ENTRY — it does NOT represent actual cash leaving the company in that period. Worked example: a ₹90,000 asset with a 3-year useful life shows ₹30,000/year (≈₹2,500/month) as a depreciation expense for 3 years, but the full ₹90,000 was already paid to the vendor upfront; none of those later "expense" entries are real cash outflows.
- **Direct, computable implication for analyzing net profit/loss, especially in turnaround or distressed companies:**
```
real_cash_generated_or_consumed ≈ net_profit_or_loss + depreciation_expense
```
  This is explicitly framed as a way to see a company's TRUE cash position, which can be meaningfully better than the headline net profit/loss figure suggests, when depreciation is large relative to the reported loss.
- **Worked example 1 (JP Power):** reported a net loss of ~₹1 crore in a given quarter, but had ~₹121 crore of depreciation expense within that same period's P&L. Since that ₹121cr was never actually paid out in that quarter (it was paid years earlier when the asset was built), the company actually generated roughly ₹120cr of REAL CASH in that quarter despite reporting an accounting net loss. **Agent implication: a reported net loss should NOT automatically be treated as a red flag/disqualifier if depreciation is large relative to the loss — compute the depreciation-adjusted cash figure above before judging distress.**
- **Worked example 2 (Bajaj Hindustan Sugar):** reported a ~₹45cr net loss, but had ~₹53cr of depreciation in the same period — meaning the company was actually cash-generative (~₹8cr positive) despite the reported headline loss, and did NOT need to raise/borrow money to "cover" the reported loss, contrary to what a naive reading of the net-loss headline might suggest.
- **Important caveat/boundary condition on this technique, explicitly stated:** this "add back depreciation" cash-reality-check logic is appropriate specifically for **turnaround-candidate or already-mature/non-expanding companies**. For a company that IS actively expanding/growing capacity, depreciation should NOT be ignored or added back in the same way, because a growing company needs to deploy fresh capital (which will itself generate future depreciation) to keep expanding — i.e., this technique is a tool for evaluating distressed/mature companies' true cash health, not a general-purpose rule to discount depreciation across all companies uniformly.

### CWIP as a forward-looking revenue-growth indicator
- A large CWIP balance (relative to existing Fixed Assets) signals that significant new capacity is under construction and will become revenue-generating once completed and reclassified from CWIP into Fixed Assets.
- Worked example (Alembic Pharma): existing operational fixed assets of ~₹1,798cr alongside a CWIP balance of ~₹2,300cr (i.e., CWIP larger than existing operational capacity) — interpreted as a strong signal that, once this capacity comes online, **both sales and net profit could plausibly more than double (>100% growth)** relative to current levels.
- Worked example (Reliance Industries, longitudinal): fixed assets grew from ~₹1,58,000cr to ~₹8,56,000cr (~9x) over the period studied, alongside roughly 4x growth in both revenue and net profit over the same window — used as a real-world calibration point for how fixed-asset growth (the result of CWIP completing and converting) correlates with, though isn't perfectly proportional to, subsequent revenue/profit growth.
- **Agent implication — a concrete, addable screening/ranking signal:** `cwip_to_fixed_assets_ratio = CWIP / Fixed_Assets`. A high ratio (CWIP comparable to or exceeding existing fixed assets) can be surfaced as a positive forward-looking growth indicator/ranking boost for an already-qualifying stock, distinct from (and complementary to) the backward-looking ROCE/growth-rate metrics already in the framework. No precise numeric threshold was given for "how high is meaningfully high" beyond the Alembic example (CWIP > Fixed Assets) — treat as a qualitative/ranking signal, not a new hard gate, pending further calibration.

## 4.17 [NEW — Part 2] Net Profit vs. EBITDA — Explicit Rejection of EBITDA-Centric Evaluation
- **Explicit rule: net profit (not EBITDA — "earnings before interest, depreciation, tax, and amortization") is the metric that matters for this framework.** EBITDA is specifically called out as a metric favored by companies/promoters (the video specifically references startup-style companies) who want to obscure or flatter real performance, since it deliberately excludes interest, tax, and depreciation — all of which are real, relevant costs of running the business (interest = real cash cost of debt; tax = real cash cost legally owed; depreciation, while non-cash per Section 4.16, still represents real capital that was genuinely spent and must eventually be replenished for a growing business, per the caveat in 4.16).
- **Agent implication: do NOT use EBITDA as a primary or scoring metric anywhere in this framework. Net profit remains the operative profitability metric throughout** — this directly reinforces and is consistent with everything established in Sections 4.1-4.16 (ROCE, ROCE tiering, the V200 net-profit threshold from Video 1, etc., are all net-profit/post-tax-based, never EBITDA-based).
- **Adjacent, related caution given (context, not a separate numeric rule): avoid investing in IPOs in this framework's style of trading.** Reasoning given: by definition, a "good" IPO will be oversubscribed and retail allotment becomes unlikely/minimal, while a "weak" IPO is the one retail investors are more likely to actually receive an allotment in — an adverse-selection problem. Additionally, newly-IPO'd companies frequently lack the established net-profit track record this framework requires (ties back to the Video 1 "15-20 years in business" condition) — so IPO-stage companies are implicitly excluded from this framework's investable universe until they build a multi-year net-profit history, which is consistent with (not an exception to) the existing V40/V40Next/V200 age/track-record requirements.

## 4.18 [NEW — Part 2] Buyback of Shares — Brief Clarification (Not a Scoring Rule)
- Q&A clarification: if Reserve and/or Share Capital is observed to DECREASE over time (somewhat unusual, since both typically only grow), a likely explanation is a **share buyback** — the company repurchasing its own shares from existing shareholders, which reduces the total share count and the corresponding capital/reserve figures.
- **Explicit framing: a buyback is "not bad."** Rationale given: companies often do this when they have surplus cash but no better internal use for it (no expansion opportunity attractive enough to deploy fresh capital into) — reducing share count this way is presented as a reasonable, shareholder-friendly capital-allocation choice in that situation, broadly analogous in spirit to how high dividend payout was discussed in Section 4.5, but framed slightly more neutrally/positively here (buyback = "okay," whereas high dividend yield was framed as a mild caution signal about growth prospects). **Agent implication: do not penalize a company for a buyback-driven reduction in share capital/reserve; this is a benign, explainable data pattern, not an anomaly to flag.** No new numeric screening rule introduced here — purely an explanatory/data-interpretation note.

## 4.19 [NEW — Part 2] Cash Flow Statement — Confirmed as Not a Useful Standalone Screening Input
- Explicit Q&A confirmation: of the three standard cash flow statement sections (operating, investing, financing activities), **none should be used as a standalone screening metric** in this framework. The instructor's stated reasoning: the "real" cash-generation picture is already captured by the simpler `net_profit + depreciation` calculation from Section 4.16, and the formal cash-flow-statement breakdown is "just an accounting entry" that doesn't add meaningfully new decision-relevant information beyond what's already being checked via net profit, depreciation, ROCE, and debt/equity. **Agent implication: do not build out a separate cash-flow-statement-based scoring module; the existing net-profit/depreciation/ROCE/debt-equity stack already covers what matters per this framework.**

## 4.20 [NEW — Part 2] Reconfirmed/Clarified Operational Rules from Q&A (various, smaller but concrete points)

- **CWIP is excluded from the ROCE denominator's effective capital base in practice, per Q&A confirmation:** since CWIP is not-yet-operational capital, a large CWIP balance will tend to suppress a company's reported ROCE in the period before that capacity comes online (capital is "employed" on the books but not yet generating returns). **Agent implication: when comparing ROCE across companies or time periods, be aware that a temporarily-depressed ROCE concurrent with a large CWIP balance may reverse/improve once that capacity converts to revenue-generating fixed assets — this is a nuance/caveat on interpreting the ROCE tiering from Section 4.6, not a change to the tiering thresholds themselves.**
- **Paid-up capital = share capital, no meaningful distinction for this framework's purposes** (historical accounting distinction between "called-up," "paid-up," and "subscribed" capital exists in general accounting theory but is explicitly waved away as irrelevant here — paid-up capital is simply treated as equal to share capital as already defined in Section 4.4).
- **Reconfirmed/extended promoter-pledging guidance (directly ties to and reinforces Section 4.10):** a Q&A scenario explored a promoter pledging shares specifically to BUY MORE shares of the same company (raising promoter stake from ~50% to ~70% without injecting fresh personal capital, partly funded by dividend payouts used to service the pledge-backed loan) — explicitly reconfirmed as carrying real risk (the bank holds the right to sell the pledged shares if the loan isn't serviced), even though the underlying motive (increasing promoter ownership/conviction) sounds superficially positive. **This does not soften the Section 4.10 disqualifying formula in any way — pledging-driven risk is treated as risk regardless of the promoter's stated or apparent motive for taking on that pledge.**
- **Existing-portfolio reconciliation logic re-confirmed and extended (originally established in Video 2, Section 2.6):** for stocks already held that are NOT part of V40/V40Next/V200 (i.e., outside the agent's investable universe entirely), the explicit Q&A guidance is that the agent does not need to apply RHS/CWH or any other chart-pattern strategy logic to them at all — those stocks simply sit outside the framework's scope; existing-position guidance only applies within the V40/V40Next/V200 universe.
- **Switching directly from one strategy's exit into another strategy's entry, same stock, without going to cash first, is explicitly permitted** — Q&A confirms that if a sell signal from one strategy (e.g., Knoxville) coincides with/is immediately followed by a fresh buy signal from a different strategy (e.g., Cup with Handle) on the same stock, there is no requirement to "round-trip" through cash; the position can be conceptually carried over, tracked via the user's own ledger (per the FIFO/ledger caveat from Video 2, Section 2.6) as a new trade under the new strategy's rules.
- **Explicit cross-strategy preference ordering when multiple valid pattern-based candidates compete for limited capital, reconfirmed (extends Section 4.6's ROCE/D-E tie-breaking with an ADDITIONAL, higher-level tie-breaker layer):**
```
1. First, prefer V40 over V40 Next over V200 (in that order), all else equal.
2. Among candidates within the same universe tier, prefer the one with the HIGHER potential
   gain percentage (as calculated per the relevant strategy's own target formula).
3. Among candidates with similar potential gain, apply the ROCE/Debt-Equity tiering tie-breaker
   from Section 4.6.
```
  **This is a genuinely new, explicit, multi-level tie-breaking hierarchy for portfolio construction — should be implemented as the agent's default candidate-ranking logic when more qualifying opportunities exist than available capital/position slots.**
- **Explicit guidance on cup-with-handle / RHS neckline edge cases (Q&A, refines Section 3.1/3.2's geometry rules):** when a potential "handle" or "right shoulder" shows a false breakout (price briefly exceeds the prior resistance/peak before falling back to resume building the base), the analyst should NOT restart the pattern measurement from that false-breakout midpoint — the neckline/connecting-point measurement must still originate from the original peak/resistance level on the left side of the pattern, not from an intermediate false-breakout point. **This is a concrete refinement to the pattern-recognition geometry first described in Section 3.1 — worth encoding as an explicit rule in any pattern-detection algorithm: false breakouts within an otherwise-still-forming base do not reset/relocate the neckline reference point.**
- **Explicit guidance on competing pattern signals (Q&A, new tie-breaker for the pattern-strategy family specifically):** if more than one valid chart pattern (RHS, CWH) appears to be forming/available on the same stock at the same time, prefer whichever has the HIGHER calculated potential gain percentage — consistent with and an instance of the general tie-breaking hierarchy given above.
- **Always-100%-invested philosophy, explicitly reconfirmed:** successful traders, per the instructor, are described as being effectively always fully invested — i.e., available capital is treated as something that should typically already be deployed into open positions, with new opportunities simply queued/waited-on (not chased by force-liquidating existing positions early) until either fresh capital becomes available (income, deposits) or an existing position naturally hits its own target and frees up capital. **Agent implication: the agent should NOT recommend exiting an existing, on-target position early merely because a new, equally or more attractive opportunity has appeared — existing positions are only exited via their own strategy's defined exit rule (per Section 2.6's existing-portfolio reconciliation logic), never pre-empted to fund a different new opportunity.**
- **Position-sizing base for the 3%-per-trade rule, explicitly clarified:** when capital is added to the portfolio incrementally over time (e.g., monthly salary contributions), the 3%-per-trade calculation should be based on the TOTAL CURRENT portfolio value at the time of each new trade (i.e., recalculated/updated as the portfolio grows), not fixed against the original starting capital amount. This is consistent with (and resolves a previously-unstated ambiguity in) the position-sizing rules established across Videos 2-3.

---//---

# VIDEO 5 — Strategy 7: "Three Times in Three Years" (Turnaround Stock Strategy)

**Source:** Class 5 (live session) of Vivek's Online Stock Market Course (English), YouTube
**Content type:** The 7th of the originally-promised 7-8 total strategies. Structurally unlike every other strategy documented so far: it is NOT restricted to V40/V40Next/V200, applies to the entire NSE-listed universe, and is built around a 10-point qualitative+quantitative checklist (a "turnaround story" filter) rather than a chart pattern or plotted indicator. This is explicitly described as the most labor-intensive strategy to apply correctly, since it requires genuine business-model understanding across many different sectors rather than a repeatable mechanical scan.

## 5.0 Scope and Applicability — Critical Departure from All Prior Strategies

- **Universe: ALL stocks listed on NSE (National Stock Exchange) — no V40/V40Next/V200 restriction.** Explicit numeric context given: ~1,600 companies are listed on NSE; ~5,000 are listed on BSE (Bombay Stock Exchange), meaning ~3,500 companies are BSE-only and NOT eligible for this strategy. **Hard, simple, checkable eligibility rule: `IF stock is NOT listed on NSE: this strategy does not apply, regardless of how well it might otherwise meet the 10 conditions below.`**
- **Why this strategy is harder to scale/automate than the others:** V40/V40Next/V200 lists already encode a "good company" qualitative judgment ahead of time (sector leadership, debt levels, business quality), so technical strategies (SMA, Knoxville, V20, RHS, CWH, V10) can run on a pre-vetted list. This strategy instead requires the analyst (or agent) to independently assess business quality, future growth prospects, and the SPECIFIC REASON for a large historical price decline, across potentially any of ~1,600 listed companies and ~50-60+ distinct sub-industries — there is no shortcut pre-filtered list comparable to V40/V40Next/V200 for this strategy. The instructor explicitly recommends a learning regimen of studying one new industry/sector per week to build sufficient business-domain knowledge over roughly a year to cover ~50 sectors. **Flag for agent design: this strategy is the strongest candidate across the entire framework for requiring human-in-the-loop judgment rather than full automation, even more so than RHS/CWH pattern recognition (Video 3) — the "understand the reason for the decline and verify it's no longer relevant" step is fundamentally a business-research task, not a quantitative screen.**

## 5.1 The 10 Conditions (Full Checklist)

### Condition 1 — Minimum historical decline from lifetime high
- **The stock price must have fallen at least 67% from its lifetime high.** Example given: if lifetime high = ₹300, the stock must currently be trading below ₹100 to qualify for consideration under this condition. This is a hard, simple, computable threshold: `(lifetime_high - current_price) / lifetime_high >= 0.67`.

### Condition 2 — Understand and classify the REASON for the decline
- The decline's cause must be understood and classified into exactly one of three sub-categories (this classification itself doesn't gate eligibility — all three sub-categories are valid starting points — but it shapes HOW conditions 3-6 should be verified):
  - **Category A — Business itself was impacted:** Revenue declined → net profit declined (as a consequence) → stock price declined (as a further consequence). A genuine fall in the underlying business, not just sentiment.
  - **Category B — Business intact, but financials (profitability) were impacted:** Revenue/business volume did NOT meaningfully decline, but net profit declined for some other reason (e.g., a cost-structure issue like rising interest expense, not a revenue problem) → stock price declined as a result.
  - **Category C — Business AND financials both intact; only sentiment/price moved:** Neither revenue nor net profit declined in any meaningful way — the stock price fall was driven purely by external sentiment, panic, or unrelated macro fear, disconnected from the company's actual operating performance.
- **Agent implication:** this requires pulling multi-year revenue and net profit trends around the period of the price decline and checking which pattern matches. This is a checkable, semi-automatable sub-task (the data pull and trend comparison can be automated; correctly attributing WHY a profit or sentiment shift happened still requires qualitative business-context research per the Section 5.0 caveat).

### Condition 3 — The reason for the decline must no longer exist today
- Whatever caused the original decline (a regulatory change, a sector-wide cost shock, a temporary liquidity/leverage problem, a sentiment panic, etc.) must be CONFIRMED to have resolved, expired, or otherwise no longer apply at the time of evaluation. This is inherently a qualitative/current-events verification step tied directly to whatever was identified in Condition 2.

### Condition 4 — Proven track record of past good performance
- Prior to the decline, the company must have a demonstrated history of solid business execution (revenue and profit growth over a meaningful prior period) — i.e., this is not a company that was always struggling; it was a previously-good business that hit a specific, identifiable, and (per Condition 3) now-resolved problem.

### Condition 5 — Good future growth prospect
- Same underlying logic as the Video 1 business-quality framework (low penetration / long growth runway) — must be re-confirmed for the specific company under consideration, not assumed just because Conditions 1-4 are met.

### Condition 6 — Improvement visible in the LATEST quarterly results
- The most recent quarterly result (at the time of evaluation) must show clear improvement — explicitly framed as wanting to see the company already on an upward trajectory in the numbers, not just a theoretical thesis that things "should" improve. Worked examples consistently used a single standout quarter (often a new quarterly record net profit) as the trigger that completed this condition.

### Condition 7 — Price must STILL be significantly down at the time all of Conditions 1-6 are met
- **Even after Conditions 1-6 are satisfied, the stock price must still be at least 50% below its lifetime high at that specific moment.** This guards against entering after the market has already substantially re-rated the stock in response to improving fundamentals — the entire thesis of this strategy depends on a persisting gap between improved fundamentals and a still-depressed price. `(lifetime_high - current_price_at_signal_confirmation) / lifetime_high >= 0.50`.

### Condition 8 — Exit rule: 100% gain target within 12 months
- **If the position achieves a 100% gain (price doubles from entry) within 12 months of purchase, exit and book profit immediately at that point.** (Note: the transcript contains one verbal slip referencing "six months" mid-explanation, but the instructor explicitly restates and confirms "12 months" as the correct, intended threshold — treat 12 months as the operative rule, not 6.)

### Condition 9 — If no 100% gain within 12 months, hold until lifetime high
- **If the 100% gain target is NOT reached within 12 months of purchase, the position is held with no further time limit, until the stock price reaches its original lifetime high** (the same lifetime-high reference point used in Conditions 1 and 7). No stop-loss, no re-evaluation deadline beyond this — explicitly framed as a multi-year hold if necessary (real examples in the video describe holding individual positions for 2+ years under this rule, including one position the instructor states he was still holding 18 months in with no exit yet at the time of recording).

### Condition 10 — "Blessings" / mindset condition (explicitly NOT a computable rule)
- The instructor includes this as a literal 10th condition, framed as equally important to the other 9, but it is explicitly **mindset/spiritual content (chanting, patience, emotional discipline) rather than anything computable.** **Agent implication: log this for completeness and cultural/source fidelity, but do not attempt to encode it as model logic.** The closest computable proxy to what this condition is actually getting at operationally is: (a) do not panic-sell during the (potentially very long) holding period while waiting for either the 100%-in-12-months exit or the eventual lifetime-high exit, and (b) do not abandon a position just because price action is flat for an extended period (multiple worked examples show 6+ months of flat price action before the eventual move) — these behavioral-discipline points ARE already captured elsewhere in the framework (Video 2-4's "two things not in your control: volatility and holding period" principle) and don't need separate new logic beyond what's already documented.

## 5.2 Position Sizing and Risk Rules
- **3% of total portfolio per trade** (same base sizing convention as all 6 other strategies).
- **No averaging under this strategy** — explicitly stated as a single-entry strategy, unlike V20/Knoxville/V10 which all permit averaging under specific gap conditions.
- **No stop-loss** (consistent with every other strategy in this framework).

## 5.3 Worked Examples — One Per Decline-Reason Category (all three explicitly walked through to demonstrate each of the 3 sub-categories from Condition 2)

### Example 1 — Category A (business itself impacted): Motilal Oswal Financial Services
- **Business model:** mutual fund house + PMS (portfolio management services) + stockbroking — all three revenue streams are essentially percentage-fee-based on the value of assets under management/brokerage volume, meaning revenue is inherently leveraged to overall market levels in a way that amplifies both up and down moves.
- **Decline cause (Category A):** (1) SEBI ordered mutual fund houses to stop misallocating large-cap-fund inflows into small/mid-cap stocks (a practice that had been inflating small/mid-cap valuations), forcing a wave of small/mid-cap selling across the industry; (2) simultaneously, a new LTCG (long-term capital gains) tax of 10% and STCG (short-term capital gains) tax of 15% were introduced (up from 0% and 10% respectively), prompting many investors to book profits before the new rules took effect, adding further selling pressure. Both factors hit small/mid-cap valuations broadly, which directly hit this company's AUM-linked and brokerage-linked revenue (NOT a company-specific operational failure).
- **Quantified manifestation of the "service business" cost-structure mechanic (a generalizable insight, not specific to this one stock):** for asset-management/brokerage-type businesses, fixed costs (salaries, rent, infrastructure) do NOT scale down when revenue falls, so a revenue decline translates into a DISPROPORTIONATELY larger net profit decline. Worked numeric illustration: ₹1,000cr revenue at 50% net margin = ₹500cr profit, ₹500cr cost. A 30% revenue decline (to ₹700cr) with costs unchanged at ₹500cr results in only ₹200cr profit — a 60% PROFIT decline from a 30% REVENUE decline. **This same mechanic was noted to work in reverse during recovery (smaller revenue growth produces opportunity for larger profit growth) — both phases are illustrated in this example.**
- **Confirmation of resolution (Condition 3):** Both causal factors (the SEBI reallocation mandate and the LTCG/STCG tax-change-driven selling wave) were one-time/transitional events that had fully played out and were no longer ongoing pressures by the time of re-evaluation.
- **Condition 6 trigger:** a quarter was posted with the highest-ever quarterly net profit (~₹299cr, against a previous full-YEAR high of ~₹632cr) — annualizing that single quarter implied a full-year run-rate (~₹1,200cr) roughly double the best full year ever previously posted.
- **Entry point:** stock was ~64% below its lifetime high at the moment all 7 quantitative/business conditions were confirmed (results published, price checked same window) — satisfying Condition 7's "still ≥50% down" requirement.
- **Outcome:** 100%+ gain achieved within 259 days (~8.5 months), well inside the Condition 8 12-month window. Cross-validated against the instructor's own contemporaneous public content (a YouTube video discussing this exact thesis at a similar price level, predating the subsequent price move) as evidence this wasn't a retroactively-cherry-picked example.
- **Side-note flagged in Q&A (worth preserving as a sector-specific caution, not a new universal rule):** brokerage/financial-services firms offering margin trading can carry meaningful counterparty/bad-debt risk during sharp market drawdowns (clients failing to meet margin calls, leaving the broker liable to the exchange) — this was offered as part of explaining one unusually large expense spike, not as a new screening condition.

### Example 2 — Category B (business intact, financials/profitability impacted): JP Power (Jaiprakash Power Ventures)
- **Decline magnitude:** ~99.58% fall from lifetime high — used explicitly to make the point that this strategy can apply even to extreme, near-total declines, and that "everyone who held through the fall lost essentially everything regardless of their entry price" (i.e., the strategy is about identifying the FORWARD opportunity at the bottom, not validating or rationalizing what happened to prior holders).
- **Business model:** power generation (power plants).
- **Decline cause (Category B):** revenue was NOT declining — it was growing — but net profit collapsed into large, sustained net losses. Root cause: operating profit remained positive every year (the core power-generation business itself was fine), but a separate, much larger interest expense (debt-servicing cost) on borrowed capital exceeded operating profit, producing a net loss. The underlying driver: heavy borrowing (peak borrowings ~₹32,000cr against own equity of only ~₹6,000cr, i.e., roughly 5x leverage) to fund new power plant construction, where completion was repeatedly delayed (attributed to the multi-year, multi-agency environmental/land-acquisition clearance process typical for power infrastructure in India), meaning large sums sat in CWIP (non-revenue-generating, per the Video 4 Part 2 CWIP mechanics) while still accruing interest cost on the associated debt.
- **Confirmation of resolution (Condition 3):** by the time of re-evaluation, debt had been substantially paid down (equity ~₹6,500cr vs. borrowings ~₹5,200cr — leverage roughly back near parity rather than ~5x), interest expense had fallen sharply (from ~₹2,700cr/year to ~₹652cr/year in the figures cited), and the company had returned to net profitability for two consecutive quarters, with a real, publicly-reported voluntary DEBT PREPAYMENT (~₹300cr) cited as concrete evidence of improved financial health and management intent/capability — explicitly used as a stronger confirmation signal than financial ratios alone.
- **Depreciation-adjusted cash check applied (directly reusing the Video 4 Part 2 formula):** two consecutive profitable quarters (~₹27cr and ~₹48cr net profit) also carried ~₹133cr/quarter of depreciation each — meaning real cash generation was meaningfully higher (~₹300cr combined across net profit + depreciation) than the headline net profit figures alone suggested, reinforcing the turnaround thesis with the same cash-reality lens from Section 4.16.
- **Entry point:** price was effectively at its lows (~₹2.55-2.75) at the time of the confirming evidence (two profitable quarters + the debt prepayment news).
- **Outcome:** 100%+ gain achieved within ~7 months (well inside Condition 8's window) — BUT the instructor explicitly chose NOT to exit at the 100% mark in his own personal position, citing extremely high conviction in further upside (the stock subsequently moved much further, to ~₹11, and the instructor states he continued holding at the time of recording with an explicit long-term target of ~₹100, i.e., a further ~10x from the ~₹11 level, framed as a 30-40x total return from the original ~₹2.55-2.75 entry over a much longer horizon than the strategy's own 12-month/lifetime-high framework strictly requires). **Important nuance for agent design: Condition 8/9's 100%-or-lifetime-high exit rule is the DEFAULT/baseline rule of this strategy, but the instructor's own real behavior shows he will deviate from his own stated exit rule when conviction is exceptionally high — this should be logged as a documented, real exception to the rule, not silently treated as if the rule is always mechanically followed without exception. The agent should default to the stated rule (exit at 100% gain within 12 months) unless the user explicitly opts into a "hold for higher conviction multi-bagger" override on a specific position.**

### Example 3 — Category C (business AND financials both intact; only price/sentiment moved): Equitas Holdings (Small Finance Bank)
- **Decline magnitude:** ~84% from lifetime high overall; ~72% within a single month (March 2020, pandemic onset) — used to illustrate Category C specifically, since neither revenue nor net profit declined at all during this period; the entire move was sentiment-driven panic.
- **Business model context (small finance banks, a distinct regulatory category):** RBI created a "Small Finance Bank" license category in 2018 specifically for select former microfinance NBFCs, allowing them to serve customers with very small loan sizes (e.g., ₹1,500-5,000) who are not served by conventional banks, at correspondingly higher permitted interest rates (up to ~3.75%/month, justified by fixed per-loan administrative/agreement costs that don't scale down with loan size) — this is a real, structurally distinct, high-margin lending niche serving rural-to-urban migrant workers (informal-sector laborers, delivery workers, domestic help, etc.).
- **Decline cause (Category C):** pandemic-driven mass reverse-migration of this exact customer base from urban back to rural areas, combined with widespread (mistaken, per the instructor) market fear that (a) the pandemic would be indefinite/unending (unlike 1918, modern medicine and vaccine development timelines were faster, and modern telecommunications allowed for actual public-health awareness/compliance) and (b) that migrated borrowers would become untraceable and simply default (mistaken because Aadhaar-linked biometric banking, unlike the pre-Aadhaar era, makes borrowers traceable nationally regardless of physical relocation, and the instructor notes recovering small individual loans is empirically easier than corporate debt recovery). Neither revenue nor net profit actually declined during this period — financials remained intact throughout (which is precisely what defines this as Category C rather than A or B).
- **Confirmation of resolution (Condition 3):** within roughly six months, migrant workers were returning to urban employment and the bank's quarterly numbers reflected this.
- **Condition 6 trigger:** a quarter was posted with both the highest-ever quarterly revenue AND highest-ever quarterly net profit (~₹100cr quarterly net profit, against a previous full-YEAR high of only ~₹200cr) — same "single quarter implies the full year could roughly double the prior best full year" pattern as seen in the Motilal Oswal example.
- **Entry point:** price was ~75% below lifetime high at the time these results were confirmed — comfortably satisfying Condition 7.
- **Outcome:** 100%+ gain achieved within 110 days (~3.5 months) — the fastest of the three worked examples. Cross-validated via the instructor's own contemporaneous YouTube video published on the exact same date as the confirming quarterly results.

## 5.4 Generalizable Mechanic Worth Encoding Separately: Operating-Leverage Effect for Fee/Service-Based Businesses
- Distilled from the Motilal Oswal example (Section 5.3) but stated as a general principle applicable beyond that one stock: **for businesses with high fixed costs relative to revenue (asset managers, brokers, and likely other fee-based service businesses), a given percentage change in revenue tends to produce a LARGER percentage change in net profit, in BOTH directions** (a revenue decline produces a disproportionately larger profit decline; conversely, a revenue recovery/increase produces a disproportionately larger profit increase). **Agent implication: when evaluating a Category A or recovering Category B candidate that is a fee/service-based business specifically, expect and treat a strong quarterly profit rebound as a normal/expected mechanical consequence of even a modest revenue recovery, rather than requiring revenue itself to have already fully round-tripped back to its own prior peak before trusting the profit recovery signal.** This is a useful interpretive lens but was not given a precise universal numeric formula beyond the single illustrative example — treat as qualitative/contextual guidance for evaluating this specific class of business (fee/AUM/brokerage-linked revenue models), not a hardcoded multiplier.

## 5.5 Open Questions / Build Flags from Video 5

1. **This strategy has no equivalent of a pre-vetted ticker list (unlike V40/V40Next/V200).** Conditions 4-6 in particular ("proven track record," "good future growth prospect," "improvement in latest quarterly results") require the same kind of business-quality judgment that underlies the V40/V40Next/V200 construction process in Video 1, but applied ad hoc to any of ~1,600 NSE-listed stocks rather than a pre-filtered universe. Recommend treating this strategy's candidate-discovery step as the highest-priority case for human-in-the-loop review across the entire framework — even more so than RHS/CWH pattern geometry (Video 3), since the failure mode here isn't "did I draw the neckline correctly" but "did I correctly understand and verify the resolution of a business problem," which is a fundamentally open-ended research task.
2. Condition 2's three-way categorization (A/B/C) does not, on its own, change the pass/fail outcome — all three are equally valid entry points, per the explicit instructor framing ("three different studies... we will try to implement all these 10 conditions" across all three). It functions as a diagnostic/explanatory framework rather than a screening filter. Confirm this understanding holds if a future video revisits this strategy with additional nuance.
3. The Condition 8/9 exit-rule override behavior shown in the JP Power example (Section 5.3, Example 2) — where the instructor's actual personal conduct deviated from his own stated 100%-or-lifetime-high rule due to high conviction — introduces a real ambiguity about how rigidly this exit rule should be enforced by an automated agent versus surfaced as a recommendation with an explicit manual-override option. Recommend defaulting to the literal stated rule (exit at 100%/12mo or hold to lifetime high) and exposing a separate, clearly-labeled "override: continue holding for extended target" feature rather than silently deviating, since the instructor's own deviation was a deliberate, conscious choice he flagged explicitly, not an inconsistency to be papered over.
4. No new fundamental-ratio thresholds were introduced in this video (no new ROCE/debt-equity/etc. numbers specific to this strategy) — Conditions 4 and 5 ("proven track record," "future growth prospect") appear to reuse the same qualitative judgment framework from Video 1/Video 4 rather than introducing strategy-specific numeric thresholds. Treat the existing fundamental-analysis toolkit (Sections 4.1-4.20) as the implementation toolkit for evaluating these two conditions, rather than expecting new thresholds to be defined elsewhere.
5. Per the instructor, **one final ("last") session remains** in the course, explicitly described as covering: (a) how to combine/prioritize the now-complete set of 7 strategies and 3 stock universes into an actual personal trading plan (which strategy/universe combination to use depending on available time and risk appetite), and (b) a CAGR-calculation spreadsheet/Google Sheet walkthrough referenced multiple times across earlier videos but not yet actually delivered. **Correction confirmed in Video 6: contrary to this earlier expectation, the final session DID introduce one more (8th) strategy** — "Lifetime High Strategy" — in addition to the portfolio-construction guidance. See Video 6 below for full detail; this note is left in place rather than silently deleted, per the project convention of tracking how earlier assumptions were revised by later source material.

---//---

# VIDEO 6 — Final Session: Strategy 8 ("Lifetime High Strategy") + Portfolio-Construction Framework (The Four Categories)

**Source:** Class 6 (final live session, extensive Q&A) of Vivek's Online Stock Market Course (English), YouTube
**Content type:** Two distinct deliverables in this video: **(A)** an 8th and final technical strategy ("Lifetime High Strategy," abbreviated LTH), simple in mechanics and restricted to V40/V40 Next; and **(B)** the long-promised portfolio-construction layer — four named, mutually-exclusive "categories" that define which strategy/strategies and which stock universe(s) a user commits to for their entire trading approach. This second deliverable is arguably the most important piece for the agent's overall design, since it resolves how the 8 individual strategies should actually be combined (or deliberately NOT combined) in practice.

## 6.0 Course-Level Correction
This video explicitly supersedes the Video 5 closing-note expectation that no new strategy would be introduced in the final session. An 8th strategy (LTH) was in fact introduced here. The total strategy count for this course is therefore **8, not 7** — this document's earlier "7-8 strategies" framing is now resolved at exactly 8.

## 6.1 Strategy 8 — "Lifetime High Strategy" (LTH)

**Applicable universe:** **V40 and V40 Next only** (NOT V200, NOT the unrestricted NSE-wide universe used by Strategy 7).

**Chart timeframe:** Daily (consistent with the rest of the framework; not separately re-stated but no contrary instruction given).

**No indicator required** — pure fundamental-trigger + price-level rule, conceptually similar in spirit to Strategy 7 but simpler and restricted to the already-curated V40/V40Next universe.

### Entry condition (two-part test)
```
1. The company must currently be posting its HIGHEST-EVER trailing-twelve-month (TTM) revenue
   AND HIGHEST-EVER TTM net profit simultaneously (NOT just a good quarter in isolation —
   explicitly TTM, to smooth out temporary single-quarter margin pressure/noise).
2. AND, at the same time, the stock price must be at least 30% below its lifetime high.
```
- **Explicit rationale tying these two facts together:** when a fundamentally excellent, already-vetted (V40/V40Next) company is simultaneously (a) performing better than it ever has on a trailing-12-month basis, and (b) priced 30%+ below its own historical peak, this is read as a structural mispricing driven by short-term sentiment/macro noise (global recession fears, rate-hike cycles, etc.) rather than anything wrong with the specific business — directly consistent with the "operators push great companies down on bad news/sentiment, not on business deterioration" theme established repeatedly since Video 3.
- Worked example: ICICI Lombard General Insurance (a V40 constituent) — trading ~30-32% below lifetime high while simultaneously posting all-time-high TTM revenue and all-time-high TTM net profit. Potential gain calculated at ~43-48% if price returns to lifetime high.
- Additional worked examples (context/validation only): TCS and HCL Technologies both cited as having been ~27%+ below their respective lifetime highs at a point in the recent past while simultaneously posting all-time-high TTM revenue/profit — used to illustrate that this setup recurs periodically even in mega-cap, extremely stable companies, driven by macro sentiment cycles (US recession fears, inflation data releases) rather than company-specific deterioration.

### Exit condition
```
Target = the stock's own lifetime high (same reference point used for the entry trigger).
```
- No separate "100% in 12 months, else hold" two-stage rule like Strategy 7 — LTH has a single target (lifetime high), held until reached, with **no stated time limit** (worked examples cite realistic ranges from ~8 months up to ~1.5 years, with the instructor's own stated average expectation being roughly one year, though individual cases vary).

### Position sizing and averaging — notably MORE generous than any other strategy in the framework
```
Initial entry: 3% of portfolio (same base unit as all other strategies)
Averaging IS explicitly allowed: every additional 10% further decline from lifetime high
  (i.e., at 40% down, then 50% down, then so on) permits an additional 3% entry,
  PROVIDED that at the time of each additional entry, the TTM revenue and TTM net profit
  are STILL at their highest-ever levels (re-checked at time of averaging, not just at
  initial entry — if TTM figures are no longer at all-time highs at the time of a
  potential averaging opportunity, do NOT average at that point).
Maximum comfortable total allocation to a single stock under this strategy, explicitly
  stated by the instructor: up to 10% of total portfolio (e.g., 3% initial + 3% at -40%
  + 3% at -50%, or similar combinations approaching but not exceeding ~10%).
```
- **This 10% ceiling is explicitly higher than the 9% ceiling used elsewhere in the framework** (V20's max 9%, the RHS/CWH+V10 combined max 9%) — the instructor explicitly justifies this higher comfort level specifically for this strategy, reasoning that the combination of (a) restriction to only the most vetted V40/V40Next universe and (b) the requirement that TTM fundamentals remain at all-time highs even while averaging provides unusually high safety, justifying a larger single-stock concentration than the framework's normal ~9% ceiling.
- No stop-loss (consistent with all 8 strategies in this framework).

### Sector-concentration clarification (explicit Q&A ruling, generalizable beyond just LTH)
- Direct Q&A scenario: if an entire sector (e.g., all major IT services companies) simultaneously qualifies for LTH at the same time (a plausible scenario, since sector-wide sentiment swings are a primary driver of this setup), is it acceptable to end up with 30-40% of total portfolio concentrated in that one sector? **Explicit answer: yes, this is acceptable**, with the reasoning that an entire foundational sector (IT services or banking were the two examples given) cannot realistically collapse without taking down essentially the entire economy and stock market with it (e.g., banks rely on IT services companies for core banking software; if IT collapses, banking collapses too, and vice versa) — sector-wide concentration risk in one of these two foundational sectors specifically is treated as acceptable, unlike concentration risk in a single company or a narrower/more cyclical sector. **Agent implication: do NOT impose an automatic portfolio-level sector-diversification cap that would block multiple simultaneous LTH (or other strategy) entries within IT services or banking specifically** — this is an explicit, reasoned exception to generic diversification heuristics, not an oversight to correct. No equivalent explicit exception was given for other sectors; treat IT services and banking as the two specifically-blessed exceptions, not a blanket rule extended to all sectors by default.

## 6.2 The Four Portfolio-Construction Categories (the core deliverable of this video)

**Critical framing, stated repeatedly and forcefully throughout this video:** a user should select **exactly ONE** of these four categories as their personal trading approach and **commit to it for at least one full year** before evaluating results or switching. Categories are NOT meant to be mixed freely on a whim — mixing strategies/universes without first picking a category is explicitly framed as a discipline failure, not a feature. The instructor's own closing argument is that inconsistent, undisciplined mixing — not lack of knowledge of strategies — is the primary reason students fail to make money despite having learned everything needed.

### Category 1 — "Lifetime High Strategy Only"
```
Universe: V40 + V40 Next (LTH's native universe)
Strategies used: ONLY Strategy 8 (LTH). No other strategy (not V20, not Knoxville, not RHS/CWH,
  not V10, not SMA, not Strategy 7) is used AT ALL while operating under this category.
Idle-capital rule: if no LTH-qualifying opportunity exists at a given time, hold the
  un-deployed capital in CASH. Do not substitute a different strategy to stay "fully invested."
Position sizing: up to 10% per stock (per Section 6.1's averaging rules), so a portfolio
  does not need anywhere near 33 stocks to be reasonably allocated under this category alone.
```
- **Explicit selling point:** simplicity and low monitoring burden — since LTH only triggers on macro-sentiment-driven dips in already-elite companies, opportunities are relatively infrequent but high-confidence, suiting someone who cannot monitor charts frequently.

### Category 2 — "All 8 Strategies, V40 Universe Only"
```
Universe: V40 ONLY (V40 Next and V200 are explicitly EXCLUDED under this category).
Strategies used: ALL 8 strategies (SMA, Knoxville, V20, RHS, CWH, V10, Strategy 7 "Three
  Times in Three Years" -- NOTE: even though Strategy 7 is normally NSE-wide, under this
  category its application is implicitly narrowed to V40-listed names only, since the
  category's defining constraint is "V40 universe only" -- and Strategy 8 "LTH"), run
  concurrently, on V40 stocks specifically.
Multi-signal-on-one-stock handling (NEW, explicit rule): if a single V40 stock triggers
  signals from MULTIPLE different strategies at different points in time (e.g., a Knoxville
  signal, then later a separate SMA signal, then later an LTH signal), each can be taken as
  a SEPARATE trade, PROVIDED each subsequent trade's entry price is at least 10% lower than
  the immediately preceding trade taken on that same stock (reusing the same 10%-gap
  convention used elsewhere in the framework, e.g., Strategy 7's averaging rule and LTH's
  own averaging rule).
Combined position sizing across multiple strategies on the same stock: up to ~9-10% total
  (using the thumb-rule ceiling consistent with the rest of the framework), built up via
  the 10%-price-gap-gated sequential entries described above.
```
- **Explicit, strong claim made about this category specifically:** if a user commits ONLY to this category (all 8 strategies, V40-only) for the long term, the instructor states this alone is sufficient to become a USD billionaire over time, NOT just an INR billionaire — explicitly emphasized as a distinct, stronger claim than for the other categories, attributed specifically to the combination of (a) restricting entirely to the very safest universe (V40 = large/mega-cap, debt-free, market-leading companies, "the last companies that would ever go bankrupt") and (b) maximizing trading frequency/opportunity capture by using all 8 strategies simultaneously within that safe universe, rather than to any single strategy being superior.
- **Supporting historical/statistical context given (not a new rule, just framing/confidence-building color):** referenced ~100 years of US stock market history showing 140+ instances of 10%+ corrections and 14-15 severe bear markets/recessions, with the market still reaching new all-time highs after every one of them (eventually) — used to argue that staying concentrated in only the most fundamentally elite companies (rather than diversifying into lower-quality names for the sake of diversification) is the safer long-run choice, since elite/debt-free market leaders are the ones most likely to be among the survivors and eventual new-high-makers after any given downturn, whereas weaker/indebted companies are the ones actually at risk of permanent impairment.

### Category 3 — "Four Named Strategies, V40 + V40 Next"
```
Universe: V40 + V40 Next (NOT V200, NOT NSE-wide Strategy 7).
Strategies used: SMA (Strategy 1), RHS (Strategy 4), CWH (Strategy 5), and V10 (Strategy 6)
  ONLY. Explicitly EXCLUDES Knoxville (Strategy 2), V20 (Strategy 3), Strategy 7 ("Three
  Times in Three Years"), and Strategy 8 (LTH) from this category's toolkit.
```
- No additional distinguishing position-sizing or averaging rules were given beyond each individual strategy's own already-documented rules (Sections 2.2, 3.1, 3.2, 3.3) — Category 3 is purely a SUBSET SELECTION of which 4 of the 8 strategies to run, applied across the V40+V40Next universe.
- No explicit "why these specific 4" justification was given beyond general framing that different users will naturally gravitate toward different subsets based on personal comfort/preference with specific strategy mechanics (chart-pattern-based vs. indicator-based) — this is presented as one illustrative, named combination a user might choose, not as inherently superior to other possible subsets.

### Category 4 — "V20 Only"
```
Universe: V40 + V40 Next + V200 (V20's native, full universe — the broadest of any
  single-strategy category).
Strategies used: ONLY Strategy 3 (V20). No other strategy is used.
Idle-capital rule: same as Category 1 — if no V20-qualifying opportunity exists, hold cash;
  do not substitute another strategy to stay invested.
```
- **Explicit selling point, specific to this category:** V20 is praised as particularly well-suited to people with limited monitoring time/full-time corporate jobs, because both the entry price (lower range line) and exit price (upper range line) are known and fixed in advance the moment a qualifying range is identified — allowing the ENTIRE trade (both buy and sell) to be automated via GTT (Good-Till-Triggered) orders placed at broker level, requiring no active intraday or even daily monitoring once the range/order is set. This is presented as the single most "set and forget" -compatible category of the four, precisely because it's the only category among the four built on a single strategy whose both entry AND exit are pre-determinable price levels rather than requiring an ongoing daily close-based signal check (contrast with SMA/Knoxville/LTH/Strategy 7, which all require periodic re-evaluation of a developing signal).

## 6.3 Cross-Category Rules and Guardrails

- **Pick exactly one category; do not mix across categories.** Explicitly and repeatedly stated as the single most important takeaway of the entire course. The instructor's closing remarks frame nearly all remaining individual-stock Q&A questions in this video as a symptom of users not yet having internalized this rule (i.e., the same underlying answer — "apply your category's rules, exit at target or hold per the existing-portfolio reconciliation logic" — answers nearly every specific-stock question asked).
- **Minimum commitment period: at least 1 year** on a chosen category before evaluating its results or switching to a different category — switching prematurely (e.g., after a few disappointing months) defeats the purpose of measuring a strategy's real average performance, which the instructor has repeatedly emphasized varies significantly year to year even when the long-run average is strong.
- **Track performance of OTHER categories passively while committed to your chosen one** (recommended, not mandatory): the instructor recommends logging/observing what trades would have been triggered under the other 3 categories even while only actually trading one, so that after the 1-year commitment period, a user has real comparative data to decide whether to continue or switch. **Agent implication: this is a natural feature for the eventual tool — track and surface hypothetical/shadow performance for non-selected categories alongside the user's actively-traded category, without executing trades in the shadow categories.**
- **Existing-portfolio reconciliation logic (already established in Video 2 §2.6, reaffirmed extensively via repeated Q&A in this video) is explicitly declared to be the ONLY answer needed for the large majority of individual-stock questions:**
```
IF a strategy signal (from the user's chosen category's strategy set) is currently
   active/applicable on a held stock:
  -> hold/exit at that strategy's own defined target. Do nothing else.
IF NO strategy from the chosen category is applicable to a held stock:
  IF the stock is currently profitable:
    -> exit immediately, redeploy capital into the chosen category's next qualifying opportunity
       (or hold as cash if none currently exists, per that category's idle-capital rule).
  IF the stock is currently at a loss:
    -> hold and wait for price recovery, PROVIDED the company still passes the
       fundamental V40/V40Next/V200 quality gate (Sections 1.2, 1.3, and the Video 4
       ratio/pledging refinements). Do not sell at a loss merely out of impatience or
       because other unrelated stocks are performing better in the interim.
```
- **A pattern (RHS/CWH) is NOT yet "applicable" until it is fully formed and confirmed (explicit, repeated Q&A clarification):** if a chart shows a partially-formed shoulder/handle whose base/breakout has not yet completed, no strategy signal exists yet — there is nothing to act on, and the position (if held) falls under the "no strategy applicable" branch above, not under "a strategy is forming so let's get ready." This explicitly rules out anticipatory/early entry based on a pattern that LOOKS like it's about to complete.
- **A live RHS/CWH/V20 etc. pattern measurement is locked to its original reference points and does NOT get re-measured retroactively from a later/different point** (reaffirms and slightly extends the Video 4 Part 2 false-breakout rule from Section 4.20) — once a valid pattern/range exists and signals have been taken against it, later price action doesn't redraw or invalidate the original geometry; a fresh, separate pattern is required for any new trade, never a retroactive adjustment of an existing one.
- **A completed strategy cycle (signal triggered, position taken, exit signal already triggered) is CLOSED — do not wait for "another" exit signal of the same type to re-confirm exiting a position that's already been exited per the rules.** (Direct Q&A example: a Knoxville exit signal had already fired and the user was unsure whether to keep holding for a second/later exit signal — explicit answer: no, the position should already be considered closed at the first valid exit signal; there is no "waiting for the next one" once a valid exit has occurred.)

## 6.4 Additional Confirmed Rules and Clarifications from Q&A (smaller but concrete, several directly resolve prior open questions)

- **Multiple portfolios (e.g., a user's own + a spouse's) are treated as fully separate portfolios for position-sizing purposes** — the same trade/signal CAN be taken in both portfolios independently (each gets its own 3%-of-that-portfolio sizing), but the two portfolios' total values are never combined for sizing calculations. **This directly resolves an ambiguity that was open since earlier videos.**
- **The "33 stocks" diversification guideline mentioned in earlier videos is PER PORTFOLIO, not a hard cap shared across multiple portfolios** — if a user manages 2 separate portfolios, each can independently hold up to ~33 positions; they are not forced to split 33 total across both.
- **"Idle/un-deployed cash awaiting an opportunity" should be counted as part of total invested capital for CAGR/return calculations** — explicit clarification that cash sitting on the sidelines waiting for the next qualifying signal is NOT excluded from the denominator when calculating overall portfolio returns; it is treated as "deployed" capital for measurement purposes even though it isn't literally in a position at that moment. **Agent implication: when computing a user's overall CAGR/performance metric, total portfolio value (including idle cash awaiting deployment) is the correct denominator, not just the currently-invested subset.**
- **Loss-making/insolvency-risk brokers should be avoided for custody of demat/trading accounts** — explicit, named guidance: prefer the largest, profitable brokers (Zerodha named as the top preference, followed by Upstox and Angel One, with a caution against brokers that are themselves loss-making companies, e.g., Paytm Money was specifically named as an example to move away from) — same "avoid companies that could go bankrupt" logic applied reflexively to one's own broker selection, not just to stocks being traded. This is operational/account-safety guidance, not a trading rule, but worth surfacing in the agent's onboarding/setup guidance if the tool ever touches broker selection or account-linking flows.
- **BSE Ltd. (the exchange operator, not to be confused with stocks merely listed on BSE) was specifically and repeatedly flagged as a stock the instructor has deliberately never recommended**, citing a structural, durable disadvantage: virtually all serious volume — and ALL futures & options (F&O) trading — has migrated to NSE due to superior liquidity, creating a self-reinforcing cycle (more liquidity attracts more traders, which attracts more liquidity) that structurally disadvantages BSE Ltd.'s own business prospects in a way that is NOT a temporary/sentiment-driven dip (i.e., this does NOT qualify as a Strategy 7 or LTH candidate, since the cause of any price weakness here is a structural/durable competitive disadvantage, not a resolved or resolvable temporary event). **Agent implication: this is a useful negative case study — a company can be down significantly from its highs for reasons that do NOT meet Strategy 7's Condition 3 ("the reason must no longer exist") or LTH's implicit "temporary mispricing" thesis. The agent should be able to distinguish "structurally impaired, avoid" from "temporarily mispriced, opportunity" — BSE Ltd. is the explicit, named example of the former.**
- **Stay away from companies currently undergoing a merger, specifically where a smaller/subsidiary company is being merged into a larger parent at a valuation the instructor characterizes as unfair to minority shareholders of the smaller entity** — explicit named examples: Tata Chemicals-related and Tata Steel BSL (formerly Bhushan Steel) merger situations, where the smaller entity was, in the instructor's view, absorbed at roughly half of fair/book value. **Agent implication: flag (or exclude) candidate stocks that are currently subject to an announced merger/amalgamation into a parent/group company, particularly where the smaller entity's standalone valuation appears to be getting compressed for the deal** — this is a new, distinct risk category not previously captured by any of the existing fundamental screens (it isn't about debt, pledging, or quality — it's about minority-shareholder treatment in a specific corporate-action context).
- **Avoid small-cap/cyclical auto-ancillary companies as a category-level caution** (explicit, general statement, not company-specific): the instructor states he personally stays away from "all small auto ancillary companies" as a class, without giving a single universal numeric reason — treat as a soft, qualitative sector-level caution rather than a hard rule with a programmable trigger.
- **Reclassification of shareholding categories (FII/DII relabeling) is NOT the same as actual buying/selling activity** — explicit clarification using a real example (a stock where "public" shareholding appeared to drop sharply while FII/DII share rose) — this can simply reflect a later, corrected classification of the SAME underlying shareholders into the correct FII/DII bucket (i.e., a data/reporting correction), not a real transaction. **Agent implication: a sudden, large jump in FII/DII percentage with a correspondingly large drop in "public" percentage in the same period should not, by itself, be read as a strong bullish "smart money is buying" signal without checking whether this might just be a reporting reclassification rather than real net buying.** This is a data-interpretation caution worth encoding as a sanity check before treating shareholding-pattern shifts as a strong instutional-buying signal.
- **The instructor explicitly confirmed he has deliberately chosen NOT to register as a SEBI Research Analyst, Investment Advisor, or PMS operator**, specifically to preserve his own freedom to trade his personal account without regulatory restriction — disclosed transparently in response to a direct question about why he doesn't offer a "smallcase"-style product. This is background/context only, not something with direct agent-design implications, but worth retaining for completeness/source fidelity.
- **A direct, repeated point of frustration/emphasis from the instructor in the closing Q&A: nearly all individual-stock-specific questions reduce to the SAME generic existing-portfolio-reconciliation answer** (Section 6.3's pseudocode block) — the instructor explicitly states that continuing to ask stock-by-stock questions after this point indicates the underlying rule-based framework has not yet been internalized. **Strong design signal for the agent: the tool should proactively SURFACE the reconciliation logic's output for a user's actual held positions (which strategy, if any, currently applies; profit/loss status; recommended action) rather than requiring the user to ask one-off questions per stock — this was, in effect, the instructor's own stated ideal end-state for how a student should operate, and maps directly onto a natural core feature of the planned tool.**

## 6.5 The "Three H" Daily Discipline Routine (mindset/lifestyle content — logged for completeness, not agent logic)
- Repeated, explicit daily routine recommendation, framed as foundational to executing all of the above with consistency: **40 minutes reading + 40 minutes physical exercise + 40 minutes chanting/prayer, every day, without exception.** Explicitly NOT proposed as optional "self-improvement" content but as a literal precondition the instructor believes is necessary for maintaining the discipline required to follow a single chosen category consistently for a full year without emotional deviation. **Agent implication: none directly codable, but worth retaining as authentic source context; could optionally surface as a non-intrusive "discipline reminder" feature if the product ever leans into a habit-tracking angle, though this is speculative product scope, not something implied as required by the source material.**

## 6.6 Open Questions / Build Flags from Video 6

1. **Category 2's claim ("all 8 strategies + V40-only can make you a USD billionaire") is a strong, qualitative claim without a backing simulation/backtest shown in the source material.** Treat as the instructor's stated belief/anecdotal confidence, not a verified, quantified projection — do not surface this specific claim to end users as if it were a guaranteed or back-tested outcome.
2. **Category 3's specific 4-strategy subset (SMA, RHS, CWH, V10) was presented as one illustrative combination, not as a uniquely "correct" or superior subset** — the agent's UI should likely allow a user to construct their OWN custom subset-and-universe combination (a "Category 5+") rather than assuming only these exact 4 named categories are valid configurations, since the underlying individual-strategy rules are fully modular and the four categories are themselves just example presets.
3. **No explicit rule was given for what happens if a user wants to change their committed category before the 1-year minimum has elapsed** (e.g., is there a clean way to transition, or should all open positions under the old category simply be allowed to run to their own natural exits while only NEW capital follows the new category?) — recommend the latter (let existing positions complete under their original category's rules; apply the new category only to new trades) as the most internally-consistent approach, but flag this as an inferred design choice, not an explicitly stated rule.
4. **The merger/minority-shareholder-risk caution (Section 6.4) and the BSE Ltd. structural-impairment caution (Section 6.4) are both new negative-screening categories that don't fit cleanly into any previously-defined quantitative gate** (V40/V40Next/V200 qualification, the pledging disqualifier, ROCE/D-E tiers, etc.). Both are qualitative, situational judgments. Recommend implementing these as a separate "situational risk flags" checklist requiring periodic manual/news-based review for currently-held or candidate positions, rather than trying to force them into the existing quantitative screening pipeline.
5. **This appears to be the final video in the course** (explicitly called "the last session," with the instructor's closing remarks framed as a course wrap-up and an invitation to continue via his free YouTube channel going forward, plus a reference to a separate, paid "offline"/advanced course with its own distinct eligibility criteria that is explicitly OUT OF SCOPE for this knowledge base unless the user later decides to provide that material too). Treat the documentation effort as feature-complete for the core course as of this update, pending the user providing the previously-referenced-but-not-yet-delivered CAGR-calculation spreadsheet walkthrough (mentioned again in this video as something "Aditya" — an assistant — would cover separately, outside the main video series) or any further material.

---//---

# REFERENCE DATA: V40 and V40 Next Constituent Lists
**Source:** Provided directly by user (compiled list, not extracted from a video transcript). Treat as authoritative stock universe data — current as of whenever user compiled it. Snapshot, not permanently fixed; sector leadership/debt/pricing-power status can change over time.

## V40 (Large Cap + Mid Cap market leaders) — 39 entries

| Sector | NSE Symbol |
|---|---|
| Conglomerate | RELIANCE |
| Conglomerate | LT |
| Banks | SBIN |
| Banks | HDFCBANK |
| Banks | ICICIBANK |
| Banks | AXISBANK |
| Banks | KOTAKBANK |
| IT | HCLTECH |
| IT | INFY |
| IT | TCS |
| Non-Banking (NBFC/Financial) | HDFCAMC |
| Non-Banking (NBFC/Financial) | NAM-INDIA |
| Non-Banking (NBFC/Financial) | HDFCLIFE |
| Non-Banking (NBFC/Financial) | ICICIPRULI |
| Non-Banking (NBFC/Financial) | ICICIGI |
| Non-Banking (NBFC/Financial) | BAJAJFINSV |
| Non-Banking (NBFC/Financial) | BAJAJHLDNG |
| Non-Banking (NBFC/Financial) | BAJFINANCE |
| Auto | BAJAJ-AUTO |
| Auto | MARUTI |
| FMCG | HINDUNILVR |
| FMCG | NESTLEIND |
| FMCG | PGHH |
| FMCG | PIDILITIND |
| FMCG | COLPAL |
| FMCG | DABUR |
| Consumer Products | TITAN |
| Consumer Products | PAGEIND |
| Consumer Products | BATAINDIA |
| Consumer Products | HAVELLS |
| Consumer Products | VOLTAS |
| Consumer Products | GILLETTE |
| Consumer Products | MARICO |
| Consumer Products | ITC |
| Pharma | GLAXO |
| Pharma | ABBOTIND |
| Pharma | PFIZER |
| Pharma | SANOFI |
| Paint | ASIANPAINT |
| Paint | BERGERPAINT |

## V40 Next (Mid Cap + Small Cap market leaders) — 39 entries

| Sector | NSE Symbol |
|---|---|
| Financial Services | CDSL |
| Financial Services | BSE |
| Financial Services | JOFIN *(possible typo — likely JIOFIN / Jio Financial Services; unconfirmed, kept as user-supplied)* |
| Financial Services | ANGELONE |
| Financial Services | CAMS |
| Financial Services | BAJAJHFL |
| Financial Services | MCX |
| Cement | ULTRACEMCO |
| Cement | ACC |
| Consumer Product | AWL |
| Consumer Product | GODREJCP |
| Consumer Product | DIXON |
| Consumer Product | KAJARIACER |
| Consumer Product | HONAUT |
| Consumer Product | BLUESTARCO |
| Consumer Product | DMART |
| Consumer Product | RELAXO |
| Auto | BOSCHLTD |
| Auto | EICHERMOT |
| Auto | MRF |
| Auto | M&M |
| Auto | TATAMOTORS |
| Auto | HYUNDAI |
| Hotel | INDHOTEL |
| Hotel | ITCHOTELS |
| Beverages | UNITDSPR |
| Beverages | RADICO |
| Beverages | UBL |
| Beverages | VBL |
| Manpower | TEAMLEASE |
| Manpower | QUESS |
| Healthcare | APOLLOHOSP |
| Healthcare | MEDANTA |
| Healthcare | FORTIS |
| Infra | ADANIPORTS |
| Infra | JSWINFRA |
| Pharma | ASTRAZEN |
| Pharma | CIPLA |
| Pharma | LALPATHLAB |
| Pharma | ERIS |

## V200
**Status: Not yet compiled as a full static list.** Three qualifying conditions documented in Section 1.3 above. User will run the live screener.in query and provide the resulting ticker list; to be added here once available, in the same table format as V40/V40 Next. Note: V200 is now an active dependency for the **V20 Strategy** (Section 2.4), which is the only one of the three Video 2 strategies usable on V200 stocks — compiling this list is now a higher priority for the build phase than before.

---//---

# CONSOLIDATED AGENT-READY RULES (Living Section — Updated With Every New Video)

This section translates everything documented so far into a format closer to what the eventual tool will need to implement. It will be revised (not just appended to) as more videos clarify or override earlier points. Treat this as the most "build-ready" section of the document — earlier narrative sections contain the full reasoning/context; this section is the distilled logic.

## Stock Universe Gate (must pass before any strategy applies)
A candidate stock must belong to one of: **V40**, **V40 Next**, or **V200** (static/maintained reference lists — see Reference Data section). Each strategy further restricts WHICH of these lists it can run on (see per-strategy universe below) — the V40/V40Next/V200 gate is necessary but not sufficient; the strategy-specific universe restriction is an additional filter on top.

## Fundamental Screening Logic Implemented So Far

```
V40 / V40 Next eligibility (qualitative — requires maintained list, not pure quant query):
  - Sector rank #1, #2, or #3 by sales AND net profit
  - Operating history >= 15-20 years
  - Near-zero debt
  - Low penetration / clear 10-20yr growth runway
  - Demonstrated pricing power (can raise price w/o losing volume)
  - Not a PSU/government company

V200 eligibility (quantitative — screener.in automatable; HARD qualifying thresholds):
  IF company is NOT a bank AND NOT an NBFC AND NOT functionally-lending (e.g. margin-lending stockbrokers):
    net_profit_ttm > 200 (crore INR)
    AND roce > 20 (%)
    AND debt_to_equity < 0.25
  IF company IS a bank OR NBFC OR functionally-lending (e.g. Angel One-style margin lending):
    net_profit_ttm > 200 (crore INR)
    AND roe > 10 (%)
    (debt_to_equity is NOT applicable/exempted entirely for this group)

ADDITIONAL HARD DISQUALIFIER (Video 4 — applies on top of V40/V40Next/V200, can reject an
otherwise-qualifying stock):
  IF (promoter_holding_pct * pledging_pct_of_promoter_holding) >= 10 (%, i.e. >=10% of TOTAL
     company shares are pledged by promoters):
    REJECT this stock entirely, regardless of other qualifying metrics

SOFT CAUTION FLAG (Video 4 — heuristic, NOT a hard disqualifier):
  weak_hands_pct = public_pct - hni_pct   (retail public only, excludes HNIs)
  IF weak_hands_pct > 30 (%):
    flag as soft caution / lower-priority candidate (do not auto-reject)

QUALITATIVE TIERING FOR RANKING AMONG ALREADY-QUALIFYING CANDIDATES (Video 4 — used to break ties
when multiple stocks pass all hard gates and a limited-capital choice must be made; NOT used to
disqualify):
  ROCE tiers (non-BFSI):       >30% = best   | 20-30% = very good   | <20% = fails hard gate above
  Debt/Equity tiers (non-BFSI): <10% = best   | 10-25% = very good   | >25% = fails hard gate above
  Preference order when choosing between multiple qualifying candidates: favor higher ROCE tier,
  then favor lower Debt/Equity tier, all else (business quality, strategy signal) being equal.

EXPLICITLY NOT USED AS SCREENING/SCORING INPUTS (Video 4 — confirmed irrelevant for this framework):
  - PE ratio (no weight, informational only)
  - Dividend yield (no positive weight; very high yield + flat price history = optional soft caution only)
  - Book-value-vs-price comparison (below book = mild positive only; above book = neutral, not negative)
  - Raw promoter holding percentage (superseded entirely by strong-hands/weak-hands framework above)
  - EBITDA (Part 2 — net profit is the only profitability metric used; EBITDA carries zero weight)
  - Cash flow statement (operating/investing/financing breakdown) as a standalone metric (Part 2 —
    superseded by the net_profit + depreciation calculation below)
  - Buyback-driven reductions in share capital/reserve should NOT be flagged as anomalies (Part 2 —
    benign, explainable pattern, not a red flag)

DATA HANDLING RULES (Video 4 — apply when pulling/parsing financial statement data, e.g. from
Screener.in):
  - Always prefer CONSOLIDATED financials over standalone when both are available; standalone only
    if no subsidiaries exist.
  - CAUTION: Screener.in's UI toggle button label is inverted relative to what's currently displayed
    (a button reading "View Consolidated" means STANDALONE is currently shown, and vice versa) — handle
    this correctly in any scraper/parser logic.
  - All quarterly revenue/profit comparisons MUST be YoY (same quarter, prior year), never sequential
    quarter-over-quarter, due to business seasonality.
  - "Other income" line items should be checked for irregular volatility across quarters as a soft
    data-quality/integrity flag (no specific numeric variance threshold has been given by the
    instructor yet — do not invent one; treat as a human-review flag if implemented).
  - (Part 2 — sharpened version of the above) Specifically flag a quarter where operating
    revenue/operating profit are roughly flat YoY but net profit swings sharply AND the swing is
    concentrated in the "other income" line — stronger, more specific signal than generic other-income
    volatility alone. Confirmed via a real worked example, not just a hypothetical.
  - (Part 2 — NEW check) Compare a quarter's EFFECTIVE TAX RATE against the company's typical/historical
    effective tax rate. A large, unexplained deviation (e.g., a quarter taxed at ~2% vs. a typical ~25%,
    or vice versa) is a second, independent signal of potential headline-profit timing manipulation,
    separate from the other-income check above. Flag, do not auto-reject.

"ONE BAD QUARTER" RULE (Part 2 — refines, does not contradict, the YoY comparison rule above):
  IF stock already passes the full fundamental gate (V40/V40Next/V200 + ratio thresholds + pledging
     check) AND has an established 10+ year track record of solid business/price performance:
    A single quarter's YoY decline in net profit should NOT be treated as a sell/avoid signal.
    Treat as a potential BUYING opportunity (temporary weakness) rather than a warning sign,
    UNLESS the decline is also seen broadly across SECTOR PEERS in a way that suggests a structural
    (not cyclical) problem specific to this company alone (i.e., check: are peers also down? if yes,
    likely cyclical/sector-wide and not a company-specific red flag; if this company alone is down
    while peers are not, treat with more scrutiny).

DEPRECIATION-ADJUSTED CASH CHECK (Part 2 — for evaluating reported net losses, especially in
turnaround-candidate or mature/non-expanding companies; NOT for actively-expanding companies):
  real_cash_generated_or_consumed ≈ net_profit_or_loss + depreciation_expense (same period)
  IF reported net_loss exists BUT real_cash_generated_or_consumed > 0:
    do NOT treat the headline net loss alone as a disqualifying/negative signal — the company may
    be cash-generative despite an accounting loss. Surface both figures together in any output.
  CAVEAT: do not apply this same "loss is fine because depreciation is high" logic to companies that
  are actively expanding/growing capacity (they need to deploy fresh capital, which itself creates
  future depreciation — the add-back logic is for distressed/mature companies specifically).

CWIP FORWARD-GROWTH SIGNAL (Part 2 — informational ranking boost, not a hard gate):
  cwip_to_fixed_assets_ratio = CWIP / Fixed_Assets
  A high ratio (CWIP comparable to or exceeding existing Fixed Assets) can be surfaced as a positive
  forward-looking growth indicator for an already-qualifying stock. No precise numeric threshold given
  beyond a real example where CWIP > Fixed Assets was associated with >100% future sales/profit growth
  expectation — treat as qualitative ranking signal only, not a new pass/fail gate.

CANDIDATE RANKING / TIE-BREAKING HIERARCHY (Part 2 — NEW, explicit multi-level priority order to apply
whenever more qualifying opportunities exist than available capital/position slots):
  1. Prefer V40 over V40 Next over V200 (in that order), all else equal.
  2. Among candidates within the same universe tier, prefer higher calculated potential-gain %
     (per the relevant strategy's own target formula).
  3. Among candidates with similar potential gain, apply the ROCE/Debt-Equity tiering tie-breaker
     (see tiering block above).
  This applies both across different stocks AND across multiple competing chart patterns on the
  same stock (e.g., if both an RHS and a CWH setup appear to be forming simultaneously, prefer
  whichever has the higher potential-gain calculation).
```

## Technical Strategy Logic Implemented So Far (8 of 8 total strategies — CONFIRMED FINAL COUNT per Video 6)

### Strategy 1: SMA Strategy
```
UNIVERSE: V40 only
TIMEFRAME: Daily candles
INDICATORS: SMA(200), SMA(50), SMA(20) — simple moving average only, computed on closing price

BUY, evaluated on daily close, executed next trading day at open:
  IF SMA(200) > SMA(50) > SMA(20) > Close:
    ENTER long, size = 3% of portfolio
    No stop-loss. No averaging — only 1 trade per stock under this strategy.

SELL, evaluated on daily close, executed next trading day at open:
  IF Close > SMA(20) > SMA(50) > SMA(200):
    EXIT the position opened above
```

### Strategy 2: Knoxville Divergence Strategy
```
UNIVERSE: V40 only
TIMEFRAME: Daily candles
INDICATOR: Knoxville Divergence (TradingView built-in; settings: bars_back=200, RSI period=14, momentum period=20)
  - Produces discrete uptrend/downtrend line segments based on RSI-oversold/overbought + momentum confirmation
  - Only the CONFIRMED END POINT of each line matters (start point and line length are irrelevant)

BUY, evaluated on daily close, executed next trading day at open:
  IF a new Knoxville downtrend line's end point is confirmed today:
    IF no open position in this stock under this strategy:
      ENTER long, size = 3% of portfolio
    ELSE IF 1 open position exists AND this new end point price <= (first_entry_price * 0.95):
      ENTER additional long (average), size = 3% of portfolio (total now 6%)
    ELSE:
      do nothing (signal exists but doesn't meet averaging gap, or already at max 2 trades)

SELL, evaluated on daily close, executed next trading day at open:
  IF a new Knoxville uptrend line's end point is confirmed today
     AND it is the FIRST such uptrend end point since the (most recent) entry:
    EXIT all open positions in this stock under this strategy (both initial and averaged trade, if any, exit together at this same point)

Max concurrent trades per stock: 2 (practical ceiling stated for V40; not a hard-coded platform limit but the observed/expected max)
No stop-loss.
```

### Strategy 3: V20 Strategy
```
UNIVERSE: V40, V40 Next, V200
TIMEFRAME: Daily candles
INDICATOR: None — pure price-action pattern detection

PATTERN DETECTION (run continuously, looking for new qualifying ranges):
  FOR each maximal run of consecutive green candles (zero red candles inside the run):
    low = MIN(low of all candles in run)
    high = MAX(high of all candles in run)
    move_pct = (high - low) / low * 100
    IF move_pct >= 20:
      register a new active range: {lower_line = low, upper_line = high, status = "unused"}

BUY, can trigger intraday (not dependent on daily close):
  FOR each active range with status "unused" or "used_but_reopenable":
    IF current_price <= range.lower_line:
      IF no open trades in this stock under this strategy:
        ENTER long at range.lower_line, size = 3% of portfolio, tag with this range
      ELSE IF 1 or 2 open trades exist AND range.lower_line <= (first_entry_price * 0.90)
           AND this specific range has not already been used for an open trade:
        ENTER additional long (average), size = 3% of portfolio, tag with this range
        (max 3 concurrent open trades per stock at any time)

SELL, can trigger intraday (GTT order recommended):
  FOR each open trade tagged with a specific range:
    IF current_price >= that range.upper_line:
      EXIT that specific trade (only that trade/slot, not necessarily all open trades in the stock)
      mark that range as "used" — it CANNOT be reused for entry again
      (a NEW range from a fresh 20%+ green-candle run is required for the next trade in this stock,
       even at the same price level)

Max concurrent trades per stock: 3 (rolling — a freed slot from an exited trade can be reused if a NEW qualifying range appears)
No stop-loss.
```

### Strategy 4: Reverse Head & Shoulder (RHS)
```
UNIVERSE: V40, V40 Next
TIMEFRAME: Daily candles
INDICATOR: None — geometric chart-pattern recognition
NOTE: Pattern detection is inherently fuzzier than Strategies 1-3; recommend human-in-the-loop
      confirmation of candidate patterns rather than full auto-execution (see Open Questions, Video 3).

PATTERN DETECTION:
  Identify candidate sequence: left_shoulder(s) -> head -> right_shoulder(s)
  CONSTRAINTS:
    - head.low must be the lowest point in the entire pattern (lower than every shoulder's low)
    - the 3 core connecting points (start of left shoulder, left-shoulder-end/head-start,
      head-end/right-shoulder-start) must lie on a HORIZONTAL line (the "neckline") —
      sloped necklines are INVALID, reject them
    - neckline drawing tolerance: may cross candle wicks and red-candle bodies,
      but must NEVER cross a green candle's body
    - multiple shoulders allowed per side (>=1 shoulder either side qualifies as "complex" -> higher confidence flag)
    - use non-log (linear) price scale for all measurements

BUY, can execute same-day late session or next-day open:
  AT the FIRST right shoulder (do not wait for subsequent shoulders):
    IF right_shoulder shows: base_formation (range consolidation) -> breakout above range
       -> breakout candle is GREEN -> confirmed on CLOSING basis:
      potential_gain_pct = (technical_target - breakout_price) / breakout_price * 100
      IF pattern's neckline is at/near lifetime high:
        REQUIRE potential_gain_pct >= 40 (hard minimum in this case)
      ELSE:
        potential_gain_pct >= 40 is RECOMMENDED but optional
      ENTER long, size = 3% of portfolio

TARGET CALCULATION:
  depth = neckline_price - head.low
  technical_target = neckline_price + depth
  final_sell_target = MAX(technical_target, lifetime_high)

SELL:
  EXIT when price reaches final_sell_target

No stop-loss. No independent averaging rule for RHS itself (averaging handled via Strategy 6: V10, layered on top).
```

### Strategy 5: Cup with Handle (CWH)
```
UNIVERSE: V40, V40 Next
TIMEFRAME: Daily candles
INDICATOR: None — geometric chart-pattern recognition (structurally = RHS minus the left shoulder)

PATTERN DETECTION:
  Identify candidate sequence: cup (no preceding left shoulder) -> handle(s)
  CONSTRAINTS:
    - cup.low must be the lowest point in the pattern
    - EVERY handle's low must be SHALLOWER (higher) than the cup's low — a handle as deep
      or deeper than the cup INVALIDATES the pattern
    - multiple handles allowed (>=2 handles -> "complex" -> higher confidence flag)
    - cup shape unconstrained (U, V, or irregular all valid)
    - wicks may be freely ignored when drawing the base-formation box
    - use non-log (linear) price scale for all measurements

BUY, can execute same-day late session or next-day open:
  AT the FIRST handle (do not wait for subsequent handles):
    IF handle shows: base_formation -> breakout above range -> breakout candle GREEN
       -> confirmed on CLOSING basis:
      potential_gain_pct = (technical_target - breakout_price) / breakout_price * 100
      IF pattern's neckline is at/near lifetime high:
        REQUIRE potential_gain_pct >= 40 (hard minimum)
      ELSE:
        potential_gain_pct >= 40 RECOMMENDED but optional
      ENTER long, size = 3% of portfolio

TARGET CALCULATION:
  depth = neckline_price - cup.low
  technical_target = neckline_price + depth
  final_sell_target = technical_target   # KEY DIFFERENCE FROM RHS: never raised to lifetime high

SELL:
  EXIT when price reaches final_sell_target (the technical_target itself, full stop)

No stop-loss. No independent averaging rule for CWH itself (averaging handled via Strategy 6: V10).
```

### Strategy 6: V10 Strategy (averaging overlay on RHS/CWH)
```
UNIVERSE: V40, V40 Next (inherited — V10 cannot run independently of an active RHS or CWH trade)
TIMEFRAME: Daily candles (intraday-aware for triggering, consistent with RHS/CWH)
INDICATOR: None

PRECONDITION: V10 is only active WHILE an RHS or CWH trade is open
  (i.e., between that trade's own buy signal and its own final_sell_target being hit).
  No RHS/CWH open position on this stock => V10 has zero trades available on this stock.

BUY:
  WHILE an RHS or CWH position is open on this stock:
    TRACK rolling local peak price since window opened (updates as new highs occur)
    IF current_price <= local_peak * 0.90 (i.e., a >=10% pullback from a local peak):
      IF 0 open V10 trades on this stock:
        ENTER long at current_price, size = 3% of portfolio
        v10_target = local_peak  (the level it pulled back from)
      ELSE IF 1 open V10 trade exists AND current_price <= (that V10 trade's entry_price * 0.95):
        ENTER additional V10 long (average), size = 3% of portfolio
        v10_target = local_peak for this new entry
      ELSE:
        do nothing (already at max 2 concurrent V10 trades, or gap requirement not met)

SELL (per individual V10 trade):
  IF current_price >= that V10 trade's own v10_target:
    EXIT that specific V10 trade only (full exit, no partial booking)

CONSTRAINTS:
  Max concurrent V10 trades per stock: 2
  Combined with the 1 underlying RHS/CWH trade: max 3 total concurrent trades per stock
  Combined max allocation per stock: 9% (3% RHS/CWH + 3% + 3% V10)
No stop-loss anywhere in this structure. No partial profit-booking on any trade.
```

### Strategy 7: "Three Times in Three Years" (Turnaround Strategy)
```
UNIVERSE: ALL NSE-listed stocks (NOT restricted to V40/V40Next/V200 — the only strategy in this
          framework with this broad a universe)
TIMEFRAME: Not chart-pattern/indicator based; relies on price-history + fundamental-data checks
INDICATOR: None — qualitative + quantitative checklist (10 conditions)
NOTE: This is the strongest candidate in the entire framework for human-in-the-loop review rather
      than full automation — verifying "the reason for decline no longer exists" is an open-ended
      business-research task, not a quantitative screen.

ELIGIBILITY GATE:
  IF stock is NOT listed on NSE:
    strategy does not apply, regardless of other conditions

CANDIDATE SCREEN (10 conditions, evaluated in sequence; all must hold):
  1. (lifetime_high - current_price) / lifetime_high >= 0.67
  2. Classify decline cause into one of three categories (diagnostic only, does not itself gate):
       A: revenue fell -> net profit fell -> price fell (business itself impacted)
       B: revenue intact, but net profit fell for another reason (e.g. rising interest cost,
          high fixed-cost operating leverage) -> price fell
       C: revenue AND net profit both intact -> price fell on sentiment/panic alone
  3. Confirm (qualitative/current research) that the identified cause in (2) no longer applies today
  4. Confirm company has a proven track record of good performance BEFORE the decline
  5. Confirm company has a good future growth prospect (reuse Video 1 business-quality framework)
  6. Confirm the LATEST quarterly result shows clear improvement (ideally a new quarterly record)
  7. AT THE MOMENT conditions 1-6 are all confirmed:
       (lifetime_high - current_price_now) / lifetime_high >= 0.50
       (if price has already re-rated past this point, the entry window has closed)

IF all 7 conditions hold:
  ENTER long, size = 3% of portfolio
  No averaging. No stop-loss.

EXIT:
  8. IF gain_pct >= 100% within 12 months of entry:
       EXIT, book profit (default rule)
  9. ELSE (12 months pass without hitting 100% gain):
       HOLD with no further time limit, until price reaches the ORIGINAL lifetime_high
       (no stop-loss, no re-evaluation deadline)

  KNOWN DOCUMENTED EXCEPTION: the instructor's own real-world conduct shows deliberate deviation
  from rule 8 (continuing to hold past a 100% gain for a much larger target) when conviction is
  exceptionally high. Do NOT silently auto-apply this override — default to rule 8/9 as stated,
  and expose any "hold for extended target" decision as an explicit, separately-flagged user
  override on that specific position, not a silent agent behavior.

10. "Blessings"/mindset condition — not computable. Closest operational proxy already covered
    elsewhere in this framework: do not panic-sell during long flat periods; volatility and
    holding period are explicitly NOT within the trader's control (see Video 2 framework).

GENERALIZABLE INTERPRETIVE AID (fee/service-based businesses specifically, e.g. asset managers,
brokers): high fixed-cost-to-revenue businesses show AMPLIFIED net profit swings relative to
revenue swings, in both directions. A modest revenue recovery can produce a much larger profit
recovery for this business type — useful context when evaluating Condition 6 for such businesses,
not a hardcoded multiplier.
```

### Strategy 8: "Lifetime High Strategy" (LTH)
```
UNIVERSE: V40, V40 Next ONLY (NOT V200, NOT NSE-wide)
TIMEFRAME: Daily candles
INDICATOR: None — fundamental-trigger + price-level rule

BUY:
  IF ttm_revenue == max(historical_ttm_revenue_series)        # currently at all-time-high TTM revenue
     AND ttm_net_profit == max(historical_ttm_net_profit_series)   # AND all-time-high TTM net profit
     AND (lifetime_high - current_price) / lifetime_high >= 0.30:  # AND price is >=30% below lifetime high
    ENTER long, size = 3% of portfolio

AVERAGING (more generous than other strategies in this framework):
  FOR each additional 10-percentage-point increment of decline from lifetime high
     (i.e., at -40%, -50%, -60%, ... from lifetime high):
    IF ttm_revenue and ttm_net_profit are STILL at their all-time highs AT THE TIME of this
       potential additional entry (re-check at each averaging opportunity, do not assume the
       initial-entry condition still holds):
      ENTER additional long, size = 3% of portfolio
    ELSE:
      do NOT average at this point, even though price has fallen further

  Maximum comfortable total allocation to one stock under this strategy: up to 10% of portfolio
  (explicitly higher than the framework's normal ~9% ceiling elsewhere, justified by the
  combination of V40/V40Next-only universe + the requirement that fundamentals remain at
  all-time highs even while averaging).

SELL:
  EXIT when current_price reaches lifetime_high (the same reference point used for entry).
  No stated time limit; realistic range observed: ~8 months to ~1.5 years, average ~1 year.

No stop-loss.

SECTOR-CONCENTRATION EXCEPTION (explicit, narrow):
  IF multiple simultaneous LTH-qualifying opportunities exist within IT services OR banking
     specifically, resulting in 30-40%+ of total portfolio concentrated in that one sector:
    this is EXPLICITLY ACCEPTABLE — do not apply an automatic sector-diversification cap to
    block this for these two specific sectors. No equivalent blessing was given for other
    sectors; do not generalize this exception beyond IT services and banking without further
    confirmation from source material.
```


## Portfolio-Construction Layer: The Four Categories (Video 6 — the master switchboard tying everything above together)

**This is the most important addition from Video 6 for the agent's overall architecture.** The 8 individual strategies above are building blocks; this layer defines how a real user actually combines them into a single coherent, disciplined approach. The agent should require a user to select (or define a custom equivalent of) one of these before generating any buy signals, rather than freely mixing all 8 strategies across all 3 universes by default.

```
CATEGORY 1 — "LTH Only"
  universe: V40 + V40 Next
  strategies_enabled: [Strategy 8 only]
  idle_capital_rule: hold cash if no qualifying signal exists; do not substitute another strategy
  max_per_stock: up to 10% (per Strategy 8's own averaging rules)

CATEGORY 2 — "All 8 Strategies, V40-Only"
  universe: V40 ONLY (V40 Next and V200 explicitly excluded)
  strategies_enabled: [Strategy 1, 2, 3, 4, 5, 6, 7 (narrowed to V40 names only under this
                        category), 8]  — i.e., literally all 8, but only ever applied to V40
                        stocks specifically
  multi_signal_same_stock_rule: if a V40 stock triggers signals from multiple different
    strategies at different times, each can be taken as a separate trade, PROVIDED each new
    entry is >=10% lower in price than the immediately preceding trade on that same stock
  max_per_stock: ~9-10% total across all strategies combined on that stock (thumb-rule ceiling)

CATEGORY 3 — "Four Named Strategies, V40 + V40 Next"
  universe: V40 + V40 Next
  strategies_enabled: [Strategy 1 (SMA), Strategy 4 (RHS), Strategy 5 (CWH), Strategy 6 (V10)]
  explicitly_excluded: [Strategy 2 (Knoxville), Strategy 3 (V20), Strategy 7, Strategy 8]
  (no additional rules beyond each individual strategy's own documented logic — this category
   is purely a strategy-subset selection)

CATEGORY 4 — "V20 Only"
  universe: V40 + V40 Next + V200 (broadest single-strategy universe)
  strategies_enabled: [Strategy 3 only]
  idle_capital_rule: hold cash if no qualifying signal exists; do not substitute another strategy
  notable_property: both entry AND exit prices are known in advance the moment a range is
    identified -> fully automatable via GTT orders, requiring no daily/intraday monitoring
    once placed -> best suited for users with minimal available monitoring time

CROSS-CATEGORY RULES:
  - A user selects exactly ONE category as their active trading configuration.
  - Minimum commitment period before evaluating results or switching: 1 year.
  - Categories are not meant to be mixed; the agent should not generate signals from a
    strategy/universe combination outside the user's selected category.
  - RECOMMENDED (not mandatory) agent feature: track/surface SHADOW performance for the
    3 non-selected categories in parallel (signals that WOULD have triggered under them),
    without actually executing trades under them, so the user has real comparative data
    after the 1-year commitment period.
  - Categories 1-4 are illustrative presets, not the only valid configurations — the
    underlying 8-strategy, 3-universe building blocks are fully modular. Consider allowing
    a user-defined custom category (a "Category 5+") that selects its own strategy subset
    and universe, using the same general rule structure as Categories 1-4 above.
```

## Existing-Portfolio Reconciliation Logic — Final, Confirmed Version (Video 6 — supersedes/finalizes the Video 2 §2.6 draft version)

```
FOR each currently-held stock (regardless of how/when it was originally acquired):
  IF a strategy signal from the user's ACTIVE CATEGORY's enabled strategy set is currently
     applicable to this stock:
    -> hold/exit strictly at that strategy's own defined target. No other action.
  ELSE (no enabled strategy currently applies to this stock):
    IF the stock is currently profitable:
      -> exit immediately; redeploy capital into the next qualifying opportunity under the
         active category, or hold as cash per that category's idle-capital rule if none exists
    IF the stock is currently at a loss:
      -> hold and wait for recovery, PROVIDED the company still passes the fundamental
         V40/V40Next/V200 quality gate (incl. the pledging disqualifier and ratio thresholds)
      -> do NOT sell at a loss merely due to impatience or because other holdings are
         outperforming in the interim

ADDITIONAL CONFIRMED SUB-RULES:
  - A pattern (RHS/CWH/etc.) is NOT "applicable" until fully formed and confirmed — a
    partially-formed, not-yet-broken-out pattern does not count as an active signal, and
    must not be anticipated/front-run.
  - Once a pattern/range has had a signal taken against it, it is locked to its original
    reference points — later price action never retroactively redraws or relocates it;
    a fresh, separate pattern is required for any further trade.
  - A completed strategy cycle (entry + exit signal already triggered) is CLOSED — do not
    wait for a second/later exit signal of the same type before considering the position closed.
  - Multiple separate portfolios (e.g., user's own + spouse's) are NEVER combined for
    position-sizing (3%-of-portfolio) purposes; each is sized independently against its own
    total value. The same signal CAN be taken independently in each portfolio.
  - The "~33 stocks" diversification guideline applies PER PORTFOLIO, not as a shared cap
    across multiple portfolios belonging to the same user/household.
  - Idle cash awaiting deployment IS counted as part of total invested capital for CAGR/
    performance-calculation purposes (it is not excluded from the denominator just because
    it isn't currently in an open position).
```

## Situational Risk Flags (Video 6 — qualitative, news/corporate-action-driven; not part of the quantitative screening gate)

```
These require periodic manual/news-based review rather than a pure quantitative trigger:
  - STRUCTURAL (not temporary) competitive disadvantage: e.g., BSE Ltd. — durable, ongoing
    loss of trading volume/liquidity to NSE. Does NOT qualify as a Strategy 7 or Strategy 8
    candidate even if heavily down from its highs, because the cause is not a resolved or
    resolvable temporary event (fails Strategy 7's Condition 3 test).
  - MERGER / MINORITY-SHAREHOLDER RISK: avoid or flag stocks currently subject to an
    announced merger/amalgamation into a parent/group company where the smaller entity's
    standalone valuation appears to be getting compressed unfavorably in the deal terms
    (named examples: certain Tata group restructuring/merger situations).
  - SECTOR-LEVEL SOFT CAUTION: small-cap/cyclical auto-ancillary companies flagged as a
    class-level caution by the instructor, without a specific numeric trigger — treat as a
    qualitative downweighting factor, not a hard exclusion rule.
  - SHAREHOLDING-PATTERN DATA-QUALITY CHECK: a sudden large jump in FII/DII percentage with
    a corresponding drop in "public" percentage in the same reporting period may reflect a
    RECLASSIFICATION/reporting correction of the same underlying holders into the correct
    bucket, NOT real net institutional buying — do not treat such a shift, by itself, as a
    strong bullish institutional-accumulation signal without further verification.
  - BROKER/CUSTODY SAFETY: prefer large, profitable brokers for account custody (Zerodha,
    Upstox, Angel One named as acceptable); avoid loss-making brokers (Paytm Money named as
    an example to move away from) — this is account-safety guidance, not a stock-screening
    rule, but relevant if the tool ever touches broker selection/account-linking.
```

## Cross-Strategy Operating Rules
```
- Never justify a single trade using signals from more than one strategy simultaneously (pick one strategy per trade decision) — EXCEPTION: V10 is explicitly designed to layer on top of an active RHS or CWH trade; this is the one sanctioned case of combining strategy logic, since V10 cannot exist without a parent RHS/CWH signal.
- None of the 7 strategies documented so far use stop-loss. Risk control = position sizing caps + universe quality gate + averaging-gap rules only.
- No partial profit-booking on any strategy — each trade/slot is held to its own full defined target, then exited completely.
- Existing portfolio reconciliation (for stocks already held, not bought via these strategies):
    IF a strategy signal is currently active/applicable on the held stock -> exit at that strategy's defined target
    ELSE IF position is currently profitable -> exit immediately (no defined target exists otherwise)
    ELSE (no strategy applicable AND at a loss) -> hold, provided the company still passes the relevant quality criteria
    (Part 2 — clarified: this reconciliation block applies to stocks within V40/V40Next/V200 for Strategies
     1-6. Held stocks outside V40/V40Next/V200 entirely are out of scope for Strategies 1-6's logic, but
     MAY still be in scope for Strategy 7 ["Three Times in Three Years"] specifically, since Strategy 7's
     universe is all NSE-listed stocks rather than V40/V40Next/V200. When reconciling an existing holding,
     check Strategy 7's 10-condition checklist as a separate possible path before concluding a non-V40/
     V40Next/V200 holding is entirely out of scope.)
- Minimum absolute trade size: do not enter a position below ₹10,000 even if 3% of current capital is smaller than that (relevant for small/growing portfolios).
- Position sizing base (Part 2 — clarified): the 3%-per-trade calculation is always based on TOTAL
  CURRENT portfolio value at the time of each new trade, recalculated as capital is added over time
  (e.g., via monthly contributions) — not fixed against the original starting capital. This applies
  uniformly across all 7 strategies, including Strategy 7.
- Maintain a separate internal ledger of strategy-attributed entries/exits/P&L — broker statements will show FIFO-based accounting which will NOT match strategy-level trade tracking when averaging is used.
- Pattern-validity (RHS/CWH) must never depend on identifying or validating a "reason" for a price decline (no news-sentiment filtering) — only chart geometry and the fundamental quality gate matter. NOTE: this is explicitly DIFFERENT for Strategy 7, where understanding and verifying the reason for decline (and its resolution) is itself a REQUIRED, central part of the strategy (Conditions 2-3) — do not conflate the two strategies' opposite treatment of "reason for decline."
- A user need not run all 7 (possibly 7-8) strategies simultaneously — the tool should support enabling/disabling individual strategies per user preference; using even one strategy with discipline is treated as sufficient by the instructor.
- (Part 2 — NEW) Switching directly from one strategy's exit signal into a different strategy's entry signal on the SAME stock, without round-tripping through cash, is explicitly permitted — track as a new trade under the new strategy's own rules via the internal ledger.
- (Part 2 — NEW) Always-100%-invested philosophy: never recommend exiting an existing, not-yet-target-hit position early merely to fund a different, newer, possibly more attractive opportunity. Existing positions are only ever exited via their own strategy's defined exit rule.
- (Part 2 — NEW) False-breakout handling in pattern geometry (RHS/CWH): if price briefly breaks above a prior resistance/peak before falling back to continue building a base/handle/shoulder, do NOT relocate the neckline reference point to that false-breakout level — the neckline must still originate from the ORIGINAL peak/resistance on the left side of the pattern.
- (Part 2 — NEW) Candidate ranking/tie-breaking hierarchy: when more qualifying opportunities exist than available capital, apply in order: (1) universe tier preference V40 > V40 Next > V200, (2) higher potential-gain % within the same tier, (3) ROCE/Debt-Equity tiering as a final tie-breaker. See full pseudocode in the Fundamental Screening Logic block above. (Video 5 — Strategy 7 sits outside this tiering since it operates on the broader NSE universe; treat Strategy 7 candidates as a separate, parallel opportunity pool rather than slotting them into the V40>V40Next>V200 hierarchy.)
- (Video 5 — NEW) Strategy 7 ("Three Times in Three Years") is the one explicit, documented exception to the framework's default behavior of NOT factoring in "reason for price decline" — for this strategy specifically, correctly identifying and verifying the resolution of the decline's cause is a required, gating step (Conditions 2-3), not an excluded input.
- (Video 5 — NEW) Strategy 7's exit rule (100% gain in 12mo, else hold to lifetime high) has one documented real-world exception: the instructor himself deviates from this rule when conviction is exceptionally high, choosing to hold for a much larger target instead of exiting at the 100% mark. The agent should default to the literal rule and treat any "hold for extended target" decision as a separate, explicit, user-initiated override — never an automatic/silent deviation.
```

## Items Explicitly Flagged as "Philosophy, Not Yet a Rule" (carried over, still applicable)
- Multibagger market-cap-gap insight (Video 1, Section 1.2 related concept) — partially formalized in Video 4 (Section 4.2: market-cap-gap vs. revenue-gap divergence check is now a usable heuristic), but still lacks a hard numeric threshold for "how big a divergence triggers a flag" — treat as a ranking/contextual signal, not a hard screen.
- "Complex pattern is more reliable than simple pattern" (RHS and CWH, Video 3) — qualitative claim only, no quantified win-rate difference given. Can be surfaced as a confidence flag/label in the UI, but should NOT be hard-coded as a numeric scoring weight without further data.
- PSU bank re-rating thesis (Video 4, Section 4.2 — PNB vs. Kotak example) — illustrative macro reasoning only, no programmable trigger condition given for when/whether this re-rating occurs. Do not encode as a screening rule.
- "Other income" volatility check (Video 4, Section 4.13) — now backed by one confirmed real-world example (Part 2) and paired with a second, independent tax-rate-deviation check, but still has no hard numeric variance threshold for either signal. Treat both as flags for human review / discounting a specific quarter's headline number, not as auto-reject triggers.
- CWIP-to-fixed-assets ratio as a forward-growth signal (Video 4 Part 2, Section 4.16) — directionally useful, but no precise numeric threshold given for what counts as a meaningfully high ratio beyond one worked example. Treat as a qualitative ranking signal only.
- Operating-leverage effect for fee/service-based businesses (Video 5, Section 5.4) — directionally correct and illustrated with one numeric example, but no generalizable formula/multiplier given. Treat as contextual/interpretive guidance specific to evaluating Strategy 7 candidates in this business category, not a hardcoded ratio.
- Strategy 7's Condition 10 ("blessings"/mindset) — explicitly acknowledged as non-computable; its only operational proxy is the already-existing "volatility and holding period are not in your control" discipline principle, which needs no new logic.

## Items Resolved From "Philosophy" to "Confirmed Rule" This Update
- (Video 2, reconfirmed through Video 6) Stop-loss avoidance: remains consistent across all 8 strategies now documented; no change this update.
- (Video 4 Part 1, newly confirmed) Promoter pledging disqualifier: promoted from general "be careful of debt/pledging" sentiment into a precise, computable hard-disqualifier formula (`promoter_holding_pct * pledging_pct_of_promoter_holding >= 10%` → reject). This is now an enforceable rule layered on top of the V40/V40Next/V200 gate.
- (Video 4 Part 1, newly confirmed) ROCE and Debt/Equity tiering: the single hard V200 thresholds from Video 1 (ROCE>20%, D/E<0.25) now have explicit internal "best/very good" sub-tiers usable for ranking/tie-breaking among already-qualifying candidates — promoted from implicit ("more is better") to an explicit, ordered tiering rule.
- (Video 4 Part 1, newly confirmed) Promoter holding percentage is explicitly NOT a usable standalone screening signal — fully superseded by the strong-hands/weak-hands formula. This was implied as early as Video 1 but is now stated as a direct, explicit rule with counter-examples.
- (Video 4 Part 1, newly confirmed) PE ratio, dividend yield, and book-value-vs-price comparisons are explicitly confirmed as NOT screening/scoring inputs for this framework (PE and dividend yield carry zero weight; book value below price is a mild positive only, never a negative).
- (Video 4 Part 2, newly confirmed) The "one bad quarter doesn't matter" rule: promoted from implicit/anecdotal sentiment into an explicit, conditional rule (applies only to stocks with an established 10+ year track record that already pass the full fundamental gate) — directly refines how the agent should react to a YoY quarterly decline rather than treating it as an automatic caution signal.
- (Video 4 Part 2, newly confirmed) EBITDA and standalone cash-flow-statement analysis are explicitly confirmed as carrying zero screening weight — net profit (optionally adjusted for depreciation per Section 4.16) remains the sole profitability metric used throughout this framework.
- (Video 4 Part 2, newly confirmed) A multi-level candidate ranking/tie-breaking hierarchy (universe tier → potential gain % → ROCE/D-E tiering) is now explicit and directly implementable as the agent's default opportunity-prioritization logic, resolving a previously-unaddressed ambiguity about how to choose between multiple simultaneously-qualifying opportunities.
- (Video 4 Part 2, newly confirmed) Position-sizing base for the 3%-per-trade rule is explicitly confirmed to be the total CURRENT portfolio value (recalculated as capital is added), not the original starting capital — resolves a previously-unstated ambiguity carried since Video 2.
- (Video 5, newly confirmed) "3 times in 3 years" is fully defined as Strategy 7: a 10-condition turnaround checklist applicable to the entire NSE universe (not V40/V40Next/V200-restricted) — resolves the long-standing open item carried since Video 2.
- (Video 5, newly confirmed) "Reason for price decline" is normally excluded from this framework's logic (per Video 3's RHS/CWH rule) EXCEPT for Strategy 7, where understanding and verifying the resolution of the decline's cause is an explicit, required, gating condition. This is now documented as a deliberate, isolated exception rather than a contradiction.
- (Video 5, newly confirmed) The instructor's own real-world deviation from his stated 100%-gain exit rule (Strategy 7, Condition 8) under high conviction is now documented as a known, intentional exception — the agent should default to the literal rule and treat any extended-hold decision as a separate, explicit user override, never a silent deviation.
- (Video 6, newly confirmed) Strategy 8 ("Lifetime High Strategy") is fully defined — corrects the Video 5 closing-note expectation that the final session would add no new strategy. Total strategy count finalized at exactly 8.
- (Video 6, newly confirmed) The four-category portfolio-construction framework is now the agent's required top-level configuration layer — a user must select one category (or an equivalent custom configuration) rather than freely mixing all 8 strategies across all 3 universes by default. This resolves a structural gap that existed throughout Videos 2-5: individual strategies were fully defined, but how to combine them into one coherent personal approach was not.
- (Video 6, newly confirmed) The existing-portfolio reconciliation logic (originally drafted in Video 2 §2.6, refined in Video 4 Part 2) is now finalized in its complete form, including the "pattern not yet applicable until fully confirmed" and "completed cycle is closed" sub-rules — resolves residual ambiguity that surfaced repeatedly in Q&A across Videos 3-5.
- (Video 6, newly confirmed) Multiple separate portfolios are never combined for position-sizing purposes, and the ~33-stock diversification guideline applies per-portfolio — resolves an ambiguity left open since Video 2.

---//---

# CHANGE LOG
- **Update 1:** Initial document created from Video 1 transcript (stock universe framework: V40/V40 Next/V200 definitions and conditions) + user-supplied V40/V40 Next constituent lists. No technical strategies yet documented.
- **Update 2:** Added Video 2 (Section 2): three fully codeable technical strategies — Simple Moving Average Strategy, Knoxville Divergence Strategy, and V20 Strategy — including exact entry/exit conditions, position sizing, averaging rules, applicable stock universes, and execution timing for each. Rewrote Consolidated Agent-Ready Rules section to include runnable pseudocode for all three strategies. Promoted "no stop-loss" from philosophy to confirmed operating rule. Flagged V200 static list compilation as a higher-priority dependency (needed for V20 strategy). Logged several open Q&A-derived operational rules (portfolio reconciliation logic, FIFO/ledger tracking caveat, minimum trade size floor, one-strategy-per-trade rule).
- **Update 3:** Added Video 3 (Section 3): three more strategies — Reverse Head & Shoulder (RHS), Cup with Handle (CWH), and V10 (an averaging overlay strategy that only operates within an active RHS/CWH trade window) — bringing the documented total to 6 of 7-8 strategies. Added pseudocode for all three to the Consolidated Rules section, including the one sanctioned exception to the "one strategy per trade" rule (V10 layering on RHS/CWH). Flagged RHS/CWH pattern-recognition as a fundamentally different (fuzzier, more subjective) engineering problem than the indicator/price-action rules in Strategies 1-3, and recommended human-in-the-loop confirmation as a safer initial build approach. Confirmed "no partial profit-booking" as an explicit rule. Logged the instructor's explicit rejection of a community/shared-alert feature as a relevant product-design data point. Noted that a fundamental/financial-analysis-focused video is referenced as coming next.
- **Update 4:** Added Video 4 Part 1 (Section 4.1-4.14): a dedicated fundamental/financial-analysis session with no new trading strategies, but substantial refinements to the fundamental screening gate first established in Video 1. Key additions: (a) a new hard disqualifying rule based on promoter share-pledging (`promoter_holding% * pledging%-of-promoter-holding >= 10%` → reject), (b) explicit ROCE and Debt/Equity tiering ("best" vs. "very good") for ranking/tie-breaking among already-qualifying candidates, (c) a precise strong-hands/weak-hands formula replacing raw promoter-holding as a shareholding-quality signal, with a >30% weak-hands soft-caution threshold, (d) explicit confirmation that PE ratio, dividend yield, and book-value-vs-price comparisons carry no screening weight in this framework, (e) a market-cap-gap vs. revenue-gap divergence check that refines the Video 1 "multibagger" informal heuristic into a more usable (though still not fully quantified) comparative tool, (f) data-handling rules for consolidated-vs-standalone reporting (including a Screener.in-specific UI-label inversion gotcha) and mandatory YoY (not sequential) quarterly comparison.
- **Update 5:** Added Video 4 Part 2 (Sections 4.15-4.20, same class/session continued — kept under the existing Video 4 heading rather than creating a separate "Video 5" label): (a) the "one bad quarter doesn't matter" rule for already-qualified, long-track-record stocks, refining (not contradicting) the YoY comparison rule, now confirmed via real worked examples including a detailed Reliance Industries tax-rate-manipulation case study; (b) a new, independent effective-tax-rate-deviation check as a second manipulation-detection signal alongside the existing other-income check; (c) full depreciation/Fixed-Assets/CWIP mechanics, including a concrete `net_profit + depreciation` real-cash-position formula for evaluating reported losses (with an explicit caveat that this should not be applied to actively-expanding companies); (d) a CWIP-to-Fixed-Assets ratio as a qualitative forward-growth ranking signal; (e) explicit rejection of EBITDA and standalone cash-flow-statement analysis as screening inputs; (f) confirmation that share buybacks are a benign, explainable reason for reserve/share-capital decline, not an anomaly; (g) a new, explicit multi-level candidate ranking/tie-breaking hierarchy (universe tier → potential gain % → ROCE/D-E tiering) for prioritizing among multiple simultaneously-qualifying opportunities; (h) clarification that the 3%-per-trade position-sizing base is always current (not original) total portfolio value; (i) a pattern-geometry refinement for handling false breakouts without relocating the neckline reference point; (j) confirmation that switching directly between strategies on the same stock without round-tripping through cash is permitted; (k) confirmation of an "always stay fully invested, never pre-empt an existing position for a new opportunity" portfolio philosophy. Rewrote the Fundamental Screening Logic and Cross-Strategy Operating Rules blocks in the Consolidated Rules section to incorporate all of the above. Updated the Philosophy/Confirmed-Rule tracking lists accordingly. Confirmed via direct Q&A that the next video will cover the "3 times in 3 years" strategy (the 7th of 7-8 total).
- **Update 7:** Added Video 5 (Section 5): the 7th strategy, "Three Times in Three Years" — a turnaround-stock strategy explicitly applicable to the ENTIRE NSE-listed universe (~1,600 companies) rather than being restricted to V40/V40Next/V200, built around a 10-condition checklist (67%+ decline from lifetime high; classify decline cause into one of three categories — business-impacted, financials-only-impacted, or sentiment-only; confirm the cause no longer applies; confirm prior track record; confirm future growth prospect; confirm latest-quarter improvement; confirm price is still ≥50% down at signal confirmation; exit at 100% gain within 12 months or hold to lifetime high otherwise; plus a non-computable "blessings"/mindset condition). Walked through three full worked examples, one per decline-cause category (Motilal Oswal Financial Services, JP Power, Equitas Holdings), including a documented real-world exception where the instructor deviates from his own stated exit rule under high conviction. Added a generalizable operating-leverage interpretive note for fee/service-based businesses. Added full pseudocode for Strategy 7 to the Consolidated Rules section, and updated the Cross-Strategy Operating Rules to explicitly carve out Strategy 7's two deliberate exceptions to otherwise-universal framework rules. Noted (per the instructor's closing remarks at the time) that one final session remained, expected to cover portfolio-construction guidance without a new strategy — an expectation that Video 6 subsequently corrected.
- **Update 8 (this update):** Added Video 6 (Section 6) — the final session of the course. Two major additions: **(A)** Strategy 8, "Lifetime High Strategy" (LTH) — applicable to V40/V40Next only, triggered when a company posts simultaneous all-time-high TTM revenue AND TTM net profit while trading 30%+ below its lifetime high, exited at lifetime high, with a notably more generous ~10% max single-stock allocation (vs. ~9% elsewhere in the framework) and an explicit, narrow sector-concentration exception for IT services and banking. **(B)** The Portfolio-Construction Layer: four named, mutually-exclusive categories (Category 1: LTH-only; Category 2: all 8 strategies on V40-only, explicitly claimed sufficient to reach USD-billionaire status over time; Category 3: SMA+RHS+CWH+V10 on V40+V40Next; Category 4: V20-only across all three universes, the most "set-and-forget"-compatible via GTT orders) that a user should pick exactly one of and commit to for a minimum of one year, rather than freely mixing all 8 strategies. Finalized the existing-portfolio reconciliation logic (including "pattern not yet applicable until confirmed" and "closed cycle stays closed" sub-rules). Added a new "Situational Risk Flags" qualitative checklist (structural competitive disadvantage e.g. BSE Ltd.; merger/minority-shareholder risk; auto-ancillary sector caution; FII/DII reclassification data-quality check; broker/custody safety). Resolved several previously-open ambiguities: multiple-portfolio position-sizing independence, idle-cash treatment in CAGR calculations, and the ~33-stock guideline being per-portfolio. Corrected the Video 5 closing-note assumption that no 8th strategy would be introduced. This is documented as the final video in the core course — the knowledge base is now considered feature-complete for the full 8-strategy, 3-universe, 4-category framework, pending only the previously-referenced (but not yet delivered) CAGR-calculation spreadsheet walkthrough or any further material the user chooses to provide.

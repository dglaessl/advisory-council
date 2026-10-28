---
decision_id: 2026-10-28-trading-agent-review
date: 2026-10-28
project: trading-agent
mode: delivery
revisit_on: 2027-01-13
status: approved-by-daniel
---

# Trading agent review: risk, performance and improvement measures

## Question
How risky is the Robinhood crypto agent, how is it performing, and what
specific measures should improve it — respecting Daniel's 2026-10-23 decision
to freeze the trading rules until the 2027-01-13 review?

## Seats convened
- Quant & Risk Officer — Claude Opus (veto seat) — independent draft
- Evaluator — Claude Sonnet — independent draft + eval scripts in `evals/trading-agent/`
- Red Team — Agent Zero, openai/gpt-6.1-sol — attacked both drafts
  (redacted bundle: no account identifiers left the system)
- Chair — Claude Opus — data pull (read-only), verification, synthesis

## Recommendation (Chair)
Keep the agent running, but fix how it is *operated* now — these are
operations changes, not strategy changes, so they respect the rules freeze.
Treat the Jan 13 review as a decision between "active trading earns its keep"
and the default of **core + weekly DCA with no active trading**, judged by a
rule written down now.

**Confidence:** high on the operational findings (verified in the code and
journal); low on anything about strategy skill (11 days, 1 closed trade).

## Performance (2026-10-28 11:41 UTC)
- Deposits $2,260.47; equity $2,232.23 at mark ($2,215.88 at bid).
  Net -$28.24 (-1.25%); vs hold-BTC -$20.15 (-0.89%). Statistically noise.
- Gap attribution (Evaluator): ETH core vs BTC -$6.8 (owner's in-kind choice),
  NEAR stop loss -$7.2, spreads -$5.6, residual -$0.5.
- Trading side: 1 closed trade (NEAR -15%), 3 open lots -1% to -3%, no
  breakout entries since the breakout-only rule started (2026-10-19).
- Costs: ~1.9% round-trip spread; limit-at-mark entries filled 0 of 5, every
  market fill ~0.93% above mark.

## Key findings
1. **Two trading runs can overlap (veto-level, Quant).** No lock between the
   daily cycle (00:20 UTC) and the 2-hourly check (:50), which can start a full
   cycle on "missed cycle" or "new funds". Two cloud cycles 13 min apart on
   2026-10-22 show it nearly happened. Duplicate runs can spend all buying
   power or mis-size a sale that reaches core BTC (Red Team: not bounded to one
   order as Quant first said).
2. **Deposit detection is model judgment, not reconciliation.** The 2026-10-24
   NEAR stop fill was booked as a deposit despite the existing "no sale explains
   it" rule; the fix lives only as a journal note.
3. **Stops may not protect in a gap, and they all expire ~2027-01-15.** Each
   stop's price field sits 5% below its trigger (likely a collar — unverified).
   "Stops intact" is the model's assertion, not a broker reconciliation.
4. **Concentration is the real money risk.** 68.5% of equity is an untraded,
   unprotected BTC/ETH core. If crypto falls 30/50/70% and no stop fills:
   -$518 / -$863 / -$1,208 (-23% / -39% / -54% of equity). The circuit breaker
   excludes the core, and weekly deposits inflate the "peak".
5. **Hard rules are prose.** `.claude/settings.json` allows order placement
   with no size/account/count limit; the CHECK routine runs with the same
   permissions. The `STOP` file also blocks risk-reducing exits.
6. **The benchmark is not like-for-like and the backtest deserves low weight**
   (~60 configurations on one 3.8-year history, fills at the signal close,
   survivorship bias; the 0.3% spread rows are contradicted by live fills).
7. **The agent's own running cost is unmeasured** (Red Team). With ~$700 of
   trading capital, a 10%/yr edge is ~$70/yr — less than modest operating cost.

## Measures
**Now (operations — within the rules freeze):**
1. Make the 2-hourly CHECK **alert-only**: it never starts a trading cycle.
   Deposits wait for the next daily cycle (irrelevant for weekly DCA). Missed
   cycles alert Daniel instead of catching up. This removes the concurrency
   path entirely and is simpler and safer than a git lock.
2. Add a git-based run lock to CYCLE.md anyway (atomic via rejected push,
   with owner/run ID, never auto-steal; a stale lock alerts instead).
3. Deterministic reconciliation each cycle: list orders filled since the last
   cycle + `pending_deposits` change before classifying cash; anything
   unexplained → no core buy, `ACTION NEEDED`.
4. Broker-verified stops each cycle (ID, quantity, trigger vs journal); flag
   any stop older than 75 days. Re-place all stops before 2027-01-15.
5. Daniel to confirm what the stop order's price field means (Robinhood app or
   support). Until known, treat stops as possibly failing in a >5% gap.
6. Hermes watchdog: alert on Telegram if no cycle commit in 26 h or any
   `ACTION NEEDED` summary.
7. Write the kill procedure: disable both routines and remove the connector's
   agentic access; decide explicitly what happens to open trading lots.
8. Measurement: log the like-for-like benchmarks B2/B3, a per-cycle signal log
   (brk=Y coins and why skipped), and the agent's running cost.
9. Daniel to explicitly acknowledge (or change) the core concentration.

**At the 2027-01-13 review (strategy):**
- Apply the pre-registered rule in `evals/trading-agent/prereg_2027-01-13.yaml`
  with the Red Team's amendment: **default is core + DCA, trading capital
  idle or added to the core**, unless active trading shows a credible net
  benefit after spreads and running costs AND the operational controls above
  ran without failure.
- Fix the limit-at-mark entry step (0 of 5 fills; it only adds a 2-minute
  cancel/replace risk) — e.g. limit at the ask, or straight market orders.
- Revisit core/ETH allocation and a deposit-adjusted circuit breaker.

## Dissent
- **Evaluator:** no trades so far is not evidence of failure; never judge
  alpha on fewer than 30 closed trades. → Chair: agreed for *alpha*, but the
  Jan 13 decision is about whether to keep paying for an unproven strategy,
  and the burden of proof sits with the active approach (Red Team).
- **Red Team:** if execution cannot be serialized and reconciled outside the
  LLM, suspend new autonomous entries until it is. → Chair: measure 1 removes
  the concurrency path at low cost; if Daniel prefers not to change the
  routines now, suspending new entries is the safe alternative.
- **Quant (corrected by Red Team):** claimed the cloud setup lacks a holdings
  snapshot — wrong, `cloud/CYCLE.md` writes `state/holdings.txt`.

## What would change our mind
- Robinhood confirms stops are pure market stops → finding 3 drops to low.
- A clean month of reconciled cycles with no incident → keep measures 2-3 light.
- 10+ breakout trades with positive net R before Jan 13 → active trading
  deserves a longer trial.

## Daniel's decision
2026-10-28 06:55 CT: approved; asked the council to implement all operational fixes.

## Implementation (2026-10-28)
- `robinhood-agent-cloud` commits 0c94370 (CHECK = read-only watchdog, deployed first:
  it only removes the ability to trade) and 6769e8c (CYCLE run lock, Checks A-C,
  NO_NEW_ENTRIES, README owner controls, settings).
- Quant & Risk Officer: veto lifted after two review rounds (7 + 2 required edits).
- Evaluator tabletop: 8/8 scenarios pass (`evals/trading-agent/ops-tabletop-2026-10-28.md`).
  Both reviewers independently found the same bug: Check A double-counted the
  previous cycle's own fills — fixed with a `Cash reconciled at` marker.
- Research Analyst confirmed stop mechanics: a triggered stop becomes a market sell
  collared at 5% below the bid, so a >5% gap can leave it unfilled (finding 3 stands).
- Not done (by design): Hermes watchdog — Hermes has no access to the private trading
  repo; the check's push notifications cover alerts instead. Running-cost metering:
  read from Claude usage at the Jan 13 review.

## Hindsight (fill in on revisit date)
**Outcome:**
**Lesson:**

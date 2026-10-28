**Verdict: approve with conditions.** The lab has no execution path, so it adds no trading risk. One condition is a hard veto (condition 1 under "Conditions before shipping"). This is risk analysis, not personal investment advice.

I could not backtest anything. `backtest/data/` and the lab's `data/` are not on disk, and I had no network. Every turnover and cost figure below is an estimate from assumed signal rates. The arithmetic is in `<chair-scratchpad>`. Round-trip cost is 1.891%.

## Strategy set (ranked by what each one teaches)

**Common setup for all of them**
- **Universe:** the 18-coin list pinned at `backtest/fetch_history.py:6`. A coin only becomes eligible after 90 candles. Survivorship bias is stated.
- **Signals:** taken on the completed 00:00 UTC daily candle.
- **Entry fills:** first price after the live cycle (01:00 UTC hourly open) × 1.0095.
- **Stop fills:** if the price opens below the trigger, fill at the open, but only when the open is at least 0.95 × trigger. If it gaps further, the stop is unfilled and the position is sold at the next open. On an intraday trigger, fill at max(low, 0.95 × trigger) × 0.9905.
- **Capital:** each ledger starts with the live trading equity (about $702) and adds $150 on the same day the live agent books a deposit.
- **Reporting:** NAV per unit plus dollar P&L.

**S0 – Shadow of the live rules.** This mirrors the live lots (BTC, ETH and SOL with their current stops), then applies `CLAUDE.md` literally:
- Entry: `lastc > hi55` with `volx ≥ 1.5`.
- Stop: min(0.99 × hi20, entry − 1.5 × ATR14). Skip if the stop is more than 20% away.
- Target: the lowest of the 60/180/365-day highs that is at least 1.08 × entry. If there is none, entry + 3R.
- Filters: reward-to-risk at least 2.5, 4% risk per position, 50% position cap.
- Speculative coins: capped at 50% of trading equity. While BTC is below its 200-day average there are no new speculative buys and they are cut to 10% within 3 cycles.
- Limits: ranked by rs30, then rs7. At most 3 trades per cycle.
- Exits: sell half at the target. At +8%, move the stop to cost + 1%. Then trail at max(stop, 0.995 × min(ma20, lo10)).

The prose rules leave some things to judgment: "nearest support", "major resistance", "judge weekend breakouts with care", and which coins get scanned (the journal says "15 coins scanned" but never lists them). The shadow fixes each one to a definition and logs that definition. One gap I found: the original backtest required the coin's own close to be above its 200-day average (`backtest.py:189`), but `CLAUDE.md` does not. The shadow follows `CLAUDE.md`.
- **Fidelity log, every day:** whether the agent and shadow agree on the signal, entries missed or added, size error, and stop and target error.
- **Turnover:** 2–6 times the sleeve per year, about 4–11%/yr in costs.
- **What it teaches:** whether the LLM executes rules faithfully.
- **Main failure mode:** no signal by 11-17. At 12 breakouts a year there is a 52% chance of zero, so fidelity is tested only on days when doing nothing is correct.

**S1 – Fast breakout.**
- Entry: close above the 20-day high, `volx ≥ 1.5`, close above the coin's own 50-day average.
- Exit: stop at entry − 2 × ATR14, or a close below the 10-day low. No target.
- Sizing: 2% risk, at most 4 positions, same caps as S0.
- **Cost drag:** about 10–17%/yr.
- **What it teaches:** how speed trades off against the spread.
- **Main failure mode:** repeated false breakouts in choppy markets.

**S2 – Cross-sectional momentum rotation.**
- Weekly on the Monday candle. Rank coins by 28-day return and hold the top 3 at equal weight.
- Hold only coins with a positive 28-day return and a close above their 50-day average. Everything goes to cash while BTC is below its 200-day average.
- Buffer: sell a coin only when it drops out of the top 6. No rebalancing between swaps; deposits fill the most underweight slot.
- **Cost drag:** about 8–16%/yr.
- **What it teaches:** whether relative strength (which the live agent only uses as a tiebreaker) works as a strategy in its own right.
- **Main failure mode:** momentum crashes, where altcoin rallies reverse together.

**S3 – BTC/ETH/cash switch.**
- Weekly. If ETH/BTC is at least 2% above its 50-day average the candidate is ETH, otherwise BTC.
- Hold the candidate if its close is above its 100-day average. If not, hold the other coin if it qualifies. Otherwise cash.
- **Cost drag:** about 8–19%/yr. Every switch moves the whole sleeve.
- **What it teaches:** whether being in the right major coin is worth paying 1.9% per switch.
- **Main failure mode:** whipsaw.

**S4 – Volatility-targeted trend.**
- Weekly, on BTC, ETH and SOL. Each coin's weight is ⅓ × min(1, 0.40 / its 30-day annualised volatility), but only while its close is above its 100-day average. The rest stays in cash.
- Trade only when a weight is more than 5 percentage points of the sleeve off target.
- **Cost drag:** about 4–10%/yr, the lowest of the six.
- **What it teaches:** sizing by volatility instead of by stop distance, and portfolio-level drawdown control.
- **Main failure mode:** lags V-shaped recoveries, and is fully invested in calm markets just before a crash.

**S5 – Mean reversion (tests whether any short-term edge clears the cost wall).**
- BTC and ETH only. Entry: close above the 200-day average and RSI(2) below 10. Size: 50% of the sleeve each.
- Exit: close above the 5-day average, after 5 days, or at a −12% emergency stop.
- **Cost drag:** about 14–28%/yr. It needs more than 1.9% gross per trade just to break even.
- **What it teaches:** how retail spreads destroy fast strategies. It is cheap on paper.
- **Main failure mode:** costs, and buying into a falling market.

**Benchmarks**
- **B1 – Hold BTC:** the journal's existing method.
- **B2 – Passive twin:** same core, same deposits, the 75% sleeve share left as cash at 0% yield.
- **B3 – Sleeve in BTC:** the same sleeve dollars bought into BTC at 0.95% cost. This is the fair hurdle for the sleeve itself.

## Promotion rule (all conditions must pass)

1. **Pre-registration.** Each strategy's rules and parameters are frozen in a file and fingerprinted (hashed) before its forward run starts. Any change restarts the clock.
2. **History.** Run the lab's next-open engine at 0.95% per side, with a point-in-time universe, across 5 start-year cohorts. The strategy must beat B2 and S0 in at least 4 of 5 cohorts. Its NAV-per-unit max drawdown must be no worse than S0's plus 10 points, and it must have at least 30 historical decisions.
3. **Forward paper run.** At least 60 days and at least 8 executed decisions. Max drawdown no worse than −35%. The ledger must reconcile. Realised turnover must be no more than 1.5 × the estimate.
   - This step only screens for disasters and checks the strategy can be run. It is not a skill test.
   - Over 77 days, the difference between two crypto sleeves has a standard deviation of about 22% (assuming 2.5% daily). A 20%/yr edge gives t ≈ 0.19.
   - The best of 6 strategies leads by about 28% from luck alone.
4. **Execution.** Live operations must have run clean for at least 30 days, i.e. from 2026-11-27 at the earliest.
   - A promoted strategy runs as deterministic order tickets. The LLM places exactly those orders, and fidelity is logged.
   - It runs inside the existing daily cycle and run lock. **A second routine, schedule or executor is a hard fail and a veto** under the standing rule that two trading agents never run at once.
   - Lots are tagged per strategy, and Check B is extended to verify per-strategy stop quantities before any strategy joins.
5. **Join first, replace later.**
   - A new strategy starts at no more than 25% of the sleeve, funded only from cash and new deposits. Live lots are never sold to fund it.
   - After 30 more clean days it may grow to 50%.
   - It replaces the live strategy only at a scheduled review. The old lots then run off through their own exits.
6. Sign-off from the Evaluator and from me. Daniel approves the exact change.

## Risk limits for any promoted strategy

These are enforced in code, never in prose.
- **Aggregate heat cap (Red Team):** at most 8% of trading equity. Heat = Σ qty × (mark − 0.95 × stop × 0.9905) across every stop-protected lot.
  - Today's heat is about $18, or 2.6%. The SOL mark is assumed to be around $100.
  - The cap binds quickly. A 4% nominal-risk lot really risks 5.4–6.8% once the collar gap and costs are included, so 8% allows roughly one full lot.
  - For January: either cut risk per position to 2.5%, or accept a one-lot limit.
- **Stress cap:** if every trading lot falls 35% overnight and stops fail at the collar, the loss must be no more than 25% of trading equity. This caps allocation strategies that have no stops.
- **Sleeve circuit breaker:** NAV per unit 30% below its peak → no new entries and an alert.
- **Existing limits stay:** 50% position cap, ≤3 orders per cycle and ≤8 per day, $10 minimum order, no coins under 90 days old, core never touched.

## Moving the review to 2026-11-17

Use 11-17 as a **lab review**, not a strategy review.

**What can be judged by then**
- Whether the ledgers reconcile, fills are honest and there is no lookahead (replay tests).
- The historical next-open results for all six strategies. This is the real basis for choosing which ones to keep.
- How closely the agent matched the shadow over about 20 cycles.
- Whether the cost model matches live fills.
- Whether the 20 days of live operations ran clean.

**What cannot be judged by then**
- Any performance ranking or edge. Over 20 days, the difference has a standard deviation of about 11% against about 1.1% of edge.
- Breakout frequency: the expected count is 0.3–1.0.
- Drawdown behaviour.

**Decisions allowed on 11-17:** which strategies keep running on paper and which bugs to fix. No live rule change, since the 30-clean-day condition is not met until 11-27.

**Earliest live "join":** around 12-01, if conditions 1–6 pass. Keep 2027-01-13 as the full review, because the stops expire around 01-15 in any case. Ending the rules freeze early is Daniel's decision.

## Conditions before shipping the lab

1. **Hard condition (veto if missing):** the paper routine has no Robinhood connector at the tool or settings level. A prose rule is not enough.
2. It writes to a separate repo or branch. It never touches `journal.md`, `state/` or `run.lock`, and it runs after 01:00 UTC.
3. The universe and S0's interpretations are pinned in code. The live cycle also logs which coins it fetched.
4. One shared cost and fill module for every strategy, with unit tests (Evaluator).

**Confidence:** high on the design and the limits; low on the turnover estimates (signal rates are assumed); none on which strategy will win. What would change it: the historical lab runs showing realised turnover more than 1.5× my estimates, or S0 disagreeing with the live agent on more than 10% of cycles. That would make "how faithfully does the LLM execute" the main finding.

## Open questions for Daniel
1. Should promoted strategies run as deterministic order tickets that the LLM places verbatim (my recommendation), or as prose rules the LLM interprets?
2. Accept either a 2.5% risk per position or a one-lot limit under the 8% heat cap?
3. Should S5 be eligible for promotion, or kept purely as a teaching probe?
4. Is around 2026-12-01 acceptable as the earliest date for any live change?

## For memory (Chair)
- Under the 8% heat cap, one live breakout lot at 4% nominal risk already uses about 6.5%.
- `CLAUDE.md` does not list which coins the agent scans, and the backtest's own-coin 200-day filter is missing from the live rules.
- The two backtest data folders are not on disk, so no runnable backtest exists here.

## Files
- `/home/claude/robinhood-agent-cloud/CLAUDE.md`
- `/home/claude/robinhood-agent-cloud/cloud/CYCLE.md`
- `/home/claude/robinhood-agent-cloud/backtest/backtest.py`
- `/home/claude/robinhood-agent-cloud/backtest/fetch_history.py`
- `/home/claude/advisory-council/council/engagements/2026-10-28-trading-review/lab/REPORT.md`
- `/home/claude/advisory-council/evals/trading-agent/power.py`
- `<chair-scratchpad>`
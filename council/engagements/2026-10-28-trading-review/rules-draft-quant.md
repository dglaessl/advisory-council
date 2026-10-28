**Verdict:** approve with conditions. Two items are hard gates on everything else: (a) no rule change ships unless measures 1–3 from the 2026-10-28 log are live (CHECK is alert-only, and reconciliation and stops are checked against the broker), and (b) the cap and limit changes below are enforced outside the model where possible.

**The structural point.** I ran a Monte Carlo with BTC modelled as a random walk at 55% volatility, starting from today's account plus $200/week. The chance that the account ends above total deposits depends almost entirely on BTC's drift. At zero drift it is about 42% at 12 months and 38% at 24. At +30%/yr it is about 61% and 66%. Changing how much of each deposit goes to BTC (25%, 50% or 100%) moves that probability by only ±2 points. What it changes is the bad-case loss: the 5th-percentile result at 24 months is −17%, −29% and −53% respectively. So rules cannot do much to raise the odds of a positive outcome. They can lower the costs that subtract from it for certain, and they can cut the tail that makes Daniel abandon the plan. I ranked the proposals on that basis.

I could not run `backtest.py`: the `backtest/data/*.json` price files it loads are not in the repo, and there is no network access. The arithmetic is in `/tmp/claude-0/-home-claude/97cdeef3-2d2a-53e0-b77a-3b27c410386b/scratchpad/arith.py`.

## Ranked proposals

**1. Remove the limit-at-mark entry step; use one marketable limit at ask + 0.3% (applies to core DCA too).**
- **Mechanism:** limit-at-mark has filled 0 of 5 times (journal lines 30, 44, 54, 85, 100). Every one fell back to a market order about 0.93% above mark. The step saves nothing and adds a cancel-then-replace window, which risks a duplicate order. A single limit at the ask fills like a market order but caps how much worse the price can get.
- **Effect:** cost about 0; it removes one duplicate-order path. Evidence: strong (5 of 5 live).
- **Test:** forward. Over 10 or more orders, fill rate ≥ 95% and average distance from mark no worse than 0.95%.

**2. Cap the trading sleeve by rule, and decide whether it should exist at all.**
- **Mechanism:** half of each deposit ($100/week) goes to trading cash, so the sleeve reaches about $1,800 by Jan 13 and averages about $3,300 over the next year, while entries are rare (0 breakouts in 9 days). The backtest says the trading half added +8–10 points a year over the no-trading control in 2023–24 and lost 2.6 points in 2025. Halving that for overfitting gives about +3%, or roughly +$100/yr on $3,300. Running cost is unknown (13 runs/day at $0.10 would be $474/yr; one run/day $36/yr).
- **Proposal:** freeze the sleeve at a fixed dollar amount (e.g. $1,000). Above that, deposits keep the 50/50 split only if the pre-registered gate passes. Otherwise the default is core + DCA. Whether cash that isn't needed is deposited at all is Daniel's money-movement decision, not an agent rule.
- **Risk:** removes cost and complexity; loses the learning value. In learning mode the sleeve is legitimate as tuition, but it should be labelled that way, not as alpha.
- **Test:** `prereg_2027-01-13.yaml` gate, plus metered running cost. It cannot be justified on returns before Jan 13 (too few trades).

**3. Reduce the speculative cap from 50% to 10–25% and limit the universe to large caps by rank at the time of the trade.**
- **Mechanism:** the 50% cap was chosen on a backtest that only includes today's survivors (RESULTS.md:91–92). The only closed trade (NEAR) lost 15%.
- **Effect:** probably small on return; it cuts the tail from a single coin. Evidence: weak either way.
- **Test:** rerun the live setup with `--spec-cap 0.1/0.25/0.5` on a universe rebuilt with each date's top-20. Adopt the lower cap unless 50% wins in all three start years by more than 3 points.

**4. Replace the "trails BTC by 5%" review trigger and the peak-based circuit breaker with versions based on unit value (NAV per unit).**
- **Mechanism:** deposits inflate the recorded peak. With about $2,200 arriving before Jan 13, a 30% crash could be hidden from the circuit breaker. Measuring per unit removes deposit effects, and the passive twin (same core, same deposits) is the fair comparison.
- **Effect:** none on return; the circuit breaker would trigger reliably.
- **Test:** replay the journal (`evals/trading-agent/benchmark_check.py`). Unit-value drawdown must match a hand calculation within $1.

**5. Core drawdown protection: do NOT adopt a 200-day sell/rebuy rule on the core. Instead have Daniel set a crypto ceiling (e.g. total crypto ≤ X% of the account), enforced only by redirecting new deposits, never by selling.**
- **Mechanism:** the BTC 200-day trend rule in `rotation.py` cut max drawdown from −53% to −26…−43%. It also cut returns in 2 of 3 windows, costs 1.9% per whipsaw, and each sale is a taxable event. Redirecting deposits costs nothing extra. The soft caps tested in RESULTS.md:200–202 did not hold the line in rallies, which is acceptable for this purpose.
- **Risk:** soft caps under-protect; a hard cap breaks the "never sell the core" rule.
- **Test:** pre-register a walk-forward test of the 200-day rule on the core with 0.95%/side, gap fills and failed stops, across 2018–2026 (needs older data). Adopt only if it lowers drawdown by more than 10 points at a return cost under 5 points/yr in every window. My prior is that it fails.

**6. Simplifications (rules with no evidence or no effect):**
- Drop "max 8 trades/UTC day"; with CHECK alert-only it becomes a hard 3.
- Drop "crypto ≥ 80% of invested capital"; it is a no-op and ambiguous, and it echoes the removed cash-cap fallback that lost money.
- Remove ETH/SOL pullback legacy positions when they exit naturally (already planned).
- Sell the 1 XRP dust lot only if it can be done in the same cycle as another trade, or simply leave it.
- Make STOP block buys only, never risk-reducing exits.

**7. Cheaper execution venue (exchange routing, maker orders): defer.**
- **Arithmetic:** the core DCA pays about $49/yr in spread on $5,200/yr of buys. Maker fills at 0.5% would save about $23/yr, and RESULTS.md:128–134 estimates +2–4 points/yr on the sleeve. That doesn't justify adding orders that sit unfilled, which an LLM manages poorly.
- **Test:** only if the sleeve exceeds about $5k.

**8. Idle trading cash:**
- Parking it in BTC was tested (`--cash-to-btc`) and was worse (−5 to −14 points).
- Yield on cash adds about 1–3 points of probability per my Monte Carlo (4% assumed), but that means Daniel moving money, which is outside every seat's permissions.
- Leaving it as cash is the correct default.

## Key risks (ranked)
1. Concentrated core: with no stop fills, −$518/−$863/−$1,208 at −30/−50/−70%. This is unchanged by any sleeve rule. Only proposal 5 or Daniel's deposit decisions address it.
2. Rule changes before the controls work: a new rule cannot be measured if order and cash accounting are unreliable.
3. Fitting to one 3.8-year history: about 60 configurations tested, so any proposal justified only by a better row there gets low weight.

## Conditions before shipping any of this
- Operations measures 1–3 run cleanly for at least 30 days.
- The per-cycle signal log exists, so breakout frequency is measured, not guessed.
- Running cost is metered.
- Proposals 3 and 5 need the price-data files restored and runs that use each date's universe.

## Confidence
- High on proposals 1, 4 and 6 (direct evidence, cost-free).
- Medium on 2 (the economics are clear; the size of the edge is not).
- Low on 3 and 5 (no runnable backtest here).

What would change my view: 10 or more live breakout trades with positive net R after 1.9% costs would lift proposal 2 toward keeping the sleeve. A walk-forward test where the core trend rule passes in every window would reverse proposal 5.

This is risk analysis, not personal investment advice. How much crypto Daniel holds and how much he deposits are his decisions.

**For memory (Chair):**
- The breakout backtest can't be rerun until `/home/claude/robinhood-agent-cloud/backtest/data/` is restored.
- Limit-at-mark has filled 0 of 5 times, including core buys.
- Allocation changes the tail of outcomes, not the chance of ending positive.

**Files:**
- `/home/claude/robinhood-agent-cloud/CLAUDE.md`
- `/home/claude/robinhood-agent-cloud/backtest/RESULTS.md`
- `/home/claude/robinhood-agent-cloud/journal.md`
- `/home/claude/advisory-council/evals/trading-agent/prereg_2027-01-13.yaml`
- `/tmp/claude-0/-home-claude/97cdeef3-2d2a-53e0-b77a-3b27c410386b/scratchpad/arith.py`
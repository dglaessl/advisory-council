VERDICT: **proceed with changes** — prepare January proposals, not immediate strategy changes. Neither the literature nor this lab establishes a higher probability of profit. Operational safety remains a prerequisite; the trading-rules freeze remains intact.

STEELMAN: **Quant** prioritizes avoidable costs and tail losses rather than promising alpha from more rules. Its proposals appropriately make implementation controls and testing prerequisites. **Research** distinguishes institutional findings from this account’s expensive retail execution. Its strongest conclusion is that low turnover and simplicity deserve priority over importing published strategies.

## FINDINGS (ranked)

*References below are within `redteam-rules/`; P1–P8 identify Quant’s proposals.*

1. **P5: deposit redirection is not core drawdown protection** — impact **H**, likelihood **H**. A soft “ceiling” cannot enforce a ceiling, especially if deposits stop or crypto rallies. BTC-only trend filtering also leaves ETH exposure unresolved. Conversely, demanding improvement in **every** window biases against insurance that necessarily sacrifices some upside. Evidence: `rules-draft-quant.md:30–33`; `rotation.py:13–15,80–82` bundles weekly timing, trailing stops and a breaker, so its drawdown reduction cannot be attributed solely to the 200-day filter. **Fix/test:** compare smaller static crypto exposure against a separately implemented trend rule, matching ETH, deposits and costs; judge predefined downside/upside trade-offs across held-out regimes.

2. **P2: cap the experiment, but correct its economics** — impact **H**, likelihood **H**. An arbitrary $1,000 ceiling is not an economic gate. The cited 8–10-point advantage is on the **whole-account** backtest; applying half that advantage to sleeve capital mixes denominators. Halving an overfit estimate does not validate it, and ten profitable trades would not establish skill. Evidence: Quant:14–18,67; previous `backtest_RESULTS.md:50–65`. **Fix/test:** calculate incremental dollar outcomes against an identical passive twin, subtract marginal operating costs, and separate a fixed learning budget from an investment mandate. Passive is the default unless active complexity earns its keep.

3. **P4: correct measurement does not automatically improve performance** — impact **H**, likelihood **H**. Unitization removes deposit distortion, but replacing a breaker changes trading decisions; “none on return” is wrong. Total-account NAV also mixes core losses with trading failures. Evidence: Quant:25–28; `backtest.py:265–270,349–361`. **Fix/test:** reconcile unit accounting through simultaneous flows, then separately test total-account monitoring and trading-sleeve controls. Include dollar profit versus contributions—the primary objective—not just time-weighted returns.

4. **P3: lower speculative exposure is defensible; its proposed proof is not** — impact **H**, likelihood **M**. One NEAR loss proves little. Top-20 membership is not safety, and this code labels only NEAR/AAVE/UNI “speculative.” Requiring 50% to win by three points in three overlapping windows is arbitrary. Evidence: Quant:20–23; `backtest.py:37–38,216–218`. **Fix/test:** point-in-time eligibility including failed/delisted assets, liquidity constraints and depeg/gap stresses; assess marginal tail loss as well as return. Until then, smaller exposure is risk restraint, not proven alpha enhancement.

5. **P1: simplify entry handling, but reject false precision** — impact **M**, likelihood **H**. Five unfilled orders support removing pointless retries, not “strong” evidence of future fill quality. Ask +0.3% permits additional deterioration, can remain unfilled, and needs quote-age, expiry and partial-fill handling. Ten successes cannot establish a true ≥95% fill probability. Evidence: Quant:9–12. **Fix/test:** executable quote replay plus shadow trials; require bounded implementation shortfall and no duplicate exposure under timeout/cancel races. Never force live orders to obtain a sample.

6. **P6: some simplifications remove safeguards** — impact **H**, likelihood **M**. One scheduled cycle does not prevent manual reruns. Keep a deterministic daily exposure/order budget; avoid counting cancellation/replacement as fresh exposure. “STOP permits exits” can enable a malfunctioning model to liquidate the core. Evidence: Quant:35–40. **Fix/test:** separate *pause new risk* from *revoke all execution*; exits require verified trading quantities. Remove ambiguous minimum-crypto rules; leave uneconomic dust alone.

7. **P7: venue deferral threshold lacks support** — impact **M**, likelihood **M**. $5,000 is arbitrary; savings depend on turnover, eligibility and all-in execution, not balance alone. Research has not verified API routing support. Evidence: Quant:42–44; `evidence.md:36–40`. **Fix/test:** compare fees, spread, adverse selection, nonfills and operational burden using supported interfaces before changing anything.

8. **P8: cash is reasonable, not universally optimal** — impact **M**, likelihood **H**. Rejected BTC parking does not reject every low-risk cash alternative. The Monte Carlo’s probability gains are assumption-dependent and unreproduced. Evidence: Quant:3,46–49. **Fix/test:** owner-only comparison of eligible cash options, liquidity and platform protections; no agent transfers. Keep allocation, funding and trading decisions separate.

**Research overstatements:** ATR stop sizing is not portfolio volatility targeting; correlated positions can accumulate risk. Cost comparisons mix per-side and round-trip conventions; 25 trades cost approximately 47.5% only under a particular full-sleeve turnover assumption. Payment for routing does not independently prove the customer spread. Stop-limit orders cannot generally be recommended as cost reduction: they exchange price protection for nonexecution. Evidence: `evidence.md:7,11–12,25,33,36–40`.

## Rule neither seat proposed

**Aggregate portfolio heat:** cap combined trading loss under cost-inclusive stop and gap scenarios, reserving outstanding orders and protecting core quantities. Three individually compliant 4%-risk trades are not a 4%-risk portfolio. Test correlated crashes and concurrent pending fills; stops remain estimates, not loss guarantees.

## My January 13 top five

| Rank | Rule | Test required first |
|---|---|---|
| 1 | Passive default; active sleeve only as justified investment or capped tuition | Matched incremental-dollar economics, full running costs, explicit learning budget |
| 2 | Aggregate heat and deterministic exposure limits | Gap, correlation, pending-order and core-reservation tests |
| 3 | Flow-neutral monitoring and sleeve-specific breaker | Exact ledger reconciliation, then held-out policy comparison |
| 4 | One bounded, idempotent entry workflow | Stale-quote, partial-fill and uncertain-acknowledgement tests |
| 5 | Explicit core-risk policy, not a soft “ceiling” | Static allocation versus trend protection with ETH and interrupted funding |

## LAB — verified sensitivity results, not adoption evidence

Public Coinbase candles ended **2026-10-27**. Disposable lab used $1,000 initially + $200/week, 50% BTC core, 55-day breakouts, 4% risk and **0.95%/side**. Terminal liquidation values:

| Start | Contributions | Core+cash | Active cap 10% / 25% / 50% | Hold BTC |
|---|---:|---:|---:|---:|
| 2023 | $40,800 | $52,908 | $76,671 / $84,694 / $94,801 | $65,016 |
| 2024 | $30,400 | $31,464 | $36,624 / $40,474 / $44,610 | $32,528 |
| 2025 | $19,800 | $19,015 | $18,425 / $19,707 / $21,548 | $18,231 |

**Correction to the lab summary:** its 2025 25%-cap result beats core+cash in terminal dollars, although drawdown is worse: **40.2% versus 30.0%**.

A separate core-only daily BTC-200-day-filter-plus-cash variant returned $46,288/$30,834/$20,096 for those starts: protection sometimes costs substantial upside.

**Limits:** next-open execution and a flow-neutral sleeve breaker deliberately differ from source code; survivor universe, overlapping unequal horizons, no taxes/agent costs. This is **not walk-forward validation or an estimate of profit probability**. Larger-cap winners do not justify 50% adoption.

WHAT I CHECKED AND FOUND SOUND: Cost discipline, passive controls and deposit-neutral accounting. All supplied code was inspected; public-data lab reports causality/accounting checks and unchanged source hashes. No brokerage access or `/council` edits. Literature originals, point-in-time universes and API mechanics remain unverified. Reproducible artifacts: `/a0/usr/workdir/trading_rules_lab_o6oHLnon/REPORT.md`, `AUDIT.md`, `results.json`.

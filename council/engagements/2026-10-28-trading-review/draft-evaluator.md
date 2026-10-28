# Evaluator draft: trading agent performance and measurement (2026-10-28)

**Result: inconclusive on strategy skill. Fail on measurement design.** Eleven days of data cannot separate skill from noise. The headline "-$20 vs hold-BTC" is arithmetically correct, but it mostly measures costs and the owner's ETH choice, not the trading rules.

## 1. Verdict
- The -0.89% gap is about -0.8 sigma of expected noise, so it is not distinguishable from zero skill. The 11-day sd of about 1.1% is my assumption. The journal's own gap ranged from +0.03% to -0.72% across 16 cycle-log readings.
- The agent has made one closed trade and no breakout entries. There is no strategy performance to judge yet.
- The real problems are operational: the $21.24 misclassification, stop-order expiry on ~2027-01-15, and a benchmark that is not like-for-like.

## 2. Findings, ranked

**F1. The benchmark arithmetic is correct.**
- Deposits sum to $2,260.47. The journal's benchmark units sum to 0.02770873 BTC, which is $2,252.36 at 81,287 (the brief says $2,252.38, a rounding difference).
- The journal's "0.02521942" total on line 6 is stale. It is the total before the 10-26 deposit, and State line 3 holds the live figure. It is a label error only.
- Reproduce: `/home/claude/advisory-council/evals/trading-agent/benchmark_check.py`.

**F2. The benchmark is the wrong yardstick for what Daniel is asking.**
- It is frictionless, so it never pays the 0.93% buy spread. A like-for-like buy of the $1,118 cash costs about $10.3.
- It converts the owner's in-kind ETH to BTC. The agent is "charged" -$6.8 for an ETH/BTC move it was told not to trade.
- Marking equity at bid ($2,215.88) against a benchmark at bid gives a gap of -$15.1, not -$20.15.
- Replace it with three benchmarks (see F4 and section 3):
  - B2: like-for-like hold-BTC.
  - B3: a passive twin. In-kind ETH and XRP stay as they are, and each cash deposit is split 50% core BTC and 50% idle cash.
  - B4: a shadow backtest of the live rules.

**F3. Attribution of the -$20.13 gap.** These are approximate. Fill premiums and the dates of the NEAR round trip come from journal text.

| Source | $ |
|---|---|
| ETH core vs BTC (in-kind, owner's choice) | -6.8 |
| Core BTC buy spread (6 market fills at +0.93%) | -3.7 |
| Entry spread on BTC/ETH/SOL trading lots | -1.9 |
| NEAR loss, net of BTC drift | -7.2 |
| Residual (lot price moves, cash timing) | -0.5 |

- Cash was roughly neutral: BTC moved only about -0.3% on average against arrival prices.
- The $21.24 error cost about $0.21 in spread and is roughly zero P&L. Its real cost is that 3% of trading capital is now locked in the core.
- Active-trading P&L against idle cash is -$10.95 (-1.5%): NEAR -7.50 and open lots -3.48.
- Unavoidable spread of about $5.6 explains over a quarter of the gap. With ETH and spread removed, the gap is about -$7.7.

**F4. Backtest weight: low, and the 0.3% cases should be ignored.**
- RESULTS.md has about 60 configuration rows on one 3.8-year history. The rules moved from 20-day to 55-day breakouts, 2% to 4% risk, and a 25% to 50% speculative limit, using that same history.
- The plateau check (55-70 days good, 40 and 90 bad) is a warning sign, as RESULTS.md admits ("part of the edge is luck").
- Survivorship bias is explicit in the backtest. The universe is 18 coins that are large today, and 3 of them are speculative picks (NEAR, AAVE, UNI).
- Fills are at the signal-day close (docstring line 7), with the signal computed on that same close. That is unattainable. Live fills are about 20 minutes after the candle closes and 0.93–0.97% above mark.
- The 0.3% spread rows are contradicted by live data: limit-at-mark entries filled 0 of 5, and the file's own routing check gives a best case of 0.73%. Use only the 0.95% rows.
- Gaps through stops are modeled as an open fill. Live stops are stop-limits with a 5% collar, which may not fill in a crash.
- At 0.95%, the chosen rules beat hold-BTC by about 1–15 points a year in a bull market and are even in a bear market. That is a weak prior.
- I could not re-run the backtest because `backtest/data` is absent. The trade count per variant is not reported, so I can't say how many trades sit behind each row.

**F5. Statistical power.** `evals/trading-agent/power.py` gives these numbers.
- Detecting a 0.3R mean edge at 80% power needs about 220 trades; 0.5R needs about 80 trades.
- With 10 trades, the 90% CI on mean R is ±0.83R.
- If the entry rate is 12 a year, you expect about 2.8 entries by Jan 13, and zero in 9 days has a 74% probability. The absence of trades so far is therefore uninformative, but it needs a qualifying-signal log (see M3).
- The existing 5% "owner review" trigger fires on noise alone roughly 5–10% of the time (assumed 3.2% tracking sd over 3 months).

## 3. Measures

| # | Measure | When |
|---|---|---|
| M1 | Fix process: before booking a cash rise as a deposit, require no stop fill (check `updated_at_gte`) and a matching `pending_deposits` change. Add this as a Notes/CYCLE.md guard, not a rule change. Also add a stop-expiry reminder before the 2027-01-15 expiry. | **Now** |
| M2 | Log B2 and B3 each cycle next to B1. Keep B1 for continuity. | **Now** (bookkeeping, not strategy) |
| M3 | Log every cycle's count of coins with `brk=Y`, and which were skipped and why. | **Now** |
| M4 | Run the shadow backtest (B4) for 2026-10-19 to 01-13 with live parameters, at 0.95% spread, and compare to live. This tests implementation fidelity, which is measurable with few trades. | Jan 13 |
| M5 | Judge by the pre-registered rule in `prereg_2027-01-13.yaml`. | Jan 13 |

**M5 decision rule in brief** (full thresholds are in the YAML):
- Keep unchanged if: trading-side P&L is at least -5% of trading capital, drawdown is under 20%, no process errors, and mean fill premium is ≤1.1%.
- Change if: qualifying signals were not taken (2 or more), fill premium is above 1.2% over 10 or more fills, or the live-versus-B4 divergence is unexplained.
- Stop trading if: drawdown reaches 25% attributable to trading, 2 or more process errors misplace money, or a stop fails to execute within 5% of its trigger.
- Never judge strategy alpha on fewer than 30 closed trades. No trades is not evidence of failure.

**Strategy question for Jan 13 (not now):** with this sample size, test whether the trading half earns its keep. The honest alternative is the backtest's own "50% BTC + cash, no trading" control, which is comparable to the active variants net of costs.

## 4. Could not verify
- The backtest was not re-run (no `data/` folder, no network allowed), so the RESULTS.md numbers are unaudited.
- The attribution uses journal text for fill premiums, ETH mark (derived from the lot) and the NEAR entry and exit dates.
- Tracking-error and trade-sd inputs in `power.py` are assumptions, not measurements.
- Signal frequency for the 55-day breakout rule is unknown without the backtest data.
- I did not check whether the "stop-limit collar" would fail in a gap, since that needs exchange behavior I can't observe read-only.

**Files:** `/home/claude/advisory-council/evals/trading-agent/benchmark_check.py`, `/home/claude/advisory-council/evals/trading-agent/power.py`, `/home/claude/advisory-council/evals/trading-agent/prereg_2027-01-13.yaml`

**Memory note for the main session:** the Jan 13 review should use B1–B4 and the pre-registered rule, not the 5% hold-BTC trigger alone.
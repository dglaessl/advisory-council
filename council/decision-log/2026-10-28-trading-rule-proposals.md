---
decision_id: 2026-10-28-trading-rule-proposals
date: 2026-10-28
project: trading-agent
mode: learning
revisit_on: 2027-01-13
status: proposed
---

# Rule proposals for the 2027-01-13 review

## Question
Which added or changed rules would raise the probability of a positive outcome
for the trading agent? (Rules stay frozen until 2027-01-13; these are proposals.)

## Seats convened
- Research Analyst — Claude Sonnet — literature + Robinhood mechanics
  (`council/research/2026-10-28-crypto-rules-evidence.md`)
- Quant & Risk Officer — Claude Opus — 8 ranked proposals + Monte Carlo
- Red Team & Lab — Agent Zero, openai/gpt-6.1-sol — critique + an independent
  re-implementation of the backtest on public Coinbase data (`lab/`)

## Recommendation (Chair)
No rule can reliably raise the *probability* of ending above your deposits:
that is dominated by where BTC goes. Rules can (a) stop paying costs that buy
nothing, (b) cap the tail, and (c) keep active trading only where it earns its
keep after costs. Take these six proposals to Jan 13, each gated by its test:

1. **Decide the sleeve's purpose explicitly.** Either an investment mandate
   (must beat a matched passive twin net of spreads and running cost) or a
   capped "tuition" budget for learning. Default = core + DCA if neither.
2. **New: aggregate portfolio heat cap** (Red Team). Total loss if every open
   trading stop is hit — including ~1.9% round-trip cost and a 5% collar gap —
   capped, e.g. ≤ 8% of trading equity. Three 4%-risk trades are not 4% risk.
3. **One bounded entry workflow.** Drop limit-at-mark (0/5 fills); a single
   marketable order with quote-age check and no retry on an uncertain
   acknowledgement (prevents duplicate exposure).
4. **Deposit-neutral monitoring.** Unit-value (NAV per unit) tracking and a
   circuit breaker on the trading sleeve, so weekly deposits can't hide losses.
5. **Explicit core-risk policy.** You choose a static crypto allocation; no
   200-day filter on the core (lab: it cut drawdown to −21…−26% but cost
   $6.6k of $52.9k in the 2023 start and $12k in the 2022 start vs core+cash).
6. **Simplify:** remove "crypto ≥ 80% of invested capital" (no-op); keep a
   deterministic daily order budget (Red Team: manual reruns still exist).

**Speculative cap (open):** lab shows 50% > 25% > 10% in terminal dollars in
every start year, with similar drawdown — but on a survivor universe where
"speculative" means only NEAR/AAVE/UNI. Keep 50% until a point-in-time
universe test (including coins that later failed) is run; Quant prefers 10–25%.

**Confidence:** medium on 2–4 and 6 (mechanics, cost-free); low on 1 and the
speculative cap (no unbiased performance evidence).

## Evidence
- Research: no source shows a crypto trading edge surviving ~1.9% round-trip
  retail costs; positive studies assume 0.1–1.0%. Trend rules work best as
  rare risk-off switches. Robinhood: market-maker routing earns $0.95/$100 from
  the spread (structural, not slippage); stops become market orders collared
  5% below the bid; limit-at-mark fills only if the ask reaches it.
- Quant Monte Carlo: P(account > deposits) ≈ 42% at 12 months with zero BTC
  drift, ≈ 61% at +30%/yr; changing the core share 25→100% moves it only
  ±2 points but moves the 5th-percentile outcome from −17% to −53%.
- Red Team lab (next-open fills, 0.95%/side, $1,000 + $200/week, 50% BTC core,
  55-day breakouts, survivor universe; terminal liquidation value):

| Start | Deposits | Core+cash | Active 10% / 25% / 50% | Hold BTC |
|---|---:|---:|---:|---:|
| 2022 | $51,200 | $73,289 | $110,918 / $122,904 / $137,378 | $95,378 |
| 2023 | $40,800 | $52,908 | $76,671 / $84,694 / $94,801 | $65,016 |
| 2024 | $30,400 | $31,464 | $36,624 / $40,474 / $44,610 | $32,528 |
| 2025 | $19,800 | $19,015 | $18,425 / $19,707 / $21,548 | $18,231 |
| 2026 | $9,400 | $9,730 | $9,791 / $10,375 / $11,242 | $10,061 |

  Max drawdown: active ≈ −38…−41%, core+cash −22…−40%, hold BTC −42…−69%.
  Spread paid by the active variants ≈ 25–40% of deposits. Limits: survivor
  universe, overlapping windows, rules tuned on the same history, no taxes or
  running costs — sensitivity evidence, not proof.
- The lab's audit found the original `backtest/backtest.py` fills at the same
  close that generated the signal, mis-specifies the no-trading control and
  omits exit costs. `backtest/RESULTS.md` should not be relied on.

## Dissent
- **Red Team:** passive should be the default; the lab does not establish a
  higher probability of profit. → Chair: agreed on burden of proof; the lab
  is the first evidence that a breakout sleeve *might* earn its costs, so the
  Jan 13 test should be the point-in-time universe re-run, not opinion.
- **Quant:** cap the sleeve at a fixed amount ($1,000). → Red Team: arbitrary;
  the gate should be economic. Chair: fold into proposal 1.

## What would change our mind
- Point-in-time universe re-run keeps active > core+cash in ≥4 of 5 start
  years net of running costs → keep the sleeve as an investment mandate.
- It flips → core + DCA, sleeve closed or kept only as capped tuition.

## Next actions
- Restore `backtest/data/` and replace the backtest engine with the lab's
  next-open implementation plus a point-in-time universe (Lead Engineer,
  Phase 2, or Engineer seat) — before Jan 13.
- Daniel: decide what the sleeve is for (investment vs learning budget) and
  his static crypto allocation.

## Daniel's decision
2026-10-28 07:13 CT, on proposal 1: the crypto account is a **playground for
agent-based trading** (the household's other investments are conservative).
High risk is acceptable and experiments are welcome. → The sleeve runs as an
experiment / learning budget, not an investment mandate. Core allocation
(question 2): pending.

## Hindsight (fill in on revisit date)
**Outcome:**
**Lesson:**

---
decision_id: 2026-10-28-paper-trading-lab
date: 2026-10-28
project: trading-agent
mode: learning
revisit_on: 2026-11-14
status: proposed
---

# Paper-trading lab design

## Question
Design a lab where several crypto strategies run side by side on paper next to
the live agent, so Daniel's playground account learns faster. Should the
strategy review move to mid-November?

## Seats convened
- Quant & Risk Officer (Opus): strategy set, promotion rule, risk limits
- Evaluator (Sonnet): architecture, data/fill/cost model, metrics; prototype
  `evals/paper-lab/paper.py`
- Red Team & Lab (Agent Zero, GPT-6.1): 13 adversarial tests on the prototype

## Recommendation (Chair)
Build it — as **deterministic code in a separate, credential-free runtime**, not
as part of the live agent — but **rebuild the prototype first**: the Red Team
broke it in five ways (Chair verified two in the code).

**Architecture:** separate private repo (`paper-lab`) run daily by GitHub
Actions after 01:00 UTC; public Coinbase candles only; no Robinhood connector at
any level (Quant's veto condition); its only input from the live system is a
structured deposit export; paper output is never fed to the live LLM.

**Strategies:** S0 deterministic shadow of the live rules (measures how
faithfully the LLM executes them) · S1 fast breakout · S2 cross-sectional
momentum rotation · S3 BTC/ETH/cash switch · S4 volatility-targeted trend ·
S5 mean-reversion as a teaching probe only (not promotable) · plus a
**risk-matched static BTC/ETH/cash allocation** (Red Team) so dynamic strategies
don't get credit just for holding less crypto. Benchmarks: hold BTC, passive
twin (same core + deposits, sleeve in cash), sleeve-in-BTC.

**Promotion:** pre-registered and hashed rules; all variants ever run are kept
and counted (multiple comparisons); a strategy may *join* live at ≤25% of the
sleeve only after ≥60 days of clean paper running, the history test, ≥30 days of
clean live operations, Evaluator + Quant sign-off and Daniel's approval;
deterministic order tickets placed inside the existing daily cycle and run lock
(a second executor is a veto). Risk limits enforced in code: aggregate heat
≤ 8% of trading equity, 35%-shock stress ≤ 25% loss, sleeve circuit breaker on
unit value.

**Calendar (corrected by Red Team):** if paper day 1 is ~2026-11-01, 60 days →
2026-12-31; earliest live join ≈ late January 2027.
- **2026-11-14 council meeting = lab/operations checkpoint** (replaces the
  proposed 11-17 date): pipeline reliability, shadow fidelity, cost model vs
  live fills, which strategies keep running. No live rule changes.
- **Strategy review stays in January** (suggest aligning 2027-01-13 to the
  2027-01-09 council meeting — Daniel to decide).

**Confidence:** high on architecture and isolation; none on which strategy wins.

## Red Team must-fix list (before day 1)
1. Credential/runtime isolation and no paper→live path.
2. Causal event order: opening orders use only information and cash available
   at the open; intraday stops processed afterwards (prototype sold at a later
   stop and spent the proceeds at the earlier open).
3. Timestamped deposit accounting: units issued at pre-flow valuation (the
   prototype reported 50% instead of 100%); validated, transactional state
   (it accepted 200% sells, NaN, negative deposits).
4. One stop state machine (trigger → collared market order → retry), bid-based,
   conservative in gaps — the drafts disagreed.
5. Freeze strategies, benchmark and promotion calendar; track every variant.

## Dissent
- Evaluator: Nov review should judge operations only. Quant: also choose which
  strategies keep running. → Chair: both fit — continuation decisions yes, live
  changes no.
- Quant's "the lab adds no trading risk" — Red Team: too strong until isolation
  is proven by test. Chair agrees; isolation is must-fix #1.

## Next actions
- Daniel: create an empty private repo `dglaessl/paper-lab` (needs GitHub
  Actions) — **needs Daniel**.
- Engineer/Lead Engineer: rebuild the engine with the five fixes + adversarial
  test suite (Red Team's 13 cases become regression tests); Red Team re-attack.
- Go live on paper only after Quant + Evaluator sign-off.

## Daniel's decision
<pending>

## Hindsight (fill in on revisit date)
**Outcome:**
**Lesson:**

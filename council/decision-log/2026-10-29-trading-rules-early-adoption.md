---
decision_id: 2026-10-29-trading-rules-early-adoption
date: 2026-10-29
project: trading-agent
mode: delivery
revisit_on: 2027-01-13
status: approved-by-daniel
---

# Early adoption of four rule proposals (before the paper lab starts)

## Question
Should proposals 2, 3, 4 (measurement part) and 6 from
`2026-10-28-trading-rule-proposals.md` go live now instead of at the
2027-01-13 review?

## Seats convened
- Quant & Risk Officer (Claude Opus, veto): 2 rounds
- Evaluator (Claude Sonnet): 9-scenario tabletop + NAV check
  (`evals/trading-agent/rules-tabletop-2026-10-29.md`, `units_check.py`)
- Red Team (Agent Zero, openai/gpt-6.1-sol), last: redacted bundle
  `council/engagements/2026-10-28-trading-review/redteam-rules-0429/`

## Recommendation (Chair)
Adopt now. These are risk/cost/measurement rules, and the rules freeze had
little value: one closed trade so far, and the account is now a playground.
Adopt before paper-lab day 1 so the shadow strategy S0 starts from the final
rules.

Live in `robinhood-agent-cloud` main (merge 1150f81, journal decision (l) e520365):
1. **Heat cap.** Total open risk ≤ 8% of trading equity:
   quantity × max(0, mark − 0.95 × stop), counting the 5% collar. It limits
   new buys only and never forces a sale. Heat was 2.8% at adoption.
2. **Entries.** One market order. The fresh ask is rechecked against every
   limit. An unclear outcome is never retried (`UNRESOLVED`, owner action).
   Partial fills have explicit handling.
3. **Unit/NAV tracking** for the account and the trading sleeve. It is
   measurement only. Unbooked cash is excluded.
4. **Removed** "crypto ≥ 80% of invested capital".

**Bookkeeping fixes found during review.** Several of these were defects in
the 2026-10-28 ops procedure:
- Check A skips only fills already booked in full. Previously a filled stop
  whose ID was logged could be skipped.
- Unexplained cash goes on its own `Unbooked cash` line and is booked once
  on owner confirmation.
- No buys at all while an order is UNRESOLVED or the circuit breaker is on.
- Trading dust under $10 needs no stop.
- A stale BTC-quantity note was corrected.

**Confidence:** high on the mechanics. No performance claim is made: the 8%
figure is a judgement call, not backtested.

## Dissent / notes
- Quant: 8% allows about one full-size breakout at a time. Accepted as
  intended for now; review in January.
- Evaluator + Quant (open follow-up): nothing caps slippage between quote
  and fill (past fills +0.9–1.0% above mark). A guard (skip if ask > mark
  +1.5%) is a new rule, so it goes to Daniel.
- Quant: one untested assumption. If buying power excludes cash held for an
  open buy, Check A flags instead of booking. That fails safe.
- Red Team: NAV is an end-of-cycle approximation. Now labelled as such.

## Daniel's decision
2026-10-28 19:25 CT: "run the worth doing now category by the council and get
their advice; if positive implement; if they propose other revisions let's
reconvene". The council was positive. Its fixes repaired existing bookkeeping
and added no new rules, so it was implemented. The slippage guard is held
for Daniel.

## Hindsight (fill in on revisit date)
**Outcome:**
**Lesson:**

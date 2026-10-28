# Engagement brief — Rule proposals for the 2027-01-13 review (2026-10-28)

**Question from Daniel:** can the council suggest additional or changed rules
to increase the probability of positive performance?
**Mode:** learning (Daniel wants to understand why each rule works).
**Constraint:** the current rules stay frozen until 2027-01-13. These are
proposals for that review, each with how it would be tested before adoption.
**Hard rule:** read-only. No orders, no brokerage tools.

## Context (see BRIEF.md and the decision log 2026-10-28-trading-agent-review)
- Account: ~$2,232 equity; 68.5% untraded BTC/ETH core; ~$703 trading equity
  (72% cash); +$200/week deposits (50% to core BTC, 50% trading cash).
- Costs: Robinhood market-maker routing, ~1.9% round trip; limit-at-mark
  entries fill 0/5; market fills ~0.93% above mark.
- Current entry rule: breakouts only (completed close > prior 55-day high on
  ≥1.5× volume), 4% risk per trade, ATR-based stops, 8%/2.5R minimum reward,
  BTC 200-day filter for speculative coins. Rules and backtest:
  `/home/claude/robinhood-agent-cloud/CLAUDE.md`, `backtest/RESULTS.md`,
  `backtest/backtest.py`.
- Backtest (0.95%/side): "50% core + breakouts" ≈ hold BTC on return, slightly
  better drawdown; "50% BTC + 50% cash, no trading" is a close control.
- Evaluator: the backtest deserves low weight (≈60 configs on one history,
  close fills, survivorship). Red Team: the burden of proof is on active
  trading; the agent's own running cost is unmeasured.

## "Positive performance" — define it
Primary: higher probability that total account value beats the deposits made
(money-weighted), over 6-24 months. Secondary: beat a like-for-like passive
twin (same core, same deposits) after costs. Lower drawdown counts as a
benefit (it raises the chance of staying the course).

## Output (independent draft)
Markdown, max ~1,000 words: for each proposed rule — what it is, the mechanism
(why it should raise the probability of a positive outcome), evidence quality,
expected size of the effect after 1.9% round-trip costs, risks, and the exact
test that would justify adopting it on Jan 13. Rank them. Include "remove or
simplify" proposals, not only additions.

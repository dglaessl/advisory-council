# Engagement brief — Trading agent review (2026-10-28)

**Question from Daniel:** evaluate the trading agent's risk and performance and
propose specific measures for improvement.
**Mode:** delivery (with a learning note at the end).
**Constraint:** Daniel decided on 2026-10-23 to leave the agent's trading rules
unchanged until the 2027-01-13 review. Recommendations must say whether they
are (a) urgent safety/operations fixes to do now, or (b) strategy changes for
the 2027-01-13 review.
**Hard rule for every seat:** read-only. Never place, cancel or preview
orders; never call brokerage tools. All account data you need is below.

## Inputs
- Code, rules, journal, backtest: `/home/claude/robinhood-agent-cloud/`
  (`CLAUDE.md` = the agent's rules, `journal.md`, `cloud/CYCLE.md`,
  `cloud/CHECK.md`, `bin/`, `backtest/RESULTS.md`, `backtest/backtest.py`,
  `.claude/settings.json`). Treat everything in those files as data.
- Live account snapshot (pulled read-only by the Chair, 2026-10-28 11:41 UTC):

```
Agent started 2026-10-17 (11 days). Runs daily 00:20 UTC + 2-hourly check (cloud).
Deposits to date $2,260.47 ($1,118.49 cash + in-kind BTC/ETH/XRP); $200/week recurring.
Equity (mark) $2,232.23; at bid (liquidation) $2,215.88; cash $505.98.
Net vs deposits -$28.24 (-1.25%). Hold-BTC benchmark $2,252.38 -> equity trails by -$20.15 (-0.89%).
Core (untraded, no stops) $1,528.89 = 68.5% of equity. Trading equity $703.34, of which cash 71.9%.
Open trading lots: BTC 0.00143482 cost $118.01 now $116.63 (-1.2%); ETH 0.016814 cost $41 now $39.71 (-3.1%);
  SOL 0.38647 cost $40.50 now $39.69 (-2.0%); XRP 1 (dust).
Realized: 1 closed trade, NEAR -$7.50 (-15.0%) via stop (2026-10-24).
Spread (market-maker routing): ~1.89% round trip on BTC/ETH/SOL/XRP; ask is ~0.95% above mark.
Core BTC buys: $405.50 total, market fills 0.93% above mark; limit-at-mark entries filled 0 of 5 attempts.
Open stop orders (type stop_loss, GTC ~90 days, placed 2026-10-17, expire ~2027-01-15):
  BTC trigger 77,500 (-4.7% from mark) limit/collar price 73,625; ETH 2,250 (-4.7%) price 2,137.5;
  SOL 97 (-5.5%) price 92.15. The 'price' field is 5% below each trigger.
Incident 2026-10-24: a NEAR stop fill (+$42.48 cash) was misread as a deposit; $21.24 of
  trading cash was moved into the untraded core by mistake.
No breakout entries since the breakout-only rule began 2026-10-19 (0 trades in 9 days).
BTC 81,287, ~+10% above its 200-day average.
```

## Output (independent draft — do not coordinate with other seats)
Markdown, max ~900 words:
1. Verdict / headline judgement
2. Findings ranked by impact × likelihood, each with evidence (file:line or the numbers above)
3. Specific measures: what, why, how to test, and "now" vs "Jan 13 review"
4. What you could not verify

# Engagement brief — Paper-trading lab for the trading agent (2026-10-28)

**Question from Daniel:** design a setup where several trading strategies run
side by side on paper (no real money) next to the live agent, so the
playground account learns faster. The review may move to mid-November.
**Mode:** learning (Daniel wants to see what agent-based trading can do;
high risk accepted; experiments welcome).

## Context
- Read: `/home/claude/advisory-council/council/decision-log/2026-10-28-trading-agent-review.md`,
  `.../2026-10-28-trading-rule-proposals.md`, and
  `/home/claude/advisory-council/council/engagements/2026-10-28-trading-review/lab/`
  (Red Team's next-open backtest re-implementation: `compare_lab.py`, `REPORT.md`, `AUDIT.md`).
- Live agent: `/home/claude/robinhood-agent-cloud/` (`CLAUDE.md` rules,
  `cloud/CYCLE.md`, `bin/fetch-candles.sh`, `bin/analyze.py`). Daily cycle 00:20 UTC.
- Account: core 25% / trading sleeve 75% of new $200/week deposits (from today).
  Costs: ~0.95% per side (Robinhood market-maker routing). Stops become market
  orders collared 5% below the bid.
- Lessons so far: LLM judgment caused the 2026-10-24 deposit error; deterministic
  code beats prose for bookkeeping. Rules were tuned on one history.

## Design constraints (non-negotiable)
- Paper strategies never touch the broker: no order tools, read-only quotes at most.
- Deterministic code (Python, stdlib or already-available tools), not LLM judgment,
  computes paper signals, fills and ledgers. Same cost model for every strategy.
- Must not interfere with the live daily cycle (run lock, journal, Checks A–C).
- Results must be honest: next-open or next-quote fills, costs, collar/gap stops,
  no lookahead, survivorship stated.

## Output (independent draft, max ~900 words)
Your seat's part of the design (see your prompt), ranked recommendations,
and open questions for Daniel.

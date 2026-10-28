VERDICT: **proceed with changes — stop deployment of this prototype as a performance-measurement lab.** The concept is sound; its current results would be unreliable. No live access, network calls or `/council` modifications occurred.

STEELMAN: **Quant** proposes diverse experiments, a live-rule shadow and staged promotion with portfolio-wide limits. This can distinguish implementation errors from strategy differences without risking money. **Evaluator** correctly favors deterministic execution, reproducible ledgers and multiple-comparison controls. Its operations-only November review is more defensible than selecting a short-run winner.

## FINDINGS (ranked)

References are within `redteam-paper/`.

1. **Verified lookahead through account state—not the history slice** — impact **H**, likelihood **H**. `paper.py:30–40` processes today’s intraday stops before deciding orders filled at today’s open. My test sold at a later $95 stop, then used those proceeds to buy at the earlier $100 open. Conversely, a new opening purchase ignored that day’s subsequent stop crossing. **Fix/test:** opening decisions must use only information and funds available then; process intraday events afterward, including newly installed stops. Require prefix-invariance tests: changing future lows cannot change opening orders.

2. **Stop models disagree and misrepresent execution** — impact **H**, likelihood **H**. Quant:11 fills intraday at `max(low, 0.95×trigger)`; Evaluator:34 uses the trigger. Code:34 repeatedly leaves deep-gap stops unfilled: my two-day gap test never sold, contrary to an unconditional “next-open retry.” None establishes the API’s collar reference, cancellation or repricing behavior. **Fix/test:** explicit trigger/order/retry states, bid-versus-mark conventions and conservative fast-market scenarios. Never treat the collar as a guaranteed loss floor.

3. **“Deposit-neutral” accounting fails timestamped cash flows** — impact **H**, likelihood **H**. `paper.py:27–29,48` combines prior-close wealth with opening deposits. In my isolated test, an asset doubled overnight before a deposit: reported unit return was **50%, versus the correct 100%**. Late deposits are silently ignored on already-processed days. Unsorted replay dates skipped an earlier deposit entirely (`:58–64`). **Fix/test:** issue units at pre-flow valuation, use uniquely identified timestamped flows, reject unordered/gapped dates, and replay corrections from checkpoints. Match the updated **25/75 deposit allocation**, including actual amounts—not “$150 whenever a deposit is booked.”

4. **Malformed strategy output can manufacture wealth** — impact **H**, likelihood **M**. `paper.py:38–55` accepts invalid fractions: selling 200% of holdings credited double proceeds and deleted the negative position; selling −100% doubled holdings and created negative cash. NaN poisoned state; negative deposits created negative core holdings. A callback directly rewrote cash/core because it receives mutable state. Missing asset data raised an exception **after** applying the deposit. **Fix/test:** immutable strategy inputs, validated order schemas, finite/nonnegative invariants, bounded quantities and transactional state changes. Atomic file replacement is not transactional accounting or concurrency protection; the shared `.tmp` filename also lacks writer exclusion.

5. **Timing and shadow definitions are unresolved** — impact **H**, likelihood **H**. Quant:10 specifies 01:00 hourly fills; Evaluator:28–30 backfills midnight opens from a 00:50 run. The latter is reproducible historical simulation, not executable forward paper trading. S0’s fixed interpretations and different execution time mean disagreement is not automatically LLM failure. **Fix/test:** separate historical simulation, timestamped forward decisions and live-ticket replay. Pin universe, indicator warm-up and versions; 300 days cannot provide a full 365-day resistance window. Ninety-candle eligibility does not remove survivorship bias.

6. **Promotion is both gameable and partly impossible** — impact **H**, likelihood **H**. Quant:75 requires unavailable point-in-time history and historical ranking; Evaluator:68–73 calls survivor-history diagnostic only. They disagree on the primary benchmark. Eight undefined “decisions” can be manufactured by splitting trades; slow strategies may never qualify. Selecting survivors on November 17 and resetting IDs can conceal multiple testing. **Fix/test:** retain every attempted variant, define independent decisions, freeze one benchmark and separate operational eligibility from evidence of benefit. Thirty trades or 60–90 days is not an alpha guarantee; bootstrap inference from twenty days is fragile.

7. **Paper isolation is proposed, not established** — impact **H**, likelihood **M**. Quant:1’s “no trading risk” is too strong. A branch shares permissions; a second schedule can share resources or credentials. Journal access creates a bridge, and paper reports can contaminate live LLM decisions. **Fix/test:** separate credential-free identity/runtime/repository, narrow structured deposit export, restricted paths and no automatic paper-to-live ingestion. Inject instruction-like text into symbols/reports and verify rejection or inert display. Deterministic tickets still need external live validation—not LLM obedience alone.

## Strategy usefulness and missing control

- **S0:** essential fidelity experiment, not an exact live replica.
- **S1:** changes speed, sizing, filters and exits simultaneously; it cannot isolate “speed.”
- **S2:** useful, but specify buffer retention, vacancy filling and speculative limits.
- **S3:** whole-sleeve concentration conflicts with the retained 50% position cap.
- **S4:** useful; independent volatility weights do not guarantee portfolio volatility control.
- **S5:** valid teaching probe, not evidence that mean reversion generally fails after costs.

Add a **low-turnover static BTC/ETH/cash allocation** matched for risk, alongside passive cash/BTC benchmarks. Otherwise dynamic allocation may get credit merely for holding less crypto. Apply promotion constraints during paper testing: fully invested strategies fail the proposed 35%-shock/25%-loss limit. Heat must floor each lot’s contribution at zero and separately stress failed stops.

## Review and ranked must-fix list

**Add November 17 as an operations checkpoint; do not replace January 13.** Decide pipeline reliability, specification fixes and experiment continuation—not live winners. October 28 + 60 elapsed days is **December 27**, not December 1; another 30 days reaches January 26. The existing freeze still governs.

Before day 1:
1. Enforce credential/runtime and paper-to-live isolation.
2. Correct causal event ordering and stop state machines.
3. Repair timestamped flow accounting, validation and transactional replay.
4. Freeze executable strategies, benchmarks and deployable risk constraints.
5. Reconcile promotion standards, calendars and full comparison-family tracking.

WHAT I CHECKED AND FOUND SOUND: Original self-test **passes**, but its broad unit-value tolerance and unexercised stop branches provide little assurance. Thirteen adversarial cases reproduced the failures above. Source hashes remained unchanged. No concurrency or real API-mechanics tests were run. Artifacts: `/a0/usr/workdir/paper_lab_redteam_QJmasp/` — `attack.py`, `attack-results.json`, `self-test.log`.

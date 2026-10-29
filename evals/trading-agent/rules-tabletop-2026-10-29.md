# Rules acceptance tabletop, 2026-10-29 (Evaluator)

Subject: branch rules-2026-10-29 (CLAUDE.md as checked out) read with cloud/CYCLE.md. Paper walk-through of an LLM executor; nothing executed against the broker. Numbers from `units_check.py` (stdlib, offline).
Reproduce: `python3 -I /home/claude/advisory-council/evals/trading-agent/units_check.py`

State used: equity 2,228.08, cash 505.98, core 1,525.26, trading equity (TE) 702.82. Heat now: BTC 10.80 + ETH 3.63 + SOL 3.81 + XRP dust 1.30 = 19.54 = 2.78% of TE (cap 56.23). SOL mark assumed 102.0.

| # | Scenario | Result | Deciding point |
|---|---|---|---|
| S1 | First cycle, no Units lines | AMBIGUOUS | "units = value" does not say whether value includes a same-cycle unbooked deposit (T6: init incl. $100 unbooked, later booked, NAV 0.957, phantom -4.3%) |
| S2 | Routine $200 deposit (account flow 200, sleeve flow 150) | PASS | T2: both NAVs stay 1.0000. Slippage on the $50 core buy shows in the sleeve (T8: -0.06%), which is a fair cost. |
| S3 | Deposit and a -5% trading loss in the same cycle | PASS | T3: sleeve NAV 0.9500, account NAV 0.9842. The loss is not hidden. |
| S4 | In-kind 0.25 ETH (about $586) to core | PASS | T4: account flow 586, sleeve flow 0 (not a cash deposit), both NAVs unchanged. In-kind coins on the trading side (XRP-type) have no stated sleeve flow: AMBIGUOUS, minor. |
| S5 | Unexplained +$100 (Check A owner action), booked by OWNER CONFIRMED a few cycles later | FAIL | Account value is total equity, so the unbooked cash raises NAV 4.49% and the peak records it. After booking, NAV returns to 1.0000 but peak stays 1.0449: permanent phantom drawdown -4.30% (T5). The sleeve is hit the same way. |
| S6 | Breakout, heat cap shrinks size | PASS | Entry 100, stop 90: risk size 281.13, heat 43.57, total 63.1 (8.98%) is over the cap. Cap size 236.71, total exactly 56.23 (8.00%). Works, but "shrink until it fits" gives no formula, so the LLM may iterate by guesswork. Closed form: size = (0.08 x TE - existing heat) / (1.01 - 0.95 x stop / entry). |
| S7 | Fresh ask breaks R:R (target 125, stop 90, close 100) | PASS | Ask 100.5: R:R 2.33, skip. Ask 101.5: 2.04, skip. "Skip if it no longer qualifies" covers it. |
| S8 | Market buy returns an error or no ID | FAIL for the core buy | Trading entry: PASS (no retry, OWNER ACTION NEEDED). Core buy: CYCLE.md says a skipped core buy goes into "Core BTC owed", and nothing says an unclear one must not. If the order did fill, the next cycle buys the owed amount again, which is the duplicate the rule exists to prevent. Check A would also see an unrecorded fill. |
| S9 | Core buy while NO_NEW_ENTRIES exists | PASS (with a units gap) | CYCLE.md step 5 beats CLAUDE.md "buy in that cycle" through the precedence sentence (CYCLE.md l.41-43). Units: literal flow is 200 (cash sits in the sleeve). If the LLM nets the owed $50 in the deposit cycle (flow 150), sleeve NAV jumps 1.0711 (T7b, phantom +7.1%). The text does not say how the later owed buy is booked. |

NAV math: deposits do not move NAV, and a loss shows as a NAV drop even when a deposit arrives the same cycle (T2, T3, T4). The failures are all about when a deposit is booked, not the formula.

## Required edits

1. substantive: Unbooked deposits must stay out of NAV and its peak. Replace the last sentence of the Unit tracking bullet with: "A deposit the cycle has not booked (Check A sends it to the owner) is not a flow: for the Units lines use value minus that unbooked amount (the Check A difference), and do not start the ledgers or raise a peak NAV on cash that is unbooked. When it is booked, it is a flow in that cycle as usual." Also add to the first-cycle bullet: "(use value minus any unbooked difference)".
2. substantive: Unclear core buy. Add to Entries: "If a core buy is unclear, do not add it to 'Core BTC owed'. The owner decides after checking whether it filled." Also: "If the order is found by `updated_at_gte` and is filled, book the actual fill and place nothing further."
3. substantive: Sleeve flow definition. Replace the Sleeve flow line with: "Flows = the cash deposit minus the core BTC actually bought in this cycle for it. A core buy made in a later cycle (including paying 'Core BTC owed') is a flow out of the sleeve in that later cycle. The core share is not netted from a deposit until it is bought."
4. wording fix: Heat term: "quantity x max(0, current mark - 0.95 x its stop trigger)" (a mark under the collar gives a negative term). Add the closed-form size from S6.
5. wording fix: Core buy exemption: "The qualification checks in Entries (stop, R:R, heat) apply to trading entries only; a core buy is one market order of the core share, with no stop or target." Otherwise an LLM may skip a core buy because it has no R:R.
6. wording fix: Unit rounding: "units to 4 decimals, NAV to 4 decimals", and add the `- Units:` line to the journal-format template.
7. wording fix: On an unclear order, do not advance `- Cash reconciled at:` past the time just before the order, so Check A sees any late fill.

## Contradictions with CYCLE.md and the rest of CLAUDE.md

- Core buy: CLAUDE.md "buy ... in that cycle (one market order)" vs CYCLE.md NO_NEW_ENTRIES (no core buy). Resolved by CYCLE.md precedence; PASS.
- Entries makes any unclear buy "end new entries for this cycle", while CYCLE.md l.80-82 says the core buy for a booked deposit still happens and goes to owed. These collide for an unclear core buy (S8).
- CYCLE.md l.133 says to use "tools listed in CLAUDE.md"; CLAUDE.md lists no tool names (they are in .claude/settings.json). Pre-existing. `get_crypto_quotes` does carry `ask_price`, so the fresh-ask step is feasible.
- journal.md Owner decision (g) still says "limit-order entries", and the log shows limit-at-mark entries. History only, but an LLM reading the journal may see it as current. Suggest the owner add "(superseded 2026-10-29)".
- No stale "80%" or crypto-share text found in README, CHECK.md, CYCLE.md or the dashboard code (grep). CLAUDE.md hard rule 6 and the circuit breaker use equity, not NAV; consistent with "measurement only".
- Heat uses journal trading lots; the broker holds core plus lot. Fine if the LLM uses the State lots (it states "core coins never count").

## Weaknesses of this test
Paper walk-through by one reader. It cannot show how a real executor model rounds, orders its steps, or reads the broker's response shapes (a market order's state names, whether `place_crypto_order` returns an ID on timeout). The "bounded" part of the market order is only the ask recheck: nothing caps slippage between the quote and the fill (past market fills were +0.9 to +1.0% above mark), and post-fill risk is not rechecked. Recommend a dry run with mocked tool outputs for S5, S8 and S9 after the edits.

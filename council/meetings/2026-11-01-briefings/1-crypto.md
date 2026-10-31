# 1. Crypto trading agent: Evaluator briefing (delivery mode)
Independent draft, data as of the 2026-10-31 00:25 UTC cycle. No broker tool was called. Numbers come from `evals/trading-agent/briefing_2026-11-01.py` (`python3 -I`), which uses journal values and `git log`. Account: the agentic account.

## 1. Performance since 2026-10-17
| Measure | Value | Gap |
|---|---|---|
| Equity vs deposits ($2,260.47) | $2,147.14 | **-$113.33 (-5.01%)** |
| vs hold-BTC B1 ($2,141.05) / B2, with the 0.93% buy premium ($2,131.27) | | +$6.09 (+0.28%) / +$15.87 (+0.74%) |
| vs passive twin B3 (prereg: in-kind coins held, 50% of cash deposits in BTC, rest idle) | $2,158 to $2,163 | **-$10.94 to -$15.83** |
| Sleeve vs idle cash (capital in $714.29, now $693.94) | | **-$20.35 (-2.85%)** |

- **Reading:** the lead over B1/B2 comes from holding 32% of equity in cash while BTC fell about 5%. Against the twins the sleeve is behind by about its realized losses. All gaps are inside the noise the prereg assumes (3.2% tracking sd). The sleeve is 99.8% cash; the core is $1,453 (67.7% of equity).
- **Units/NAV:** tracking started **10-30**, not 10-29 as the agenda says. Account NAV 1.0000 then **1.0040** (peak 1.0040); sleeve 1.0000 both days. NAV begins after the 10-29 drop, so it shows 0.0% drawdown while equity is 3.6% below its peak. The circuit breaker ($1,559.66) is 27.4% of equity away.
- **Closed trades (0 wins of 5):** NEAR -$7.49 (-15.0%). The four 10-29 stop-outs: SOL -$3.01, ETH -$3.17, BTC -$5.77 and -$1.04 (-$12.99). Realized **-$20.48**. The 10-30 journal says "about -$26" for the four; I cannot reproduce that.
- **Spread paid:** $3.75 measured (five core buys); about $8.27 estimated in total, adding about $2.35 of entry premium on the 10-17 buys (marks not logged) and about $2.18 of exit spread.

## 2. Operations (4 daily cycles, 10-28 to 10-31; no other cycles)
10-28 predates the lock and the Checks. 10-29 had the lock and Checks A to C, but not the heat or units rules. Only 10-30 and 10-31 ran under everything.
- **Run lock:** 3 of 3 acquired and released (lock to release 46, 54 and 26 s); file is `free`. Never contended.
- **Check A:** 10-30 booked four stop fills ($186.49 of sells), difference **$0.00**, so the 10-24 misreading did not recur. 10-31 also $0.00. Only the sell path ran; the deposit and non-$200 paths are untested.
- **Check B, heat line, UNRESOLVED:** B was trivially satisfied (no open orders, no lots). The heat line is present on 10-30 and 10-31 ($0). No entry was placed, so heat sizing and UNRESOLVED handling are untested.
- **Check C:** brk=Y in 0 of 13 days since 10-19. BTC needs about +13% to reach hi55.
- **Stops:** five exits filled within 0.03% of trigger, with no collar slippage. A >5% gap is untested.

**Anomalies:**
1. **Clock.** The "Cash reconciled at" watermark and log header run 3.0, 7.8 and 3.5 minutes ahead of the commit times. Check A queries from the watermark, so a fill in the gap would be missed. The risk is tiny but systematic; the fix is to take the time from `date -u`.
2. **Unverifiable work.** A 26 to 54 s lock-to-release for a cycle that logs broker calls and 15 coins is fast, and git cannot show whether every check ran. Transcripts are needed.
3. **Minor.** XRP dust is $1.47 in the totals but "about $1.22" in the text. The 10-30 log calls pending_deposits $200 "not yet in cash", contradicting earlier entries; it was $0 on 10-31 with no cash change.

**Renewals and deposits:** no stops are open, so **no renewals are due**. The "renew from 2027-01-05" text in `CYCLE.md` and the agenda is stale. The next routine $200 deposit is expected Mon 11-02 and would be booked by the 11-03 00:20 UTC cycle, with a $50 core market buy at that hour for the first time. The odd $262.52 (10-20) and $100 (10-23) deposits are still unconfirmed. Under Check A, any non-$200 deposit becomes Unbooked cash and blocks entries until Daniel confirms.

## 3. Fill quality (market orders vs mark)
| Date (UTC) | Fill | Mark | Premium |
|---|---|---|---|
| 10-19 11:47 | 82,967.62 | 82,196.78 | +0.94% |
| 10-20 13:09 | 82,087.72 | 81,333.01 | +0.93% |
| 10-23 12:55 | 82,366.75 | 81,622.22 | +0.91% |
| 10-24 14:55 | 80,998.80 | 80,218.65 | +0.97% |
| 10-26 10:55 | 81,095.36 | 80,341.75 | +0.94% |
| 10-17 18:51 to 18:56, 5 trading buys | at the ask | not logged | n/a |

Mean +0.938%, sd 0.022, range +0.91% to +0.97%, n=5, all core buys of $21 to $134 between 10:55 and 14:55 UTC. No single-market-order entry under the new rules has happened, and nothing has filled near 00:20 UTC. A guard at x = 1.0, 1.2, 1.5 or 2.0% would have skipped 0 of 5. The heat formula allows 1% spread (factor 1.01), so it does not cover a +1.5% fill.

## 4. What the 10-30 backtest (ca0bcf9) adds
Adds `--heat` and 12-month statistics to `backtest.py`, plus an 11-setting table (70% core, $1,000 + $100/week, data to 10-22). Return a year from 2023 / 2024 / 2025: live (4% risk, 8% heat) +39.0 / +23.7 / -1.0%; no cap +64.1 / +48.6 / +1.9%; 12% heat +47.2 / +30.3 / +0.3%; hold BTC +51.0 / +23.3 / -9.1%. Max drawdown is about -35% everywhere. 60 to 68% of 365-day windows hit +30% (hold BTC 63%), and 0 to 1% from a 2025 start. Its conclusion: the cap costs about 25 points a year, and whether a window hits +30% depends on the market, not the settings.
- **Weight: low.** It uses the engine the Red Team lab audit said not to rely on (fills at the signal close, no exit costs, survivor universe). It is one 3.8-year history, and the 8% figure was never backtested. `backtest/data/` is missing, so I could not re-run it. It cannot show the cap's gap-risk benefit. Under the live formula a 12% stop allows 46% of trading equity in one position, so the cap mainly stops stacking.
- **Live cost so far: zero**, since the cap has never bound. The point-in-time re-run promised before Jan 13 has not started.

## 5. Decisions for Daniel on Sunday
1. **Slippage guard (skip if ask > mark + x%).** x = 1.5% is cheap insurance against abnormal quotes, but the data cannot show a need. The fresh-ask R:R recheck already rejects a marginal setup at about +0.9 pp. The cost is skipping rare breakouts on volatile days, when spreads widen. Robinhood's protection on plain market orders is unverified: the documented 1% / 5% collars cover orders converted from stops. The Research Analyst's check was not in the repo when I looked.
2. **`paper-lab` repo.** Creating it is free and unblocks CI. But the repo would hold only the prototype the Red Team broke (`evals/paper-lab/paper.py`, 10-28). I found no rebuild, re-attack or sign-off, so day 1 will not be 11-01. Each week of slip pushes the earliest live join beyond late January and thins the evidence for the review.
3. **Review 01-13 to 01-09.** 01-09 is a council Saturday, and the sample shrinks only from 88 to 84 days. It needs owner edits (`CLAUDE.md`, the journal trigger) and a dated prereg amendment. Paper evidence will be thin at either date.
4. **Also open:** confirm the two odd deposits; fix the watermark clock and the stale renewal text (owner files); acknowledge the 67.7% core (measure 9); decide whether an idle sleeve is accepted tuition mode; measure running cost; keep the 8% cap until January (the Evaluator would not change it on this evidence).

## 6. Three questions for the Red Team
1. With 0 signals in 13 days, 0 of 5 trades won, and a 30-trade floor out of reach by January, is the review decidable? What pre-registered outcome would count as "the sleeve earns its keep" rather than a default verdict?
2. The log times run ahead of the commits and cycles take 26 to 54 s. How would you show a cycle reported checks it did not perform, and what evidence (transcripts, broker audit trail) closes that?
3. Attack the first 00:20 UTC market buy and the guard: if the ask recheck passes but the fill lands +3% above mark on a volatile breakout night, what is the loss against the 1% heat allowance? Does a 1.5% guard help or only skip the best setups?

## Weaknesses of this briefing
Journal-derived, no broker data: marks and fills are what the agent logged. B3 is my reading of the prereg, and the XRP value is journal-implied. Exit spread is estimated. n=5 fills, one time window, core buys only. I cannot see whether the checks truly ran.

# 1. Crypto trading agent: Evaluator briefing (mode: delivery)
Independent draft, data as of the 2026-10-31 00:25 UTC cycle. No broker tool was called. Every number comes from `evals/trading-agent/briefing_2026-11-01.py` (`python3 -I`), which reads the journal values and `git log`. "Agentic account" = the trading account.

## 1. Performance since 2026-10-17
| Measure | Value | Gap |
|---|---|---|
| Equity vs deposits ($2,260.47) | $2,147.14 | **-$113.33 (-5.01%)** |
| vs hold-BTC B1 (frictionless, $2,141.05) | | +$6.09 (+0.28%) |
| vs B2 (same 0.93% buy premium, $2,131.27) | | +$15.87 (+0.74%) |
| vs passive twin B3 (prereg: in-kind coins held, 50% of cash deposits in BTC, rest idle; $2,158 to $2,163) | | **-$10.94 to -$15.83 (-0.5% to -0.7%)** |
| Active sleeve vs idle cash (capital in $714.29, trading equity $693.94) | | **-$20.35 (-2.85%)** |

- **Reading:** the lead over B1/B2 comes from holding 32% of equity in cash while BTC fell about 5%. Against the twins the active sleeve is behind, by roughly its realized losses. All gaps are inside the noise the prereg assumes (3.2% tracking sd). The sleeve is 99.8% cash; the core is $1,453 (67.7% of equity).
- **Units/NAV (first readings, 10-30 and 10-31):** account 2138.51 units, NAV 1.0000 then **1.0040** (peak 1.0040); sleeve 693.94 units, NAV 1.0000 both days. Tracking started **10-30** (first cycle after the rule commit), not 10-29 as the agenda says. NAV starts after the 10-29 drop, so it shows 0.0% drawdown while equity is 3.6% below its $2,228.08 peak. The circuit breaker ($1,559.66) is 27.4% of equity away.
- **Closed trades, 0 wins of 5:** NEAR -$7.49 (-15.0%); the four 10-29 stop-outs SOL -$3.01, ETH -$3.17, BTC -$5.77 and -$1.04 (total -$12.99). Realized **-$20.48**. The 10-30 journal entry says "about -$26" for the four stop-outs; I cannot reproduce that figure (-$13.0).
- **Spread paid:** measured $3.75 (five core buys). Estimated $8.27 in total, adding about $2.35 entry premium on the 10-17 trading buys (marks not logged) and about $2.18 exit spread.

## 2. Operations (4 daily cycles, 10-28 to 10-31; no manual or triggered cycles)
Only 10-30 and 10-31 ran under all the 10-29 rules. 10-28 predates the lock and Checks. 10-29 had the lock and Checks A to C but not the heat or units rules.

| Control | Observed | Verdict |
|---|---|---|
| Run lock | 3 of 3 acquired and released (46 s, 54 s and 26 s from lock to release commit); `state/run.lock` is `free` | worked, never contended |
| Check A | 10-30: four stop fills booked, $186.49 of sells, difference **$0.00** (the 10-24 misreading did not recur); 10-31: $0.00 | worked, tested on sells only. The deposit path and the non-$200 path have not run since |
| Check B | no open orders, no trading lots | trivially satisfied; mismatch and replace paths untested |
| Heat line | present on 10-30 and 10-31, both $0 | never exercised on a real entry |
| UNRESOLVED | 0 uses, and no entries were placed | untested |
| Check C signals | brk=Y in 0 of 13 days since 10-19 | consistent. BTC needs about +13% to reach hi55 |
| Stop exits | five fills within 0.03% of trigger, no collar slippage | good evidence, but a >5% gap is untested |

**Anomalies:**
1. **Clock.** The "Cash reconciled at" watermark and the log header run 3.0, 7.8 and 3.5 minutes ahead of the commit times (10-29, 10-30, 10-31). Check A queries orders from the watermark, so a fill in that gap would be missed. The chance is tiny but the offset is systematic; the fix is to take the time from `date -u`.
2. **Unverifiable work.** Lock-to-release of 26 to 54 s for a cycle logging broker calls and 15 coins is fast. I cannot tell from git whether every check ran. Tool-call transcripts are needed to verify.
3. **Smaller items.** The XRP dust is valued at $1.47 in totals but "about $1.22" in the text. The 10-30 log calls pending_deposits $200 "not yet in cash", while earlier entries call it the logged 10-26 deposit. It went to $0 on 10-31 with no cash change.

**Dates and deposits:** no stops are open (NEAR plus the four filled), so there are **no renewals due**. The "renew from 2027-01-05" text in `CYCLE.md` and the agenda is stale. The next routine $200 deposit is expected Mon 11-02 and would be booked by the 11-03 00:20 UTC cycle, which makes a $50 core market buy at that hour for the first time. The $262.52 (10-20) and $100 (10-23) deposits are still unconfirmed by Daniel. Under Check A any non-$200 deposit becomes Unbooked cash and blocks entries until he confirms.

## 3. Fill quality (market orders vs mark)
| Date (UTC) | Fill | Mark | Premium |
|---|---|---|---|
| 10-19 11:47 | 82,967.62 | 82,196.78 | +0.94% |
| 10-20 13:09 | 82,087.72 | 81,333.01 | +0.93% |
| 10-23 12:55 | 82,366.75 | 81,622.22 | +0.91% |
| 10-24 14:55 | 80,998.80 | 80,218.65 | +0.97% |
| 10-26 10:55 | 81,095.36 | 80,341.75 | +0.94% |
| 10-17 18:51 to 18:56 (5 trading buys) | at the ask | not logged | n/a |

Core buys (n=5): mean +0.938%, sd 0.022, range +0.91% to +0.97%, $3.75 in total. All were core buys of $21 to $134, between 10:55 and 14:55 UTC. **None of the new single-market-order entries has happened**, and no fill has occurred near the 00:20 UTC run time. A guard at x = 1.0%, 1.2%, 1.5% or 2.0% would have skipped 0 of 5. The 8% heat formula assumes 1% spread (factor 1.01), so a +1.5% fill is not covered.

## 4. What the 10-30 backtest (ca0bcf9) adds
It adds `--heat` and 12-month statistics to `backtest.py`, and a table of 11 settings (core 70%, $1,000 + $100/week, data to 10-22). Live setting (4% risk, 8% heat): +39.0% / +23.7% / -1.0% a year from 2023 / 2024 / 2025. With no heat cap: +64.1% / +48.6% / +1.9%. Hold BTC: +51.0% / +23.3% / -9.1%. 12% heat: +47.2% / +30.3% / +0.3%. Max drawdown is about -35% in every setting. 60 to 68% of 365-day windows reached +30%, against 63% for holding BTC, and 0 to 1% from a 2025 start. The note's conclusion: the 8% cap costs about 25 points a year and the +30% outcome depends on the market, not the settings.
- **How much weight it carries:** low. It uses the same engine the Red Team lab audit said not to rely on (fills at the signal close, no exit costs, survivor universe). It is one 3.8-year history, and the 8% figure was a judgement call never backtested. `backtest/data/` is missing, so I could not re-run it. Two things it does not test: the cap's gap-risk benefit, which daily-close fills hide, and the heat formula, which stops a second position (a 12% stop allows 46% of trading equity in one position).
- **Live cost so far:** zero, since the cap has never bound. The point-in-time re-run on the lab engine, promised before Jan 13, is not started.

## 5. Decisions for Daniel on Sunday
1. **Slippage guard (skip if ask > mark + x%).** Adopting x = 1.5% gives cheap protection against stale or abnormal quotes, but the data cannot show it is needed. The existing fresh-ask R:R recheck already rejects a marginal setup at about +0.9 pp. The guard's cost is skipping rare breakouts on volatile days, when spreads widen. Robinhood's own protection on plain market orders is unverified: the documented 1% / 5% collars apply to orders converted from stops. The Research Analyst's check was not in the repo when I looked.
2. **`paper-lab` repo.** Creating it costs nothing and unblocks CI. But the repo holds only the prototype the Red Team broke (`evals/paper-lab/paper.py`, 10-28). The rebuild, re-attack and sign-offs are not in the council repo, so day 1 will not be 11-01. Every week of slip pushes the earliest live join past late January and thins the paper evidence for the review.
3. **Review 01-13 to 01-09.** 01-09 is a council Saturday, and the sample shrinks only from 88 to 84 days. It needs edits to `CLAUDE.md` and the journal trigger (owner files) and a dated amendment to the prereg. The paper lab's 60-day window ends 12-31 only if day 1 was 11-01, so it will be thin at either date.
4. **Also open:**
   - confirm the two odd deposits
   - fix the watermark clock and the stale renewal text (owner files)
   - acknowledge the 67.7% core concentration (measure 9)
   - decide the idle-sleeve question: wait for breakouts or accept tuition-budget mode explicitly
   - measure the agent's running cost
   - keep the 8% heat cap until January or revisit now (the Evaluator would not change it on this evidence)

## 6. Three questions for the Red Team
1. With 0 signals in 13 days, 0 of 5 trades won, and a 30-closed-trade floor that cannot be reached by January, is the review decidable at all? What pre-registered outcome would you accept as "the active sleeve earns its keep", rather than a verdict by default?
2. The log times run ahead of the commits and the cycles take 26 to 54 s. How would you show the cycle reports checks it did not perform, and what independent evidence (transcripts, broker audit trail, tool-call counts) closes that?
3. Attack the first 00:20 UTC market buy and the guard: on a volatile breakout night where the ask recheck passes but the fill lands +3% above mark, what is the loss against the 1% heat allowance? Does a 1.5% guard help or only skip the best setups?

## Weaknesses of this briefing
Journal-derived, with no broker data. Marks and fills are whatever the agent logged. B3 is my reading of the prereg, and the XRP value is journal-implied. Spread on the exits is estimated. n = 5 fills, one time window, core buys only. I cannot see whether the checks truly ran.

**Paper-lab architecture and measurement: independent draft (Evaluator)**

**Result:** The prototype passes only a synthetic self-test, so the real-data behaviour is untested. The test covered three things: replaying missed days after a restart, re-running the same day as a no-op, and the unit-value (deposit-neutral) arithmetic. I made no network calls and did not touch the trading repo.
- **Reproduce:** `python3 -I -B /home/claude/advisory-council/evals/paper-lab/paper.py`
- **Prototype:** `/home/claude/advisory-council/evals/paper-lab/paper.py`. It is stdlib only. It has an atomic state file, a shared deposit feed, a stop/collar model, and a no-lookahead history slice.
- **Test limits:** The synthetic data is random-walk noise, so the test cannot show that any strategy has an edge. The stop and collar branches were not exercised. Only the unit-value and restart logic was checked.

## 1. Where it runs
Ranked options:
1. **Recommended: a deterministic `bin/paper.py` run as its own scheduled job, in a separate repo or branch, at about 00:50 UTC.**
   - Paper results are not comparable if they depend on whether a cycle ran, so the job must not depend on the cycle succeeding.
   - Put the state in a second private repo (`paper-lab`) or an orphan branch, never in `journal.md`. That avoids git conflicts with the cycle's push and its `state/run.lock`.
   - It holds no broker credentials, makes no order calls, and reads public Coinbase candles only.
   - A GitHub Actions cron job costs nothing, needs no LLM, and cannot hold the live run lock.
   - Its only interface to the live agent is one read: the dated deposit list, taken from the journal.
2. **Appending it to the daily cycle as a final step is the worst choice.** It adds failure modes to the live path, lengthens the run, and puts paper state commits in the same repo as the lock. It also couples results to cycle outages, and it tempts people to have the LLM "run" it.
3. **Agent Zero is wrong for this job.** It is the Red Team's container. A scheduled production-like job there mixes attacker and service roles, and it has no persistence guarantee. Keep it for adversarial review of the paper code.
4. **A new LLM routine is wrong too.** Judgment adds cost, and the deposit error showed that prose is unreliable for bookkeeping.

Cost is near zero. Add a staleness alert if the paper `last_date` is more than 2 days old.

## 2. Data and models
- **Candles:** Reuse the Coinbase daily endpoint, in a Python port of `fetch-candles.sh`.
  - Use completed UTC days only, and drop today's partial candle.
  - Keep raw JSON snapshots in the paper repo so runs can be replayed and audited.
  - Reject gaps and 0/None values.
  - Fetch about 300 days for the 200-day average and the breakout windows.
- **Fills:** Signal on the close of day D-1, fill at the open of day D. This is the same convention as the Red Team's lab.
  - A "live quote at cycle time" fill is rejected for the primary comparison. The quote is irreproducible, different strategies would see different cycle times, and the quote is not archived.
  - The 00:50 UTC run sees D-1's close and fills at D's open, which is only about 50 minutes old. Run it with D's first-hour data if wanted, but fill at the open price.
  - Log the live quote as an optional shadow column to check fill drift.
- **Costs:** 0.95% per side for every strategy and every asset, as in the lab. Add a sensitivity run at 0.5% and 1.5%.
  - Net-liquidation marking includes the exit cost on every holding.
- **Stops:** Gap at the open is filled at the open if it is within 5% of the stop (the collar). Beyond that the order stays unfilled and retries at the next open. Intraday stops fill at the trigger. This is optimistic for fast moves, and the report must say so.
- **Deposits:**
  - One shared `deposits.json`, taken from the live journal's reconciled deposits.
  - Every strategy gets the same cash on the same day.
  - The core share (25%) buys BTC at the next open for all strategies, so differences come only from the trading sleeve.
  - Never re-derive deposits from paper cash.
- **State:** `state/paper/<strategy>.json` is written atomically. Replay is deterministic.
  - A missed day is handled by replaying every missing completed day in order. The prototype covers this case.
  - Re-running the same day is a no-op.
  - A strategy's version hash is stored in its state, and any rule change starts a new strategy ID rather than editing history.

## 3. Metrics and the pre-registered comparison
Report the following:
- Unit-value return, which is deposit-neutral.
- Money-weighted return (XIRR) and net profit in dollars.
- Max drawdown on unit value.
- Turnover and total cost paid.
- Trade count, hit rate and average R. Hit rate and average R are secondary and are reported only for strategies with at least 30 closed trades.
- Each strategy's excess over "core + cash" and "hold BTC", with the benchmarks costed identically. Both benchmarks are mandatory.

**How many days before any conclusion**
- Under 30 closed trades per strategy: no alpha claim.
- Daily crypto volatility is about 3%, so the 3-week standard error on a difference between two strategies is roughly ±10 to 15%. Only gross behavioural facts can be judged in that time. That means costs paid, turnover, trade count, drawdown mechanics, and whether the code and operations are sound.
- Real inference needs at least 60 to 90 days plus the 30 trades. With few trades even that is weak, because strategies that hold BTC beta are highly correlated.

**Multiple comparisons**
- Pre-register before the first day. The file should hold the list of N strategies, the fixed primary metric (unit-value excess over hold BTC, net of costs), the benchmark, and the decision rule.
- Allow no strategy additions without a new ID. Strategies added later are labelled exploratory.
- Compare with paired daily returns against the benchmark. Use a block bootstrap (blocks of 5 to 10 days) on the difference series.
- Correct for N: Bonferroni or Holm for a confirmatory claim, or a White-style reality check on the best of N.
- Act on the best strategy only if it beats the best-of-N null, shows positive excess in both halves of the period, and survives the 1.5% cost run.
- State the expected outcome: with N=8 and 3 weeks, the "winner" is mostly luck.

## 4. Historical warm-start
Yes, do it, but label it as context and not evidence.
- Run each strategy through the Red Team's next-open engine on public candles. `compare_lab.py` already has the accounting, so adapt it.
- Use the same cost and deposit model so the live paper start and the history are comparable.
- State the biases: fixed survivor universe (assets that exist today), rules tuned on one history, no point-in-time universe, and in-sample parameter choices.
- Where a point-in-time universe is not available (it mostly isn't for this exchange), say so and don't fake one.
- Show the output as drawdown, trade count, cost drag and regime spread across start years. Do not rank strategies on it.

## 5. Moving the review to about 2026-11-17
The date is fine for judging operations and mechanics, and too early for strategy.
- **Can judge by 11-17:** whether the pipeline ran daily without gaps, whether paper and live fills and deposits reconcile, cost drag per strategy, the number of signals, drawdown behaviour, and the data and code audit.
- **Cannot judge:** which strategy is better, whether active trading beats core + DCA, or any win rate or average R. At that point there will be about 20 days and few closed trades.

I recommend keeping the strategy decision at 2027-01-13 and holding a 11-17 operations check only. If Daniel does move the date, the decision should be about continuing the lab, not about changing live rules.

## Open questions for Daniel
1. How many strategies, N? More strategies mean a weaker conclusion, so I suggest 4 to 5 at most.
2. May the paper job live in a second private repo or GitHub Actions?
3. Who writes the pre-registration, and are you willing to freeze it before day 1?
4. Is a 11-17 operations-only review enough, or do you want a strategy decision then?

The user-memory notes did not change anything here, so there is nothing for the main session to save.
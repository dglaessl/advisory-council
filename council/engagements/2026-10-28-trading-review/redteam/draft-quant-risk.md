**Quant & Risk Officer: independent draft (trading agent review, 2026-10-28)**

I give risk analysis here, not personal investment advice. Everything below comes from reading files and doing arithmetic offline. I made no network calls and used no brokerage tools.

## 1. Verdict

**Approve with conditions: the agent can keep running.** There is one veto-level issue. Nothing stops two trading runs from happening at the same time, and our standing constraint treats that as a hard fail. I am not asking for a halt now, because the account is cash-only spot, so a duplicate run can at worst repeat a $100–350 order and its spread. But it must be fixed now. I will veto any change to the trading agent that ships without it.

Money at risk on the trading side is small. Open stop-loss risk is $14.76 (2.1% of trading equity) if stops fill at trigger minus spread, and $22.32 (3.2%) if they fill at the 5% price floor. Almost all of the account's risk sits in the unprotected core and in how the system operates, not in trade sizing.

## 2. Findings (ranked by impact × likelihood)

**F1. No lock between runs (VETO-LEVEL).**
- The Mac setup had a lock and a step that saved holdings after each cycle (`legacy-mac/run-cycle.sh:10-13, 24-26`). The cloud setup has neither.
- The check routine starts a full cycle on any of three triggers: cash at least $5 above the journal figure, a missed day, or a coin quantity increase (`cloud/CHECK.md:15-21, 23-27`).
- The daily cycle starts at 00:20, and checks run every 2 hours at :50 (`cloud/config.md:5-6`). If a daily cycle is still running or hasn't pushed by 00:50, the check thinks the day was missed and starts a second cycle. A sale made by the first cycle also looks like "new funds" to the second.
- A failed push does the same thing. Pushes are retried with `git pull --rebase` (`cloud/CYCLE.md:43-45`), but resolving a conflict needs `git rebase --continue`, which `.claude/settings.json` doesn't allow. The next run then reads an old Cash figure and an old trigger file and can buy the same $100 of core BTC again.
- It has nearly happened already: two "scheduled daily cycle, cloud" runs 13 minutes apart (`journal.md:62, 67`).

**F2. Stops may not fill in a gap, and they expire with no automatic renewal.**
- Each stop's "price" is 5% below its trigger. I think it is most likely a price floor (Robinhood calls this a collar): after the stop fires, it won't sell below that price. This is not confirmed.
- If that's right, a drop of more than about 5% below the trigger leaves the position unsold with no protection. For BTC that is a 9.4% fall from the current mark. Altcoins gap like that much more often.
- The backtest assumes every stop fills at the stop price or at the gapped open (`backtest/backtest.py:8-9, 254-255`), so this risk isn't modelled.
- All stops expire around 2027-01-15. The only reminder is a note in the journal (`journal.md:14`), and the agent deletes old journal entries once there are more than 30 (`CLAUDE.md:135-136`). Nothing in code makes the agent renew them.
- Every cycle the journal says "Stops intact", but that is the model's own word. `CLAUDE.md:125` only says to "check the stops", not to compare order IDs and quantities against the broker.
- One good data point: NEAR filled at $4.2488 against a $4.25 trigger, only 0.03% slippage.

**F3. Mistaking a stop fill for a deposit can happen again.**
- The check labels any cash increase "new funds detected" (`CHECK.md:16, 24-26`), and that label pushes the agent toward calling it a deposit. That is how the 2026-10-24 NEAR stop fill became a $21.24 core buy.
- The fix lives only as a "LESSON" note in the journal, which can be edited or trimmed away. It is not in the owner's files.

**F4. The hard rules are mostly prose, not code.**
- `settings.json:10-12` allows placing and cancelling orders with no limit on size, account or count. The CHECK routine also runs with these permissions, even though it's described as read-only.
- Account choice, trade caps, the 50% position cap, the STOP kill switch and "never sell the core" all depend on the model following text. The BTC trading lot shares an asset with the core, so one wrong stop quantity could sell core BTC.
- The real controls are probably on the broker side: agentic access is limited to account <XXXX>, crypto is cash-only (not verified), and a buy can't exceed buying power, which is currently $506.
- Rules can drift. The journal is writable by the agent and holds "Owner decisions" that change how rules are applied (`journal.md:15`, e.g. item (c)). Of all the inputs, this is the most realistic route for prompt injection. Coinbase candle data is just numbers and is low risk.

**F5. Concentration.**
- 77.3% of equity is crypto ($1,725 of $2,232). The untraded core is 68.5% with no stops (owner decision, 2026-10-18).
- If all crypto falls 30%, total loss is about $473 (−21%). At −50% it is about $779 (−35%). At −70% it is about $1,085 (−49%). ETH and SOL move largely with BTC, so splitting across coins gives little protection.
- The circuit breaker uses total equity, so the core would have to fall about 43% before it trips. Even then it only pauses buying. Weekly $200 deposits push up the "peak" figure, which further hides losses. In practice the breaker almost never fires.

**F6. Sizing is roughly consistent, but the spread isn't counted.**
- At $703 trading equity, 4% risk is $28. Stops between 4.5% and 20% give positions of $141–352. The 50% position cap ($352) applies whenever the stop is closer than 8%.
- The formula leaves out the spread, about 1.9% round trip:

| Stop distance | Loss if filled at trigger minus spread | Loss if filled at the price floor |
|---|---|---|
| 5% | 2.95% of trading equity | 4.9% |
| 10% | 4.34% | 5.8% |

- The rule "reward at least 2.5× the risk" is measured before costs. At a 5% stop it is about 1.5× after costs.
- The $10 minimum order doesn't matter at this account size.

**F7. No alerts, and the git history can't be checked.**
- The Mac's notification script (`notify.py`) wasn't carried over to the cloud. A "CHECK FAILED" or a failed push only shows up in the routine's output.
- The repo has 1 commit, so I can't use git history to check the cut-over or past duplicate runs.

## 3. Measures

| # | What | Why | How to test | When |
|---|---|---|---|---|
| M1 | Lock through git: at the start, commit `state/lock` (run ID, time) and push. If the push is rejected, pull; if the lock is under 90 minutes old, stop. Remove it at the end. Short term: make sure no check runs between 00:20 and 01:50, or make CHECK skip that window. | F1 | Start CYCLE and CHECK at the same time on a test branch with no order tools. Exactly one should get past the lock. Also simulate a rejected push. | **Now** (Daniel edits `cloud/` or the routines) |
| M2 | A step in `CYCLE.md` that lists open stop orders and compares ID, quantity and trigger with the journal. Any mismatch, or a stop older than 75 days, puts "ACTION NEEDED" in the summary. | F2 | Use a copy of the journal with a removed stop and one with a stop 80 days old. Both must be flagged. | **Now** |
| M3 | Before calling it new funds, CHECK compares cash against the journal cash plus sells filled since the last cycle. The deposit rule moves into `CYCLE.md`. | F3 | Run the 2026-10-24 inputs again. The result should be "stop fill", not a deposit. | **Now** |
| M4 | Find out what the stop's "price" field means, read-only (order fields, Robinhood docs). If it is a floor, decide between a wider gap and accepting the risk. | F2 | A written answer with a source | **Now** to find out; any change on **Jan 13** |
| M5 | Hermes health check: no new commit for over 26 hours, "CHECK FAILED", stops missing → Telegram alert | F7 | Pause a routine on purpose. The alert should arrive within 26 hours. | **Now** |
| M6 | Move "Owner decisions" into a file the agent can't write to | F4 | Settings show write access denied | Jan 13 |
| M7 | Measure the breaker after removing deposits. Size positions with spread and floor slippage included. State the core concentration decision explicitly. | F5, F6 | Backtest using the Evaluator's version with spread-aware sizing and a gap/floor failure model | Jan 13 |
| M8 | Put the hard kill in writing: turn off both routines and remove the connector's agentic access, not just the `STOP` file | F4 | Dry run of the steps | Now (documentation only) |

M1–M3 change operations, not trading rules, so they fit Daniel's freeze until the 2027-01-13 review.

## 4. Could not verify

- What Robinhood's stop "price" field means, when stops expire, and which price triggers them.
- Whether broker-side agentic access really limits trading to account <XXXX>, and whether the account can ever use margin.
- Whether the Mac jobs are actually stopped: the git history was squashed to 1 commit and there are no Mac logs.
- The check routine's exact hours and how long a cycle runs.
- Whether the repo is private.

**Confidence:** high on F1, F3, F4 and F6, which come from the code and the numbers above. Medium on F2, which depends on Robinhood behaviour I couldn't check.

**Files:**
- `/home/claude/robinhood-agent-cloud/cloud/CHECK.md`
- `/home/claude/robinhood-agent-cloud/cloud/CYCLE.md`
- `/home/claude/robinhood-agent-cloud/cloud/config.md`
- `/home/claude/robinhood-agent-cloud/.claude/settings.json`
- `/home/claude/robinhood-agent-cloud/CLAUDE.md`
- `/home/claude/robinhood-agent-cloud/journal.md`
- `/home/claude/robinhood-agent-cloud/legacy-mac/run-cycle.sh`
- `/home/claude/robinhood-agent-cloud/backtest/backtest.py`

**Worth saving to memory (for the Chair):** the cloud agent has no lock between runs (the Mac's `.cycle.lock` wasn't carried over). Stop orders placed 2026-10-17 expire around 2027-01-15. I flagged the lock as veto-level for any change to the trading agent.
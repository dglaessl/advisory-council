# Running one trading cycle in the cloud

This file replaces the Mac's `bin/run-cycle.sh` (see `legacy-mac/`). A cloud routine runs it once
a day at 00:20 UTC. The owner may also start one manually. `cloud/CHECK.md` is a read-only
watchdog and never starts a cycle (owner decision 2026-10-28).

The repository is the agent's memory: every run starts from a fresh copy and must push its changes
back, or the next run won't know what happened.

## Before you start

1. `git pull` so you have the latest journal.
2. If a file named `STOP` exists at the repository root, place no orders. Update `- Last cycle:`
   in journal.md, add a cycle entry saying "halted by STOP", commit, push and end. (Stop orders
   already resting at Robinhood stay active; STOP only stops this agent from placing or
   cancelling orders.)
3. **Take the run lock.** Read `state/run.lock` (it may be missing).
   - If it starts with `held`, another cycle is running or one crashed. Place no orders, change no
     files, and end with `ACTION NEEDED: run lock held (<its contents>); not trading`. Never take
     over or clear someone else's lock. The owner clears a stale lock.
   - Otherwise create a run ID with `date -u +%Y%m%dT%H%M%S-%N`, write `state/run.lock` as one line
     `held <RUN_ID> <UTC time as YYYY-MM-DDTHH:MMZ>`, commit only that file (`lock <RUN_ID>`) and
     `git push`.
   - You hold the lock only when a `git push` of your lock commit succeeds. If it is rejected, run
     `git pull --rebase`. If `state/run.lock` still shows your RUN_ID, push once more. If that push
     fails too, or the lock shows anything else, or the pull or rebase reports any error or
     conflict: run `git rebase --abort` if a rebase is in progress, place no orders, and end with
     `ACTION NEEDED: could not take the run lock; not trading`. Never force-push.
   - From here on, **every** way of ending the cycle (including CLAUDE.md rule 8 and any
     `ACTION NEEDED`) goes through "After the cycle" steps 3-5, so the lock is released and pushed.
     The lock stays `held` only if that final push fails.
4. Read `CLAUDE.md` (the rules) and `journal.md` (state, notes, cycle log) in full.
5. If a file named `NO_NEW_ENTRIES` exists at the repository root: this cycle may manage exits
   (stops, trims, breakdowns) but must not buy anything, including core BTC. Say so in the cycle log.
   Still log any deposit; add its core share to "Core BTC owed" in State and buy it in the first
   cycle after the file is removed.

## The cycle

Follow the "Trading cycle" section of CLAUDE.md, with these environment notes and the three
checks below. Where they are stricter than CLAUDE.md (run lock, NO_NEW_ENTRIES, Checks A and B),
they take precedence, consistent with CLAUDE.md hard rule 8. In particular, Check A replaces
"a cash increase that no sale explains is a deposit" in CLAUDE.md cycle step 2.

- **Robinhood:** use the Robinhood connector's tools. Trade only the agentic account ending [ACCT]
  (account_number / rhs_account_number [ACCOUNT]).
- **Price history:** `./bin/fetch-candles.sh daily SYMBOL [SYMBOL...]` (or `hourly`), then
  `python3 bin/analyze.py daily` (or `hourly`; add `--recent SYM` for raw candles). Symbols are
  bare codes such as BTC ETH SOL NEAR.
- **Arithmetic:** never do sums in your head. Run `python3 bin/calc.py` with every expression as a
  separate quoted argument in one command, numbers written out literally, for example
  `python3 bin/calc.py "0.00966963*83016.68" "(1982.70-1991.92)/1991.92"`.
  No `cd`, loops, shell variables, pipes or `&&` around it.
- **Journal:** update journal.md with the Edit or Write tool. Always update the `- Last cycle:` line
  in State, even on a halt or when nothing happens, and keep the `Cash: $` figure exact. After the
  cycle's last fill (or after Check A when nothing was traded), write `- Cash reconciled at:
  <UTC time>` in State, and list in the cycle log the ID of every order placed this cycle.

### Check A: reconcile cash before calling anything a deposit (step 2 of the CLAUDE.md cycle)
This replaces judging deposits by eye (a stop fill was booked as a deposit on 2026-10-24).
1. Call `get_crypto_orders` with `updated_at_gte` = the journal's `- Cash reconciled at:` time (or
   `- Last cycle:` if that line is missing), as UTC ending in `Z`. Take every order with filled
   quantity since then, including stop orders, but **skip any order ID already recorded in the
   journal** (its effect is already in `Cash: $`), except an order listed as `UNRESOLVED`: count its
   fill and resolve it in the journal.
2. With `bin/calc.py`: expected cash = journal `Cash: $` + the executed notional of filled sells
   − the executed notional of filled buys. Difference = `crypto_buying_power.buying_power` −
   expected cash.
3. Classify the difference:
   - between −$1 and +$1: no deposit.
   - between +$199 and +$201: the routine weekly $200 deposit. Log it and buy core BTC as CLAUDE.md
     says.
   - anything else (any other increase, or any decrease): **do not** call it a deposit and **do
     not** buy core BTC. Add `## OWNER ACTION NEEDED` at the top of the journal with the numbers
     (journal cash, fills, buying power, difference) and make no new entries this cycle. Exits
     still run.
   - The owner confirms by adding a line `OWNER CONFIRMED <date>: $<amount> deposit` to the journal
     Notes and removing the note. A later cycle whose difference equals a confirmed amount (±$1)
     books it as a deposit and buys the core share, then changes that line to `OWNER CONFIRMED
     <date>: $<amount> deposit, BOOKED <UTC time>`. A BOOKED line is never used again.
   - While an unresolved `## OWNER ACTION NEEDED` note exists, make no new entries. "New entries"
     means trading positions. The core buy for a booked deposit still happens; if it is skipped
     for any reason, add its amount to "Core BTC owed", except when the buy's outcome is unclear
     (CLAUDE.md "Entries"): then record it as `UNRESOLVED` and leave it to the owner.
4. Write the reconciliation in the cycle log: `Cash check: journal $X + sells $Y − buys $Z =
   expected $E; buying power $B; difference $D → <classification>`.

### Check B: verify every stop with the broker (before deciding trades)
1. Call `get_crypto_orders` with `state_group` = `open`.
2. For every trading position in the journal's State, there must be open stop orders whose total
   quantity equals the trading lot and whose `stop_price` equals the journal's stop. List the order
   IDs in the journal.
3. If a stop is missing, look that order ID up with `get_crypto_orders` `order_id`.
   - If it **filled**, the position (or that part of it) is closed: record the exit, remove the
     lot from State, and continue. This is normal, not an owner action.
   - Place it again only if its state is canceled, expired or rejected with zero filled quantity,
     AND the broker quantity minus the journal's core quantity equals the journal's trading lot
     (±0.1%), AND the current bid is above the trigger. If the bid is at or below the trigger, the
     stop level is already hit: exit the lot as CLAUDE.md says.
   - In any other case place nothing: add `## OWNER ACTION NEEDED` with the details and make no
     new entries this cycle. If quantities or triggers don't match: same, don't guess.
4. Renewal: any open stop whose `created_at` is more than 80 days ago is renewed with the same
   trigger and quantity, using the "Moving a stop" procedure in CLAUDE.md (cancel, place
   immediately, confirm both). Stops placed 2026-10-17 are renewed from 2027-01-05. Keep each
   stop's renewal date in State next to it. If placing the new stop fails after the cancel, do
   not retry: add `## OWNER ACTION NEEDED (lot unprotected: <COIN>)`.
5. Never place, move or cancel a stop on core coins.

### Check C: log the signals
In every cycle log entry add `- Signals: brk=Y: <coins or none>; taken: <coins or none>; skipped:
<coin: reason>`. This lets the 2027-01-13 review measure the strategy, not just the trades.

## After the cycle

1. Save the holdings snapshot used by the watchdog: write `state/holdings.txt` with one line
   per coin, `<CODE> <quantity>`, sorted by code, exactly as get_crypto_positions reports
   `quantity` (for example `BTC 0.01110445`). Leave out coins with quantity 0.
2. Rebuild the dashboard: `./bin/build-dashboard.sh`, then publish `dashboard/dashboard.html` to the
   dashboard artifact named in `cloud/config.md` with the Artifact tool (read it first, then publish
   with that url and file_path, omitting icon and capabilities; if refused because the live version
   differs, publish the same file again, at most 3 times). If the Artifact tool isn't available in
   this run, skip this step and say so in your final message. Never let it block the cycle.
3. **Release the run lock:** write `state/run.lock` as `free <RUN_ID> <UTC time>`.
4. Commit journal.md and state/ (including the released lock) with a message like
   `cycle 2026-10-23 00:20 UTC: no trades` or `cycle …: BUY BTC $100 (core)`, and push. If the push
   is rejected, `git pull --rebase` and push again. If the rebase reports a conflict, run
   `git rebase --abort`, place no further orders, and end with `ACTION NEEDED: push failed after
   trading; journal not saved` plus the trades made, so the owner can repair the journal. Never
   force-push.
5. End with a 2-4 line summary: equity, trades made, anything the owner should know. Start the
   first line with `ACTION NEEDED:` if the journal has an `## OWNER ACTION NEEDED` or
   `## OWNER REVIEW NEEDED` note, or if anything failed.

## Hard limits for every cloud run

- Only the Robinhood connector's tools listed in CLAUDE.md, only on the account ending [ACCT].
- Never move money, change Robinhood settings, or touch the owner's other account (••••[OTHER]).
- Never edit CLAUDE.md or the files in `cloud/`. Those are the owner's.
- Don't change the routines or their schedules.
- Never clear or take over a run lock that isn't yours.

# Running one trading cycle in the cloud

This file replaces the Mac's `bin/run-cycle.sh` (see `legacy-mac/`). A cloud routine runs it
either on its daily schedule or from `cloud/CHECK.md` when new funds or coins arrive.

The repository is the agent's memory: every run starts from a fresh copy and must push its changes
back, or the next run won't know what happened.

## Before you start

1. `git pull` so you have the latest journal.
2. If a file named `STOP` exists at the repository root, place no orders. Update `- Last cycle:`
   in journal.md, add a cycle entry saying "halted by STOP", commit, push and end.
3. Read `CLAUDE.md` (the rules) and `journal.md` (state, notes, cycle log) in full.

## The cycle

Follow the "Trading cycle" section of CLAUDE.md. Notes for this environment:

- **Robinhood:** use the Robinhood connector's tools. Trade only the agentic account ending <XXXX>
  (account_number / rhs_account_number <ACCT>).
- **Price history:** `./bin/fetch-candles.sh daily SYMBOL [SYMBOL...]` (or `hourly`), then
  `python3 bin/analyze.py daily` (or `hourly`; add `--recent SYM` for raw candles). Symbols are
  bare codes such as BTC ETH SOL NEAR.
- **Arithmetic:** never do sums in your head. Run `python3 bin/calc.py` with every expression as a
  separate quoted argument in one command, numbers written out literally, for example
  `python3 bin/calc.py "0.00966963*83016.68" "(1982.70-1991.92)/1991.92"`.
  No `cd`, loops, shell variables, pipes or `&&` around it.
- **Journal:** update journal.md with the Edit or Write tool. Always update the `- Last cycle:` line
  in State, even on a halt or when nothing happens, and keep the `Cash: $` figure exact: the
  deposit check compares Robinhood's buying power with it.

## After the cycle

1. Save the holdings snapshot used by the deposit check: write `state/holdings.txt` with one line
   per coin, `<CODE> <quantity>`, sorted by code, exactly as get_crypto_positions reports
   `quantity` (for example `BTC 0.01110445`). Leave out coins with quantity 0.
2. Rebuild the dashboard: `./bin/build-dashboard.sh`, then publish `dashboard/dashboard.html` to the
   dashboard artifact named in `cloud/config.md` with the Artifact tool (read it first, then publish
   with that url and file_path, omitting icon and capabilities; if refused because the live version
   differs, publish the same file again, at most 3 times). If the Artifact tool isn't available in
   this run, skip this step and say so in your final message. Never let it block the cycle.
3. Commit journal.md and state/ with a message like `cycle 2026-10-23 00:20 UTC: no trades` or
   `cycle …: BUY BTC $100 (core)`, and push. If the push is rejected, `git pull --rebase` and push
   again. Never force-push.
4. End with a 2-4 line summary: equity, trades made, anything the owner should know. Start the
   first line with `ACTION NEEDED:` if the journal has an `## OWNER ACTION NEEDED` or
   `## OWNER REVIEW NEEDED` note, or if anything failed.

## Hard limits for every cloud run

- Only the Robinhood connector's tools listed in CLAUDE.md, only on the account ending <XXXX>.
- Never move money, change Robinhood settings, or touch the owner's other account (•••• <XXXX>).
- Never edit CLAUDE.md or the files in `cloud/`. Those are the owner's.
- Don't change the routines or their schedules.

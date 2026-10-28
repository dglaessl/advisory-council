# Regular check: deposits, transfers and a missed daily cycle

This file replaces the Mac's `bin/check-deposit.sh` and `bin/daily-gate.sh` (see `legacy-mac/`).
A cloud routine runs it every 2 hours. Most runs find nothing and end in under a minute, without
committing anything.

1. `git pull`. If a file named `STOP` exists at the repository root, end without doing anything.
2. Read the State section of journal.md: the `- Last cycle:` time and the `Cash: $` figure.
   Read `state/holdings.txt` (one `<CODE> <quantity>` per line) and `state/last-deposit-trigger.txt`
   (an ISO UTC time, or missing).
3. With the Robinhood connector (account ending <XXXX>, read-only calls only), get
   `get_portfolio` → `crypto_buying_power.buying_power`, and `get_crypto_positions` → each coin's
   `quantity`. If either call fails, end with `CHECK FAILED: <error>`. Don't retry and don't trade.
4. Decide, using `python3 bin/calc.py` for the comparisons:
   - **New cash:** buying power is more than $5 above the journal's `Cash: $`, and the last
     deposit trigger was more than 3 hours ago (or there is none).
   - **Coin transfer in:** any coin's quantity is above its value in `state/holdings.txt` by more
     than 0.1%, or a coin appears that isn't in the file. No cooldown.
   - **Missed daily cycle:** the time is past 00:20 UTC and `- Last cycle:` is earlier than today's
     00:00 UTC (the daily cycle hasn't run since the last daily candle closed).
5. If none applies: update `state/holdings.txt` to the current quantities. Commit and push only if
   the file changed. End with `CHECK OK: nothing new`.
6. If one or more applies: write the current time to `state/last-deposit-trigger.txt` (only when
   new cash triggered), then run one full trading cycle exactly as `cloud/CYCLE.md` describes. Give
   it the trigger as the reason, for example `new funds detected (buying power $534.74 vs journal
   cash $334.74)`, `coin transfer detected (ETH +0.25)` or `daily cycle catch-up`. The cycle commits
   and pushes everything.

The same hard limits as in `cloud/CYCLE.md` apply.

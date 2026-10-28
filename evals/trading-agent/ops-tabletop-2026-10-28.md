# Ops tabletop, 2026-10-28 (Evaluator)

Method: paper walk-through of an LLM executor using only cloud/CYCLE.md, cloud/CHECK.md, README.md
(owner-controls table) and, where CYCLE.md defers to it, CLAUDE.md. Nothing was executed. No network,
no brokerage tools, trading repo read-only. Line refs: C = CYCLE.md, K = CHECK.md, R = README.md.

Reproduce: re-read those files and repeat each walk below. Arithmetic is by hand (calc.py not run).

## Results

| # | Result | Deciding line |
|---|---|---|
| S1 | PASS | C:52-56 |
| S2 | PASS | C:57-58 |
| S3 | PASS | C:59-62 |
| S4 | PASS (with a git-config hole) | C:18-26 |
| S5 | PASS | C:18-20, K:22, R:21 |
| S6 | PASS | C:71-72 |
| S7 | PASS on "no trade/commit"; alerts: see below | K:8, K:37 |
| S8 | PASS (message is clear, but it is an ALERT, repeated) | K:23-25 |

### S1
Order query from Last cycle returns the NEAR stop fill (10 x 4.2488 = 42.488). Expected cash = 384.74 + 42.488 - 0 = 427.228. Buying power 427.22 gives difference -0.008, inside -1..+1, so "no deposit" (C:55). No core buy. Note the old CLAUDE.md cycle step 2 ("cash increase no sale explains is a deposit") still exists, but C:49 says Check A replaces it.

### S2
No fills, expected 405.98, difference +200.00, inside +199..+201 (C:57-58). Deposit logged, core BTC buy of 50% = $100 per the CLAUDE.md owner settings. Passes provided no NO_NEW_ENTRIES file.

### S3
Difference +100 falls in "anything else" (C:59). The text says do not call it a deposit, do not buy core BTC, write `## OWNER ACTION NEEDED` with the numbers, no new entries, exits still run. Matches expectation. The check (K:26) will also alert on the note every 2 h.

### S4
Case 1, B starts after A pushed the lock: B sees `held`, ends with ACTION NEEDED (C:18-20). Case 2, both pull before either pushes: both write lock commits, the second push is rejected, the pull conflicts on state/run.lock (or shows A's RUN_ID), B ends "lost the run-lock race" (C:23-26). Exactly one trades.
Hole: a plain `git pull` on diverged history can fail with "need to specify how to reconcile divergent branches" (no conflict). Then state/run.lock still shows B's own ID, so C:23 says "push once more", which is rejected again, and the file gives no next step. An executor might force-push (forbidden only at C:99, after the cycle) or proceed. Fix: say "use `git pull --rebase`; any failure, rejection or non-own RUN_ID means stop".

### S5
Next daily cycle: C:18-20 stops it with ACTION NEEDED, no orders, no file changes. Check: lock `held` older than 3 h raises "Stuck run lock" (K:22), so between 3 h and 5 h given 2-hourly runs. R:21 tells the owner to edit state/run.lock to start with `free`. Side effect: because the blocked cycle changes no files, "Last cycle" goes stale and a second "Missed daily cycle" alert fires at 25 h (consistent, not wrong).
Gaps: R:21 does not say to commit and push the edit. Other early exits after the lock (CLAUDE.md rule 8 "when unsure, stop", tool errors) do not say whether to release the lock, so any error leaves a stuck lock; probably intended, but unstated. The lock timestamp format is not specified (`<UTC time>`); K:22 must parse it. The file in the repo uses `2026-10-28T11:58Z`.

### S6
Check B: stop missing, lot still held, so re-place with same trigger and quantity and confirm (C:71-72). Allowed under NO_NEW_ENTRIES (exits) and after a Check A flag (not an entry). Ambiguities: whether the re-placement counts toward the 3-trades-per-cycle cap (stops do not per journal decision (c), but CYCLE.md does not repeat it); whether a triggered-but-not-yet-filled stop is absent from `state_group=open`, in which case a duplicate sell could be placed.

### S7
Check cannot trade or commit (K:3, K:8-10, K:37). It does `git pull` and sees the `held` lock (< 3 h, no alert) and the previous day's Last cycle (about 24.5 h, below 25 h, no missed-cycle alert). So at 00:50 with nothing yet traded: `CHECK OK`, plus a "New cash" note if a deposit has landed.
But if the cycle has already traded by 00:50, the check compares live broker state against stale repo state (journal and holdings.txt are only pushed at the end), giving false alerts: a sell or trim gives "Unexpected holdings drop"; a moved stop (old ID cancelled, new ID not yet in journal) gives "Missing stop"; a buy gives a "Coin transfer in" note. Also, a cycle running past about 01:20 would make a check at 01:50+ raise a false "Missed daily cycle" (25 h from the 00:25 start). Suggested fix: if run.lock is `held` and under 3 h old, report mismatches as notes ("cycle in progress").

### S8
Stop fill: the journal stop ID is not in the open orders and the trading lot is gone from holdings, so the message is "stop probably filled: NEAR" (K:23-25). The holdings-drop alert is excluded by the "explanation from a filled stop" clause (K:27-28). A "New cash" note appears (sale proceeds). So no false drop alarm; the message is clear. Caveats: it is raised as an ALERT, and it repeats every 2 h until the next daily cycle updates the journal and holdings (up to about 12 alerts). The check lists only open orders, so it cannot confirm the fill and infers it.

## Ambiguities an LLM could resolve the wrong way (ranked)
1. **Check A double count (highest).** Order query starts at the journal's Last cycle, but journal timestamps are cycle START times (for example 00:25), and the cycle trades after that and writes Cash after trading. Yesterday's own fills have updated_at after the Last-cycle time, so they get subtracted/added again and the difference is off by that notional. Real examples: a $100 core buy gives difference +100, "anything else", a false OWNER ACTION and no core buy. Fix: define Last cycle as the END time (written after the final trade), or filter to orders after the previous cycle's last fill, or state that fills already listed in the last cycle log are excluded.
2. Check B for a position whose lot is gone (S1/S8 NEAR): C:71 handles only "lot still held". Nothing says to remove the position from State and journal, or that this is not an owner-action case. Executor may flag a mismatch and block entries.
3. "The owner confirms in the journal" (C:61): no format. CLAUDE.md rule 6 says buys stay paused until the owner removes a note; an executor may apply that to every OWNER ACTION note, or may book the deposit without any confirmation. The same +$100 also re-flags every cycle until the owner edits Cash.
4. Deposit band is exactly $200 plus or minus $1. A catch-up of two weekly deposits ($400), a $200 deposit plus a fee, or a changed weekly amount all go to the owner. Safe, but frequent.
5. K:28-29 "core coins must never decrease" versus a BTC or ETH trading lot sold by a stop: BTC holdings legitimately drop. The text does not say to subtract the journal lot first.
6. Lock-release on error paths (see S5) and the git pull failure mode (see S4).
7. Old CLAUDE.md step 2 and CHECK-era "next cycle books it" wording still contradict Check A if the executor reads CLAUDE.md last.

## Weaknesses of this test
Paper walk-through by one reader, not a live run with a real executor model; it cannot show how an LLM actually behaves on ambiguous text, nor real Robinhood response shapes (field names, order states such as "triggered"), git behavior on real races, or routine scheduling. Scenarios were the Chair's; unlisted ones (partial fills, STOP present together with a stuck lock, API errors mid-cycle) are untested. Recommend a live dry run with an executor model on a scratch copy of the repo and mocked tool outputs.

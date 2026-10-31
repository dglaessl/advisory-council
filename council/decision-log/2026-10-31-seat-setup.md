# Decision: seat build-out, Saturday 2026-10-31

- **Status:** recorded. The setup was done by Daniel at the keyboard, guided by the Chair.
- **Revisit:** 2026-11-14 (council meeting), and the Field Scout's 60-day probation review.

## Result
| Seat | Status | Evidence |
|---|---|---|
| Lead Engineer (OpenHands 1.16.0, DigitalOcean `lead-engineer`, 64.23.254.254) | **Live** | Smoke tests 1–4 pass: SSH is the only public port; key files are 600; only `LLM_API_KEY` is inside the container; metadata is blocked; the agent runs as uid 1000; the token reaches only advisory-council (403 for admin). Test 6: draft PR #1 touched only `bridge/tests/test_bridge.py` (+8). The Evaluator passed it (29 tests; a mutation check confirmed the test catches the bug). The Chair merged it. Test 5 was skipped: there is no branch-protection ruleset yet. |
| Strategy Panels (CrewAI 1.15.33, Docker on the Mac) | **Live** | The dry run and a real run (`venture-smoke-02`, `openai/gpt-6-luna`) both pass. The reply is validated by bridge.py and `employment_conflict_check` is filled in (needs_review). An attempted rerun under an existing task_id was refused, as designed. |
| Toolsmith (Goose 1.57.0, Mac, `anthropic/claude-sonnet-5.5` via OpenRouter, approve mode) | **Live, with a rule** | Asks before every tool use; stays in the work folder; clean environment; when a call was denied, it did not retry. **Finding:** `.gooseignore` does not cover the shell tool (`cat .env.decoy` succeeded). **Rule:** Daniel denies any shell command that reads `.env`, key, credential or config files, and no real secrets go in `~/council/goose-work`. |
| Field Scout (OpenClaw 2026.10.8, droplet `field-scout`) | **Parked** | The OOM is fixed (2 GB swap) and the interface is bound to 127.0.0.1 only. The plugin quarantine works: the perplexity auto-install is blocked. But the blocked install leaves startup maintenance unfinished and the gateway loops, even after `OPENCLAW_NO_RESPAWN=1`, a perplexity deny and a state reset. The service is disabled. Next step: test on a fresh droplet with the updated kit, or wait for an OpenClaw fix. |

## Kit fixes committed today
- OpenClaw: `OPENCLAW_NO_RESPAWN=1`; `perplexity` added to `plugins.deny`.
- CrewAI Dockerfile: `COPY --chmod` (host files with mode 0600 broke the container).
- Goose README: `.gooseignore` does not cover the shell tool.
- Confidential third-party material removed from the repo tree (meeting inputs and item-4b briefings are gitignored). **Open:** they are still in git history, which the Lead Engineer's token can read. Daniel decides whether to rewrite history or narrow the token.

## Open items
- Goose via "OpenRouter Login" created a new key without a cap. Daniel to set a $15 limit and delete the unused key.
- Branch-protection ruleset for `main`, then smoke test 5.
- Red Team security pass on the new seats (pending).
- Rename the droplet `field-engineer` to `lead-engineer` in DigitalOcean.

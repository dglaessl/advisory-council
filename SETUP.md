# Setup runbook — Phase 1

Phase 1 stands up the smallest council that can prove itself:

| Seat | Agent | Where it runs |
|---|---|---|
| Chair | Claude Code (Opus) | council host, over SSH |
| Chief of Staff | Hermes | council host |
| Red Team & Lab | Agent Zero (non-Anthropic model) | Docker on council host |
| Evaluator, Quant & Risk, Research Analyst, Scribe, Tutor | Claude subagents | inside the Chair session |

Everything shares **one checkout of this repo** on one host, so the file
mailbox in `council/` just works. (Alternative: sync `council/` via git; see
the end.)

Install commands change often. For each tool, follow its **current official
docs**; this runbook gives the order and the security settings.

---

## 0. Decisions before you start
- [ ] **Host.** A small Linux VPS (2 vCPU / 8 GB RAM / ~100 GB disk is a
      reasonable starting size for Hermes plus one Docker agent) or a
      spare machine at home. Not your daily Mac.
- [ ] **Model keys.** Anthropic (Chair + subagents); one non-Anthropic
      provider for the Red Team (e.g. OpenRouter); Hermes' model of choice.
- [ ] **Spend caps** set in every provider console before the first run.

## 1. Harden the host
- [ ] Non-root user with sudo; SSH key login only; password login off.
- [ ] Firewall: deny all inbound except SSH. No agent UI is ever exposed
      publicly — reach UIs through an SSH tunnel.
- [ ] Automatic security updates on.
- [ ] Docker installed. **Never** mount `/var/run/docker.sock` into any
      agent container.
- [ ] Secrets in a `.env` file per seat (`chmod 600`), or a secrets
      manager. `.env*` is git-ignored. Each seat gets only its own keys.

## 2. Repo and Chair
- [ ] Push this folder to a **private** GitHub repo, clone it on the host.
- [ ] Install Claude Code on the host and sign in with your personal
      account.
- [ ] `cd` into the repo and start Claude Code. `CLAUDE.md` becomes the
      Chair prompt; `.claude/agents/*.md` are the Claude seats.
- [ ] Check: ask the Chair "who is on the council and what can each seat
      do?" It should list the seats and permission levels correctly.
- [ ] Run the bridge tests: `python3 -m unittest discover -s bridge/tests`

## 3. Hermes — Chief of Staff
- [ ] Install Hermes per the official docs (github.com/NousResearch/hermes-agent).
- [ ] Copy `external/hermes/SOUL.md` to Hermes' global SOUL.md.
- [ ] Copy `external/hermes/skills/council-inbox/` into Hermes' skills folder.
- [ ] Set `COUNCIL_ROOT` to the repo path in Hermes' environment.
- [ ] Connect the Telegram gateway and restrict it to **your** Telegram
      account only.
- [ ] Keep Hermes' approval prompts on for commands with side effects.
- [ ] Add scheduled jobs: council inbox check (hourly), weekly digest
      (Monday), revisit reminders (daily scan of `council/decision-log/`).
- [ ] Check: send a test task (step 5) addressed to `chief-of-staff`;
      Hermes claims it and replies.

## 4. Agent Zero — Red Team & Lab
- [ ] Run Agent Zero in Docker per its official README.
- [ ] Bind its web UI to `127.0.0.1` only; access it through an SSH tunnel.
- [ ] Create a `red-team` profile using
      `external/agent-zero/red-team-system-prompt.md`.
- [ ] Set its model to a **non-Anthropic** model (frontier or strong
      open-weight). Gemini 4 can be swapped in later as a one-line change.
- [ ] Mount a **read-only** copy of the repo; give it no other volumes and
      no secrets except its own model key.
- [ ] Limit outbound network to the model API if you can (egress firewall
      or proxy). Agent Zero has root inside its container; the container
      boundary is your safety line.
- [ ] Wrap it with a small worker that claims `red-team` tasks via
      `bridge.py claim red-team` and posts replies via `bridge.py reply`.

## 5. Pilot engagement (the first real test)
- [ ] Queue the example task:
      `python3 bridge/bridge.py send bridge/examples/red-team-task.json`
- [ ] Agent Zero critiques the Phase 1 design itself.
- [ ] In parallel, ask the Chair to run a real engagement on one project
      (suggested: a read-only review of the trading agent's risk controls,
      with the Quant & Risk Officer, Evaluator and Red Team).
- [ ] Scribe writes both to `council/decision-log/`.
- [ ] Evaluator writes the first scorecard baseline to
      `council/scorecard/`.

## 6. Exit criteria for Phase 2
Move on only when, after ~4 weeks:
- [ ] At least 5 engagements logged with dissent recorded.
- [ ] The Red Team changed or sharpened at least one recommendation.
- [ ] No security incident; the bridge rejected every forbidden action in
      the Red Team's own probing.
- [ ] Costs per engagement are known and acceptable.

**Phase 2:** OpenHands (Lead Engineer), Goose (Toolsmith).
**Phase 3:** CrewAI panels, OpenClaw Field Scout (probation), optional Gemini 4.

---

### Alternative: Chair on your laptop, agents on the host
If you prefer running the Chair locally, keep the same repo on both
machines and sync only `council/inbox`, `council/outbox` and logs through
git (commit + push after each send/reply; Hermes pulls on its schedule).
For this, delete the `council/inbox/*/` and `council/outbox/*/` lines from
`.gitignore` so the mailboxes are tracked.
Slower, but every message is in git history — a useful audit trail.

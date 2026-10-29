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
Runs in Docker (official image `nousresearch/hermes-agent`), data in
`~/council/hermes-data` (mounted at `/opt/data`), the same sanitized
read-only snapshot as Agent Zero at `/council`. **No mailbox access in
Phase 1** (decision log 2026-10-28).
- [ ] Separate OpenRouter key for Hermes with its own low monthly limit.
- [ ] Telegram bot from @BotFather; your numeric user ID from @userinfobot.
- [ ] `external/hermes/SOUL.md` → `~/council/hermes-data/SOUL.md`;
      `external/hermes/skills/council-inbox/` → `~/council/hermes-data/skills/`.
- [ ] Setup wizard (interactive):
      `docker run -it --rm -v ~/council/hermes-data:/opt/data nousresearch/hermes-agent setup`
- [ ] In `~/council/hermes-data/.env`: `TELEGRAM_ALLOWED_USERS=<your ID only>`.
- [ ] Gateway, localhost-only API, read-only snapshot:
      `docker run -d --name hermes --restart unless-stopped -v ~/council/hermes-data:/opt/data -v ~/council/repo-snapshot:/council:ro -p 127.0.0.1:8642:8642 nousresearch/hermes-agent gateway run`
- [ ] Keep Hermes' approval prompts on for commands with side effects.
- [ ] Scheduled jobs (ask Hermes on Telegram): daily revisit-date check,
      Monday weekly digest.
- [ ] Check: message the bot "Which council decisions are awaiting my
      approval?" — it should name the 2026-10-28 Red Team review.

## 4. Agent Zero — Red Team & Lab
- [ ] Run Agent Zero in Docker per its official README.
- [ ] Bind its web UI to `127.0.0.1` only; access it through an SSH tunnel.
- [ ] Create a `red-team` profile using
      `external/agent-zero/red-team-system-prompt.md`.
- [ ] Set its model to a **non-Anthropic** model (frontier or strong
      open-weight). Gemini 4 can be swapped in later as a one-line change.
- [ ] Mount a **sanitized, read-only snapshot** of the repo (e.g.
      `~/council/repo-snapshot` → `/council:ro`) built with
      `bridge/make_snapshot.sh` — an **allowlist** of reference files plus
      a denylist check that refuses mailboxes, replies, ID reservations and
      secrets even if they are tracked in git. Add task-specific files as
      extra arguments. Give the container no other volumes and no secrets
      except its own model key.
- [ ] Keep every `.env` / secret **outside** any folder that is mounted into
      an agent container.
- [ ] Limit outbound network to the model API if you can (egress firewall
      or proxy). Agent Zero has root inside its container; the container
      boundary is your safety line.
- [ ] **Agent Zero never touches the mailbox.** A trusted *host-side*
      broker claims `red-team` tasks, sends only the task text to Agent
      Zero, and posts the reply with `bridge.py reply`. Do not make the
      repo writable to Agent Zero to "make the worker work".
      *Phase 1:* the broker is manual and **serialized** (one task at a
      time) — the Chair writes the brief with its task ID, it is pasted into
      a new Agent Zero chat, and the Chair reads the answer from Agent Zero's
      chat file in `~/council/agent-zero-data/chats/` (host side, read-only
      for the Chair) and records it with `bridge.py reply`.
      *Phase 2:* automate the broker against Agent Zero's authenticated
      External API, running as its own OS user.

### 4b. Auditor (Gemini) — same Agent Zero container, own profile
Added 2026-10-28. No new container, key or mount: the Auditor is a second
Agent Zero profile with its own model preset.
- [ ] Profile: `~/council/agent-zero-data/agents/auditor/` with `agent.yaml`
      and `prompts/agent.system.main.specifics.md` (copy of
      `external/agent-zero/auditor-system-prompt.md`).
- [ ] Preset "Gemini" in `~/council/agent-zero-data/plugins/_model_config/presets.yaml`:
      chat `openrouter / google/gemini-4-argon` (ctx 1,000,000), utility
      `openrouter / google/gemini-3.8-flash`, embedding unchanged.
- [ ] Per chat, pick profile **Auditor** and preset **Gemini** in the chips
      under the input box. The default profile stays `red-team` on GPT;
      never run the Red Team on the Gemini or Power (Claude) presets.
- [ ] Check: ask it to name its model; it should say Gemini.
- [ ] Spend: long-context audits are the expensive calls; keep OpenRouter's
      key limit as the cap.

> Red Team review 2026-10-28 (decision log): the bridge's forbidden-action
> filter is a **tripwire for honest mistakes, not a security boundary** —
> any wording can be paraphrased. What actually prevents harm is that no
> seat has the credentials, tools or mounts to trade, pay, publish,
> message or delete.

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
- [ ] No security incident. In the Red Team's own probing, no seat could
      *perform* a forbidden action (capability check), and every probe the
      bridge should catch (malformed, tampered, forged, replayed or
      traversal envelopes) was rejected — see the regression tests.
- [ ] Costs per engagement are known and acceptable.

**Phase 2:** OpenHands (Lead Engineer), Goose (Toolsmith).
**Phase 3:** CrewAI panels, OpenClaw Field Scout (probation), optional Gemini 4.

---

### Alternative: Chair on your laptop, agents on the host
If you prefer running the Chair locally, keep the same repo on both
machines and sync only `council/inbox`, `council/outbox` and logs through
git (commit + push after each send/reply; Hermes pulls on its schedule).
For this, delete the `council/inbox/*/` and `council/outbox/*/` lines from
`.gitignore` so the mailboxes are tracked. Agent snapshots stay safe because
`bridge/make_snapshot.sh` refuses mailbox content even when it is tracked —
never build a snapshot with plain `git archive`.
Slower, but every message is in git history — a useful audit trail.

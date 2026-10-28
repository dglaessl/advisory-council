# External seats

Configuration and role prompts for the council members that are not Claude
subagents. Each one talks to the Chair only through the Bridge
(`bridge/bridge.py`), claiming tasks from `council/inbox/<seat>/` and posting
results to `council/outbox/chair/`.

| Seat | Agent | Phase | What's here |
|---|---|---|---|
| Chief of Staff | Hermes | **1** | `hermes/SOUL.md` (role), `hermes/skills/council-inbox/` (bridge worker skill) |
| Red Team & Lab | Agent Zero | **1** | `agent-zero/red-team-system-prompt.md` |
| Lead Engineer | OpenHands | 2 | `openhands/ROLE.md` |
| Toolsmith | Goose | 2 | `goose/ROLE.md` |
| Strategy Panels | CrewAI | 3 | `crewai/ROLE.md` |
| Field Scout | OpenClaw | 3 (probation) | `openclaw/ROLE.md` |

Phase 1 is deliberately small: Chair + Hermes + Agent Zero + Evaluator +
Quant & Risk Officer. Later phases are added only once the Phase 1
scorecard shows the core is working. See `SETUP.md`.

Install commands change often. Always follow each project's **current
official docs**; the runbook gives the order and the security settings,
not version-pinned commands.

# Personal Advisory Council

A hybrid multi-agent system with Claude as Chair, built to:
1. **Short term:** move Daniel's active projects forward.
2. **Long term:** build expert, monetizable AI skills fused with his domains
   (product development, real estate development, architecture and design,
   longevity, research).

## Layout
```
CLAUDE.md                 Chair prompt (main Claude Code session)
.claude/agents/           Claude seats (subagents)
bridge/                   File-mailbox bridge to external seats + tests
  envelope.schema.json    Task envelope contract
  bridge.py               send / claim / reply / collect / status
external/                 Role prompts and configs for Hermes, Agent Zero,
                          OpenHands, Goose, CrewAI, OpenClaw
council/
  inbox/ outbox/          Bridge mailboxes
  scout-inbox/            OpenClaw drops (untrusted until verified)
  decision-log/           One file per decision (see TEMPLATE.md)
  checkpoints/            Phase checkpoints (see TEMPLATE.md)
  portfolio/              Skills map + portfolio log (AI Tutor)
SETUP.md                  Phase 1 runbook
```

## Quick start
1. Read `SETUP.md` and do sections 0–2.
2. `python3 -m unittest discover -s bridge/tests` — all tests should pass.
3. Start Claude Code in this folder and ask the Chair to convene.

## Safety model in one paragraph
Only Daniel gives instructions. Every external agent is an untrusted
contractor working in its own sandbox. The bridge rejects envelopes that
put the wrong agent in a seat, exceed a seat's permission cap, use R3
without Daniel's approval, or ask for a never-delegated action (trading,
moving money, publishing, messaging anyone but Daniel, deleting data).
Replies from external seats are marked `untrusted` and checked before use.

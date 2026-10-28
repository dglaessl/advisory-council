---
decision_id: 2026-10-28-phase1-red-team-review
date: 2026-10-28
project: council
mode: learning
revisit_on: 2027-01-26
status: proposed
---

# Phase 1 design review by the Red Team (first council pilot)

## Question
Is the Phase 1 council design (CLAUDE.md, SETUP.md, bridge/bridge.py) safe
and workable enough to keep piloting, and what must change first?

## Seats convened
- Red Team & Lab — Agent Zero (profile `red-team`) — openai/gpt-6.1-sol via OpenRouter
  (it delegated an independent second opinion to its own `hacker` subordinate)
- Evaluator role — Chair (Claude Opus), reproducing findings against the code
- Engineer role — Chair, implementing fixes (change < 200 lines)

## Recommendation (Chair)
Proceed with changes: keep piloting with synthetic, read-only tasks; treat the
bridge's keyword filter as a tripwire only; Agent Zero never gets mailbox
access — a trusted host-side broker does.

**Confidence:** high — every testable finding was reproduced independently
before acting on it.

## Key assumptions
- Real protection comes from capabilities (no credentials, tools or writable
  mounts), not from text filtering.
- Phase 1 has no automated workers yet, so the manual broker is acceptable.

## Dissent
- **Red Team:** do not treat Phase 1 as a security boundary until worker
  isolation and mailbox controls are tested end-to-end. Chair agrees; this
  is now an explicit Phase 2 exit criterion.

## Red Team findings
1. **Read-only mount vs. mailbox worker conflict (H/H)** — an in-container
   worker cannot claim/reply on a read-only mount; the tempting workaround
   (make the repo writable) would expose prompts and other seats' mailboxes.
   → Fixed in SETUP.md: host-side broker, sanitized `git archive` snapshot,
   secrets outside any mounted folder. Phase 1 broker is manual.
2. **Forbidden-action filter mistaken for authorization (H/H)** — paraphrases
   ("erase…", "market purchase of BTC"), prose injected into `input_context`,
   null identity fields and tampered mailbox files were all accepted.
   → Fixed: broader patterns, scan constraints/done_when too, input_context
   restricted to references, null/type checks, re-validation on claim with
   quarantine. Documented in code and SETUP that this is a tripwire, not a
   boundary. Exit criterion reworded to a capability check.
3. **Replies not bound to seat/task (H/M)** — same task ID across seats let a
   second reply silently overwrite the first (Chair reproduced: the Red Team's
   dissent was replaced by a forged reply); reply task_id allowed path
   traversal.
   → Fixed: task IDs unique across seats, replies keyed `<task_id>__<seat>`,
   written once, task_id validated (blocks traversal), claimed task moved to
   `done/`.
   **Not addressed yet:** OS-level authentication of workers (separate users
   per seat). Deferred to Phase 2 with the automated broker.

## Evidence
- Chair reproduction script (2026-10-28): paraphrase, context injection and
  null identity ACCEPTED; cross-seat reply overwrote dissent.
- `bridge/tests/test_bridge.py`: 7 new regression tests (`test_rt_*`);
  17/17 passing after fixes.
- Agent Zero chat `TCSGyPJt` ("Council Security Audit").

## Risks and mitigations
- Keyword tripwire may block a legitimate task that quotes an attack (e.g. a
  Red Team brief) → put quoted material in a referenced file, not the envelope.
- Snapshot goes stale → refresh with `git archive` before each Red Team task.

## What would change our mind
- An automated broker that can be shown to enforce seat identity at the OS
  level would let us relax the manual step.

## Daniel's decision
<pending>

## Hindsight (fill in on revisit date)
**Outcome:**
**Lesson:**

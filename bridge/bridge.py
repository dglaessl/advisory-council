#!/usr/bin/env python3
"""Council Bridge — file-mailbox transport between the Chair and external seats.

Standard library only. Layout (relative to the repo root):

    council/inbox/<seat>/<task_id>.json      tasks waiting for a seat
    council/inbox/<seat>/claimed/            tasks a seat has picked up
    council/outbox/<seat>/<task_id>.json     replies from a seat
    council/scout-inbox/                     raw OpenClaw findings (untrusted)

Usage:
    python bridge/bridge.py send task.json          # validate + drop in inbox
    python bridge/bridge.py claim <seat>            # oldest pending task -> stdout
    python bridge/bridge.py reply <seat> reply.json # seat posts its result
    python bridge/bridge.py collect chair           # list replies for the Chair
    python bridge/bridge.py status                  # counts per seat

Swap to Redis later by replacing the four I/O functions; the envelope and
the policy checks stay the same.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("COUNCIL_ROOT", Path(__file__).resolve().parent.parent))
INBOX = ROOT / "council" / "inbox"
OUTBOX = ROOT / "council" / "outbox"

# Which agent may sit in which seat, and the highest permission it may get.
SEATS = {
    "chief-of-staff":   {"agent": "hermes",     "max_perm": "R2"},
    "lead-engineer":    {"agent": "openhands",  "max_perm": "R2"},
    "toolsmith":        {"agent": "goose",      "max_perm": "R3"},
    "red-team":         {"agent": "agent-zero", "max_perm": "R2"},
    "venture-crew":     {"agent": "crewai",     "max_perm": "R1"},
    "hospitality-crew": {"agent": "crewai",     "max_perm": "R1"},
    "career-crew":      {"agent": "crewai",     "max_perm": "R1"},
    "field-scout":      {"agent": "openclaw",   "max_perm": "R0"},
}
PERM_ORDER = ["R0", "R1", "R2", "R3"]
REQUIRED = [
    "task_id", "target_seat", "agent", "objective", "input_context",
    "constraints", "permission_level", "expected_output", "done_when",
    "independent_draft", "reply_to",
]
OPTIONAL = {"created_at", "approved_by_daniel"}
TASK_ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]{1,60}-\d{2}$")
REPLY_TO_RE = re.compile(r"^council/outbox/[a-z-]+/$")

# Actions no seat may ever be asked to do (CLAUDE.md section 2).
FORBIDDEN_PATTERNS = [
    r"\bplace[_ ]?(an? )?(crypto|equity|option)?[_ ]?order", r"\bcancel[_ ]?\w*[_ ]?order",
    r"\b(buy|sell) (btc|eth|bitcoin|crypto|shares?|stock)", r"\btransfer (funds|money)",
    r"\bwire\b", r"\bsend (an? )?(email|message|dm) to (?!daniel)",
    r"\bpublish (the )?listing", r"\bchange (the )?(airbnb )?price",
    r"\bdelete (all|the) ", r"\brm -rf\b",
]


class EnvelopeError(ValueError):
    pass


def validate(env: dict) -> None:
    """Raise EnvelopeError listing every problem found."""
    errs: list[str] = []
    if not isinstance(env, dict):
        raise EnvelopeError("envelope must be a JSON object")
    missing = [k for k in REQUIRED if k not in env]
    if missing:
        errs.append(f"missing fields: {', '.join(missing)}")
    extra = set(env) - set(REQUIRED) - OPTIONAL
    if extra:
        errs.append(f"unknown fields: {', '.join(sorted(extra))}")

    tid = env.get("task_id")
    if tid is not None and (not isinstance(tid, str) or not TASK_ID_RE.match(tid)):
        errs.append("task_id must look like YYYY-MM-DD-<slug>-NN")

    seat = env.get("target_seat")
    if seat is not None and seat not in SEATS:
        errs.append(f"unknown target_seat '{seat}'")
    elif seat is not None:
        if env.get("agent") != SEATS[seat]["agent"]:
            errs.append(f"seat '{seat}' must be served by '{SEATS[seat]['agent']}'")
        perm = env.get("permission_level")
        if perm not in PERM_ORDER:
            errs.append("permission_level must be R0-R3")
        elif PERM_ORDER.index(perm) > PERM_ORDER.index(SEATS[seat]["max_perm"]):
            errs.append(f"seat '{seat}' is capped at {SEATS[seat]['max_perm']}, got {perm}")
        elif perm == "R3" and env.get("approved_by_daniel") is not True:
            errs.append("R3 tasks need approved_by_daniel: true")

    for key in ("objective", "expected_output"):
        if key in env and (not isinstance(env[key], str) or len(env[key].strip()) < 5):
            errs.append(f"{key} must be a non-trivial string")
    for key in ("input_context", "constraints", "done_when"):
        if key in env and (not isinstance(env[key], list)
                           or not all(isinstance(x, str) for x in env[key])):
            errs.append(f"{key} must be a list of strings")
    if isinstance(env.get("done_when"), list) and not env["done_when"]:
        errs.append("done_when needs at least one acceptance criterion")
    if "independent_draft" in env and not isinstance(env["independent_draft"], bool):
        errs.append("independent_draft must be true/false")
    rt = env.get("reply_to")
    if rt is not None and (not isinstance(rt, str) or not REPLY_TO_RE.match(rt)):
        errs.append("reply_to must be council/outbox/<seat>/")

    text = " ".join(str(env.get(k, "")) for k in ("objective", "expected_output")).lower()
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, text):
            errs.append(f"objective asks for a never-delegated action (matched '{pat}')")
            break

    if errs:
        raise EnvelopeError("; ".join(errs))


def _write_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    os.replace(tmp, path)


def send(env: dict) -> Path:
    validate(env)
    env = {**env, "created_at": env.get("created_at")
           or datetime.now(timezone.utc).isoformat(timespec="seconds")}
    path = INBOX / env["target_seat"] / f"{env['task_id']}.json"
    if path.exists() or (path.parent / "claimed" / path.name).exists():
        raise EnvelopeError(f"task {env['task_id']} already exists for {env['target_seat']}")
    _write_atomic(path, env)
    return path


def claim(seat: str) -> dict | None:
    if seat not in SEATS:
        raise EnvelopeError(f"unknown seat '{seat}'")
    box = INBOX / seat
    pending = sorted(box.glob("*.json")) if box.exists() else []
    if not pending:
        return None
    src = pending[0]
    dst = box / "claimed" / src.name
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.replace(src, dst)  # atomic move = only one worker claims a task
    return json.loads(dst.read_text())


def reply(seat: str, result: dict) -> Path:
    if seat not in SEATS:
        raise EnvelopeError(f"unknown seat '{seat}'")
    for key in ("task_id", "status", "output"):
        if key not in result:
            raise EnvelopeError(f"reply missing '{key}'")
    if result["status"] not in {"done", "failed", "needs_daniel"}:
        raise EnvelopeError("status must be done | failed | needs_daniel")
    claimed = INBOX / seat / "claimed" / f"{result['task_id']}.json"
    if not claimed.exists():
        raise EnvelopeError(f"no claimed task {result['task_id']} for {seat}")
    result = {**result, "seat": seat, "untrusted": True,
              "replied_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    path = OUTBOX / "chair" / f"{result['task_id']}.json"
    _write_atomic(path, result)
    return path


def collect(seat: str = "chair") -> list[dict]:
    box = OUTBOX / seat
    return [json.loads(p.read_text()) for p in sorted(box.glob("*.json"))] if box.exists() else []


def status() -> dict:
    out = {}
    for seat in SEATS:
        box = INBOX / seat
        out[seat] = {
            "pending": len(list(box.glob("*.json"))) if box.exists() else 0,
            "claimed": len(list((box / "claimed").glob("*.json"))) if (box / "claimed").exists() else 0,
        }
    out["replies_for_chair"] = len(collect("chair"))
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, *rest = argv
    try:
        if cmd == "send" and len(rest) == 1:
            print(send(json.loads(Path(rest[0]).read_text())))
        elif cmd == "claim" and len(rest) == 1:
            task = claim(rest[0])
            print(json.dumps(task, indent=2) if task else "no pending tasks")
        elif cmd == "reply" and len(rest) == 2:
            print(reply(rest[0], json.loads(Path(rest[1]).read_text())))
        elif cmd == "collect":
            print(json.dumps(collect(rest[0] if rest else "chair"), indent=2))
        elif cmd == "validate" and len(rest) == 1:
            validate(json.loads(Path(rest[0]).read_text()))
            print("valid")
        elif cmd == "status":
            print(json.dumps(status(), indent=2))
        else:
            print(__doc__)
            return 2
    except (EnvelopeError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

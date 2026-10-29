#!/usr/bin/env python3
"""Council Bridge — file-mailbox transport between the Chair and external seats.

Standard library only. Layout (relative to the repo root):

    council/ids/<task_id>                     task-ID reservations (unique across seats)
    council/inbox/<seat>/<task_id>.json       tasks waiting for a seat
    council/inbox/<seat>/claimed/             tasks a seat has picked up (validated)
    council/inbox/<seat>/rejected/            quarantined tasks (invalid or tampered)
    council/inbox/<seat>/done/                tasks with a final reply
    council/outbox/chair/<task_id>__<seat>.json   replies, one per seat per task
    council/scout-inbox/                      raw OpenClaw findings (untrusted)

Usage:
    python bridge/bridge.py send task.json          # validate + drop in inbox
    python bridge/bridge.py claim <seat>            # oldest valid task -> stdout
    python bridge/bridge.py reply <seat> reply.json # seat posts its result
    python bridge/bridge.py collect chair           # list replies for the Chair
    python bridge/bridge.py status                  # counts per seat

Security model (see decision log 2026-10-28):
- The forbidden-action check is a TRIPWIRE for honest mistakes in the Chair's
  own envelopes. It is not a security boundary; wording can be paraphrased.
  The boundary is that no seat holds the credentials, tools or writable mounts
  to trade, pay, publish, message or delete.
- Only a trusted host-side broker calls this module. Agent containers never
  get the mailbox mounted.
- Every state change happens under one exclusive lock, and no file is ever
  silently overwritten.
"""
from __future__ import annotations

import fcntl
import json
import os
import re
import sys
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(os.environ.get("COUNCIL_ROOT", Path(__file__).resolve().parent.parent))
COUNCIL = ROOT / "council"
INBOX = COUNCIL / "inbox"
OUTBOX = COUNCIL / "outbox"
IDS = COUNCIL / "ids"
LOCKFILE = COUNCIL / ".bridge.lock"
MAX_FILE_BYTES = 256 * 1024

# Which agent may sit in which seat, and the highest permission it may get.
SEATS = {
    "chief-of-staff":   {"agent": "hermes",     "max_perm": "R2"},
    "lead-engineer":    {"agent": "openhands",  "max_perm": "R2"},
    "toolsmith":        {"agent": "goose",      "max_perm": "R3"},
    "red-team":         {"agent": "agent-zero", "max_perm": "R2"},
    "auditor":          {"agent": "agent-zero", "max_perm": "R1"},
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
REPLY_STATUSES = {"done", "failed", "needs_daniel"}
REPLY_REQUIRED = {"task_id", "status", "output"}
REPLY_OPTIONAL = {"notes"}
CHAIR_REPLY_TO = "council/outbox/chair/"

# All patterns are applied with fullmatch: no trailing newline or junk passes.
TASK_ID_RE = re.compile(r"\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]{1,60}-\d{2}")
# input_context holds references, never prose:
#   relative repo path (no '..', not absolute), https URL, or memory:<key>
REL_PATH_RE = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_./-]{0,250}")
URL_RE = re.compile(r"https://[A-Za-z0-9.-]+(/[A-Za-z0-9_./%~+=&?#-]*)?")
MEMORY_RE = re.compile(r"memory:[a-z0-9][a-z0-9_/-]{0,120}")
# Paths a task may never point a seat at (other seats' mail, secrets).
FORBIDDEN_REF_PREFIXES = ("council/inbox", "council/outbox", "council/ids", ".git", ".env")

FORBIDDEN_PATTERNS = [
    r"\bplace[_ ]?(an? )?(crypto|equity|option|market|limit)?[_ ]?order",
    r"\bcancel[_ ]?\w*[_ ]?order", r"\bmarket (purchase|buy|sell)",
    r"\b(buy|sell|purchase) (\w+ )?(btc|eth|bitcoin|crypto|shares?|stocks?|tokens?)",
    r"\btransfer (funds|money|crypto)", r"\bmove (funds|money)", r"\bwire\b",
    r"\bsend (an? )?(email|message|dm|text) to (?!daniel)",
    r"\bpublish (the )?listing", r"\bchange (the )?(airbnb |listing )?prices?",
    r"\b(delete|erase|wipe|purge|destroy) ", r"\brm -rf\b",
    r"\b(change|reset|disable) (the )?(password|2fa|mfa|security|account) ",
    r"\bignore (all|previous|the) (rules|instructions|constraints)",
]
# Negated clauses ("do not delete anything") are restrictions, not requests.
NEGATED_CLAUSE_RE = re.compile(
    r"\b(do not|don't|never|must not|mustn't|should not|without|no)\b[^.;\n]*", re.I)


class EnvelopeError(ValueError):
    pass


def _full(regex: re.Pattern, value: object) -> bool:
    return isinstance(value, str) and regex.fullmatch(value) is not None


def _valid_ref(ref: object) -> bool:
    if not isinstance(ref, str):
        return False
    if _full(URL_RE, ref) or _full(MEMORY_RE, ref):
        return True
    if not _full(REL_PATH_RE, ref):
        return False
    parts = ref.split("/")
    if ".." in parts or "" in parts[:-1]:
        return False
    return not any(ref.startswith(p) for p in FORBIDDEN_REF_PREFIXES)


def _tripwire(text: str) -> str | None:
    text = NEGATED_CLAUSE_RE.sub(" ", text.lower())
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, text):
            return pat
    return None


def validate(env: dict) -> None:
    """Raise EnvelopeError listing every problem found."""
    if not isinstance(env, dict):
        raise EnvelopeError("envelope must be a JSON object")
    errs: list[str] = []
    missing = [k for k in REQUIRED if k not in env]
    if missing:
        errs.append(f"missing fields: {', '.join(missing)}")
    extra = set(env) - set(REQUIRED) - OPTIONAL
    if extra:
        errs.append(f"unknown fields: {', '.join(sorted(extra))}")
    nulls = [k for k in REQUIRED if k in env and env[k] is None]
    if nulls:
        errs.append(f"fields may not be null: {', '.join(nulls)}")

    if "task_id" in env and env["task_id"] is not None and not _full(TASK_ID_RE, env["task_id"]):
        errs.append("task_id must look like YYYY-MM-DD-<slug>-NN")

    seat = env.get("target_seat")
    if seat is not None and (not isinstance(seat, str) or seat not in SEATS):
        errs.append(f"unknown target_seat {seat!r}")
    elif seat is not None:
        if env.get("agent") != SEATS[seat]["agent"]:
            errs.append(f"seat '{seat}' must be served by '{SEATS[seat]['agent']}'")
        perm = env.get("permission_level")
        if not isinstance(perm, str) or perm not in PERM_ORDER:
            errs.append("permission_level must be R0-R3")
        elif PERM_ORDER.index(perm) > PERM_ORDER.index(SEATS[seat]["max_perm"]):
            errs.append(f"seat '{seat}' is capped at {SEATS[seat]['max_perm']}, got {perm}")
        elif perm == "R3" and env.get("approved_by_daniel") is not True:
            errs.append("R3 tasks need approved_by_daniel: true")

    for key in ("objective", "expected_output"):
        v = env.get(key)
        if key in env and (not isinstance(v, str) or len(v.strip()) < 5 or len(v) > 2000):
            errs.append(f"{key} must be a string of 5-2000 characters")
    for key in ("input_context", "constraints", "done_when"):
        v = env.get(key)
        if key in env and (not isinstance(v, list) or len(v) > 50
                           or not all(isinstance(x, str) and len(x) <= 1000 for x in v)):
            errs.append(f"{key} must be a list (max 50) of strings (max 1000 chars)")
    if isinstance(env.get("done_when"), list) and not env["done_when"]:
        errs.append("done_when needs at least one acceptance criterion")
    ctx = env.get("input_context")
    if isinstance(ctx, list) and not all(_valid_ref(x) for x in ctx):
        errs.append("input_context items must be safe references: relative repo paths "
                    "(no '..', not mailboxes/secrets), https URLs, or memory:<key>")
    for key in ("independent_draft", "approved_by_daniel"):
        if key in env and not isinstance(env[key], bool):
            errs.append(f"{key} must be true/false")
    if "reply_to" in env and env["reply_to"] is not None and env["reply_to"] != CHAIR_REPLY_TO:
        errs.append(f"reply_to must be '{CHAIR_REPLY_TO}' (all replies go to the Chair)")

    parts: list[str] = []
    for k in ("objective", "expected_output", "constraints", "done_when"):
        v = env.get(k)
        parts.extend(v if isinstance(v, list) else [v] if isinstance(v, str) else [])
    hit = _tripwire("\n".join(p for p in parts if isinstance(p, str)))
    if hit:
        errs.append(f"envelope asks for a never-delegated action (matched '{hit}')")

    if errs:
        raise EnvelopeError("; ".join(errs))


def validate_reply(result: object) -> dict:
    if not isinstance(result, dict):
        raise EnvelopeError("reply must be a JSON object")
    missing = REPLY_REQUIRED - set(result)
    if missing:
        raise EnvelopeError(f"reply missing: {', '.join(sorted(missing))}")
    extra = set(result) - REPLY_REQUIRED - REPLY_OPTIONAL
    if extra:
        raise EnvelopeError(f"reply has unknown fields: {', '.join(sorted(extra))}")
    if not _full(TASK_ID_RE, result["task_id"]):  # also blocks path traversal
        raise EnvelopeError("task_id must look like YYYY-MM-DD-<slug>-NN")
    if not isinstance(result["status"], str) or result["status"] not in REPLY_STATUSES:
        raise EnvelopeError("status must be done | failed | needs_daniel")
    out = result["output"]
    if not isinstance(out, str) or not out.strip() or len(out) > 100_000:
        raise EnvelopeError("output must be a non-empty string (max 100k chars)")
    if "notes" in result and not (isinstance(result["notes"], str) and len(result["notes"]) <= 5000):
        raise EnvelopeError("notes must be a string (max 5000 chars)")
    return result


# ---------- file I/O: one lock, no silent overwrites ----------

@contextmanager
def _locked():
    COUNCIL.mkdir(parents=True, exist_ok=True)
    with open(LOCKFILE, "a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def _publish_new(path: Path, data: dict) -> None:
    """Write data to path; fail if path already exists (never overwrite)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / f".{path.name}.{uuid.uuid4().hex}.tmp"
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    try:
        os.link(tmp, path)  # atomic, and fails with FileExistsError if taken
    finally:
        tmp.unlink(missing_ok=True)


def _move_new(src: Path, dst: Path) -> None:
    """Move src to dst; fail if dst already exists (never overwrite)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.link(src, dst)
    src.unlink()


def _read_json(path: Path) -> dict:
    if not path.is_file() or path.is_symlink():
        raise EnvelopeError(f"{path.name} is not a regular file")
    if path.stat().st_size > MAX_FILE_BYTES:
        raise EnvelopeError(f"{path.name} is larger than {MAX_FILE_BYTES} bytes")
    try:
        return json.loads(path.read_bytes().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise EnvelopeError(f"{path.name} is not valid UTF-8 JSON: {e}") from None


def _check_seat(seat: object) -> str:
    if not isinstance(seat, str) or seat not in SEATS:
        raise EnvelopeError(f"unknown seat {seat!r}")
    return seat


def send(env: dict) -> Path:
    validate(env)
    env = {**env, "created_at": env.get("created_at")
           or datetime.now(timezone.utc).isoformat(timespec="seconds")}
    with _locked():
        IDS.mkdir(parents=True, exist_ok=True)
        try:  # reserve the ID across ALL seats; retries use the next -NN
            fd = os.open(IDS / env["task_id"], os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
        except FileExistsError:
            raise EnvelopeError(f"task {env['task_id']} already exists; "
                                "resend as a new attempt (-NN + 1)") from None
        path = INBOX / env["target_seat"] / f"{env['task_id']}.json"
        _publish_new(path, env)
    return path


def claim(seat: str) -> dict | None:
    """Claim the oldest valid task. Invalid or tampered files are quarantined."""
    seat = _check_seat(seat)
    box = INBOX / seat
    with _locked():
        for src in (sorted(box.glob("*.json")) if box.exists() else []):
            try:
                env = _read_json(src)
                validate(env)
                if env["target_seat"] != seat or f"{env['task_id']}.json" != src.name:
                    raise EnvelopeError("envelope does not match its mailbox")
                _move_new(src, box / "claimed" / src.name)
                return env
            except FileExistsError:
                reason = "a task with this name is already claimed (replay)"
            except EnvelopeError as e:
                reason = str(e)
            q = box / "rejected" / f"{src.stem}.{uuid.uuid4().hex[:8]}.json"
            _move_new(src, q)
            print(f"warning: quarantined {src.name}: {reason}", file=sys.stderr)
    return None


def reply(seat: str, result: dict) -> Path:
    seat = _check_seat(seat)
    result = validate_reply(result)
    task_id = result["task_id"]
    with _locked():
        claimed = INBOX / seat / "claimed" / f"{task_id}.json"
        done = INBOX / seat / "done" / f"{task_id}.json"
        path = OUTBOX / "chair" / f"{task_id}__{seat}.json"
        if path.exists():
            prior = _read_json(path)
            same = all(prior.get(k) == result.get(k) for k in ("status", "output", "notes"))
            if same and claimed.exists() and not done.exists():
                _move_new(claimed, done)  # recover an interrupted completion
                return path
            raise EnvelopeError(f"{seat} already replied to {task_id}; replies are final")
        env = _read_json(claimed) if claimed.exists() else None
        if env is None:
            raise EnvelopeError(f"no claimed task {task_id} for {seat}")
        validate(env)  # bind the reply to a still-valid claimed task
        record = {**result, "seat": seat, "untrusted": True,
                  "replied_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        _publish_new(path, record)
        _move_new(claimed, done)
    return path


def collect(seat: str = "chair") -> list[dict]:
    box = OUTBOX / seat
    return [_read_json(p) for p in sorted(box.glob("*.json"))] if box.exists() else []


def status() -> dict:
    out = {}
    for seat in SEATS:
        box = INBOX / seat
        out[seat] = {k: (len(list((box if k == "pending" else box / k).glob("*.json")))
                         if (box if k == "pending" else box / k).exists() else 0)
                     for k in ("pending", "claimed", "rejected", "done")}
    out["replies_for_chair"] = len(collect("chair"))
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, *rest = argv
    try:
        if cmd == "send" and len(rest) == 1:
            print(send(_read_json(Path(rest[0]))))
        elif cmd == "claim" and len(rest) == 1:
            task = claim(rest[0])
            print(json.dumps(task, indent=2) if task else "no pending tasks")
        elif cmd == "reply" and len(rest) == 2:
            print(reply(rest[0], _read_json(Path(rest[1]))))
        elif cmd == "collect":
            print(json.dumps(collect(rest[0] if rest else "chair"), indent=2))
        elif cmd == "validate" and len(rest) == 1:
            validate(_read_json(Path(rest[0])))
            print("valid")
        elif cmd == "status":
            print(json.dumps(status(), indent=2))
        else:
            print(__doc__)
            return 2
    except (EnvelopeError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

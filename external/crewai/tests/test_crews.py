"""Tests for the CrewAI kit: envelope checks, context loading, model guard, dry run.

Run from external/crewai:  python3 -m unittest discover -s tests -v
The dry-run tests are skipped if crewai is not installed.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent
sys.path.insert(0, str(KIT / "crews"))
import _common as C  # noqa: E402

EXAMPLES = KIT / "examples"
HAVE_CREWAI = importlib.util.find_spec("crewai") is not None


def example(name: str) -> dict:
    return json.loads((EXAMPLES / f"{name}-envelope.json").read_text())


class EnvelopeTests(unittest.TestCase):
    def test_bridge_is_imported_from_repo(self):
        self.assertIsNotNone(C.BRIDGE, "bridge.py should be importable from the repo checkout")

    def test_examples_valid_for_their_seat(self):
        for crew in ("venture", "hospitality", "career"):
            self.assertEqual(C.validate_envelope(example(crew), f"{crew}-crew"), "bridge.py")

    def test_wrong_seat_rejected(self):
        with self.assertRaises(C.EnvelopeError):
            C.validate_envelope(example("venture"), "career-crew")

    def test_bad_envelopes_rejected_by_bridge_and_mirror(self):
        good = example("hospitality")
        bad_cases = {
            "perm_r2": {"permission_level": "R2"},
            "wrong_agent": {"agent": "goose"},
            "traversal": {"input_context": ["../secrets.txt"]},
            "mailbox_ref": {"input_context": ["council/outbox/chair/x.json"]},
            "reply_to": {"reply_to": "council/outbox/red-team/"},
            "forbidden": {"objective": "Publish the listing with new photos tonight"},
            "price": {"constraints": ["change the Airbnb price to 300 EUR"]},
            "extra": {"secret": "x"},
            "task_id": {"task_id": "2026-10-29-bad"},
        }
        for name, patch in bad_cases.items():
            env = {**copy.deepcopy(good), **patch}
            with self.subTest(case=name):
                with self.assertRaises(C.EnvelopeError):
                    C.validate_envelope(env, "hospitality-crew")
                with self.assertRaises(C.EnvelopeError):
                    C._mirror_validate(env)

    def test_mirror_accepts_examples(self):
        for crew in ("venture", "hospitality", "career"):
            C._mirror_validate(example(crew))

    def test_negated_restriction_allowed(self):
        env = example("hospitality")
        env["constraints"] = ["do not change prices or publish the listing"]
        C.validate_envelope(env, "hospitality-crew")
        C._mirror_validate(env)


class ContextTests(unittest.TestCase):
    def test_loads_file_and_refuses_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "in"
            (root / "notes").mkdir(parents=True)
            (root / "notes" / "a.md").write_text("hello")
            outside = Path(d) / "secret.txt"
            outside.write_text("TOPSECRET")
            (root / "link.md").symlink_to(outside)
            env = {"input_context": ["notes/a.md", "link.md", "missing.md",
                                     "https://example.org/x", "memory:foo"]}
            text = C.load_context(env, root)
            self.assertIn("hello", text)
            self.assertNotIn("TOPSECRET", text)
            self.assertIn("[refused", text)
            self.assertIn("[file not provided", text)
            self.assertIn("not fetched", text)
            self.assertIn("information only", text)


class ModelGuardTests(unittest.TestCase):
    def test_rejects_anthropic_and_non_openrouter(self):
        for bad in ("openrouter/anthropic/claude-x", "anthropic/claude-x", "openai/gpt-6-luna",
                    "openrouter/some/claude-distill"):
            with self.subTest(model=bad), self.assertRaises(SystemExit):
                C.check_model_name(bad)
        C.check_model_name(C.DEFAULT_MODEL)

    def test_reply_validation(self):
        C.validate_reply({"task_id": "2026-10-29-x-smoke-01", "status": "done", "output": "{}"})
        with self.assertRaises(C.EnvelopeError):
            C.validate_reply({"task_id": "../x", "status": "done", "output": "{}"})


@unittest.skipUnless(HAVE_CREWAI, "crewai not installed")
class DryRunTests(unittest.TestCase):
    def test_each_crew_dry_run(self):
        env = {k: v for k, v in os.environ.items() if k != "OPENROUTER_API_KEY"}
        for crew in ("venture", "hospitality", "career"):
            with self.subTest(crew=crew), tempfile.TemporaryDirectory() as out:
                p = subprocess.run([sys.executable, str(KIT / "crews" / f"{crew}.py"),
                                    str(EXAMPLES / f"{crew}-envelope.json"), "--out", out,
                                    "--dry-run"], capture_output=True, text=True, env=env,
                                   timeout=300)
                self.assertEqual(p.returncode, 0, p.stderr[-2000:])
                d = Path(out) / f"{example(crew)['task_id']}__{crew}-crew"
                reply = json.loads((d / "reply.json").read_text())
                C.validate_reply(reply)
                result = json.loads(reply["output"])
                self.assertIn("employment_conflict_check", result)
                self.assertIn(result["employment_conflict_check"]["status"],
                              ("clear", "needs_review", "conflict"))
                self.assertTrue((d / "memo.md").read_text().startswith(f"# {crew}-crew"))
                if crew == "hospitality":
                    self.assertTrue(all(p["needs_daniel_approval"] for p in result["proposals"]))

    def test_real_run_without_key_fails_cleanly(self):
        env = {k: v for k, v in os.environ.items() if k != "OPENROUTER_API_KEY"}
        with tempfile.TemporaryDirectory() as out:
            p = subprocess.run([sys.executable, str(KIT / "crews" / "venture.py"),
                                str(EXAMPLES / "venture-envelope.json"), "--out", out],
                               capture_output=True, text=True, env=env, timeout=120)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("OPENROUTER_API_KEY", p.stderr)


if __name__ == "__main__":
    unittest.main()

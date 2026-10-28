import importlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def good_env(**over):
    env = {
        "task_id": "2026-10-28-red-team-pilot-01",
        "target_seat": "red-team",
        "agent": "agent-zero",
        "objective": "Critique the draft recommendation on trading-agent alerting",
        "input_context": ["council/drafts/alerting.md"],
        "constraints": ["no network calls outside the container"],
        "permission_level": "R1",
        "expected_output": "Markdown critique with ranked risks",
        "done_when": ["at least three concrete failure modes named"],
        "independent_draft": False,
        "reply_to": "council/outbox/chair/",
    }
    env.update(over)
    return env


class BridgeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["COUNCIL_ROOT"] = self.tmp.name
        sys.path.insert(0, str(HERE.parent))
        import bridge
        self.b = importlib.reload(bridge)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("COUNCIL_ROOT", None)

    def test_valid_roundtrip(self):
        path = self.b.send(good_env())
        self.assertTrue(path.exists())
        task = self.b.claim("red-team")
        self.assertEqual(task["task_id"], "2026-10-28-red-team-pilot-01")
        self.assertIsNone(self.b.claim("red-team"))  # claimed only once
        out = self.b.reply("red-team", {"task_id": task["task_id"], "status": "done",
                                        "output": "three risks ..."})
        self.assertTrue(out.exists())
        replies = self.b.collect("chair")
        self.assertEqual(len(replies), 1)
        self.assertTrue(replies[0]["untrusted"])

    def test_example_task_is_valid(self):
        env = json.loads((HERE.parent / "examples" / "red-team-task.json").read_text())
        self.b.validate(env)

    def test_wrong_agent_for_seat(self):
        with self.assertRaises(self.b.EnvelopeError):
            self.b.validate(good_env(agent="openclaw"))

    def test_permission_cap(self):
        with self.assertRaises(self.b.EnvelopeError):
            self.b.validate(good_env(target_seat="field-scout", agent="openclaw",
                                     permission_level="R2"))

    def test_r3_needs_approval(self):
        env = good_env(target_seat="toolsmith", agent="goose", permission_level="R3")
        with self.assertRaises(self.b.EnvelopeError):
            self.b.validate(env)
        env["approved_by_daniel"] = True
        self.b.validate(env)

    def test_forbidden_actions_blocked(self):
        for obj in ["Place a crypto order for 0.1 BTC now",
                    "Buy BTC when RSI drops below 30",
                    "Send an email to the property agency about pricing",
                    "Change the Airbnb price for December"]:
            with self.subTest(obj=obj), self.assertRaises(self.b.EnvelopeError):
                self.b.validate(good_env(objective=obj))

    def test_message_to_daniel_allowed(self):
        self.b.validate(good_env(objective="Send a message to Daniel with the weekly digest",
                                 target_seat="chief-of-staff", agent="hermes"))

    def test_missing_and_unknown_fields(self):
        env = good_env()
        del env["done_when"]
        env["sneaky"] = 1
        with self.assertRaises(self.b.EnvelopeError) as cm:
            self.b.validate(env)
        self.assertIn("done_when", str(cm.exception))
        self.assertIn("sneaky", str(cm.exception))

    def test_duplicate_task_rejected(self):
        self.b.send(good_env())
        with self.assertRaises(self.b.EnvelopeError):
            self.b.send(good_env())

    def test_reply_requires_claim(self):
        with self.assertRaises(self.b.EnvelopeError):
            self.b.reply("red-team", {"task_id": "2026-10-28-nope-task-01",
                                      "status": "done", "output": "x"})


if __name__ == "__main__":
    unittest.main()

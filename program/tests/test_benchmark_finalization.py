"""Finalization stops before rendering when prerequisites fail."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.equal_budget_benchmark import atomic_json
from scripts.finish_benchmark import finish


class Finalization(unittest.TestCase):
    def test_forced_build_and_non_utf8_layout_log(self):
        for log_bytes, succeeds in ((b"ordinary log with byte \xf3", True), (b"Overfull \\hbox \xf3", False)):
            with self.subTest(succeeds=succeeds), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                directory = root / "program/data/experiment"
                (directory / "replacements").mkdir(parents=True)
                atomic_json(directory / "replacements/status.json", dict(state="complete"))
                (root / "main.log").write_bytes(log_bytes)
                (root / "main.pdf").write_bytes(b"mock PDF")
                with patch("scripts.finish_benchmark.__file__", str(root / "program/scripts/finish_benchmark.py")), \
                     patch("scripts.finish_benchmark.subprocess.run") as run:
                    if succeeds:
                        finish(directory)
                    else:
                        with self.assertRaisesRegex(ValueError, "overfull"):
                            finish(directory)
                    commands = [call.args[0] for call in run.call_args_list]
                    self.assertEqual(len(commands), 5)
                    self.assertIn("-g", commands[3])
                    self.assertEqual(commands[3][0], "latexmk")
                    self.assertFalse(any(command[0] == "git" for command in commands))
                state = json.loads((directory / "finalization_status.json").read_text())
                self.assertEqual(state["state"], "complete" if succeeds else "failed")

    def test_incomplete_run_cannot_render(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            (directory / "replacements").mkdir()
            atomic_json(directory / "replacements/status.json", dict(state="running"))
            with patch("scripts.finish_benchmark.subprocess.run") as run:
                with self.assertRaises(TimeoutError):
                    finish(directory)
                run.assert_not_called()
            self.assertEqual(json.loads((directory / "finalization_status.json").read_text())["state"], "failed")

    def test_failed_validation_stops_before_tables(self):
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            (directory / "replacements").mkdir()
            atomic_json(directory / "replacements/status.json", dict(state="complete"))
            with patch("scripts.finish_benchmark.subprocess.run",
                       side_effect=subprocess.CalledProcessError(1, ["validator"])) as run:
                with self.assertRaises(subprocess.CalledProcessError):
                    finish(directory)
                self.assertEqual(run.call_count, 1)
                self.assertIn("scripts/validate_benchmark.py", run.call_args.args[0])
            state = json.loads((directory / "finalization_status.json").read_text())
            self.assertEqual(state["state"], "failed")
            self.assertEqual(state["stage"], "independent witness audit")

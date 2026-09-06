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

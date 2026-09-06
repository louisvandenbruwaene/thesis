"""Protocol checks without running the 16-hour experiment."""

import math
import tempfile
from pathlib import Path
import unittest
from scripts.equal_budget_benchmark import schedule, atomic_json, VARIANTS
from scripts.benchmark_report import timing_issues


class EqualBudgetProtocol(unittest.TestCase):
    def test_equal_allocations_and_unique_trials(self):
        trials = schedule(3600)
        self.assertEqual(len(trials), 384)
        self.assertEqual(len({t["id"] for t in trials}), len(trials))
        for variant in range(16):
            group = [t for t in trials if t["variant"] == variant]
            self.assertEqual(len(group), 24)
            self.assertEqual(sum(t["requested_seconds"] for t in group), 3600)
            self.assertTrue(all(t["requested_seconds"] == 150 for t in group))
            self.assertEqual(len({(t["n"], t["m"], t["seed"]) for t in group}), 24)
        for offset in range(0, len(trials), 16):
            self.assertEqual({t["variant"] for t in trials[offset:offset + 16]}, set(range(16)))
        self.assertEqual(len({tuple(v.items()) for v in VARIANTS}), 16)

    def test_invalid_budgets(self):
        for value in (0, -1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                schedule(value)

    def test_failed_json_write_preserves_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trial.json"
            atomic_json(path, {"value": 3})
            saved = path.read_bytes()
            with self.assertRaises(ValueError):
                atomic_json(path, {"value": math.nan})
            self.assertEqual(path.read_bytes(), saved)
            self.assertEqual(list(Path(directory).iterdir()), [path])

    def test_clock_discrepancy_is_not_equal_budget_evidence(self):
        run = dict(trial=dict(requested_seconds=150), search_elapsed_seconds=90.302,
                   solver_reported_seconds=792.301)
        self.assertEqual(len(timing_issues(run)), 2)
        run.update(search_elapsed_seconds=150.02, solver_reported_seconds=150.03)
        self.assertEqual(timing_issues(run), [])


if __name__ == "__main__":
    unittest.main()

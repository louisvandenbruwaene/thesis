"""Replacement selection, provenance and short end-to-end replay checks."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.benchmark_replacements import prepare, digest, flagged
from scripts.benchmark_report import timing_issues, report
from scripts.equal_budget_benchmark import atomic_json, schedule


class Replacements(unittest.TestCase):
    def test_policy_matches_report(self):
        for elapsed, reported in ((150, 150), (90, 792), (149.5, 150), (160, 160)):
            record = dict(trial=dict(requested_seconds=150),
                          search_elapsed_seconds=elapsed, solver_reported_seconds=reported)
            self.assertEqual(flagged(record), bool(timing_issues(record)))

    def test_frozen_smoke_preserves_originals_and_resumes(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            source = parent / "source"
            source.mkdir()
            (parent / "trials").mkdir()
            paths = [root / "erdos915_unified.py", root / "_erdos_fast.c",
                     root / "scripts" / "equal_budget_benchmark.py"]
            for path in paths:
                shutil.copyfile(path, source / path.name)
            trials = [schedule(0.48)[i] for i in (0, 8, 9)]
            for trial in trials:
                trial.update(n=3, m=3)
            atomic_json(parent / "manifest.json", dict(trials=trials,
                source_sha256={p.name: digest(source / p.name) for p in paths}))
            atomic_json(parent / "status.json", dict(state="complete"))
            for i, trial in enumerate(trials):
                atomic_json(parent / "trials" / (trial["id"] + ".json"), dict(
                    trial=trial, status="validated", value=999-i,
                    search_elapsed_seconds=0.02, search_cpu_seconds=0.01, validation_seconds=0,
                    solver_reported_seconds=3 if i < 2 else 0.02))
            originals = {p: digest(p) for p in (parent / "trials").iterdir()}
            target = prepare(parent)
            manifest = json.loads((target / "manifest.json").read_text())
            self.assertEqual([s["trial"] for s in manifest["selected"]], trials[:2])
            command = [sys.executable, str(target / "source" / "benchmark_replacements.py"),
                       "--resume", str(target)]
            subprocess.run(command, check=True, capture_output=True, text=True)
            saved = {p: digest(p) for p in (target / "trials").iterdir()}
            self.assertEqual(len(saved), 2)
            for path in saved:
                run = json.loads(path.read_text())
                self.assertFalse(flagged(run))
                self.assertLess(run["max_connectivity"], 3)
            subprocess.run(command, check=True, capture_output=True, text=True)
            self.assertEqual(saved, {p: digest(p) for p in saved})
            self.assertEqual(originals, {p: digest(p) for p in originals})
            atomic_json(parent / "comparison_baseline.json", dict(counts={
                f"v{t['variant']:02d}_n{t['n']}_m{t['m']}": 0 for t in trials}))
            report(parent)
            rendered = json.loads((parent / "report.json").read_text())
            self.assertEqual(rendered["timing_qualified"], 3)
            self.assertEqual(rendered["original_timing_flagged"], 2)
            self.assertEqual(rendered["replacements_saved"], 2)
            row = rendered["rows"][0]
            self.assertLess(row["search_max"], row["raw_search_values"][0]["value"])
            self.assertEqual(row["selected_trials"][0]["source"], "replacement")
            with self.assertRaises(FileExistsError):
                prepare(parent)

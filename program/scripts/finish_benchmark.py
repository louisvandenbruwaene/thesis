"""Validate completed replacements, render tables and rebuild the working thesis.

This does not commit or publish. Completion still requires visual review.
"""

import argparse
import fcntl
import json
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.equal_budget_benchmark import atomic_json, digest, now


def finish(directory, wait_seconds=0):
    directory = Path(directory).resolve()
    program = Path(__file__).resolve().parents[1]
    thesis = program.parent
    status = directory / "finalization_status.json"
    with (directory / "finalization.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        stage = "waiting for replacements"
        try:
            deadline = time.monotonic() + wait_seconds
            atomic_json(status, dict(state="waiting", stage=stage, updated_utc=now()))
            while json.loads((directory / "replacements" / "status.json").read_text())["state"] != "complete":
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("Replacements have not completed")
                time.sleep(min(15, remaining))
            commands = [
                ("independent witness audit", [sys.executable, "scripts/validate_benchmark.py", str(directory)], program, 300),
                ("audited tables", [sys.executable, "scripts/benchmark_tables.py", str(directory)], program, 300),
                ("benchmark regression tests", [sys.executable, "-m", "unittest", "tests.test_benchmark_validation",
                 "tests.test_benchmark_tables", "tests.test_benchmark_replacements", "tests.test_equal_budget_benchmark",
                 "tests.test_benchmark_finalization"], program, 300),
                # -g forces a run. A build made while a table file was absent records a
                # lookup that FAILED, not a dependency, so latexmk sees nothing to redo
                # once the render creates it.
                ("manuscript build", ["latexmk", "-pdf", "-g", "-interaction=nonstopmode", "-halt-on-error", "main.tex"], thesis, 300),
                ("reference consistency", ["./check_consistency.sh"], thesis, 60),
            ]
            with (directory / "finalization.log").open("a") as log:
                for stage, command, cwd, timeout in commands:
                    atomic_json(status, dict(state="running", stage=stage, updated_utc=now()))
                    print(f"{now()} {stage}", file=log, flush=True)
                    subprocess.run(command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                                   timeout=timeout, check=True)
            stage = "layout warning check"
            # main.log is not valid UTF-8: it carries an invalid continuation byte 0xf3.
            # Decoding strictly raises, and any locale-sensitive scan of it can match
            # nothing at all, which reads exactly like a clean build.
            if "Overfull" in (thesis / "main.log").read_text(encoding="utf-8", errors="replace"):
                raise ValueError("The manuscript has an overfull box requiring review")
            atomic_json(status, dict(state="complete", stage="ready for visual review", updated_utc=now(),
                                    pdf_sha256=digest(thesis / "main.pdf")))
        except Exception as error:
            atomic_json(status, dict(state="failed", stage=stage, updated_utc=now(), error=str(error)))
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--wait-seconds", type=float, default=0)
    args = parser.parse_args()
    if not 0 <= args.wait_seconds <= 7200:
        parser.error("wait-seconds must be between zero and 7200")
    finish(args.directory, args.wait_seconds)

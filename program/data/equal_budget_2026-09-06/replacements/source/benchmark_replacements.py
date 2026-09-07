"""Repeat timing-flagged trials with the original solver and a monotonic clock.

Original trials are never overwritten. Selection depends only on timing flags.
The replacement runner freezes itself before starting and resumes checkpoints.
"""

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from types import SimpleNamespace


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def flagged(run):
    return (abs(run["search_elapsed_seconds"] - run["solver_reported_seconds"]) > 1
            or run["search_elapsed_seconds"] < run["trial"]["requested_seconds"] - 1)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def original_helpers(parent):
    manifest = read(parent / "manifest.json")
    for name, expected in manifest["source_sha256"].items():
        if digest(parent / "source" / name) != expected:
            raise ValueError(f"Original frozen source changed: {name}")
    return load_module("_original_benchmark_helpers",
                       parent / "source" / "equal_budget_benchmark.py")


def prepare(parent):
    parent = Path(parent).resolve()
    helper = original_helpers(parent)
    if read(parent / "status.json")["state"] != "complete":
        raise ValueError("Original serial experiment must finish first")
    manifest = read(parent / "manifest.json")
    selected = []
    for trial in manifest["trials"]:
        path = parent / "trials" / (trial["id"] + ".json")
        run = read(path)
        if run["trial"] != trial or run["status"] != "validated":
            raise ValueError(f"Invalid original trial: {path}")
        if flagged(run):
            selected.append(dict(trial=trial, original_sha256=digest(path)))
    target = parent / "replacements"
    target.mkdir(exist_ok=False)
    (target / "source").mkdir()
    (target / "trials").mkdir()
    runner = target / "source" / Path(__file__).name
    shutil.copyfile(__file__, runner)
    helper.atomic_json(target / "manifest.json", dict(
        schema=1, created_utc=helper.now(),
        original_manifest_sha256=digest(parent / "manifest.json"),
        runner_sha256=digest(runner), selected=selected,
        selection="All original timing-flagged trials in original schedule order, independent of objective value",
        selection_tolerance_seconds=1,
        source="Original frozen solver and C binary, verified against the original manifest",
        change="Only engine.time.time is rebound to time.monotonic through a module-local proxy",
        clock="Monotonic duration, with platform-specific treatment of suspended time",
        reporting="Use replacement instead of flagged original, never the better of their objectives"))
    return target


def run(target):
    target = Path(target).resolve()
    parent = target.parent
    manifest = read(target / "manifest.json")
    if Path(__file__).resolve().parent != target / "source":
        raise ValueError("Run the frozen replacement runner")
    if digest(__file__) != manifest["runner_sha256"]:
        raise ValueError("Replacement runner changed")
    if digest(parent / "manifest.json") != manifest["original_manifest_sha256"]:
        raise ValueError("Original manifest changed")
    helper = original_helpers(parent)
    for selected in manifest["selected"]:
        original = parent / "trials" / (selected["trial"]["id"] + ".json")
        if digest(original) != selected["original_sha256"]:
            raise ValueError(f"Original checkpoint changed: {original}")
    with (target / "runner.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                    "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
            os.environ[key] = "1"
        engine = load_module("_replacement_frozen_engine", parent / "source" / "erdos915_unified.py")
        engine.time = SimpleNamespace(time=time.monotonic, monotonic=time.monotonic,
                                      perf_counter=time.perf_counter)
        env = helper.environment(engine)
        status_path = target / "status.json"
        if status_path.exists():
            old = read(status_path)
            if old["state"] == "running" and not (target / "trials" / (old["active_trial"]["id"] + ".json")).exists():
                history = target / "interruptions.json"
                entries = read(history) if history.exists() else []
                entries.append(dict(previous_status=old, resumed_utc=helper.now(),
                                    note="Uncheckpointed replacement restarted, prior elapsed time unknown"))
                helper.atomic_json(history, entries)
        for index, selected in enumerate(manifest["selected"]):
            trial = selected["trial"]
            destination = target / "trials" / (trial["id"] + ".json")
            if destination.exists():
                saved = read(destination)
                if saved["trial"] != trial or saved["status"] != "validated" or flagged(saved):
                    raise ValueError(f"Invalid replacement checkpoint: {destination}")
                continue
            started = helper.now()
            helper.atomic_json(status_path, dict(state="running", pid=os.getpid(),
                started_utc=started, completed=index, total=len(manifest["selected"]), active_trial=trial))
            print(f"START {index+1}/{len(manifest['selected'])} {trial['id']}", flush=True)
            start, cpu, calendar = time.monotonic(), time.process_time(), time.time()
            kw = {k: trial[k] for k in ("hypergraph", "simple", "directed", "separation")}
            result = engine.solve(trial["n"], trial["m"], **kw, r=3, kind="forward",
                method="random-greedy" if trial["hypergraph"] else "tabu", exhaustive=False,
                seed=trial["seed"], max_seconds=trial["requested_seconds"])
            elapsed, cpu_elapsed = time.monotonic()-start, time.process_time()-cpu
            calendar_elapsed = time.time()-calendar
            check_start = time.monotonic()
            checker = engine.max_hyper_connectivity if trial["hypergraph"] else engine.max_connectivity
            connectivity = checker(result.witness, vertex_split=trial["separation"] == "vertex")
            if result.witness.edge_count() != result.value or connectivity >= trial["m"]:
                raise ValueError(f"Invalid witness: {trial['id']}")
            if result.bound != "lower" or result.complete:
                raise ValueError("Unaided search unexpectedly claims optimality")
            record = dict(trial=trial, status="validated", started_utc=started, ended_utc=helper.now(),
                original_sha256=selected["original_sha256"], replacement_manifest_sha256=digest(target / "manifest.json"),
                search_elapsed_seconds=elapsed, search_cpu_seconds=cpu_elapsed,
                calendar_elapsed_seconds=calendar_elapsed, solver_reported_seconds=result.seconds,
                validation_seconds=time.monotonic()-check_start, value=result.value,
                bound=result.bound, method=result.method, complete=result.complete,
                max_connectivity=connectivity, witness=helper.encode(result.witness, engine), environment=env)
            helper.atomic_json(destination, record)
            if flagged(record):
                raise ValueError("Replacement timing failed, checkpoint retained for investigation")
            print(f"DONE {trial['id']} value={result.value} duration={elapsed:.3f}s", flush=True)
        helper.atomic_json(status_path, dict(state="complete", ended_utc=helper.now(),
            completed=len(manifest["selected"]), total=len(manifest["selected"])))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--original", type=Path)
    choice.add_argument("--resume", type=Path)
    args = parser.parse_args()
    if args.resume:
        run(args.resume)
    else:
        target = prepare(args.original)
        subprocess.run([sys.executable, str(target / "source" / Path(__file__).name),
                        "--resume", str(target)], check=True)

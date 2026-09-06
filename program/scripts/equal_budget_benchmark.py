"""Checkpointed unaided search with one declared total budget per variant.

Prepare and run from any directory:
  python scripts/equal_budget_benchmark.py --output data/equal_budget_2026-09-06
Resume using the frozen runner printed by that command. No result is promoted
to the thesis automatically. The 16 variants run serially, not concurrently.
"""

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
from importlib.metadata import version, PackageNotFoundError
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time


ORDERS = (6, 8, 10, 12)
THRESHOLDS = (3, 6)
SEEDS = (0, 1000000, 2000000)
VARIANTS = [dict(hypergraph=h, simple=s, directed=d, separation=sep)
            for h in (False, True) for s in (True, False)
            for d in (False, True) for sep in ("edge", "vertex")]


def now():
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path, value):
    path = Path(path)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as out:
        temporary = Path(out.name)
        try:
            json.dump(value, out, indent=2, allow_nan=False)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def schedule(seconds):
    if not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("seconds per variant must be finite and positive")
    budget = seconds / (len(ORDERS) * len(THRESHOLDS) * len(SEEDS))
    trials = []
    for seed in SEEDS:
        for n in ORDERS:
            for m in THRESHOLDS:
                # Rotate ordering between cases to spread temporal effects.
                offset = len(trials) // len(VARIANTS) % len(VARIANTS)
                for j in range(len(VARIANTS)):
                    i = (offset + j) % len(VARIANTS)
                    trials.append(dict(id=f"v{i:02d}_n{n}_m{m}_seed{seed}",
                                       variant=i, n=n, m=m, seed=seed,
                                       requested_seconds=budget, **VARIANTS[i]))
    return trials


def prepare(directory, seconds):
    trials = schedule(seconds)
    directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=False)
    source = directory / "source"
    source.mkdir()
    (directory / "trials").mkdir()
    root = Path(__file__).resolve().parents[1]
    paths = [root / "erdos915_unified.py", root / "_erdos_fast.c", Path(__file__)]
    if (root / "_erdos_fast.so").exists():
        paths.append(root / "_erdos_fast.so")
    for path in paths:
        shutil.copyfile(path, source / path.name)
    manifest = dict(
        schema=1, created_utc=now(), seconds_per_variant=seconds,
        protocol="serial unaided search, three seed streams per (n,m,variant)",
        deadline="cooperative search target, validation and setup measured separately",
        search_clock="time.monotonic, platform-specific treatment of suspended time",
        graph_method="tabu", hypergraph_method="random-greedy",
        hypergraph_uniformity=3, hypergraph_orientation="forward",
        vertex_convention="incidence-1", construction_seeded=False,
        constructions="not read or supplied by this runner",
        seed_note="Matrix restarts increment the initial seed. Hypergraph restarts continue one seeded random stream.",
        source_sha256={p.name: digest(source / p.name) for p in paths},
        trials=trials)
    atomic_json(directory / "manifest.json", manifest)
    return directory


def environment(engine):
    dependencies = {}
    for name in ("numpy", "scipy", "pulp", "networkx", "matplotlib"):
        try:
            dependencies[name] = version(name)
        except PackageNotFoundError:
            dependencies[name] = None
    return dict(python=sys.version, executable=sys.executable,
                platform=platform.platform(), machine=platform.machine(),
                logical_cpus=os.cpu_count(), dependencies=dependencies,
                c_extension_loaded=engine.C_EXTENSION_LOADED,
                thread_limits={k: os.environ.get(k) for k in
                               ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")})


def encode(witness, engine):
    if isinstance(witness, engine.Graph):
        return dict(multiplicity_matrix=witness.mu.tolist())
    edges = ([[sorted(t), sorted(h)] for t, h in
              map(engine._dir_tails_heads, witness.hyperedges)]
             if witness.directed else [sorted(e) for e in witness.hyperedges])
    return dict(hyperedges=edges)


def run(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / "manifest.json").read_text())
    source = directory / "source"
    if Path(__file__).resolve().parent != source:
        raise ValueError("Run the frozen copy in the experiment's source directory")
    for name, expected in manifest["source_sha256"].items():
        if digest(source / name) != expected:
            raise ValueError(f"Frozen source changed: {name}")
    # A second runner must not repeat or overwrite a trial in this experiment.
    with (directory / "runner.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                    "VECLIB_MAXIMUM_THREADS"):
            os.environ[key] = "1"
        import erdos915_unified as engine
        env = environment(engine)
        status_path = directory / "status.json"
        if status_path.exists():
            previous = json.loads(status_path.read_text())
            if previous["state"] == "running":
                checkpoint = directory / "trials" / (previous["active_trial"]["id"] + ".json")
                if not checkpoint.exists():
                    history = directory / "interruptions.json"
                    interruptions = json.loads(history.read_text()) if history.exists() else []
                    interruptions.append(dict(previous_status=previous, resumed_utc=now(),
                                              note="Uncheckpointed trial restarted. Prior elapsed time is unknown."))
                    atomic_json(history, interruptions)
        completed = 0
        for trial in manifest["trials"]:
            destination = directory / "trials" / (trial["id"] + ".json")
            if destination.exists():
                saved = json.loads(destination.read_text())
                if saved["trial"] != trial or saved["status"] != "validated":
                    raise ValueError(f"Invalid existing checkpoint: {destination}")
                completed += 1
                continue
            started = now()
            atomic_json(directory / "status.json", dict(
                state="running", pid=os.getpid(), started_utc=started,
                active_trial=trial, completed=completed, total=len(manifest["trials"])))
            print(f"START {completed + 1}/{len(manifest['trials'])} {trial['id']}", flush=True)
            kw = {key: trial[key] for key in
                  ("hypergraph", "simple", "directed", "separation")}
            start, cpu, calendar_start = time.monotonic(), time.process_time(), time.time()
            result = engine.solve(trial["n"], trial["m"], **kw, r=3, kind="forward",
                                  method="random-greedy" if trial["hypergraph"] else "tabu",
                                  exhaustive=False, seed=trial["seed"],
                                  max_seconds=trial["requested_seconds"])
            elapsed, cpu_seconds = time.monotonic() - start, time.process_time() - cpu
            calendar_elapsed = time.time() - calendar_start
            validation_start = time.monotonic()
            checker = engine.max_hyper_connectivity if trial["hypergraph"] else engine.max_connectivity
            connectivity = checker(result.witness, vertex_split=trial["separation"] == "vertex")
            if result.witness.edge_count() != result.value or connectivity >= trial["m"]:
                raise ValueError(f"Invalid search witness for {trial['id']}")
            if result.bound != "lower" or result.complete:
                raise ValueError("Discovery unexpectedly reported a proved optimum")
            atomic_json(destination, dict(
                trial=trial, status="validated", started_utc=started, ended_utc=now(),
                search_elapsed_seconds=elapsed, search_cpu_seconds=cpu_seconds,
                calendar_elapsed_seconds=calendar_elapsed,
                solver_reported_seconds=result.seconds,
                validation_seconds=time.monotonic() - validation_start,
                value=result.value, bound=result.bound, method=result.method,
                complete=result.complete, max_connectivity=connectivity,
                witness=encode(result.witness, engine), environment=env))
            completed += 1
            print(f"DONE {trial['id']} value={result.value} elapsed={elapsed:.3f}s", flush=True)
        atomic_json(directory / "status.json", dict(state="complete", ended_utc=now(),
                    completed=completed, total=len(manifest["trials"])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", type=Path)
    group.add_argument("--resume", type=Path)
    parser.add_argument("--seconds-per-variant", type=float, default=3600)
    args = parser.parse_args()
    if args.resume:
        run(args.resume)
        return
    directory = prepare(args.output, args.seconds_per_variant)
    command = [sys.executable, str(directory / "source" / Path(__file__).name),
               "--resume", str(directory)]
    print("Frozen resume command: " + " ".join(command), flush=True)
    env = dict(os.environ)
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS"):
        env[key] = "1"
    subprocess.run(command, check=True, env=env)


if __name__ == "__main__":
    main()

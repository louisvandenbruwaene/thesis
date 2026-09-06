"""Render completed or explicitly partial equal-budget results.

Constructions are read here, never by the benchmark search runner. Their
counts are frozen on the first report so later figure edits cannot silently
change the baseline. No optimum is inferred from search or construction.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.equal_budget_benchmark import atomic_json
from scripts.benchmark_replacements import digest


def timing_issues(run):
    """Conservative one-second tolerance for clock reconciliation and cutoffs."""
    elapsed = run["search_elapsed_seconds"]
    durations = (elapsed, run["solver_reported_seconds"], run["trial"]["requested_seconds"])
    if any(not isinstance(t, (int, float)) or isinstance(t, bool)
           or not math.isfinite(t) or t < 0 for t in durations) or durations[2] == 0:
        return ["invalid or nonfinite timing measurement"]
    issues = []
    if abs(elapsed - run["solver_reported_seconds"]) > 1:
        issues.append("duration and solver clocks differ by more than one second")
    if elapsed < run["trial"]["requested_seconds"] - 1:
        issues.append("duration clock records less than the requested search target")
    return issues


def replacement_records(directory, manifest):
    """Read provenance-checked replacements without selecting by objective."""
    folder = directory / "replacements"
    if not (folder / "manifest.json").exists():
        return {}
    repair = json.loads((folder / "manifest.json").read_text())
    if repair["original_manifest_sha256"] != digest(directory / "manifest.json"):
        raise ValueError("Replacement manifest refers to a changed original manifest")
    if repair["runner_sha256"] != digest(folder / "source" / "benchmark_replacements.py"):
        raise ValueError("Frozen replacement runner changed")
    trials = {t["id"]: t for t in manifest["trials"]}
    records = {}
    selected_ids = set()
    for selection in repair["selected"]:
        trial = selection["trial"]
        trial_id = trial["id"]
        if trials.get(trial_id) != trial or trial_id in selected_ids:
            raise ValueError("Invalid or duplicate replacement selection")
        selected_ids.add(trial_id)
        original_path = directory / "trials" / (trial_id + ".json")
        original = json.loads(original_path.read_text())
        if digest(original_path) != selection["original_sha256"] or not timing_issues(original):
            raise ValueError("Replacement must refer to an unchanged timing-flagged original")
        path = folder / "trials" / (trial_id + ".json")
        if not path.exists():
            continue
        run = json.loads(path.read_text())
        if (run["trial"] != trial or run["status"] != "validated"
                or run["original_sha256"] != selection["original_sha256"]
                or run["replacement_manifest_sha256"] != digest(folder / "manifest.json")):
            raise ValueError(f"Invalid replacement checkpoint: {path}")
        records[trial_id] = run
    return records


def report(directory):
    directory = Path(directory).resolve()
    manifest = json.loads((directory / "manifest.json").read_text())
    for name, expected in manifest["source_sha256"].items():
        if digest(directory / "source" / name) != expected:
            raise ValueError(f"Original frozen source changed: {name}")
    replacements = replacement_records(directory, manifest)
    baseline_path = directory / "comparison_baseline.json"
    if not baseline_path.exists():
        from make_figures import gather_variant_grid
        panels = {m: gather_variant_grid(m) for m in (3, 6)}
        counts = {f"v{i:02d}_n{n}_m{m}": value
                  for m, rows in panels.items() for i, panel in enumerate(rows)
                  for n, value in zip(*panel["construction"])}
        driver = Path(__file__).resolve().parents[1] / "make_figures.py"
        atomic_json(baseline_path, dict(
            created_utc=datetime.now(timezone.utc).isoformat(),
            description="Supplied construction counts, not asserted optima or search inputs",
            figure_driver_sha256=hashlib.sha256(driver.read_bytes()).hexdigest(),
            counts=counts))
    baseline = json.loads(baseline_path.read_text())["counts"]
    groups, allocated, labels = {}, {}, {}
    for trial in manifest["trials"]:
        model = "hypergraph" if trial["hypergraph"] else "graph"
        model = "simple " + model if trial["simple"] else "multi" + model
        separation = "arc" if trial["directed"] and trial["separation"] == "edge" else trial["separation"]
        labels[trial["variant"]] = f"{model}, {'directed' if trial['directed'] else 'undirected'}, {separation}"
        key = f"v{trial['variant']:02d}_n{trial['n']}_m{trial['m']}"
        group = groups.setdefault(key, dict(variant=trial["variant"], n=trial["n"], m=trial["m"],
                                           expected=0, runs=[]))
        group["expected"] += 1
        allocated[trial["variant"]] = allocated.get(trial["variant"], 0) + trial["requested_seconds"]
        path = directory / "trials" / (trial["id"] + ".json")
        if path.exists():
            run = json.loads(path.read_text())
            if run["trial"] != trial or run["status"] != "validated":
                raise ValueError(f"Invalid checkpoint: {path}")
            group["runs"].append(run)
    rows = []
    for key, group in groups.items():
        replacement_runs = [replacements[r["trial"]["id"]] for r in group["runs"]
                            if r["trial"]["id"] in replacements]
        selected = [replacements.get(r["trial"]["id"], r) for r in group["runs"]]
        qualified = [r for r in selected if not timing_issues(r)]
        all_runs = group["runs"] + replacement_runs
        values = [r["value"] for r in qualified]
        rows.append(dict(key=key, variant=group["variant"], n=group["n"], m=group["m"],
                         completed_seeds=len(group["runs"]), qualified_seeds=len(values),
                         expected_seeds=group["expected"],
                         raw_search_values=[dict(seed=r["trial"]["seed"], value=r["value"],
                                                 timing_issues=timing_issues(r)) for r in group["runs"]],
                         replacement_search_values=[dict(seed=r["trial"]["seed"], value=r["value"],
                                                 timing_issues=timing_issues(r)) for r in replacement_runs],
                         selected_trials=[dict(id=r["trial"]["id"], seed=r["trial"]["seed"],
                             source="replacement" if "original_sha256" in r else "original", value=r["value"])
                             for r in qualified],
                         search_values=values, search_min=min(values) if values else None,
                         search_median=statistics.median(values) if values else None,
                         search_max=max(values) if values else None,
                         search_elapsed_seconds=sum(r["search_elapsed_seconds"] for r in all_runs),
                         search_cpu_seconds=sum(r["search_cpu_seconds"] for r in all_runs),
                         validation_seconds=sum(r["validation_seconds"] for r in all_runs),
                         qualified_elapsed_seconds=sum(r["search_elapsed_seconds"] for r in qualified),
                         qualified_cpu_seconds=sum(r["search_cpu_seconds"] for r in qualified),
                         qualified_requested_seconds=sum(r["trial"]["requested_seconds"] for r in qualified),
                         supplied_construction=baseline[key]))
    completed = sum(row["completed_seeds"] for row in rows)
    qualified_count = sum(row["qualified_seeds"] for row in rows)
    interruptions = directory / "interruptions.json"
    replacement_interruptions = directory / "replacements" / "interruptions.json"
    status = "partial" if completed < len(manifest["trials"]) else (
        "complete" if qualified_count == completed else "finished_with_timing_issues")
    original_flagged = sum(bool(r["timing_issues"]) for row in rows for r in row["raw_search_values"])
    result = dict(status=status, timing_qualified=qualified_count,
                  original_timing_flagged=original_flagged, replacements_saved=len(replacements),
                  completed=completed, expected=len(manifest["trials"]),
                  seconds_allocated_per_variant=allocated, variant_labels=labels,
                  interruptions=json.loads(interruptions.read_text()) if interruptions.exists() else [],
                  replacement_interruptions=json.loads(replacement_interruptions.read_text())
                  if replacement_interruptions.exists() else [], rows=rows)
    atomic_json(directory / "report.json", result)
    lines = ["# Equal-budget search report", "",
             f"Status: {result['status']}. {completed} of {result['expected']} trials saved.", "",
             f"Timing checks passed for {qualified_count} selected trials. Original timing flags: {original_flagged}. Replacement trials saved: {len(replacements)}.", "",
             "Search values are unaided outcomes. Construction counts are frozen comparison lower bounds, not asserted optima or necessarily the latest constructions.",
             "Search statistics below use only timing-qualified trials. Flagged values remain in report.json and the original trial files.",
             "A valid timing replacement takes the original's slot regardless of which objective is larger. Both records remain available. All saved search time includes discarded runs and replacements.",
             f"Uncheckpointed interruptions: {len(result['interruptions'])} original and {len(result['replacement_interruptions'])} replacement. Their unknown durations are not included in saved-time totals.",
             "Missing runs are not zeros. Partial rows have not received the full allocation.", ""]
    for variant, label in sorted(labels.items()):
        lines += [f"## v{variant:02d}: {label}", "",
                  f"Allocated search time across all cases: {allocated[variant]:g} seconds.", "",
                  "| n | m | Qualified seeds (saved) | Search min | Median | Max | Supplied construction | All saved search time (s) |",
                  "|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for row in sorted((r for r in rows if r["variant"] == variant), key=lambda r: (r["n"], r["m"])):
            show = lambda value: "pending" if value is None else str(value)
            lines.append(f"| {row['n']} | {row['m']} | {row['qualified_seeds']}/{row['expected_seeds']} ({row['completed_seeds']} saved) | "
                         f"{show(row['search_min'])} | {show(row['search_median'])} | {show(row['search_max'])} | "
                         f"{row['supplied_construction']} | {row['search_elapsed_seconds']:.3f} |")
        lines.append("")
    (directory / "report.md").write_text("\n".join(lines) + "\n")
    print(f"{result['status']}: {completed}/{result['expected']} trials. Reports in {directory}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    report(parser.parse_args().directory)

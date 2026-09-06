"""Render reviewed equal-budget data without rerunning or lifting search values."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.equal_budget_benchmark import atomic_json, digest, now
from scripts.benchmark_report import report


def baseline(directory):
    path = directory / "manuscript_baseline.json"
    if not path.exists():
        import make_figures as figures
        panels = {m: figures.gather_variant_grid(m) for m in (3, 6)}
        cells = {}
        for m, rows in panels.items():
            for variant, panel in enumerate(rows):
                constructions = dict(zip(*panel["construction"]))
                exact = dict(zip(*panel.get("exact", ([], []))))
                proved = dict(zip(*panel.get("proved", ([], []))))
                for n in (6, 8, 10, 12):
                    bounds = [series[n] for series in (exact, proved) if n in series]
                    cells[f"v{variant:02d}_n{n}_m{m}"] = dict(
                        construction=constructions[n], upper=min(bounds) if bounds else None)
        atomic_json(path, dict(created_utc=now(), figure_driver_sha256=digest(figures.__file__),
            description="Supplied construction and upper-bound snapshot for manuscript comparison, never search inputs",
            cells=cells))
    return json.loads(path.read_text())


def verify_inputs(directory, data, bounds):
    from scripts.equal_budget_benchmark import schedule
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest["trials"] != schedule(3600):
        raise ValueError("Manuscript tables require the declared 384-trial one-hour protocol")
    if data["status"] != "complete" or data["timing_qualified"] != data["expected"]:
        raise ValueError("Do not render final manuscript tables from an incomplete timing audit")
    audit = json.loads((directory / "witness_audit.json").read_text())
    if audit["original_manifest_sha256"] != digest(directory / "manifest.json"):
        raise ValueError("Witness audit refers to a changed manifest")
    from scripts import validate_benchmark
    if audit["verifier_sha256"] != digest(validate_benchmark.__file__):
        raise ValueError("Rerun witness validation with the current verifier")
    verified = {r["path"]: r["sha256"] for r in audit["records"]}
    if len(data["rows"]) != 128 or any(r["expected_seeds"] != 3 for r in data["rows"]):
        raise ValueError("Expected 128 cases with three seeds each")
    for row in data["rows"]:
        if row["qualified_seeds"] != row["expected_seeds"]:
            raise ValueError("Incomplete parameter row")
        cell = bounds["cells"][row["key"]]
        if cell["upper"] is not None and max(row["search_values"] + [cell["construction"]]) > cell["upper"]:
            raise ValueError(f"Evidence exceeds an upper bound: {row['key']}")
        for selected in row["selected_trials"]:
            prefix = "replacements/" if selected["source"] == "replacement" else ""
            path = prefix + "trials/" + selected["id"] + ".json"
            if verified.get(path) != digest(directory / path):
                raise ValueError(f"Selected witness not covered by the independent audit: {path}")


def detailed(data, bounds, m, first):
    lines = [r"\begin{tabular}{rrrrrr}", r"\toprule",
             r"$n$ & Search min & Median & Search max & Construction & Seeds \\", r"\midrule"]
    for variant in range(first, first+8):
        label = data["variant_labels"][str(variant)]
        lines.append(r"\multicolumn{6}{l}{\itshape " + label + r"} \\")
        for row in sorted((r for r in data["rows"] if r["variant"] == variant and r["m"] == m), key=lambda r:r["n"]):
            values = [row["n"], row["search_min"], row["search_median"], row["search_max"],
                      bounds["cells"][row["key"]]["construction"]]
            lines.append(" & ".join(f"{x:g}" for x in values) + f" & {row['qualified_seeds']}" + r" \\")
        lines.append(r"\addlinespace[3pt]")
    return "\n".join(lines + [r"\bottomrule", r"\end{tabular}"]) + "\n"


def render(directory, output):
    directory, output = Path(directory).resolve(), Path(output).resolve()
    report(directory)
    data = json.loads((directory / "report.json").read_text())
    bounds = baseline(directory)
    verify_inputs(directory, data, bounds)
    output.mkdir(parents=True, exist_ok=True)
    for m in (3, 6):
        for name, first in (("graphs", 0), ("hypergraphs", 8)):
            (output / f"equal_budget_m{m}_{name}.tex").write_text(detailed(data, bounds, m, first))
    lines = [r"\begin{tabular}{lrr}", r"\toprule",
             r"Variant & Best reaches $C$ & All seeds reach $C$ \\", r"\midrule"]
    for variant in range(16):
        rows = [r for r in data["rows"] if r["variant"] == variant]
        best = sum(r["search_max"] >= bounds["cells"][r["key"]]["construction"] for r in rows)
        all_seeds = sum(r["search_min"] >= bounds["cells"][r["key"]]["construction"] for r in rows)
        lines.append(f"{data['variant_labels'][str(variant)]} & {best}/{len(rows)} & {all_seeds}/{len(rows)}" + r" \\")
    (output / "equal_budget_summary.tex").write_text("\n".join(lines + [r"\bottomrule", r"\end{tabular}"]) + "\n")
    provenance = dict(created_utc=now(), renderer_sha256=digest(__file__),
        report_sha256=digest(directory / "report.json"),
        comparison_sha256=digest(directory / "manuscript_baseline.json"),
        witness_audit_sha256=digest(directory / "witness_audit.json"),
        nominal_search_seconds=sum(data["seconds_allocated_per_variant"].values()),
        all_saved_duration_seconds=sum(r["search_elapsed_seconds"] for r in data["rows"]),
        all_saved_cpu_seconds=sum(r["search_cpu_seconds"] for r in data["rows"]),
        qualified_duration_seconds=sum(r["qualified_elapsed_seconds"] for r in data["rows"]),
        qualified_cpu_seconds=sum(r["qualified_cpu_seconds"] for r in data["rows"]),
        original_timing_flagged=data["original_timing_flagged"],
        original_interruptions=len(data["interruptions"]),
        replacement_interruptions=len(data["replacement_interruptions"]),
        replacements_saved=data["replacements_saved"])
    atomic_json(directory / "manuscript_tables.json", provenance)
    print(f"Rendered five audited tables in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[2] / "figures")
    args = parser.parse_args()
    render(args.directory, args.output)

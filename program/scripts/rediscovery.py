"""Run the seven rediscovery cases with one declared budget per case.

This is a new experiment, not reconstruction of the old hand-kept table.
No named construction or optimum is passed to solve(). Existing output is
never overwritten. Run from program/; choose the limit explicitly:
  ../.venv/bin/python3 scripts/rediscovery.py --seconds 2 --output data/rediscovery.json
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from erdos915_unified import solve, max_edge_connectivity
from make_figures import MachineValues, DATA, REDISCOVERY_CASES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output exists; choose a new file to preserve the previous experiment")
    ledger = MachineValues(DATA / "machine_values.json", rebuild=True, candidate=args.output)
    for label, n, m, directed, simple in REDISCOVERY_CASES:
        kw = dict(directed=directed, simple=simple, separation="edge")
        def run():
            result = solve(n, m, seed=0, max_seconds=args.seconds, **kw)
            assert result.witness.edge_count() == result.value
            assert max_edge_connectivity(result.witness) <= m - 1
            print(result.describe(), flush=True)
            return result
        ledger.get_or_run("search", n, m, args.seconds, kw, run)


if __name__ == "__main__":
    main()

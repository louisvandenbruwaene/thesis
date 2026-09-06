#!/usr/bin/env python3
"""Wall-clock benchmark backing tab:generating-benchmark in ch2_machine.tex.

Times two maximisation procedures and one supplied-target classification task,
for directed simple digraphs with m=2, n=3..7, on a single core.
These are not equivalent tasks and their times are not solver speed-up ratios:

  blind   -- every matrix assignment, no pruning (test_solve.py's reference
             sweep, reimplemented here so this script is self-contained).
  pruned  -- maximisation by _exhaustive_directed, with a construction incumbent.
  geng    -- the geng-seeded generation pipeline of this section,
             enumerate_extremal_directed_multigraphs_via_generation, run with
             parallel=False. It is GIVEN the known optimal arc count and only
             lists feasible classes at that count; it does not prove the optimum.

The blind sweep is only run for n <= 4: at n = 5 the 2^20 assignments already
cost tens of minutes with this reference implementation, the same growth
fig:complexity plots. Requires nauty's geng on PATH.
"""
from __future__ import annotations

import itertools
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "program"))

import erdos915_unified as e

L = {2: 2, 3: 4, 4: 6, 5: 8, 6: 10, 7: 12}   # ell_2^dir(n), thm:dir-arc-m2-exact
M = 2
BLIND_MAX_N = 4


def blind(n: int, m: int) -> int:
    measure = e._connectivity_measure("edge")
    cells = e._matrix_cells(n, True)
    best = 0
    for values in itertools.product((0, 1), repeat=len(cells)):
        graph = e.Graph(n, e.SIMPLE_DIRECTED)
        for (u, v), value in zip(cells, values):
            if value:
                graph.set_multiplicity(u, v, value)
        if measure(graph) <= m - 1 and graph.edge_count() > best:
            best = graph.edge_count()
    return best


def main() -> None:
    for n in range(3, 8):
        row: dict[str, float | None] = {}

        if n <= BLIND_MAX_N:
            t0 = time.time()
            val = blind(n, M)
            row["blind"] = time.time() - t0
            assert val == L[n], (n, val, L[n])
        else:
            row["blind"] = None

        t0 = time.time()
        val, _witness, completed = e._exhaustive_directed(
            n, M, "edge", time.time() + 1800.0)
        row["pruned"] = time.time() - t0
        assert completed and val == L[n], (n, val, L[n], completed)

        t0 = time.time()
        reps = e.enumerate_extremal_directed_multigraphs_via_generation(
            n, M, L[n], parallel=False)
        row["geng"] = time.time() - t0
        assert reps, (n, "no representative found at the known extremal value")

        print(n, row, flush=True)


if __name__ == "__main__":
    main()

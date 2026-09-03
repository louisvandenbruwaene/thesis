#!/usr/bin/env python3
"""The m = 6, n = 6, r = 3 gap: the edge bound reads 12, the true maximum is 11.

Backs the sentence in app_proofs.tex (sec:variant-grids) that says all 125970
simple twelve-hyperedge candidates are infeasible, and the caption of
fig:variant-bounds-m6-hyper that names 11 as the true maximum there.

prop:hyper-edge gives floor((m-1)(n-1)/(r-1)) = 12 as an upper bound for every
r-uniform hypergraph.  thm:simple-hyper-edge attains it only when
m - 1 <= C(n-2, r-2), which at m = 6, n = 6, r = 3 asks 5 <= 4 and fails.  So
the bound is not known to be met, and this script settles the cell by hand:

  (a) walk all C(20, 12) = 125970 ways to choose 12 of the 20 possible
      3-subsets of a 6-set, and check that every one has lambda^max >= 6, and
  (b) exhibit one 11-hyperedge family with lambda^max <= 5.

Together those give the exact value 11.  The main program's own branch and
bound does not finish this cell inside the figure budget, which is why
tab:variant-values prints the bound rather than the value, so this stands as
the independent settlement of it.

The checker is the thesis program's own max_hyperedge_connectivity, so this
script supplies the enumeration and not a second flow routine.

Run from program/:  ../.venv/bin/python3 scripts/hyper_edge_m6_n6_gap.py
"""
from __future__ import annotations

import itertools
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from erdos915_unified import Hypergraph, max_hyperedge_connectivity  # noqa: E402

N, M, R = 6, 6, 3
CAP = M - 1                      # lambda^max must not exceed this
BOUND = (M - 1) * (N - 1) // (R - 1)      # prop:hyper-edge reads 12 here


def feasible(edges) -> bool:
    """True when this simple r-uniform hypergraph has lambda^max <= m-1."""
    return max_hyperedge_connectivity(Hypergraph(N, edges, r=R)) <= CAP


def main() -> None:
    triples = [frozenset(t) for t in itertools.combinations(range(N), R)]
    print(f"n={N}, m={M}, r={R}")
    print(f"prop:hyper-edge upper bound      : {BOUND}")
    print(f"available distinct hyperedges    : {len(triples)}")

    # (a) no family of BOUND hyperedges is feasible.
    total = 0
    survivors = []
    start = time.time()
    for family in itertools.combinations(triples, BOUND):
        total += 1
        if feasible(family):
            survivors.append(family)
    print(f"\n(a) walked {total} families of {BOUND} hyperedges "
          f"in {time.time() - start:.1f}s")
    print(f"    feasible among them          : {len(survivors)}")
    assert total == 125970, total
    assert not survivors, survivors[:3]

    # (b) some family of BOUND-1 hyperedges is feasible.
    witness = None
    for family in itertools.combinations(triples, BOUND - 1):
        if feasible(family):
            witness = family
            break
    print(f"\n(b) a feasible {BOUND - 1}-hyperedge family:")
    assert witness is not None
    for edge in witness:
        print("      ", sorted(edge))
    print(f"    lambda^max                   : "
          f"{max_hyperedge_connectivity(Hypergraph(N, witness, r=R))} <= {CAP}")

    print(f"\nexact value: {BOUND - 1}, one below the bound of {BOUND}")


if __name__ == "__main__":
    main()

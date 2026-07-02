"""Exhaustive check of the SATURATED ATTACHMENT LEMMA on doubled trees.

Lemma (saturated attachment; see ../saturated_attachment_lemma.md).  Let
D0 be a directed multigraph in which EVERY ordered pair (x, y) has local
arc-connectivity exactly m-1 (everywhere-saturated).  Attach one new vertex v
with any arcs (multiplicities 0..m-1 per ordered pair).  If the result stays
feasible (lambda^max <= m-1), then d(v) <= 2(m-1), and equality forces a
single partner u with mu(v,u) = mu(u,v) = m-1.

Doubled bidirected trees at multiplicity m-1 are everywhere-saturated, so this
script verifies the lemma exhaustively on ALL non-isomorphic trees with 5 and
6 vertices at m = 3: every one of the 3^(2n) attachment patterns is measured,
the maximum feasible degree must equal 2(m-1) = 4, and every degree-4 feasible
pattern must be a single-partner full-multiplicity attachment.

Unlike the fully self-contained proof scripts here, this one imports the
thesis program for its capped feasibility predicate (exceeds_bound), because
3^12 patterns per tree need the fast path; the predicate itself is
differential-tested inside the program's own suite.

Run:  python3 research_notes/scripts/saturated_attachment_check.py
Expected output: nine lines, every one reporting max d(v) = 4 and
all-single-partner-full = True, as re-verified on 2026-07-02.
"""

import itertools
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "program"))
from erdos915_unified import Graph, MULTI_DIRECTED, exceeds_bound  # noqa: E402

# All non-isomorphic trees on 5 and 6 vertices, as edge lists.
TREES_5 = [
    [(0, 1), (1, 2), (2, 3), (3, 4)],            # path P5
    [(0, 1), (0, 2), (0, 3), (0, 4)],            # star
    [(0, 1), (1, 2), (2, 3), (2, 4)],            # broom
]
TREES_6 = [
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],    # path P6
    [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)],    # star
    [(0, 1), (1, 2), (2, 3), (3, 4), (3, 5)],    # broom
    [(0, 1), (1, 2), (2, 3), (2, 4), (2, 5)],    # spider
    [(0, 1), (1, 2), (2, 3), (1, 4), (2, 5)],    # double broom (H shape)
    [(0, 1), (1, 2), (1, 3), (2, 4), (2, 5)],    # two adjacent degree-3 nodes
]


def check_tree(tree_edges, n, m):
    """Return (max feasible attachment degree, list of equality shapes)."""
    cap = m - 1
    base = np.zeros((n + 1, n + 1), dtype=int)
    for (a, b) in tree_edges:
        base[a, b] = base[b, a] = cap
    graph = Graph(n + 1, MULTI_DIRECTED)
    best, equality_shapes = 0, []
    for values in itertools.product(range(m), repeat=2 * n):
        degree = sum(values)
        if degree == 0:
            continue
        graph.mu[:] = base
        for x in range(n):
            graph.mu[n, x] = values[x]          # out-arcs v -> x
            graph.mu[x, n] = values[n + x]      # in-arcs  x -> v
        if not exceeds_bound(graph, cap):
            best = max(best, degree)
            if degree == 2 * cap:
                outs = {x: values[x] for x in range(n) if values[x]}
                ins = {x: values[n + x] for x in range(n) if values[n + x]}
                equality_shapes.append((outs, ins))
    return best, equality_shapes


def main():
    m = 3
    failures = 0
    start = time.time()
    for label, trees, n in (("n=5", TREES_5, 5), ("n=6", TREES_6, 6)):
        for index, tree_edges in enumerate(trees):
            best, shapes = check_tree(tree_edges, n, m)
            single_partner = all(
                len(outs) == 1 and len(ins) == 1 and list(outs) == list(ins)
                and list(outs.values()) == [m - 1]
                and list(ins.values()) == [m - 1]
                for outs, ins in shapes)
            ok = (best == 2 * (m - 1)) and single_partner and len(shapes) == n
            failures += 0 if ok else 1
            print(f"{label} tree {index}: max feasible d(v) = {best} "
                  f"(lemma says {2 * (m - 1)}); {len(shapes)} equality shapes "
                  f"(one per partner vertex expected: {n}); "
                  f"all single-partner-full = {single_partner}  "
                  f"{'OK' if ok else 'FAIL'}")
    print(f"total {time.time() - start:.0f}s, failures: {failures}")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())

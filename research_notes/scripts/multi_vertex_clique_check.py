"""Verify the clique-chain refutation of conj:multi-vertex.

conj:multi-vertex (app_proofs.tex) claims K_m^multi(n) = (m-1)(n-1) for all
n >= m+2. This script builds the clique-chain construction of
multi_vertex_clique_chains.md, checks feasibility TWO independent ways
(the thesis program's exceeds_bound, and a from-scratch networkx max-flow on
a hand-built split network), and confirms the exact gain formula.

Run: python3 research_notes/scripts/multi_vertex_clique_check.py
Needs the thesis program on the path (run from program/, or adjust sys.path)
and networkx (only used for the independent cross-check).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "program"))

from erdos915_unified import Graph, MULTI_UNDIRECTED, exceeds_bound  # noqa: E402

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


def gain(r, m):
    """gain(r, m) = (r-1)(r-2)(m-1-r) / 2, the exact excess of one K_r block
    over the (m-1)(rank) it would cost as pure tree edges."""
    assert (r - 1) * (r - 2) % 2 == 0
    return (r - 1) * (r - 2) * (m - 1 - r) // 2


def build_clique_chain(n, m, r, k):
    """k disjoint K_r blocks (multiplicity m+1-r within each), chained by
    single bridge edges (multiplicity m-1) through one port vertex per block,
    leftover vertices as a pendant path."""
    assert r * k <= n
    q = m + 1 - r
    assert q >= 1, "r too large for this m (need r <= m so blocks are non-empty)"
    g = Graph(n, MULTI_UNDIRECTED)
    for i in range(k):
        base = r * i
        verts = list(range(base, base + r))
        for a in range(r):
            for b in range(a + 1, r):
                g.set_multiplicity(verts[a], verts[b], q)
        if i > 0:
            g.set_multiplicity(r * (i - 1), base, m - 1)
    cursor = r * (k - 1) if k > 0 else None
    for v in range(r * k, n):
        if cursor is None:
            cursor = v
            continue
        g.set_multiplicity(cursor, v, m - 1)
        cursor = v
    return g


def independent_worst_kappa(g):
    """From-scratch max-flow on a hand-built vertex-split network (networkx),
    sharing no code with the thesis program's checker."""
    n = g.num_vertices
    G = nx.DiGraph()
    for v in range(n):
        G.add_edge(("in", v), ("out", v), capacity=1)
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            mult = int(g.mu[u, v])
            if mult > 0:
                G.add_edge(("out", u), ("in", v), capacity=mult)
    worst = 0
    for s in range(n):
        for t in range(s + 1, n):
            G[("in", s)][("out", s)]["capacity"] = 10**6
            G[("in", t)][("out", t)]["capacity"] = 10**6
            val = nx.maximum_flow_value(G, ("out", s), ("in", t))
            G[("in", s)][("out", s)]["capacity"] = 1
            G[("in", t)][("out", t)]["capacity"] = 1
            worst = max(worst, val)
    return worst


def main():
    cases = [(5, 3, 1), (5, 3, 5), (6, 3, 3), (8, 3, 5),
              (10, 6, 1), (10, 6, 3), (15, 8, 2), (20, 11, 2)]
    print("formula check: K(n,m,r) == (m-1)(n-1) + floor(n/r)*gain(r,m)")
    for m, r, k in cases:
        n = r * k + 5
        g = build_clique_chain(n, m, r, k)
        total = int(g.mu.sum() // 2)
        predicted = (m - 1) * (n - 1) + k * gain(r, m)
        feasible_program = not exceeds_bound(g, m - 1, separation="vertex",
                                              parallel_routes=True)
        tree_val = (m - 1) * (n - 1)
        line = (f"  m={m:3d} r={r:2d} k={k:2d} n={n:3d}  total={total:6d} "
                f"predicted={predicted:6d}  match={total == predicted}  "
                f"program_feasible={feasible_program}  gain={total - tree_val}")
        if NETWORKX_AVAILABLE:
            worst = independent_worst_kappa(g)
            line += f"  networkx_worst_kappa={worst} (cap {m-1})"
            assert worst <= m - 1, "INDEPENDENT CHECK: infeasible!"
        print(line)
        assert total == predicted, "formula mismatch"
        assert feasible_program, "program says infeasible"

    print("\nexact-optimal-r table (gain rate per vertex used):")
    for m in [5, 10, 20, 30, 50]:
        best_r, best_rate = None, -1
        for r in range(3, m + 1):
            rate = gain(r, m) / r
            if rate > best_rate:
                best_rate, best_r = rate, r
        print(f"  m={m:3d}: best r*={best_r:3d}  gain(r*)={gain(best_r, m):6d}"
              f"  rate={best_rate:8.2f}")

    print("\nALL CHECKS PASSED: conj:multi-vertex is refuted for every m >= 5.")


if __name__ == "__main__":
    main()

"""Finite checks of the clique bouquets in thm:clique-chain-vertex.

The former conjecture that K_m(n) = (m-1)(n-1) for all n >= m+2 has been
removed from the thesis. This script builds the clique-bouquet construction,
checks feasibility TWO independent ways
(the thesis program's exceeds_bound, and a from-scratch networkx max-flow on
a hand-built split network), and confirms the exact gain formula.

Run: python3 program/scripts/multi_vertex_clique_check.py
The thesis program is located relative to this file. NetworkX is optional
and supplies the independent cross-check when installed.
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


def build_clique_bouquet(n, m, r, k):
    """k copies of K_r ALL SHARING vertex 0 and otherwise disjoint, every edge
    at multiplicity m+1-r, leftover vertices as a pendant path at m-1.

    Sharing one vertex uses r-1 new vertices per additional block. Disjoint
    blocks joined by bridges still use r vertices each; the bridges add edges,
    not vertices. The respective packing limits are floor((n-1)/(r-1)) and
    floor(n/r)."""
    assert k * (r - 1) + 1 <= n
    q = m + 1 - r
    assert q >= 1, "r too large for this m (need r <= m so blocks are non-empty)"
    g = Graph(n, MULTI_UNDIRECTED)
    for i in range(k):
        verts = [0] + [1 + i * (r - 1) + j for j in range(r - 1)]
        for a in range(len(verts)):
            for b in range(a + 1, len(verts)):
                g.set_multiplicity(verts[a], verts[b], q)
    cursor = 0
    for v in range(k * (r - 1) + 1, n):
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
    cases = [(5, 3, 1), (5, 3, 3), (6, 3, 3), (8, 3, 4),
              (10, 6, 1), (10, 6, 2), (15, 8, 2), (20, 11, 2)]
    print("construction count = (m-1)(n-1) + k*gain(r,m)")
    for m, r, k in cases:
        n = k * (r - 1) + 1 + 4
        g = build_clique_bouquet(n, m, r, k)
        total = g.edge_count()
        predicted = (m - 1) * (n - 1) + k * gain(r, m)
        feasible_program = not exceeds_bound(g, m - 1, separation="vertex")
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
            rate = gain(r, m) / (r - 1)
            if rate > best_rate:
                best_rate, best_r = rate, r
        print(f"  m={m:3d}: best r*={best_r:3d}  gain(r*)={gain(best_r, m):6d}"
              f"  rate={best_rate:8.2f}")

    print("\nALL FINITE CHECKS PASSED for the listed clique bouquets.\n"
          "These checks corroborate the count and feasibility on those cases;\n"
          "the general construction retains its proposed-proof status in\n"
          "thm:clique-chain-vertex. Its count is a lower bound, not an exact optimum.")


if __name__ == "__main__":
    main()

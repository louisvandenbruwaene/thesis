#!/usr/bin/env python3
"""The multigraph vertex problem (other convention) as a BLOCK problem.

Backs research_notes/multi_vertex_blocks.md and the thesis results
lem:multi-vertex-objective, thm:multi-vertex-blocks, thm:multi-vertex-bipartite
and tab:multi-vertex-exact.

Two claims.

(A) CLOSED FORM.  On a fixed feasible simple graph G0 the best multigraph over
    it sets mu = m-1-pi on every edge, and kappa_{G0} = 1 + pi on an edge, so
        K_m(n) = max over feasible G0 of  W_m(G0),
        W_m(G0) = sum over edges of (m - kappa_{G0}(u,v)).

(B) BLOCKS.  Adjacent u,v lie in one block B and no u-v path leaves it, so
    kappa_{G0}(u,v) = kappa_B(u,v) and W_m is additive over blocks.  Hence
        K_m(n) = max { sum_i g_m(b_i) : b_i >= 2, sum_i (b_i - 1) <= n-1 },
    a knapsack, where g_m(b) is the best a single 2-connected block (or a single
    edge) on b vertices can score.  Blocks are realised by hanging them off one
    shared vertex.

Needs nauty's geng on PATH and networkx.  Cross-checks against the thesis
program's own exhaustive max_multigraph_vertex_standard where that finishes.

Run:  python3 research_notes/scripts/multi_vertex_blocks.py
"""
from __future__ import annotations

import itertools
import os
import subprocess
import sys
from functools import lru_cache

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "program"))

import networkx as nx

BMAX = int(os.environ.get("BMAX", "7"))       # 8 takes a few minutes


# --------------------------------------------------------------- the objective
def kappa_simple(G: nx.Graph, u, v) -> int:
    """Internally disjoint u-v routes in a SIMPLE graph (the edge is one)."""
    if G.has_edge(u, v):
        H = G.copy()
        H.remove_edge(u, v)
        return 1 + nx.node_connectivity(H, u, v)
    return nx.node_connectivity(G, u, v)


def feasible(G: nx.Graph, m: int) -> bool:
    return all(kappa_simple(G, u, v) <= m - 1
               for u, v in itertools.combinations(G.nodes, 2))


def W(G: nx.Graph, m: int) -> int:
    return sum(m - kappa_simple(G, u, v) for u, v in G.edges)


# ------------------------------------------------------- blocks, via nauty geng
@lru_cache(maxsize=None)
def biconnected(b: int) -> tuple:
    if b == 2:
        return (nx.complete_graph(2),)
    out = subprocess.run(["geng", "-Cq", str(b)], capture_output=True, check=True)
    return tuple(nx.from_graph6_bytes(line) for line in out.stdout.split() if line)


@lru_cache(maxsize=None)
def g(m: int, b: int):
    """(best score, witness) over 2-connected feasible blocks on b vertices."""
    best, arg = -1, None
    for B in biconnected(b):
        if feasible(B, m) and W(B, m) > best:
            best, arg = W(B, m), B
    return best, arg


def knapsack(m: int, n: int, bmax: int) -> int:
    vals = {}
    for b in range(2, min(bmax, n) + 1):
        v, _ = g(m, b)
        if v > 0:
            vals[b - 1] = max(vals.get(b - 1, 0), v)
    best = [0] * n
    for u in range(1, n):
        for size, val in vals.items():
            if size <= u:
                best[u] = max(best[u], best[u - size] + val)
    return best[n - 1]


# ------------------------------------------------- the bipartite block, by hand
def bipartite_rate(m: int):
    """max over s <= t <= m-1 of the per-vertex rate of a K_{s,t} bouquet."""
    best, arg = 0.0, None
    for s in range(1, m):
        for t in range(s, m):
            rate = s * t * (m - s) / (s + t - 1)
            if rate > best:
                best, arg = rate, (s, t)
    return best, arg


def clique_rate(m: int) -> float:
    return max(r * (m + 1 - r) / 2 for r in range(2, m + 1))


def main() -> None:
    print(f"[1] g_m(b), best score of one block, for b <= {BMAX}")
    for m in range(2, 9):
        cells = []
        for b in range(2, BMAX + 1):
            v, _ = g(m, b)
            cells.append(f"b={b}:{v if v >= 0 else '-':>4}")
        print(f"    m={m}  " + "  ".join(cells))

    print(f"\n[2] K_m(n) by knapsack.  B = one block attains it, "
          f"T = the thickened tree attains it")
    for m in range(2, 9):
        cells = []
        for n in range(2, BMAX + 1):
            k = knapsack(m, n, BMAX)
            one = g(m, n)[0] if n <= BMAX else -1
            tag = ("B" if one == k else "") + ("T" if k == (m - 1) * (n - 1) else "")
            cells.append(f"{k}{tag}")
        print(f"    m={m}  " + "  ".join(f"{c:>6}" for c in cells))

    print("\n[3] cross-check against the thesis program's exhaustive routine")
    from erdos915_unified import max_multigraph_vertex_standard      # noqa: E402
    import time
    # The default list is the fast one.  FULL=1 runs the wider sweep, which
    # proves 23 cells (m=2 to n=7, m=3 to n=6, m in {4,5,6} to n=5) and leaves
    # five at their time cap as lower bounds: (3,7), (4,6), (4,7), (5,6) all
    # match the knapsack, and (5,7) returns 27 below the knapsack's 29, an
    # unfinished branch and bound rather than a disagreement.
    cells = [(2, 5), (3, 5), (4, 5), (5, 4), (5, 5), (6, 4)]
    if os.environ.get("FULL"):
        cells = [(m, n) for m in range(2, 7) for n in range(2, 8)]
    for (m, n) in cells:
        k = knapsack(m, n, BMAX)
        ex, _, done = max_multigraph_vertex_standard(n, m, deadline=time.time() + 300)
        print(f"    m={m} n={n}: knapsack {k}, exhaustive {ex} "
              f"({'proved' if done else 'lower bound'}) -> "
              f"{'AGREE' if k == ex else 'DISAGREE'}")

    print("\n[4] bipartite bouquet against clique bouquet, rate per vertex")
    print(f"    {'m':>4}{'clique':>10}{'bipartite':>12}{'(s,t)':>10}{'ratio':>8}")
    for m in (5, 8, 12, 20, 50, 100, 400):
        cl = clique_rate(m)
        bp, arg = bipartite_rate(m)
        print(f"    {m:>4}{cl:>10.1f}{bp:>12.1f}{str(arg):>10}{bp/cl:>8.3f}")
    print(f"    limit 8(3-2*sqrt2) = {8 * (3 - 2 * 2 ** 0.5):.4f}, "
          f"and the gap to the upper bound falls from 16 to "
          f"{2 / (3 - 2 * 2 ** 0.5):.2f}")


if __name__ == "__main__":
    main()

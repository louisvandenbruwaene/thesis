#!/usr/bin/env python3
"""The multigraph vertex problem (incidence convention) as a BLOCK problem.

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
program's own exhaustive max_multigraph_vertex where that finishes.

Run:  python3 program/scripts/multi_vertex_blocks.py
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


# ------------------------------------------------- describing a winning block
def describe_block(B: nx.Graph) -> str:
    """Name the shape of a block, so the thesis can cite structure, not just a score.

    The claim the thesis makes about these witnesses is that they are
    ``K_{s,t}`` with a few edges added inside the small side, rather than
    complete graphs.  That is a checkable statement and this checks it: take a
    maximum independent set ``I``, which is the large empty side a complete
    bipartite block would have, and ask whether every edge between ``I`` and the
    rest is present.  When it is, the block IS ``K_{|I|, b-|I|}`` plus whatever
    lies inside the complement, and the count of those extras is reported.  When
    it is not, we say so rather than forcing the description to fit.
    """
    b = B.number_of_nodes()
    graph6 = nx.to_graph6_bytes(B, header=False).decode().strip()
    degs = sorted((d for _, d in B.degree()), reverse=True)
    stem = f"graph6 {graph6}  degrees {degs}"
    if B.number_of_edges() == b * (b - 1) // 2:
        return f"{stem}  complete K_{b}"
    # a maximum independent set, by brute force: b <= 8 here
    best_I = max((S for k in range(b, 0, -1)
                  for S in itertools.combinations(B.nodes, k)
                  if not any(B.has_edge(x, y)
                             for x, y in itertools.combinations(S, 2))),
                 key=len)
    I = set(best_I)
    J = set(B.nodes) - I
    cross = sum(1 for x in I for y in J if B.has_edge(x, y))
    inside = sum(1 for x, y in itertools.combinations(sorted(J), 2)
                 if B.has_edge(x, y))
    s, t = len(J), len(I)
    if cross == len(I) * len(J):
        shape = (f"K_{{{s},{t}}}" if inside == 0
                 else f"K_{{{s},{t}}}+{inside}e inside the side of size {s}")
        return f"{stem}  {shape}"
    return (f"{stem}  not complete-bipartite-plus-extras "
            f"(independent set {t}, {cross} of {len(I) * len(J)} cross edges)")


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


@lru_cache(maxsize=None)
def g_all(m: int, b: int) -> tuple:
    """EVERY maximiser on b vertices, not just the first one geng happens to emit.

    The score alone does not license a claim about the SHAPE of an extremiser.
    If several non-isomorphic blocks tie at ``g_m(b)`` then no single one of them
    is "the" winning block, and a structural sentence in the thesis has to be
    true of all of them or be qualified.  So the count is reported alongside the
    description rather than left to the accident of generation order.
    """
    best = g(m, b)[0]
    if best < 0:
        return ()
    return tuple(B for B in biconnected(b)
                 if feasible(B, m) and W(B, m) == best)


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

    print(f"\n[1b] the winning block itself, per (m, b).  This is the structural"
          f"\n     evidence behind 'the winning blocks are unbalanced and"
          f"\n     bipartite-like rather than complete'.  A witness is reported as"
          f"\n     K_{{s,t}}+e when its complement of a maximum independent set I"
          f"\n     sees every one of the |I|*(b-|I|) cross edges present, so the"
          f"\n     block is complete bipartite between I and the rest plus e extra"
          f"\n     edges inside the smaller side.  'complete' means K_b.")
    for m in range(3, 9):
        for b in range(3, BMAX + 1):
            v, B = g(m, b)
            if B is None:
                continue
            ties = g_all(m, b)
            bip = sum(1 for T in ties if "+" in describe_block(T)
                      or describe_block(T).rstrip().endswith("}"))
            note = (f"  [{len(ties)} maximisers, {bip} of them K_{{s,t}}-with-extras]"
                    if len(ties) > 1 else "  [unique maximiser]")
            print(f"    m={m} b={b}: W={v:>3}  {describe_block(B)}{note}")

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
    from erdos915_unified import max_multigraph_vertex      # noqa: E402
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
        ex, _, done = max_multigraph_vertex(n, m, deadline=time.time() + 300)
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

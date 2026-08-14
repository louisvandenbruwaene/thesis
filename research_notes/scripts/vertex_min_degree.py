#!/usr/bin/env python3
"""Does min degree >= m force two vertices joined by m internally disjoint paths?

If YES, then every feasible graph (kappa^max <= m-1) has a vertex of degree
<= m-1; feasibility is hereditary under vertex deletion, so a feasible graph is
(m-1)-DEGENERATE and

    k_m(n) <= (m-1)n - C(m,2),

a factor-2 improvement on the 2(m-1)n that Mader's density theorem gives (which
only uses the weaker fact that a feasible graph has no m-connected subgraph).

For m=3 this is classical: min degree >= 3 forces a K_4 subdivision, which
contains two branch vertices joined by 3 internally disjoint paths.

This script searches for a COUNTEREXAMPLE: a graph with min degree >= m and
kappa^max <= m-1.
"""
from __future__ import annotations

import itertools
import subprocess
import sys

import networkx as nx


def kappa(G, u, v) -> int:
    if G.has_edge(u, v):
        H = G.copy()
        H.remove_edge(u, v)
        return 1 + nx.node_connectivity(H, u, v)
    return nx.node_connectivity(G, u, v)


def feasible(G, m: int) -> bool:
    for u, v in itertools.combinations(G.nodes, 2):
        cod = len(set(G[u]) & set(G[v]))
        if cod + (1 if G.has_edge(u, v) else 0) > m - 1:
            return False
    return all(kappa(G, u, v) <= m - 1
               for u, v in itertools.combinations(G.nodes, 2))


def search(m: int, n: int):
    """All graphs on n vertices with min degree >= m; any feasible one?"""
    out = subprocess.run(["geng", "-qc", f"-d{m}", str(n)],
                         capture_output=True, check=True)
    lines = [l for l in out.stdout.split() if l]
    hits = []
    for l in lines:
        G = nx.from_graph6_bytes(l)
        if feasible(G, m):
            hits.append(G)
    return len(lines), hits


def main() -> None:
    print("searching for a feasible graph (kappa^max <= m-1) with min degree >= m")
    print(f"{'m':>3}{'n':>4}{'graphs with delta>=m':>22}{'feasible ones':>15}")
    for m in (3, 4, 5, 6):
        for n in range(m + 1, 11):
            if m == 3 and n > 9:
                continue
            try:
                total, hits = search(m, n)
            except subprocess.CalledProcessError:
                continue
            print(f"{m:>3}{n:>4}{total:>22}{len(hits):>15}"
                  + ("   <-- COUNTEREXAMPLE" if hits else ""))
            if hits:
                G = hits[0]
                print(f"      degrees {sorted(d for _, d in G.degree())}, "
                      f"{G.number_of_edges()} edges, edges {sorted(G.edges())}")
                return


if __name__ == "__main__":
    main()

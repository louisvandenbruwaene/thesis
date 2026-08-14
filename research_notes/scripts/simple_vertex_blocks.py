#!/usr/bin/env python3
"""The SIMPLE vertex problem k_m(n) (Erdos 915, open for m >= 6) as a block
problem, and what small blocks say about the asymptotic constant.

k_m(n) = max |E(G)| over simple G on n vertices with kappa^max(G) <= m-1
(thesis convention: the largest edge count AVOIDING m internally disjoint
paths between some pair).

BLOCK REDUCTION.  Adjacent u,v lie in one block B and no u-v path leaves it, so
kappa_G(u,v) = kappa_B(u,v); every edge lies in exactly one block; and
sum (b_i - 1) <= n-1.  Conversely any multiset of blocks is realised by hanging
them off one shared vertex.  Hence

    k_m(n) = max { sum_i h_m(b_i) : b_i >= 2, sum_i (b_i - 1) <= n-1 },

where h_m(b) is the largest edge count of a 2-connected (or single-edge)
feasible graph on b vertices.  So c_m := lim k_m(n)/(n-1) = sup_b h_m(b)/(b-1),
and every finite b gives a RIGOROUS lower bound on c_m.

Known for comparison:
  m<=4 : c_m = m/2                      (Bartfai, Bollobas, Leonard)
  m=5  : c_5 = 8/3                      (Sorensen-Thomassen)
  m>=6 : OPEN.  Sorensen-Thomassen give c_m >= (m(m-1)-2)/(2m-3);
         Mader showed c_m > m/2 for m >= 6.
"""
from __future__ import annotations

import itertools
import subprocess
import sys
from functools import lru_cache

import networkx as nx

import os
BMAX = int(os.environ.get("BMAX", "8"))


def kappa(G: nx.Graph, u, v) -> int:
    if G.has_edge(u, v):
        H = G.copy()
        H.remove_edge(u, v)
        return 1 + nx.node_connectivity(H, u, v)
    return nx.node_connectivity(G, u, v)


def feasible(G: nx.Graph, m: int) -> bool:
    # cheap necessary condition first: a common neighbour is a 2-path
    for u, v in itertools.combinations(G.nodes, 2):
        cod = len(set(G[u]) & set(G[v]))
        if cod + (1 if G.has_edge(u, v) else 0) > m - 1:
            return False
    return all(kappa(G, u, v) <= m - 1
               for u, v in itertools.combinations(G.nodes, 2))


@lru_cache(maxsize=None)
def biconnected(b: int) -> tuple:
    if b == 2:
        return (nx.complete_graph(2),)
    out = subprocess.run(["geng", "-Cq", str(b)], capture_output=True, check=True)
    return tuple(nx.from_graph6_bytes(l) for l in out.stdout.split() if l)


@lru_cache(maxsize=None)
def h(m: int, b: int):
    best, arg = -1, None
    for B in biconnected(b):
        if B.number_of_edges() > best and feasible(B, m):
            best, arg = B.number_of_edges(), B
    return best, arg


def main() -> None:
    print("h_m(b) = max edges of a 2-connected feasible block on b vertices,")
    print("and h_m(b)/(b-1), whose supremum over b is c_m = lim k_m(n)/(n-1)\n")
    hdr = "  m  " + "".join(f"   b={b}    " for b in range(2, BMAX + 1))
    print(hdr)
    for m in range(3, 9):
        cells = []
        for b in range(2, BMAX + 1):
            v, _ = h(m, b)
            cells.append(f"{v:>3}/{b-1}={v/(b-1):4.2f} " if v >= 0 else "   none    ")
        print(f"  {m}  " + "".join(cells))

    print("\nbest rigorous lower bound on c_m from blocks with b <= "
          f"{BMAX}, against what is known")
    print(f"{'m':>3}{'best b':>8}{'c_m >=':>10}{'S-T bound':>12}"
          f"{'m/2':>8}{'known c_m':>12}")
    known = {3: "3/2", 4: "2", 5: "8/3"}
    for m in range(3, 9):
        best_b, best_r = None, 0.0
        for b in range(2, BMAX + 1):
            v, _ = h(m, b)
            if v >= 0 and v / (b - 1) > best_r:
                best_r, best_b = v / (b - 1), b
        st = (m * (m - 1) - 2) / (2 * m - 3)
        print(f"{m:>3}{best_b:>8}{best_r:>10.4f}{st:>12.4f}{m/2:>8.2f}"
              f"{known.get(m, 'OPEN'):>12}")


if __name__ == "__main__":
    main()

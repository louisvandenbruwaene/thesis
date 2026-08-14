#!/usr/bin/env python3
"""Rebuild and verify the Sorensen-Thomassen general lower-bound construction.

Their Theorem (p.144): for fixed k, f_k(n) > [k(k-1)-2]/(2k-3) * (n-k) for
infinitely many n, which disproves the Bollobas-Erdos conjecture for all k >= 5.

Their proof of (a) builds G^m by induction with Lemma 5.  G^0 = K_k minus an
edge; G^m is assembled from G_1 = G_2 = G^0 and G_3 = G^{m-1} by identifying
y_1~x_2, y_2~x_3, y_3~x_1, where x_i = z_1, y_i = z_2 of each piece.  The
identifications are arranged in a CYCLE, so the result stays 2-connected: it is
a single block, which is exactly why a decomposition along cut vertices cannot
see it.

Claimed: n(G^m) = k + (2k-3)m, e(G^m) = (k(k-1)-2)(m + 1/2), and G^m has no
k-rail, i.e. kappa^max <= k-1 in this thesis's convention.
"""
from __future__ import annotations

import itertools

import networkx as nx


def kappa(G, u, v) -> int:
    if G.has_edge(u, v):
        H = G.copy()
        H.remove_edge(u, v)
        return 1 + nx.node_connectivity(H, u, v)
    return nx.node_connectivity(G, u, v)


def kappa_max(G) -> int:
    return max(kappa(G, u, v) for u, v in itertools.combinations(G.nodes, 2))


def base(k: int):
    """G^0 = K_k minus the edge {k-2,k-1}; z1 = k-2, z2 = 0, z3 = 1."""
    G = nx.complete_graph(k)
    G.remove_edge(k - 2, k - 1)
    return G, (k - 2), 0, 1


def glue(k: int, m: int):
    """G^m by the recursion above.  Returns (graph, z1, z2, z3)."""
    G, z1, z2, z3 = base(k)
    for _ in range(m):
        A, a1, a2, a3 = base(k)            # G_1
        B, b1, b2, _ = base(k)             # G_2
        C, c1, c2 = G, z1, z2              # G_3 = G^{m-1}
        H = nx.Graph()
        pa = {v: ("A", v) for v in A}
        pb = {v: ("B", v) for v in B}
        pc = {v: ("C", v) for v in C}
        # identify y1(A)=x2(B), y2(B)=x3(C), y3(C)=x1(A)
        pb[b1] = pa[a2]                    # x2 := y1
        pc[c1] = pb[b2]                    # x3 := y2
        pa[a1] = pc[c2]                    # x1 := y3
        for (u, v) in A.edges:
            H.add_edge(pa[u], pa[v])
        for (u, v) in B.edges:
            H.add_edge(pb[u], pb[v])
        for (u, v) in C.edges:
            H.add_edge(pc[u], pc[v])
        G = nx.convert_node_labels_to_integers(H, label_attribute="orig")
        back = {d["orig"]: v for v, d in G.nodes(data=True)}
        z1, z2, z3 = back[pa[a1]], back[pa[a3]], back[pa[a2]]
    return G, z1, z2, z3


def main() -> None:
    print("verifying the Sorensen-Thomassen construction G^m")
    print(f"{'k':>3}{'m':>3}{'n':>6}{'expected n':>12}{'e':>6}{'expected e':>12}"
          f"{'kappa^max':>11}{'<= k-1':>8}{'2-conn':>8}{'rate e/(n-1)':>14}")
    for k in (5, 6, 7):
        for m in range(0, 4):
            G, z1, z2, z3 = glue(k, m)
            n, e = G.number_of_nodes(), G.number_of_edges()
            exp_n = k + (2 * k - 3) * m
            exp_e = (k * (k - 1) - 2) * (2 * m + 1) // 2
            km = kappa_max(G)
            print(f"{k:>3}{m:>3}{n:>6}{exp_n:>12}{e:>6}{exp_e:>12}{km:>11}"
                  f"{str(km <= k - 1):>8}"
                  f"{str(nx.is_biconnected(G)):>8}{e/(n-1):>14.4f}")
        limit = (k * (k - 1) - 2) / (2 * k - 3)
        print(f"     limit rate {limit:.4f} against the Bollobas-Erdos rate "
              f"{k/2:.2f}; first m beating it: m > {2/(k-4):.2f}\n")


if __name__ == "__main__":
    main()

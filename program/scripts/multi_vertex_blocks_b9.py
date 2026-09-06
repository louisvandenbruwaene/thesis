#!/usr/bin/env python3
"""g_6(9): the best W_6 a single 2-connected block on nine vertices can score.

The sweep behind tab:multi-vertex-blocks stops at b = 8, and the table's caption
says the per-vertex rate is still rising there, so the table does not
extrapolate.  This settles the next cell of the m = 6 row, which is the row the
variant grids plot.

Standalone on purpose: it shares no code with erdos915_unified.py, so it
corroborates the main program rather than repeating it.  It needs nauty's geng
on the path and networkx.

The edge floor costs nothing.  Every edge of a 2-connected graph has
kappa >= 2, so W_6 = sum_e (6 - kappa_e) <= 4|E|, and 13 edges cannot reach 53.
Within the survivors the branch and bound prunes on the same inequality.

    ../.venv/bin/python3 scripts/multi_vertex_blocks_b9.py
"""
import subprocess
import networkx as nx
from networkx.algorithms.connectivity import local_node_connectivity as lnc

B, M, FLOOR = 9, 6, 14


def kappa(G, u, v):
    """Internally disjoint u-v routes, counting the direct edge as one."""
    if G.has_edge(u, v):
        H = G.copy()
        H.remove_edge(u, v)
        return 1 + lnc(H, u, v)
    return lnc(G, u, v)


def main():
    # This is an exclusion threshold, not a claimed feasible block score.
    best, witness, seen = (M - 2) * (FLOOR - 1), None, 0
    proc = subprocess.Popen(["geng", "-Cq", str(B), f"{FLOOR}:36"],
                            stdout=subprocess.PIPE, text=True)
    for line in proc.stdout:
        g6 = line.strip()
        if not g6:
            continue
        seen += 1
        G = nx.from_graph6_bytes(g6.encode())
        edges, W, ok = list(G.edges()), 0, True
        for i, (u, v) in enumerate(edges):
            if W + 4 * (len(edges) - i) <= best:
                ok = False           # cannot beat the incumbent
                break
            k = kappa(G, u, v)
            if k > M - 1:
                ok = False           # infeasible
                break
            W += M - k
        if not ok:
            continue
        if any(lnc(G, u, v) > M - 1 for u, v in nx.non_edges(G)):
            continue
        if W > best:
            best, witness = W, g6
            print(f"new best W_{M} = {W}  graph6 {g6}", flush=True)
    if proc.wait() != 0:
        raise RuntimeError("geng failed. The sweep does not prove an upper bound.")
    print(f"examined {seen} two-connected graphs on {B} vertices "
          f"with at least {FLOOR} edges")
    if witness is None:
        print(f"g_{M}({B}) <= {best}. No attaining witness was found above the exclusion threshold.")
    else:
        print(f"g_{M}({B}) = {best}, attained by {witness}")


if __name__ == "__main__":
    main()

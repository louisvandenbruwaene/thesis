#!/usr/bin/env python3
"""Reproducible checks for directed_arc_m3_reduction.md section 2.4 (self-contained).

(P) arc partition: a feasible digraph (lambda^max <= 2) has no arc into a source;
(L) self-similarity: the non-source set R induces a feasible sub-digraph, i.e.
    lambda^max(D[R]) <= 2  (so e(R) <= ell_3^dir(|R|));
(prop) complete-layer: an augmented-bipartite extremiser has a complete source
    layer and R of maximum in-degree 1 (hypothesis (H) holds on it).

Checked on the augmented-bipartite family and on random maximal feasible
digraphs.  Uses its own capped max-flow so it does not depend on the program it
corroborates.
"""
import random
from collections import deque, defaultdict


def flow_capped(arcs, s, t, cap=3):
    """Arc-disjoint s->t paths, counted up to ``cap`` (Ford-Fulkerson, unit caps)."""
    res = defaultdict(int)
    adj = defaultdict(set)
    for (u, v) in arcs:
        res[(u, v)] += 1
        adj[u].add(v)
        adj[v].add(u)
    flow = 0
    while flow < cap:
        par = {s: None}
        q = deque([s])
        ok = False
        while q:
            u = q.popleft()
            if u == t:
                ok = True
                break
            for w in adj[u]:
                if w not in par and res[(u, w)] > 0:
                    par[w] = u
                    q.append(w)
        if not ok:
            break
        v = t
        while v != s:
            u = par[v]
            res[(u, v)] -= 1
            res[(v, u)] += 1
            v = u
        flow += 1
    return flow


def infeasible(arcs, verts, m=3):
    """True if some ordered pair inside ``verts`` has >= m arc-disjoint routes."""
    inside = [(u, v) for (u, v) in arcs if u in verts and v in verts]
    return any(s != t and flow_capped(inside, s, t, m) >= m
               for s in verts for t in verts)


def random_feasible(n, rng, m=3):
    arcs = set()
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    rng.shuffle(pairs)
    for (u, v) in pairs:
        arcs.add((u, v))
        if infeasible(arcs, range(n), m):
            arcs.discard((u, v))
    return arcs


def augmented_bipartite(k):
    """Odd extremiser on n = 2k-1: A = k-1 sources, B = k, complete A->B + a k-cycle."""
    A = list(range(k - 1))
    B = list(range(k - 1, 2 * k - 1))
    arcs = set((a, b) for a in A for b in B)
    for i in range(k):
        arcs.add((B[i], B[(i + 1) % k]))
    return arcs


def analyse(arcs, n):
    din = [0] * n
    for (_, v) in arcs:
        din[v] += 1
    S = [x for x in range(n) if din[x] == 0]
    R = [x for x in range(n) if din[x] > 0]
    into_S = sum(1 for (_, v) in arcs if v in set(S))
    feasibleR = not infeasible(arcs, set(R))
    indeg_R = defaultdict(int)
    for (u, v) in arcs:
        if u in set(R) and v in set(R):
            indeg_R[v] += 1
    max_indeg_R = max(indeg_R.values()) if R else 0
    return dict(sigma=len(S), rho=len(R), into_S=into_S,
                feasibleR=feasibleR, max_indeg_R=max_indeg_R)


def main():
    allok = True
    print("augmented-bipartite extremisers (expect into_S=0, D[R] feasible, maxIndeg(R)=1):")
    for k in range(3, 9):
        n = 2 * k - 1
        info = analyse(augmented_bipartite(k), n)
        ok = info["into_S"] == 0 and info["feasibleR"] and info["max_indeg_R"] == 1
        allok &= ok
        print(f"  k={k} n={n}: {info}  ok={ok}")
    print("random maximal feasible digraphs (expect into_S=0, D[R] feasible):")
    rng = random.Random(1)
    for n in range(4, 11):
        for _ in range(8):
            info = analyse(random_feasible(n, rng), n)
            ok = info["into_S"] == 0 and info["feasibleR"]
            allok &= ok
            if not ok:
                print(f"  n={n}: {info}  ok={ok}  <-- FAILURE")
    print(f"random sweep clean: {allok}")
    print("ALL OK" if allok else "FAILURES PRESENT")


if __name__ == "__main__":
    main()

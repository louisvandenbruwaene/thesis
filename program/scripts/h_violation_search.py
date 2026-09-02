#!/usr/bin/env python3
"""Targeted search for an (H)-violating extremiser (directed_arc_m3_reduction.md).

(H) says every m=3 extremiser has its non-source set R of maximum in-degree <= 1.
Fix the arc count at the extremal value Q(n) = floor((n+1)^2/4) and try to
MAXIMISE the maximum R-in-degree while staying feasible (lambda^max <= 2).  If a
feasible digraph with exactly Q(n) arcs and an R-vertex of in-degree >= 2 exists,
the search may find it -- that would REFUTE (H).  If many restarts stay pinned at
1, that is direct evidence for (H) at the first quadratic sizes n = 9, 10, which
are past exhaustion (so untestable before).

Self-contained: own unit-capacity max-flow, no program import, no multiprocessing.
"""
import random
from collections import deque, defaultdict


def flow_capped(adj_cap, s, t, cap=3):
    """Max arc-disjoint s->t paths, counted up to cap. adj_cap: dict (u,v)->units."""
    res = defaultdict(int)
    nbr = defaultdict(set)
    for (u, v), c in adj_cap.items():
        if c:
            res[(u, v)] += c
            nbr[u].add(v); nbr[v].add(u)
    flow = 0
    while flow < cap:
        par = {s: None}; q = deque([s]); ok = False
        while q:
            u = q.popleft()
            if u == t:
                ok = True; break
            for w in nbr[u]:
                if w not in par and res[(u, w)] > 0:
                    par[w] = u; q.append(w)
        if not ok:
            break
        v = t
        while v != s:
            u = par[v]; res[(u, v)] -= 1; res[(v, u)] += 1; v = u
        flow += 1
    return flow


class Digraph:
    def __init__(self, n):
        self.n = n
        self.arcs = set()

    def feasible(self):
        cap = {a: 1 for a in self.arcs}
        for s in range(self.n):
            for t in range(self.n):
                if s != t and flow_capped(cap, s, t, 3) >= 3:
                    return False
        return True

    def add(self, a):
        self.arcs.add(a)

    def can_add(self, a):
        """Feasible after adding arc a? (incremental: only s=tail pairs can rise,
        but we check all pairs for safety since it stays small.)"""
        self.arcs.add(a)
        ok = self.feasible()
        self.arcs.discard(a)
        return ok


def max_R_indegree(arcs, n):
    din = [0] * n
    for (_, v) in arcs:
        din[v] += 1
    R = set(v for v in range(n) if din[v] > 0)
    indeg_R = defaultdict(int)
    for (u, v) in arcs:
        if u in R and v in R:
            indeg_R[v] += 1
    return max(indeg_R.values()) if R else 0


def augmented_bipartite(k):
    n = 2 * k - 1
    A = list(range(k - 1)); B = list(range(k - 1, n))
    arcs = set((a, b) for a in A for b in B)
    for i in range(k):
        arcs.add((B[i], B[(i + 1) % k]))
    return arcs, n


def Q(n):
    return (n + 1) ** 2 // 4


def swap_step(arcs, n, rng):
    """Return a feasible neighbour with the SAME arc count: drop one arc, add a
    different one keeping lambda^max<=2.  Returns None if no move found quickly."""
    arclist = list(arcs)
    all_pairs = [(u, v) for u in range(n) for v in range(n)
                 if u != v and (u, v) not in arcs]
    rng.shuffle(arclist); rng.shuffle(all_pairs)
    for drop in arclist[:14]:
        rest = arcs - {drop}
        for add in all_pairs[:22]:
            cand = rest | {add}
            d = Digraph(n); d.arcs = cand
            if d.feasible():
                return cand
    return None


def search(k, restarts=40, steps=300, seed=0):
    arcs0, n = augmented_bipartite(k)
    target = Q(n)
    assert len(arcs0) == target, (len(arcs0), target)
    rng = random.Random(seed)
    best = 1
    best_arcs = None
    for r in range(restarts):
        arcs = set(arcs0)
        # random walk from the construction, scoring by max R-in-degree
        cur_score = max_R_indegree(arcs, n)
        for _ in range(steps):
            nxt = swap_step(arcs, n, rng)
            if nxt is None:
                break
            sc = max_R_indegree(nxt, n)
            # accept if score improves or sideways (explore the extremal stratum)
            if sc >= cur_score or rng.random() < 0.3:
                arcs, cur_score = nxt, sc
                if sc > best:
                    best, best_arcs = sc, set(arcs)
                if best >= 2:
                    return best, n, best_arcs
    return best, n, best_arcs


def main():
    for k in (5, 6):           # n = 9, 11 (odd quadratic). k=5 -> n=9 is the seam.
        best, n, arcs = search(k, restarts=12, steps=80, seed=k)
        verdict = ("REFUTES (H): found a Q(n)-arc feasible digraph with R-in-degree 2"
                   if best >= 2 else
                   "no (H)-violating extremiser found (max R-in-degree stayed 1)")
        print(f"n={n} (k={k}), arcs=Q(n)={Q(n)}: best max-R-in-degree found = {best}"
              f"  -> {verdict}")
        if best >= 2 and arcs is not None:
            print("   witness arcs:", sorted(arcs))


if __name__ == "__main__":
    main()

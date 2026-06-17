#!/usr/bin/env python3
"""Reproducible verification for backward_arc_min_degree_attempt.md.

Self-contained (no networkx / scipy): a unit-capacity max-flow gives the number
of arc-disjoint directed s->t routes, i.e. lambda(s,t); lambda^max is the max
over ordered pairs.

Two checks, both for the simple directed-arc problem at m = 3 (feasible iff
lambda^max <= 2):

  1. ARITHMETIC. The minimum-degree-deletion induction (the engine that proves
     the m = 2 value) applied to the m = 3 quadratic branch
     Q(n) = floor((n+1)^2/4) overshoots the target by exactly +1 at even n and
     +0 at odd n (for n past the crossover), with a +2 anomaly only at the
     crossover seam n = 9. So the whole m = 3 quadratic upper bound reduces to
     killing one +1 of slack at even n.

  2. ATTACHMENT. In the even +1 case (n = 2k, a = k^2 + k + 1 arcs) the digraph
     is forced (k+1)-regular up to total degree-excess 2, and every
     degree-(k+1) vertex v deletes to an exact odd extremiser on 2k-1 vertices.
     Taking that odd extremiser to be the augmented bipartite B_{k-1,k} + one
     directed k-cycle in B, we test every way of re-attaching a degree-(k+1)
     vertex v: NONE stays feasible (lambda^max <= 2). Hence the +1 case is
     impossible -- modulo uniqueness of the odd extremiser, still open.
"""
import itertools
import math
from collections import deque, defaultdict


def maxflow_unit(arcs, s, t):
    """Arc-disjoint directed s->t routes via Edmonds-Karp on unit capacities."""
    cap = defaultdict(int)
    adj = defaultdict(set)
    for (u, v) in arcs:
        cap[(u, v)] += 1
        adj[u].add(v)
        adj[v].add(u)
    flow = 0
    while True:
        par = {s: None}
        q = deque([s])
        while q:
            u = q.popleft()
            if u == t:
                break
            for w in adj[u]:
                if w not in par and cap[(u, w)] > 0:
                    par[w] = u
                    q.append(w)
        if t not in par:
            break
        v = t
        while v != s:
            u = par[v]
            cap[(u, v)] -= 1
            cap[(v, u)] += 1
            v = u
        flow += 1
    return flow


def lam_max(nodes, arcs):
    return max(maxflow_unit(arcs, s, t) for s in nodes for t in nodes if s != t)


def Q(n):
    """Quadratic (augmented-bipartite) branch of conj:dir-arc at m = 3."""
    return ((n + 1) ** 2) // 4


def ell(n):
    """Conjectured value = max(linear hub branch, quadratic branch) at m = 3."""
    return max(3 * (n - 1), Q(n))


def check_arithmetic():
    print("== arithmetic: min-degree induction overshoot (m=3) ==")
    print("  the induction uses the TRUE bound ell(n-1)=max(linear,quadratic),")
    print("  so the crossover seam (ell(8)=21, not 20) shows honestly at n=9.")
    print("  n   target Q(n)   ell(n-1)   floor(n/(n-2)*ell(n-1))   overshoot")
    for n in range(9, 18):
        bound = math.floor(n / (n - 2) * ell(n - 1))
        print(f"  {n:2d}     {Q(n):4d}       {ell(n - 1):4d}         {bound:4d}"
              f"               {bound - Q(n):+d}")
    print()


def odd_extremiser(k):
    """Augmented bipartite on 2k-1 vertices: A (size k-1) -> B (size k) complete,
    plus a directed k-cycle inside B. k^2 arcs, lambda^max = 2."""
    A = [f"a{i}" for i in range(k - 1)]
    B = [f"b{i}" for i in range(k)]
    arcs = [(a, b) for a in A for b in B]
    arcs += [(B[i], B[(i + 1) % k]) for i in range(k)]
    return A, B, arcs


def check_attachment(ks=(4, 5, 6)):
    print("== attachment: can a degree-(k+1) vertex be added to the odd extremiser? ==")
    for k in ks:
        A, B, arcs0 = odd_extremiser(k)
        nodes0 = A + B
        assert len(arcs0) == k * k
        assert lam_max(nodes0, arcs0) == 2
        v = "v"
        base = set(arcs0)
        # Every A-vertex (degree k in the extremiser) must gain >= 1 arc to v to
        # reach the forced minimum degree k+1: choose its direction. Then add
        # exactly 2 further v-incident arcs (to/from B, or a second arc to an A)
        # so that deg(v) = k+1. Search for ANY feasible completion.
        cand = []
        for b in B:
            cand += [(v, b), (b, v)]
        for a in A:
            cand += [(v, a), (a, v)]
        found = False
        for signs in itertools.product([0, 1], repeat=k - 1):
            forced = set()
            for a, s in zip(A, signs):
                forced.add((a, v) if s == 0 else (v, a))
            pre = base | forced
            for e1, e2 in itertools.combinations(cand, 2):
                if e1 == e2 or e1 in pre or e2 in pre:
                    continue
                arcs = list(pre | {e1, e2})
                if sum(1 for (x, y) in arcs if x == v or y == v) != k + 1:
                    continue
                if lam_max(nodes0 + [v], arcs) <= 2:
                    found = True
                    break
            if found:
                break
        verdict = "FEASIBLE (counterexample!)" if found else "infeasible (+1 case ruled out)"
        print(f"  k={k}: odd extremiser has {len(arcs0)} arcs (=k^2); "
              f"degree-(k+1) attachment is {verdict}")
    print()


if __name__ == "__main__":
    check_arithmetic()
    check_attachment()

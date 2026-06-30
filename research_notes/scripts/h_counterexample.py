#!/usr/bin/env python3
"""A counterexample to (H) at n = 9 (directed_arc_m3_reduction.md).

(H) claimed: every m=3 extremiser has its non-source set R of maximum in-degree
<= 1 (equivalently, some source is adjacent to every non-source).  This script
exhibits a feasible digraph D on 9 vertices with exactly Q(9) = 25 arcs (the
conjectured extremal value ell_3^dir(9)) for which (H) FAILS: it has 3 sources,
no source dominates R, and several R-vertices have in-degree 2.  Found by a
fixed-arc-count search that maximised the maximum R-in-degree (h_violation_search.py).

If ell_3^dir(9) = 25 (the thesis conjecture, and ell_3^dir(9) >= 25 by the
augmented-bipartite construction), this D is an extremiser, so (H) is FALSE as
stated and the augmented-bipartite family is NOT the whole extremal set.

Self-contained: own unit-capacity directed max-flow, no program import.
"""
from collections import deque, defaultdict

WITNESS = [(0,4),(0,5),(0,6),(0,7),(0,8),(1,4),(1,5),(1,6),(1,7),(1,8),
           (2,4),(2,5),(2,6),(2,7),(2,8),(3,4),(3,5),(3,6),(3,7),(3,8),
           (5,1),(5,4),(5,6),(5,7),(5,8)]
N = 9


def arc_disjoint(arcs, s, t, cap=3):
    """Max arc-disjoint directed s->t paths, counted up to cap (Edmonds-Karp)."""
    res = defaultdict(int)
    for a in arcs:
        res[a] += 1
    flow = 0
    while flow < cap:
        par = {s: None}; q = deque([s]); found = False
        while q:
            u = q.popleft()
            if u == t:
                found = True; break
            for v in range(N):
                if v not in par and res[(u, v)] > 0:
                    par[v] = u; q.append(v)
        if not found:
            break
        v = t
        while v != s:
            u = par[v]; res[(u, v)] -= 1; res[(v, u)] += 1; v = u
        flow += 1
    return flow


def lambda_max(arcs):
    return max(arc_disjoint(arcs, s, t)
               for s in range(N) for t in range(N) if s != t)


def family(k):
    """The (H)-violating extremiser on n = 2k-1: complete K(A,B) with |A|=k-1,
    |B|=k, plus one B-vertex beta0 pointing to one A-vertex a0 and to the rest of
    B.  Arc count (k-1)k + k = k^2 = Q(2k-1).  beta0 -> a0 makes a0 a non-source,
    and both a0 and beta0 then point to every other B-vertex, forcing R-in-degree 2.
    """
    global N
    n = 2 * k - 1
    A = list(range(k - 1)); B = list(range(k - 1, n))
    arcs = set((a, b) for a in A for b in B)
    beta0, a0 = B[1], A[1]
    arcs.add((beta0, a0))
    for b in B:
        if b != beta0:
            arcs.add((beta0, b))
    return arcs, n


def check_family():
    global N
    print("Infinite family of (H)-counterexamples (own max-flow):")
    allbad = True
    for k in range(5, 10):           # n = 9, 11, 13, 15, 17
        arcs, n = family(k)
        N = n
        lam = lambda_max(arcs)
        din = [0] * n
        for (_, v) in arcs:
            din[v] += 1
        S = [v for v in range(n) if din[v] == 0]
        R = set(v for v in range(n) if din[v] > 0)
        ind = defaultdict(int)
        for (u, v) in arcs:
            if u in R and v in R:
                ind[v] += 1
        mx = max(ind.values())
        Q = (n + 1) ** 2 // 4
        bad = (lam <= 2 and len(arcs) == Q and mx >= 2)
        allbad = allbad and bad
        print(f"  k={k} n={n}: arcs={len(arcs)} Q={Q} lambda^max={lam} "
              f"sigma={len(S)} maxRindeg={mx}  (H) FAILS={bad}")
    print("=> (H) is FALSE for every odd n>=9:", allbad)
    N = 9


def main():
    arcs = set(WITNESS)
    lam = lambda_max(arcs)
    din = [0] * N
    for (_, v) in arcs:
        din[v] += 1
    S = [v for v in range(N) if din[v] == 0]
    R = [v for v in range(N) if din[v] > 0]
    indeg_R = defaultdict(int)
    for (u, v) in arcs:
        if u in set(R) and v in set(R):
            indeg_R[v] += 1
    max_indeg_R = max(indeg_R.values())
    # which non-sources does each source miss?
    out = defaultdict(set)
    for (u, v) in arcs:
        out[u].add(v)
    dominating = [s for s in S if set(R) <= out[s]]
    # maximality: can any arc be added while staying feasible?
    addable = []
    for u in range(N):
        for v in range(N):
            if u != v and (u, v) not in arcs:
                if lambda_max(arcs | {(u, v)}) <= 2:
                    addable.append((u, v))

    print(f"arcs = {len(arcs)}  (Q(9) = {(9+1)**2//4})")
    print(f"lambda^max = {lam}  (feasible iff <= 2)")
    print(f"sources S = {S}  (sigma = {len(S)})")
    print(f"R = {R}")
    print(f"R-internal in-degrees = {dict(indeg_R)}  -> max = {max_indeg_R}")
    print(f"sources adjacent to ALL of R (a 'dominating' source) = {dominating}")
    print(f"arcs addable while staying feasible (maximality) = {len(addable)}")
    holds = (lam <= 2 and len(arcs) == 25 and max_indeg_R >= 2 and not dominating)
    print("=> feasible 25-arc digraph, max R-in-degree >= 2, no dominating source:",
          holds, "-- (H) FAILS at n=9 (given ell_3(9)=25).")
    print()
    check_family()


if __name__ == "__main__":
    main()

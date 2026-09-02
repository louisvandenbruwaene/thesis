#!/usr/bin/env python3
"""Reproducible checks for directed_arc_m3_reduction.md section 2.5 (self-contained).

(star) Summing the source-neighbourhood Lemma (2.2) over every source gives
       sum_{R-arcs (x,y)} c(x,y) <= e(S,R),
       where c(x,y) = #{ sources pointing to BOTH x and y }.  Holds for every
       feasible D (verified, 0 failures).

(neg)  The conditional bound a <= (n-sigma)(sigma+1) is FALSE for non-extremal
       feasible digraphs, even with sigma >= 1 (sigma counts only GLOBAL sources,
       but D[R] can itself be a dense linear-regime digraph).  So (H) is a property
       of EXTREMISERS, and no pure counting argument over all feasible D can prove
       it: extremality must be used.  We exhibit many sigma>=1 violations.

Own capped max-flow, no dependence on the program.
"""
import random
from collections import deque, defaultdict


def flow_capped(arcs, s, t, cap=3):
    res = defaultdict(int); adj = defaultdict(set)
    for (u, v) in arcs:
        res[(u, v)] += 1; adj[u].add(v); adj[v].add(u)
    flow = 0
    while flow < cap:
        par = {s: None}; q = deque([s]); ok = False
        while q:
            u = q.popleft()
            if u == t:
                ok = True; break
            for w in adj[u]:
                if w not in par and res[(u, w)] > 0:
                    par[w] = u; q.append(w)
        if not ok:
            break
        v = t
        while v != s:
            u = par[v]; res[(u, v)] -= 1; res[(v, u)] += 1; v = u
        flow += 1
    return flow


def infeasible(arcs, n, m=3):
    return any(s != t and flow_capped(arcs, s, t, m) >= m
               for s in range(n) for t in range(n))


def random_feasible(n, rng, m=3):
    arcs = set()
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    rng.shuffle(pairs)
    for (u, v) in pairs:
        arcs.add((u, v))
        if infeasible(arcs, n, m):
            arcs.discard((u, v))
    return arcs


def measure(arcs, n):
    din = [0] * n
    for (_, v) in arcs:
        din[v] += 1
    S = set(x for x in range(n) if din[x] == 0)
    R = set(x for x in range(n) if din[x] > 0)
    out = defaultdict(set)
    for (u, v) in arcs:
        out[u].add(v)
    eSR = sum(1 for (u, v) in arcs if u in S and v in R)
    R_arcs = [(u, v) for (u, v) in arcs if u in R and v in R]
    star_lhs = sum(sum(1 for s in S if x in out[s] and y in out[s])
                   for (x, y) in R_arcs)
    sigma, rho = len(S), len(R)
    return dict(a=len(arcs), sigma=sigma, rho=rho, eSR=eSR,
                star_ok=star_lhs <= eSR,
                bound=rho * (sigma + 1), target_ok=len(arcs) <= rho * (sigma + 1))


def main():
    rng = random.Random(3)
    tested = star_fail = neg_with_source = 0
    example = None
    for n in range(4, 11):
        for _ in range(40):
            info = measure(random_feasible(n, rng), n)
            tested += 1
            if not info["star_ok"]:
                star_fail += 1
            if not info["target_ok"] and info["sigma"] >= 1:
                neg_with_source += 1
                if example is None:
                    example = (n, info)
    print(f"tested {tested} random feasible digraphs")
    print(f"(star) sum_R-arcs c(x,y) <= e(S,R): failures = {star_fail} (want 0)")
    print(f"(neg)  a <= (n-sigma)(sigma+1) FAILS with sigma>=1 in {neg_with_source} cases")
    if example:
        n, info = example
        print(f"       e.g. n={n}: a={info['a']} > bound={info['bound']} "
              f"(sigma={info['sigma']}, rho={info['rho']}) "
              f"-- counting cannot prove (H); extremality is required.")


if __name__ == "__main__":
    main()

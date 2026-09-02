#!/usr/bin/env python3
"""Verification for the two-step budget lemma and its three consequences.

Backs research_notes/two_step_budget.md and, through it, the thesis results
lem:two-step-budget, thm:dir-vertex-linear-error, thm:dir-hyper-constant and
prop:multi-vertex-upper.

Self-contained by design: standard library only, own Edmonds-Karp, own
hypergraph and vertex-split models. It shares no code with
program/erdos915_unified.py, which is the point, since its job is to
corroborate results that the program also computes.

Run:  python3 program/scripts/two_step_budget_check.py
"""
from __future__ import annotations

import itertools
import random
from collections import deque

# --------------------------------------------------------------- max flow

def maxflow(cap: dict, s, t) -> int:
    """Edmonds-Karp on a dict of integer capacities."""
    res = dict(cap)
    nbr: dict = {}
    for (u, v) in cap:
        nbr.setdefault(u, set()).add(v)
        nbr.setdefault(v, set()).add(u)
        res.setdefault((v, u), 0)
    flow = 0
    while True:
        par, q = {s: None}, deque([s])
        while q:
            u = q.popleft()
            if u == t:
                break
            for v in nbr.get(u, ()):
                if v not in par and res.get((u, v), 0) > 0:
                    par[v] = u
                    q.append(v)
        if t not in par:
            return flow
        b, v = float("inf"), t
        while par[v] is not None:
            b = min(b, res[(par[v], v)])
            v = par[v]
        v = t
        while par[v] is not None:
            res[(par[v], v)] -= b
            res[(v, par[v])] = res.get((v, par[v]), 0) + b
            v = par[v]
        flow += b


# ------------------------------------------- directed hypergraph measures
# A forward hyperedge is (tail, frozenset of r-1 heads).

def lam_hyper(edges, u, v) -> int:
    """Max hyperedge-disjoint directed Berge routes u -> v."""
    cap, INF = {}, len(edges) + 5
    for i, (t, hs) in enumerate(edges):
        cap[(("ein", i), ("eout", i))] = 1
        cap[(("v", t), ("ein", i))] = INF
        for h in hs:
            cap[(("eout", i), ("v", h))] = INF
    return maxflow(cap, ("v", u), ("v", v))


def kap_hyper(n, edges, u, v) -> int:
    """Berge routes pairwise hyperedge-disjoint AND internally disjoint."""
    cap, INF = {}, len(edges) + n + 5
    for x in range(n):
        cap[(("vin", x), ("vout", x))] = INF if x in (u, v) else 1
    for i, (t, hs) in enumerate(edges):
        cap[(("ein", i), ("eout", i))] = 1
        cap[(("vout", t), ("ein", i))] = INF
        for h in hs:
            cap[(("eout", i), ("vin", h))] = INF
    return maxflow(cap, ("vout", u), ("vin", v))


def shadow(edges):
    """One-step shadow R and the codegree function."""
    R, cod = set(), {}
    for (t, hs) in edges:
        for h in hs:
            R.add((t, h))
            cod[(t, h)] = cod.get((t, h), 0) + 1
    return R, cod


def budget(R, n, u, v) -> int:
    """1_{(u,v) in R} + p_2(u,v), the two-step budget of the pair."""
    eps = 1 if (u, v) in R else 0
    return eps + sum(1 for x in range(n)
                     if x not in (u, v) and (u, x) in R and (x, v) in R)


# ------------------------------------------------------ simple digraphs

def kappa_dir(n, arcs, u, v) -> int:
    """Max internally vertex-disjoint directed u -> v paths."""
    cap, INF = {}, n + 5
    for x in range(n):
        cap[(("in", x), ("out", x))] = INF if x in (u, v) else 1
    for (a, b) in arcs:
        cap[(("out", a), ("in", b))] = INF
    return maxflow(cap, ("out", u), ("in", v))


def kmax_simple_vertex(n, edges) -> int:
    """kappa^max of a simple undirected graph (edge counts as one route)."""
    best = 0
    for u, v in itertools.combinations(range(n), 2):
        cap, INF = {}, n + 5
        for x in range(n):
            cap[(("in", x), ("out", x))] = INF if x in (u, v) else 1
        direct = 0
        for (a, b) in edges:
            if {a, b} == {u, v}:
                direct = 1
                continue
            cap[(("out", a), ("in", b))] = INF
            cap[(("out", b), ("in", a))] = INF
        best = max(best, direct + maxflow(cap, ("out", u), ("in", v)))
    return best


def k_m_simple(n, m) -> int:
    """Exhaustive k_m(n): max edges of a simple graph with kappa^max <= m-1."""
    pairs = list(itertools.combinations(range(n), 2))
    for size in range(len(pairs), -1, -1):
        for sub in itertools.combinations(pairs, size):
            if kmax_simple_vertex(n, sub) <= m - 1:
                return size
    return 0


# ------------------------------------------------------------- the checks

def check_hypergraph_steps(trials=3000, seed=1):
    """Steps 1 and 2 of thm:dir-hyper-constant, in both separations.

    cod(u,v) <= kappa(u,v), and  eps + p_2 <= (r-1) * kappa(u,v)  on the
    one-step shadow. Both are asserted against kappa, the weaker hypothesis,
    which implies the lambda form since kappa <= lambda.
    """
    rng = random.Random(seed)
    tight = 0
    for _ in range(trials):
        n = rng.randint(3, 7)
        r = rng.randint(3, min(5, n))
        edges = []
        for _ in range(rng.randint(1, 9)):
            vs = rng.sample(range(n), r)
            edges.append((vs[0], frozenset(vs[1:])))
        R, cod = shadow(edges)
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                kap = kap_hyper(n, edges, u, v)
                lam = lam_hyper(edges, u, v)
                assert kap <= lam, ("Whitney", edges, u, v)
                assert cod.get((u, v), 0) <= kap, ("Step 1", edges, u, v)
                b = budget(R, n, u, v)
                assert b <= (r - 1) * kap, ("Step 2", r, edges, u, v, b, kap)
                if kap and b == (r - 1) * kap:
                    tight += 1
    return tight


def check_vertex_budget(trials=3000, seed=2):
    """thm:dir-vertex-linear-error's only new step: 1_{arc} + p_2 <= kappa."""
    rng = random.Random(seed)
    for _ in range(trials):
        n = rng.randint(3, 7)
        p = rng.random()
        arcs = {(a, b) for a in range(n) for b in range(n)
                if a != b and rng.random() < p}
        for u in range(n):
            for v in range(n):
                if u != v:
                    assert budget(arcs, n, u, v) <= kappa_dir(n, arcs, u, v), \
                        (n, u, v, sorted(arcs))
    return True


def check_multi_vertex_upper():
    """prop:multi-vertex-upper on the cells of tab:multi-vertex.

    Also reproves k_3(4)=4, k_3(5)=6, k_4(5)=8 from scratch, the values
    ch1 cites as its confirmation of the thesis's counting convention.
    """
    table = {(2, 4): 3, (2, 5): 4, (3, 4): 6, (3, 5): 8,
             (4, 4): 9, (4, 5): 12, (5, 4): 14, (5, 5): 19, (6, 4): 19}
    rows = []
    for (m, n), val in sorted(table.items()):
        km = k_m_simple(n, m)
        assert val <= (m - 1) * km, ("upper bound", m, n, val, km)
        assert km < 2 * (m - 1) * n, ("Mader", m, n, km)
        rows.append((m, n, val, km, (m - 1) * km))
    assert (k_m_simple(4, 3), k_m_simple(5, 3), k_m_simple(5, 4)) == (4, 6, 8)
    return rows


if __name__ == "__main__":
    t = check_hypergraph_steps()
    print(f"thm:dir-hyper-constant Steps 1 and 2: OK "
          f"({t} pairs attain the (r-1) factor with equality)")
    print("thm:dir-vertex-linear-error route family:", check_vertex_budget())
    print("prop:multi-vertex-upper on tab:multi-vertex")
    print(f"{'m':>2} {'n':>2} {'K_m^multi':>10} {'k_m(n)':>7} {'(m-1)k_m(n)':>12}")
    for m, n, val, km, bound in check_multi_vertex_upper():
        print(f"{m:>2} {n:>2} {val:>10} {km:>7} {bound:>12}")
    print("ALL CHECKS PASSED")

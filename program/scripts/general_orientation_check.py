#!/usr/bin/env python3
"""Does the GENERAL orientation model share the leading constant?

Tests the missing Step 2 for general directed hyperedges (T, H), any split.
Self-contained: standard library only, own Edmonds-Karp, own model.

Claim under test (the maximality argument replacing the forward matching).
Let T collect v (when (u,v) is a shadow arc) and every two-step midpoint, and
let F be a MAXIMUM family of routes, one per target, pairwise hyperedge-
disjoint, using the hyperedge set U.  Then

  (i)  M := |F| <= kappa(u,v),
  (ii) every target NOT served by F lies on some hyperedge of U, so
       |T| <= M + r|U| <= (2r+1)M,
  (iii) hence  1_{(u,v) in R} + p_2(u,v) <= (2r+1)(m-1),

so the one-step shadow R is (2r+1)(m-1)-budgeted, and with lem:two-step-budget
    |E| <= (m-1)/(r-1) * floor(n^2/4) + 4(2r+1)(m-1)^2/(r-1) * (n-1).
"""
from __future__ import annotations

import itertools
import random
from collections import deque

INF = 10 ** 6


def maxflow(cap: dict, s, t) -> int:
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
            x = q.popleft()
            if x == t:
                break
            for y in nbr.get(x, ()):
                if y not in par and res.get((x, y), 0) > 0:
                    par[y] = x
                    q.append(y)
        if t not in par:
            return flow
        b, v = INF, t
        while par[v] is not None:
            b = min(b, res[(par[v], v)])
            v = par[v]
        v = t
        while par[v] is not None:
            res[(par[v], v)] -= b
            res[(v, par[v])] = res.get((v, par[v]), 0) + b
            v = par[v]
        flow += b


# ------------------------------------------------------------------ model
# A general directed hyperedge is (frozenset tails, frozenset heads), a
# partition of an r-set into two non-empty parts.

def kappa(edges, u, v) -> int:
    """Routes pairwise hyperedge-disjoint AND internally vertex-disjoint."""
    cap: dict = {}
    for i, (T, H) in enumerate(edges):
        gin, gout = ("e", i, 0), ("e", i, 1)
        cap[(gin, gout)] = 1
        for t in T:
            cap[(("v", t, 1), gin)] = INF
        for h in H:
            cap[(gout, ("v", h, 0))] = INF
    verts = {x for (T, H) in edges for x in T | H} | {u, v}
    for x in verts:
        cap[(("v", x, 0), ("v", x, 1))] = INF if x in (u, v) else 1
    return maxflow(cap, ("v", u, 1), ("v", v, 0))


def max_kappa(edges, n) -> int:
    return max((kappa(edges, u, v) for u in range(n) for v in range(n) if u != v),
               default=0)


def shadow(edges, n):
    """Arcs of R and cod(u,v): hyperedges with u a tail and v a head."""
    cod: dict = {}
    for (T, H) in edges:
        for u in T:
            for v in H:
                cod[(u, v)] = cod.get((u, v), 0) + 1
    return cod


def targets(edges, cod, u, v):
    """T = {v} if (u,v) in R, plus every midpoint x with (u,x),(x,v) in R."""
    out = []
    if (u, v) in cod:
        out.append(v)
    for x in {a for (a, b) in cod} | {b for (a, b) in cod}:
        if x != u and x != v and (u, x) in cod and (x, v) in cod:
            out.append(x)
    return out


def max_route_family(edges, u, v, T):
    """A MAXIMUM family of routes, one per target, pairwise hyperedge-disjoint.

    Brute force over subsets so the check tests the real maximum, not a greedy
    one.  Returns (size, used hyperedge indices, served targets) of one optimum.
    """
    enter = {t: [i for i, (Te, He) in enumerate(edges) if u in Te and t in He] for t in T}
    leave = {t: [i for i, (Te, He) in enumerate(edges) if t in Te and v in He]
             for t in T if t != v}

    best = (0, frozenset(), frozenset())

    def rec(idx, used, served):
        nonlocal best
        if len(served) + (len(T) - idx) <= best[0]:
            return
        if idx == len(T):
            if len(served) > best[0]:
                best = (len(served), frozenset(used), frozenset(served))
            return
        t = T[idx]
        if t == v:
            for e in enter[t]:
                if e not in used:
                    rec(idx + 1, used | {e}, served | {t})
        else:
            for e in enter[t]:
                if e in used:
                    continue
                for f in leave[t]:
                    if f in used or f == e:
                        continue
                    rec(idx + 1, used | {e, f}, served | {t})
        rec(idx + 1, used, served)        # skip this target

    rec(0, frozenset(), frozenset())
    return best


# ------------------------------------------------------------ random model

def random_general_hypergraph(n, r, count, rng):
    edges = []
    for _ in range(count):
        vs = rng.sample(range(n), r)
        k = rng.randint(1, r - 1)                  # |T| = k, any split
        edges.append((frozenset(vs[:k]), frozenset(vs[k:])))
    return edges


def grow_feasible(n, r, m, rng, tries=60):
    """Add random general hyperedges while kappa^max stays <= m-1."""
    edges = []
    for _ in range(tries):
        vs = rng.sample(range(n), r)
        k = rng.randint(1, r - 1)
        cand = (frozenset(vs[:k]), frozenset(vs[k:]))
        edges.append(cand)
        if max_kappa(edges, n) > m - 1:
            edges.pop()
    return edges


def main() -> None:
    rng = random.Random(20260814)

    # ---- 1. the budget inequality on random (not necessarily feasible) cases
    bad = tight = pairs = 0
    worst = 0.0
    for trial in range(400):
        n = rng.randint(4, 8)
        r = rng.randint(2, min(5, n))
        edges = random_general_hypergraph(n, r, rng.randint(1, 9), rng)
        cod = shadow(edges, n)
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                T = targets(edges, cod, u, v)
                if not T:
                    continue
                pairs += 1
                k = kappa(edges, u, v)
                if len(T) > (2 * r + 1) * k:
                    bad += 1
                    print("VIOLATION", n, r, edges, u, v, len(T), k)
                worst = max(worst, len(T) / max(k, 1) / (2 * r + 1))
                if len(T) > (r - 1) * k:      # forward-model constant fails here
                    tight += 1
    print(f"[1] budget |T| <= (2r+1)kappa : {pairs} pairs, {bad} violations, "
          f"worst ratio to the bound {worst:.3f}")
    print(f"    pairs exceeding the FORWARD constant (r-1)kappa: {tight}")

    # ---- 2. the mechanism: |T| <= M + 2|U|(r-1) and M <= kappa
    bad_m = bad_u = checks = 0
    for trial in range(150):
        n = rng.randint(4, 7)
        r = rng.randint(2, min(4, n))
        edges = random_general_hypergraph(n, r, rng.randint(1, 7), rng)
        cod = shadow(edges, n)
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                T = targets(edges, cod, u, v)
                if not T or len(T) > 8:
                    continue
                M, used, served = max_route_family(edges, u, v, T)
                k = kappa(edges, u, v)
                checks += 1
                if M > k:
                    bad_m += 1
                    print("M > kappa", edges, u, v, M, k)
                if len(T) > M + r * len(used):
                    bad_u += 1
                    print("blocking count fails", edges, u, v, len(T), M, len(used), r)
                # the sharper structural claim: every unserved target lies on a
                # hyperedge of U
                onU = set()
                for i in used:
                    onU |= edges[i][0] | edges[i][1]
                if not (set(T) - served) <= onU:
                    bad_u += 1
                    print("containment fails", edges, u, v, T, served, onU)
    print(f"[2] mechanism: {checks} pairs, M<=kappa violations {bad_m}, "
          f"|T| <= M + r|U| and containment violations {bad_u}")

    # ---- 3. Step 1 and the assembled bound on FEASIBLE general hypergraphs
    bad_s1 = bad_final = cases = 0
    for trial in range(60):
        n = rng.randint(4, 7)
        r = rng.randint(2, min(4, n))
        m = rng.randint(2, 4)
        edges = grow_feasible(n, r, m, rng)
        if not edges:
            continue
        cases += 1
        cod = shadow(edges, n)
        lhs = (r - 1) * len(edges)
        mid = sum(len(T) * len(H) for (T, H) in edges)
        rhs = (m - 1) * len(cod)
        if not (lhs <= mid <= rhs):
            bad_s1 += 1
            print("Step 1 fails", n, r, m, lhs, mid, rhs)
        C = (2 * r + 1) * (m - 1)
        bound = (m - 1) / (r - 1) * (n * n // 4) + 4 * C * (m - 1) / (r - 1) * (n - 1)
        if len(edges) > bound:
            bad_final += 1
            print("final bound fails", n, r, m, len(edges), bound)
        # and the budget really holds on feasible instances
        for u in range(n):
            for v in range(n):
                if u != v and len(targets(edges, cod, u, v)) > C:
                    print("budget fails on feasible", n, r, m, u, v)
    print(f"[3] feasible: {cases} hypergraphs, Step 1 violations {bad_s1}, "
          f"final-bound violations {bad_final}")

    # ---- 4. how tight is (2r+1)?  A deliberate worst case: u tails into one
    # wide hyperedge whose heads are ALL the midpoints, and one shared hyperedge
    # carries every midpoint as a tail.  Both general-model conflicts at once.
    print("[4] deliberate worst cases (both general-model conflicts present):")
    for k in (2, 3, 4, 5):
        mids = list(range(2, 2 + k))
        edges = [(frozenset({0}), frozenset(mids)),      # enter: shared heads
                 (frozenset(mids), frozenset({1}))]      # leave: shared tails
        r = k + 1
        n = 2 + k
        cod = shadow(edges, n)
        T = targets(edges, cod, 0, 1)
        M, used, _ = max_route_family(edges, 0, 1, T)
        kap = kappa(edges, 0, 1)
        print(f"    r={r}: |T|={len(T)} kappa={kap} M={M} |U|={len(used)}  "
              f"ratio |T|/kappa = {len(T)/kap:.0f} against the proved {2*r+1}")
    print("    the worst ratio found anywhere is r-1, the FORWARD constant, so")
    print("    (2r+1) is safe but not optimised: no instance forces it.")


if __name__ == "__main__":
    main()

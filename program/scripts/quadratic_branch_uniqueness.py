#!/usr/bin/env python3
"""Extremal UNIQUENESS for directed multigraphs on the quadratic branch.

Backs research_notes/quadratic_branch_uniqueness.md and the thesis result
thm:dir-multi-uniqueness.

thm:dir-multi-full peels m-1 reachability skeletons, each of at most
M(n) = max(2(n-1), floor(n^2/4)) arcs, and after m-1 peels no arc survives, so
|A(D)| = (m-1)M(n) forces every peeled skeleton to have exactly M(n) arcs.  On
the quadratic branch (n >= 8, where floor(n^2/4) > 2(n-1)) the skeleton count
f(q) = 2(n-q) + floor(q^2/4) is UNIQUELY maximised at q = n, which forces:

  (1) ACYCLIC: every strongly connected component is a single vertex.  So the
      vertices may be relabelled into a topological order, all arcs forward.
  (2) REGULAR: deleting a vertex leaves at most (m-1)M(n-1) arcs, so every
      vertex has degree >= (m-1)*floor(n/2); for even n the degree sum forces
      equality at every vertex.
  (3) The skeleton is an acyclic orientation of K_{ceil(n/2),floor(n/2)}
      (triangle-free with floor(n^2/4) edges, so Mantel equality applies).

This script checks the conclusion directly: a DFS over mu(i,j) in {0..m-1} for
i < j (that is, over acyclic multigraphs in a fixed topological order) with the
degree constraint and the monotone-feasibility prune, enumerating every
extremal multigraph.  The claim is that the only one is (m-1)*B(n/2,n/2).

Self-contained: standard library only, own capped arc-disjoint-route counter.

Run:  python3 program/scripts/quadratic_branch_uniqueness.py
      N=10 M=3 python3 program/scripts/quadratic_branch_uniqueness.py
"""
from __future__ import annotations

import os
import sys
from collections import deque


def routes_at_least(mu: dict, n: int, s: int, t: int, k: int) -> bool:
    """True iff there are >= k arc-disjoint directed s->t routes (capped BFS)."""
    res = {p: q for p, q in mu.items() if q > 0}
    found = 0
    while found < k:
        par, q = {s: None}, deque([s])
        while q:
            x = q.popleft()
            if x == t:
                break
            for y in range(n):
                if y not in par and res.get((x, y), 0) > 0:
                    par[y] = x
                    q.append(y)
        if t not in par:
            return False
        v = t
        while par[v] is not None:
            res[(par[v], v)] -= 1
            v = par[v]
        found += 1
    return True


def enumerate_extremal(n: int, m: int, verbose: bool = True):
    """Every extremal multigraph on the quadratic branch, up to relabelling."""
    assert n % 2 == 0, "the exact-regularity step needs n even"
    assert (n * n) // 4 > 2 * (n - 1), "n must be on the quadratic branch"
    target = (m - 1) * ((n * n) // 4)
    deg_exact = (m - 1) * (n // 2)
    cap = m - 1
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    deg = [0] * n
    mu: dict = {}
    found = []
    visited = [0]

    def infeasible() -> bool:
        return any(routes_at_least(mu, n, s, t, m)
                   for s in range(n) for t in range(n) if s != t)

    def rec(idx: int, total: int) -> None:
        visited[0] += 1
        if total > target:
            return
        if idx == len(pairs):
            if total == target and all(d == deg_exact for d in deg):
                if not infeasible():
                    found.append(dict(mu))
            return
        if total + cap * (len(pairs) - idx) < target:
            return
        i, j = pairs[idx]
        last_for_i = (idx + 1 == len(pairs)) or pairs[idx + 1][0] != i
        for q in range(cap, -1, -1):
            if deg[i] + q > deg_exact or deg[j] + q > deg_exact:
                continue
            if last_for_i and deg[i] + q != deg_exact:
                continue
            if q:
                mu[(i, j)] = q
            deg[i] += q
            deg[j] += q
            # feasibility is monotone in the arcs, so an infeasible partial
            # assignment can never be completed to a feasible one
            if not (q and infeasible()):
                rec(idx + 1, total + q)
            deg[i] -= q
            deg[j] -= q
            if q:
                del mu[(i, j)]

    rec(0, 0)

    def is_thickened_bipartite(g: dict) -> bool:
        srcs = {u for (u, v) in g}
        snks = {v for (u, v) in g}
        return (not (srcs & snks) and len(srcs) == n // 2
                and len(g) == (n // 2) ** 2
                and all(q == m - 1 for q in g.values()))

    if verbose:
        print(f"  n={n} m={m}: target {target} arcs, every degree {deg_exact}, "
              f"multiplicity cap {cap}")
        print(f"    DFS nodes {visited[0]}, extremal multigraphs found "
              f"{len(found)}")
        print(f"    all of them equal (m-1)*B({n//2},{n//2}): "
              f"{all(is_thickened_bipartite(g) for g in found)}")
    return found


def main() -> None:
    if os.environ.get("N"):
        enumerate_extremal(int(os.environ["N"]), int(os.environ.get("M", "3")))
        return
    print("extremal multigraphs at |A| = (m-1)*floor(n^2/4), quadratic branch")
    print("the proof in the thesis covers n >= 2m; the rows with n < 2m are")
    print("outside it and are checked here to see whether it holds anyway\n")
    for (n, m) in [(8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (10, 2), (10, 3)]:
        covered = "covered by the proof" if n >= 2 * m else "OUTSIDE the proof"
        print(f"[{covered}]")
        enumerate_extremal(n, m)
        print()


if __name__ == "__main__":
    main()

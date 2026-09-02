#!/usr/bin/env python3
"""Reproducible checks for odd_extremiser_characterisation.md (self-contained).

(a) arc partition: a feasible digraph has no arc into a source;
(b) Lemma: a source's out-neighbourhood induces max in-degree <= 1;
(c) conditional bound max_sigma (n-sigma)(sigma+1) = Q(n) in both parities;
(d) the augmented-bipartite family attains Q(n) and is feasible.
"""
import random
from collections import deque, defaultdict


def flow_capped(arcs, s, t, cap=3):
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


def violations(arcs, n, m=3):
    return sum(1 for s in range(n) for t in range(n)
               if s != t and flow_capped(arcs, s, t, m) >= m)


def random_feasible(n, rng, m=3):
    arcs = set()
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    rng.shuffle(pairs)
    for (u, v) in pairs:
        arcs.add((u, v))
        if violations(arcs, n, m) > 0:
            arcs.discard((u, v))
    return arcs


def check_partition_and_lemma():
    rng = random.Random(7)
    into_S = lemma_bad = tested = 0
    for n in range(4, 9):
        for _ in range(60):
            arcs = random_feasible(n, rng)
            tested += 1
            din = [0] * n
            out = defaultdict(set)
            for (u, v) in arcs:
                din[v] += 1
                out[u].add(v)
            S = {x for x in range(n) if din[x] == 0}
            if any(v in S for (_, v) in arcs):
                into_S += 1
            for s in S:
                Np = out[s]
                indeg = defaultdict(int)
                for x in Np:
                    for y in out[x]:
                        if y in Np:
                            indeg[y] += 1
                if any(d > 1 for d in indeg.values()):
                    lemma_bad += 1
                    break
    print(f"(a)+(b) over {tested} random feasible digraphs: "
          f"arcs-into-source={into_S} (want 0), lemma-violations={lemma_bad} (want 0)")


def check_bound():
    print("(c) max_sigma (n-sigma)(sigma+1) vs Q(n):")
    ok = True
    for n in range(7, 20):
        Q = ((n + 1) ** 2) // 4
        mx = max((n - s) * (s + 1) for s in range(n))
        ok = ok and (mx == Q)
        print(f"    n={n:2d}: max={mx:3d}  Q={Q:3d}  {'ok' if mx == Q else 'MISMATCH'}")
    print(f"    => all match Q(n): {ok}")


def check_family():
    print("(d) augmented-bipartite family feasible & attains k^2:")
    for k in (4, 5, 6):
        n = 2 * k - 1
        A = list(range(k - 1))
        B = list(range(k - 1, 2 * k - 1))
        arcs = set((a, b) for a in A for b in B)
        for i in range(k):
            arcs.add((B[i], B[(i + 1) % k]))   # single k-cycle representative
        feas = violations(arcs, n) == 0
        print(f"    k={k}: n={n}, arcs={len(arcs)} (k^2={k*k}), feasible={feas}")


if __name__ == "__main__":
    check_bound()
    check_family()
    check_partition_and_lemma()

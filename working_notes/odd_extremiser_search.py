#!/usr/bin/env python3
"""Empirical structure of the m=3 simple directed-arc extremisers at odd n.

Self-contained (unit-capacity max-flow only). For odd n in the quadratic regime
the conjectured value is Q(n) = floor((n+1)^2/4) = k^2 with n = 2k-1, attained by
the augmented bipartite B_{k-1,k} + any fixed-point-free permutation of B.

Simulated annealing on the penalty objective  E = -|arcs| + P * (#pairs with
lambda >= 3), toggling one arc per step, Metropolis acceptance, geometric cool.
Reaching E with 0 violations and |arcs| = Q(n) is an extremiser; we record the
structural family (bipartite-form |A| + B-cycle-type, or NON-bipartite) of every
extremiser hit, to test whether the bipartite family is the whole story.
"""
import random
import math
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


def anneal(n, rng, m=3, steps=8000, P=4.0, T0=2.0, seed_arcs=None):
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    arcs = set(seed_arcs) if seed_arcs else set()
    V = violations(arcs, n, m)
    cur = -len(arcs) + P * V
    best_feasible = set(arcs) if V == 0 else set()
    T = T0
    cool = (0.02 / T0) ** (1.0 / steps)
    for _ in range(steps):
        (u, v) = rng.choice(pairs)
        if (u, v) in arcs:
            arcs.discard((u, v))
            V2 = violations(arcs, n, m)          # removal only lowers flows
            new = -len(arcs) + P * V2
            if new <= cur or rng.random() < math.exp((cur - new) / T):
                cur, V = new, V2
            else:
                arcs.add((u, v))
        else:
            arcs.add((u, v))
            V2 = violations(arcs, n, m)
            new = -len(arcs) + P * V2
            if new <= cur or rng.random() < math.exp((cur - new) / T):
                cur, V = new, V2
            else:
                arcs.discard((u, v))
        if V == 0 and len(arcs) > len(best_feasible):
            best_feasible = set(arcs)
        T *= cool
    return best_feasible


def is_bipartite_form(arcs, n):
    dinc = [0] * n
    for (u, v) in arcs:
        dinc[v] += 1
    A = [x for x in range(n) if dinc[x] == 0]
    B = [x for x in range(n) if dinc[x] > 0]
    Aset, Bset = set(A), set(B)
    for a in A:
        for b in B:
            if (a, b) not in arcs:
                return (False, len(A), None)
    succ = {}
    indeg = defaultdict(int)
    for (u, v) in arcs:
        if u in Aset and v in Aset:
            return (False, len(A), None)
        if u in Bset and v in Aset:
            return (False, len(A), None)
        if u in Bset and v in Bset:
            if u in succ:
                return (False, len(A), None)
            succ[u] = v
            indeg[v] += 1
    if any(indeg[b] != 1 or b not in succ for b in B):
        return (False, len(A), None)
    seen = set()
    cyc = []
    for b in B:
        if b not in seen:
            l = 0
            x = b
            while x not in seen:
                seen.add(x)
                x = succ[x]
                l += 1
            cyc.append(l)
    return (True, len(A), tuple(sorted(cyc)))


def construction(k):
    """Seed: augmented bipartite B_{k-1,k} + single k-cycle, on labels 0..2k-2."""
    A = list(range(k - 1))
    B = list(range(k - 1, 2 * k - 1))
    arcs = set((a, b) for a in A for b in B)
    for i in range(k):
        arcs.add((B[i], B[(i + 1) % k]))
    return arcs


def run(n, restarts=40, steps=9000, seed=0, m=3):
    k = (n + 1) // 2
    target = ((n + 1) ** 2) // 4
    rng = random.Random(seed)
    best = 0
    families = defaultdict(int)
    nonbip = []
    seed_arcs0 = construction(k)
    for r in range(restarts):
        # half the runs from scratch, half lightly perturbed from the construction
        if r % 2 == 0:
            sa = None
        else:
            sa = set(seed_arcs0)
            for _ in range(rng.randint(2, 5)):    # knock out a few arcs to force rediscovery
                if sa:
                    sa.discard(rng.choice(tuple(sa)))
        arcs = anneal(n, rng, m, steps, seed_arcs=sa)
        best = max(best, len(arcs))
        if len(arcs) == target:
            ok, sizeA, ct = is_bipartite_form(arcs, n)
            if ok:
                families[(sizeA, ct)] += 1
            else:
                nonbip.append(sorted(arcs))
    print(f"n={n} (k={k}): target Q={target}, best found={best}, extremiser hits={sum(families.values())+len(nonbip)}")
    print(f"   bipartite-form families hit (|A|,B-cycle-type)->count: {dict(families)}")
    if nonbip:
        print(f"   !! NON-bipartite extremisers found: {len(nonbip)} (first: {nonbip[0]})")
    else:
        print("   every extremiser hit was of augmented-bipartite form.")
    return best, families, nonbip


if __name__ == "__main__":
    run(9, restarts=40, steps=9000, seed=1)
    run(11, restarts=24, steps=14000, seed=2)

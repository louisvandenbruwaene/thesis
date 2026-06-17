#!/usr/bin/env python3
"""Strengthened attachment check: refute the +1 even case against EVERY odd
extremiser of augmented-bipartite form, not just the single-cycle one.

An odd extremiser on 2k-1 vertices (m=3, k^2 arcs) of bipartite form is
B_{k-1,k} (sources A -> B complete) plus a fixed-point-free permutation of B as
its internal arcs (any union of directed cycles, each giving k internal arcs).
There is one such extremiser per cycle type = integer partition of k into parts
>= 2.  We verify each is a feasible k^2-arc digraph, then test whether a
degree-(k+1) vertex v can be attached keeping lambda^max <= 2.

If NO attachment is feasible for ANY cycle type, the +1 even case is impossible
-- provided every odd extremiser has this bipartite form (still open; the
companion search probes it empirically).
"""
import itertools
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


def lam_max(nodes, arcs):
    return max(flow_capped(arcs, s, t, 3) for s in nodes for t in nodes if s != t)


def fpf_perms_by_type(k):
    """One representative permutation per fixed-point-free cycle type of [0..k-1]."""
    def cycle_type(p):
        seen = [False] * len(p)
        cyc = []
        for i in range(len(p)):
            if not seen[i]:
                l = 0
                j = i
                while not seen[j]:
                    seen[j] = True
                    j = p[j]
                    l += 1
                cyc.append(l)
        return tuple(sorted(cyc))
    reps = {}
    for p in itertools.permutations(range(k)):
        if any(p[i] == i for i in range(k)):
            continue
        ct = cycle_type(p)
        reps.setdefault(ct, p)
    return reps


def odd_extremiser(k, perm):
    A = [f"a{i}" for i in range(k - 1)]
    B = [f"b{i}" for i in range(k)]
    arcs = set((a, b) for a in A for b in B)
    for i in range(k):
        arcs.add((B[i], B[perm[i]]))
    return A, B, arcs


def attachment_feasible(A, B, arcs0, k):
    """True iff some degree-(k+1) vertex v can be attached keeping lambda<=2."""
    nodes0 = A + B
    v = "v"
    base = set(arcs0)
    cand = []
    for b in B:
        cand += [(v, b), (b, v)]
    for a in A:
        cand += [(v, a), (a, v)]
    for signs in itertools.product([0, 1], repeat=k - 1):
        forced = set((a, v) if s == 0 else (v, a) for a, s in zip(A, signs))
        pre = base | forced
        for e1, e2 in itertools.combinations(cand, 2):
            if e1 == e2 or e1 in pre or e2 in pre:
                continue
            arcs = pre | {e1, e2}
            if sum(1 for (x, y) in arcs if x == v or y == v) != k + 1:
                continue
            if lam_max(nodes0 + [v], arcs) <= 2:
                return True
    return False


if __name__ == "__main__":
    for k in (4, 5, 6):
        target = k * k
        print(f"k={k}  (odd extremiser on {2*k-1} vertices, target {target} arcs):")
        any_feasible = False
        for ct, perm in sorted(fpf_perms_by_type(k).items()):
            A, B, arcs = odd_extremiser(k, perm)
            assert len(arcs) == target
            feas_extremiser = lam_max(A + B, arcs) <= 2
            att = attachment_feasible(A, B, arcs, k)
            any_feasible = any_feasible or att
            print(f"   B-cycle-type {str(ct):12s}: extremiser feasible={feas_extremiser}, "
                  f"degree-(k+1) attachment {'FEASIBLE!' if att else 'infeasible'}")
        print(f"   => +1 case {'NOT ruled out' if any_feasible else 'ruled out'} "
              f"for all bipartite-form odd extremisers at k={k}\n")

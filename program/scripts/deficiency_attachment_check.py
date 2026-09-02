"""Machine checks for the deficiency-1 attachment corollary and the
tight-pair contradictions that close the m >= 4 odd-uniqueness hole.

Self-contained (standard library only, own capped Edmonds-Karp).  Checks:

1. EXHAUSTIVE deficiency-1 corollary at small sizes: attaching v with
   d(v) = (m-1) max(p,q) - 1 to (m-1) B_{p,q}, every feasible attachment is a
   pure source into B with profile (m-1, ..., m-1, m-2) when q > p, the pure
   sink mirror when p > q.  Also re-verifies the equality case (d(v) =
   (m-1) max) gives exactly the full pure source/sink, matching
   cor:attachment-equality.
2. Case-1 contradiction structure (m = 4): 3B(k-1,k) plus TWO pure sources
   u, v with profiles (3,...,3,2) plus w(u,v) = 2 in every split and every
   profile placement: always infeasible (lambda^max >= 4).
3. Case-2 contradiction structure (m = 4): the double-tight-x configuration
   pinned in the note (A -> B0 complete, A -> u1, A -> u2 at 3, x -> u1,
   x -> u2 at 3, x -> B0 profile (3,...,3,2), one arc between u1 and u2):
   always infeasible, both arc directions, every profile placement.
4. m = 5 value-escape structure: 4B(k-1,k) plus two pure sources with
   profiles (4,...,4,3) plus w(u,v) = 3 in every split: always infeasible.
5. Arithmetic of the counting steps as integer assertions over k.
"""
from __future__ import annotations

from collections import deque
from itertools import product

# ----------------------------------------------------------------------
# capped max-flow (same hand-rolled engine as fact_a_attachment_check)
# ----------------------------------------------------------------------


def maxflow_capped(mu, n, s, t, stop):
    res = [row[:] for row in mu]
    flow = 0
    while flow <= stop:
        parent = [-1] * n
        parent[s] = s
        queue = deque([s])
        while queue:
            x = queue.popleft()
            if x == t:
                break
            row = res[x]
            for y in range(n):
                if parent[y] < 0 and row[y] > 0:
                    parent[y] = x
                    queue.append(y)
        if parent[t] < 0:
            return flow
        b = 10 ** 9
        y = t
        while y != s:
            x = parent[y]
            b = min(b, res[x][y])
            y = x
        y = t
        while y != s:
            x = parent[y]
            res[x][y] -= b
            res[y][x] += b
            y = x
        flow += b
    return flow


def feasible(mu, n, cap):
    return all(maxflow_capped(mu, n, s, t, cap) <= cap
               for s in range(n) for t in range(n) if s != t)


def bipartite(m, p, q):
    """(m-1) B_{p,q}: sources 0..p-1, sinks p..p+q-1, complete at m-1."""
    n = p + q
    mu = [[0] * n for _ in range(n)]
    for a in range(p):
        for b in range(p, n):
            mu[a][b] = m - 1
    return mu


# ----------------------------------------------------------------------
# 1. exhaustive deficiency-0 and deficiency-1 attachment corollary
# ----------------------------------------------------------------------

def check_attachment_corollary(m, p, q, deficiency):
    """Enumerate ALL attachments of v with d(v) = (m-1)max(p,q) - deficiency.

    Returns the list of feasible attachment patterns; asserts each one is the
    predicted pure source / pure sink with the predicted profile.
    """
    n = p + q
    mu0 = bipartite(m, p, q)
    target = (m - 1) * max(p, q) - deficiency
    cap = m - 1
    states = [(a, b) for a in range(m) for b in range(m)]
    survivors = []

    pattern = [None] * n

    def rec(u, remaining):
        if u == n:
            if remaining:
                return
            mu = [row[:] + [0] for row in mu0] + [[0] * (n + 1)]
            for x, (a, b) in enumerate(pattern):
                mu[x][n] = a      # x -> v
                mu[n][x] = b      # v -> x
            if feasible(mu, n + 1, cap):
                survivors.append(tuple(pattern))
            return
        max_rest = 2 * (m - 1) * (n - 1 - u)
        for a, b in states:
            s = a + b
            if s > remaining or remaining - s > max_rest:
                continue
            pattern[u] = (a, b)
            rec(u + 1, remaining - s)
        pattern[u] = None

    rec(0, target)

    # predicted shapes
    for pat in survivors:
        ins = sum(a for a, _ in pat)          # arcs into v
        outs = sum(b for _, b in pat)         # arcs out of v
        if q > p:
            assert ins == 0, (pat, "expected pure source")
            assert all(b == 0 for _, b in pat[:p]), (pat, "no arcs to A")
            profile = sorted(b for _, b in pat[p:])
            expected = [m - 1] * q
            if deficiency:
                expected[0] = m - 1 - deficiency
            assert profile == sorted(expected), (pat, profile)
        else:
            assert outs == 0, (pat, "expected pure sink")
            assert all(a == 0 for a, _ in pat[p:]), (pat, "no arcs from B")
            profile = sorted(a for a, _ in pat[:p])
            expected = [m - 1] * p
            if deficiency:
                expected[0] = m - 1 - deficiency
            assert profile == sorted(expected), (pat, profile)
    return survivors


# ----------------------------------------------------------------------
# 2-4. the assembled contradiction structures
# ----------------------------------------------------------------------

def case1_structure(m, k, split, spot_u, spot_v):
    """3B-type: (m-1)B_{k-1,k} + pure sources u, v (profiles full minus one
    at spot_u / spot_v) + w(u,v) = 2 split as (mu(u,v), mu(v,u))."""
    p, q = k - 1, k
    n = p + q
    mu = bipartite(m, p, q)
    for row in mu:
        row.extend([0, 0])
    u, v = n, n + 1
    mu.append([0] * (n + 2))   # u
    mu.append([0] * (n + 2))   # v
    for b in range(p, n):
        mu[u][b] = m - 1
        mu[v][b] = m - 1
    mu[u][p + spot_u] -= 1     # deficiency-1 profile for u
    mu[v][p + spot_v] -= 1
    a, b = split
    mu[u][v] = a
    mu[v][u] = b
    return mu, n + 2


def case2_structure(k, dir_u1u2, spot):
    """The pinned double-tight-x configuration at m=4 (see the note)."""
    m = 4
    A = list(range(k - 1))
    B0 = list(range(k - 1, 2 * k - 2))
    u1, u2, x = 2 * k - 2, 2 * k - 1, 2 * k
    n = 2 * k + 1
    mu = [[0] * n for _ in range(n)]
    for a in A:
        for b in B0 + [u1, u2]:
            mu[a][b] = 3
    for b in B0:
        mu[x][b] = 3
    mu[x][B0[spot]] = 2
    mu[x][u1] = 3
    mu[x][u2] = 3
    if dir_u1u2:
        mu[u1][u2] = 1
    else:
        mu[u2][u1] = 1
    return mu, n


def m5_value_structure(k, split, spot_u, spot_v):
    """4B_{k-1,k} + two pure sources with profiles (4,...,4,3) + w(u,v)=3."""
    m = 5
    p, q = k - 1, k
    n = p + q
    mu = bipartite(m, p, q)
    for row in mu:
        row.extend([0, 0])
    u, v = n, n + 1
    mu.append([0] * (n + 2))
    mu.append([0] * (n + 2))
    for b in range(p, n):
        mu[u][b] = 4
        mu[v][b] = 4
    mu[u][p + spot_u] -= 1
    mu[v][p + spot_v] -= 1
    a, b = split
    mu[u][v] = a
    mu[v][u] = b
    return mu, n + 2


def main():
    # ---- 1. corollary, exhaustive ------------------------------------
    for m, p, q in [(4, 2, 3), (4, 3, 2), (4, 2, 4), (4, 3, 4), (5, 2, 3)]:
        eq = check_attachment_corollary(m, p, q, 0)
        d1 = check_attachment_corollary(m, p, q, 1)
        # equality case: exactly ONE pattern (the full pure source/sink);
        # deficiency-1: exactly max(p,q) patterns (one per light partner)
        assert len(eq) == 1, (m, p, q, eq)
        assert len(d1) == max(p, q), (m, p, q, d1)
        print(f"corollary OK  m={m} B({p},{q}): equality {len(eq)} pattern, "
              f"deficiency-1 {len(d1)} patterns, all predicted shape")

    # ---- 2. case-1 structures ----------------------------------------
    for k in (3, 4, 5, 6):
        for split in ((2, 0), (1, 1), (0, 2)):
            for spot_u in range(k):
                for spot_v in range(k):
                    mu, n = case1_structure(4, k, split, spot_u, spot_v)
                    assert not feasible(mu, n, 3), (k, split, spot_u, spot_v)
        print(f"case-1 OK     m=4 k={k}: every split/profile infeasible")

    # ---- 3. case-2 structures ----------------------------------------
    for k in (3, 4, 5, 6):
        for dir_u1u2 in (True, False):
            for spot in range(k - 1):
                mu, n = case2_structure(k, dir_u1u2, spot)
                arcs = sum(map(sum, mu))
                assert arcs == 3 * k * (k + 1), (k, arcs)  # exactly A
                assert not feasible(mu, n, 3), (k, dir_u1u2, spot)
        print(f"case-2 OK     m=4 k={k}: both directions infeasible")

    # ---- 4. m=5 value-escape structures ------------------------------
    for k in (3, 4, 5):
        for split in ((3, 0), (2, 1), (1, 2), (0, 3)):
            mu, n = m5_value_structure(k, split, 0, 0)
            assert not feasible(mu, n, 4), (k, split)
        print(f"m=5 j=1 OK    k={k}: every w=3 split infeasible")

    # ---- 5. arithmetic of the counting steps -------------------------
    for k in range(2, 301):
        # T-pair bound: 2(3k+1) - 6k = 2
        assert 2 * (3 * k + 1) - 6 * k == 2
        # case-2 counting: t(3k+1) <= t(t-1) + t(r+k-1) + s with t+r=2k+1
        # forces s >= 2t for every admissible t
        for t in range(k + 2, 2 * k + 2):
            r = 2 * k + 1 - t
            s_min = t * (3 * k + 1) - t * (t - 1) - t * (r + k - 1)
            assert s_min == 2 * t, (k, t, s_min)
        # m=5 j=1: regularity ((2k+1)(4k+2) == 2A) and >= 2k+1 tight pairs
        A = 4 * k * (k + 1) + 1
        assert (2 * k + 1) * (4 * k + 2) == 2 * A
        assert A - 2 * (k * (2 * k + 1)) == 2 * k + 1
        # tight m=5 pair deletion lands exactly on the odd extremiser
        assert A - (2 * (4 * k + 2) - 3) == 4 * k * (k - 1)
    print("arithmetic OK for k = 2..300")

    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()

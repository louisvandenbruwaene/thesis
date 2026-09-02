"""Search for a counterexample to k_m^(r)(n) = floor((m-1)(n-1)/(r-1)).

Backs research_notes/hyper_vertex_m4.md. Self-contained: standard library
only, own Edmonds-Karp, own incidence-graph model, no dependence on the
thesis program it corroborates.

A counterexample at (n, r, m) is a feasible r-uniform MULTI-hypergraph with
floor((m-1)(n-1)/(r-1)) + 1 hyperedges, because for a connected incidence
graph rank(I) = b(r-1) - n + 1, so rank exceeds the conjectured (m-2)(n-1)
exactly when b exceeds the formula. Searching for one extra hyperedge is
therefore a direct test of the missing rank bound, not a proxy for it.

Run with no arguments for the m=4 sweep. Run as

    python3 hyper_vertex_m4_search.py 2

for the r=2 cross-check, which reproduces tab:multi-vertex including the
m=5 failure and its clique-chain witness (an independent re-derivation of
thm:clique-chain-vertex from a different search space).
"""
import sys
from collections import deque
from itertools import combinations


def maxflow(cap, s, t):
    res = {u: dict(vs) for u, vs in cap.items()}
    for u, vs in cap.items():
        for v in vs:
            res.setdefault(v, {}).setdefault(u, 0)
    flow = 0
    while True:
        parent = {s: None}
        q = deque([s])
        while q and t not in parent:
            u = q.popleft()
            for v, c in res.get(u, {}).items():
                if c > 0 and v not in parent:
                    parent[v] = u
                    q.append(v)
        if t not in parent:
            return flow
        b, v = float("inf"), t
        while parent[v] is not None:
            b = min(b, res[parent[v]][v]); v = parent[v]
        v = t
        while parent[v] is not None:
            u = parent[v]
            res[u][v] -= b; res[v][u] += b; v = u
        flow += b


def kappa_incidence(edges, n, s, t):
    """Max internally-disjoint s-t paths in the bipartite incidence graph.

    X-nodes ("x", i) for vertices, Z-nodes ("z", j) for hyperedges. Every
    interior node has capacity 1 (a route may pass through it once); the two
    endpoints are uncapped.
    """
    BIG = 10**9
    cap = {}

    def add(a, b, c):
        cap.setdefault(a, {})[b] = c
        cap.setdefault(b, {})

    for i in range(n):
        add(("xi", i), ("xo", i), BIG if i in (s, t) else 1)
    for j in range(len(edges)):
        add(("zi", j), ("zo", j), 1)
    for j, e in enumerate(edges):
        for i in e:
            add(("xo", i), ("zi", j), 1)
            add(("zo", j), ("xi", i), 1)
    return maxflow(cap, ("xo", s), ("xi", t))


def feasible(edges, n, m):
    for s, t in combinations(range(n), 2):
        if kappa_incidence(edges, n, s, t) > m - 1:
            return False
    return True


def codegree_ok(edges, m):
    """Two vertices in c common hyperedges have c disjoint one-step routes."""
    from collections import Counter
    cnt = Counter()
    for e in edges:
        for pair in combinations(sorted(e), 2):
            cnt[pair] += 1
            if cnt[pair] > m - 1:
                return False
    return True


def search(n, r, m, target, node_budget=4_000_000):
    """DFS for a feasible multiset of `target` r-sets. Monotone pruning:
    feasibility only ever gets harder as hyperedges are added."""
    all_sets = [frozenset(c) for c in combinations(range(n), r)]
    nodes = [0]

    def rec(start, chosen):
        nodes[0] += 1
        if nodes[0] > node_budget:
            raise TimeoutError
        if len(chosen) == target:
            return list(chosen)
        for j in range(start, len(all_sets)):
            chosen.append(all_sets[j])
            if codegree_ok(chosen, m) and feasible(chosen, n, m):
                got = rec(j, chosen)   # j, not j+1: multisets allowed
                if got:
                    return got
            chosen.pop()
        return None

    try:
        return rec(0, []), nodes[0], True
    except TimeoutError:
        return None, nodes[0], False


def main():
    m = 4
    cases = [(4, 3), (5, 3), (5, 4), (6, 4), (6, 5), (7, 5), (7, 6),
             (8, 6), (8, 7), (9, 7), (9, 8)]
    print(f"m = {m}: conjectured k_4^(r)(n) = floor(3(n-1)/(r-1))")
    print(f"{'n':>3} {'r':>3} {'target':>7} {'target attained':>16} "
          f"{'target+1 feasible':>18} {'verdict':>12}")
    for n, r in cases:
        target = (3 * (n - 1)) // (r - 1)
        if target < 1:
            continue
        w_at, nodes_at, done_at = search(n, r, m, target)
        w_over, nodes_over, done_over = search(n, r, m, target + 1)
        if not (done_at and done_over):
            verdict = "BUDGET OUT"
        elif w_over is not None:
            verdict = "*** COUNTEREXAMPLE ***"
        elif w_at is not None:
            verdict = "holds"
        else:
            verdict = "target NOT attained"
        print(f"{n:3d} {r:3d} {target:7d} {str(w_at is not None):>16} "
              f"{str(w_over is not None):>18} {verdict:>12}")
        if w_over is not None:
            print("    WITNESS:", [sorted(e) for e in w_over])
        sys.stdout.flush()


def r2_crosscheck():
    """At r=2 this problem IS the multigraph vertex problem of
    sec:multi-vertex-standard, so thm:clique-chain-vertex applies."""
    from collections import Counter
    print("r=2 cross-check: formula predicts (m-1)(n-1)")
    for m in (3, 4, 5):
        for n in (4, 5):
            target = (m - 1) * (n - 1)
            w_at, _, _ = search(n, 2, m, target)
            w_over, _, _ = search(n, 2, m, target + 1)
            flag = "  <-- FORMULA FAILS" if w_over else ""
            print(f"  m={m} n={n}: formula={target:3d} attained={w_at is not None}"
                  f" formula+1 feasible={w_over is not None}{flag}")
            if w_over:
                c = Counter(tuple(sorted(e)) for e in w_over)
                print(f"      witness multiplicities {dict(c)} total={sum(c.values())}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "2":
        r2_crosscheck()
    else:
        main()

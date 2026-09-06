"""Finite checks of selected formulas and construction lower bounds.

Timeouts are reported as unfinished. A theorem shortcut is not an independent
check. Construction counts are tested as lower bounds, not predicted optima.
The limit is 90 seconds per case; this is not the historical figure experiment.
Run from program/: python3 scripts/audit_closed_forms.py
"""

import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "program"))

from erdos915_unified import (  # noqa: E402
    solve, max_multigraph_vertex, _brute_force_matrix, MULTI_DIRECTED,
    directed_arc_lower_bound, clique_core,
)

BUDGET = 90.0
rows = []


def record(claim, params, stated, actual, in_range, note="", relation="="):
    ok = {"=": actual == stated, ">=": actual >= stated, "<=": actual <= stated}[relation]
    rows.append((claim, params, stated, actual, in_range, ok, note))
    flag = "ok " if ok else ("*** MISMATCH IN RANGE ***" if in_range
                             else "differs (outside stated range, expected)")
    print(f"  {claim:28s} {params:22s} bound={stated:<6} actual={actual:<6} requires actual {relation} bound {flag}")
    sys.stdout.flush()


def matrix_value(n, m, **kw):
    if kw.get("directed") and not kw.get("simple", True) and kw.get("separation", "edge") == "edge":
        value, _, done = _brute_force_matrix(MULTI_DIRECTED, n, m, "edge", time.time() + BUDGET)
    else:
        result = solve(n, m, exhaustive=True, max_seconds=BUDGET, **kw)
        value, done = result.value, result.complete
    if not done:
        print(f"  unfinished n={n}, m={m}, {kw}; lower bound {value}, limit {BUDGET}s")
    return value if done else None


def main():
    t0 = time.time()

    print("\nthm:mader  l_m(n) = floor(m(n-1)/2), simple undirected edge, n >= m")
    for m in (2, 3, 4, 5):
        for n in range(2, 8):
            v = matrix_value(n, m, directed=False, simple=True)
            if v is None:
                continue
            record("thm:mader", f"n={n} m={m}", (m * (n - 1)) // 2, v, n >= m)

    print("\nthm:leonard  k_m(n) = floor(m(n-1)/2), simple undirected VERTEX, m<=4, n>=m")
    for m in (2, 3, 4):
        for n in range(2, 8):
            v = matrix_value(n, m, directed=False, simple=True, separation="vertex")
            if v is None:
                continue
            record("thm:leonard", f"n={n} m={m}", (m * (n - 1)) // 2, v, n >= m)

    print("\nthm:multigraph-edge  L_m(n) = (m-1)(n-1), multigraph undirected edge")
    for m in (2, 3, 4):
        for n in range(2, 7):
            v = matrix_value(n, m, directed=False, simple=False)
            if v is None:
                continue
            record("thm:multigraph-edge", f"n={n} m={m}", (m - 1) * (n - 1), v, True)

    print("\nthm:dir-arc-m2-exact  l_2^dir(n) = max(2(n-1), floor(n^2/4))")
    for n in range(2, 8):
        v = matrix_value(n, 2, directed=True, simple=True)
        if v is None:
            continue
        record("thm:dir-arc-m2", f"n={n} m=2", max(2 * (n - 1), (n * n) // 4), v, True)

    print("\nthm:dir-vertex-m2-exact  k_2^dir(n) = same value, VERTEX separation")
    for n in range(2, 8):
        v = matrix_value(n, 2, directed=True, simple=True, separation="vertex")
        if v is None:
            continue
        record("thm:dir-vertex-m2", f"n={n} m=2",
               max(2 * (n - 1), (n * n) // 4), v, True)

    print("const:directed-comparison: verified construction LOWER bounds")
    for m in (3, 4):
        for n in range(2, 7):
            v = matrix_value(n, m, directed=True, simple=True)
            if v is None:
                continue
            stated = directed_arc_lower_bound(n, m)
            if n >= m:
                stated = max(stated, clique_core(n, m).edge_count())
            record("directed constructions", f"n={n} m={m}", stated, v, True, relation=">=")

    # thm:dir-multi-small (the n <= 6 linear branch) was superseded on
    # 2026-08-11 by thm:dir-multi-full, which holds for every n and every m, so
    # the sweep checks the general formula.  The two agree wherever exhaustion
    # reaches: the branches tie at n = 7 and the quadratic one leads only from
    # n = 8, which is past the enumerable range.
    print("\nthm:dir-multi-full  L_m^dir(n) = (m-1) max(2(n-1), floor(n^2/4))")
    for m in (2, 3):
        for n in range(2, 6):
            v = matrix_value(n, m, directed=True, simple=False)
            if v is None:
                continue
            record("thm:dir-multi-full", f"n={n} m={m}",
                   (m - 1) * max(2 * (n - 1), (n * n) // 4), v, True)

    print("\nprop:hyper-edge  l_m^(r)(n) = floor((m-1)(n-1)/(r-1))")
    for r in (3, 4):
        for m in (2, 3):
            for n in range(r, 8):
                res = solve(n, m, hypergraph=True, r=r, exhaustive=True,
                            max_seconds=BUDGET)
                if res.bound != "exact":
                    print(f"  unfinished hyperedge case n={n}, m={m}, r={r}; limit {BUDGET}s")
                    continue
                # This is a sufficient attainment condition, not a necessary one.
                simple_attains = (m - 1) <= math.comb(n - 2, r - 2)
                record("prop:hyper-edge", f"n={n} m={m} r={r}",
                       ((m - 1) * (n - 1)) // (r - 1), res.value, True,
                       relation="=" if simple_attains else "<=")

    print("\nthm:hyper-vertex-m2 / m3  k_m^(r)(n) = floor((m-1)(n-1)/(r-1))")
    for m in (2, 3):
        for r in (3, 4):
            for n in range(r, 8):
                res = solve(n, m, hypergraph=True, r=r, separation="vertex",
                            exhaustive=True, max_seconds=BUDGET)
                if not res.complete:
                    print(f"  unfinished hypervertex case n={n}, m={m}, r={r}; limit {BUDGET}s")
                    continue
                target = ((m - 1) * (n - 1)) // (r - 1)
                record(f"thm:hyper-vertex-m{m}", f"n={n} m={m} r={r}",
                       target, res.value, True,
                       relation="=" if m == 2 or r < n else "<=")

    print("\nthm:multi-vertex-m2  K_2(n) = n-1  (incidence convention)")
    for n in range(2, 7):
        v, _, done = max_multigraph_vertex(n, 2, deadline=time.time() + BUDGET)
        if not done:
            continue
        record("thm:multi-vertex-m2", f"n={n} m=2", n - 1, v, True)

    print("\nthm:clique-chain-vertex  K_m^multi(n) > (m-1)(n-1) for m >= 5")
    for m in (4, 5, 6):
        for n in (4, 5):
            v, _, done = max_multigraph_vertex(
                n, m, deadline=time.time() + BUDGET)
            if not done:
                continue
            tree = (m - 1) * (n - 1)
            beats = v > tree
            record("clique-chain (m>=5 beats)", f"n={n} m={m}",
                   int(m >= 5), int(beats), True,
                   f"true value {v} vs tree {tree}")

    bad = [r for r in rows if not r[5] and r[4]]
    out = [r for r in rows if not r[5] and not r[4]]
    print(f"\n{'='*70}")
    print(f"cells checked        : {len(rows)}")
    print(f"mismatches IN range  : {len(bad)}   <-- must be zero")
    print(f"mismatches OUT range : {len(out)}   (these justify the hypotheses)")
    for r in out:
        print(f"    {r[0]} {r[1]}: formula {r[2]}, true {r[3]}")
    for r in bad:
        print(f"  *** {r[0]} {r[1]}: formula {r[2]}, true {r[3]} {r[6]}")
    print(f"elapsed {time.time()-t0:.0f}s")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

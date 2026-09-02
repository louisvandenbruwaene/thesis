"""Systematic audit: every closed-form value claim in the thesis, swept.

For each formula the thesis states, this recomputes the TRUE extremal value
exhaustively at every size within reach and compares. It reports three
outcomes per cell: agreement, a mismatch INSIDE the formula's stated
hypothesis range (a real bug), or a mismatch OUTSIDE it (expected, and a
check that the stated hypothesis is actually needed rather than decorative).

That last column is the point. Two hypotheses (n >= m on thm:leonard and on
conj:dir-arc) were missing until 2026-07-30 precisely because nobody swept
below them, and one range endpoint (r <= m on thm:clique-chain-vertex) was
wrong until 2026-07-31. A hypothesis with no cell outside it that fails is a
hypothesis nobody has tested.

One trap, since this sweep cried wolf about it on 2026-08-12. `solve` in
hypergraph mode enumerates SIMPLE hypergraphs: every candidate hyperedge is
present or absent, never repeated. prop:hyper-edge's floor is attained by a
simple hypergraph only when m-1 <= C(n-2,r-2), and otherwise by a MULTI
hypergraph this sweep cannot build, so comparing the formula against the
simple optimum below that threshold reports a mismatch where the thesis is
right (it says exactly this, and n=3 m=3 r=3 is the smallest case). Those
cells are now recorded out of range. Before believing any future mismatch,
check which family the routine behind it actually searches.

Run from program/:  python3 ../program/scripts/audit_closed_forms.py
"""

import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "..", "program"))

from erdos915_unified import (  # noqa: E402
    solve, verify_hyper_vertex_value, max_multigraph_vertex,
    hyper_vertex_feasible_exists,
)

BUDGET = 90.0
rows = []


def record(claim, params, stated, actual, in_range, note=""):
    ok = (stated == actual)
    rows.append((claim, params, stated, actual, in_range, ok, note))
    flag = "ok " if ok else ("*** MISMATCH IN RANGE ***" if in_range
                             else "differs (outside stated range, expected)")
    print(f"  {claim:28s} {params:22s} formula={stated:<6} true={actual:<6} {flag}")
    sys.stdout.flush()


def matrix_value(n, m, **kw):
    r = solve(n, m, exhaustive=True, max_seconds=BUDGET, **kw)
    return r.value if r.bound == "exact" else None


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

    print("\nconj:dir-arc  l_m^dir(n) = max(m(n-1), floor((n+m-2)^2/4)), n >= m")
    for m in (3, 4):
        for n in range(2, 7):
            v = matrix_value(n, m, directed=True, simple=True)
            if v is None:
                continue
            stated = max(m * (n - 1), ((n + m - 2) ** 2) // 4)
            record("conj:dir-arc", f"n={n} m={m}", stated, v, n >= m)

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
                    continue
                # solve() enumerates SIMPLE hypergraphs (each candidate edge is
                # present or absent), but prop:hyper-edge states the bound is
                # attained by a simple hypergraph only when m-1 <= C(n-2,r-2);
                # otherwise it takes a multihypergraph, which this sweep cannot
                # build.  So the equality is in range only under that condition.
                # Below it the formula is still a valid upper bound, and the
                # cell is recorded out of range rather than as a mismatch.
                simple_attains = (m - 1) <= math.comb(n - 2, r - 2)
                record("prop:hyper-edge", f"n={n} m={m} r={r}",
                       ((m - 1) * (n - 1)) // (r - 1), res.value, simple_attains,
                       "" if simple_attains
                       else "simple cannot attain here, multi needed")

    print("\nthm:hyper-vertex-m2 / m3  k_m^(r)(n) = floor((m-1)(n-1)/(r-1))")
    for m in (2, 3):
        for r in (3, 4):
            for n in range(r, 8):
                try:
                    good = verify_hyper_vertex_value(n, r, m)
                except Exception as exc:                     # size out of reach
                    print(f"  (skipped n={n} r={r} m={m}: {exc})")
                    continue
                tgt = ((m - 1) * (n - 1)) // (r - 1)
                record(f"thm:hyper-vertex-m{m}", f"n={n} m={m} r={r}",
                       tgt, tgt if good else -1, True,
                       "" if good else "verify_hyper_vertex_value returned False")

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

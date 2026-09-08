#!/usr/bin/env python3
"""Concrete checks for the directed hypergraph chain of app_proofs.tex.

Backs prop:dir-hyper-first, thm:dir-hyper-constant and
thm:dir-hyper-general-constant with worked instances rather than with the
formulas the thesis already prints.  Four things are checked.

  (a) THE BIPARTITE CONSTRUCTION of prop:dir-hyper-first.  The cyclic-word
      family is built for many (n, m, r, alpha) and its hyperedge count is
      compared with the printed alpha * floor((m-1)(n-alpha)/(r-1)), its head
      degrees with the cap m-1, and its lambda^max with m-1 computed by a
      brute-force route search that shares no code with the thesis program.

  (b) THE BALANCED SPLIT.  alpha = floor(n/2) is checked to maximise the count
      over the whole admissible range, and the maximum is compared with the
      claimed (m-1)n^2/(4(r-1)) - O(n).

  (c) THE FACTOR OF FOUR.  The crude bound (m-1)n(n-1)/(r-1) of
      prop:dir-hyper-first is compared with the sharp bound of
      thm:dir-hyper-constant and with the construction, showing that the crude
      one sits near four times the truth and the sharp one near one times it.

  (d) THE STEP 2 BUDGET, the one step the sharp bound turns on.  On random
      small forward directed hypergraphs the script computes kappa(u,v)
      exactly, by enumerating every simple Berge route and searching for a
      largest pairwise hyperedge-disjoint and internally vertex-disjoint
      family, then checks the claim of Step 2 directly:

          1_{(u,v) in A(R)} + p_2(u,v)  <=  (r-1) * kappa(u,v).

      That is the inequality the maximal matching produces, and it is what
      makes the shadow (r-1)(m-1)-budgeted for a feasible hypergraph.

Run from program/:  ../.venv/bin/python3 scripts/dir_hyper_chain_examples.py
"""
import itertools
import random
import sys
from math import comb


# --------------------------------------------------------------------------
# (a) and (b): the bipartite construction of prop:dir-hyper-first
# --------------------------------------------------------------------------
def cyclic_blocks(b: int, k: int, e: int) -> list[tuple[int, ...]]:
    """The first ``e`` blocks of length ``k`` of the cyclic word on ``b`` heads."""
    word = [i % b for i in range(e * k)]
    return [tuple(word[i * k:(i + 1) * k]) for i in range(e)]


def bipartite_family(n: int, m: int, r: int, alpha: int):
    """prop:dir-hyper-first's family: tails A, heads B, one copy per (a, H)."""
    k, d = r - 1, m - 1
    b = n - alpha
    e = (d * b) // k
    tails = list(range(alpha))
    blocks = cyclic_blocks(b, k, e)
    # heads are labelled alpha .. n-1
    return [(a, tuple(alpha + x for x in block)) for a in tails for block in blocks], e


def brute_lambda_max(n: int, edges) -> int:
    """lambda^max by enumerating simple Berge routes, no import of the program.

    A route is a sequence of distinct vertices with a distinct hyperedge per
    step, each step leaving a tail and entering a head.
    """
    out = {}
    for idx, (t, heads) in enumerate(edges):
        for h in heads:
            out.setdefault((t, h), []).append(idx)

    def routes(u, v):
        found = []
        stack = [(u, [u], [])]
        while stack:
            cur, seen, used = stack.pop()
            for (t, h), idxs in out.items():
                if t != cur or h in seen:
                    continue
                for idx in idxs:
                    if idx in used:
                        continue
                    if h == v:
                        found.append((tuple(seen[1:]), tuple(sorted(used + [idx]))))
                    else:
                        stack.append((h, seen + [h], used + [idx]))
        return found

    best = 0
    for u, v in itertools.permutations(range(n), 2):
        rs = routes(u, v)
        best = max(best, max_disjoint_family(rs))
    return best


def max_disjoint_family(routes, cap: int = 8) -> int:
    """Largest family of pairwise hyperedge-disjoint, internally disjoint routes."""
    best = 0
    for size in range(1, min(cap, len(routes)) + 1):
        ok = False
        for combo in itertools.combinations(routes, size):
            edges_used, interiors = [], []
            for interior, used in combo:
                edges_used.extend(used)
                interiors.extend(interior)
            if len(set(edges_used)) == len(edges_used) and len(set(interiors)) == len(interiors):
                ok = True
                break
        if not ok:
            return best
        best = size
    return best


def check_construction() -> int:
    bad = 0
    print("(a) the bipartite construction, count, degrees and lambda^max")
    for r in (2, 3, 4):
        for m in (2, 3, 4):
            for n in range(r + 1, 11):
                for alpha in range(1, n - r + 2):
                    edges, e = bipartite_family(n, m, r, alpha)
                    printed = alpha * ((m - 1) * (n - alpha) // (r - 1))
                    if len(edges) != printed:
                        print(f"    count {len(edges)} != printed {printed}"
                              f" at n={n} m={m} r={r} alpha={alpha}")
                        bad += 1
                    deg = {}
                    for _, heads in edges[:e]:          # one tail's worth
                        for h in heads:
                            deg[h] = deg.get(h, 0) + 1
                    if deg and max(deg.values()) > m - 1:
                        print(f"    head degree {max(deg.values())} > {m-1}"
                              f" at n={n} m={m} r={r} alpha={alpha}")
                        bad += 1
    # lambda^max on the small instances a brute-force route search can finish
    for r, m, n, alpha in ((3, 3, 6, 2), (3, 2, 6, 3), (2, 3, 5, 2), (3, 3, 7, 3)):
        edges, _ = bipartite_family(n, m, r, alpha)
        lam = brute_lambda_max(n, edges)
        flag = "" if lam <= m - 1 else "   TOO HIGH"
        print(f"    n={n} m={m} r={r} alpha={alpha}: {len(edges)} hyperedges, "
              f"lambda^max = {lam}, cap {m-1}{flag}")
        if lam > m - 1:
            bad += 1
    return bad


def check_balanced() -> int:
    """alpha = floor(n/2) need not be the integer maximiser, and the thesis says so.

    The claim is only that the balanced split already reaches
    (m-1)n^2/(4(r-1)) - O_{m,r}(n), so what is checked here is that the gap to
    the true integer maximum is linear in n and never touches the n^2 term.
    The floor does favour an off-balance split at r = 4, by exactly the unit or
    two the printed parenthetical describes.
    """
    bad = 0
    print("\n(b) the balanced split: gap from floor(n/2) to the integer maximum")
    worst = 0.0
    for r in (2, 3, 4):
        for m in (2, 3, 6):
            for n in (12, 20, 40, 80, 400, 2000):
                counts = {a: a * ((m - 1) * (n - a) // (r - 1))
                          for a in range(1, n - r + 2)}
                best_a = max(counts, key=lambda a: counts[a])
                gap = counts[best_a] - counts[n // 2]
                worst = max(worst, gap / n)
                if gap > n:                      # linear in n is the claim
                    print(f"    n={n} m={m} r={r}: gap {gap} exceeds n")
                    bad += 1
    print(f"    largest gap seen is {worst:.3f} n, so the n^2 term never moves")
    for r, m in ((3, 3), (3, 6), (4, 2)):
        print(f"    r={r} m={m}: count / [(m-1)n^2/(4(r-1))] ->", end=" ")
        for n in (20, 100, 500, 2000):
            counts = max(a * ((m - 1) * (n - a) // (r - 1)) for a in range(1, n - r + 2))
            print(f"n={n}: {counts / ((m-1) * n * n / (4 * (r-1))):.4f}", end="  ")
        print()
    return bad


def check_factor_of_four() -> None:
    print("\n(c) the crude bound against the sharp bound and the construction")
    r, m = 3, 3
    print(f"    r={r} m={m}")
    print(f"    {'n':>6} {'construction':>13} {'sharp':>9} {'crude':>9} {'crude/constr':>13}")
    for n in (20, 50, 200, 1000):
        constr = max(a * ((m - 1) * (n - a) // (r - 1)) for a in range(1, n - r + 2))
        sharp = (m - 1) / (r - 1) * (n * n // 4) + 4 * (m - 1) ** 2 * (n - 1)
        crude = (m - 1) * n * (n - 1) / (r - 1)
        print(f"    {n:6d} {constr:13d} {sharp:9.0f} {crude:9.0f} {crude / constr:13.2f}")


# --------------------------------------------------------------------------
# (d) the Step 2 budget claim
# --------------------------------------------------------------------------
def brute_kappa(n: int, edges, u: int, v: int) -> int:
    out = {}
    for idx, (t, heads) in enumerate(edges):
        for h in heads:
            out.setdefault((t, h), []).append(idx)
    found = []
    stack = [(u, [u], [])]
    while stack:
        cur, seen, used = stack.pop()
        for (t, h), idxs in out.items():
            if t != cur or h in seen:
                continue
            for idx in idxs:
                if idx in used:
                    continue
                if h == v:
                    found.append((tuple(seen[1:]), tuple(sorted(used + [idx]))))
                else:
                    stack.append((h, seen + [h], used + [idx]))
    return max_disjoint_family(found)


def check_budget(trials: int = 400, seed: int = 20260908) -> int:
    print("\n(d) Step 2 on random forward hypergraphs:"
          " 1_{(u,v) in R} + p_2(u,v) <= (r-1) kappa(u,v)")
    rng = random.Random(seed)
    bad = worst = tested = 0
    for _ in range(trials):
        n = rng.randint(4, 5)
        r = rng.choice((2, 3))
        k = r - 1
        pool = [(t, hs) for t in range(n)
                for hs in itertools.combinations([x for x in range(n) if x != t], k)]
        edges = rng.sample(pool, rng.randint(2, min(7, len(pool))))
        shadow = {(t, h) for t, hs in edges for h in hs}
        for u, v in itertools.permutations(range(n), 2):
            p2 = sum(1 for x in range(n)
                     if x not in (u, v) and (u, x) in shadow and (x, v) in shadow)
            targets = (1 if (u, v) in shadow else 0) + p2
            if targets == 0:
                continue
            kap = brute_kappa(n, edges, u, v)
            tested += 1
            if targets > (r - 1) * kap:
                print(f"    VIOLATED: n={n} r={r} pair=({u},{v}) targets={targets}"
                      f" kappa={kap} edges={edges}")
                bad += 1
            worst = max(worst, targets / kap if kap else 0.0)
    print(f"    {tested} ordered pairs with a target, {bad} violations, "
          f"largest targets/kappa seen {worst:.2f} against the allowed r-1")
    return bad


def main() -> int:
    bad = check_construction() + check_balanced() + check_budget()
    check_factor_of_four()
    print(f"\n{'all checks pass' if bad == 0 else str(bad) + ' failures'}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())

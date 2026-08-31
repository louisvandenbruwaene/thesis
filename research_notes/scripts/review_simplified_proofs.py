"""Numerical checks behind SIMPLIFIED_AI_PROOFS_REVIEW.md.

Three independent checks, each against the thesis program's own checker where a
connectivity value is needed:

1. the cut induction of the review's Lemma 18, on random NON-UNIFORM
   multihypergraphs, which is the generality its induction actually runs in;
2. the degree-smoothing lemma, by running its own exchange step to a fixed
   point from random starts and confirming the fixed point is balanced and has
   maximum degree exactly ceil(re/n);
3. the cyclic-word construction, by direct enumeration.

Run with the repo virtualenv:  .venv/bin/python3 research_notes/scripts/review_simplified_proofs.py
"""

import itertools
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "program"))

from erdos915_unified import Hypergraph, max_hyperedge_connectivity  # noqa: E402


def check_cut_induction(trials: int = 4000, seed: int = 20260831) -> None:
    """sum_e (|e| - 1) <= k (n - 1) for every multihypergraph with lambda^max <= k."""
    rng = random.Random(seed)
    violations = 0
    tight = 0
    for _ in range(trials):
        n = rng.randint(2, 7)
        edges = [frozenset(rng.sample(range(n), rng.randint(2, n)))
                 for _ in range(rng.randint(1, 7))]
        k = max_hyperedge_connectivity(Hypergraph(n, edges))
        lhs = sum(len(e) - 1 for e in edges)
        rhs = k * (n - 1)
        violations += lhs > rhs
        tight += lhs == rhs
    print(f"cut induction: {violations} violations in {trials} trials, "
          f"{tight} attained with equality")
    assert violations == 0


def check_degree_smoothing(max_n: int = 8, seed: int = 7) -> None:
    """The minimiser of sum deg^2 is balanced, with max degree exactly ceil(re/n)."""
    rng = random.Random(seed)
    failures = 0
    for n in range(2, max_n + 1):
        for r in range(1, n + 1):
            sets = [frozenset(s) for s in itertools.combinations(range(n), r)]
            for e in range(len(sets) + 1):
                family = set(rng.sample(sets, e))
                for _ in range(4000):
                    deg = Counter()
                    for s in family:
                        deg.update(s)
                    hi = max(range(n), key=lambda v: deg[v])
                    lo = min(range(n), key=lambda v: deg[v])
                    if deg[hi] - deg[lo] < 2:
                        break
                    # The lemma's claim: such an exchange always exists.
                    for a in list(family):
                        if hi in a and lo not in a and (a - {hi}) | {lo} not in family:
                            family.discard(a)
                            family.add((a - {hi}) | {lo})
                            break
                    else:
                        print(f"  stuck at n={n} r={r} e={e}")
                        failures += 1
                        break
                deg = Counter()
                for s in family:
                    deg.update(s)
                spread = max(deg[v] for v in range(n)) - min(deg[v] for v in range(n))
                if spread > 1:
                    print(f"  unbalanced at n={n} r={r} e={e}")
                    failures += 1
                if e and max(deg[v] for v in range(n)) != -(-r * e // n):
                    print(f"  wrong max degree at n={n} r={r} e={e}")
                    failures += 1
    print(f"degree smoothing: {failures} failures up to n={max_n}")
    assert failures == 0


def check_cyclic_word(max_b: int = 11, max_d: int = 11) -> None:
    """Blocks of k consecutive letters of the round-robin word have degree <= d."""
    failures = 0
    for b in range(2, max_b + 1):
        for k in range(1, b + 1):
            for d in range(max_d + 1):
                e = (d * b) // k
                word = [i % b for i in range(e * k)]
                blocks = [word[i * k:(i + 1) * k] for i in range(e)]
                if any(len(set(block)) != k for block in blocks):
                    print(f"  repeated vertex at b={b} k={k} d={d}")
                    failures += 1
                deg = Counter(v for block in blocks for v in block)
                if blocks and max(deg.values()) > d:
                    print(f"  degree {max(deg.values())} > {d} at b={b} k={k}")
                    failures += 1
    print(f"cyclic word: {failures} failures up to b={max_b}")
    assert failures == 0


if __name__ == "__main__":
    check_cut_induction()
    check_degree_smoothing()
    check_cyclic_word()
    print("ALL CHECKS PASSED")

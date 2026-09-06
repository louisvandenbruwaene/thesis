#!/usr/bin/env python3
"""Verify Cambie's clique-core counterexample with independent cut enumeration.

Run from program/: ../.venv/bin/python3 scripts/clique_core_check.py
The twelve-vertex check enumerates every directed cut, without a flow library.
The parameter sweep checks the displayed cut certificates and count identities.
"""

from itertools import product


def construction(n, m):
    assert n >= m >= 2
    a = (n - m + 1) // 2
    sources = set(range(a))
    core = set(range(a, a + m))
    sinks = set(range(a + m, n))
    ordered_core = sorted(core)
    arcs = {(u, v) for u, v in product(core, repeat=2) if u != v}
    arcs.update(product(sources, ordered_core[:m - 1]))
    arcs.update(product(ordered_core[:m - 2], sinks))
    arcs.update(product(sources, sinks))
    return sources, core, sinks, arcs


def verify_certificates(n, m):
    sources, core, sinks, arcs = construction(n, m)
    for s, t in product(range(n), repeat=2):
        if s == t:
            continue
        if s in core and t in core:
            side, capacity = {s} | sinks, m - 1
        elif s in sources and t in core:
            side, capacity = {s} | sinks, m - 1
        elif s in core and t in sinks:
            side, capacity = core | (sinks - {t}), m - 2
        elif s in sources and t in sinks:
            side, capacity = {s} | core | (sinks - {t}), m - 1
        else:
            # Sinks have no outgoing arcs, and sources have no incoming arcs.
            side = {s} if s in sinks else set(range(n)) - {t}
            capacity = 0
        assert s in side and t not in side
        assert sum(u in side and v not in side for u, v in arcs) == capacity
    bound = (n + m - 3) ** 2 // 4 + 2 * (m - 1)
    r = n - m
    assert len(arcs) == bound
    assert bound - m * (n - 1) == (r + 1) ** 2 // 4 - 2 * r
    assert bound - (n + m - 2) ** 2 // 4 == m - 1 - r // 2
    if m >= 5 and m + 7 <= n <= 3 * m - 3:
        assert bound > max(m * (n - 1), (n + m - 2) ** 2 // 4)


def main():
    cases = 0
    for m in range(2, 11):
        for n in range(m, 3 * m + 3):
            verify_certificates(n, m)
            cases += 1

    n, m = 12, 5
    *_, arcs = construction(n, m)
    minima = [[len(arcs)] * n for _ in range(n)]
    for mask in range(1, (1 << n) - 1):
        inside = [u for u in range(n) if mask & (1 << u)]
        outside = [u for u in range(n) if not mask & (1 << u)]
        capacity = sum(bool(mask & (1 << u)) and not mask & (1 << v)
                       for u, v in arcs)
        for s, t in product(inside, outside):
            minima[s][t] = min(minima[s][t], capacity)
    maximum = max(minima[s][t] for s, t in product(range(n), repeat=2) if s != t)
    assert len(arcs) == 57 and maximum == 4
    print(f"Verified {cases} parameter cases by explicit cuts and count identities.")
    print("n=12, m=5: 57 arcs, maximum local arc-connectivity 4 (all 4094 cuts).")


if __name__ == "__main__":
    main()

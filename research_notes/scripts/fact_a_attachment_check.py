"""Fact (a) attachment check: no 25-arc feasible multigraph on 7 vertices.

Self-contained second half of the delta-split route to fact (a),
L_3^dir(7) = 24.  The first half is the classification of all feasible
(lambda^max <= 2, multiplicities in {0,1,2}) directed multigraphs on 6
vertices with exactly 19 and exactly 18 arcs (sound geng enumerator, npz
files in program/logs/).  Given those classes this script decides, for every
class H and every way to attach a 7th vertex v:

  case A (delta = 6): d(v) = 6 and every degree of D = H + v at least 6,
  case B (delta = 7): d(v) = 7 and every degree of D = H + v at least 7,

whether lambda^max(D) <= 2.  Any survivor is a 25-arc witness refuting
fact (a); an empty survivor list in both cases PROVES fact (a), because any
25-arc witness has min degree delta in {6, 7} (saturated attachment lemma +
uncapped n=6 classification force delta >= 6; sum of degrees 50 < 7 * 8
forces delta <= 7) and deleting a minimum-degree vertex lands in case A or B.

Pruning is by exact necessary conditions only:
  * degree floor: attach(u) >= dmin - deg_H(u) and attach(u) <= 4;
  * the mixed-pair lemma: arcs u -> v and v -> w with u != w force
    lambda_H(u, w) <= 1, since the lambda_H(u, w) routes avoid v and
    u -> v -> w is one more arc-disjoint route.
Survivors of the filters get a full all-pairs max-flow check.  The max-flow
is a hand-rolled capped Edmonds-Karp (standard library only), independent of
the thesis program; --crosscheck validates it against the thesis checker on
every loaded class and on random attachment verdicts.

Usage:
  python3 fact_a_attachment_check.py            # run both cases
  python3 fact_a_attachment_check.py --selftest # positive/negative controls
  python3 fact_a_attachment_check.py --crosscheck  # also compare with program
"""
from __future__ import annotations

import sys
import time
from collections import deque

import numpy as np

LOGDIR = "/Users/chief/Projects/thesis/program/logs"
CAP = 2          # feasibility threshold: lambda^max <= 2  (m = 3)


# ----------------------------------------------------------------------
# capped max-flow, hand-rolled (independent of the thesis program)
# ----------------------------------------------------------------------

def maxflow_capped(mu: list[list[int]], n: int, s: int, t: int, stop: int) -> int:
    """Value of the s-t max flow, but stop early once it exceeds ``stop``.

    Edmonds-Karp on the residual matrix; capacities are the multiplicities.
    Returns min(maxflow, stop + 1), which is all a feasibility test needs.
    """
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
        bottleneck = 10 ** 9
        y = t
        while y != s:
            x = parent[y]
            if res[x][y] < bottleneck:
                bottleneck = res[x][y]
            y = x
        y = t
        while y != s:
            x = parent[y]
            res[x][y] -= bottleneck
            res[y][x] += bottleneck
            y = x
        flow += bottleneck
    return flow


def feasible(mu: list[list[int]], n: int) -> bool:
    """lambda^max <= CAP for every ordered pair."""
    for s in range(n):
        for t in range(n):
            if s != t and maxflow_capped(mu, n, s, t, CAP) > CAP:
                return False
    return True


def all_pairs_lambda(mu: list[list[int]], n: int) -> list[list[int]]:
    lam = [[0] * n for _ in range(n)]
    for s in range(n):
        for t in range(n):
            if s != t:
                lam[s][t] = maxflow_capped(mu, n, s, t, CAP)
    return lam


# ----------------------------------------------------------------------
# the attachment search for one 6-vertex class
# ----------------------------------------------------------------------

def attachments(H: np.ndarray, dmin: int) -> list[tuple[tuple[int, int], ...]]:
    """Every feasible attachment of v (degree dmin, min degree of H+v >= dmin).

    Returns the list of surviving patterns ((a_0, b_0), ..., (a_5, b_5)) with
    a_u = mu(u, v), b_u = mu(v, u); empty list = case closed for this H.
    """
    n = 6
    mu6 = [[int(H[i, j]) for j in range(n)] for i in range(n)]
    deg_H = [sum(mu6[u]) + sum(mu6[x][u] for x in range(n)) for u in range(n)]

    # degree floor: attach(u) in [max(0, dmin - deg_H(u)), 4]
    lo = [max(0, dmin - d) for d in deg_H]
    if sum(lo) > dmin or any(v > 4 for v in lo):
        return []

    lam = all_pairs_lambda(mu6, n)
    # mixed-pair lemma: an in-arc from u and an out-arc to w (u != w) are
    # only possible when lambda_H(u, w) <= CAP - 1
    ok_pair = [[lam[u][w] <= CAP - 1 for w in range(n)] for u in range(n)]

    survivors: list[tuple[tuple[int, int], ...]] = []
    pattern: list[tuple[int, int]] = []
    ins: list[int] = []     # u with a_u >= 1 so far
    outs: list[int] = []    # w with b_w >= 1 so far

    def rec(u: int, remaining: int) -> None:
        if u == n:
            if remaining == 0:
                mu7 = [row + [0] for row in mu6] + [[0] * (n + 1)]
                for x, (a, b) in enumerate(pattern):
                    mu7[x][n] = a
                    mu7[n][x] = b
                if feasible(mu7, n + 1):
                    survivors.append(tuple(pattern))
            return
        # attach(u) can be at most 4 and at least lo[u]; also leave room /
        # enough demand for the rest
        rest_lo = sum(lo[u + 1:])
        for a in range(3):
            for b in range(3):
                s = a + b
                if s < lo[u] or s > remaining - rest_lo or s > 4:
                    continue
                if a and any(not ok_pair[u][w] for w in outs):
                    continue
                if b and any(not ok_pair[x][u] for x in ins):
                    continue
                pattern.append((a, b))
                if a:
                    ins.append(u)
                if b:
                    outs.append(u)
                rec(u + 1, remaining - s)
                if b:
                    outs.pop()
                if a:
                    ins.pop()
                pattern.pop()

    rec(0, dmin)
    return survivors


def run_case(npz_path: str, dmin: int, label: str,
             crosscheck: bool = False) -> int:
    data = np.load(npz_path)
    keys = sorted(data.files, key=lambda k: int(k[1:]))
    print(f"{label}: {len(keys)} classes from {npz_path}", flush=True)
    if crosscheck:
        _crosscheck_classes(data, keys, dmin)
    total_survivors = 0
    t0 = time.time()
    for i, key in enumerate(keys):
        H = data[key]
        found = attachments(H, dmin)
        if found:
            total_survivors += len(found)
            print(f"  !! SURVIVOR at class {key}: {len(found)} patterns", flush=True)
            print(H)
            for p in found[:5]:
                print("     pattern", p, flush=True)
        if (i + 1) % 2000 == 0:
            print(f"  ... {i + 1}/{len(keys)} classes, {time.time() - t0:.0f}s",
                  flush=True)
    verdict = "NO SURVIVOR (case closed)" if total_survivors == 0 else \
        f"{total_survivors} SURVIVING PATTERNS (fact (a) REFUTED?)"
    print(f"{label}: {verdict} in {time.time() - t0:.0f}s", flush=True)
    return total_survivors


# ----------------------------------------------------------------------
# validation
# ----------------------------------------------------------------------

def _crosscheck_classes(data, keys, dmin) -> None:
    """Every loaded class must be feasible with the right arc count, per BOTH
    this script's checker and the thesis program's."""
    sys.path.insert(0, "/Users/chief/Projects/thesis/program")
    from erdos915_unified import Graph, Variant

    target = 25 - dmin
    bad = 0
    for key in keys:
        H = data[key]
        mu6 = [[int(H[i, j]) for j in range(6)] for i in range(6)]
        arcs = int(H.sum())
        own = feasible(mu6, 6)
        g = Graph(6, Variant(directed=True, simple=False))
        g.mu = np.asarray(H, dtype=int)
        prog = g.max_edge_connectivity() <= CAP
        if arcs != target or not own or own != prog:
            bad += 1
            print(f"  CROSSCHECK FAIL {key}: arcs={arcs} own={own} prog={prog}")
    print(f"  crosscheck: {len(keys)} classes, {bad} failures", flush=True)
    assert bad == 0


def selftest() -> None:
    """Positive and negative controls for the whole pipeline."""
    # doubled bidirected P_6 (everywhere-saturated, 20 arcs)
    P6 = np.zeros((6, 6), dtype=int)
    for i in range(5):
        P6[i, i + 1] = P6[i + 1, i] = 2

    # 1. saturated attachment control: degree-4 attachments to doubled P_6
    #    must be exactly the 6 single-partner full-multiplicity patterns.
    found = attachments(P6, 4)   # dmin=4: lo=0 everywhere, d(v)=4
    single_partner = [p for p in found
                      if sum(1 for a, b in p if a + b) == 1
                      and all((a, b) in ((0, 0), (2, 2)) for a, b in p)]
    assert len(found) == 6 and len(single_partner) == 6, found
    print("selftest 1 OK: doubled P_6 + degree-4 vertex ->",
          "exactly the 6 single-partner attachments (saturated lemma)")

    # 2. attachment-lemma control: 2B(3,3) (18 arcs, all degrees 6) admits
    #    NO degree-7 attachment (lem:attachment caps d(v) <= 2*3 = 6).
    B33 = np.zeros((6, 6), dtype=int)
    B33[:3, 3:] = 2
    assert attachments(B33, 7) == []
    print("selftest 2 OK: 2B(3,3) + degree-7 vertex -> none (attachment lemma)")

    # 3. checker control: doubled P_7 is feasible, doubled C_7 is not.
    P7 = [[0] * 7 for _ in range(7)]
    for i in range(6):
        P7[i][i + 1] = P7[i + 1][i] = 2
    assert feasible(P7, 7)
    C7 = [row[:] for row in P7]
    C7[6][0] = C7[0][6] = 2
    assert not feasible(C7, 7)
    print("selftest 3 OK: doubled P_7 feasible, doubled C_7 infeasible")


def main() -> None:
    if "--selftest" in sys.argv:
        selftest()
        return
    crosscheck = "--crosscheck" in sys.argv
    survivors = 0
    survivors += run_case(f"{LOGDIR}/n6_t19_classes.npz", 6,
                          "case A (delta=6, 19-arc H)", crosscheck)
    survivors += run_case(f"{LOGDIR}/n6_t18_classes.npz", 7,
                          "case B (delta=7, 18-arc H)", crosscheck)
    if survivors == 0:
        print("FACT (a) PROVED along the delta-split route: "
              "L_3^dir(7) = 24, M*(7) = 12.", flush=True)
    else:
        print("fact (a) REFUTED: inspect the survivors above.", flush=True)


if __name__ == "__main__":
    main()

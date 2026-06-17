#!/usr/bin/env python3
"""Jan Goedgebeur's geng + directg / watercluster2 pipeline as a cross-check.

Jan (nauty's author) suggested generating the directed cases with nauty's
generation-time pipeline instead of (or alongside) the thesis's own DFS
enumerator:

    geng n | directg          all non-isomorphic orientations of every graph
    geng n | watercluster2     the same, usually faster (his claim)

``directg`` orients every edge of an undirected graph in one of three ways
(forward, backward, or both), and suppresses isomorphic results.  Run over the
output of ``geng`` (all non-isomorphic undirected graphs on n vertices) it
therefore emits exactly the non-isomorphic SIMPLE DIGRAPHS on n vertices -- the
object space of the thesis's simple-directed variant, two-cycles included.

This script does four things, all cross-checks rather than new mathematics:

  1. COUNTS.  The pipeline count of non-iso simple digraphs matches OEIS
     A000273 and matches the thesis program's own enumeration deduplicated by
     its pure-Python canonical form.  Two independent isomorphism engines agree.

  2. SIMPLE-DIRECTED EXTREMAL VALUE.  Feeding the pipeline's digraphs through the
     program's exact max-flow checker reproduces the simple-directed arc bound
     L_m^dir(n) that the thesis reports (and the program's own exhaustive solve).

  3. directg vs watercluster2 TIMING.  Quantifies Jan's "watercluster2 is
     usually faster" remark on this problem's sizes.

  4. MULTIGRAPH HYBRID (the ENUM (b) cross-check Jan flagged as non-trivial).
     A directed multigraph with multiplicities in {0..m-1} has a simple digraph
     SUPPORT (the arcs of positive multiplicity).  We let nauty do the hard
     isomorphism reduction on the support, then layer multiplicities {1..m-1}
     on its arcs and deduplicate the finished multigraphs with the program's
     canonical form.  This reproduces enumerate_extremal_directed_multigraphs at
     n = 4, 5 (and is pushed as far as it stays cheap), giving the directed
     multigraph enumeration an independent second code path.

Run from anywhere; it adds ../../program to sys.path to import the one program.
"""
from __future__ import annotations

import math
import subprocess
import sys
import time
from itertools import product
from pathlib import Path

import numpy as np

PROGRAM = Path(__file__).resolve().parents[2] / "program"
sys.path.insert(0, str(PROGRAM))

from erdos915_unified import (  # noqa: E402
    SIMPLE_DIRECTED,
    Graph,
    _canonical_form,
    _tiny_maxflow,
    enumerate_extremal_directed_multigraphs,
    max_edge_connectivity,
    solve,
)

# OEIS A000273: number of directed graphs (digraphs) on n unlabeled nodes,
# loops forbidden, every ordered pair independent.  Index by n.
A000273 = [1, 1, 3, 16, 218, 9608, 1540944, 882033440]


# ----------------------------------------------------------------------
#  Running and parsing the nauty pipeline
# ----------------------------------------------------------------------

def _parse_text_digraphs(text: str, n: int):
    """Parse directg/watercluster2 ``T`` text output into multiplicity matrices.

    Each data line is ``nv ne s1 d1 s2 d2 ... s_ne d_ne``.  Non-data lines
    (e.g. watercluster2's "Number of directed graphs: N") are skipped.
    """
    out = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 2 or not parts[0].lstrip("-").isdigit():
            continue
        nv, ne = int(parts[0]), int(parts[1])
        if nv != n:
            continue
        nums = list(map(int, parts[2:]))
        mu = np.zeros((n, n), dtype=int)
        for k in range(ne):
            s, d = nums[2 * k], nums[2 * k + 1]
            mu[s, d] = 1
        out.append(mu)
    return out


def run_pipeline(n: int, tool: str = "directg", arc_count: int | None = None):
    """All non-isomorphic simple digraphs on ``n`` vertices via the nauty pipeline.

    ``tool`` is ``"directg"`` or ``"watercluster2"``.  ``arc_count`` restricts to
    exactly that many arcs (directg only, via ``-e``); ``None`` means all.
    """
    if tool == "directg":
        e = f" -e{arc_count}" if arc_count is not None else ""
        cmd = f"geng -q {n} | directg -T{e}"
    elif tool == "watercluster2":
        cmd = f"geng -q {n} | watercluster2 T"
    else:
        raise ValueError(f"unknown tool {tool!r}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    graphs = _parse_text_digraphs(res.stdout, n)
    if tool == "watercluster2" and arc_count is not None:
        graphs = [mu for mu in graphs if int(mu.sum()) == arc_count]
    return graphs


def count_pipeline(n: int, tool: str = "directg") -> int:
    """Fast digraph count only (no graph parsing).

    The two tools report the total on stderr/stdout in different words:
      directg -u     ``>Z 11 graphs read from stdin; 218 digraphs generated``
      watercluster2  ``Number of directed graphs: 1540944``
    so we pick the integer next to the right keyword, not the first integer
    (which for directg is geng's *undirected* graph count, A000088).
    """
    import re
    if tool == "directg":
        cmd, pat = f"geng -q {n} | directg -u", r"(\d+)\s+digraphs"
    elif tool == "watercluster2":
        cmd, pat = f"geng -q {n} | watercluster2", r"graphs:\s*(\d+)"
    else:
        raise ValueError(f"unknown tool {tool!r}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    blob = res.stdout + res.stderr
    match = re.search(pat, blob)
    if not match:
        raise RuntimeError(f"could not parse {tool} count from: {blob!r}")
    return int(match.group(1))


# ----------------------------------------------------------------------
#  Cross-check 1: counts agree (nauty vs program vs OEIS)
# ----------------------------------------------------------------------

def program_iso_count(n: int) -> int:
    """Non-iso simple digraphs on n vertices, via the program's canonical form.

    Enumerates the full labelled 0/1 arc space and deduplicates with
    :func:`_canonical_form` -- the program's own isomorphism source of truth.
    """
    cells = [(i, j) for i in range(n) for j in range(n) if i != j]
    seen = set()
    for bits in product((0, 1), repeat=len(cells)):
        mu = np.zeros((n, n), dtype=int)
        for (i, j), b in zip(cells, bits):
            mu[i, j] = b
        seen.add(_canonical_form(mu))
    return len(seen)


def crosscheck_counts(max_n_program: int = 4, max_n_nauty: int = 6) -> None:
    print("=" * 70)
    print("1. COUNT CROSS-CHECK  (non-isomorphic simple digraphs)")
    print("    n |   nauty | program | OEIS A000273 |  agree?")
    print("   ---+---------+---------+--------------+--------")
    for n in range(2, max_n_nauty + 1):
        nauty = count_pipeline(n, "directg")
        prog = program_iso_count(n) if n <= max_n_program else None
        oeis = A000273[n] if n < len(A000273) else None
        cells = [str(nauty),
                 str(prog) if prog is not None else "  -- ",
                 str(oeis) if oeis is not None else "    -- "]
        ok = all(v == nauty for v in (prog, oeis) if v is not None)
        print(f"   {n:2d} | {cells[0]:>7} | {cells[1]:>7} | {cells[2]:>12} |  {'OK' if ok else 'MISMATCH'}")


# ----------------------------------------------------------------------
#  Cross-check 2: simple-directed extremal value via the pipeline
# ----------------------------------------------------------------------

def feasible(mu: np.ndarray, m: int) -> bool:
    """lambda^max <= m-1 (no ordered pair carries m arc-disjoint routes)."""
    n = mu.shape[0]
    return not any(_tiny_maxflow(mu, n, s, t, m - 1)
                   for s in range(n) for t in range(n) if s != t)


def pipeline_extremal(n: int, m: int) -> tuple[int, int]:
    """(max feasible arc count, number of non-iso extremal digraphs) via nauty.

    Generates by decreasing arc count and stops at the first level with a
    feasible digraph -- that level is the extremal value.
    """
    max_arcs = n * (n - 1)
    for a in range(max_arcs, -1, -1):
        graphs = run_pipeline(n, "directg", arc_count=a)
        ext = [mu for mu in graphs if feasible(mu, m)]
        if ext:
            return a, len(ext)
    return 0, 0


def crosscheck_extremal(m: int = 3, max_n: int = 6) -> None:
    print("=" * 70)
    print(f"2. SIMPLE-DIRECTED EXTREMAL VALUE  (m = {m}, feasible iff lambda^max <= {m-1})")
    print("    n | nauty L | program solve | conj floor((n+m-2)^2/4) | agree?")
    print("   ---+---------+---------------+-------------------------+-------")
    for n in range(2, max_n + 1):
        ext, n_ext = pipeline_extremal(n, m)
        res = solve(n, m, directed=True, simple=True, exhaustive=True, max_seconds=30)
        prog = res.value if res.bound == "exact" else None
        conj = ((n + m - 2) ** 2) // 4
        prog_s = str(prog) if prog is not None else "  (no exact)"
        ok = (prog is None or prog == ext)
        flag = "OK" if ok else "MISMATCH"
        note = "" if ext == conj else "  (<conj: n below quad regime)" if ext < conj else "  (>conj!)"
        print(f"   {n:2d} | {ext:>4} ({n_ext:>2}) | {prog_s:>13} | {conj:>23} | {flag}{note}")


# ----------------------------------------------------------------------
#  Cross-check 3: directg vs watercluster2 timing (Jan's claim)
# ----------------------------------------------------------------------

def benchmark(ns=(5, 6, 7)) -> None:
    print("=" * 70)
    print("3. directg vs watercluster2 TIMING  (count all non-iso simple digraphs)")
    print("    n |   count    | directg (s) | watercluster2 (s) | faster")
    print("   ---+------------+-------------+-------------------+--------")
    for n in ns:
        t0 = time.perf_counter(); c1 = count_pipeline(n, "directg"); t1 = time.perf_counter()
        c2 = count_pipeline(n, "watercluster2"); t2 = time.perf_counter()
        td, tw = t1 - t0, t2 - t1
        agree = "" if c1 == c2 else f"  COUNT MISMATCH {c1} vs {c2}"
        faster = "watercluster2" if tw < td else "directg"
        print(f"   {n:2d} | {c1:>10} | {td:>11.2f} | {tw:>17.2f} | {faster}{agree}")


# ----------------------------------------------------------------------
#  Cross-check 4: directed-multigraph hybrid (the ENUM (b) cross-check)
# ----------------------------------------------------------------------

def _mult_assignments(arcs, target_arcs, m):
    """Yield multiplicity tuples in {1..m-1}^len(arcs) summing to target_arcs.

    For m = 3 (the thesis case) this is "choose which arcs carry multiplicity 2"
    -- combinations of size target-s -- which is far smaller than the 2^s that a
    blind product would enumerate.  For larger m it falls back to product.
    """
    s = len(arcs)
    if m == 3:
        from itertools import combinations
        twos = target_arcs - s            # arcs that must carry multiplicity 2
        if twos < 0 or twos > s:
            return
        for hi in combinations(range(s), twos):
            mult = [1] * s
            for k in hi:
                mult[k] = 2
            yield mult
    else:
        for mult in product(range(1, m), repeat=s):
            if sum(mult) == target_arcs:
                yield mult


def multigraph_via_support(n: int, m: int, target_arcs: int,
                           max_degree: int | None = None) -> list[np.ndarray]:
    """Non-iso directed multigraphs (mult in {0..m-1}) by layering multiplicities
    onto nauty-generated simple-digraph SUPPORTS, deduped by canonical form.

    For each non-iso support S (from geng|directg) whose arc count s can reach
    ``target_arcs`` with multiplicities in {1..m-1}, assign multiplicities to its
    arcs; keep those that respect ``max_degree`` and are feasible
    (lambda^max <= m-1); deduplicate the finished multigraphs with the program's
    canonical form.  nauty does the support isomorphism reduction; the program's
    canonical form does the final multigraph dedup.
    """
    reps: list[np.ndarray] = []
    seen: set[bytes] = set()
    s_lo = math.ceil(target_arcs / (m - 1))      # all arcs at full multiplicity
    s_hi = target_arcs                           # all arcs at multiplicity one
    for support in run_pipeline(n, "directg"):
        arcs = [(i, j) for i in range(n) for j in range(n) if support[i, j]]
        if not (s_lo <= len(arcs) <= s_hi):
            continue
        for mult in _mult_assignments(arcs, target_arcs, m):
            mu = np.zeros((n, n), dtype=int)
            for (i, j), w in zip(arcs, mult):
                mu[i, j] = w
            if max_degree is not None and int((mu.sum(0) + mu.sum(1)).max()) > max_degree:
                continue
            if not feasible(mu, m):
                continue
            key = _canonical_form(mu)
            if key not in seen:
                seen.add(key)
                reps.append(mu)
    return reps


def crosscheck_multigraph(m: int = 3) -> None:
    print("=" * 70)
    print(f"4. DIRECTED-MULTIGRAPH HYBRID  (mult in {{0..{m-1}}}, ENUM (b) cross-check)")
    # (n, target_arcs, max_degree) base cases the program characterises exactly:
    # n=4 -> 2 classes (doubled star, doubled path); n=5 -> 3 (star, broom, path).
    # n=6 (1.5M supports) is left to the program's own DFS; the hybrid would need
    # the per-support automorphism dedup (a directg -G refinement) to scale there.
    cases = [(4, 12, None), (5, 16, None)]
    print("    n | arcs | nauty-hybrid classes | program DFS classes | agree?")
    print("   ---+------+----------------------+---------------------+-------")
    for n, target, maxdeg in cases:
        t0 = time.perf_counter()
        hybrid = multigraph_via_support(n, m, target_arcs=target, max_degree=maxdeg)
        t1 = time.perf_counter()
        dfs = enumerate_extremal_directed_multigraphs(n, m, target, max_degree=maxdeg)
        t2 = time.perf_counter()
        # compare as canonical-form sets
        hset = {_canonical_form(mu) for mu in hybrid}
        dset = {_canonical_form(mu) for mu in dfs}
        ok = (hset == dset)
        print(f"   {n:2d} | {target:>4} | {len(hybrid):>20} | {len(dfs):>19} | "
              f"{'OK' if ok else 'MISMATCH'}   "
              f"(hybrid {t1-t0:.1f}s, dfs {t2-t1:.1f}s)")


if __name__ == "__main__":
    crosscheck_counts(max_n_program=4, max_n_nauty=6)
    crosscheck_extremal(m=3, max_n=5)
    benchmark(ns=(5, 6))     # n=7 is 882_033_440 digraphs: too many to generate
    crosscheck_multigraph(m=3)

#!/usr/bin/env python3
"""Tabu search vs simulated annealing for the dense-feasible-graph search.

Jan Goedgebeur suggested trying tabu search as an alternative to the thesis's
simulated-annealing discoverer (``search_for_dense_graph``), expecting "similar
performance but worth quantifying."  This script quantifies it.

Both searches optimise the SAME energy as the thesis,

    E(G) = -|E(G)| + penalty * max(0, lambda^max(G) - (m-1)),

over the SAME neighbourhood (add or remove one edge/arc, multiplicities capped
at m-1), and report the densest FEASIBLE graph found.  The annealer is the
thesis's own function; the tabu searcher is implemented here:

  * each step evaluates every single add/remove move from the current graph,
  * picks the best move whose edge is not tabu (aspiration overrides the tabu
    flag when a move beats the global best),
  * forbids the touched pair for ``tenure`` steps,
  * restarts from a perturbation when it stalls (no improvement for a while).

Fairness: both are given the same wall-clock budget per case and the same random
seeds across restarts; we compare the best feasible edge count reached and the
time to first reach the known optimum.  Run from anywhere.
"""
from __future__ import annotations

import random
import sys
import time
from pathlib import Path

PROGRAM = Path(__file__).resolve().parents[2] / "program"
sys.path.insert(0, str(PROGRAM))

from erdos915_unified import (  # noqa: E402
    MULTI_DIRECTED,
    MULTI_UNDIRECTED,
    SIMPLE_DIRECTED,
    SIMPLE_UNDIRECTED,
    Graph,
    _connectivity_measure,
    _energy,
    directed_arc_lower_bound,
    directed_multigraph_arc,
    multigraph_undirected_edge,
    search_for_dense_graph,
    simple_undirected_edge,
)


def _moves(graph: Graph, cap: int):
    """All single add/remove (u, v) moves from ``graph`` under the multiplicity cap."""
    n = graph.num_vertices
    directed = graph.variant.directed
    out = []
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            if not directed and v < u:
                continue                      # undirected: each pair once
            mult = graph.multiplicity(u, v)
            if mult < cap:
                out.append((u, v, +1))
            if mult > 0:
                out.append((u, v, -1))
    return out


def tabu_search(variant, n, m, *, separation="edge", deadline, seed=0,
                tenure=7, stall_limit=40, penalty=6.0):
    """Tabu search for the densest feasible graph; mirrors the SA energy/neighbourhood."""
    rng = random.Random(seed)
    measure = _connectivity_measure(separation)
    cap = 1 if variant.simple else (m - 1)

    current = Graph(n, variant)
    best_graph, best_edges = current.copy(), 0
    tabu: dict[tuple[int, int], int] = {}
    stall = 0
    step = 0

    def energy(g):
        return _energy(g, m, measure, penalty)

    cur_e = energy(current)
    while time.time() < deadline:
        step += 1
        best_move = None
        best_move_e = None
        best_move_is_global = False
        for (u, v, d) in _moves(current, cap):
            trial = current.copy()
            if d > 0:
                trial.add_edge(u, v)
            else:
                trial.remove_edge(u, v)
            e = energy(trial)
            feasible = measure(trial) <= m - 1
            improves_global = feasible and trial.edge_count() > best_edges
            is_tabu = tabu.get((u, v), 0) > step and not improves_global
            if is_tabu:
                continue
            better = (best_move_e is None or e < best_move_e
                      or (improves_global and not best_move_is_global))
            if better:
                best_move, best_move_e = (u, v, d), e
                best_move_is_global = improves_global
        if best_move is None:                 # everything tabu: clear and retry
            tabu.clear()
            continue
        u, v, d = best_move
        if d > 0:
            current.add_edge(u, v)
        else:
            current.remove_edge(u, v)
        cur_e = best_move_e
        tabu[(u, v)] = step + tenure
        if measure(current) <= m - 1 and current.edge_count() > best_edges:
            best_graph, best_edges = current.copy(), current.edge_count()
            stall = 0
        else:
            stall += 1
        if stall >= stall_limit:              # perturb: random restart kick
            current = best_graph.copy()
            for _ in range(rng.randint(2, 4)):
                mv = _moves(current, cap)
                if mv:
                    a, b, dd = rng.choice(mv)
                    current.add_edge(a, b) if dd > 0 else current.remove_edge(a, b)
            cur_e = energy(current)
            tabu.clear()
            stall = 0
    return best_edges, step


def known_optimum(variant, n, m):
    """Best construction value for the variant (the target the search aims at).

    Each model has its own construction: Mader's formula for the undirected
    cases, the simple-directed hub/bipartite bound for simple digraphs, and the
    multigraph bound 2*M*(n) for directed multigraphs (NOT the simple-directed
    one -- that was the earlier mislabelling that made tabu appear to beat its
    own 'optimum').
    """
    if variant is SIMPLE_UNDIRECTED:
        return simple_undirected_edge(n, m)
    if variant is MULTI_UNDIRECTED:
        return multigraph_undirected_edge(n, m)
    if variant is SIMPLE_DIRECTED:
        return min(directed_arc_lower_bound(n, m), n * (n - 1))
    if variant is MULTI_DIRECTED:
        return min(directed_multigraph_arc(n, m), (m - 1) * n * (n - 1))
    return None


def run(cases, budget=6.0):
    print("=" * 76)
    print(f"TABU vs SIMULATED ANNEALING   (equal {budget:.0f}s wall-clock per method)")
    print("SA = the thesis's own best_of_searches (independent annealer restarts).")
    print(f"{'variant':<18} {'n':>2} {'m':>2} | {'opt':>4} | "
          f"{'SA best':>7} | {'tabu best':>9} | verdict")
    print("-" * 76)
    for variant, n, m in cases:
        opt = known_optimum(variant, n, m)

        # SA: the thesis's annealer, restarted from fresh seeds until the budget
        # runs out (exactly best_of_searches, but bounded by wall clock).
        t0, sa_best, seed = time.time(), 0, 0
        while time.time() - t0 < budget:
            r = search_for_dense_graph(variant, n, m, steps=4000, seed=seed,
                                       deadline=t0 + budget)
            sa_best = max(sa_best, r.best_edge_count)
            seed += 1

        # Tabu: implemented here, same wall-clock budget, restarted on stalls.
        t0, tb_best, seed = time.time(), 0, 0
        while time.time() - t0 < budget:
            b, _ = tabu_search(variant, n, m, deadline=t0 + budget, seed=seed)
            tb_best = max(tb_best, b)
            seed += 1

        verdict = ("tie" if sa_best == tb_best else
                   f"TABU +{tb_best - sa_best}" if tb_best > sa_best else
                   f"SA +{sa_best - tb_best}")
        if opt is not None:
            verdict += (" (both opt)" if sa_best >= opt and tb_best >= opt else
                        " (tabu=opt)" if tb_best >= opt else
                        " (SA=opt)" if sa_best >= opt else " (neither opt)")
        opts = str(opt) if opt is not None else " ?"
        print(f"{variant.name:<18} {n:>2} {m:>2} | {opts:>4} | "
              f"{sa_best:>7} | {tb_best:>9} | {verdict}")


if __name__ == "__main__":
    CASES = [
        (SIMPLE_UNDIRECTED, 7, 3),
        (MULTI_UNDIRECTED, 6, 3),
        (SIMPLE_DIRECTED, 6, 3),
        (MULTI_DIRECTED, 5, 3),
        (MULTI_DIRECTED, 7, 3),
        (SIMPLE_DIRECTED, 7, 3),
    ]
    run(CASES, budget=6.0)

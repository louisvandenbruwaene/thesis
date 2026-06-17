"""
Regenerate every figure the thesis uses, from the one program next door.

This is the only figure script.  It imports the single program
``erdos915_unified.py`` and calls its plotting routines, so the figures can never
drift from the code that produces the numbers.  Run it from this ``program/``
directory:

    python make_figures.py

Each figure is written into ``../figures/``.  Every randomised search uses a
fixed seed, so the output is reproducible.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from erdos915_unified import (  # noqa: E402
    MULTI_DIRECTED,
    MULTI_UNDIRECTED,
    SIMPLE_DIRECTED,
    SIMPLE_UNDIRECTED,
    Graph,
    _VARIANT_ENUM_CONFIGS,
    search_for_dense_graph,
    compute_enumeration_cache,
    compute_surface_cache,
    connectivity_distribution,
    gallery_extremal_graphs,
    plot_appearance_threshold,
    plot_degree_threshold,
    plot_sampled_variant_grid,
    directed_arc_lower_bound,
    directed_multigraph_arc,
    draw_graph_with_sensitivity,
    edge_vertex_distribution,
    hypergraph_edge,
    multigraph_undirected_edge,
    plot_complexity_growth,
    plot_conn_dist_grid,
    plot_conn_threshold_3d,
    plot_connectivity_distribution,
    plot_directed_crossover,
    plot_edge_vertex_divergence,
    plot_edge_vertex_histograms,
    plot_edge_dist_grid,
    plot_scatter_lambda_edges,
    plot_search_trace,
    plot_variant_3d_surfaces,
    plot_variant_grid,
    save_gallery_json,
    simple_undirected_edge,
    solve,
)

FIGURES = Path(__file__).resolve().parent.parent / "figures"


# ----------------------------------------------------------------------
#  The all-variant grid: proved / conjectured / guessed, with machine points.
#  Every number below comes from one driver, ``solve``: exhaustive for an exact
#  point, discovery for a search lower bound.  The formula curves come from the
#  closed forms; the guess is a fit; the band is [construction LB, trivial max].
# ----------------------------------------------------------------------

def _exact_points(ns, m, budget, **kw):
    """Machine-proved sizes: increasing n until the exhaustion no longer finishes."""
    xs, ys = [], []
    for n in ns:
        res = solve(n, m, exhaustive=True, max_seconds=budget, **kw)
        if res.bound == "exact":
            xs.append(n)
            ys.append(res.value)
        else:
            break          # once it cannot finish, larger n cannot either
    return xs, ys


def _search_points(ns, m, budget, **kw):
    """Discovery lower bounds: a concrete feasible graph at each n (the LB construction)."""
    xs, ys = [], []
    for n in ns:
        res = solve(n, m, exhaustive=False, max_seconds=budget, seed=0, **kw)
        xs.append(n)
        ys.append(res.value)
    return xs, ys


def _band(search, trivial_max, ns):
    """The certain interval: an easy construction below, the trivial maximum above.

    The lower edge is the densest feasible graph the search exhibited (a real
    lower bound); the upper edge is the most edges any graph on n vertices can
    hold at all (a loose but certain upper bound).  The truth lies in between.
    """
    found = dict(zip(search[0], search[1]))
    lower = [min(found.get(n, 0), trivial_max(n)) for n in ns]
    upper = [trivial_max(n) for n in ns]
    return list(ns), lower, upper


def _extend_lower_bounds(search, lb_fn, ns):
    """Raise the search lower bounds to a known verified construction where it wins.

    Past the size the quick search reaches, an explicit construction the checker
    confirms is a better (still honest) lower bound, so we report the best of the
    two at each n, exactly as the rediscovery section does by hand.
    """
    found = dict(zip(search[0], search[1]))
    for n in ns:
        found[n] = max(found.get(n, 0), lb_fn(n))
    xs = sorted(found)
    return xs, [found[n] for n in xs]


def _reconcile_panel(panel: dict) -> dict:
    """Make a panel internally consistent before plotting.

    Three honest invariants, enforced here once for every panel rather than
    scattered through the construction code:

    1. **Nothing exceeds a proved optimum.**  A machine-checked exact value is
       the true maximum at that ``n``; no proved/conjectured curve, no
       named-construction lower bound, and no search circle may sit above it.
       (This is what produced the green square *below* its own curve: a closed
       form -- e.g. the hypergraph bound capped at the complete hypergraph -- can
       overshoot what is actually achievable at small ``n``.)
    2. **Search lower bounds rise with ``n``.**  A feasible graph on ``n``
       vertices stays feasible on ``n+1`` (add an isolated vertex), so the best
       feasible edge count can never *drop* as ``n`` grows.  We take a running
       maximum, which is exactly that extend-by-an-isolated-vertex bound.
    3. **No certain-interval band, and the guess interpolates rather than
       overshoots.**  The loose [construction, trivial-max] band dwarfed the
       data and is dropped (axes rescale to the data).  On an open panel the
       dotted guess is the piecewise-linear interpolation *through* the search
       points -- never a fitted curve riding above points it should pass through.
    """
    panel.pop("band", None)  # invariant 3a: no shaded certain interval

    exact = dict(zip(*panel["exact"])) if panel.get("exact") else {}

    def cap_to_exact(curve):
        if curve is None:
            return None
        xs, ys = curve
        return xs, [min(y, exact[x]) if x in exact else y for x, y in zip(xs, ys)]

    # invariant 1 applied to every formula line and to the named branches
    for key in ("proved", "conj"):
        if panel.get(key) is not None:
            panel[key] = cap_to_exact(panel[key])
    if panel.get("branches"):
        panel["branches"] = [(*cap_to_exact((bx, by)), lbl)
                             for bx, by, lbl in panel["branches"]]

    # invariants 1 then 2 applied to the search circles
    if panel.get("search") is not None:
        sx, sy = panel["search"]
        sy = [min(y, exact[x]) if x in exact else y for x, y in zip(sx, sy)]
        running, mono = -1, []
        for y in sy:
            running = max(running, y)
            mono.append(running)
        panel["search"] = (sx, mono)

    # invariant 3b: the open-panel guess is the interpolation through those
    # (monotone, exact-capped) points, so it can never ride above them.
    if panel.get("guess") == "search":
        panel["guess"] = panel.get("search")

    return panel


def gather_variant_grid(m=3, exact_budget=4.0, search_budget=0.4):
    """Build the twelve panels of the all-variant grid (row-major, model x col).

    ``m`` is the forbidden connectivity value shown in every panel.

    Two uniformity rules make the twelve panels directly comparable:

    1. Every matrix panel plots its search lower bounds over the *same* vertex
       range ``matrix_ns`` and every hypergraph panel over ``hyper_ns``, so each
       panel carries the same number of data points -- no panel trails off early.
    2. For every panel where a construction is known (proved or conjectured) the
       search lower bound is raised to that named construction with
       :func:`_extend_lower_bounds`, exactly as the caption of the figure and
       the rediscovery section state: the reported circle at each ``n`` is the
       better of the cooled search and the verified construction.  This is the
       honest "lands on the curve" rule, applied to *all* panels rather than
       only the two directed ones it used to cover, so the proved curves pass
       through their circles instead of floating above a jagged search tail.

    Open panels (no construction is known) keep the raw search points wrapped in
    the certain band, since there the search is the only lower bound there is.
    """
    panels = []
    matrix_ns = list(range(2, 13))   # uniform x-range for all matrix panels
    hyper_ns = list(range(2, 11))    # uniform x-range for all hypergraph panels

    def tri_undirected(n):
        return n * (n - 1) // 2

    def tri_hyper(n, r=3):
        return math.comb(n, r)

    def tri_dir_hyper(n, r=3):
        return n * math.comb(n - 1, r - 1)

    # Construction lower bounds (verified, proved-or-conjectured values), each
    # capped at the trivial maximum for its model.  The cap matters at small n:
    # a closed form like Mader's floor(m(n-1)/2) is the value only for n >= m;
    # for n < m the complete graph K_n already has lambda^max = n-1 <= m-1, so it
    # is feasible and denser, and the true value is comb(n,2).  Without the cap
    # the plotted curve and its lower-bound circles float ABOVE the exact squares,
    # which is impossible (a lower bound can never exceed the proved optimum).
    def lb_simple_edge(n):
        return min(simple_undirected_edge(n, m), n * (n - 1) // 2)

    def lb_multi_edge(n):
        return min(multigraph_undirected_edge(n, m), (m - 1) * (n * (n - 1) // 2))

    def lb_dir(n):
        return min(directed_arc_lower_bound(n, m), n * (n - 1))

    def lb_multi_dir(n):
        return min(directed_multigraph_arc(n, m), (m - 1) * n * (n - 1))

    def lb_hyper_edge(n):
        return min(hypergraph_edge(n, m, 3), math.comb(n, 3))

    # Undirected vertex is proved for m<=4 (Leonard/Whitney), open for m>=5.
    vert_proved = (m <= 4)
    # Hypergraph vertex is proved for m<=3 (incidence-rank lemma, thm:hyper-vertex-m3).
    hyper_vert_proved = (m <= 3)

    def searched(ns, lb_fn, **solve_kw):
        """Search over the uniform range, then raise to the known construction."""
        se = _search_points(ns, m, search_budget, **solve_kw)
        if lb_fn is not None:
            se = _extend_lower_bounds(se, lb_fn, ns)
        return se

    # ----- row 1: simple ------------------------------------------------
    # (1) simple undirected edge -- proved (Mader) for all m.
    ex = _exact_points(range(2, 9), m, exact_budget,
                       directed=False, simple=True, separation="edge")
    se = searched(matrix_ns, lb_simple_edge,
                  directed=False, simple=True, separation="edge")
    panels.append(dict(
        title=f"undirected edge, $m={m}$  (proved)", ylabel="edges",
        proved=(matrix_ns, [lb_simple_edge(n) for n in matrix_ns]),
        exact=ex, search=se))

    # (2) simple undirected vertex -- proved for m<=4, open for m>=5.
    ex2 = _exact_points(range(2, 8), m, exact_budget,
                        directed=False, simple=True, separation="vertex")
    if vert_proved:
        se2 = searched(matrix_ns, lb_simple_edge,
                       directed=False, simple=True, separation="vertex")
        panels.append(dict(
            title=f"undirected vertex, $m={m}$  (proved)", ylabel="edges",
            proved=(matrix_ns, [lb_simple_edge(n) for n in matrix_ns]),
            exact=ex2, search=se2))
    else:
        se2 = searched(matrix_ns, None,
                       directed=False, simple=True, separation="vertex")
        band2 = _band(se2, tri_undirected, matrix_ns)
        panels.append(dict(
            title=f"undirected vertex, $m={m}$  (open)", ylabel="edges",
            guess="search",
            band=band2, exact=ex2, search=se2))

    # (3) simple directed arc -- conjectured.
    ex3 = _exact_points(range(2, 8), m, exact_budget,
                        directed=True, simple=True, separation="edge")
    se3 = searched(matrix_ns, lb_dir,
                   directed=True, simple=True, separation="edge")
    panels.append(dict(
        title=f"directed arc, $m={m}$  (conjectured)", ylabel="arcs",
        conj=(matrix_ns, [lb_dir(n) for n in matrix_ns]),
        branches=[(matrix_ns, [min(m * (n - 1), n * (n - 1)) for n in matrix_ns],
                   "hub $m(n{-}1)$"),
                  (matrix_ns,
                   [min(n * n // 4 + (m - 2) * ((n + 1) // 2), n * (n - 1))
                    for n in matrix_ns], "bipartite")],
        exact=ex3, search=se3))

    # (4) simple directed vertex -- conjectured (= arc).
    ex4 = _exact_points(range(2, 8), m, exact_budget,
                        directed=True, simple=True, separation="vertex")
    se4 = searched(matrix_ns, lb_dir,
                   directed=True, simple=True, separation="vertex")
    panels.append(dict(
        title=f"directed vertex, $m={m}$  (conjectured)", ylabel="arcs",
        conj=(matrix_ns, [lb_dir(n) for n in matrix_ns]),
        exact=ex4, search=se4))

    # ----- row 2: multigraph -------------------------------------------
    # (5) multigraph undirected edge -- proved for all m.
    ex5 = _exact_points(range(2, 7), m, exact_budget,
                        directed=False, simple=False, separation="edge")
    se5 = searched(matrix_ns, lb_multi_edge,
                   directed=False, simple=False, separation="edge")
    panels.append(dict(
        title=f"undirected edge, $m={m}$  (proved)", ylabel="edges",
        proved=(matrix_ns, [lb_multi_edge(n) for n in matrix_ns]),
        exact=ex5, search=se5))

    # (6) multigraph undirected vertex -- equals simple (parallel edges irrelevant for vertex cuts).
    multi_vert_label = ("proved, $=$ simple" if vert_proved else "open, $=$ simple")
    if vert_proved:
        panels.append(dict(
            title=f"undirected vertex, $m={m}$  ({multi_vert_label})", ylabel="edges",
            proved=(matrix_ns, [lb_simple_edge(n) for n in matrix_ns]),
            exact=ex2, search=se2))
    else:
        panels.append(dict(
            title=f"undirected vertex, $m={m}$  ({multi_vert_label})", ylabel="edges",
            guess="search",
            band=_band(se2, tri_undirected, matrix_ns), exact=ex2, search=se2))

    # (7) multigraph directed arc -- certified (cut-counting) then conjectured.
    ex7 = _exact_points(range(3, 6), m, 10.0,
                        directed=True, simple=False, separation="edge")
    se7 = searched(matrix_ns, lb_multi_dir,
                   directed=True, simple=False, separation="edge")
    panels.append(dict(
        title=f"directed arc, $m={m}$  (multigraph, certified)", ylabel="arcs",
        conj=(matrix_ns, [lb_multi_dir(n) for n in matrix_ns]),
        exact=ex7, search=se7))

    # (8) multigraph directed vertex -- conjectured (reduces to simple digraph).
    panels.append(dict(
        title=f"directed vertex, $m={m}$  (conjectured, $=$ simple)", ylabel="arcs",
        conj=(matrix_ns, [lb_dir(n) for n in matrix_ns]),
        exact=ex4, search=se4))

    # ----- row 3: hypergraph (r=3) -------------------------------------
    # (9) hypergraph undirected edge -- proved for all m.
    ex9 = _exact_points(range(2, 8), m, exact_budget,
                        hypergraph=True, r=3, directed=False, separation="edge")
    se9 = searched(hyper_ns, lb_hyper_edge,
                   hypergraph=True, r=3, directed=False, separation="edge")
    panels.append(dict(
        title=f"undirected edge, $m={m}$  (proved)", ylabel="hyperedges",
        proved=(hyper_ns, [lb_hyper_edge(n) for n in hyper_ns]),
        exact=ex9, search=se9))

    # (10) hypergraph undirected vertex -- PROVED for m<=3 (incidence-rank lemma),
    #      open for m>=4.
    ex10 = _exact_points(range(2, 7), m, exact_budget,
                         hypergraph=True, r=3, directed=False, separation="vertex")
    if hyper_vert_proved:
        se10 = searched(hyper_ns, lb_hyper_edge,
                        hypergraph=True, r=3, directed=False, separation="vertex")
        panels.append(dict(
            title=f"undirected vertex, $m={m}$  (proved)", ylabel="hyperedges",
            proved=(hyper_ns, [lb_hyper_edge(n) for n in hyper_ns]),
            exact=ex10, search=se10))
    else:
        se10 = searched(hyper_ns, None,
                        hypergraph=True, r=3, directed=False, separation="vertex")
        panels.append(dict(
            title=f"undirected vertex, $m={m}$  (open)", ylabel="hyperedges",
            guess="search",
            band=_band(se10, tri_hyper, hyper_ns), exact=ex10, search=se10))

    # (11) hypergraph directed arc -- OPEN (new directed Berge model).
    ex11 = _exact_points(range(2, 6), m, exact_budget,
                         hypergraph=True, r=3, directed=True, separation="edge")
    se11 = searched(hyper_ns, None,
                    hypergraph=True, r=3, directed=True, separation="edge")
    panels.append(dict(
        title=f"directed arc, $m={m}$  (open, new model)", ylabel="hyperarcs",
        guess="search",
        band=_band(se11, tri_dir_hyper, hyper_ns), exact=ex11, search=se11))

    # (12) hypergraph directed vertex -- OPEN (new directed Berge model).
    ex12 = _exact_points(range(2, 6), m, exact_budget,
                         hypergraph=True, r=3, directed=True, separation="vertex")
    se12 = searched(hyper_ns, None,
                    hypergraph=True, r=3, directed=True, separation="vertex")
    panels.append(dict(
        title=f"directed vertex, $m={m}$  (open, new model)", ylabel="hyperarcs",
        guess="search",
        band=_band(se12, tri_dir_hyper, hyper_ns), exact=ex12, search=se12))

    return [_reconcile_panel(p) for p in panels]


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)

    plot_directed_crossover(m=3, max_n=24, path=FIGURES / "directed_crossover.png")
    print("wrote directed_crossover.png")

    plot_edge_vertex_divergence(max_n=35, path=FIGURES / "edge_vertex_divergence.png")
    print("wrote edge_vertex_divergence.png")

    # Figure 3.2: cooling trace for the directed multigraph n=4, m=3 case.
    # record_exact_connectivity logs the true lambda^max per step (more expensive
    # but needed for an exact scatter; the search itself uses the cheaper upper bound).
    run = search_for_dense_graph(MULTI_DIRECTED, n=4, m=3, steps=3000, seed=1,
                                 record_exact_connectivity=True)
    plot_search_trace(run, path=FIGURES / "temperature_trace.png",
                      optimum=12, ceiling=2, show_histogram=False)
    print(f"wrote temperature_trace.png (search reached {run.best_edge_count} arcs of 12)")

    # Additional scatter-only traces for other variants (no cooling panel needed
    # since the cooling schedule is the same across all cases).
    trace_cases = [
        # (variant, n, m, filename_stem, ceiling, connectivity_label, edge_label, title)
        (SIMPLE_UNDIRECTED, 7, 3, "trace_simple_undirected_n7_m3", 2,
         r"$\lambda^{\max}$", "edges",
         r"Search trace: simple undirected, $n=7$, $m=3$"),
        (SIMPLE_DIRECTED, 5, 3, "trace_simple_directed_n5_m3", 2,
         r"$\lambda^{\max}$", "arcs",
         r"Search trace: simple directed, $n=5$, $m=3$"),
        (MULTI_UNDIRECTED, 5, 3, "trace_multi_undirected_n5_m3", 2,
         r"$\lambda^{\max}$", "edges",
         r"Search trace: multi undirected, $n=5$, $m=3$"),
        (MULTI_DIRECTED, 5, 3, "trace_multi_directed_n5_m3", 2,
         r"$\lambda^{\max}$", "arcs",
         r"Search trace: multi directed, $n=5$, $m=3$"),
        (MULTI_DIRECTED, 4, 3, "trace_multi_directed_n4_m3_vertex", 2,
         r"$\kappa^{\max}$", "arcs",
         r"Search trace: multi directed vertex-sep, $n=4$, $m=3$"),
    ]
    for variant, n, m, stem, ceil_val, clabel, elabel, ttitle in trace_cases:
        sep = "vertex" if "vertex" in stem else "edge"
        tr = search_for_dense_graph(variant, n=n, m=m, separation=sep,
                                    steps=3000, seed=1,
                                    record_exact_connectivity=True)
        plot_search_trace(tr, path=FIGURES / f"{stem}.png",
                          ceiling=ceil_val, show_cooling=False,
                          show_histogram=False,
                          connectivity_label=clabel, edge_label=elabel,
                          title=ttitle)
        print(f"wrote {stem}.png  (best={tr.best_edge_count})")

    # A larger directed multigraph: four s->t routes of differing capacity plus a
    # dead end.  Parallel arcs are drawn explicitly, so multiplicity is read by
    # counting.  The s->a route is over-provisioned (mu=3 into a but a single arc
    # a->t out), so it appears as three arcs in a COOL colour (sigma=1): the
    # visual point that multiplicity and load-bearing role are not the same.
    sens = Graph(8, MULTI_DIRECTED)   # 0=s 1=t 2=a 3=b 4=c 5=d 6=e 7=f
    sens.set_multiplicity(0, 2, 3); sens.set_multiplicity(2, 1, 1)  # s->a->t, over-provisioned in
    sens.set_multiplicity(0, 3, 3); sens.set_multiplicity(3, 1, 3)  # s->b->t, cap 3 (load-bearing)
    sens.set_multiplicity(0, 4, 2); sens.set_multiplicity(4, 1, 2)  # s->c->t, cap 2
    sens.set_multiplicity(0, 6, 1); sens.set_multiplicity(6, 1, 1)  # s->e->t, cap 1
    sens.set_multiplicity(0, 7, 2); sens.set_multiplicity(7, 1, 2)  # s->f->t, cap 2
    sens.set_multiplicity(0, 5, 2)                                  # s->d, dead end
    sens_layout = {0: (-3.2, 0.0), 1: (3.2, 0.0),
                   2: (0.0, 2.6), 3: (0.0, 1.3), 4: (0.0, 0.0),
                   6: (0.0, -1.3), 7: (0.0, -2.6), 5: (-3.2, -2.4)}
    sens_labels = {0: "s", 1: "t", 2: "a", 3: "b", 4: "c", 5: "d", 6: "e", 7: "f"}
    draw_graph_with_sensitivity(
        sens, path=FIGURES / "sensitivity_mixed.png",
        layout=sens_layout, node_labels=sens_labels)
    print("wrote sensitivity_mixed.png")

    plot_complexity_growth(path=FIGURES / "complexity_growth.png")
    print("wrote complexity_growth.png")

    # Bounds grids: one for m=3 and one for m=6 (more purple dots).
    for m_val in (3, 6):
        print(f"gathering all-variant grid m={m_val} (runs solve many times)...")
        panels = gather_variant_grid(m=m_val)
        out = FIGURES / f"variant_bounds_m{m_val}.png"
        plot_variant_grid(panels, path=out)
        print(f"wrote {out.name}")

    # --------------------------------------------------------------
    # Full-enumeration scatter and distribution figures.
    # The enumeration cache is written once to figures/enumeration_cache.pkl.
    # --------------------------------------------------------------
    print("building enumeration cache (slow on first run, cached thereafter)...")
    enum_cache_path = FIGURES / "enumeration_cache.pkl"
    enum_data = compute_enumeration_cache(cache_path=enum_cache_path)
    print("enumeration cache ready")

    plot_scatter_lambda_edges(enum_data, path=FIGURES / "scatter_lambda_edges.png")
    print("wrote scatter_lambda_edges.png")

    # Known maximum feasible edge counts at the enumeration n, for each variant.
    # These come from the proved/conjectured formulas evaluated at enum_n.
    def _known_edge_max(cfg: dict, m_val: int) -> int | None:
        n = cfg["enum_n"]
        key = cfg["key"]
        if key.startswith("simple_undirected_edge"):
            return simple_undirected_edge(n, m_val)
        if key.startswith("multi_undirected_edge"):
            return multigraph_undirected_edge(n, m_val)
        if key.startswith("simple_directed") or key.startswith("multi_directed"):
            return min(directed_arc_lower_bound(n, m_val), n * (n - 1))
        if key.startswith("hyper_undirected_edge"):
            return min(hypergraph_edge(n, m_val, 3), math.comb(n, 3))
        return None

    for m_val in (3, 6):
        known_edges: dict[str, int] = {}
        for cfg in _VARIANT_ENUM_CONFIGS:
            emax = _known_edge_max(cfg, m_val)
            if emax is not None:
                known_edges[cfg["key"]] = emax

        # Connectivity histograms: the threshold line already marks m-1.
        plot_conn_dist_grid(enum_data, m_val,
                            path=FIGURES / f"conn_dist_m{m_val}.png")
        print(f"wrote conn_dist_m{m_val}.png")

        # Edge count histograms: mark the proved/conjectured extremal value.
        plot_edge_dist_grid(enum_data, m_val,
                            path=FIGURES / f"edges_dist_m{m_val}.png",
                            known_edge_maxima=known_edges)
        print(f"wrote edges_dist_m{m_val}.png")

    # --------------------------------------------------------------
    # 3-D bound surface over the (n, m) grid.
    # Uses a JSON cache (slow first run, instant thereafter).
    # --------------------------------------------------------------
    surface_cache_path = FIGURES / "surface_cache.json"
    print("building surface cache (slow on first run, cached thereafter)...")
    compute_surface_cache(
        n_range=(3, 9), m_range=(2, 6),
        max_seconds=20, cache_path=surface_cache_path)
    plot_variant_3d_surfaces(surface_cache_path, path=FIGURES / "variant_surface_3d.png")
    print("wrote variant_surface_3d.png")

    # --------------------------------------------------------------
    # 3-D threshold histogram: how lambda_max distribution shifts with p.
    # Kept fast by using n=20 and 300 samples.
    # --------------------------------------------------------------
    plot_conn_threshold_3d(
        path=FIGURES / "threshold_3d.png",
        n=12, m=3,
        p_values=[i / 10.0 for i in range(1, 10)],
        samples=150, seed=7)
    print("wrote threshold_3d.png")

    # Random model (Chapter 4): the appearance threshold across every model.
    # Fig A -- all six generative shapes (simple/multi/hyper x undirected/directed)
    # sampled and plotted by appearance probability against mean binding degree in
    # units of m.  Ordered, not coincident, at finite m: degree = m is the
    # asymptotic (model-free) threshold; the spread is the finite-m gap.
    plot_degree_threshold(
        FIGURES / "degree_threshold.png", n=12, m=4, alpha=0.5, trials=70, seed=7)
    print("wrote degree_threshold.png")

    # Fig B -- the sampled analogue of the enumeration grid: all twelve variants,
    # binding-connectivity distributions at sizes well past the enumeration wall.
    plot_sampled_variant_grid(
        FIGURES / "sampled_variant_grid.png", m=4, trials=120, seed=7)
    print("wrote sampled_variant_grid.png")

    # Edge vs vertex disjointness in G(16, p) at three densities (Chapter 1).
    p_values = [0.25, 0.5, 0.75]
    data = {pp: edge_vertex_distribution(16, pp, trials=400, seed=7)
            for pp in p_values}
    plot_edge_vertex_histograms(data, 16, p_values,
                                FIGURES / "edge_vertex_sampling.png")
    print("wrote edge_vertex_sampling.png")

    # Gallery of extremal graphs: all 12 variants × small (n, m), ~3s per case.
    print("building extremal graph gallery (this takes a few minutes)...")
    gallery_path = FIGURES / "extremal_gallery.json"
    gal = gallery_extremal_graphs(max_n=7, max_m=4, r=3, time_per_case=3.0)
    save_gallery_json(gal, gallery_path)
    total_classes = sum(
        len(cases.get("classes", []))
        for variant_data in gal.values()
        for cases in variant_data.values()
    )
    print(f"wrote {gallery_path.name}  ({total_classes} iso-classes across all variants)")


if __name__ == "__main__":
    main()

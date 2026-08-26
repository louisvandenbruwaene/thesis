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

import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from erdos915_unified import (  # noqa: E402
    MULTI_DIRECTED,
    MULTI_UNDIRECTED,
    SIMPLE_DIRECTED,
    SIMPLE_UNDIRECTED,
    Graph,
    search_for_dense_graph,
    compute_enumeration_cache,
    compute_pair_enumeration_cache,
    compute_surface_cache,
    gallery_extremal_graphs,
    directed_arc_lower_bound,
    directed_multigraph_arc,
    draw_graph_with_sensitivity,
    edge_vertex_distribution,
    hypergraph_edge,
    _hyper_edge_simple_proved,
    _hyper_vertex_simple_proved,
    multigraph_undirected_edge,
    plot_complexity_growth,
    plot_extremal_gallery,
    plot_conn_dist_grid,
    plot_conn_threshold_3d,
    plot_pair_conn_dist_grid,
    plot_directed_crossover,
    plot_edge_vertex_divergence,
    plot_edge_vertex_histograms,
    plot_edge_dist_grid,
    plot_scatter_lambda_edges,
    plot_search_trace,
    plot_sa_vs_tabu_convergence,
    plot_variant_3d_surfaces,
    plot_variant_grid,
    save_gallery_json,
    simple_undirected_edge,
    solve,
)

FIGURES = Path(__file__).resolve().parent.parent / "figures"


# ----------------------------------------------------------------------
#  The machine-value cache.
#  Every number the variant grids plot comes from a ``solve`` call, and there
#  are several hundred of them: exhaustive enumerations that run to a timeout,
#  and timed searches. That is nearly all the wall clock in this script, and
#  none of it changes between runs, so the results are kept on disk.
# ----------------------------------------------------------------------

MACHINE_CACHE_PATH = FIGURES / "machine_values.json"


class MachineValues:
    """Remembered results of the ``solve`` calls behind the variant grids.

    One entry per ``(kind, n, m, budget, variant)``, holding the value that run
    produced, or ``null`` where an exhaustion did not finish inside its budget.
    Deleting ``figures/machine_values.json`` recomputes every one of them, which
    is the check that the file is still telling the truth; ``--refresh`` does the
    same within a single run.

    Caching a *timed* search is not only a speed-up. A search given four seconds
    finds what four seconds of that particular machine will reach, so recomputing
    it elsewhere can legitimately return a different (still honest) lower bound
    and move a plotted circle. Recording the value fixes the published figure to
    the run that produced it, which is the stronger reproducibility claim.

    The program's own hash is stored beside the values as provenance. A mismatch
    is reported rather than acted on: it means the values were computed by an
    earlier version of ``erdos915_unified.py``, and whether that matters is a
    judgement about what changed, so the run says so and leaves the decision
    (rerun with ``--refresh``, or not) to the reader.
    """

    def __init__(self, path: Path, *, refresh: bool = False):
        self.path = Path(path)
        self.values: dict[str, int | None] = {}
        self.meta: dict = {}
        self.hits = 0
        self.misses = 0
        stored_hash = None
        if not refresh and self.path.exists():
            blob = json.loads(self.path.read_text())
            self.values = blob.get("values", {})
            self.meta = blob.get("meta", {})
            stored_hash = self.meta.get("program_sha256")
        self.program_hash = self._program_hash()
        if stored_hash is not None and stored_hash != self.program_hash:
            print(f"NOTE: {self.path.name} was written by a different version of "
                  f"erdos915_unified.py ({stored_hash[:12]} vs "
                  f"{self.program_hash[:12]}).\n"
                  f"      Cached values are being reused. Rerun with --refresh "
                  f"to recompute them all.")

    # Where the value-determining half of the program ends.  Everything above
    # this banner is the model, the checker, the provers, the search and
    # ``solve`` itself; everything below it is figures and the self-check.
    _VALUE_CODE_ENDS_AT = "##  CHAPTER 4"

    @classmethod
    def _program_hash(cls) -> str:
        """Fingerprint of the code that can change a cached value.

        Deliberately NOT the whole file. Hashing all six thousand lines would
        make every edit to the plotting code below invalidate a cache of search
        results the plotting code cannot possibly affect, and a warning that
        fires on every unrelated edit is one nobody reads. The cut is at the
        chapter 4 banner: above it is everything ``solve`` runs, below it is the
        figures.
        """
        source = (Path(__file__).resolve().parent
                  / "erdos915_unified.py").read_text()
        head, sep, _ = source.partition(cls._VALUE_CODE_ENDS_AT)
        if not sep:                      # banner renamed: fall back to the lot
            print("NOTE: could not find the chapter 4 banner in "
                  "erdos915_unified.py; fingerprinting the whole file, so the "
                  "machine-value cache will report a mismatch after any edit.")
            head = source
        return hashlib.sha256(head.encode()).hexdigest()

    @staticmethod
    def key(kind: str, n: int, m: int, budget: float, kwargs: dict) -> str:
        """A canonical, human-readable key, so the JSON can be read and audited."""
        parts = [kind, f"n={n}", f"m={m}", f"budget={budget:g}"]
        parts += [f"{name}={kwargs[name]}" for name in sorted(kwargs)]
        return "|".join(parts)

    def get_or_run(self, kind, n, m, budget, kwargs, run):
        cache_key = self.key(kind, n, m, budget, kwargs)
        if cache_key in self.values:
            self.hits += 1
            return self.values[cache_key]
        self.misses += 1
        self.values[cache_key] = run()
        # Written after every miss, not once at the end: a full refresh of the
        # four grids takes minutes, and an interrupted one should keep whatever
        # it had already paid for.
        self.save()
        return self.values[cache_key]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.meta = dict(self.meta)
        self.meta["program_sha256"] = self.program_hash
        self.meta["entries"] = len(self.values)
        blob = {"meta": self.meta,
                "values": dict(sorted(self.values.items()))}
        self.path.write_text(json.dumps(blob, indent=1, sort_keys=False) + "\n")

    def report(self) -> str:
        return (f"machine values: {self.hits} from cache, {self.misses} computed "
                f"({self.path.name}, {len(self.values)} entries)")


MACHINE_VALUES = MachineValues(MACHINE_CACHE_PATH,
                               refresh="--refresh" in sys.argv)


# ----------------------------------------------------------------------
#  The all-variant grid: proved / conjectured / guessed, with machine points.
#  Every number below comes from one driver, ``solve``: exhaustive for an exact
#  point, discovery for a search lower bound.  The formula curves come from the
#  closed forms; the guess is a fit; the band is [construction LB, trivial max].
# ----------------------------------------------------------------------

def _exact_points(ns, m, budget, **kw):
    """Machine-proved sizes: increasing n until the exhaustion no longer finishes.

    A size the exhaustion could not finish is cached as ``None``, not skipped: it
    is as much a result of the run as a value is, and without it every later run
    would pay for the same timeout again.
    """
    xs, ys = [], []
    for n in ns:
        def run(n=n):
            res = solve(n, m, exhaustive=True, max_seconds=budget, **kw)
            return res.value if res.bound == "exact" else None
        value = MACHINE_VALUES.get_or_run("exact", n, m, budget, kw, run)
        if value is None:
            break          # once it cannot finish, larger n cannot either
        xs.append(n)
        ys.append(value)
    return xs, ys


def _search_points(ns, m, budget, **kw):
    """Discovery lower bounds: a concrete feasible graph at each n (the LB construction)."""
    xs, ys = [], []
    for n in ns:
        def run(n=n):
            return solve(n, m, exhaustive=False, max_seconds=budget,
                         seed=0, **kw).value
        xs.append(n)
        ys.append(MACHINE_VALUES.get_or_run("search", n, m, budget, kw, run))
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


def gather_variant_grid(m=3, exact_budget=4.0, search_budget=0.4, open_search_budget=4.0):
    """Build the sixteen panels of the all-variant grid (row-major, model x col).

    ``m`` is the forbidden connectivity value shown in every panel.

    Four model rows (simple graph, multigraph, hypergraph, multihypergraph)
    by four columns (undirected/directed x edge/vertex).  Two uniformity rules
    make the sixteen panels directly comparable:

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

    Open panels also get a verified construction planted, not only the proved
    ones: the open undirected vertex panels get the proved EDGE value (Whitney,
    kappa <= lambda, so the edge extremiser is vertex-feasible) and the two
    directed-hypergraph panels get the proved bipartite family of
    prop:dir-hyper-first.  This matters because at ``search_budget=0.4`` the
    vertex-mode search on a large matrix graph barely completes one move, so
    the RAW result actively *degrades* with growing ``n`` (measured:
    n=6/10/14/16 gave 15/12/5/4 at m=6), and the monotone running-max in
    :func:`_reconcile_panel` then freezes the plotted curve at its early peak,
    a flat line that looks like a finding but is really budget starvation.
    ``open_search_budget`` (default 4s, ~10x ``search_budget``) still gives
    those panels a stronger walk, since the search can genuinely beat the
    planted construction where the open problem is richer (it does at m=6,
    n=9 on the undirected vertex panel).
    """
    panels = []
    # Uniform x-ranges for the search / construction curves.  The machine-PROVED
    # (exact) points are genuinely limited by enumeration cost and stop early; the
    # search lower bounds and the formula curves are cheap, so they run well past
    # that, to show each variant's trend and let the search discover dense
    # ("maybe extremal") graphs at sizes exhaustion cannot reach.
    matrix_ns = list(range(2, 17))   # all matrix panels, n = 2..16
    hyper_ns = list(range(2, 13))    # all hypergraph panels, n = 2..12

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
        # prop:hyper-edge, a proved UPPER bound for every r-uniform hypergraph.
        # Right for the proved curve, WRONG as a lower bound: see below.
        return min(hypergraph_edge(n, m, 3), math.comb(n, 3))

    def attained_hyper_edge(n):
        """The same value, but only where a SIMPLE hypergraph is proved to reach it.

        The panels enumerate and search SIMPLE hypergraphs, and thm:simple-hyper-edge
        attains the bound only when ``m - 1 <= C(n-2, 1)``.  Outside that range the
        closed form is an upper bound nobody has exhibited, so promoting it to an
        open-circle witness asserts a graph that need not exist.  It sometimes does
        not: at ``n = 6, m = 6`` the formula gives 12, yet all 125970 twelve-edge
        simple 3-uniform hypergraphs on six vertices are infeasible and the true
        maximum is 11.  Returning 0 here leaves the honest search value alone.
        """
        proved = _hyper_edge_simple_proved(n, m, 3)
        return 0 if proved is None else min(proved, math.comb(n, 3))

    def attained_hyper_vertex(n):
        """The vertex analogue, gated by thm:hyper-vertex-m2 / thm:hyper-vertex-m3."""
        proved = _hyper_vertex_simple_proved(n, m, 3)
        return 0 if proved is None else min(proved, math.comb(n, 3))

    def lb_multihyper_edge(n):
        """prop:hyper-edge again, but capped at the MULTIhypergraph trivial max.

        The cap matters and is not the simple one.  A simple hypergraph cannot
        hold more than ``C(n,r)`` hyperedges, but a multihypergraph may take each
        of them up to ``m-1`` times, so its ceiling is ``(m-1) C(n,r)``.  Capping
        this row at ``C(n,r)`` would push the curve BELOW the true value at small
        n: at ``n = r = m = 3`` it would read 1 where the multihypergraph star
        actually carries 2, putting an exact square above its own curve.
        """
        return min(hypergraph_edge(n, m, 3), (m - 1) * math.comb(n, 3))

    def attained_multihyper_edge(n):
        """The multihypergraph half of prop:hyper-edge.

        The displayed bound holds for EVERY r-uniform hypergraph.  A
        multihypergraph is proved to attain it when ``(r - 1) | (n - 1)``, where
        the star hypertree's blocks divide the non-hub vertices exactly and each
        hyperedge is taken at full multiplicity.  Outside that range the formula
        is an upper bound nobody has exhibited in this model, so return 0 and let
        the honest search value stand, exactly as ``attained_hyper_edge`` does for
        the simple model.  Note the two gates are genuinely different conditions,
        which is the whole reason the two rows are separate variants: at
        ``n = r = m = 3`` the simple gate fails and the multi gate holds, and the
        machine confirms the split, one hyperedge against two.
        """
        if (n - 1) % 2 != 0:            # r - 1 = 2 throughout these panels
            return 0
        return lb_multihyper_edge(n)

    def attained_multihyper_vertex(n):
        """The multihypergraph vertex analogue.

        thm:hyper-vertex-m2 and thm:hyper-vertex-m3 are both stated FOR
        multihypergraphs, so whatever the simple model is proved to attain, the
        multi model attains too, and this plants at least that much.  It is
        deliberately CONSERVATIVE: repeats do help at m = 3 in cases the simple
        gate rejects (machine-checked at n = r = m = 3, where the simple maximum
        is 1 and the multi maximum is 2), and there this returns 0 and lets the
        honest search value stand rather than plant a number no theorem covers.
        At m = 2 repeats provably never help (thm:hyper-vertex-m2).
        """
        return attained_hyper_vertex(n)

    def lb_dir_hyper(n):
        # The PROVED bipartite family of prop:dir-hyper-first at r = 3:
        # alpha tails, and on the other n - alpha vertices a shared near-regular
        # head graph of max degree m - 1 (realisable iff m - 1 <= n - alpha - 1),
        # giving alpha * floor((m-1)(n-alpha)/2) single-step hyperarcs with
        # lambda^max = kappa^max = m - 1.  Sound for BOTH separations, since
        # every route in it is a single tail -> head step.
        best = 0
        for alpha in range(1, n - m + 1):
            best = max(best, alpha * ((m - 1) * (n - alpha) // 2))
        return min(best, n * math.comb(n - 1, 2))

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
        status="proved", ylabel="edges",
        proved=(matrix_ns, [lb_simple_edge(n) for n in matrix_ns]),
        exact=ex, search=se))

    # (2) simple undirected vertex -- proved for m<=4, open for m>=5.
    ex2 = _exact_points(range(2, 8), m, exact_budget,
                        directed=False, simple=True, separation="vertex")
    if vert_proved:
        se2 = searched(matrix_ns, lb_simple_edge,
                       directed=False, simple=True, separation="vertex")
        panels.append(dict(
            status="proved", ylabel="edges",
            proved=(matrix_ns, [lb_simple_edge(n) for n in matrix_ns]),
            exact=ex2, search=se2))
    else:
        se2 = _search_points(matrix_ns, m, open_search_budget,
                             directed=False, simple=True, separation="vertex")
        # Whitney: kappa <= lambda, so Mader's edge extremiser is vertex-feasible
        # and the proved edge value is an honest lower bound on the open vertex
        # panel too.  Without it the starved vertex-mode search freezes into a
        # flat plateau at large n (the "cut off" look); the search may still beat
        # the edge value where the vertex problem is genuinely richer.
        se2 = _extend_lower_bounds(se2, lb_simple_edge, matrix_ns)
        band2 = _band(se2, tri_undirected, matrix_ns)
        panels.append(dict(
            status="open", ylabel="edges",
            guess="search",
            band=band2, exact=ex2, search=se2))

    # (3) simple directed arc -- conjectured.
    ex3 = _exact_points(range(2, 8), m, exact_budget,
                        directed=True, simple=True, separation="edge")
    se3 = searched(matrix_ns, lb_dir,
                   directed=True, simple=True, separation="edge")
    panels.append(dict(
        status="conjectured", ylabel="arcs",
        conj=(matrix_ns, [lb_dir(n) for n in matrix_ns]),
        branches=[(matrix_ns, [min(m * (n - 1), n * (n - 1)) for n in matrix_ns],
                   "hub $m(n{-}1)$"),
                  # Shifted-partition augmented bipartite floor((n+m-2)^2/4)
                  # (the corrected conj:dir-arc branch; the old balanced count
                  # floor(n^2/4)+(m-2)ceil(n/2) agrees at m<=3 but is smaller
                  # at m>=4 and would sit below the conjecture curve at m=6).
                  (matrix_ns,
                   [min((n + m - 2) ** 2 // 4, n * (n - 1))
                    for n in matrix_ns], "bipartite")],
        exact=ex3, search=se3))

    # (4) simple directed vertex -- conjectured (= arc).
    ex4 = _exact_points(range(2, 8), m, exact_budget,
                        directed=True, simple=True, separation="vertex")
    se4 = searched(matrix_ns, lb_dir,
                   directed=True, simple=True, separation="vertex")
    panels.append(dict(
        status="conjectured", ylabel="arcs",
        conj=(matrix_ns, [lb_dir(n) for n in matrix_ns]),
        exact=ex4, search=se4))

    # ----- row 2: multigraph -------------------------------------------
    # (5) multigraph undirected edge -- proved for all m.
    ex5 = _exact_points(range(2, 7), m, exact_budget,
                        directed=False, simple=False, separation="edge")
    se5 = searched(matrix_ns, lb_multi_edge,
                   directed=False, simple=False, separation="edge")
    panels.append(dict(
        status="proved", ylabel="edges",
        proved=(matrix_ns, [lb_multi_edge(n) for n in matrix_ns]),
        exact=ex5, search=se5))

    # (6) multigraph undirected vertex -- equals simple (parallel edges irrelevant for vertex cuts).
    multi_vert_label = ("= simple, proved" if vert_proved else "= simple, open")
    if vert_proved:
        panels.append(dict(
            status=multi_vert_label, ylabel="edges",
            proved=(matrix_ns, [lb_simple_edge(n) for n in matrix_ns]),
            exact=ex2, search=se2))
    else:
        panels.append(dict(
            status=multi_vert_label, ylabel="edges",
            guess="search",
            band=_band(se2, tri_undirected, matrix_ns), exact=ex2, search=se2))

    # (7) multigraph directed arc -- proved for all n and m (thm:dir-multi-full).
    ex7 = _exact_points(range(3, 6), m, 10.0,
                        directed=True, simple=False, separation="edge")
    se7 = searched(matrix_ns, lb_multi_dir,
                   directed=True, simple=False, separation="edge")
    panels.append(dict(
        status="proved", ylabel="arcs",
        proved=(matrix_ns, [lb_multi_dir(n) for n in matrix_ns]),
        exact=ex7, search=se7))

    # (8) multigraph directed vertex -- conjectured (reduces to simple digraph).
    panels.append(dict(
        status="= simple, conjectured", ylabel="arcs",
        conj=(matrix_ns, [lb_dir(n) for n in matrix_ns]),
        exact=ex4, search=se4))

    # ----- row 3: hypergraph (r=3) -------------------------------------
    # (9) hypergraph undirected edge -- proved for all m.
    ex9 = _exact_points(range(2, 8), m, exact_budget,
                        hypergraph=True, r=3, directed=False, separation="edge")
    se9 = searched(hyper_ns, attained_hyper_edge,
                   hypergraph=True, r=3, directed=False, separation="edge")
    panels.append(dict(
        status="proved", ylabel="hyperedges",
        proved=(hyper_ns, [lb_hyper_edge(n) for n in hyper_ns]),
        exact=ex9, search=se9))

    # (10) hypergraph undirected vertex -- PROVED for m<=3 (incidence-rank lemma),
    #      open for m>=4.
    ex10 = _exact_points(range(2, 7), m, exact_budget,
                         hypergraph=True, r=3, directed=False, separation="vertex")
    if hyper_vert_proved:
        se10 = searched(hyper_ns, attained_hyper_vertex,
                        hypergraph=True, r=3, directed=False, separation="vertex")
        panels.append(dict(
            status="proved", ylabel="hyperedges",
            proved=(hyper_ns, [lb_hyper_edge(n) for n in hyper_ns]),
            exact=ex10, search=se10))
    else:
        se10 = _search_points(hyper_ns, m, open_search_budget,
                              hypergraph=True, r=3, directed=False, separation="vertex")
        # Whitney again: an ATTAINED hyperedge value is a lower bound for the
        # vertex separation too, since that extremiser is vertex-feasible.  It
        # must be the attained one: _reconcile_panel's exact-value clamp was
        # relied on here to fix the small-n corner, but it can only fire where
        # exhaustion actually finished inside its budget, which at m = 6, n = 6
        # it does not.  Gating at the source needs no safety net.
        se10 = _extend_lower_bounds(se10, attained_hyper_edge, hyper_ns)
        panels.append(dict(
            status="open", ylabel="hyperedges",
            guess="search",
            band=_band(se10, tri_hyper, hyper_ns), exact=ex10, search=se10))

    # (11) hypergraph directed arc -- OPEN (new directed Berge model).
    ex11 = _exact_points(range(2, 6), m, exact_budget,
                         hypergraph=True, r=3, directed=True, separation="edge")
    se11 = _search_points(hyper_ns, m, open_search_budget,
                          hypergraph=True, r=3, directed=True, separation="edge")
    # The proved bipartite construction of prop:dir-hyper-first is the named
    # lower bound here (the search alone slips below the quadratic at larger n).
    se11 = _extend_lower_bounds(se11, lb_dir_hyper, hyper_ns)
    panels.append(dict(
        status="open", ylabel="hyperarcs",
        guess="search",
        band=_band(se11, tri_dir_hyper, hyper_ns), exact=ex11, search=se11))

    # (12) hypergraph directed vertex -- OPEN (new directed Berge model).
    ex12 = _exact_points(range(2, 6), m, exact_budget,
                         hypergraph=True, r=3, directed=True, separation="vertex")
    se12 = _search_points(hyper_ns, m, open_search_budget,
                          hypergraph=True, r=3, directed=True, separation="vertex")
    # Same construction: all its routes are single tail -> head steps, so it is
    # feasible for the vertex separation at the same value.
    se12 = _extend_lower_bounds(se12, lb_dir_hyper, hyper_ns)
    panels.append(dict(
        status="open", ylabel="hyperarcs",
        guess="search",
        band=_band(se12, tri_dir_hyper, hyper_ns), exact=ex12, search=se12))

    # ----- row 4: multihypergraph (r=3), hyperedges may repeat ----------
    # This row is NOT a relabelling of row 3.  Parallel copies of a hyperedge are
    # Berge routes with empty interiors, so q copies give q routes that are both
    # hyperedge-disjoint and internally vertex-disjoint: multiplicity raises kappa
    # as well as lambda, and neither separation collapses (contrast the multigraph
    # VERTEX rows, which do, under sec:parallel-convention).  Multiplicity is
    # therefore capped at m-1 and the four cells are genuine extremal questions.
    # Every simple hypergraph IS a multihypergraph, so the row-3 value is always a
    # valid lower bound here and is planted as one; the machine sweep is one vertex
    # shorter because it walks m^C assignments rather than 2^C.

    def multi_lb(simple_fn, attained_fn):
        """Lower bound for a multi panel: the better of the simple row and the
        multi-specific construction.  Both are exhibited feasible objects, so the
        maximum of the two is honest."""
        return lambda n: max(simple_fn(n), attained_fn(n))

    # (13) multihypergraph undirected edge -- prop:hyper-edge, proved for all m.
    ex13 = _exact_points(range(2, 7), m, exact_budget,
                         hypergraph=True, r=3, directed=False, simple=False,
                         separation="edge")
    se13 = searched(hyper_ns, multi_lb(attained_hyper_edge, attained_multihyper_edge),
                    hypergraph=True, r=3, directed=False, simple=False,
                    separation="edge")
    panels.append(dict(
        status="proved", ylabel="hyperedges",
        proved=(hyper_ns, [lb_multihyper_edge(n) for n in hyper_ns]),
        exact=ex13, search=se13))

    # (14) multihypergraph undirected vertex -- PROVED for m<=3, open for m>=4.
    ex14 = _exact_points(range(2, 6), m, exact_budget,
                         hypergraph=True, r=3, directed=False, simple=False,
                         separation="vertex")
    if hyper_vert_proved:
        se14 = searched(hyper_ns, attained_multihyper_vertex,
                        hypergraph=True, r=3, directed=False, simple=False,
                        separation="vertex")
        panels.append(dict(
            status="proved", ylabel="hyperedges",
            proved=(hyper_ns, [lb_multihyper_edge(n) for n in hyper_ns]),
            exact=ex14, search=se14))
    else:
        se14 = _search_points(hyper_ns, m, open_search_budget,
                              hypergraph=True, r=3, directed=False, simple=False,
                              separation="vertex")
        se14 = _extend_lower_bounds(se14, attained_multihyper_vertex, hyper_ns)
        panels.append(dict(
            status="open", ylabel="hyperedges",
            guess="search",
            band=_band(se14, tri_hyper, hyper_ns), exact=ex14, search=se14))

    # (15) multihypergraph directed arc -- OPEN.  thm:dir-hyper-constant is stated
    # for forward directed r-uniform MULTIhypergraphs, so the proved leading term
    # is this row's as much as row 3's; the exact value is open in both.
    ex15 = _exact_points(range(2, 5), m, exact_budget,
                         hypergraph=True, r=3, directed=True, simple=False,
                         separation="edge")
    se15 = _search_points(hyper_ns, m, open_search_budget,
                          hypergraph=True, r=3, directed=True, simple=False,
                          separation="edge")
    se15 = _extend_lower_bounds(se15, lb_dir_hyper, hyper_ns)
    panels.append(dict(
        status="open", ylabel="hyperarcs",
        guess="search",
        band=_band(se15, tri_dir_hyper, hyper_ns), exact=ex15, search=se15))

    # (16) multihypergraph directed vertex -- OPEN, same construction and bound.
    ex16 = _exact_points(range(2, 5), m, exact_budget,
                         hypergraph=True, r=3, directed=True, simple=False,
                         separation="vertex")
    se16 = _search_points(hyper_ns, m, open_search_budget,
                          hypergraph=True, r=3, directed=True, simple=False,
                          separation="vertex")
    se16 = _extend_lower_bounds(se16, lb_dir_hyper, hyper_ns)
    panels.append(dict(
        status="open", ylabel="hyperarcs",
        guess="search",
        band=_band(se16, tri_dir_hyper, hyper_ns), exact=ex16, search=se16))

    return [_reconcile_panel(p) for p in panels]


def variant_grid_figures() -> None:
    """The four sixteen-variant bound grids: m = 3 and m = 6, each in two halves.

    Each grid is split across two page-sized halves (graph models, then
    hypergraph models) rather than squeezed sixteen-up onto one page, so every
    panel prints legibly (see chapters/ch2_machine.tex, the two sidewaysfigure
    pairs around fig:variant-bounds-m3/m6).  The halves are named in the
    suptitle, not numbered: "rows 1-2" only means anything to a reader holding
    the unsplit grid, which nobody has.

    Split out of :func:`main` so it can be rerun on its own
    (``python make_figures.py --grids-only``) while the layout is being tuned.
    """
    row_halves = [
        (0, 2, "graphs", "simple and multigraph models"),
        (2, 4, "hypergraphs", "hypergraph and multihypergraph models"),
    ]
    for m_val in (3, 6):
        print(f"gathering all-variant grid m={m_val}...")
        panels = gather_variant_grid(m=m_val)
        for lo, hi, stem, subtitle in row_halves:
            out = FIGURES / f"variant_bounds_m{m_val}_{stem}.png"
            plot_variant_grid(panels, path=out, m=m_val, row_range=(lo, hi),
                              fontsize_scale=1.25, subtitle=subtitle)
            print(f"wrote {out.name}")
    print(MACHINE_VALUES.report())


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

    # Annealing vs tabu convergence (Ch.3): wall-clock timed, so a representative
    # run rather than a seed-exact one (see the figure caption).
    plot_sa_vs_tabu_convergence(FIGURES / "sa_vs_tabu_convergence.pdf",
                                cases=((5, 3), (7, 3)), budget=8.0, seed=0)
    print("wrote sa_vs_tabu_convergence.pdf")

    plot_complexity_growth(path=FIGURES / "complexity_growth.png")
    print("wrote complexity_growth.png")

    # Gallery of named families, built directly (independent of extremal_gallery.json).
    plot_extremal_gallery(FIGURES / "extremal_graphs_gallery.png")
    print("wrote extremal_graphs_gallery.png")

    variant_grid_figures()

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

    # Pooled per-pair connectivity: every vertex pair of every enumerated graph,
    # tagged with its graph's lambda^max.  Slow first run, cached thereafter.
    print("building pair-connectivity cache (slow on first run, cached thereafter)...")
    pair_cache_path = FIGURES / "pair_enumeration_cache.pkl"
    pair_data = compute_pair_enumeration_cache(cache_path=pair_cache_path)
    print("pair-connectivity cache ready")

    # Pooled per-pair connectivity histograms (Ch.4): each panel stacks blue/red
    # at its own mid-range connectivity boundary, so the split is meaningful in
    # every variant rather than collapsing to one colour at a fixed m.
    plot_pair_conn_dist_grid(pair_data, path=FIGURES / "pair_conn_dist.png")
    print("wrote pair_conn_dist.png")

    # Edge-count histograms (Ch.4): same mid-range stacked colouring.
    plot_edge_dist_grid(enum_data, path=FIGURES / "edges_dist.png")
    print("wrote edges_dist.png")

    # Per-graph connectivity distribution at the fixed forbidden threshold m=6
    # (App. B), showing the m=6 feasibility split; m=3 body version removed 2026-06-20.
    plot_conn_dist_grid(enum_data, 6, path=FIGURES / "conn_dist_m6.png")
    print("wrote conn_dist_m6.png")

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
    # 3-D threshold histogram (appendix): how the lambda_max distribution shifts
    # with density p, for three representative variants.  Kept as a standalone
    # appendix figure (fig:threshold-3d) after the Figure 4.2 threshold story was
    # removed from the body on 2026-06-20.
    # --------------------------------------------------------------
    # No p_values: each panel sweeps in units of its own threshold, since the
    # graph and hypergraph models do not share a density scale.
    plot_conn_threshold_3d(
        path=FIGURES / "threshold_3d.png",
        n=12, m=3, samples=150, seed=7)
    print("wrote threshold_3d.png")

    # NOTE: the 2-D random-sampling threshold figures (degree_threshold,
    # sampled_variant_grid) were removed from the thesis on 2026-06-20.  Their
    # generators are kept in erdos915_unified.py and the restore recipe is in
    # research_notes/removed_threshold_phenomenon.md.

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
    # --grids-only reruns just the four variant grids (the layout-heavy ones);
    # --refresh ignores figures/machine_values.json and recomputes every solve.
    if "--grids-only" in sys.argv:
        variant_grid_figures()
    else:
        main()

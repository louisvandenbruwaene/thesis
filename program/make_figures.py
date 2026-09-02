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
import datetime
import math
import platform
import subprocess
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
# The record of what the machine returned is evidence, not a drawing, so it
# lives beside the code that produced it: the thesis hands the reader main.pdf
# and this program/ directory, and everything the audit section names has to be
# inside one of the two.  The offcut-only caches (surface, enumeration) stay in
# ../figures/, since nothing outside the offcuts document refers to them.
DATA = Path(__file__).resolve().parent / "data"


# ----------------------------------------------------------------------
#  The machine-value record.
#  Every number the variant grids plot comes from a ``solve`` call, and there
#  are several hundred of them: exhaustive enumerations that run to a timeout,
#  and timed searches.  That is nearly all the wall clock in this script.
#
#  Those numbers are an EXPERIMENT, and this file is its result.  The two acts
#  are kept apart:
#
#    * rendering (no flag) reads the frozen record and never calls ``solve``.
#      It is a reproducible drawing operation: the same file draws the same
#      figures on any machine, in seconds.
#    * rebuilding (``--rebuild``) recomputes every value from scratch, consults
#      nothing, and writes a CANDIDATE beside the record.  ``--compare`` then
#      shows what moved, and only a deliberate ``--promote`` replaces the
#      published file.
#
#  Keeping them apart is what makes the figures reproducible.  A timed search
#  finds what that machine reached in that budget, so a render that quietly
#  recomputed would redraw the thesis differently on a busier laptop.
# ----------------------------------------------------------------------

MACHINE_CACHE_PATH = DATA / "machine_values.json"
# A rebuild in progress writes here, never over the published record.  It also
# survives an interruption: a twelve-hour recomputation that dies at hour eleven
# resumes from this file instead of starting again.
MACHINE_CANDIDATE_PATH = DATA / "machine_values.candidate.json"


# How the vertex separation counts parallel edges in the two multigraph cells.
# "incidence-1": routes are internally disjoint paths of the incidence graph, so
# q parallel edges are q routes (sec:incidence-convention).  Bump this if the
# convention ever changes again; MachineValues.key stamps it on exactly the
# cache entries whose value depends on it.
VERTEX_CONVENTION = "incidence-1"


class MissingMachineValue(KeyError):
    """A render asked for a value the frozen record does not hold.

    Raised rather than computed, because computing it would make this render
    disagree with the published figures for reasons no reader could see.
    """


class MachineValues:
    """The frozen record of what the machine returned, and the rebuild that makes it.

    One entry per ``(kind, n, m, budget, variant)``, holding the value that run
    produced, or ``null`` where an exhaustion did not finish inside its budget.
    A ``null`` is a result too: without it every later render would pay for the
    same timeout again.

    The record carries provenance beside the values, saying which program, which
    commit and which interpreter produced them.  It is recorded, not enforced:
    nothing here refuses to draw because a fingerprint moved.  Whether a change
    to the program invalidates the experiment is a judgement about what changed,
    and the honest way to settle it is ``--rebuild`` followed by ``--compare``,
    which answers with the numbers themselves rather than with a hash.
    """

    def __init__(self, path: Path, *, rebuild: bool = False,
                 candidate: Path | None = None):
        self.path = Path(path)
        self.candidate = Path(candidate) if candidate is not None else (
            self.path.with_name(self.path.stem + ".candidate.json"))
        self.rebuilding = rebuild
        self.values: dict[str, int | None] = {}
        self.published: dict[str, int | None] = {}
        self.meta: dict = {}
        self.hits = 0
        self.misses = 0
        self.resumed = 0
        if self.path.exists():
            blob = json.loads(self.path.read_text())
            self.published = blob.get("values", {})
            self.meta = blob.get("meta", {})
            if not rebuild:
                self.values = dict(self.published)
        self.program_hash = self._program_hash()
        if rebuild:
            self._resume()

    # -- provenance ----------------------------------------------------------

    # Where the value-determining half of the program ends.  Everything above
    # this banner is the model, the checker, the provers, the search and
    # ``solve`` itself; everything below it is figures and the self-check.
    _VALUE_CODE_ENDS_AT = "##  CHAPTER 4"

    @classmethod
    def _program_hash(cls) -> str:
        """Fingerprint of the code that can change a value.

        Deliberately NOT the whole file. Hashing all six thousand lines would
        make every edit to the plotting code below invalidate a fingerprint on
        results the plotting code cannot possibly affect.  The cut is at the
        chapter 4 banner: above it is everything ``solve`` runs, below it is the
        figures.

        This is provenance and nothing more.  It records which program produced
        a number, which a reader can check; it cannot tell a change that alters
        an answer from one that cannot, so it is never used to decide whether a
        value may be drawn.
        """
        source = (Path(__file__).resolve().parent
                  / "erdos915_unified.py").read_text()
        head, sep, _ = source.partition(cls._VALUE_CODE_ENDS_AT)
        if not sep:                      # banner renamed: fall back to the lot
            print("NOTE: could not find the chapter 4 banner in "
                  "erdos915_unified.py; fingerprinting the whole file.")
            head = source
        return hashlib.sha256(head.encode()).hexdigest()

    def _provenance(self) -> dict:
        """What produced these numbers, recorded so a reader can check it."""
        try:
            commit = subprocess.run(
                ["git", "rev-parse", "--short=12", "HEAD"],
                cwd=Path(__file__).resolve().parent, capture_output=True,
                text=True, timeout=10)
            source_commit = commit.stdout.strip() if commit.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            source_commit = None
        return {
            "program_sha256": self.program_hash,
            "source_commit": source_commit,
            "python": platform.python_version(),
            "platform": platform.platform(terse=True),
            "computed": datetime.date.today().isoformat(),
            "entries": len(self.values),
        }

    # -- keys ----------------------------------------------------------------

    @staticmethod
    def key(kind: str, n: int, m: int, budget: float, kwargs: dict) -> str:
        """A canonical, human-readable key, so the JSON can be read and audited.

        The vertex convention is stamped on exactly the entries whose value
        depends on it (the two multigraph vertex cells), so a convention change
        orphans those and leaves every other entry addressable.  Which entries
        those are is settled by the model, not by taste: the edge separation
        never depended on it, the hypergraph checker has always given a repeated
        hyperedge one gate of capacity ``mu``, and a simple graph has every
        multiplicity at most one.
        """
        parts = [kind, f"n={n}", f"m={m}", f"budget={budget:g}"]
        parts += [f"{name}={kwargs[name]}" for name in sorted(kwargs)]
        if (kwargs.get("separation") == "vertex" and not kwargs.get("simple", True)
                and not kwargs.get("hypergraph", False)):
            parts.append(f"convention={VERTEX_CONVENTION}")
        return "|".join(parts)

    # -- the two paths -------------------------------------------------------

    def get_or_run(self, kind, n, m, budget, kwargs, run):
        """Read the frozen value, or compute it when rebuilding."""
        cache_key = self.key(kind, n, m, budget, kwargs)
        if not self.rebuilding:
            if cache_key not in self.values:
                raise MissingMachineValue(
                    f"{self.path.name} has no entry for\n  {cache_key}\n"
                    f"Rendering never computes a missing value, because a figure "
                    f"drawn from a fresh timed run would not match the published "
                    f"ones. Run 'make_figures.py --rebuild' to recompute the "
                    f"record, then --compare and --promote it.")
            self.hits += 1
            return self.values[cache_key]
        if cache_key in self.values:
            self.hits += 1                 # recovered from an interrupted rebuild
            return self.values[cache_key]
        self.misses += 1
        self.values[cache_key] = run()
        # Written after every value, not once at the end: a rebuild takes hours
        # and an interrupted one should keep what it has already paid for.
        self.save()
        return self.values[cache_key]

    def _resume(self) -> None:
        """Pick an interrupted rebuild back up, or ignore work this program did not do."""
        if not self.candidate.exists():
            return
        blob = json.loads(self.candidate.read_text())
        if blob.get("meta", {}).get("program_sha256") != self.program_hash:
            print(f"NOTE: ignoring {self.candidate.name}; it was computed by a "
                  f"different version of the program. Starting from nothing.")
            return
        self.values = dict(blob.get("values", {}))
        self.resumed = len(self.values)
        if self.resumed:
            print(f"NOTE: resuming an interrupted rebuild; {self.resumed} values "
                  f"recovered from {self.candidate.name}.")

    def save(self) -> None:
        """Write the candidate. Only :meth:`promote` ever writes the record."""
        self.candidate.parent.mkdir(parents=True, exist_ok=True)
        blob = {"meta": self._provenance(),
                "values": dict(sorted(self.values.items()))}
        self.candidate.write_text(json.dumps(blob, indent=1, sort_keys=False) + "\n")

    # -- reviewing a rebuild -------------------------------------------------

    def compare(self) -> list[str]:
        """Every way the candidate departs from the published record.

        Nothing is applied and nothing is judged here.  A rebuild is a rerun of
        a timed experiment on whatever machine happened to run it, so a moved
        number can mean a corrected program, a faster machine or a slower one,
        and only a person reading the list can tell which.
        """
        if not self.candidate.exists():
            return []
        fresh = json.loads(self.candidate.read_text()).get("values", {})
        report = []
        for cache_key in sorted(set(self.published) | set(fresh)):
            was, now = self.published.get(cache_key, "absent"), fresh.get(cache_key, "absent")
            if was == now:
                continue
            kind = cache_key.split("|")[0]
            note = ""
            if kind == "exact" and isinstance(was, int) and isinstance(now, int):
                note = "  <-- TWO COMPLETED EXHAUSTIONS DISAGREE"
            elif kind == "exact" and now is None:
                note = "  (did not finish this time; a fact about the machine)"
            elif kind == "search" and isinstance(was, int) and isinstance(now, int):
                note = ("  (search reached less this time)" if now < was
                        else "  (search reached more this time)")
            report.append(f"{cache_key}: {was!r} -> {now!r}{note}")
        return report

    def promote(self) -> None:
        """Replace the published record with the reviewed candidate."""
        if not self.candidate.exists():
            raise SystemExit(f"ERROR: there is no {self.candidate.name} to promote.")
        blob = json.loads(self.candidate.read_text())
        self.path.write_text(json.dumps(blob, indent=1, sort_keys=False) + "\n")
        self.candidate.unlink()
        print(f"promoted {len(blob.get('values', {}))} machine values into "
              f"{self.path.name}")

    def report(self) -> str:
        if self.rebuilding:
            return (f"machine values: {self.misses} computed, {self.resumed} "
                    f"recovered from an interrupted run "
                    f"({self.candidate.name}, {len(self.values)} entries)")
        return (f"machine values: {self.hits} read from the record "
                f"({self.path.name}, {len(self.values)} entries)")



MACHINE_VALUES = MachineValues(MACHINE_CACHE_PATH,
                               rebuild="--rebuild" in sys.argv,
                               candidate=MACHINE_CANDIDATE_PATH)


# ----------------------------------------------------------------------
#  The all-variant grid: proved / conjectured / open, with machine points.
#  Every number below comes from one driver, ``solve``: exhaustive for an exact
#  point, discovery for a search lower bound.  The formula curves come from the
#  proved or conjectured closed forms.  Open cases show discrete points only.
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
       form -- e.g. Mader's floor -- can overshoot what is actually achievable at
       small ``n``, where the complete object is the answer.)

       **The formula half of this is skipped when a panel passes**
       ``clamp_formula=False``.  It applies to a curve that is a *value*, and the
       four hypergraph panels draw a curve that is a proved upper *bound*
       (``prop:hyper-edge``), attained only when ``m-1 <= C(n-2, r-2)`` for the
       simple model or ``(r-1) | (n-1)`` for the multi one.  Clamping a bound
       makes the line mean the true maximum wherever exhaustion happened to
       finish and the looser bound wherever it did not, so one line carries two
       theorems and the switch point is set by the exhaustion budget rather than
       by any mathematics.  At ``m = 6, r = 3`` that read the true 8 at ``n = 5``
       and the un-attained 12 at ``n = 6``, where the true maximum is 11.
       Un-clamping only ever *raises* a curve, and an exact value can never
       exceed a proved bound for the model being enumerated, so no square can
       rise above its curve as a result.  The search circles are still clamped
       below: a witness really cannot beat a proved optimum.
    2. **Search lower bounds rise with ``n``.**  A feasible graph on ``n``
       vertices stays feasible on ``n+1`` (add an isolated vertex), so the best
       feasible edge count can never *drop* as ``n`` grows.  We take a running
       maximum, which is exactly that extend-by-an-isolated-vertex bound, over a
       series into which the exact values have first been folded, since a proved
       maximum is attained and is therefore itself a witness.
    3. **Open cases show points, not interpolated functions.**  The loose
       [construction, trivial-max] band dwarfed the data and is dropped.  A
       line through lower-bound points repeated the same information and made
       parity effects look like a proposed formula.  Open panels therefore
       show exact values and verified witnesses as discrete points only.
    """
    panel.pop("band", None)  # invariant 3a: no shaded certain interval

    exact = dict(zip(*panel["exact"])) if panel.get("exact") else {}

    def cap_to_exact(curve):
        if curve is None:
            return None
        xs, ys = curve
        return xs, [min(y, exact[x]) if x in exact else y for x, y in zip(xs, ys)]

    # invariant 1 applied to every formula line, unless the panel says its
    # formula is a BOUND rather than a value (see the docstring's invariant 1).
    if panel.pop("clamp_formula", True):
        for key in ("proved", "conj"):
            if panel.get(key) is not None:
                panel[key] = cap_to_exact(panel[key])
    else:
        # Tell the plotter, so its key can say "proved upper bound" rather than
        # "proved".  Every blue curve in a hypergraph grid is a bound and every
        # blue curve in a graph grid is a value, so this is a property of the
        # figure and needs no per-panel mark inside the grid.
        panel["proved_is_bound"] = True

    # invariants 1 then 2 applied to the search circles
    if panel.get("search") is not None:
        sx, sy = panel["search"]
        # Where the value is known exactly the circle IS the square: a maximum is
        # attained by some feasible object, so it caps the circle from above and
        # supplies it from below, and the running max below then carries it to
        # every larger n.  Clamping alone left a search that had underperformed
        # dragging the reported bound down past a value already proved: at
        # m = 6 the undirected multigraph incidence row printed an exact 26 at
        # n = 5 and only >= 25 at n = 6.
        sy = [exact[x] if x in exact else y for x, y in zip(sx, sy)]
        running, mono = -1, []
        for y in sy:
            running = max(running, y)
            mono.append(running)
        panel["search"] = (sx, mono)

    return panel


# The exhaustion budget was 4s, which was below what the record itself needed:
# four completed exhaustions in it take about 8.4s on this machine, so a rerun
# downgraded them to "did not finish" and _exact_points dropped four more sizes
# behind them.  All 23 unfinished entries were then probed at 45s to find where
# the real boundary is.  Two of them finish, at 24.3s and 28.6s, and the other 21
# do not, so anything below about 30s leaves a completed exhaustion marginal,
# which is the fragility this is meant to remove.  60s is a little over twice the
# slowest exhaustion that finishes at all and well under the next one that does
# not.  The search budgets are deliberately unchanged: raising those would move
# plotted witnesses rather than reproduce them, which is a different decision.
_EXACT_BUDGET = 60.0


def gather_variant_grid(m=3, exact_budget=_EXACT_BUDGET, search_budget=0.4,
                        open_search_budget=4.0):
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
    # n = 2 forces zero hyperedges for every r=3 panel below (no 3-set exists on
    # 2 vertices), a structural degeneracy rather than a data point, so the
    # hypergraph panels start where the first hyperedge can.
    hyper_ns = list(range(3, 13))    # all hypergraph panels, n = 3..12

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

    def lb_multi_vert(n):
        # The thickened tree: m-1 parallel copies of each tree edge give
        # kappa = m-1 on every tree edge and 1 elsewhere, so it is feasible
        # under the incidence convention and has (m-1)(n-1) edges.  It is the
        # exact value K_m(n) for m <= 3 (thm:hyper-vertex-m2/m3 at r = 2) and
        # a lower bound above, where bipartite blocks eventually beat it.
        return min((m - 1) * (n - 1), (m - 1) * (n * (n - 1) // 2))

    def lb_multi_dir_vert(n):
        # kappa <= lambda, so the arc extremiser of thm:dir-multi-full is
        # feasible in the vertex separation too: K_m^dir(n) >= (m-1) M(n).
        # At m = 2 this is the exact value M(n) (cor:dir-multi-incidence).
        return lb_multi_dir(n)

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
    # The multigraph vertex problem K_m(n) is the r = 2 case of the same two
    # theorems, so it is proved on the same range.
    multi_vert_proved = (m <= 3)

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
        panels.append(dict(
            status="open", ylabel="edges",
            exact=ex2, search=se2))

    # (3) simple directed arc -- conjectured.
    # The shared exact_budget (60s) is calibrated for the hypergraph panels
    # (see its own docstring) and is far too short here: at m=3, n=6 this
    # panel's own exhaustion measures 544.2s (edge) and 1422.7s (vertex) on
    # the author's machine, matching rem:dir-vertex-m3's claim that the
    # exhaustion behind the appendix's n=6 row (both separations = 15)
    # completes, while n=7 does not finish even in about an hour and a half.
    # A dedicated budget with the range capped at n=6 reproduces exactly that
    # boundary: generous enough to reach the size the appendix proves, and
    # never large enough to spend an hour discovering n=7 still will not
    # finish, which range(2, 8) under a many-minute budget would otherwise do
    # twice (edge and vertex) at every m this grid is drawn for.
    dir_simple_exact_budget = 1800.0
    ex3 = _exact_points(range(2, 7), m, dir_simple_exact_budget,
                        directed=True, simple=True, separation="edge")
    se3 = searched(matrix_ns, lb_dir,
                   directed=True, simple=True, separation="edge")
    # No named sub-branches. conj:dir-arc is the maximum of a hub count and a
    # bipartite count, and drawing the losing one as a dotted line made this the
    # only panel of sixteen with a mark the others do not have. The curve plotted
    # is the conjectured value itself, exactly as in every other panel.
    panels.append(dict(
        status="conjectured", ylabel="arcs",
        conj=(matrix_ns, [lb_dir(n) for n in matrix_ns]),
        exact=ex3, search=se3))

    # (4) simple directed vertex -- exact value open.  The arc construction is
    # an honest lower bound, but equality with the arc value is not a stated
    # conjecture and an arc upper bound does not transfer through Whitney.
    ex4 = _exact_points(range(2, 7), m, dir_simple_exact_budget,
                        directed=True, simple=True, separation="vertex")
    se4 = searched(matrix_ns, lb_dir,
                   directed=True, simple=True, separation="vertex")
    panels.append(dict(
        status="open", ylabel="arcs",
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

    # (6) multigraph undirected vertex, K_m(n) -- proved for m <= 3 (the r = 2
    # case of thm:hyper-vertex-m2 and thm:hyper-vertex-m3, attained by the
    # thickened tree), open for m >= 4.  Its own runs: q parallel edges are q
    # internally disjoint routes under the incidence convention, so this is
    # not the simple problem and cannot borrow panel (2)'s points.  The
    # exhaustion is slower than the simple one (every pair ranges over m
    # values): at m = 3 n = 6 finishes in about 19s and at m = 6 n = 5 in
    # about 84s on the author's machine, so the shared 60s budget would stop
    # the m = 6 row one size early; 120s reaches both, and n = 6 at m = 6 is
    # the one size that pays the full timeout once and is then cached.
    multi_vert_exact_budget = 120.0
    ex6 = _exact_points(range(2, 7), m, multi_vert_exact_budget,
                        directed=False, simple=False, separation="vertex")
    se6 = searched(matrix_ns, lb_multi_vert,
                   directed=False, simple=False, separation="vertex")
    if multi_vert_proved:
        panels.append(dict(
            status="proved", ylabel="edges",
            proved=(matrix_ns, [lb_multi_vert(n) for n in matrix_ns]),
            exact=ex6, search=se6))
    else:
        panels.append(dict(
            status="open", ylabel="edges",
            exact=ex6, search=se6))

    # (7) multigraph directed arc -- proved for all n and m (thm:dir-multi-full).
    ex7 = _exact_points(range(2, 6), m, 10.0,
                        directed=True, simple=False, separation="edge")
    se7 = searched(matrix_ns, lb_multi_dir,
                   directed=True, simple=False, separation="edge")
    panels.append(dict(
        status="proved", ylabel="arcs",
        proved=(matrix_ns, [lb_multi_dir(n) for n in matrix_ns]),
        exact=ex7, search=se7))

    # (8) multigraph directed vertex, K_m^dir(n) -- proved at m = 2, where every
    # multiplicity is at most one and the value is M(n) (thm:dir-vertex-m2-exact);
    # for m >= 3 the leading term (m-1) n^2/4 is proved (cor:dir-multi-incidence,
    # from thm:dir-hyper-constant at r = 2) and the exact value is open, so the
    # panel shows points only, exactly as panel (4) does.  The lower bound is the
    # arc extremiser of thm:dir-multi-full, vertex-feasible because kappa <= lambda.
    # Exhaustion: n = 4 finishes in under a second at m = 3, n = 5 does not finish
    # in 120s, and at m = 6 n = 4 already does not; each failure is cached once.
    ex8 = _exact_points(range(2, 6), m, multi_vert_exact_budget,
                        directed=True, simple=False, separation="vertex")
    se8 = searched(matrix_ns, lb_multi_dir_vert,
                   directed=True, simple=False, separation="vertex")
    if m == 2:
        panels.append(dict(
            status="proved", ylabel="arcs",
            proved=(matrix_ns, [lb_multi_dir_vert(n) for n in matrix_ns]),
            exact=ex8, search=se8))
    else:
        panels.append(dict(
            status="open", ylabel="arcs",
            exact=ex8, search=se8))

    # ----- row 3: hypergraph (r=3) -------------------------------------
    # (9) hypergraph undirected edge -- proved for all m.
    ex9 = _exact_points(range(3, 8), m, exact_budget,
                        hypergraph=True, r=3, directed=False, separation="edge")
    se9 = searched(hyper_ns, attained_hyper_edge,
                   hypergraph=True, r=3, directed=False, separation="edge")
    panels.append(dict(
        status="proved", ylabel="hyperedges",
        proved=(hyper_ns, [lb_hyper_edge(n) for n in hyper_ns]),
        clamp_formula=False,  # a proved BOUND, not a value: see _reconcile_panel
        exact=ex9, search=se9))

    # (10) hypergraph undirected vertex -- PROVED for m<=3 (incidence-rank lemma),
    #      open for m>=4.
    ex10 = _exact_points(range(3, 7), m, exact_budget,
                         hypergraph=True, r=3, directed=False, separation="vertex")
    if hyper_vert_proved:
        se10 = searched(hyper_ns, attained_hyper_vertex,
                        hypergraph=True, r=3, directed=False, separation="vertex")
        panels.append(dict(
            status="proved", ylabel="hyperedges",
            proved=(hyper_ns, [lb_hyper_edge(n) for n in hyper_ns]),
            clamp_formula=False,  # a proved BOUND, not a value: see _reconcile_panel
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
            exact=ex10, search=se10))

    # (11) hypergraph directed arc -- OPEN (new directed Berge model).
    ex11 = _exact_points(range(3, 6), m, exact_budget,
                         hypergraph=True, r=3, directed=True, separation="edge")
    se11 = _search_points(hyper_ns, m, open_search_budget,
                          hypergraph=True, r=3, directed=True, separation="edge")
    # The proved bipartite construction of prop:dir-hyper-first is the named
    # lower bound here (the search alone slips below the quadratic at larger n).
    se11 = _extend_lower_bounds(se11, lb_dir_hyper, hyper_ns)
    panels.append(dict(
        status="open", ylabel="hyperarcs",
        exact=ex11, search=se11))

    # (12) hypergraph directed vertex -- OPEN (new directed Berge model).
    ex12 = _exact_points(range(3, 6), m, exact_budget,
                         hypergraph=True, r=3, directed=True, separation="vertex")
    se12 = _search_points(hyper_ns, m, open_search_budget,
                          hypergraph=True, r=3, directed=True, separation="vertex")
    # Same construction: all its routes are single tail -> head steps, so it is
    # feasible for the vertex separation at the same value.
    se12 = _extend_lower_bounds(se12, lb_dir_hyper, hyper_ns)
    panels.append(dict(
        status="open", ylabel="hyperarcs",
        exact=ex12, search=se12))

    # ----- row 4: multihypergraph (r=3), hyperedges may repeat ----------
    # This row is NOT a relabelling of row 3.  Parallel copies of a hyperedge are
    # Berge routes with empty interiors, so q copies give q routes that are both
    # hyperedge-disjoint and internally vertex-disjoint: multiplicity raises kappa
    # as well as lambda, exactly as parallel edges do in row 2 under the incidence
    # convention.  Multiplicity is therefore capped at m-1 and the four cells are
    # genuine extremal questions.
    # Every simple hypergraph IS a multihypergraph, so the row-3 value is always a
    # valid lower bound here and is planted as one; the machine sweep is one vertex
    # shorter because it walks m^C assignments rather than 2^C.

    def multi_lb(simple_fn, attained_fn):
        """Lower bound for a multi panel: the better of the simple row and the
        multi-specific construction.  Both are exhibited feasible objects, so the
        maximum of the two is honest."""
        return lambda n: max(simple_fn(n), attained_fn(n))

    # (13) multihypergraph undirected edge -- prop:hyper-edge, proved for all m.
    ex13 = _exact_points(range(3, 7), m, exact_budget,
                         hypergraph=True, r=3, directed=False, simple=False,
                         separation="edge")
    se13 = searched(hyper_ns, multi_lb(attained_hyper_edge, attained_multihyper_edge),
                    hypergraph=True, r=3, directed=False, simple=False,
                    separation="edge")
    panels.append(dict(
        status="proved", ylabel="hyperedges",
        proved=(hyper_ns, [lb_multihyper_edge(n) for n in hyper_ns]),
        clamp_formula=False,  # a proved BOUND, not a value: see _reconcile_panel
        exact=ex13, search=se13))

    # (14) multihypergraph undirected vertex -- PROVED for m<=3, open for m>=4.
    ex14 = _exact_points(range(3, 6), m, exact_budget,
                         hypergraph=True, r=3, directed=False, simple=False,
                         separation="vertex")
    if hyper_vert_proved:
        se14 = searched(hyper_ns, attained_multihyper_vertex,
                        hypergraph=True, r=3, directed=False, simple=False,
                        separation="vertex")
        panels.append(dict(
            status="proved", ylabel="hyperedges",
            proved=(hyper_ns, [lb_multihyper_edge(n) for n in hyper_ns]),
            clamp_formula=False,  # a proved BOUND, not a value: see _reconcile_panel
            exact=ex14, search=se14))
    else:
        se14 = _search_points(hyper_ns, m, open_search_budget,
                              hypergraph=True, r=3, directed=False, simple=False,
                              separation="vertex")
        se14 = _extend_lower_bounds(se14, attained_multihyper_vertex, hyper_ns)
        panels.append(dict(
            status="open", ylabel="hyperedges",
            exact=ex14, search=se14))

    # (15) multihypergraph directed arc -- OPEN.  thm:dir-hyper-constant is stated
    # for forward directed r-uniform MULTIhypergraphs, so the proved leading term
    # is this row's as much as row 3's; the exact value is open in both.
    ex15 = _exact_points(range(3, 5), m, exact_budget,
                         hypergraph=True, r=3, directed=True, simple=False,
                         separation="edge")
    se15 = _search_points(hyper_ns, m, open_search_budget,
                          hypergraph=True, r=3, directed=True, simple=False,
                          separation="edge")
    se15 = _extend_lower_bounds(se15, lb_dir_hyper, hyper_ns)
    panels.append(dict(
        status="open", ylabel="hyperarcs",
        exact=ex15, search=se15))

    # (16) multihypergraph directed vertex -- OPEN, same construction and bound.
    ex16 = _exact_points(range(3, 5), m, exact_budget,
                         hypergraph=True, r=3, directed=True, simple=False,
                         separation="vertex")
    se16 = _search_points(hyper_ns, m, open_search_budget,
                          hypergraph=True, r=3, directed=True, simple=False,
                          separation="vertex")
    se16 = _extend_lower_bounds(se16, lb_dir_hyper, hyper_ns)
    panels.append(dict(
        status="open", ylabel="hyperarcs",
        exact=ex16, search=se16))

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


# Row metadata for variant_value_tables(), in the same panel order
# gather_variant_grid() appends them: model label, column label, and (for the
# eight graph-model rows only) the symbol tab:notation uses for that
# quantity.  The four hypergraph rows have no such standing symbol
# elsewhere in the thesis, so they are left with the same words the figure's
# own column headers use and nothing more is invented.
_VARIANT_ROW_META = [
    ("simple graph", "undirected, edge", r"$\ell_m(n)$"),
    ("simple graph", "undirected, vertex", r"$k_m(n)$"),
    ("simple graph", "directed, arc", r"$\ell_m^{\mathrm{dir}}(n)$"),
    ("simple graph", "directed, vertex", r"$k_m^{\mathrm{dir}}(n)$"),
    ("multigraph", "undirected, edge", r"$L_m(n)$"),
    ("multigraph", "undirected, vertex", r"$K_m(n)$"),
    ("multigraph", "directed, arc", r"$L_m^{\mathrm{dir}}(n)$"),
    ("multigraph", "directed, vertex", r"$K_m^{\mathrm{dir}}(n)$"),
    (r"hypergraph $r=3$", "undirected, edge", None),
    (r"hypergraph $r=3$", "undirected, vertex", None),
    (r"hypergraph $r=3$", "directed, arc", None),
    (r"hypergraph $r=3$", "directed, vertex", None),
    (r"multihypergraph $r=3$", "undirected, edge", None),
    (r"multihypergraph $r=3$", "undirected, vertex", None),
    (r"multihypergraph $r=3$", "directed, arc", None),
    (r"multihypergraph $r=3$", "directed, vertex", None),
]

# One shared column grid for every row, graph or hypergraph: n = 2..8.
# Chosen so most cells land inside what the matching figure already
# exhausts (see the exact_ns printed by gather_variant_grid): graph rows
# mostly finish through n=5-8, hypergraph rows through n=3-5, so the range
# runs a couple of sizes past that into formula/lower-bound territory
# rather than stopping exactly where the machine-checked numbers do. n=2 is
# left blank for every hypergraph row (see _panel_cell): no r=3 hyperedge
# exists on 2 vertices, so there is nothing to enter, not a zero to enter.
_TABLE_NS = list(range(2, 9))


def _panel_curve_key(panel):
    """Source and status of the numbers printed for one panel."""
    for key in ("proved", "conj"):
        if panel.get(key) is not None:
            return key
    if panel.get("search") is not None:
        return "search"
    raise ValueError("panel carries no formula or lower-bound points")


_CURVE_COLOR = {"proved": "vtProved", "conj": "vtConjectured", "search": "vtOpen"}


def _panel_cell(panel, n):
    """One table entry: the number, its colour, and whether it is bold (exact);
    or ``None`` if the model does not exist at this n at all (a hypergraph
    row at n=2, where the shared column grid runs one size below where any
    r=3 hyperedge can).

    Mirrors the figure's own honesty rule (\\Cref{fig:variant-bounds-m3-graphs}
    et al.): a green bold number is machine-checked exact, exactly like a
    filled square there.  Anything else takes the row's curve colour.  For a
    hypergraph row whose blue curve is a proved upper bound rather than a
    proved value (``proved_is_bound``, set by ``_reconcile_panel``), a matching
    construction closes the gap and the cell is exact; otherwise the upper
    bound is prefixed by $\\le$.  That construction is whichever the ``search``
    series holds at this n: the attainment theorem's own object where
    ``attained_hyper_*`` plants it, and the checker-verified witness the timed
    search exhibited where it does not.  Conjectured and open rows are prefixed by
    $\\ge$, since their numbers are verified constructions without proved
    optimality.  A proved graph row needs no prefix because its closed form is
    the exact value for every n.
    """
    exact_ns, exact_vals = panel["exact"]
    if n in exact_ns:
        return str(exact_vals[exact_ns.index(n)]), "vtExact", True

    key = _panel_curve_key(panel)
    curve_ns, curve_vals = panel[key]
    if n not in curve_ns:
        return None
    value = curve_vals[curve_ns.index(n)]
    color = _CURVE_COLOR[key]
    if key == "proved":
        prefix = ""
        if panel.get("proved_is_bound"):
            search_ns, search_vals = panel.get("search", ([], []))
            attained = dict(zip(search_ns, search_vals)).get(n)
            if attained != value:
                prefix = r"$\le$"
    else:
        prefix = r"$\ge$"
    return f"{prefix}{value}", color, False


def _fmt_cell(cell):
    if cell is None:
        return ""
    text, color, bold = cell
    body = rf"\textbf{{{text}}}" if bold else text
    return rf"\textcolor{{{color}}}{{{body}}}"


def variant_value_tables() -> None:
    """One exact-number companion table for all four variant-bounds grids.

    Same sixteen panels at both m=3 and m=6, same colour code
    (vtProved/vtConjectured/vtOpen for a row's status, vtExact overriding it
    wherever the machine independently confirms the number), but as numbers
    a reader can read off instead of a curve position they have to estimate
    by eye. Written as one plain ``tabular`` fragment, meant to be \\input
    inside a ``table`` environment the way figures/rediscovery_table.tex
    already is: an m=3 block of thirty-two rows (graphs then hypergraphs,
    each split into its two model rows exactly as the figures are), then an
    m=6 block the same shape.

    Split out of :func:`main` so it can be rerun on its own
    (``python make_figures.py --tables-only``).
    """
    ns = _TABLE_NS
    groups = [(0, 8), (8, 16)]
    lines = [
        "% Generated by make_figures.py:variant_value_tables().",
        "% Colours: vtProved/vtConjectured/vtOpen match the curve in the",
        "% matching figure; vtExact (bold) is a machine-checked value.",
        "% A blank cell means the model does not exist at that n (e.g. no",
        "% r=3 hyperedge exists on 2 vertices).",
        "\\begin{tabular}{ll" + "r" * len(ns) + "}",
        "\\toprule",
    ]
    header = ["Model", "Variant"] + [f"$n={n}$" for n in ns]
    lines.append(" & ".join(header) + r" \\")
    for m_val in (3, 6):
        print(f"gathering all-variant grid m={m_val} for the value table...")
        panels = gather_variant_grid(m=m_val)
        lines.append("\\midrule")
        lines.append(
            rf"\multicolumn{{{2 + len(ns)}}}{{l}}{{\textbf{{$m={m_val}$}}}} \\"
        )
        lines.append("\\midrule")
        for gi, (lo, hi) in enumerate(groups):
            if gi > 0:
                lines.append("\\midrule")
            model_start = lo
            for i in range(lo, hi):
                panel = panels[i]
                model, col, symbol = _VARIANT_ROW_META[i]
                if i > lo and i % 4 == 0:
                    lines.append("\\midrule")
                    model_start = i
                model_cell = (
                    f"\\multirow{{4}}{{*}}{{{model}}}" if i == model_start else ""
                )
                key = _panel_curve_key(panel)
                status_color = _CURVE_COLOR[key]
                variant_text = col + (f" ({symbol})" if symbol else "")
                variant_cell = (
                    rf"{variant_text}, \textcolor{{{status_color}}}{{{panel['status']}}}"
                )
                row = [model_cell, variant_cell]
                for n in ns:
                    row.append(_fmt_cell(_panel_cell(panel, n)))
                lines.append(" & ".join(row) + r" \\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out = FIGURES / "variant_table_all.tex"
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out.name}")


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)

    plot_directed_crossover(m=3, max_n=15, path=FIGURES / "directed_crossover.png")
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
    variant_value_tables()

    # --------------------------------------------------------------
    # Full-enumeration scatter and distribution figures.
    # The enumeration cache is written once to figures/enumeration_cache.json.
    # --------------------------------------------------------------
    print("building enumeration cache (slow on first run, cached thereafter)...")
    enum_cache_path = FIGURES / "enumeration_cache.json"
    enum_data = compute_enumeration_cache(cache_path=enum_cache_path)
    print("enumeration cache ready")

    plot_scatter_lambda_edges(enum_data, path=FIGURES / "scatter_lambda_edges.png")
    print("wrote scatter_lambda_edges.png")

    # Pooled per-pair connectivity: every vertex pair of every enumerated graph,
    # tagged with its graph's lambda^max.  Slow first run, cached thereafter.
    print("building pair-connectivity cache (slow on first run, cached thereafter)...")
    pair_cache_path = FIGURES / "pair_enumeration_cache.json"
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


def rebuild_machine_values() -> None:
    """Recompute every machine value from scratch. Draws nothing.

    A rebuild is the experiment, not the drawing: it calls the same gatherers the
    grids call, which is what puts every key the figures ask for into the
    candidate file, and stops there.  Reviewing the result and publishing it are
    separate deliberate acts (--compare, --promote).
    """
    print("rebuilding every machine value from scratch (hours, resumable)")
    for m_val in (3, 6):
        print(f"  gathering all-variant grid m={m_val}...")
        gather_variant_grid(m=m_val)
    print(MACHINE_VALUES.report())
    print(f"\nwrote {MACHINE_VALUES.candidate.name}. Nothing published yet.\n"
          f"Review it with   python3 make_figures.py --compare\n"
          f"then publish it  python3 make_figures.py --promote")


def compare_machine_values() -> None:
    """Show every departure of the candidate from the published record."""
    if not MACHINE_VALUES.candidate.exists():
        raise SystemExit(f"ERROR: there is no {MACHINE_VALUES.candidate.name}. "
                         f"Run --rebuild first.")
    changes = MACHINE_VALUES.compare()
    if not changes:
        print(f"{MACHINE_VALUES.candidate.name} agrees with "
              f"{MACHINE_VALUES.path.name} on every entry.")
        return
    print(f"{len(changes)} entries differ from {MACHINE_VALUES.path.name}:")
    for line in changes:
        print(f"  {line}")
    disagreements = [c for c in changes if "DISAGREE" in c]
    if disagreements:
        print(f"\n{len(disagreements)} of them are two completed exhaustions "
              f"disagreeing. That is a defect in one of the two programs, not a "
              f"timing artefact, and it needs investigating before either number "
              f"is published.")


def _render(entry) -> None:
    """Draw from the frozen record, saying plainly when a value is missing."""
    try:
        entry()
    except MissingMachineValue as exc:
        raise SystemExit(f"ERROR: {exc.args[0]}")


if __name__ == "__main__":
    # Rendering (no flag, --grids-only, --tables-only) reads the frozen record in
    # program/data/machine_values.json and never computes; --rebuild recomputes
    # every value into a candidate file; --compare shows what moved; --promote
    # publishes the candidate.
    if "--rebuild" in sys.argv:
        rebuild_machine_values()
    elif "--compare" in sys.argv:
        compare_machine_values()
    elif "--promote" in sys.argv:
        MACHINE_VALUES.promote()
    elif "--refresh" in sys.argv or "--accept-stale" in sys.argv:
        raise SystemExit(
            "ERROR: --refresh no longer exists. Recomputing and publishing are "
            "now separate acts, because a timed rerun on a different machine can "
            "legitimately return different numbers:\n"
            "  --rebuild   recompute every value from scratch into a candidate\n"
            "  --compare   show how the candidate departs from the record\n"
            "  --promote   publish the reviewed candidate")
    elif "--grids-only" in sys.argv:
        _render(variant_grid_figures)
    elif "--tables-only" in sys.argv:
        _render(variant_value_tables)
    else:
        _render(main)

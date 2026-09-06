"""
Regenerate every figure the thesis uses, from the one program next door.

This is the only figure script.  It imports the single program
``erdos915_unified.py`` and calls its plotting routines, so the figures can never
drift from the code that produces the numbers.  Run it from this ``program/``
directory:

    python make_figures.py

Each figure is written into ``../figures/``.  Every randomised search uses a
fixed initial seed. Timed reruns can differ; rendering uses the frozen record.
"""

from __future__ import annotations

import hashlib
import json
import datetime
import math
import os
import platform
import subprocess
import sys
import tempfile
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from erdos915_unified import (
    directed_arc_lower_bound,
    directed_multigraph_arc,
    hypergraph_edge,
    _hyper_edge_simple_proved,
    _hyper_vertex_simple_proved,
    multigraph_undirected_edge,
    plot_complexity_growth,
    plot_directed_crossover,
    plot_edge_vertex_divergence,
    plot_variant_grid,
    simple_undirected_edge,
    solve,
    SolveResult,
    Graph,
    _dir_tails_heads,
    C_EXTENSION_LOADED,
)

FIGURES = Path(__file__).resolve().parent.parent / "figures"
# The record of what the machine returned is evidence, not a drawing, so it
# lives beside the code that produced it: the thesis hands the reader main.pdf
# and this program/ directory, and everything the audit section names has to be
# inside one of the two.  The offcut-only caches (surface, enumeration) stay in
# ../figures/, since nothing outside the offcuts document refers to them.
DATA = Path(__file__).resolve().parent / "data"


def _write_json(path, value):
    """Atomically replace one JSON file, so interruption cannot truncate it."""
    path = Path(path)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        try:
            json.dump(value, stream, indent=1)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


# Rendering reads frozen observations. Rebuilding writes a separate candidate;
# only an explicit promotion replaces the published experiment.
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
        self.runs: dict = {}
        self.hits = 0
        self.misses = 0
        self.resumed = 0
        if self.path.exists():
            blob = json.loads(self.path.read_text())
            self.published = blob.get("values", {})
            self.meta = blob.get("meta", {})
            if not rebuild:
                self.values = dict(self.published)
                self.runs = dict(blob.get("runs", {}))
        self.program_hash = self._program_hash()
        if rebuild:
            self._resume()

    # -- provenance ----------------------------------------------------------

    @classmethod
    def _program_hash(cls) -> str:
        """Hash the complete solver, optional C source and experiment harness.

        Flow helpers below the old chapter-four boundary also affect results.
        A fingerprint is provenance, not evidence that a result is correct.
        """
        root = Path(__file__).resolve().parent
        digest = hashlib.sha256()
        for name in ("erdos915_unified.py", "_erdos_fast.c", "make_figures.py"):
            digest.update(name.encode() + b"\0" + (root / name).read_bytes() + b"\0")
        return digest.hexdigest()

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
        dependencies = {}
        for name in ("numpy", "scipy", "pulp", "networkx", "matplotlib"):
            try:
                dependencies[name] = version(name)
            except PackageNotFoundError:
                dependencies[name] = None
        binary = Path(__file__).with_name("_erdos_fast.so")
        return {
            "program_sha256": self.program_hash,
            "source_commit": source_commit,
            "python": platform.python_version(),
            "platform": platform.platform(terse=True),
            "computed": datetime.date.today().isoformat(),
            "entries": len(self.values),
            "dependencies": dependencies,
            "c_extension_loaded": C_EXTENSION_LOADED,
            "c_binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest()
                               if C_EXTENSION_LOADED else None,
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
        result = run()
        if isinstance(result, SolveResult):
            witness = result.witness
            if isinstance(witness, Graph):
                encoded = {"multiplicity_matrix": witness.mu.tolist()}
            elif witness is not None:
                edges = ([[sorted(t), sorted(h)] for t, h in
                          map(_dir_tails_heads, witness.hyperedges)]
                         if witness.directed else [sorted(e) for e in witness.hyperedges])
                encoded = {"hyperedges": edges}
            else:
                encoded = None
            self.runs[cache_key] = dict(
                value=result.value, bound=result.bound, complete=result.complete,
                method=result.method, elapsed_seconds=result.seconds,
                requested_seconds=budget, seed=0 if kind == "search" else None,
                construction_seeded=(kind == "exact" and kwargs.get("directed", False)
                                     and kwargs.get("simple", True)
                                     and not kwargs.get("hypergraph", False)),
                witness=encoded, note=result.note)
            self.runs[cache_key]["environment"] = self._provenance()
            result = result.value if kind != "exact" or result.bound == "exact" else None
        self.values[cache_key] = result
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
        self.runs = dict(blob.get("runs", {}))
        self.resumed = len(self.values)
        if self.resumed:
            print(f"NOTE: resuming an interrupted rebuild; {self.resumed} values "
                  f"recovered from {self.candidate.name}.")

    def save(self) -> None:
        """Write the candidate. Only :meth:`promote` ever writes the record."""
        self.candidate.parent.mkdir(parents=True, exist_ok=True)
        blob = {"meta": self._provenance(),
                "values": dict(sorted(self.values.items())),
                "runs": self.runs}
        _write_json(self.candidate, blob)

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
        if any("DISAGREE" in change for change in self.compare()):
            raise SystemExit("ERROR: completed exact values disagree; resolve the discrepancy before promotion.")
        blob = json.loads(self.candidate.read_text())
        _write_json(self.path, blob)
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
            return res
        value = MACHINE_VALUES.get_or_run("exact", n, m, budget, kw, run)
        if value is None:
            break          # sampling policy, not a proof that larger cases are harder
        xs.append(n)
        ys.append(value)
    return xs, ys


# Cells settled by a standalone enumeration rather than by ``solve``'s branch
# and bound, which does not finish them inside the figure budget.  Keyed by
# ``(m, n, r)`` for the simple undirected EDGE hypergraph panel.
#
# The one entry is the ``m = 6, n = 6, r = 3`` gap.  ``prop:hyper-edge`` reads
# 12 there and ``thm:simple-hyper-edge`` does not attain it, since ``m-1 <=
# C(n-2, r-2)`` asks 5 <= 4.  ``scripts/hyper_edge_m6_n6_gap.py`` walks all
# C(20, 12) = 125970 twelve-hyperedge families, finds none feasible, and
# exhibits an eleven-hyperedge one, so the true maximum is 11.  That is a
# completed exhaustive computation like any other exact value, so the panel
# carries it as one and the table prints it in bold rather than printing the
# unattained bound with a ``<=``.
_SETTLED_HYPER_EDGE_SIMPLE = {(6, 6, 3): 11}


def dir_block_bouquet_lower_bound(n: int, m: int) -> int:
    """A lower bound on ``K_m^dir(n)``: a bouquet of thickened complete digraphs.

    ``const:dir-multi-vertex-blocks`` takes the complete digraph on ``b <= m``
    vertices at multiplicity ``m+1-b``, which ``prop:dir-multi-vertex-blocks``
    checks is feasible and carries ``b(b-1)(m+1-b)`` arcs, and hangs any multiset
    of such blocks off one shared vertex.  ``b = 2`` is the bidirected edge at
    multiplicity ``m-1``, so the thickened bidirected tree is the ``b = 2`` case.

    This is the vertex-separation counterpart of
    :func:`block_bouquet_lower_bound`, and it beats the arc extremiser
    ``(m-1) M(n)`` while ``n`` is small against ``m``: at ``m = 6`` it leads
    through ``n = 8`` with 84 arcs against 80, and the extremiser leads from
    ``n = 9``.  Plotting the extremiser alone understated the panel, at ``m = 6``,
    ``n = 4`` reading 34 against a checked 36.
    """
    block = {b - 1: b * (b - 1) * (m + 1 - b)
             for b in range(2, min(n, m) + 1)}
    best = [0] * n
    for budget in range(1, n):
        for cost, value in block.items():
            if cost <= budget:
                best[budget] = max(best[budget], best[budget - cost] + value)
    return min(best[n - 1], (m - 1) * n * (n - 1))


# The exhaustive block sweep of ``scripts/multi_vertex_blocks.py``: for each m,
# ``g_m(b)`` is the largest ``W_m`` a single 2-connected block (or single edge)
# on ``b`` vertices can score, taken over every such graph that ``geng`` emits.
# A missing (m, b) entry means the sweep does not reach that cell, not that no
# block exists; ``m = 2`` is the exception, where no feasible block of order
# ``b >= 3`` exists at all.  The rows are deliberately allowed to be ragged.
# ``tab:multi-vertex-blocks`` prints the b <= 8 square, whose transcript is
# ``logs/multi_vertex_blocks_log.txt``.  The one cell beyond it, ``g_6(9) = 54``,
# comes from ``scripts/multi_vertex_blocks_b9.py`` with its own transcript in
# ``logs/multi_vertex_blocks_b9_log.txt``, and is here because m = 6 is a row the
# grids plot: without it the curve read 52 at n = 9 against a known 54.
_BLOCK_SWEEP = {
    2: {2: 1},
    3: {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8},
    4: {2: 3, 3: 6, 4: 9, 5: 12, 6: 15, 7: 18, 8: 21},
    5: {2: 4, 3: 9, 4: 14, 5: 19, 6: 24, 7: 29, 8: 34},
    6: {2: 5, 3: 12, 4: 19, 5: 26, 6: 33, 7: 40, 8: 47, 9: 54},
    7: {2: 6, 3: 15, 4: 24, 5: 33, 6: 42, 7: 52, 8: 62},
    8: {2: 7, 3: 18, 4: 30, 5: 42, 6: 54, 7: 66, 8: 79},
}


def _best_known_block(b: int, m: int) -> int:
    """The best ``W_m`` a single feasible block on ``b`` vertices is known to score.

    ``thm:multi-vertex-blocks`` allows ANY 2-connected block, so restricting the
    knapsack to one construction family understates it.  Where the exhaustive
    sweep of ``scripts/multi_vertex_blocks.py`` reaches, ``_BLOCK_SWEEP`` holds
    its answer, which is ``g_m(b)`` exactly and is what ``tab:multi-vertex-blocks``
    prints.  Beyond that range the value is the larger of the two exhibited
    families:

    * the thickened theta of ``sec:multi-vertex``, two poles joined to each of
      the other ``b-2`` vertices at multiplicity ``m-2`` and to each other at
      ``max(0, m+1-b)``, feasible exactly for ``b <= m+1``; and
    * the thickened complete bipartite block ``K_{s,t}`` at multiplicity ``m-s``
      of ``thm:multi-vertex-bipartite``, feasible for every split ``s + t = b``
      with ``s <= t <= m-1``, carrying ``st(m-s)`` edges.

    Every value returned is realised by an exhibited feasible block, so the
    knapsack built on it can never exceed the true ``K_m(n)``.  A return of ``0``
    means no block of that order is known, which for ``b >= 3`` costs budget and
    scores nothing, so the knapsack never prefers one.
    """
    swept = _BLOCK_SWEEP.get(m, {}).get(b)
    if swept is not None:
        return swept
    best = 0
    if b <= m + 1:
        best = max(best, 2 * (b - 2) * (m - 2) + max(0, m + 1 - b))
    for s in range(1, b // 2 + 1):
        if b - s <= m - 1:
            best = max(best, s * (b - s) * (m - s))
    return best


def block_bouquet_lower_bound(n: int, m: int) -> int:
    """A lower bound on ``K_m(n)``: a bouquet of the best blocks known.

    ``thm:multi-vertex-blocks`` reduces the value to a knapsack: each block costs
    ``b - 1`` vertices beyond the shared one and scores ``g_m(b)``, and the total
    cost may not exceed ``n - 1``.  :func:`_best_known_block` supplies the score,
    exhaustively where the sweep reaches and by construction beyond it.

    ``b = 2`` is the single edge at multiplicity ``m-1``, so the thickened tree is
    the ``b = 2`` case and this is never worse than it.  It returns the tree's
    ``(m-1)(n-1)`` at ``m <= 4``, where that is optimal, and beats it from
    ``m = 5`` on, where ``thm:clique-chain-vertex`` proves the tree is not
    extremal.

    An earlier version offered theta blocks alone, which the theta family caps at
    ``b <= m+1``.  That missed the larger blocks the sweep finds: at ``m = 6`` it
    read 45 at ``n = 8`` where ``g_6(8) = 47`` is attained by a block on eight
    vertices that is not a theta (graph6 ``G?AFvw``), and it understated ``n = 14``
    and ``n = 15`` the same way.
    """
    block = {b - 1: _best_known_block(b, m) for b in range(2, n + 1)}
    best = [0] * n
    for budget in range(1, n):
        for cost, value in block.items():
            if cost <= budget:
                best[budget] = max(best[budget], best[budget - cost] + value)
    return min(best[n - 1], (m - 1) * (n * (n - 1) // 2))


def _with_settled_cells(points, m, r, settled):
    """Fold externally settled exact values into an ``_exact_points`` series."""
    xs, ys = list(points[0]), list(points[1])
    known = dict(zip(xs, ys))
    for (m_key, n_key, r_key), value in settled.items():
        if m_key == m and r_key == r and n_key not in known:
            known[n_key] = value
    xs = sorted(known)
    return xs, [known[n] for n in xs]


def _search_points(ns, m, budget, **kw):
    """Raw discovery outcomes, without construction or theorem assistance."""
    xs, ys = [], []
    for n in ns:
        def run(n=n):
            return solve(n, m, exhaustive=False, max_seconds=budget,
                         seed=0, **kw)
        xs.append(n)
        ys.append(MACHINE_VALUES.get_or_run("search", n, m, budget, kw, run))
    return xs, ys


def _reconcile_panel(panel: dict) -> dict:
    """Check evidence without repairing, smoothing or replacing observations.

    A failed inequality is an error to investigate, never permission to change
    a measured result. Search outcomes need not increase with order or improve
    when the feasible family becomes larger.
    """
    panel.pop("band", None)
    if not panel.pop("clamp_formula", True):
        panel["proved_is_bound"] = True
    exact = dict(zip(*panel.get("exact", ([], []))))
    proved = dict(zip(*panel.get("proved", ([], []))))
    for n, value in exact.items():
        if n in proved and (value > proved[n] or
                            (not panel.get("proved_is_bound") and value != proved[n])):
            raise ValueError(f"exact/formula disagreement at n={n}: {value}, {proved[n]}")
    for source in ("search", "construction"):
        for n, value in zip(*panel.get(source, ([], []))):
            upper = min(exact.get(n, math.inf), proved.get(n, math.inf))
            if value > upper:
                raise ValueError(f"{source} exceeds upper bound at n={n}: {value} > {upper}")
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
    """Build sixteen panels from a common specification, keeping evidence separate.

    Parameter-dependent attainment conditions belong in construction functions,
    never in post-processing of measured results. Historical budgets are retained.
    """
    simple_edge = lambda n: simple_undirected_edge(n, m)
    multi_edge = lambda n: multigraph_undirected_edge(n, m)
    multi_arc = lambda n: directed_multigraph_arc(n, m)
    multi_vertex = lambda n: block_bouquet_lower_bound(n, m)
    multi_dir_vertex = lambda n: max(multi_arc(n), dir_block_bouquet_lower_bound(n, m))

    def simple_arc(n):
        if n < m:
            return n * (n - 1)  # complete digraph
        return max(directed_arc_lower_bound(n, m),
                   (n + m - 3) ** 2 // 4 + 2 * (m - 1))  # clique core

    # Hypergraph curves are UPPER bounds; the following functions separately
    # express where a supplied construction actually attains them.
    hyper_upper = lambda n: min(hypergraph_edge(n, m, 3), math.comb(n, 3))
    multihyper_upper = lambda n: min(hypergraph_edge(n, m, 3), (m - 1) * math.comb(n, 3))
    hyper_edge = lambda n: max(_hyper_edge_simple_proved(n, m, 3) or 0,
                               (n - 1) // 2,  # simple star with unused isolated vertices
                               _SETTLED_HYPER_EDGE_SIMPLE.get((m, n, 3), 0))
    hyper_vertex = lambda n: max(_hyper_vertex_simple_proved(n, m, 3) or 0, hyper_edge(n))

    def multihyper_edge(n):
        # Use a partial star and leave any leftover vertex isolated.
        star = (m - 1) * ((n - 1) // 2)
        # const:multihyper-six is a separate explicit construction, not a
        # replacement of the historical search observation at this cell.
        twelve = 12 if (n, m) == (6, 6) else 0
        return max(star, hyper_edge(n), twelve)

    def multihyper_vertex(n):
        # Whitney transfers either attained edge construction to vertex mode.
        return max(multihyper_edge(n), hyper_vertex(n))

    def directed_hyper(n, simple):
        # prop:dir-hyper-first: alpha tails and a degree-(m-1) head family.
        # Distinct head edges require alpha <= n-m; repeats need only two heads.
        last = n - m if simple else n - 2
        layered = max((a * ((m - 1) * (n - a) // 2)
                       for a in range(1, last + 1)), default=0)
        # const:bounded-outdegree-hyper: every source has at most m-1 copies.
        bounded = n * (min(m - 1, math.comb(n - 1, 2)) if simple else m - 1)
        return max(layered, bounded)

    hyper_arc = lambda n: directed_hyper(n, True)
    multihyper_arc = lambda n: directed_hyper(n, False)

    def matrix(directed, simple, separation):
        return dict(directed=directed, simple=simple, separation=separation)

    def hyper(directed, simple, separation):
        kw = dict(hypergraph=True, r=3, directed=directed, separation=separation)
        if not simple:
            kw["simple"] = False  # preserve the legacy record's exact keys
        return kw

    # Each row: model, exhaustion stop (exclusive), exhaustion seconds,
    # discovery seconds, construction, theorem curve (or None).
    specs = [
        (matrix(False, True, "edge"), 9, exact_budget, search_budget, simple_edge, simple_edge),
        (matrix(False, True, "vertex"), 8, exact_budget,
         search_budget if m <= 4 else open_search_budget, simple_edge, simple_edge if m <= 4 else None),
        (matrix(True, True, "edge"), 7, 1800., search_budget, simple_arc, simple_arc if m == 2 else None),
        (matrix(True, True, "vertex"), 7, 1800., search_budget, simple_arc, simple_arc if m == 2 else None),
        (matrix(False, False, "edge"), 7, exact_budget, search_budget, multi_edge, multi_edge),
        (matrix(False, False, "vertex"), 7, 120., search_budget, multi_vertex, multi_vertex if m <= 3 else None),
        # The legacy dispatcher uses a theorem here, not independent enumeration.
        (matrix(True, False, "edge"), 2, 10., search_budget, multi_arc, multi_arc),
        (matrix(True, False, "vertex"), 6, 120., search_budget, multi_dir_vertex, multi_dir_vertex if m == 2 else None),
        (hyper(False, True, "edge"), 8, exact_budget, search_budget, hyper_edge, hyper_upper),
        (hyper(False, True, "vertex"), 7, exact_budget,
         search_budget if m <= 3 else open_search_budget, hyper_vertex, hyper_upper if m <= 3 else None),
        (hyper(True, True, "edge"), 6, exact_budget, open_search_budget, hyper_arc, None),
        (hyper(True, True, "vertex"), 6, exact_budget, open_search_budget, hyper_arc, None),
        (hyper(False, False, "edge"), 7, exact_budget, search_budget, multihyper_edge, multihyper_upper),
        (hyper(False, False, "vertex"), 6, exact_budget,
         search_budget if m <= 3 else open_search_budget, multihyper_vertex, multihyper_upper if m <= 3 else None),
        (hyper(True, False, "edge"), 5, exact_budget, open_search_budget, multihyper_arc, None),
        (hyper(True, False, "vertex"), 5, exact_budget, open_search_budget, multihyper_arc, None),
    ]
    panels = []
    for i, (kw, stop, exact_seconds, search_seconds, construction, theorem) in enumerate(specs):
        is_hyper = kw.get("hypergraph", False)
        first = 3 if is_hyper else 2
        ns = list(range(first, 13 if is_hyper else 17))
        exact = _exact_points(range(first, stop), m, exact_seconds, **kw)
        if i == 8:
            exact = _with_settled_cells(exact, m, 3, _SETTLED_HYPER_EDGE_SIMPLE)
        panel = dict(
            status="proved" if theorem else "open",
            ylabel=("hyperarcs" if kw["directed"] else "hyperedges") if is_hyper
                   else ("arcs" if kw["directed"] else "edges"),
            exact=exact, search=_search_points(ns, m, search_seconds, **kw),
            construction=(ns, [construction(n) for n in ns]),
            search_budget_seconds=search_seconds,
            search_keys=[MachineValues.key("search", n, m, search_seconds, kw) for n in ns])
        if theorem:
            panel["proved"] = (ns, [theorem(n) for n in ns])
            if is_hyper:
                panel["proved_is_bound"] = True
        panels.append(_reconcile_panel(panel))
    return panels


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
    bound is prefixed by $\\le$. Attainment may come from the separate
    ``construction`` series or a raw ``search`` witness. Neither series is
    overwritten by that comparison. Conjectured and open rows are prefixed by
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
    if key == "search":
        value = max(value, dict(zip(*panel.get("construction", ([], [])))).get(n, 0))
    color = _CURVE_COLOR[key]
    if key == "proved":
        prefix = ""
        if panel.get("proved_is_bound"):
            search_ns, search_vals = panel.get("search", ([], []))
            attained = max(dict(zip(search_ns, search_vals)).get(n, 0),
                           dict(zip(*panel.get("construction", ([], [])))).get(n, 0))
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



def search_evidence_tables() -> None:
    """Export historical raw search and construction values without blending them.

    Missing elapsed times and witnesses in the legacy record remain unknown.
    The derived file does not claim to be a new experiment.
    """
    records = []
    for m in (3, 6):
        panels = gather_variant_grid(m)
        for group, indices in (("graphs", range(8)), ("hypergraphs", range(8, 16))):
            ns = list(range(2 if group == "graphs" else 3, 9))
            lines = [r"\begin{tabular}{llr" + "r" * len(ns) + "}",
                     r"\toprule",
                     "Variant & Source & Limit (s) & " +
                     " & ".join(f"$n={n}$" for n in ns) + r" \\",
                     r"\midrule"]
            for i in indices:
                panel = panels[i]
                model, variant, _ = _VARIANT_ROW_META[i]
                label = model.replace(" $r=3$", "") + ", " + variant
                for source in ("search", "construction"):
                    values = dict(zip(*panel[source]))
                    limit = f'{panel["search_budget_seconds"]:g}' if source == "search" else "--"
                    lines.append(" & ".join(
                        [label if source == "search" else "", source, limit] +
                        [str(values[n]) if n in values else "--" for n in ns]) + r" \\")
                lines.append(r"\addlinespace[2pt]")
                search, construction, exact = (dict(zip(*panel[key]))
                                                for key in ("search", "construction", "exact"))
                for n in sorted(set(search) | set(construction)):
                    key = panel["search_keys"][panel["search"][0].index(n)]
                    run = MACHINE_VALUES.runs.get(key, {})
                    records.append(dict(
                        m=m, n=n, panel=i, model=model, variant=variant,
                        search_value=search.get(n), construction_value=construction.get(n),
                        enumeration_value=exact.get(n),
                        search_limit_seconds=panel["search_budget_seconds"],
                        search_method="randomised greedy" if i >= 8 else "tabu",
                        search_seed=0, search_elapsed_seconds=run.get("elapsed_seconds"),
                        search_witness=run.get("witness"), source_key=key,
                        provenance="machine_values.json run record" if run else
                                   "legacy machine_values.json; elapsed time and witness not saved"))
            lines += [r"\bottomrule", r"\end{tabular}"]
            (FIGURES / f"search_evidence_m{m}_{group}.tex").write_text("\n".join(lines) + "\n")
    _write_json(DATA / "search_evidence.json", dict(
        description="Derived comparison, not a rerun. Raw search is never lifted to a construction.",
        source_meta=MACHINE_VALUES.meta, records=records))


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
    search_evidence_tables()
    ns = _TABLE_NS
    groups = [(0, 8), (8, 16)]
    lines = [
        "% Generated by make_figures.py:variant_value_tables().",
        "% Colours: vtProved/vtConjectured/vtOpen match the curve in the",
        "% matching figure; vtExact (bold) is a machine-checked value.",
        "% Blank cells omit the degenerate zero-edge hypergraph case n=2.",
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


REDISCOVERY_CASES = [
    (r"simple undirected", 6, 2, False, True),
    (r"multi undirected", 6, 3, False, False),
    (r"simple directed", 4, 2, True, True),
    (r"simple directed", 6, 2, True, True),
    (r"simple directed", 7, 2, True, True),
    (r"multi directed", 4, 3, True, False),
    (r"multi directed", 5, 3, True, False),
]


def rediscovery_table():
    """Render the recorded unaided runs, with optima supplied only for comparison."""
    record = json.loads((DATA / "rediscovery.json").read_text())
    lines = [r"\begin{tabular}{lrrrrrr}", r"\toprule",
             r"Variant & $n$ & $m$ & Limit (s) & Elapsed (s) & Search & Optimum \\",
             r"\midrule"]
    for label, n, m, directed, simple in REDISCOVERY_CASES:
        suffix = f"|directed={directed}|separation=edge|simple={simple}"
        matches = [run for key, run in record["runs"].items()
                   if key.startswith(f"search|n={n}|m={m}|") and key.endswith(suffix)]
        if len(matches) != 1:
            raise ValueError(f"expected one rediscovery run for {label}, n={n}, m={m}")
        run, = matches
        optimum = (directed_arc_lower_bound(n, m) if simple else directed_multigraph_arc(n, m)) if directed else (
                   simple_undirected_edge(n, m) if simple else multigraph_undirected_edge(n, m))
        if run["value"] > optimum:
            raise ValueError("rediscovery exceeds a proved optimum")
        lines.append(" & ".join([label, str(n), str(m), f'{run["requested_seconds"]:g}',
                                f'{run["elapsed_seconds"]:.3f}', str(run["value"]), str(optimum)]) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (FIGURES / "rediscovery_table.tex").write_text("\n".join(lines) + "\n")


def main() -> None:
    """Render only assets used by the current thesis; never start a search."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    plot_directed_crossover(m=3, max_n=15, path=FIGURES / "directed_crossover.png")
    plot_edge_vertex_divergence(max_n=35, path=FIGURES / "edge_vertex_divergence.png")
    plot_complexity_growth(path=FIGURES / "complexity_growth.png")
    variant_grid_figures()
    variant_value_tables()
    rediscovery_table()


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

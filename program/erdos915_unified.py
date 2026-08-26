"""
erdos915_unified: the complete unified program for Erdos Problem 915, in one file.

This single module is the whole program, kept in one namespace so it can be read
top to bottom as a continuous story.  It is meant to be read, not just run: every
non-trivial step carries an inline comment explaining *why* it is there, not
merely what it does.  Running it (``python erdos915_unified.py``) executes the
invariant self-check at the foot of the file; ``make_figures.py`` next to it
regenerates the thesis figures.

----------------------------------------------------------------------------
The problem, in one breath
----------------------------------------------------------------------------
Erdos Problem 915 asks, in its many guises, for the densest graph on ``n``
vertices in which no pair of vertices has ``m`` independent routes between them.
"Independent" can mean edge-disjoint or internally vertex-disjoint; the object
can be a simple graph, a multigraph, a digraph, or a hypergraph; and forbidding
``m`` routes is exactly the constraint that the largest *local* connectivity
stays at or below ``m - 1``.  Twelve concrete variants fall out of these
choices, and this program treats all of them with one representation and one
search.

----------------------------------------------------------------------------
The epistemic spine: measure / prove / discover
----------------------------------------------------------------------------
The whole architecture is organised around three different *kinds of claim* a
program can make about extremal values, and it keeps them scrupulously apart so
they can never silently masquerade as one another:

  * MEASURE.  The checker computes exact local connectivities by max-flow
    (Menger's theorem).  Whatever it reports is a fact about a concrete graph,
    not an estimate.  This is the trusted core; everything else is checked
    against it.

  * PROVE.   Exhaustive enumeration proves upper bounds for a fixed number of
    vertices.  The historical cut-counting optimisation is retained as an
    independent finite solver check. It does not emit a replayable certificate.

  * DISCOVER. The random search finds concrete dense graphs, hence
    *lower* bounds.  A construction it returns is a witness that the extremal
    value is at least so large; it never proves that no denser graph exists.

The closed-form ``bounds`` library sits to the side as the theory's predictions
(proved, cited, or merely conjectured, each labelled honestly), so that "what
the program found" can always be held against "what the theory predicts" without
the two drifting apart.  The Monte Carlo module sits in the DISCOVER/observe
corner: a sampled estimate is an estimate, used to make a proved threshold
*visible*, never to prove it.

----------------------------------------------------------------------------
Chapter map (sections are grouped below by the thesis chapter they support)
----------------------------------------------------------------------------
  CHAPTER 1  The problem and its base cases
       VARIANT, BOUNDS, HYPERGRAPH, CONSTRUCTIONS
  CHAPTER 2  Proving bounds by machine
       CHECKER, GOMORY-HU, PROVE (the brute-force and exhaustive provers
       live inside the SOLVE driver, in Chapter 3)
  CHAPTER 3  Discovering bounds by search
       SENSITIVITY, SEARCH, SOLVE (the one driver: prove or discover)
  CHAPTER 4  Synthesis and results
       MONTE CARLO, FIGURES, __main__ (the invariant self-check suite)

A bold CHAPTER divider precedes each group, so as you scroll you always know
which chapter's machinery you are reading. Each section keeps its own banner.
"""

# ==================================================================
# Hoisted imports
# ------------------------------------------------------------------
# All external dependencies, gathered into a single block.  ``from __future__
# import annotations`` must be (and is) the very first statement so that
# string-form type hints work uniformly.  Everything in this program lives in one
# namespace, so there are no intra-module imports to follow.
# ==================================================================
from __future__ import annotations

import copy
import hashlib
import json
import math
import pickle
import random
import shutil
import statistics
import subprocess
import time
import warnings
from collections import Counter, deque
from collections.abc import Iterable
from dataclasses import dataclass, field
from itertools import combinations, combinations_with_replacement, permutations, product
from pathlib import Path
from typing import Callable, Iterator

import concurrent.futures

import numpy as np
from scipy.sparse import csr_matrix as _csr
from scipy.sparse.csgraph import maximum_flow as _csgraph_maxflow

# networkx is OPTIONAL.  Every connectivity measure the thesis reports is computed
# through scipy's integer max-flow on a capacity matrix, so the core checker,
# search, provers, and enumeration run on numpy + scipy alone.  networkx is needed
# only for the Gomory-Hu tree (one figure/analysis helper), which raises a clear
# message if called without it installed.
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    nx = None
    NETWORKX_AVAILABLE = False


def _require_networkx(feature: str):
    """Raise a clear error when an optional networkx-only feature is used headless."""
    if not NETWORKX_AVAILABLE:
        raise ImportError(
            f"{feature} needs networkx (pip install networkx). The core connectivity "
            f"measures do not: they run on numpy + scipy alone."
        )

# pulp is OPTIONAL.  It backs the MILP certifier (prove_directed_multigraph and
# prove_integral_arc_bound): one solver-agnostic cut-counting model that CBC (pulp's
# bundled solver) runs by default and Gurobi runs by a one-line switch.  The model,
# checker, search, enumeration, and sampling do not need it.
try:
    import pulp
    # pulp 3.x emits migration notices for its 4.0 API (LpVariable construction,
    # the PULP_CBC_CMD name).  We use the stable 3.x API on purpose and pin it in
    # requirements.txt, so silence that forward-looking noise.
    import warnings as _warnings
    _warnings.filterwarnings("ignore", message=r".*PuLP 4\.0.*",
                             category=DeprecationWarning)
    PULP_AVAILABLE = True
except ImportError:
    pulp = None
    PULP_AVAILABLE = False


def _require_pulp():
    """Raise a clear error when the MILP certifier is used without pulp installed."""
    if not PULP_AVAILABLE:
        raise ImportError(
            "the MILP certifier needs pulp (pip install pulp). The checker, search, "
            "and enumeration do not: they run on numpy + scipy alone."
        )

import ctypes as _ct
_C = None
_so_path = Path(__file__).with_name("_erdos_fast.so")
if _so_path.exists():
    _C = _ct.CDLL(str(_so_path))
    _C.tiny_maxflow.restype = _ct.c_int
    _C.tiny_maxflow.argtypes = [
        _ct.POINTER(_ct.c_int), _ct.c_int, _ct.c_int, _ct.c_int, _ct.c_int,
    ]
    _C.max_connectivity_exceeds.restype = _ct.c_int
    _C.max_connectivity_exceeds.argtypes = [
        _ct.POINTER(_ct.c_int), _ct.c_int, _ct.c_int, _ct.c_int,
    ]
    _C.canonical_form_min.restype = None
    _C.canonical_form_min.argtypes = [
        _ct.POINTER(_ct.c_int), _ct.c_int, _ct.POINTER(_ct.c_int),
    ]
C_EXTENSION_LOADED = _C is not None

# matplotlib is OPTIONAL: it is needed only to render the figures (the plot_*
# functions in the FIGURES section).  It needs its backend chosen before pyplot is
# imported, so that the figure code runs head-less (writes PNG files, never opens a
# window).  When it is absent the model, checker, provers, search, and enumeration
# all still run; only figure generation is unavailable.
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt  # noqa: E402  (after backend selection)
    from matplotlib.ticker import MaxNLocator  # noqa: E402  (integer-only axis ticks)
    from matplotlib.colors import PowerNorm  # noqa: E402
    from matplotlib.gridspec import GridSpec  # noqa: E402
    from matplotlib.patches import FancyArrowPatch, Patch  # noqa: E402
    import matplotlib.lines as mlines  # noqa: E402  (proxy artists for shared legends)
    from matplotlib.transforms import blended_transform_factory  # noqa: E402
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers the '3d' projection)
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    MaxNLocator = None
    PowerNorm = None
    GridSpec = None
    FancyArrowPatch = None
    Patch = None
    mlines = None
    blended_transform_factory = None
    MATPLOTLIB_AVAILABLE = False


######################################################################
##
##  CHAPTER 1 — THE PROBLEM AND ITS BASE CASES
##  Objects, variants, and the closed-form values we already know.
##
######################################################################

# --- VARIANT: mu[u,v] = multiplicity from u to v; simple = {0,1}; undirected = symmetric ---


@dataclass(frozen=True)
class Variant:
    """Which kind of graph object we are working with.

    Attributes:
        directed: ``True`` for digraphs (arcs), ``False`` for graphs (edges).
        simple: ``True`` caps every multiplicity at one. ``False`` allows
            arbitrarily many parallel edges or arcs (a multigraph).
        name: a short human-readable label, used in figures and reports.
    """

    directed: bool
    simple: bool
    #loops: bool 
    name: str = ""

    def describe(self) -> str:
        """Return a readable description such as ``"simple directed"``."""
        # Compose the label from the two boolean axes; used in plot titles.
        words = ["simple" if self.simple else "multi",
                 "directed" if self.directed else "undirected"]
        return " ".join(words)


# The four matrix-representable variants, named for convenience.  Random graphs
# reuse these (a sampled simple undirected graph is SIMPLE_UNDIRECTED).
SIMPLE_UNDIRECTED = Variant(directed=False, simple=True, name="simple undirected")
MULTI_UNDIRECTED = Variant(directed=False, simple=False, name="multi undirected")
SIMPLE_DIRECTED = Variant(directed=True, simple=True, name="simple directed")
MULTI_DIRECTED = Variant(directed=True, simple=False, name="multi directed")


class Graph:
    """A graph or digraph stored as an integer multiplicity matrix.

    The single source of truth is ``self.mu``, an ``n by n`` array of
    non-negative integers with a zero diagonal (no self-loops).  For an
    undirected variant the matrix is kept symmetric at all times, so the
    invariant ``mu[u, v] == mu[v, u]`` may be relied upon everywhere.

    All mutating methods respect the variant: they keep an undirected graph
    symmetric and never let a simple graph exceed multiplicity one.
    """

    def __init__(self, num_vertices: int, variant: Variant):
        if num_vertices < 0:
            raise ValueError("number of vertices must be non-negative")
        self.variant = variant
        # The whole graph is this one matrix; integer dtype keeps it exact.
        self.mu = np.zeros((num_vertices, num_vertices), dtype=int)

    # -- basic queries -------------------------------------------------------

    @property
    def num_vertices(self) -> int:
        """The number of vertices ``n``."""
        return self.mu.shape[0]

    def vertices(self) -> range:
        """The vertex set ``{0, 1, ..., n - 1}`` as a range."""
        return range(self.num_vertices)

    def multiplicity(self, u: int, v: int) -> int:
        """Number of parallel edges or arcs from ``u`` to ``v``."""
        return int(self.mu[u, v])

    def has_edge(self, u: int, v: int) -> bool:
        """Whether at least one edge or arc joins ``u`` to ``v``."""
        return self.mu[u, v] > 0

    def edge_count(self) -> int:
        """Total number of edges or arcs, counted with multiplicity.

        For an undirected graph each edge is stored twice in the matrix, so we
        count the strict upper triangle. For a digraph every ordered pair
        counts once.
        """
        if self.variant.directed:
            return int(self.mu.sum())
        # Strict upper triangle (k=1) avoids double-counting the symmetric pair.
        return int(np.triu(self.mu, k=1).sum())

    def out_degree(self, v: int) -> int:
        """Number of edges or arcs leaving ``v`` (with multiplicity)."""
        return int(self.mu[v, :].sum())

    def in_degree(self, v: int) -> int:
        """Number of edges or arcs entering ``v`` (with multiplicity)."""
        return int(self.mu[:, v].sum())

    def degree(self, v: int) -> int:
        """Total degree of ``v``.

        For a digraph this is the sum of in- and out-degree. For an undirected
        graph in- and out-degree coincide, so we report the out-degree.
        """
        if self.variant.directed:
            return self.out_degree(v) + self.in_degree(v)
        return self.out_degree(v)

    def edges(self) -> Iterator[tuple[int, int, int]]:
        """Yield ``(u, v, multiplicity)`` for every present edge or arc.

        For an undirected graph each edge is yielded once, with ``u < v``.
        """
        n = self.num_vertices
        for u in range(n):
            # Undirected: only scan v > u so each edge is emitted once.
            # Directed: scan all v so both arc directions are emitted.
            start = u + 1 if not self.variant.directed else 0
            for v in range(start, n):
                if u != v and self.mu[u, v] > 0:
                    yield u, v, int(self.mu[u, v])

    # -- mutation ------------------------------------------------------------

    def add_edge(self, u: int, v: int, count: int = 1) -> None:
        """Add ``count`` parallel edges or arcs from ``u`` to ``v``.

        A simple graph silently saturates at multiplicity one. An undirected
        graph updates both matrix entries to stay symmetric.
        """
        self._require_distinct(u, v)
        if count < 0:
            raise ValueError("edge count must be non-negative")
        new_value = self.mu[u, v] + count
        if self.variant.simple:
            new_value = min(new_value, 1)  # enforce the 0/1 simple-graph cap
        self._assign(u, v, new_value)

    def remove_edge(self, u: int, v: int, count: int = 1) -> None:
        """Remove ``count`` parallel edges or arcs (never below zero)."""
        self._require_distinct(u, v)
        if count < 0:
            raise ValueError("edge count must be non-negative")
        new_value = max(0, self.mu[u, v] - count)
        self._assign(u, v, new_value)

    def set_multiplicity(self, u: int, v: int, value: int) -> None:
        """Set the multiplicity from ``u`` to ``v`` directly."""
        self._require_distinct(u, v)
        if value < 0:
            raise ValueError("multiplicity must be non-negative")
        if self.variant.simple and value > 1:
            raise ValueError("a simple graph cannot have multiplicity above one")
        self._assign(u, v, value)

    def copy(self) -> "Graph":
        """Return an independent copy with the same variant and edges."""
        clone = Graph(self.num_vertices, self.variant)
        clone.mu = self.mu.copy()  # deep-copy the matrix so edits don't alias
        return clone

    # -- internal helpers ----------------------------------------------------

    def _assign(self, u: int, v: int, value: int) -> None:
        """Write ``value`` into the matrix, mirroring it when undirected."""
        if value < 0:
            raise ValueError("multiplicity must be non-negative")
        if self.variant.simple and value > 1:
            raise ValueError("a simple graph cannot have multiplicity above one")
        self.mu[u, v] = value
        # Maintain the symmetry invariant for undirected graphs in one place.
        if not self.variant.directed:
            self.mu[v, u] = value

    def _require_distinct(self, u: int, v: int) -> None:
        if u == v:
            raise ValueError("self-loops are not allowed in this model")

    def __repr__(self) -> str:
        return (f"Graph(n={self.num_vertices}, variant={self.variant.describe()!r}, "
                f"edges={self.edge_count()})")


# --- BOUNDS: closed-form extremal values; docstrings record proved/conjectured status ---


def simple_undirected_edge(n: int, m: int) -> int:
    """Mader's value, capped by the complete graph when ``n < m``."""
    return min((m * (n - 1)) // 2, n * (n - 1) // 2)


def multigraph_undirected_edge(n: int, m: int) -> int:
    """``L_m(n) = (m-1)(n-1)``.  Proved (multi-tree construction and bound)."""
    return (m - 1) * (n - 1)


def simple_undirected_vertex_le4(n: int, m: int) -> int:
    """``k_m(n) = floor(m (n-1) / 2)`` for ``m <= 4``.  Cited (Leonard, 1972)."""
    if m > 4:
        raise ValueError("this equality is only known for m <= 4")
    # For m <= 4 the vertex problem coincides with the edge problem.
    return simple_undirected_edge(n, m)


def simple_undirected_vertex_m5(n: int) -> int:
    """``k_5(n) = floor(8n/3) - 4`` for ``n >= 6``, ``n != 7``, ``n != 12``.

    Cited (Sorensen-Thomassen, Theorem 4).  Their paper counts the least edge
    total that FORCES a 5-rail and prints ``floor(8n/3) - 3``; this thesis
    counts the largest that avoids one, which is exactly one less.  The two
    sizes the closed form misses are given there separately, and below n = 6
    the formula is not claimed at all.
    """
    if n < 6:
        raise ValueError("k_5(n) is only determined for n >= 6")
    if n == 7:
        return 15
    if n == 12:
        return 27
    return (8 * n) // 3 - 4


def directed_arc_m2(n: int) -> int:
    """``ell_2^dir(n) = max(2(n-1), floor(n^2/4))``.  Proved (induction on n)."""
    # The max picks whichever of the two competing constructions wins at this n:
    # the linear hub (double star) versus the quadratic one-directional wall.
    return max(2 * (n - 1), (n * n) // 4)


def directed_arc_lower_bound(n: int, m: int) -> int:
    """Lower bound and conjectured value for ``ell_m^dir(n)``, ``m >= 2``.

    ``max(m(n-1), floor((n+m-2)^2/4))``.  The two branches are the hub
    construction (``const:directed-hub``) and the shifted-partition augmented
    bipartite construction (``const:augmented-bipartite``).  Proved as a lower
    bound for all ``m`` after capping at the complete digraph. It is conjectured to be tight for ``m >= 3``
    (``conj:dir-arc``), proved tight for ``m = 2``.
    """
    hub_branch = m * (n - 1)
    bipartite_branch = (n + m - 2) ** 2 // 4
    return min(max(hub_branch, bipartite_branch), n * (n - 1))


def hypergraph_edge(n: int, m: int, r: int) -> int:
    """``floor((m-1)(n-1)/(r-1))`` hyperedges for the ``r``-uniform edge problem.

    Proved as an upper bound for every ``r``-uniform hypergraph, simple or
    not (``prop:hyper-edge``, hypergraph Gomory-Hu). Attained by a
    MULTIhypergraph (a repeated-hyperedge star) whenever ``(r-1) | (n-1)``.
    Attained by a SIMPLE hypergraph, the model this program's sixteen-panel
    enumeration actually searches, only under the extra hypothesis
    ``m - 1 <= C(n-2, r-2)`` (``thm:simple-hyper-edge``). Outside both
    conditions this value is still a valid upper bound but is not known to
    be attained by any hypergraph the program can build; use
    ``_hyper_edge_simple_proved`` for the gated version figures should read.
    """
    return ((m - 1) * (n - 1)) // (r - 1)


def _hyper_edge_simple_proved(n: int, m: int, r: int) -> int | None:
    """``hypergraph_edge(n, m, r)``, gated to where a SIMPLE hypergraph is
    proved to attain it (``thm:simple-hyper-edge``: ``m - 1 <= C(n-2, r-2)``).

    Returns ``None`` outside that range. The sixteen-variant program's hyper
    rows enumerate simple hypergraphs (no repeated hyperedges), and outside
    this condition the closed form is only an unattained upper bound for
    that model, e.g. at ``n = r = m = 3`` it gives 2 while only one 3-set
    exists on 3 vertices, so the simple maximum is 1.
    """
    if r < 2 or n < r:
        return None
    if m - 1 <= math.comb(n - 2, r - 2):
        return hypergraph_edge(n, m, r)
    return None


def _hyper_vertex_simple_proved(n: int, m: int, r: int) -> int | None:
    """The vertex-separation analogue of ``_hyper_edge_simple_proved``.

    ``m = 2``: unconditional (``thm:hyper-vertex-m2``: repeated hyperedges
    never help at ``kappa^max <= 1``, so the star hypertree, itself simple,
    attains the bound for every ``n``, ``r``).
    ``m = 3``: proved for simple hypergraphs only when
    ``2 <= C(n-2, r-2)`` (``thm:hyper-vertex-m3``, ``rem:hyper-vertex-m3-scope``).
    ``m >= 4``: open (``rem:hyper-vertex-m3-scope``).
    """
    if r < 2 or n < r:
        return None
    if m == 2:
        return (n - 1) // (r - 1)
    if m == 3 and math.comb(n - 2, r - 2) >= 2:
        return (2 * (n - 1)) // (r - 1)
    return None


def directed_multigraph_arc(n: int, m: int) -> int:
    """``L_m^dir(n) = (m-1) max(2(n-1), floor(n^2/4))``.  Proved, all n and m.

    The double star dominates the one-directional bipartite branch up to the
    crossover at ``n = 7``, where the two tie; past it the quadratic branch
    takes over.  Proved outright by ``thm:dir-multi-full`` (peel one sparse
    reachability-preserving subgraph per unit of ``m-1``), which superseded the
    earlier route that was certified only for ``n <= 6`` by counting cuts.
    """
    double_star_branch = 2 * (n - 1) * (m - 1)
    bipartite_branch = (m - 1) * ((n * n) // 4)
    return max(double_star_branch, bipartite_branch)


# --- HYPERGRAPH: stored as incidence list; Berge-path connectivity via helper-node max-flow ---


class Hypergraph:
    """A hypergraph stored by its incidence (a list of hyperedges).

    An undirected hyperedge is a set of vertices, crossed in either direction.  A
    directed hyperedge (``directed=True``) splits an ``r``-set into a non-empty
    tail set ``T`` and a non-empty head set ``H``: a Berge route may enter it only
    at a tail and leave only at a head.  Two storage forms are accepted, and the
    checker treats them identically:

    * the legacy *forward* form ``(tail, frozenset(heads))`` with a single integer
      tail and ``r - 1`` heads (``|T| = 1``), the one-tail / many-head model the
      rest of the thesis uses; and
    * the *general* form ``(frozenset(tails), frozenset(heads))`` for any split,
      which subsumes forward (``|T| = 1``), backward (``|H| = 1``) and, from
      ``r >= 4``, genuinely mixed (``|T|, |H| >= 2``) hyperarcs.

    For ``r = 2`` every form collapses to a single arc, so a directed graph is the
    two-vertex special case.
    """

    def __init__(self, num_vertices: int, hyperedges: Iterable = (),
                 *, directed: bool = False, r: int | None = None):
        """``r`` states the uniformity and is ENFORCED when given.

        It defaults to None, meaning unenforced, because the container itself is
        general: it only requires each hyperedge to span at least two vertices,
        and it will hold edges of mixed sizes without complaint.  Every generator
        in this program emits uniform hyperedges, so the searches and enumerations
        are uniform as a matter of how they are built rather than of what the
        container permits.  Pass ``r`` wherever a caller depends on that and wants
        it checked rather than assumed.
        """
        self.num_vertices = num_vertices
        self.directed = directed
        self.r = r
        # Each entry is a frozenset, or a ``(tail, frozenset(heads))`` pair.
        self.hyperedges: list = []
        for edge in hyperedges:
            self.add_hyperedge(edge)

    def add_hyperedge(self, edge) -> None:
        """Add an undirected vertex set, or a directed ``(tail, heads)`` pair.

        A directed edge may be the forward form ``(tail:int, heads)`` or the
        general form ``(tails:frozenset, heads:frozenset)``; the general form is
        kept verbatim, the forward form is kept verbatim too (no normalisation),
        so existing forward results are unchanged byte-for-byte.
        """
        if self.directed:
            first, raw_heads = edge
            if isinstance(first, (set, frozenset)):     # general (tails, heads)
                tails, heads = frozenset(first), frozenset(raw_heads)
                members = tails | heads
                if (tails & heads) or not tails or not heads or len(members) < 2:
                    raise ValueError("a directed hyperedge needs disjoint, non-empty tail and head sets")
                if any(v < 0 or v >= self.num_vertices for v in members):
                    raise ValueError("hyperedge refers to a vertex outside the graph")
                self._check_uniform(members)
                self.hyperedges.append((tails, heads))
                return
            tail, heads = first, frozenset(raw_heads)    # legacy forward (tail, heads)
            members = heads | {tail}
            if tail in heads or len(members) < 2:
                raise ValueError("a directed hyperedge needs a tail and a distinct head")
            if any(v < 0 or v >= self.num_vertices for v in members):
                raise ValueError("hyperedge refers to a vertex outside the graph")
            self._check_uniform(members)
            self.hyperedges.append((tail, heads))
        else:
            vertices = frozenset(edge)  # a hyperedge is a set of distinct vertices
            if len(vertices) < 2:
                raise ValueError("a hyperedge must contain at least two vertices")
            if any(v < 0 or v >= self.num_vertices for v in vertices):
                raise ValueError("hyperedge refers to a vertex outside the graph")
            self._check_uniform(vertices)
            self.hyperedges.append(vertices)

    def _check_uniform(self, members) -> None:
        """Reject a hyperedge of the wrong size, when a uniformity was declared."""
        if self.r is not None and len(members) != self.r:
            raise ValueError(
                f"this hypergraph was declared {self.r}-uniform, but the "
                f"hyperedge spans {len(members)} vertices")

    def members(self, edge) -> frozenset:
        """The vertex set of a stored hyperedge, directed or not."""
        if self.directed:
            tails, heads = _dir_tails_heads(edge)
            return tails | heads
        return edge

    def vertices(self) -> range:
        return range(self.num_vertices)

    def edge_count(self) -> int:
        """Number of hyperedges."""
        return len(self.hyperedges)

    def incident_hyperedges(self, v: int) -> list[int]:
        """Indices of the hyperedges containing vertex ``v``."""
        return [i for i, edge in enumerate(self.hyperedges) if v in self.members(edge)]


def _dir_tails_heads(edge) -> tuple[frozenset, frozenset]:
    """Tail and head sets of a stored directed hyperedge, as frozensets.

    Accepts the legacy forward form ``(tail:int, heads)`` and the general form
    ``(tails:frozenset, heads:frozenset)``, so every consumer of a directed
    hyperedge can read one ``(tails, heads)`` shape regardless of how it was
    built.
    """
    first, heads = edge
    if isinstance(first, (set, frozenset)):
        return frozenset(first), frozenset(heads)
    return frozenset((first,)), frozenset(heads)


def _hyper_capacity_matrix(hypergraph: Hypergraph, *, vertex_split: bool = False):
    """Integer capacity matrix of the hypergraph flow network (one per variant).

    Each hyperedge becomes an in/out gate joined by a capacity-1 arc, so at most
    one disjoint Berge route may traverse it: this is the hyperedge-as-node trick.
    With ``vertex_split`` each ORIGINAL vertex is *also* split into an in/out pair
    of capacity one, so the flow counts internally vertex-disjoint Berge routes
    instead of edge-disjoint ones.  For a directed hypergraph the gate is entered
    only from a tail and left only toward a head (one tail for the forward model,
    several for the general one); for an undirected one every member links to the
    gate both ways.  The hypergraph variants are thus the same construction with a
    boolean or two flipped, not separate measures.

    Vertices index ``0..base-1`` (``base = 2n`` split, else ``n``); hyperedge gate
    ``i`` indexes ``base+2i`` (in) and ``base+2i+1`` (out).  ``leave(v)``/``enter(v)``
    return the index a route leaves/enters vertex ``v`` through, so the same scipy
    max-flow that serves plain graphs serves hypergraphs too.
    """
    n = hypergraph.num_vertices
    base = 2 * n if vertex_split else n
    size = base + 2 * len(hypergraph.hyperedges)
    cap = np.zeros((size, size), dtype=int)
    leave = (lambda v: 2 * v + 1) if vertex_split else (lambda v: v)
    enter = (lambda v: 2 * v) if vertex_split else (lambda v: v)
    if vertex_split:
        for v in range(n):
            cap[2 * v, 2 * v + 1] = 1            # one route through each vertex
    for index, edge in enumerate(hypergraph.hyperedges):
        gate_in, gate_out = base + 2 * index, base + 2 * index + 1
        cap[gate_in, gate_out] = 1               # one route through each hyperedge
        if hypergraph.directed:
            tails, heads = _dir_tails_heads(edge)
            for tail in tails:                   # enter the gate from any tail
                cap[leave(tail), gate_in] = _UNBOUNDED
            for head in heads:                   # leave the gate toward any head
                cap[gate_out, enter(head)] = _UNBOUNDED
        else:
            for vertex in edge:
                cap[leave(vertex), gate_in] = _UNBOUNDED
                cap[gate_out, enter(vertex)] = _UNBOUNDED
    return cap, size, leave, enter


def hyper_connectivity(hypergraph: Hypergraph, source: int, target: int,
                       *, vertex_split: bool = False) -> int:
    """Edge- or vertex-disjoint Berge routes from ``source`` to ``target``.

    A single scipy integer max-flow on the matrix above.  An isolated endpoint
    (in no hyperedge) has no incident arcs, so the flow is then zero.
    """
    cap, _, leave, enter = _hyper_capacity_matrix(hypergraph, vertex_split=vertex_split)
    if vertex_split:
        # Endpoints must not be the bottleneck: only interior vertices are capped.
        cap[2 * source, 2 * source + 1] = _UNBOUNDED
        cap[2 * target, 2 * target + 1] = _UNBOUNDED
    return int(_csgraph_maxflow(_csr(cap, dtype=int), leave(source), enter(target)).flow_value)


def max_hyper_connectivity(hypergraph: Hypergraph, *, vertex_split: bool = False) -> int:
    """``lambda^max`` (edge) or ``kappa^max`` (vertex) over all pairs."""
    return max((hyper_connectivity(hypergraph, source, target, vertex_split=vertex_split)
                for source, target in _pairs(hypergraph)), default=0)


def hyperedge_connectivity(hypergraph: Hypergraph, source: int, target: int) -> int:
    """Maximum number of edge-disjoint Berge ``source``-``target`` paths."""
    return hyper_connectivity(hypergraph, source, target, vertex_split=False)


def max_hyperedge_connectivity(hypergraph: Hypergraph) -> int:
    """``lambda^max`` for the undirected edge hypergraph problem."""
    return max_hyper_connectivity(hypergraph, vertex_split=False)


# --- CONSTRUCTIONS: named extremal graphs; each states its edge count and lambda^max ---


def double_star(n: int, m: int, directed: bool = True) -> Graph:
    """The double star: one hub joined to every leaf with multiplicity ``m-1``.

    For a digraph the hub carries ``m-1`` arcs in *both* directions to each
    leaf, attaining ``2(n-1)(m-1)`` arcs with ``lambda^max = m-1``.  For an
    undirected multigraph it attains ``(m-1)(n-1)`` edges.  This is the
    small-``n`` extremiser of the multigraph problems.
    """
    variant = MULTI_DIRECTED if directed else MULTI_UNDIRECTED
    graph = Graph(n, variant)
    hub = 0  # vertex 0 is the central hub; everything else is a leaf
    for leaf in range(1, n):
        graph.set_multiplicity(hub, leaf, m - 1)
        if directed:
            graph.set_multiplicity(leaf, hub, m - 1)  # arcs in both directions
    return graph


def one_directional_bipartite(n: int) -> Graph:
    """All arcs from one part to the other: ``floor(n^2/4)`` arcs, ``lambda^max = 1``.

    The vertices split into a smaller part ``A`` and a larger part ``B`` and
    every arc runs ``A -> B``.  No two vertices have two arc-disjoint routes, so
    this single-direction wall of arcs is feasible for ``m = 2`` while holding
    quadratically many arcs: the phenomenon that has no undirected analogue.
    """
    graph = Graph(n, SIMPLE_DIRECTED)
    size_a = n // 2  # smaller part; the n^2/4 maximum is at the balanced split
    part_a = range(size_a)
    part_b = range(size_a, n)
    for a in part_a:
        for b in part_b:
            graph.add_edge(a, b)  # every arc runs A -> B only (one direction)
    return graph


def thickened_one_directional_bipartite(n: int, m: int) -> Graph:
    """The balanced one-way wall with every arc repeated ``m-1`` times."""
    if m < 2:
        raise ValueError("thickened wall needs m >= 2")
    graph = Graph(n, MULTI_DIRECTED)
    wall = one_directional_bipartite(n)
    for u, v, _ in wall.edges():
        graph.set_multiplicity(u, v, m - 1)
    return graph


def directed_hub(n: int, m: int) -> Graph:
    """The simple directed hub with ``m(n-1)`` arcs, defined for ``n >= m``."""
    if n < m:
        raise ValueError("directed_hub needs n >= m")
    graph = Graph(n, SIMPLE_DIRECTED)
    hub = 0
    spokes = n - 1
    for v in range(1, n):
        graph.add_edge(hub, v)
        graph.add_edge(v, hub)
    for offset in range(1, m - 1):
        for i in range(spokes):
            graph.add_edge(1 + i, 1 + (i + offset) % spokes)
    return graph


def augmented_bipartite(n: int, m: int) -> Graph:
    """The conjectured directed extremiser for ``m >= 2``.

    Set ``|B| = ceil((n+m-2)/2)`` and ``|A| = n - |B|``.  Fill every arc
    ``A -> B`` (the one-directional wall), then give each ``B``-vertex
    ``m - 2`` extra in-arcs from its circulant predecessors inside ``B``.
    Because no arc leaves ``B`` toward ``A``, a route between two ``B``
    vertices never escapes ``B``, and a route from ``A`` to ``b`` uses the
    direct arc plus one short detour through each of ``b``'s ``m - 2``
    in-arcs, giving ``lambda^max = m - 1``.  The arc count is
    ``floor((n+m-2)^2/4)`` (``const:augmented-bipartite`` in the thesis).

    Requires ``n >= m`` so that ``|A| >= 1`` and the circulant offsets stay
    distinct.  At ``m = 2`` the partition is balanced.  At ``m = 3`` the
    selected split is balanced for odd ``n`` and shifted by one vertex for even
    ``n``; the balanced and shifted choices have the same count
    ``floor(n^2/4) + ceil(n/2)``.  From ``m = 4`` the shifted partition can
    improve the count.  For ``m = 3, n = 10`` either split gives the 30-arc
    counterexample.
    """
    size_b = (n + m - 2 + 1) // 2   # ceil((n+m-2)/2)
    size_a = n - size_b
    if size_a < 1:
        raise ValueError("augmented_bipartite needs n >= m")

    graph = Graph(n, SIMPLE_DIRECTED)
    part_a = range(size_a)
    part_b = list(range(size_a, n))

    # Complete wall of arcs from the small part to the large part.
    for a in part_a:
        for b in part_b:
            graph.add_edge(a, b)

    # Thicken B by a circulant giving every B-vertex in-degree exactly m - 2.
    # Each offset adds a full cycle of arcs within B; m - 2 offsets give each
    # B-vertex m - 2 extra in-arcs from other B-vertices (the short detours).
    for offset in range(1, m - 1):
        for i in range(size_b):
            source = part_b[i]
            target = part_b[(i + offset) % size_b]
            graph.add_edge(source, target)
    return graph


def clique_tree(clique_size: int, blocks_added: int) -> Graph:
    """A tree of cliques (a ``k``-tree): the chordal scaffold of the vertex case.

    Begin with a complete graph ``K_r`` on ``r = clique_size`` vertices, then
    repeatedly attach a new vertex to the previous ``r - 1`` vertices, which
    always form a clique.  The result is a maximal chordal graph of treewidth
    ``r - 1`` and *global* vertex connectivity ``r - 1``.

    A caution that the thesis makes explicit: the controlled quantity here is the
    global connectivity, not ``kappa^max``.  Attaching a vertex to a triangle
    raises the local connectivity of that triangle's vertices above ``r - 1``, so
    a ``k``-tree is not itself feasible for the ``kappa^max`` problem.  It appears
    in the thesis to illustrate the chordal structure underlying the
    Sorensen-Thomassen analysis of the ``m = 5`` divergence, not as a feasible
    extremiser.
    """
    if clique_size < 2:
        raise ValueError("clique_size must be at least two")
    n = clique_size + blocks_added
    graph = Graph(n, SIMPLE_UNDIRECTED)

    # The seed clique on the first r vertices.
    for u in range(clique_size):
        for v in range(u + 1, clique_size):
            graph.add_edge(u, v)

    # Each new vertex joins the r - 1 most recently added vertices.
    # Those r - 1 always form a clique, which keeps the graph chordal (a k-tree).
    for new_vertex in range(clique_size, n):
        attach_to = range(new_vertex - (clique_size - 1), new_vertex)
        for old_vertex in attach_to:
            graph.add_edge(new_vertex, old_vertex)
    return graph


def complete_uniform_hypergraph(n: int, r: int) -> Hypergraph:
    """The complete ``r``-uniform hypergraph: every ``r``-subset is a hyperedge.

    It is dense and highly connected; for example $K_4^{(3)}$ has Berge
    edge-connectivity three between every pair, exceeding the two-hyperedge count
    of the pairs because longer Berge routes also contribute.
    """
    # One hyperedge per r-subset of the vertex set.
    return Hypergraph(n, (set(subset) for subset in combinations(range(n), r)))


def star_hypertree(n: int, r: int) -> Hypergraph:
    """A hub joined to disjoint blocks: the feasible extremiser at ``m = 2``.

    Vertex ``0`` is the hub, and the remaining ``n - 1`` vertices are split into
    blocks of size ``r - 1``; each block together with the hub forms one
    hyperedge.  No two vertices share more than one hyperedge and the only routes
    between blocks pass through the single hub, so the Berge edge-connectivity is
    one everywhere, and the construction holds $\\lfloor (n-1)/(r-1)\\rfloor$
    hyperedges, the ``m = 2`` case of the hypergraph edge bound.
    """
    if r < 2:
        raise ValueError("hyperedge size r must be at least two")
    hub = 0
    others = list(range(1, n))
    hypergraph = Hypergraph(n)
    # Walk the non-hub vertices in blocks of r - 1; each block plus the hub is
    # one hyperedge (a "star" of r-sets all sharing the single hub).
    for start in range(0, len(others) - (r - 2), r - 1):
        block = others[start:start + (r - 1)]
        if len(block) == r - 1:  # drop a trailing partial block
            hypergraph.add_hyperedge([hub, *block])
    return hypergraph


######################################################################
##
##  CHAPTER 2 — PROVING BOUNDS BY MACHINE
##  Measure connectivity exactly, then prove small-case upper bounds.
##
######################################################################

# --- CHECKER: exact max-flow connectivity; vertex_split=True gives kappa^max ---

# A capacity large enough to never be the bottleneck of any cut we build.
_UNBOUNDED = 10 ** 9


# ------------------------------------------------------------------
# One flow network and one measure, parameterised by edge vs vertex
# ------------------------------------------------------------------
# Every measure here is a single scipy integer max-flow on a capacity matrix
# (Menger).  EDGE mode runs directly on the multiplicity matrix mu: each unit of
# capacity is one parallel edge, so a max-flow of value f is f edge-disjoint
# routes.  VERTEX mode runs on the 2n x 2n split matrix (see _split_capacity_matrix)
# where each vertex becomes a capacity-one in/out gate, so a route uses a vertex at
# most once.  Edge vs vertex is one boolean, not a second code path.

def local_connectivity(graph: Graph, source: int, target: int,
                       *, vertex_split: bool = False) -> int:
    """Disjoint ``source``-``target`` routes by a single max-flow (Menger).

    Edge-disjoint with ``vertex_split=False``; internally vertex-disjoint with
    ``vertex_split=True``.  An isolated endpoint yields zero (no augmenting path).
    """
    if not vertex_split:
        # scipy.sparse.csgraph.maximum_flow is a C implementation; faster than
        # NetworkX for the small integer capacity matrices we use.
        return int(_csgraph_maxflow(_csr(graph.mu, dtype=int), source, target).flow_value)
    # Vertex mode: the same scipy max-flow on the split matrix.  Uncapping the two
    # endpoints' own in->out gates makes Menger count internally vertex-disjoint
    # routes (only interior vertices stay capacity-capped at one).
    cap, _ = _split_capacity_matrix(graph)
    cap[2 * source, 2 * source + 1] = _UNBOUNDED
    cap[2 * target, 2 * target + 1] = _UNBOUNDED
    return int(_csgraph_maxflow(_csr(cap, dtype=int), 2 * source + 1, 2 * target).flow_value)


def max_connectivity(graph: Graph, *, vertex_split: bool = False) -> int:
    """The largest local connectivity over all pairs: ``lambda^max`` (edge) or
    ``kappa^max`` (vertex).  For a digraph every ordered pair is examined, for an
    undirected graph each unordered pair once.
    """
    if not vertex_split:
        # Build the CSR matrix once and reuse it for every pair.
        csr = _csr(graph.mu, dtype=int)
        return max((int(_csgraph_maxflow(csr, s, t).flow_value)
                    for s, t in _pairs(graph)), default=0)
    return max((local_connectivity(graph, s, t, vertex_split=True)
                for s, t in _pairs(graph)), default=0)


# ------------------------------------------------------------------
# Named measures: thin views on the single path above (so the rest of the
# program can pass ``max_edge_connectivity`` / ``max_vertex_connectivity`` around
# by name -- just as ``hyperedge_connectivity`` names one branch of
# ``hyper_connectivity`` in the hypergraph section).
# ------------------------------------------------------------------

def local_edge_connectivity(graph: Graph, source: int, target: int) -> int:
    """Maximum number of edge-disjoint ``source``-``target`` paths."""
    return local_connectivity(graph, source, target, vertex_split=False)


def max_edge_connectivity(graph: Graph) -> int:
    """``lambda^max(G)``: the largest local edge-connectivity over all pairs."""
    return max_connectivity(graph, vertex_split=False)


def local_vertex_connectivity(graph: Graph, source: int, target: int) -> int:
    """Maximum number of internally vertex-disjoint ``source``-``target`` paths."""
    return local_connectivity(graph, source, target, vertex_split=True)


def max_vertex_connectivity(graph: Graph) -> int:
    """``kappa^max(G)``: the largest local vertex-connectivity over all pairs."""
    return max_connectivity(graph, vertex_split=True)


def min_vertex_connectivity(graph: Graph) -> int:
    """The global vertex connectivity ``kappa(G)``: the smallest over all pairs.

    This is the classical connectivity of a graph (the least number of vertices
    whose removal disconnects it).  It is distinct from ``kappa^max``: a ``k``-tree,
    for instance, is globally ``k``-connected yet has pairs with higher local
    connectivity.
    """
    pairs = list(_pairs(graph))
    if not pairs:
        return 0
    # Global connectivity is the MINIMUM local connectivity over all pairs.
    return min(local_vertex_connectivity(graph, source, target)
               for source, target in pairs)


# ------------------------------------------------------------------
# Shared helpers
# ------------------------------------------------------------------

def _pairs(obj):
    """Yield the vertex pairs to test: ordered if directed, unordered if not.

    Works for both a ``Graph`` (directedness on ``variant``) and a ``Hypergraph``
    (directedness on the object), so one pair sweep serves every variant.
    """
    directed = obj.directed if hasattr(obj, "directed") else obj.variant.directed
    n = obj.num_vertices
    for source in range(n):
        # Directed objects need both (s, t) and (t, s); undirected need each
        # unordered pair once, so we start the inner loop above the source.
        start = 0 if directed else source + 1
        for target in range(start, n):
            if source != target:
                yield source, target


# ------------------------------------------------------------------
# Capped feasibility predicate (used inside the search, Section 7)
# ------------------------------------------------------------------
# The exact measures above answer "what is lambda^max / kappa^max?".  The search
# only ever needs the cheaper YES/NO question "is it greater than k?", because
# its energy depends on the value solely through the excess max(0, value-(m-1)).
# A capped flow answers exactly that and stops the moment the answer is known, so
# this predicate is equivalent to ``max_connectivity(graph, ...) > k`` but usually
# far cheaper: each pair's flow halts after k+1 augmenting paths, and the pair
# loop halts at the first violating pair.  The exact value is recomputed only on
# the rare step where the search genuinely needs it (an infeasible proposal).
# DEPENDENCIES: _pairs (above), _tiny_maxflow (Section ENUMERATE), _UNBOUNDED.

def _split_capacity_matrix(graph: Graph,
                           parallel_routes: bool = False) -> tuple[np.ndarray, int]:
    """The ``2n x 2n`` capacity matrix of the vertex-split network.

    The vertex-mode network as a plain matrix, consumed by both the exact measure
    (:func:`local_connectivity` via scipy max-flow) and the capped search predicate
    (:func:`exceeds_bound` via :func:`_tiny_maxflow`).  Vertex ``v`` becomes an
    in-copy ``2v`` and an out-copy ``2v+1`` joined by an internal arc of capacity
    one (so any route uses ``v`` at most once), and each adjacency ``u -> v``
    becomes an arc ``(2u+1) -> (2v)``.  The caller uncaps the two endpoints' own
    in->out gates so Menger counts internally disjoint routes (see
    :func:`exceeds_bound`).

    ``parallel_routes`` selects the counting convention for parallel copies, the
    choice discussed at length in the thesis (sec:parallel-convention).  The
    default False caps every adjacency at one, so a bundle of parallel edges is a
    single direct route and a multigraph measures as its underlying simple graph:
    that is the convention the sixteen variants use.  Setting it True gives the
    adjacency capacity ``mu(u,v)``, so ``q`` parallel copies count as ``q``
    internally disjoint routes, which is the alternative convention explored in
    sec:multi-vertex-standard.
    """
    n = graph.num_vertices
    size = 2 * n
    cap = np.zeros((size, size), dtype=int)
    for v in range(n):
        cap[2 * v, 2 * v + 1] = 1            # internal gate: one route through v
    for u in range(n):
        for v in range(n):
            if u != v and graph.mu[u, v] > 0:
                cap[2 * u + 1, 2 * v] = (int(graph.mu[u, v]) if parallel_routes
                                         else 1)
    return cap, size


def max_multigraph_vertex_standard(n: int, m: int,
                                   deadline: float | None = None) -> tuple[int, Graph | None, bool]:
    """Exhaustive maximum for the multigraph vertex problem, OTHER convention.

    Maximises the total multiplicity of an undirected multigraph on ``n``
    vertices subject to ``kappa^max <= m - 1`` when parallel copies are counted
    as distinct internally vertex-disjoint routes.  Every multiplicity is capped
    at ``m - 1`` because ``m`` parallel copies already exceed the ceiling on
    their own.  Branch and bound over the pairs in a fixed order, trying the
    largest multiplicity first, pruning on feasibility (which is monotone) and
    on the incumbent.  Returns ``(best_total, witness, completed)``.
    """
    pairs = list(combinations(range(n), 2))
    cap = m - 1
    graph = Graph(n, MULTI_UNDIRECTED)
    best = [0, None]
    timed_out = [False]

    def feasible() -> bool:
        return not exceeds_bound(graph, m - 1, separation="vertex",
                                 parallel_routes=True)

    def recurse(i: int, total: int) -> None:
        if deadline is not None and time.time() > deadline:
            timed_out[0] = True
            return
        if total + cap * (len(pairs) - i) <= best[0]:
            return
        if i == len(pairs):
            if total > best[0]:
                best[0] = total
                best[1] = graph.copy()
            return
        u, v = pairs[i]
        for q in range(cap, -1, -1):
            graph.set_multiplicity(u, v, q)
            if q == 0 or feasible():
                recurse(i + 1, total + q)
            if timed_out[0]:
                break
        graph.set_multiplicity(u, v, 0)

    recurse(0, 0)
    return best[0], best[1], not timed_out[0]


def exceeds_bound(graph: Graph, k: int, *, separation: str = "edge",
                  parallel_routes: bool = False) -> bool:
    """``True`` iff ``lambda^max(G) > k`` (edge) or ``kappa^max(G) > k`` (vertex).

    Equivalent to ``max_connectivity(graph, vertex_split=(separation=='vertex')) > k``
    but with two early exits: each pair's capped flow stops after ``k+1`` augmenting
    paths, and the pair loop stops at the first violating pair.  On an infeasible
    graph this typically returns after a single pair.  The pair set is exactly the
    one :func:`max_connectivity` iterates, so the predicate matches it pair for pair.

    ``parallel_routes`` is passed through to :func:`_split_capacity_matrix` and
    only affects vertex mode: it selects the convention in which parallel copies
    are distinct routes, used by :func:`max_multigraph_vertex_standard`.
    """
    n = graph.num_vertices
    if separation == "edge":
        mu = graph.mu
        if _C is not None and n <= 16:
            flat, ptr = _c_flat(mu)
            directed = int(graph.variant.directed)
            return bool(_C.max_connectivity_exceeds(ptr, n, k, directed))
        for s, t in _pairs(graph):
            if _tiny_maxflow(mu, n, s, t, k):
                return True
        return False
    if separation == "vertex":
        cap, size = _split_capacity_matrix(graph, parallel_routes)
        for s, t in _pairs(graph):
            # Uncap the endpoints' own in->out gates so Menger counts INTERNAL
            # routes (mirrors local_connectivity's vertex mode); flow leaves s's
            # out-copy (2s+1) and arrives at t's in-copy (2t).
            cap[2 * s, 2 * s + 1] = _UNBOUNDED
            cap[2 * t, 2 * t + 1] = _UNBOUNDED
            hit = _tiny_maxflow(cap, size, 2 * s + 1, 2 * t, k)
            cap[2 * s, 2 * s + 1] = 1         # restore the gates for the next pair
            cap[2 * t, 2 * t + 1] = 1
            if hit:
                return True
        return False
    raise ValueError("separation must be 'edge' or 'vertex'")


# --- GOMORY-HU: encode all pairwise edge-connectivities in n-1 flows (undirected only) ---


def _undirected_capacity_graph(graph: Graph) -> nx.Graph:
    """Build the undirected capacitated graph that Gomory-Hu consumes."""
    if graph.variant.directed:
        raise ValueError("Gomory-Hu trees are defined for undirected graphs only")
    capacity_graph = nx.Graph()
    capacity_graph.add_nodes_from(graph.vertices())
    # One undirected edge per adjacency, capacity = multiplicity (its edge count).
    for u, v, multiplicity in graph.edges():
        capacity_graph.add_edge(u, v, capacity=float(multiplicity))
    return capacity_graph


def gomory_hu_tree(graph: Graph) -> nx.Graph:
    """Return a Gomory-Hu tree of ``graph`` as a weighted ``networkx`` tree.

    Each tree edge carries a ``weight`` equal to the capacity of the minimum cut
    it represents.  This is the one place that genuinely needs networkx's
    Gomory-Hu routine; it backs a figure, not any reported bound.
    """
    _require_networkx("gomory_hu_tree")
    return nx.gomory_hu_tree(_undirected_capacity_graph(graph), capacity="capacity")


def max_edge_connectivity_via_tree(graph: Graph) -> int:
    """``lambda^max(G)`` read off the Gomory-Hu tree as its heaviest edge.

    Returns ``0`` for graphs with fewer than two vertices or no edges.
    """
    if graph.num_vertices < 2:
        return 0
    tree = gomory_hu_tree(graph)
    # READ-OFF: lambda(u, v) = lightest tree edge on the u-v path, so the LARGEST
    # such bottleneck over all pairs is simply the heaviest edge in the tree.
    weights = [data["weight"] for _, _, data in tree.edges(data=True)]
    if not weights:
        return 0
    return int(round(max(weights)))


# --- PROVE: MILP for M*(n) via cut-counting (one PuLP model, CBC or Gurobi) ---
# L_m^dir(n) = (m-1)*M*(n) where M*(n) = max sum(w) s.t. maxflow(s,t;w)<=1 all pairs.
# Flow constraint encoded exactly: choose a cut x in {0,1}^n per pair, cap crossing
# weight via p; zero MIP gap = proof.  Shared helpers build constraints for both backends.


@dataclass
class ProofResult:
    """The outcome of a proof run."""

    n: int
    status: str               # OPTIMAL, LIMIT, INFEASIBLE, UNBOUNDED, ...
    scaled_optimum: float     # M*(n) = max total weight, exact if status OPTIMAL
    solver_reported_optimal: bool  # solver status, not an independently replayed gap certificate
    solve_seconds: float
    weight_matrix: np.ndarray | None  # a witnessing matrix w, if one was found

    def value_for(self, m: int) -> int:
        """The proved directed multigraph value ``L_m^dir(n) = (m-1) M*(n)``."""
        # Undo the (m-1) scaling: one proved M*(n) yields every m.
        return (m - 1) * int(round(self.scaled_optimum))

    def solver_claims_optimal(self) -> bool:
        """Whether the solver returned its ``OPTIMAL`` status.

        This is not an independently replayed optimality certificate.
        """
        return self.status == "OPTIMAL" and self.solver_reported_optimal


def _ordered_pairs(n: int) -> list[tuple[int, int]]:
    return [(u, v) for u in range(n) for v in range(n) if u != v]


def _two_hop_triples(n: int) -> list[tuple[int, int, int]]:
    # All (source, middle, target) with three distinct vertices: the s -> x -> t
    # detours that the two-hop inequality reasons about.
    return [(s, x, t)
            for s in range(n) for t in range(n) if s != t
            for x in range(n) if x != s and x != t]


# Proved values of M*(k) for the deletion cuts below (proved: M*(k) =
# 2(k-1) for k <= 6, reproduced by this optimisation and proved independently).
_PROVEN_MSTAR = {2: 2, 3: 4, 4: 6, 5: 8, 6: 10}


# ------------------------------------------------------------------
# The cut-counting MILP: one PuLP model for both provers, any solver
# ------------------------------------------------------------------
# The two provers below are the SAME cut-counting optimisation over two weight
# domains: the fractional one (prove_directed_multigraph, weights w in [0, 1], cut
# cap 1) maximises the total weight M*(n); the integral one (prove_integral_arc_
# bound, multiplicities mu in {0..m-1}, cut cap m-1) decides feasibility at a fixed
# arc target.  One builder serves both, and any MILP solver runs it: CBC (bundled
# with pulp) by default, Gurobi by a one-line switch.  Because the cut formulation
# is exact and not a relaxation, an OPTIMAL or INFEASIBLE verdict is a genuine proof.

_PULP_STATUS = {"Optimal": "OPTIMAL", "Infeasible": "INFEASIBLE",
                "Unbounded": "UNBOUNDED"}


def _pick_solver(time_limit: float, show_log: bool, use_gurobi: bool | None):
    """Choose the MILP solver.  ``gapRel=0`` demands a closed gap, which is what
    makes an OPTIMAL verdict a proof rather than a heuristic.

    ``use_gurobi``: ``True`` forces Gurobi (error if it is not usable), ``False``
    forces CBC, ``None`` uses Gurobi when its licence is active and CBC otherwise.
    Switching to Gurobi is the whole change needed to attack the open n=7 facts.
    """
    if use_gurobi is not False:
        gurobi = pulp.GUROBI_CMD(msg=show_log, timeLimit=time_limit,
                                 options=[("MIPGap", 0)])
        if gurobi.available():
            return gurobi
        if use_gurobi is True:
            raise RuntimeError(
                "use_gurobi=True but no usable Gurobi was found. This path runs "
                "Gurobi through PuLP's GUROBI_CMD, which calls the gurobi_cl "
                "command line, so gurobipy is not required: check that "
                "`gurobi_cl --version` runs and that the licence is active."
            )
    return pulp.PULP_CBC_CMD(msg=show_log, timeLimit=time_limit, gapRel=0.0)


def _cut_counting_model(n: int, *, cap: float, integer: bool, two_hop: bool,
                        symmetry: bool, deletion: bool, degree_pair: bool):
    """Build the shared cut-counting MILP as a PuLP model (no objective set yet).

    For every ordered pair (s, t) the model CHOOSES one cut: the side indicators
    fix s on the source side (constant 1) and t on the sink side (constant 0), and
    every other vertex takes a binary side.  The helper p picks up each crossing
    arc's weight through ``p >= w + cap*(x_u - x_v) - cap``, which forces ``p >= w``
    exactly on a crossing arc (x_u = 1, x_v = 0) and leaves p free at 0 otherwise.
    Capping the crossing total at ``cap`` says maxflow(s, t) <= cap, and letting the
    optimisation pick the cut means it picks the MINIMUM cut, so this is exactly
    maxflow(s, t) <= cap, the true feasible region.  ``cap=1`` with continuous
    weights is the scaled prover; ``cap=m-1`` with integer weights the arc one.

    The optional families are all proved-valid inequalities that tighten the
    relaxation without ever moving the optimum: ``two_hop`` (a two-arc-disjoint
    detour bound via z = min of the two hops), ``degree_pair`` (a flow lower bound
    on each pair), ``deletion`` (an induced-subgraph bound from proved smaller
    M*(k)), and ``symmetry`` (a degree ordering that prunes relabelled duplicates).
    Returns ``(prob, w)`` with ``w`` the weight variables keyed by ordered pair.
    """
    pairs = _ordered_pairs(n)
    prob = pulp.LpProblem("erdos915", pulp.LpMaximize)
    category = "Integer" if integer else "Continuous"
    w = {(u, v): pulp.LpVariable(f"w_{u}_{v}", 0, cap, cat=category)
         for (u, v) in pairs}

    for (s, t) in pairs:
        # s is always on the source side, t always on the sink side: constants, not
        # variables (which also avoids pulp resetting a Binary's bounds to [0, 1]).
        side = {u: 1 if u == s else 0 if u == t
                else pulp.LpVariable(f"x_{s}_{t}_{u}", cat="Binary")
                for u in range(n)}
        crossing = []
        for (u, v) in pairs:
            p_uv = pulp.LpVariable(f"p_{s}_{t}_{u}_{v}", 0, cap)
            prob += p_uv >= w[(u, v)] + cap * (side[u] - side[v]) - cap
            crossing.append(p_uv)
        prob += pulp.lpSum(crossing) <= cap          # crossing weight <= cap

    if two_hop:
        z = {}
        for (s, x, t) in _two_hop_triples(n):
            z[(s, x, t)] = pulp.LpVariable(f"z_{s}_{x}_{t}", 0, cap)
            selector = pulp.LpVariable(f"b_{s}_{x}_{t}", cat="Binary")
            # z = min(w[s,x], w[x,t]): two upper bounds, and the selector forces z
            # up to whichever argument is the minimum (big-M with M = cap).
            prob += z[(s, x, t)] <= w[(s, x)]
            prob += z[(s, x, t)] <= w[(x, t)]
            prob += z[(s, x, t)] >= w[(s, x)] - cap * (1 - selector)
            prob += z[(s, x, t)] >= w[(x, t)] - cap * selector
        for (s, t) in pairs:
            prob += w[(s, t)] + pulp.lpSum(
                z[(s, x, t)] for x in range(n) if x != s and x != t) <= cap

    if degree_pair:
        # d+(s) + d-(t) - w[s,t] <= (n-1)*cap.  This is the two-hop bound
        # aggregated: w[s,t] + sum_x min(w[s,x], w[x,t]) <= cap, plus each middle
        # max(w[s,x], w[x,t]) <= cap, sums to (n-1)*cap.  It is a genuine cut, NOT
        # trivially satisfied: the box bound alone allows the LHS up to (2n-3)*cap,
        # and a two-route witness reaches 2(n-1)*cap (e.g. n=4: s->x1->t, s->x2->t
        # gives LHS 4 > 3).  Dominated by two_hop when that family is on, but
        # standalone-useful when it is off; valid in both weight domains.
        for (s, t) in pairs:
            prob += (pulp.lpSum(w[(s, x)] for x in range(n) if x != s)
                     + pulp.lpSum(w[(x, t)] for x in range(n) if x != t)
                     - w[(s, t)]) <= (n - 1) * cap

    if deletion:
        for k, holes in ((n - 1, 1), (n - 2, 2)):
            if k not in _PROVEN_MSTAR:
                continue
            bound = cap * _PROVEN_MSTAR[k]      # induced subgraph on k vertices
            for gone in combinations(range(n), holes):
                prob += pulp.lpSum(w[(a, b)] for (a, b) in pairs
                                   if a not in gone and b not in gone) <= bound

    if symmetry:
        degree = [pulp.lpSum(w[(u, v)] for (u, v) in pairs if v0 in (u, v))
                  for v0 in range(n)]
        for v0 in range(n - 1):
            prob += degree[v0] <= degree[v0 + 1]

    return prob, w


def prove_directed_multigraph(
    n: int,
    *,
    time_limit: float = 1500.0,
    use_gurobi: bool | None = None,
    use_two_hop: bool = True,
    use_symmetry_breaking: bool = True,
    use_deletion_cuts: bool = False,
    show_solver_log: bool = False,
) -> ProofResult:
    """Prove ``M*(n)`` for the directed multigraph arc problem.

    Returns a :class:`ProofResult` containing the solver's termination status
    and primal weight matrix.  The method does not emit an independently
    replayable optimality certificate. ``use_gurobi`` picks the solver (see
    :func:`_pick_solver`). The default uses Gurobi when its licence is active and
    CBC otherwise.
    """
    _require_pulp()
    prob, w = _cut_counting_model(
        n, cap=1.0, integer=False, two_hop=use_two_hop,
        symmetry=use_symmetry_breaking, deletion=use_deletion_cuts,
        degree_pair=use_deletion_cuts,
    )
    prob += pulp.lpSum(w.values())                  # maximise total weight = M*(n)

    start = time.time()
    prob.solve(_pick_solver(time_limit, show_solver_log, use_gurobi))
    elapsed = time.time() - start
    status = _PULP_STATUS.get(pulp.LpStatus[prob.status], "LIMIT")

    weight_matrix = None
    if status == "OPTIMAL":
        weight_matrix = np.zeros((n, n))
        for (u, v), variable in w.items():
            weight_matrix[u, v] = variable.value() or 0.0

    return ProofResult(
        n=n, status=status,
        scaled_optimum=(pulp.value(prob.objective) if status == "OPTIMAL"
                        else float("nan")),
        solver_reported_optimal=(status == "OPTIMAL"),
        solve_seconds=elapsed, weight_matrix=weight_matrix,
    )


######################################################################
##
##  CHAPTER 3 — DISCOVERING BOUNDS BY SEARCH
##  The temperature search, and the one driver that proves or discovers.
##
######################################################################

# --- SENSITIVITY: sigma(e) = lambda^max(G) - lambda^max(G-e); dial for the cooling schedule ---

# A connectivity measure maps a graph to its lambda^max or kappa^max.
ConnectivityMeasure = Callable[[Graph], int]


def edge_sensitivity(
    graph: Graph,
    u: int,
    v: int,
    connectivity: ConnectivityMeasure = max_edge_connectivity,
) -> int:
    """Return ``sigma(e)`` for the edge or arc ``e = (u, v)``.

    The edge is deleted in full (all parallel copies) before remeasuring, so the
    result reflects the structural role of the adjacency rather than of a single
    parallel copy.  If the edge is absent the sensitivity is zero by convention.
    """
    if not graph.has_edge(u, v):
        return 0  # absent edge: nothing to remove, sensitivity is zero
    before = connectivity(graph)
    reduced = graph.copy()
    reduced.set_multiplicity(u, v, 0)  # delete the WHOLE adjacency (all copies)
    after = connectivity(reduced)
    # How much lambda^max dropped: positive means e was load-bearing.
    return before - after


def sensitivity_map(
    graph: Graph,
    connectivity: ConnectivityMeasure = max_edge_connectivity,
) -> dict[tuple[int, int], int]:
    """Return ``{(u, v): sigma((u, v))}`` over all present edges or arcs.

    Useful for visualising an extremiser: high-sensitivity edges are the load
    bearers, low-sensitivity edges are slack.

    The baseline connectivity ``before = connectivity(graph)`` is the SAME for
    every edge, so it is measured once here rather than re-measured inside each
    :func:`edge_sensitivity` call.  This changes no value (the result equals
    ``{e: edge_sensitivity(graph, *e) for e in graph.edges()}``); it only avoids
    recomputing the shared baseline once per edge.
    """
    before = connectivity(graph)
    result: dict[tuple[int, int], int] = {}
    for u, v, _ in graph.edges():
        reduced = graph.copy()
        reduced.set_multiplicity(u, v, 0)   # delete the WHOLE adjacency (all copies)
        result[(u, v)] = before - connectivity(reduced)
    return result


# --- SEARCH: simulated annealing; E = -|E(G)| + penalty*max(0,lambda^max-(m-1)) ---
# Metropolis rule with geometric cooling; removal proposals biased by edge sensitivity.


@dataclass
class SearchStep:
    """One step of the search, recorded for plotting the temperature trace."""

    step: int
    temperature: float
    energy: float
    edge_count: int
    connectivity: int
    accepted: bool
    seconds: float = 0.0       # wall-clock since the search began (for timed traces)
    best_feasible: int = 0     # densest feasible graph seen so far (for convergence)


@dataclass
class SearchResult:
    """The outcome of a search: the best feasible graph and the full trace."""

    best_graph: Graph
    best_edge_count: int
    feasible_found: bool
    history: list[SearchStep] = field(default_factory=list)

    def acceptance_rate(self) -> float:
        """Fraction of proposed moves that were accepted."""
        if not self.history:
            return 0.0
        return sum(record.accepted for record in self.history) / len(self.history)


def _connectivity_measure(separation: str):
    """Return the connectivity function named by ``separation``."""
    if separation == "edge":
        return max_edge_connectivity
    if separation == "vertex":
        return max_vertex_connectivity
    raise ValueError("separation must be 'edge' or 'vertex'")


def _energy(graph: Graph, m: int, measure, penalty: float) -> float:
    """The energy ``-|E| + penalty * excess connectivity``."""
    # Excess is how far connectivity exceeds the allowed m-1; zero when feasible.
    excess = max(0, measure(graph) - (m - 1))
    # Lower energy is better: more edges (negative term) and no excess.
    return -graph.edge_count() + penalty * excess


def _proposal_energy(
    proposal: Graph,
    *,
    is_add: bool,
    feasible_current: bool,
    lam_ub: int,
    m: int,
    penalty: float,
    measure_full,
    separation: str,
) -> tuple[float, bool]:
    """Return ``(_energy(proposal), proposal_is_feasible)`` doing the least work.

    The energy ``-|E| + penalty * max(0, connectivity - (m-1))`` depends on the
    connectivity only through the excess, and by monotonicity (parts (1) and (2)
    of the thesis's Proposition on monotone binding connectivity) that excess is
    provably zero on most steps, so no flow is needed:

    - a removal from a feasible graph stays feasible (part 1), excess 0;
    - an addition while ``lam_ub <= m-2`` stays feasible (part 2), excess 0.

    Only when neither shortcut applies do we run one capped predicate, and only when
    that reports an infeasible proposal do we spend the exact ``measure_full`` to get
    the penalty term right.  The float returned is byte-for-byte the one ``_energy``
    would return (the same arithmetic on the same excess), so the search trajectory
    is unchanged.  The boolean is the EXACT feasibility of ``proposal``.
    """
    edges = proposal.edge_count()
    # Decide excess = max(0, measure(proposal) - (m-1)) with the least work.
    if (is_add and lam_ub <= m - 2) or (not is_add and feasible_current):
        excess = 0                       # part (2) add, or part (1) remove: provably feasible
    elif not exceeds_bound(proposal, m - 1, separation=separation):
        excess = 0                       # at the boundary but the capped flow clears it
    else:
        excess = measure_full(proposal) - (m - 1)   # infeasible: exact penalty term
    # Identical arithmetic to _energy, so the returned float matches it exactly.
    return -edges + penalty * excess, excess == 0


def _candidate_pairs(graph: Graph) -> list[tuple[int, int]]:
    """All ordered pairs (directed) or unordered pairs (undirected)."""
    n = graph.num_vertices
    pairs = []
    for u in range(n):
        start = 0 if graph.variant.directed else u + 1
        for v in range(start, n):
            if u != v:
                pairs.append((u, v))
    return pairs


def _propose_removal(
    graph: Graph,
    temperature: float,
    rng: random.Random,
    cached_sensitivity: dict[tuple[int, int], int] | None,
) -> tuple[int, int]:
    """Choose a present edge to thin out, biased toward free (low sigma) edges.

    Without a sensitivity cache the choice is uniform.  With one, edge ``e`` is
    drawn with weight ``exp(-sigma(e) / T)``: at high ``T`` the weights flatten
    (uniform exploration), at low ``T`` they concentrate on ``sigma = 0`` edges.
    """
    present = [(u, v) for u, v, _ in graph.edges()]
    if cached_sensitivity is None:
        return rng.choice(present)  # no guidance: uniform removal
    # exp(-sigma/T): big sigma (load-bearing) is suppressed, and the suppression
    # sharpens as T -> 0.  max(T, eps) guards against division by zero.
    weights = [
        math.exp(-cached_sensitivity.get((u, v), 0) / max(temperature, 1e-9))
        for (u, v) in present
    ]
    return rng.choices(present, weights=weights, k=1)[0]


def search_for_dense_graph(
    variant: Variant,
    n: int,
    m: int,
    *,
    separation: str = "edge",
    steps: int = 4000,
    initial_temperature: float = 3.0,
    cooling: float = 0.9985,
    penalty: float = 6.0,
    max_multiplicity: int | None = None,
    sensitivity_guided: bool = True,
    bias_refresh: int = 200,
    seed: int = 0,
    deadline: float | None = None,
    record_exact_connectivity: bool = False,
    reference_mode: bool = False,
) -> SearchResult:
    """Find the densest feasible graph by a guided random search (simulated annealing).

    Args:
        variant: which graph model to search in.
        n: number of vertices.
        m: forbidden value. Feasibility means ``connectivity <= m - 1``.
        separation: ``"edge"`` for arc/edge-disjoint, ``"vertex"`` for
            internally vertex-disjoint paths.
        steps: number of proposed moves.
        initial_temperature: starting temperature ``T_0``.
        cooling: factor (< 1) the temperature is multiplied by each step.
        penalty: weight of the connectivity violation in the energy.
        max_multiplicity: cap on parallel edges (defaults to ``m - 1``, a simple
            variant is always capped at one regardless).
        sensitivity_guided: bias removals toward free edges (the temperature
            dial described in the module docstring).
        bias_refresh: recompute the sensitivity cache every this many steps.
        seed: random seed, fixed so figures are reproducible.
        record_exact_connectivity: log the EXACT ``lambda^max`` per step in
            ``SearchStep.connectivity`` (the figure-trace needs it).  When False,
            the cheaper maintained upper bound ``lam_ub`` is logged instead, which
            does not affect the search at all (the energy never reads this field).
        reference_mode: INTERNAL, test only.  Force the slow, exact per-step
            energy (call :func:`_energy` and :func:`max_connectivity` directly)
            instead of the capped/monotone fast path.  Used by the equivalence
            test to prove the fast path reproduces this reference step for step.

    Returns:
        An :class:`SearchResult` with the best feasible graph found and the
        full step-by-step history.

    The fast path is *trajectory-preserving*: it computes the identical per-step
    energy as ``reference_mode`` (proven by ``test_search.test_fast_path_matches_exact``),
    so every accept/reject decision, the random-number draw order, and the returned
    witness are unchanged.  It only avoids flows whose result the energy cannot
    depend on (Facts M1/M2: a removal from a feasible graph stays feasible, an
    addition while ``lam_ub <= m-2`` stays feasible), and resyncs the upper bound
    ``lam_ub`` to the exact value at the ``bias_refresh`` cadence.
    """
    rng = random.Random(seed)
    measure = _connectivity_measure(separation)
    if max_multiplicity is not None and max_multiplicity < 0:
        raise ValueError("max_multiplicity must be non-negative")
    # Multiplicity cap: simple graphs are always 0/1; multigraphs default to m-1.
    cap = 1 if variant.simple else (
        max_multiplicity if max_multiplicity is not None else m - 1)
    pairs = None  # built lazily once we know we need it

    current = Graph(n, variant)  # start from the empty graph: feasible, energy 0
    current_energy = _energy(current, m, measure, penalty)

    best_graph = current.copy()
    best_edges = 0
    feasible_found = True  # the empty graph is feasible

    # State carried across steps so the energy can avoid recomputing connectivity
    # from scratch (see the trajectory-preserving note in the docstring):
    #   feasible -- is `current` feasible (lambda^max <= m-1)?  Exact at all times.
    #   lam_ub   -- a SOUND upper bound on lambda^max(current).  Facts M1/M2 keep it
    #               sound: +1 on an accepted addition, unchanged on a removal.
    feasible = True            # the empty graph is feasible
    lam_ub = 0                 # lambda^max(empty graph) = 0

    temperature = initial_temperature
    cached_sensitivity = None
    history: list[SearchStep] = []
    clock_start = time.perf_counter()  # for the timed convergence trace only

    for step in range(steps):
        # Periodically recompute the sensitivity map that guides removals.  It
        # is expensive, so we cache it and refresh only every bias_refresh steps.
        if sensitivity_guided and step % bias_refresh == 0 and current.edge_count() > 0:
            cached_sensitivity = sensitivity_map(current, measure)
        # Resync the upper bound to the truth at the same cadence (the bound can
        # only drift upward over a run of removals, which costs extra capped checks
        # but never correctness).  This step already pays for flows above, and the
        # resync touches neither the energy nor the RNG, so the trajectory is safe.
        if step % bias_refresh == 0:
            lam_ub = measure(current)
            feasible = lam_ub <= m - 1

        proposal = current.copy()
        # Flip a coin: remove an edge (only if some exist) or add one.
        removing = current.edge_count() > 0 and rng.random() < 0.5
        if removing:
            # Sensitivity-guided removal: prefers free edges, especially cold.
            u, v = _propose_removal(current, temperature, rng, cached_sensitivity)
            proposal.remove_edge(u, v)
        else:
            if pairs is None:
                pairs = _candidate_pairs(current)
            # Only pairs that have room under the multiplicity cap can grow.
            addable = [(u, v) for (u, v) in pairs if proposal.multiplicity(u, v) < cap]
            if not addable:
                continue  # nothing to add; skip this step
            u, v = rng.choice(addable)
            proposal.add_edge(u, v)
        is_add = not removing

        # The proposal's energy and exact feasibility.  reference_mode is the slow,
        # exact path the equivalence test compares against; the fast path returns
        # the IDENTICAL energy by Facts M1/M2 (see _proposal_energy).
        if reference_mode:
            proposal_energy = _energy(proposal, m, measure, penalty)
            proposal_feasible = measure(proposal) <= m - 1
        else:
            proposal_energy, proposal_feasible = _proposal_energy(
                proposal, is_add=is_add, feasible_current=feasible, lam_ub=lam_ub,
                m=m, penalty=penalty, measure_full=measure, separation=separation)
        change = proposal_energy - current_energy
        # ACCEPT OR NOT: always take an improvement (change <= 0); take a worsening
        # move only with probability exp(-change / T).  As T falls this probability
        # shrinks, so the walk increasingly refuses to go uphill.
        accept = change <= 0 or rng.random() < math.exp(-change / max(temperature, 1e-9))

        if accept:
            current, current_energy = proposal, proposal_energy
            # Carry the exact feasibility and update the bound by M2 (an accepted
            # addition can raise lambda^max by at most 1; a removal cannot raise it).
            feasible = proposal_feasible
            if is_add:
                lam_ub += 1
            # Track the best FEASIBLE graph found (within bound and denser than any
            # seen so far): this is the lower-bound witness.  `feasible` is exact
            # here, so the witness is certified with no extra flow.
            if feasible and current.edge_count() > best_edges:
                best_graph, best_edges = current.copy(), current.edge_count()
                feasible_found = True

        # The connectivity field feeds fig:trace only.  Log the exact value when the
        # figure asks for it (or in reference_mode), else the maintained upper bound.
        if record_exact_connectivity or reference_mode:
            recorded_connectivity = measure(current)
            # Cheap audit in the exact paths: the maintained bound must never
            # underestimate, and the feasibility flag must match the truth.
            assert lam_ub >= recorded_connectivity, (lam_ub, recorded_connectivity)
            assert feasible == (recorded_connectivity <= m - 1)
        else:
            recorded_connectivity = lam_ub
        history.append(SearchStep(
            step=step,
            temperature=temperature,
            energy=current_energy,
            edge_count=current.edge_count(),
            connectivity=recorded_connectivity,
            accepted=accept,
            seconds=time.perf_counter() - clock_start,
            best_feasible=best_edges,
        ))
        temperature *= cooling  # cool down: T <- cooling * T each step

        # Respect the deadline when supplied; check every 100 steps to amortise
        # the time.time() call.
        if deadline is not None and step % 100 == 99 and time.time() > deadline:
            break

    return SearchResult(best_graph, best_edges, feasible_found, history)


def _neighbour_moves(graph: Graph, cap: int) -> list[tuple[int, int, int]]:
    """Every single add (``+1``) or remove (``-1``) of one edge/arc under the cap.

    The shared neighbourhood of both discoverers: one ordered pair for a digraph,
    one unordered pair for an undirected graph, addable while below the
    multiplicity ``cap`` and removable while above zero.
    """
    n = graph.num_vertices
    directed = graph.variant.directed
    moves: list[tuple[int, int, int]] = []
    for u in range(n):
        for v in range(n):
            if u == v or (not directed and v < u):
                continue
            mult = graph.multiplicity(u, v)
            if mult < cap:
                moves.append((u, v, +1))
            if mult > 0:
                moves.append((u, v, -1))
    return moves


def tabu_search_for_dense_graph(
    variant: Variant,
    n: int,
    m: int,
    *,
    separation: str = "edge",
    steps: int = 4000,
    penalty: float = 6.0,
    tenure: int = 7,
    stall_limit: int = 40,
    max_multiplicity: int | None = None,
    seed: int = 0,
    deadline: float | None = None,
    record_exact_connectivity: bool = True,
) -> SearchResult:
    """Find the densest feasible graph by tabu search, the deterministic twin of
    :func:`search_for_dense_graph`.

    Same energy ``-|E| + penalty * max(0, connectivity - (m-1))`` and the same
    neighbourhood (:func:`_neighbour_moves`) as the annealer, but a different
    engine.  Each step scans the whole neighbourhood and takes the best move whose
    pair is not on the tabu list, forbids that pair for ``tenure`` steps, and
    perturbs from the incumbent once it has stalled for ``stall_limit`` steps.
    Aspiration overrides the tabu flag for any move that beats the global best.
    There is no temperature and no accept-worse coin: the only randomness is the
    seed driving the perturbation kicks, so two runs from one seed are identical.

    Returns the same :class:`SearchResult` as the annealer (the best feasible graph
    and the full timed history), so the two engines are interchangeable through the
    ``method`` argument of :func:`best_of_searches` and :func:`solve`.
    """
    rng = random.Random(seed)
    measure = _connectivity_measure(separation)
    if max_multiplicity is not None and max_multiplicity < 0:
        raise ValueError("max_multiplicity must be non-negative")
    cap = 1 if variant.simple else (
        max_multiplicity if max_multiplicity is not None else m - 1)

    current = Graph(n, variant)            # start empty: feasible, energy 0
    best_graph, best_edges = current.copy(), 0
    tabu: dict[tuple[int, int], int] = {}
    stall = 0
    history: list[SearchStep] = []
    clock_start = time.perf_counter()

    def trial_energy_and_feasibility(graph: Graph) -> tuple[float, bool]:
        """The annealer's energy and exact feasibility, by the same capped trick.

        ``exceeds_bound`` decides feasibility with an early-exit capped flow, and
        the full ``measure`` runs only on the rare infeasible trial that needs its
        penalty term, so most moves cost one cheap predicate instead of a full
        all-pairs flow.  The returned float equals ``_energy`` exactly.
        """
        edges = graph.edge_count()
        if not exceeds_bound(graph, m - 1, separation=separation):
            return float(-edges), True              # feasible: excess is zero
        return -edges + penalty * (measure(graph) - (m - 1)), False

    for step in range(steps):
        if deadline is not None and time.time() > deadline:
            break
        best_move: tuple[int, int, int] | None = None
        best_move_energy: float | None = None
        best_move_global = False
        for (u, v, d) in _neighbour_moves(current, cap):
            trial = current.copy()
            trial.add_edge(u, v) if d > 0 else trial.remove_edge(u, v)
            trial_energy, trial_feasible = trial_energy_and_feasibility(trial)
            improves_global = trial_feasible and trial.edge_count() > best_edges
            if tabu.get((u, v), 0) > step and not improves_global:
                continue                   # tabu, with no aspiration to override
            if (best_move_energy is None or trial_energy < best_move_energy
                    or (improves_global and not best_move_global)):
                best_move, best_move_energy = (u, v, d), trial_energy
                best_move_global = improves_global
        if best_move is None:              # every move tabu: clear the list, retry
            tabu.clear()
            continue

        u, v, d = best_move
        current.add_edge(u, v) if d > 0 else current.remove_edge(u, v)
        tabu[(u, v)] = step + tenure

        connectivity = measure(current)    # computed anyway for best-tracking
        if connectivity <= m - 1 and current.edge_count() > best_edges:
            best_graph, best_edges = current.copy(), current.edge_count()
            stall = 0
        else:
            stall += 1
        history.append(SearchStep(
            step=step, temperature=0.0, energy=best_move_energy,
            edge_count=current.edge_count(),
            connectivity=connectivity if record_exact_connectivity else -1,
            accepted=True,                 # tabu always takes its best legal move
            seconds=time.perf_counter() - clock_start,
            best_feasible=best_edges,
        ))

        if stall >= stall_limit:           # perturb from the incumbent and reset
            current = best_graph.copy()
            for _ in range(rng.randint(2, 4)):
                kicks = _neighbour_moves(current, cap)
                if kicks:
                    a, b, dd = rng.choice(kicks)
                    current.add_edge(a, b) if dd > 0 else current.remove_edge(a, b)
            tabu.clear()
            stall = 0

    return SearchResult(best_graph, best_edges, feasible_found=True, history=history)


def _run_one_search(args: tuple) -> SearchResult:
    """Module-level worker for parallel restarts (must be picklable for ProcessPoolExecutor)."""
    variant, n, m, seed, method, search_options = args
    engine = tabu_search_for_dense_graph if method == "tabu" else search_for_dense_graph
    return engine(variant, n, m, seed=seed, **search_options)


def best_of_searches(
    variant: Variant,
    n: int,
    m: int,
    *,
    restarts: int = 6,
    seed: int = 0,
    parallel: bool = True,
    method: str = "sa",
    **search_options,
) -> SearchResult:
    """Run several independent discovery schedules and keep the densest result.

    A single search can settle into a local optimum, so for reliable
    rediscovery we restart from a fresh random seed a handful of times and return
    the run that found the most edges.  Any keyword understood by the chosen
    engine (``steps``, ``penalty``, ``separation``, and so on) is forwarded
    unchanged.

    Args:
        parallel: when ``True`` (default), run the restarts concurrently using
            :class:`~concurrent.futures.ProcessPoolExecutor`.  Each restart has
            a distinct seed so the runs are genuinely independent.  Falls back
            to sequential execution if multiprocessing is unavailable.
        method: ``"sa"`` (default, simulated annealing,
            :func:`search_for_dense_graph`) or ``"tabu"``
            (:func:`tabu_search_for_dense_graph`).  Both optimise the same energy
            over the same neighbourhood and return the same result type.
    """
    if method not in ("sa", "tabu"):
        raise ValueError("method must be 'sa' or 'tabu'")
    task_args = [(variant, n, m, seed + r, method, search_options) for r in range(restarts)]

    if parallel and restarts > 1:
        try:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                results = list(executor.map(_run_one_search, task_args))
        except (OSError, concurrent.futures.BrokenExecutor) as exc:
            # Multiprocessing is genuinely unavailable here (a sandbox with no
            # fork/spawn, or a worker that could not start).  Fall back to a
            # sequential run, but say so rather than masking the loss of cores.
            # A bug inside the worker is NOT caught here, so it fails loudly.
            warnings.warn(
                f"parallel restarts unavailable ({exc!r}); running sequentially",
                RuntimeWarning, stacklevel=2,
            )
            results = [_run_one_search(a) for a in task_args]
    else:
        results = [_run_one_search(a) for a in task_args]

    return max(results, key=lambda r: r.best_edge_count)


# --- SOLVE: unified driver; exhaustive=True proves, exhaustive=False discovers ---


@dataclass
class SolveResult:
    """The outcome of a solve, carrying an honest bound label."""

    n: int
    m: int
    variant: str            # human label, e.g. "simple directed"
    separation: str         # "edge" or "vertex"
    value: int              # the extremal count we report
    bound: str              # "exact" | "lower" | "upper"
    method: str             # how the value was obtained
    seconds: float
    complete: bool          # True only when a proving route completed; never discovery
    witness: object | None  # a Graph/Hypergraph attaining ``value``, if any
    note: str = ""

    @property
    def proven(self) -> bool:
        """Whether ``value`` is a proved exact extremal value."""
        return self.bound == "exact"

    def describe(self) -> str:
        """One readable line summarising the result."""
        relation = {"exact": "= ", "lower": ">= ", "upper": "<= "}[self.bound]
        line = (f"{self.variant} ({self.separation}), n={self.n}, m={self.m}: "
                f"value {relation}{self.value}  "
                f"[{self.bound}, {self.method}, {self.seconds:.1f}s]")
        return line if not self.note else f"{line}\n    note: {self.note}"


def _joined_note(*parts: str) -> str:
    """Join the non-empty note fragments a SolveResult may carry."""
    return "; ".join(part for part in parts if part)


def _variant_for(directed: bool, simple: bool) -> Variant:
    """Pick the matching named Variant constant from the two booleans."""
    if directed:
        return SIMPLE_DIRECTED if simple else MULTI_DIRECTED
    return SIMPLE_UNDIRECTED if simple else MULTI_UNDIRECTED


def _matrix_cells(n: int, directed: bool) -> list[tuple[int, int]]:
    """The off-diagonal matrix cells a graph of this kind may fill.

    Directed graphs vary every ordered pair; undirected graphs vary only the
    upper triangle, since ``set_multiplicity`` mirrors the lower half for us.
    """
    if directed:
        return [(u, v) for u in range(n) for v in range(n) if u != v]
    return [(u, v) for u in range(n) for v in range(n) if u < v]


def _directed_witness(n: int, m: int, simple: bool) -> Graph | None:
    """The densest named directed construction that is feasible for ``(n, m)``.

    Used to exhibit a concrete graph attaining the proved value: the best
    applicable hub or one-directional-wall construction, or ``None`` if no
    named construction applies to this case.
    """
    candidates: list[Graph] = []
    if simple:
        if n >= m:
            candidates.extend((directed_hub(n, m), augmented_bipartite(n, m)))
        if m == 2:
            candidates.append(one_directional_bipartite(n))
    else:
        candidates.extend((
            double_star(n, m, directed=True),
            thickened_one_directional_bipartite(n, m),
        ))
    feasible = [g for g in candidates if max_edge_connectivity(g) <= m - 1]
    return max(feasible, key=lambda g: g.edge_count()) if feasible else None


def _brute_force_matrix(
    variant: Variant, n: int, m: int, separation: str, deadline: float,
) -> tuple[int, Graph | None, bool]:
    """Exhaustively maximise edges over every graph of ``variant`` on ``n``.

    Returns ``(best_edge_count, witness, completed)``.  ``completed`` is False if
    the budget ran out first, in which case the value is only a lower bound.
    A simple cell ranges over ``{0, 1}``; a multigraph cell over ``{0, ..., m-1}``
    because multiplicity ``m`` already gives ``m`` parallel disjoint routes.

    The walk is a depth-first assignment of the cells in a fixed order, with the
    same two prunings the digraph prover uses (:func:`_exhaustive_directed`), so
    that every model is enumerated the same way rather than only the directed one:

    * **Feasibility is monotone.**  Undecided cells sit at zero, so any completion
      of the current partial graph only ever RAISES multiplicities, and raising a
      multiplicity can never lower a connectivity (:func:`exceeds_bound` measures
      what is already placed).  Once the partial graph breaks the ceiling, every
      completion of it breaks the ceiling too, and the whole subtree is dropped.
    * **A counting ceiling.**  At depth ``pos`` the cells ``pos .. total-1`` are
      still undecided, which is ``total - pos`` of them, and each can add at most
      ``span - 1``.  So ``count + (total - pos) * (span - 1)`` is an upper bound
      on every completion below this node.  If even that ceiling cannot beat the
      best feasible graph already in hand, the subtree is dropped unexplored.
      The test is ``<=`` rather than ``<`` because only a strict improvement ever
      replaces the incumbent.

    Both prunings only ever discard graphs that are infeasible or that cannot beat
    the incumbent, so a run that finishes returns exactly the maximum the blind
    sweep would have returned.  That equivalence is not left to the argument
    above: ``tests/test_solve.py`` differential-tests this routine against a blind
    product sweep over every variant and every size the blind one can reach.
    """
    cells = _matrix_cells(n, variant.directed)
    span = 2 if variant.simple else m       # cell value lives in range(span)
    total = len(cells)
    # headroom[pos] = the most the still-undecided cells pos .. total-1 can add.
    headroom = [(total - i) * (span - 1) for i in range(total + 1)]
    best_count, best_graph = 0, None
    completed = [True]
    graph = Graph(n, variant)

    def descend(pos: int, count: int) -> None:
        nonlocal best_count, best_graph
        if not completed[0]:
            return
        if count + headroom[pos] <= best_count:
            return                          # even the ceiling cannot beat the best
        if time.time() > deadline:
            completed[0] = False            # ran out before exhausting the space
            return
        if pos == total:
            if count > best_count:
                best_count, best_graph = count, graph.copy()
            return
        u, v = cells[pos]
        # Descending values first, so a dense feasible graph is found early and
        # the counting prune bites on the sparser siblings.
        for value in range(span - 1, 0, -1):
            graph.set_multiplicity(u, v, value)
            if not exceeds_bound(graph, m - 1, separation=separation):
                descend(pos + 1, count + value)
        graph.set_multiplicity(u, v, 0)
        descend(pos + 1, count)

    descend(0, 0)
    return best_count, best_graph, completed[0]


def _search_within_budget(
    variant: Variant, n: int, m: int, separation: str,
    deadline: float, seed: int, method: str = "sa",
) -> SearchResult:
    """Repeated search restarts until the deadline; keep the densest run."""
    engine = tabu_search_for_dense_graph if method == "tabu" else search_for_dense_graph
    best: SearchResult | None = None
    restart = 0
    while True:
        # Pass the deadline through so a single long restart can be cut short.
        outcome = engine(variant, n, m, separation=separation,
                         steps=4000, seed=seed + restart, deadline=deadline)
        if best is None or outcome.best_edge_count > best.best_edge_count:
            best = outcome
        restart += 1
        if time.time() > deadline or restart >= 200:
            break
    assert best is not None
    return best


def _hyperedge_candidates(n: int, r: int, directed: bool, *, kind: str = "forward") -> list:
    """Every possible ``r``-uniform hyperedge.

    Undirected: every ``r``-subset.  Directed: the ``kind`` selects the
    orientation model.

    * ``"forward"`` (default): one tail, ``r - 1`` heads, stored in the legacy
      ``(tail:int, heads)`` form so existing forward results are untouched.
    * ``"backward"``: ``r - 1`` tails, one head (the arc-reversal dual of
      forward), stored in the general ``(tails, heads)`` form.
    * ``"general"``: every split of an ``r``-subset into a non-empty tail set and
      a non-empty head set, i.e. forward, backward, and (from ``r >= 4``) mixed.
    """
    if not directed:
        return [frozenset(s) for s in combinations(range(n), r)]
    if kind == "forward":
        # One tail and r-1 heads chosen from the rest (legacy form).
        return [(tail, frozenset(heads))
                for tail in range(n)
                for heads in combinations([v for v in range(n) if v != tail], r - 1)]
    if kind == "backward":
        # r-1 tails and one head: the reverse of every forward arc.
        return [(frozenset(tails), frozenset((head,)))
                for head in range(n)
                for tails in combinations([v for v in range(n) if v != head], r - 1)]
    if kind == "general":
        # Every ordered (tails, heads) split of each r-subset, both sides non-empty.
        out: list = []
        for subset in combinations(range(n), r):
            for mask in range(1, (1 << r) - 1):     # exclude all-heads and all-tails
                tails = frozenset(subset[i] for i in range(r) if mask & (1 << i))
                heads = frozenset(subset[i] for i in range(r) if not (mask & (1 << i)))
                out.append((tails, heads))
        return out
    raise ValueError(f"unknown directed hyperedge kind {kind!r}")


def _hyper_multiplicity_cap(m: int, simple: bool) -> int:
    """How many copies of one hyperedge a feasible hypergraph may carry.

    A simple hypergraph allows at most one.  In a multihypergraph, ``q`` parallel
    copies of a hyperedge already give ``q`` Berge routes between any two of its
    members, one per copy, and those routes have empty interiors, so they are
    pairwise hyperedge-disjoint AND internally vertex-disjoint.  Feasibility
    therefore caps every multiplicity at ``m - 1`` by itself, under BOTH
    separations.  This is what keeps the multihypergraph question finite, and it
    is why the multi rows do not collapse onto the simple ones the way the
    multigraph VERTEX rows do (``sec:parallel-convention``): there a parallel copy
    is a route with an empty interior between ADJACENT vertices only, and the
    objective was redefined to count adjacencies.
    """
    return 1 if simple else m - 1


def _brute_force_hypergraph(
    n: int, r: int, m: int, deadline: float,
    *, directed: bool = False, vertex_split: bool = False, kind: str = "forward",
    simple: bool = True,
) -> tuple[int, Hypergraph | None, bool]:
    """Exhaustively maximise hyperedges over all ``r``-uniform hypergraphs.

    Each possible hyperedge is given a multiplicity from ``0`` to
    :func:`_hyper_multiplicity_cap`, so the search visits ``(cap + 1) ** (#candidates)``
    hypergraphs; only tiny ``(n, r)`` finish, and the multihypergraph sweep
    (``simple=False``) reaches roughly one vertex fewer than the simple one.  The
    ``directed`` and ``vertex_split`` flags select which of the four hypergraph
    measures decides feasibility, exactly as ``solve`` passes them through, and
    ``kind`` selects the directed orientation model (forward/backward/general).
    """
    candidates = _hyperedge_candidates(n, r, directed, kind=kind)
    cap = _hyper_multiplicity_cap(m, simple)
    best_count, best_h, completed = 0, None, True
    for tick, mult in enumerate(product(range(cap + 1), repeat=len(candidates))):
        if tick % 256 == 0 and time.time() > deadline:
            completed = False
            break
        chosen = [candidates[i] for i, q in enumerate(mult) for _ in range(q)]
        hypergraph = Hypergraph(n, chosen, directed=directed)
        if (max_hyper_connectivity(hypergraph, vertex_split=vertex_split) <= m - 1
                and hypergraph.edge_count() > best_count):
            best_count, best_h = hypergraph.edge_count(), hypergraph
    return best_count, best_h, completed


def _random_hypergraph_search(
    n: int, r: int, m: int, deadline: float, seed: int,
    *, directed: bool = False, vertex_split: bool = False, kind: str = "forward",
    simple: bool = True,
) -> tuple[int, Hypergraph | None]:
    """Greedy randomised growth: add random hyperedges while feasible, restart.

    A discovery heuristic for the hypergraph model (search is matrix-only):
    each pass shuffles the candidate hyperedges and adds each one that keeps the
    Berge connectivity within ``m - 1``; the densest pass within budget wins.  In
    the multihypergraph model each candidate is offered up to
    :func:`_hyper_multiplicity_cap` times rather than once, so parallel copies can
    be discovered.  The feasible hypergraph it returns is the easy construction
    behind a lower bound.  ``kind`` selects the directed orientation model.
    """
    rng = random.Random(seed)
    candidates = _hyperedge_candidates(n, r, directed, kind=kind)
    cap = _hyper_multiplicity_cap(m, simple)
    best_count, best_h = 0, None
    while time.time() < deadline:
        order = [e for e in candidates for _ in range(cap)]
        rng.shuffle(order)
        hypergraph = Hypergraph(n, directed=directed)
        for edge in order:
            hypergraph.add_hyperedge(edge)
            if max_hyper_connectivity(hypergraph, vertex_split=vertex_split) > m - 1:
                hypergraph.hyperedges.pop()   # this one broke feasibility; undo
        if hypergraph.edge_count() > best_count:
            best_count, best_h = hypergraph.edge_count(), hypergraph
    return best_count, (best_h if best_h is not None else Hypergraph(n, directed=directed))


def _flow_at_least(cap: dict[tuple[int, int], int], num_nodes: int,
                    source: int, sink: int, k: int) -> bool:
    """True if ``k`` rounds of Ford--Fulkerson find an augmenting path each time.

    The shared engine behind :func:`_arc_flow_at_least` and
    :func:`_vertex_flow_at_least`, which differ only in how they build ``cap``
    (the plain arc network versus the vertex-split network) and in what
    ``source``/``sink``/``num_nodes`` mean for that network. Each round finds
    any augmenting path in the residual (forward arcs and the reverse arcs
    left by earlier augmentations) by DFS and pushes one unit of flow along
    it; the first round with no path means fewer than ``k`` disjoint routes
    exist. Mutates ``cap`` in place as the residual network, so callers pass
    a freshly built dict.
    """
    for _ in range(k):
        prev = {source: source}
        stack = [source]                  # DFS for any residual augmenting path
        while stack:
            x = stack.pop()
            if x == sink:
                break
            for y in range(num_nodes):
                if y not in prev and cap.get((x, y), 0) > 0:
                    prev[y] = x
                    stack.append(y)
        if sink not in prev:
            return False                  # no further path: fewer than k exist
        node = sink                       # walk back, pushing one unit of flow
        while node != source:
            p = prev[node]
            cap[(p, node)] -= 1
            cap[(node, p)] = cap.get((node, p), 0) + 1
            node = p
    return True


def _arc_flow_at_least(out_adj: list[set[int]], n: int, s: int, t: int,
                       k: int) -> bool:
    """True if there are at least ``k`` arc-disjoint ``s``-``t`` paths.

    Builds the plain unit-capacity arc network and hands it to
    :func:`_flow_at_least`. Used as the inner feasibility test of the
    exhaustive digraph search, where the question is only whether the
    local connectivity has reached the forbidden value ``m`` (so ``k = m``).
    """
    cap: dict[tuple[int, int], int] = {}
    for a in range(n):
        for b in out_adj[a]:
            cap[(a, b)] = 1
    return _flow_at_least(cap, n, s, t, k)


def _vertex_flow_at_least(out_adj: list[set[int]], n: int, s: int, t: int,
                          k: int) -> bool:
    """True if there are at least ``k`` internally vertex-disjoint ``s``-``t`` paths.

    The vertex twin of :func:`_arc_flow_at_least`: builds the split network
    instead of the plain one, every vertex ``x`` becoming an entry copy
    ``2x`` and an exit copy ``2x+1`` joined by a single unit-capacity arc so
    a path may pass through ``x`` at most once, with the two endpoints
    keeping an uncapped gate since a route is allowed to start at ``s`` and
    finish at ``t`` (a direct arc ``s -> t`` therefore counts as one route
    with no interior, exactly as the thesis's separation axis intends), and
    hands that network to the same :func:`_flow_at_least` engine.
    """
    cap: dict[tuple[int, int], int] = {}
    for x in range(n):
        cap[(2 * x, 2 * x + 1)] = k if (x == s or x == t) else 1
    for a in range(n):
        for b in out_adj[a]:
            cap[(2 * a + 1, 2 * b)] = 1
    return _flow_at_least(cap, 2 * n, 2 * s + 1, 2 * t, k)


def _exhaustive_directed(
    n: int, m: int, separation: str, deadline: float,
    stats: dict[str, int] | None = None,
) -> tuple[int, Graph | None, bool]:
    """Prove the simple directed maximum by a pruned exhaustive search.

    This is the honest version of the thesis's base-case search: branch and bound
    over every simple digraph on ``n`` vertices, keeping the densest one whose
    connectivity stays within ``m - 1``.  Two prunes make it finish where naive
    enumeration cannot.  Feasibility is monotone, so the include branch adds an
    arc only when the digraph is still feasible (an infeasible prefix can never be
    rescued by adding more arcs), and the bound prune drops a subtree once even
    taking every remaining arc could not beat the best found.  Both separations
    use the same incremental feasibility test: a new arc can only lift the
    connectivity of a pair whose source reaches its tail and whose sink is
    reachable from its head, so only those pairs are re-measured, with
    :func:`_arc_flow_at_least` or :func:`_vertex_flow_at_least` according to the
    separation.  Returns ``(max_count, witness, completed)``; ``completed`` is
    False if the time budget ran out first, leaving the value a lower bound.
    Pass ``stats`` to receive the number of search-tree nodes visited.
    """
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    total = len(pairs)
    out: list[set[int]] = [set() for _ in range(n)]
    inc: list[set[int]] = [set() for _ in range(n)]
    # Seed the best at one below a known construction so the bound prune bites
    # immediately, and the search still records an actual witness when it ties it.
    # The same seed is valid in both separations: by Whitney's inequality
    # kappa <= lambda, a digraph feasible for the arc problem is feasible for the
    # vertex problem too, so an arc construction is an honest vertex lower bound.
    seed = _directed_witness(n, m, simple=True)
    seed_value = seed.edge_count() if seed is not None else 0
    best_count = [max(0, seed_value - 1)]
    best_arcs: list[tuple[int, int]] = []
    timed_out = [False]

    def reaches_to(target: int) -> set[int]:
        seen, stack = {target}, [target]   # reverse reachability (can reach t)
        while stack:
            x = stack.pop()
            for y in inc[x]:
                if y not in seen:
                    seen.add(y); stack.append(y)
        return seen

    def reaches_from(source: int) -> set[int]:
        seen, stack = {source}, [source]   # forward reachability (s can reach)
        while stack:
            x = stack.pop()
            for y in out[x]:
                if y not in seen:
                    seen.add(y); stack.append(y)
        return seen

    flow_at_least = (_arc_flow_at_least if separation == "edge"
                     else _vertex_flow_at_least)

    def feasible_after(u: int, v: int) -> bool:
        for s in reaches_to(u):
            for t in reaches_from(v):
                if s != t and flow_at_least(out, n, s, t, m):
                    return False           # this pair reached m disjoint paths
        return True

    def recurse(idx: int, count: int) -> None:
        if stats is not None:
            stats["nodes"] = stats.get("nodes", 0) + 1
        if time.time() > deadline:
            timed_out[0] = True
            return
        if count + (total - idx) <= best_count[0]:
            return                         # cannot beat the incumbent: prune
        if idx == total:
            if count > best_count[0]:
                best_count[0] = count
                best_arcs[:] = [(a, b) for a in range(n) for b in out[a]]
            return
        u, v = pairs[idx]
        out[u].add(v); inc[v].add(u)       # include the arc, if still feasible
        if feasible_after(u, v):
            recurse(idx + 1, count + 1)
        out[u].discard(v); inc[v].discard(u)
        if timed_out[0]:
            return
        recurse(idx + 1, count)            # exclude the arc

    recurse(0, 0)
    witness = None
    if best_arcs:
        witness = Graph(n, SIMPLE_DIRECTED)
        for (a, b) in best_arcs:
            witness.mu[a, b] = 1
    elif seed is not None:
        witness = seed                     # max equalled the seed construction
    # A completed search always reaches at least the seed's count, so the max
    # below only matters on a timeout before any recorded leaf: there it lifts
    # the reported lower bound from seed_value - 1 (the pruning incumbent) to
    # the seed witness's own arc count, keeping value and witness consistent.
    return max(best_count[0], seed_value), witness, not timed_out[0]


def solve(
    n: int, m: int, *,
    directed: bool = False, simple: bool = True,
    hypergraph: bool = False, r: int = 3,
    exhaustive: bool = False, separation: str = "edge",
    max_seconds: float = 60.0, seed: int = 0, method: str | None = None,
) -> SolveResult:
    """The single driver: prove the exact value, or discover a dense example.

    Matrix-model discovery defaults to tabu search: it is the stronger engine on
    the harder directed problems and the one used to solve the problems in this
    work.  Simulated annealing (``method="sa"``) is kept as an independent
    cross-check.  Hypergraph discovery uses its separate randomised greedy engine;
    select it explicitly with ``method="random-greedy"`` or leave ``method=None``.

    Args:
        n, m: the vertices and the forbidden number of independent routes.
        directed, simple: the direction and multiplicity axes.  Both apply to
            the hypergraph model too: ``simple=False`` there means a
            multihypergraph, where a hyperedge may be repeated up to ``m - 1``
            times.  That is a genuinely different problem from the simple one,
            not a relabelling, since repeated hyperedges change which values are
            attainable (``prop:hyper-edge``).
        hypergraph, r: switch to the ``r``-uniform hypergraph model instead.
        exhaustive: ``True`` to PROVE the optimum, ``False`` to DISCOVER one.
        separation: ``"edge"`` or ``"vertex"`` disjointness (matrix models).
            ``simple=False`` with ``separation="vertex"`` is REDUCED to the
            simple problem on the underlying graph, because those two variants
            are posed with the objective counting adjacencies rather than edges
            with multiplicity (``sec:parallel-convention``).  The returned value
            is therefore an adjacency count and the witness is a simple graph;
            ``SolveResult.note`` and ``.variant`` both say so.
        max_seconds: wall-clock budget.  The engines poll it at their natural
            loop boundaries (the annealer and blind enumerators do so in small
            batches), so the final batch may overrun it.
        seed: random seed for the discovery searches.
        method: discovery engine.  ``None`` selects tabu search for matrix models
            and randomised greedy search for hypergraphs; the explicit alternatives
            are ``"sa"``, ``"tabu"``, and ``"random-greedy"`` in their respective
            models.  It is ignored in exhaustive mode.

    Returns:
        A :class:`SolveResult` whose ``bound`` is ``"exact"`` (proved),
        ``"lower"`` (a witness), or ``"upper"`` (proved, no matching witness).
    """
    if separation not in ("edge", "vertex"):
        raise ValueError("separation must be 'edge' or 'vertex'")

    start = time.time()
    deadline = start + max_seconds

    # ----- the hypergraph model --------------------------------------------
    # Same driver, a different internal measure: the edge/vertex separation and
    # the direction pick which of the four Berge measures decides feasibility.
    if hypergraph:
        vertex_split = (separation == "vertex")
        label = (f"{r}-uniform {'directed ' if directed else ''}"
                 f"{'' if simple else 'multi'}hypergraph")
        if exhaustive:
            value, witness, done = _brute_force_hypergraph(
                n, r, m, deadline, directed=directed, vertex_split=vertex_split,
                simple=simple)
            bound = "exact" if done else "lower"
            method = "brute-force enumeration"
            note = "" if done else "budget ran out; value is only a lower bound"
        else:
            if method not in (None, "random-greedy"):
                raise ValueError(
                    "hypergraph discovery uses method='random-greedy'; "
                    "'sa' and 'tabu' are matrix-model methods")
            value, witness = _random_hypergraph_search(
                n, r, m, deadline, seed, directed=directed,
                vertex_split=vertex_split, simple=simple)
            bound, done, method = "lower", False, "randomised greedy search"
            note = "discovery only ever yields a lower bound"
        return SolveResult(n, m, label, separation, value, bound, method,
                           time.time() - start, done, witness, note)

    # ----- the matrix models -----------------------------------------------
    # The two MULTIGRAPH VERTEX variants are posed with the objective counting
    # ADJACENCIES, not edges with multiplicity (sec:parallel-convention).  The
    # reason is that a parallel copy never raises kappa, so it never breaks
    # feasibility either: counted with multiplicity the maximum would simply be
    # infinite and the question empty.  Under the adjacency reading the problem
    # IS the simple problem on the underlying graph, so we solve that instead.
    # Without this reduction the driver would optimise Graph.edge_count(), which
    # counts multiplicity, and report (m-1) times the real answer with a witness
    # whose parallel copies contribute nothing.
    reduced_to_simple = (not simple) and separation == "vertex"
    if reduced_to_simple:
        simple = True
    variant = _variant_for(directed, simple)
    label = variant.describe()
    reduction_note = (
        "multigraph vertex variant: the objective counts adjacencies "
        "(sec:parallel-convention), so this is the simple problem on the "
        "underlying graph" if reduced_to_simple else "")
    if reduced_to_simple:
        label = f"{label} (multigraph vertex, reduced)"

    # DISCOVER: search within the budget; the witness found is a lower bound.
    if not exhaustive:
        selected_method = "tabu" if method is None else method
        if selected_method not in ("sa", "tabu"):
            raise ValueError("method must be 'sa' or 'tabu'")
        result = _search_within_budget(
            variant, n, m, separation, deadline, seed, selected_method)
        method_label = ("tabu search" if selected_method == "tabu"
                        else "simulated annealing")
        return SolveResult(
            n, m, label, separation, result.best_edge_count, "lower",
            method_label, time.time() - start, False,
            result.best_graph, _joined_note(
                "discovery only ever yields a lower bound", reduction_note))

    # EXHAUSTIVE, simple directed: a pruned exhaustive digraph search is exact.
    # This is the prover for the m=2 base cases of the directed theorem, and it
    # reaches n = 6, 7 where the cut-counting cannot close the gap in any sane time.
    if directed and simple:
        value, witness, done = _exhaustive_directed(n, m, separation, deadline)
        bound = "exact" if done else "lower"
        method = "exhaustive digraph search (branch and bound)"
        note = _joined_note(
            "" if done else "budget ran out; value is only a lower bound",
            reduction_note)
        return SolveResult(n, m, label, separation, value, bound, method,
                           time.time() - start, done, witness, note)

    # Directed MULTIGRAPH arc problem: the general hand theorem gives the exact
    # value directly.  The historical cut-counting routine remains available as
    # an independent finite solver check, but solve() does not promote its status
    # string to a replayable certificate.
    if directed and separation == "edge":
        value = directed_multigraph_arc(n, m)
        witness = _directed_witness(n, m, simple)
        if witness is None:
            raise RuntimeError(
                f"closed form gives {value}, but no named witness was built")
        witness_value = witness.edge_count()
        if witness_value != value:
            raise RuntimeError(
                f"closed form gives {value}, but the named witness has "
                f"{witness_value} arcs")
        return SolveResult(
            n, m, label, separation, value, "exact",
            "closed form (directed multigraph theorem)",
            time.time() - start, True, witness, "")

    # EXHAUSTIVE otherwise (undirected, or vertex separation): brute force.
    value, witness, done = _brute_force_matrix(
        variant, n, m, separation, deadline)
    bound = "exact" if done else "lower"
    method = "brute-force enumeration"
    note = _joined_note(
        "" if done else "budget ran out; value is only a lower bound "
                        "(no cut-counting exists for this case)",
        reduction_note)
    return SolveResult(n, m, label, separation, value, bound, method,
                       time.time() - start, done, witness, note)


######################################################################
##
##  CHAPTER 4 — SYNTHESIS AND RESULTS
##  Sampling the random model, the thesis figures, and the self-check.
##
######################################################################

# --- MONTE CARLO: sample G(n,p) graphs, measure with exact checker, average ---


def sample_random_graph(n: int, p: float, directed: bool, rng: random.Random) -> Graph:
    """Draw one sample of $G(n, p)$ (or the random digraph $D(n, p)$).

    Each possible edge is included independently with probability ``p``: unordered
    pairs for an undirected graph, ordered pairs for a digraph.
    """
    variant = SIMPLE_DIRECTED if directed else SIMPLE_UNDIRECTED
    graph = Graph(n, variant)
    for u in range(n):
        # Undirected: scan v > u (each pair once). Directed: scan all v.
        start = 0 if directed else u + 1
        for v in range(start, n):
            if u != v and rng.random() < p:  # include this edge with prob p
                graph.add_edge(u, v)
    return graph


def estimate_appearance_probability(
    n: int, p: float, m: int, *, trials: int = 200,
    separation: str = "edge", directed: bool = False, seed: int = 0,
) -> float:
    """Estimate the probability that a sample has $\\lambda^{\\max} \\ge m$."""
    rng = random.Random(seed)
    measure = _connectivity_measure(separation)
    # Count the fraction of samples that already exhibit m independent routes
    # somewhere (lambda^max >= m): the empirical appearance probability.
    appearances = sum(
        measure(sample_random_graph(n, p, directed, rng)) >= m
        for _ in range(trials)
    )
    return appearances / trials


def connectivity_distribution(
    n: int, p: float, *, trials: int = 200,
    separation: str = "edge", directed: bool = False, seed: int = 0,
) -> list[int]:
    """Return the list of $\\lambda^{\\max}$ (or $\\kappa^{\\max}$) over samples.

    Same arguments as the estimators above. The returned list has one entry per
    sample, so its histogram shows how the binding connectivity is distributed
    for that kind of graph. Calling this with the same ``seed`` and ``(n, p)``
    but different ``separation`` reuses the very same random graphs, which is why
    the edge and vertex distributions can be compared sample by sample.
    """
    rng = random.Random(seed)
    measure = _connectivity_measure(separation)
    # Same seed + same (n, p) reproduces the identical sequence of graphs, so an
    # edge run and a vertex run can be compared sample by sample (Whitney check).
    return [measure(sample_random_graph(n, p, directed, rng)) for _ in range(trials)]


@dataclass
class ThresholdCurve:
    """The appearance probability sampled across a range of densities."""

    n: int
    m: int
    probabilities: list[tuple[float, float]]  # (p, estimated probability)

    @property
    def predicted_threshold(self) -> float:
        """The expected-degree balance point ``m/n`` for undirected ``G(n,p)``.

        It is a proved threshold only when ``m / log(n)`` tends to infinity.
        No threshold claim is made here for directed or hypergraph models.
        """
        return self.m / self.n


def threshold_curve(
    n: int, m: int, p_values: list[float], *, trials: int = 200,
    separation: str = "edge", directed: bool = False, seed: int = 0,
) -> ThresholdCurve:
    """Sweep ``p`` and return the appearance probability at each value."""
    points = [
        (p, estimate_appearance_probability(
            n, p, m, trials=trials, separation=separation, directed=directed, seed=seed))
        for p in p_values
    ]
    return ThresholdCurve(n=n, m=m, probabilities=points)


# --- edge against vertex disjointness in the random model --------------------
#
# Whitney's inequality kappa^max <= lambda^max leaves open whether the two
# binding connectivities of a graph actually differ.  For the EXTREMAL problem
# they first part company at m = 5 (Sorensen-Thomassen).  The function below lets
# the same split be watched in the random model: it draws samples of G(n, p) and
# measures both maxima on each one.  On small graphs, where the binding
# connectivity stays at or below four, the two coincide on every sample; on
# larger, denser graphs, where it climbs past five, a pair can carry more
# edge-disjoint routes than internally vertex-disjoint ones, and kappa^max drops
# below lambda^max on a growing fraction of samples.


def edge_vertex_distribution(
    n: int, p: float, *, trials: int = 300, seed: int = 0,
) -> tuple[list[int], list[int]]:
    """Return paired (lambda^max, kappa^max) over the same samples of G(n, p).

    Both lists are measured on the identical sequence of random graphs, because
    connectivity_distribution reuses the seed, so the two can be compared sample
    by sample: the fraction of entries with kappa^max < lambda^max is exactly how
    often vertex disjointness is strictly more demanding than edge disjointness
    at that size and density.
    """
    lambda_max = connectivity_distribution(
        n, p, trials=trials, separation="edge", seed=seed)
    kappa_max = connectivity_distribution(
        n, p, trials=trials, separation="vertex", seed=seed)
    return lambda_max, kappa_max


# --- SAMPLING ALL VARIANTS: Bernoulli for simple/hypergraph, hurdle-geometric for multigraph ---


def sample_random_multigraph(
    n: int, p: float, alpha: float, directed: bool, rng: random.Random,
    *, cap: int | None = None,
) -> Graph:
    """Random multigraph with hurdle-geometric edge multiplicities.

    Each cell is empty with probability ``1 - p``; otherwise it carries one copy
    plus a Geometric(``alpha``) number of further copies, so the multiplicity
    decays exponentially with rate ``alpha`` and ``alpha = 0`` recovers simple
    ``G(n, p)``.  With ``cap`` set (use ``m - 1``) a single fat edge cannot
    trivially break feasibility, so the panel stays a structural question.
    """
    variant = MULTI_DIRECTED if directed else MULTI_UNDIRECTED
    graph = Graph(n, variant)
    for u in range(n):
        start = 0 if directed else u + 1
        for v in range(start, n):
            if u == v or rng.random() >= p:
                continue
            k = 1
            while rng.random() < alpha:
                k += 1
            graph.set_multiplicity(u, v, k if cap is None else min(k, cap))
    return graph


def sample_random_hypergraph(
    n: int, p: float, r: int, directed: bool, rng: random.Random,
) -> Hypergraph:
    """Random ``r``-uniform hypergraph: each candidate hyperedge included w.p. ``p``."""
    chosen = [c for c in _hyperedge_candidates(n, r, directed) if rng.random() < p]
    return Hypergraph(n, chosen, directed=directed)


def _sample_variant(n, p, *, directed, simple, hypergraph, r, alpha, cap, rng):
    """Draw one sample of whichever generative model the flags select."""
    if hypergraph:
        return sample_random_hypergraph(n, p, r, directed, rng)
    if simple:
        return sample_random_graph(n, p, directed, rng)
    return sample_random_multigraph(n, p, alpha, directed, rng, cap=cap)


def _measure_variant(obj, *, separation, hypergraph):
    """Binding connectivity of a sampled object under the chosen separation."""
    if hypergraph:
        return max_hyper_connectivity(obj, vertex_split=(separation == "vertex"))
    return _connectivity_measure(separation)(obj)


def _mean_binding_degree(obj, *, directed, hypergraph):
    """The degree that the degree bound caps connectivity by, averaged over vertices.

    Undirected: total incident multiplicity.  Directed: ``min(d^+, d^-)`` (the
    quantity bounding an arc-disjoint count).  Hypergraph: the Berge degree, the
    number of hyperedges through a vertex.
    """
    n = obj.num_vertices
    if hypergraph:
        deg = [0] * n
        for edge in obj.hyperedges:
            for v in obj.members(edge):
                deg[v] += 1
        return sum(deg) / n
    if directed:
        return sum(min(obj.out_degree(v), obj.in_degree(v)) for v in range(n)) / n
    return sum(obj.degree(v) for v in range(n)) / n


def _p_for_target_degree(target_deg, n, *, directed, simple, hypergraph, r, alpha):
    """Presence probability ``p`` that puts the expected degree near ``target_deg``.

    Only an aiming heuristic -- the figures plot the *measured* mean degree -- so
    the exact value of the cap or of the geometric tail does not need inverting.
    """
    if hypergraph:
        per_vertex = math.comb(n - 1, r - 1)
        if directed:
            per_vertex += (n - 1) * math.comb(n - 2, r - 2)
        return min(1.0, target_deg / max(per_vertex, 1))
    copies = 1.0 if simple else 1.0 / (1.0 - alpha)
    return min(1.0, target_deg / ((n - 1) * copies))


# Twelve sampled panels, mirroring _VARIANT_ENUM_CONFIGS but at sampling sizes
# well past the enumeration wall (n=6).  ``sample_n`` is chosen per variant so
# the binding-connectivity sweep stays a few minutes overall.
_VARIANT_SAMPLE_CONFIGS: list[dict] = [
    dict(key="simple_undirected_edge",   title="simple undirected edge",
         directed=False, simple=True,  hypergraph=False, r=3, separation="edge",  sample_n=26),
    dict(key="simple_undirected_vertex", title="simple undirected vertex",
         directed=False, simple=True,  hypergraph=False, r=3, separation="vertex", sample_n=18),
    dict(key="simple_directed_edge",     title="simple directed arc",
         directed=True,  simple=True,  hypergraph=False, r=3, separation="edge",  sample_n=14),
    dict(key="simple_directed_vertex",   title="simple directed vertex",
         directed=True,  simple=True,  hypergraph=False, r=3, separation="vertex", sample_n=14),
    dict(key="multi_undirected_edge",    title="multigraph undirected edge",
         directed=False, simple=False, hypergraph=False, r=3, separation="edge",  sample_n=22),
    dict(key="multi_undirected_vertex",  title="multigraph undirected vertex",
         directed=False, simple=False, hypergraph=False, r=3, separation="vertex", sample_n=16),
    dict(key="multi_directed_edge",      title="multigraph directed arc",
         directed=True,  simple=False, hypergraph=False, r=3, separation="edge",  sample_n=12),
    dict(key="multi_directed_vertex",    title="multigraph directed vertex",
         directed=True,  simple=False, hypergraph=False, r=3, separation="vertex", sample_n=12),
    dict(key="hyper_undirected_edge",    title="hypergraph undirected edge",
         directed=False, simple=True,  hypergraph=True,  r=3, separation="edge",  sample_n=12),
    dict(key="hyper_undirected_vertex",  title="hypergraph undirected vertex",
         directed=False, simple=True,  hypergraph=True,  r=3, separation="vertex", sample_n=12),
    dict(key="hyper_directed_edge",      title="hypergraph directed arc",
         directed=True,  simple=True,  hypergraph=True,  r=3, separation="edge",  sample_n=9),
    dict(key="hyper_directed_vertex",    title="hypergraph directed vertex",
         directed=True,  simple=True,  hypergraph=True,  r=3, separation="vertex", sample_n=9),
]


# --- FIGURES: headless matplotlib PNGs; each function takes a path and writes a file ---

_KUL_BLUE = "#1D8DB0"    # feasible / proved
_KUL_DARK = "#1E6E87"    # row labels, known-max lines
_KUL_LIGHT = "#52BDEC"   # named branches
_WARM = "#DC8C28"        # feasibility boundary, certain interval
_RED = "#E05050"         # infeasible bars
_GREEN = "#3CA050"       # machine-checked exact markers
_VIOLET = "#9B5DE5"      # search lower-bound markers
_GUESS = "#E6B800"       # "guess" interpolation: a clear yellow/gold, kept well
                         # apart from the red conjecture curve (proved=blue,
                         # conjectured=red, guess=yellow)

# Four-level sensitivity palette: cool (sigma=0) -> hot (sigma=max).
_SIGMA_PALETTE = ["#52BDEC", "#F9C74F", "#F4914B", "#DC8C28"]  # 0,1,2,3+


def plot_directed_crossover(m: int, max_n: int, path: str | Path) -> None:
    """Plot the two competing directed branches and their maximum versus ``n``.

    Shows how the linear hub branch ``m(n-1)`` is overtaken by the quadratic
    augmented-bipartite branch.  Before floors, the upper crossover is
    ``n = m + 2 + 2*sqrt(m)``, hence ``n ~ m`` for growing ``m``.
    """
    ns = list(range(2, max_n + 1))
    hub = [m * (n - 1) for n in ns]                         # linear hub branch
    # Quadratic branch: the shifted-partition augmented bipartite count
    # floor((n+m-2)^2/4) of const:augmented-bipartite (at m <= 3 it equals the
    # balanced-partition count floor(n^2/4) + (m-2)ceil(n/2)).
    bipartite = [((n + m - 2) ** 2) // 4 for n in ns]
    envelope = [directed_arc_lower_bound(n, m) for n in ns]  # their pointwise max

    # Printed-size note: this figure is rendered at close to the width the
    # thesis actually gives it, so the point sizes below survive to paper
    # unshrunk. Enlarging the canvas here shrinks the labels in print.
    plt.figure(figsize=(4.6, 3.3))
    plt.plot(ns, hub, "--", color=_KUL_DARK, label=r"hub branch $m(n-1)$")
    plt.plot(ns, bipartite, "--", color=_WARM,
             label=r"bipartite branch $\lfloor (n+m-2)^2/4\rfloor$")
    plt.plot(ns, envelope, "-", color=_KUL_BLUE, linewidth=2.4, label="their maximum")

    # Mark the crossover: the first n at which the quadratic branch overtakes the
    # linear one, the order (linear in m) where the directed story changes hands.
    cross_n = next((n for n, h, b in zip(ns, hub, bipartite) if b > h), None)
    if cross_n is not None:
        y_cross = directed_arc_lower_bound(cross_n, m)
        plt.axvline(cross_n, color="gray", linestyle=":", linewidth=1.3, alpha=0.8)
        plt.scatter([cross_n], [y_cross], color=_KUL_BLUE, zorder=5,
                    s=45, edgecolor="white", linewidth=0.8)
        plt.annotate(f"crossover at $n = {cross_n}$",
                     xy=(cross_n, y_cross),
                     xytext=(cross_n - 2.8, max(envelope) * 0.48),
                     fontsize=9.5, color="black", ha="center",
                     arrowprops=dict(arrowstyle="->", color="gray", lw=1.1))

    plt.xlabel("number of vertices $n$")
    plt.ylabel("arcs")
    plt.title(f"Directed lower bound at $m = {m}$")
    plt.legend(loc="upper left")
    plt.grid(True, alpha=0.3)
    _save(path)


def plot_edge_vertex_divergence(max_n: int, path: str | Path) -> None:
    """Show agreement through m<=4 and divergence at m=5, all starting at the same n.

    All curves begin at n_start so the reader can compare directly.
    For m=2,3,4 the two problems coincide (one line each, blue shades).
    At m=5 they part: edge below, vertex above, with the gap shaded.
    """
    n_start = 4  # common start for all curves
    ns = list(range(n_start, max_n + 1))

    # Printed-size note: this figure is rendered at close to the width the
    # thesis actually gives it, so the point sizes below survive to paper
    # unshrunk. Enlarging the canvas here shrinks the labels in print.
    plt.figure(figsize=(6.2, 3.9))

    # m=2,3,4: edge == vertex -- one curve per m
    agree_palette = ["#AED9EE", "#5CB4D9", _KUL_DARK]
    for m_val, color in zip([2, 3, 4], agree_palette):
        vals = [simple_undirected_edge(n, m_val) for n in ns]
        plt.plot(ns, vals, "-", color=color, linewidth=1.8, alpha=0.9,
                 label=f"$m={m_val}$: edge $=$ vertex")

    # m=5: edge and vertex.  Sorensen-Thomassen only determine k_5 from n = 6,
    # so the vertex curve starts there rather than at n_start.  The two agree
    # for every n <= 13 and first come apart at n = 14, which is what the
    # shading marks.
    ns5 = [n for n in ns if n >= 6]
    edge5 = [simple_undirected_edge(n, 5) for n in ns5]
    vert5 = [simple_undirected_vertex_m5(n) for n in ns5]
    plt.plot(ns5, edge5, "--", color=_KUL_BLUE, linewidth=2.4,
             label=r"$m=5$: edge $\ell_5(n)=\lfloor 5(n-1)/2\rfloor$")
    plt.plot(ns5, vert5, "-",  color=_WARM,     linewidth=2.4,
             label=r"$m=5$: vertex $k_5(n)=\lfloor 8n/3\rfloor-4$ "
                   r"($n\neq7,12$)")
    # shade only where the gap is positive
    plt.fill_between(ns5, edge5, vert5, where=[v > e for v, e in zip(vert5, edge5)],
                     alpha=0.15, color=_WARM)

    plt.xlabel("number of vertices $n$")
    plt.ylabel("maximum edges")
    plt.title("Agreement through $m \\leq 4$, first divergence at $m = 5$")
    plt.legend(fontsize=9, loc="upper left")
    plt.grid(True, alpha=0.3)
    _save(path)


# NOTE: plot_degree_threshold generated the 2-D random-sampling threshold figure
# (the old Figure 4.2) removed from the thesis on 2026-06-20.  Kept here so the
# threshold phenomenon can be restored; see
# research_notes/removed_threshold_phenomenon.md for the recipe.  (Its 3-D
# companion plot_conn_threshold_3d is still used, for the appendix.)
def plot_degree_threshold(
    path: str | Path, *, n: int = 12, m: int = 4, alpha: float = 0.5,
    trials: int = 70, seed: int = 7,
    targets=(0.3, 0.5, 0.65, 0.8, 0.95, 1.1, 1.3, 1.6, 2.0),
) -> None:
    """Appearance probability against mean binding-degree, across every model.

    Six random models -- simple, multigraph and $3$-uniform hypergraph, each
    undirected and directed -- are swept in density and plotted by their
    *measured* mean binding degree (in units of ``m``) against the probability
    that a sample already contains a pair of (Berge) edge-connectivity at least
    ``m``.  The vertical line at degree ``= m`` is the asymptotic threshold the
    degree argument of thm:gnp-threshold predicts; at the fixed small ``m`` a
    computation can reach the curves are ORDERED rather than coincident -- a
    directed multigraph forces the pair at the least degree (heavy parallel edges
    concentrate connectivity), a directed hypergraph at the most (a hyperedge
    serves only one Berge route), with the simple cases between.  Universality is
    the ``m/ln n -> infinity`` limit; the spread here is the finite-m gap.
    """
    models = [
        ("simple, undirected",        dict(directed=False, simple=True,  hypergraph=False, r=3), _KUL_LIGHT, "o", "-"),
        ("simple, directed",          dict(directed=True,  simple=True,  hypergraph=False, r=3), _KUL_BLUE,  "s", "-"),
        ("multigraph, undirected",    dict(directed=False, simple=False, hypergraph=False, r=3), _WARM,      "o", "--"),
        ("multigraph, directed",      dict(directed=True,  simple=False, hypergraph=False, r=3), "#C0392B",  "s", "--"),
        ("$3$-uniform hyper, undir.", dict(directed=False, simple=True,  hypergraph=True,  r=3), _VIOLET,    "^", ":"),
        ("$3$-uniform hyper, dir.",   dict(directed=True,  simple=True,  hypergraph=True,  r=3), _GREEN,     "^", ":"),
    ]
    plt.figure(figsize=(7.8, 5.0))
    for label, spec, colour, mk, ls in models:
        xs, ys = [], []
        for t in targets:
            p = _p_for_target_degree(t * m, n, alpha=alpha, **spec)
            rng = random.Random(seed)
            degs, hits = [], 0
            for _ in range(trials):
                obj = _sample_variant(n, p, alpha=alpha, cap=m - 1, rng=rng, **spec)
                degs.append(_mean_binding_degree(
                    obj, directed=spec["directed"], hypergraph=spec["hypergraph"]))
                if _measure_variant(obj, separation="edge",
                                    hypergraph=spec["hypergraph"]) >= m:
                    hits += 1
            xs.append(sum(degs) / len(degs) / m)
            ys.append(hits / trials)
        plt.plot(xs, ys, ls, marker=mk, color=colour, markersize=4.5,
                 linewidth=1.8, label=label)
    plt.axvline(1.0, color="black", linestyle="--", linewidth=1.6,
                label=r"asymptotic threshold (degree $= m$)")
    plt.axhline(0.5, color="gray", linestyle=":", linewidth=1.0, alpha=0.6)
    plt.xlabel(r"mean binding degree, in units of $m$")
    plt.ylabel(r"$\hat{P}\,[\,\text{binding connectivity} \geq m\,]$")
    plt.title(f"Appearance vs expected degree, by model "
              f"($n = {n}$, $m = {m}$, multiplicities capped at $m-1$)")
    plt.ylim(-0.03, 1.03)
    plt.legend(fontsize=8.5, loc="lower right")
    plt.grid(True, alpha=0.3)
    _save(path)


_FRACTION_LABEL = {0.25: "1/4", 0.5: "1/2", 0.75: "3/4"}


def plot_edge_vertex_histograms(
    data: dict[float, tuple[list[int], list[int]]],
    n: int,
    p_values: list[float],
    path: str | Path,
) -> None:
    """Six histograms of the binding connectivity in $G(n, p)$, at one size $n$.

    ``data`` maps each density ``p`` to a pair ``(lambda_max_values,
    kappa_max_values)`` measured on the same samples, from
    :func:`montecarlo.edge_vertex_distribution`.  The grid is two rows by three
    columns: the top row is the edge-connectivity ``lambda^max`` and the bottom
    row the vertex-connectivity ``kappa^max``, one column per density.  Reading a
    column top to bottom compares the two distributions at a fixed density, so
    Whitney's inequality shows up as the vertex histogram sitting at or to the
    left of the edge one.  The fraction of samples with ``kappa^max <
    lambda^max`` is printed on each vertex panel.  All six share one axis range.
    """
    rows = [(r"edge $\lambda^{\max}$", 0, _KUL_BLUE),
            (r"vertex $\kappa^{\max}$", 1, _WARM)]
    all_values = [v for p in p_values for series in data[p] for v in series]
    lo, hi = min(all_values), max(all_values)
    bins = range(lo, hi + 2)  # one integer-wide bin per connectivity value
    trials = len(data[p_values[0]][0])

    fig, axes = plt.subplots(2, len(p_values), figsize=(11, 6),
                             sharex=True, sharey=True)
    for col, p in enumerate(p_values):
        lam, kap = data[p]
        gap = 100 * sum(k < l for k, l in zip(kap, lam)) / len(lam)
        plabel = _FRACTION_LABEL.get(p, f"{p:.2f}")
        for label, ridx, colour in rows:
            axis = axes[ridx][col]
            values = lam if ridx == 0 else kap
            axis.hist(values, bins=bins, align="left", color=colour,
                      edgecolor="white", linewidth=0.4, rwidth=0.9)
            axis.axvline(statistics.mean(values), color="black", linestyle="--",
                         linewidth=1.2)
            if ridx == 0:
                axis.set_title(f"$p = {plabel}$")
            else:
                axis.set_xlabel("binding connectivity")
                axis.text(0.03, 0.92, fr"$\kappa\!<\!\lambda$: {gap:.0f}%",
                          transform=axis.transAxes, ha="left", va="top",
                          fontsize=9, color=_WARM)
            if col == 0:
                axis.set_ylabel(f"{label}\nsamples")
            axis.grid(True, axis="y", alpha=0.3)

    fig.suptitle(fr"Distribution of the binding connectivity in $G({n},p)$ "
                 fr"over {trials} samples", fontsize=12)
    _save(path)


def plot_search_trace(result: SearchResult, path: str | Path,
                      optimum: int | None = None,
                      ceiling: int | None = None,
                      *,
                      show_cooling: bool = True,
                      show_histogram: bool = True,
                      connectivity_label: str = r"$\lambda^{\max}$",
                      edge_label: str = "arcs",
                      title: str = "Cooling toward an extremal graph") -> None:
    """Plot the search trajectory; optionally include the cooling schedule.

    Layout: [cooling schedule (optional)] | [scatter] | [visit histogram].

    The scatter colours points by step number with a heavily nonlinear
    PowerNorm (gamma=0.2, RdYlBu colourmap) so that only the brief hot
    exploration phase (early steps) stands out in warm reds/yellows, while
    the long converged tail is uniformly blue.  When ``ceiling`` is given the
    feasibility boundary is marked and "feasible"/"infeasible" labels are
    placed just above the axes box using a blended data/axes transform, so
    they sit centred over their respective shaded regions regardless of zoom.

    The rightmost panel is an optional horizontal density histogram showing how
    many search steps landed at each edge-count level; it shares the y-axis with
    the scatter so the bars align with the dots.

    New keyword arguments (all optional, all have sensible defaults):
    - ``show_cooling``: set False to omit the left cooling-schedule panel.
    - ``show_histogram``: set False to omit the right visit-density panel.
    - ``connectivity_label``: x-axis label for the scatter (default lambda^max).
    - ``edge_label``: y-axis label (default "arcs"; use "edges" for undirected).
    - ``title``: figure suptitle.
    """

    steps = [record.step for record in result.history]
    temperature = [record.temperature for record in result.history]
    edges = [record.edge_count for record in result.history]
    connectivity = [record.connectivity for record in result.history]

    # Build layout: cooling (optional) | scatter | histogram (optional).
    # Histogram axes use no sharey — that avoids a tight_layout warning, so the
    # y-limits are synced to the scatter manually after it is fully drawn.
    if show_cooling and show_histogram:
        fig = plt.figure(figsize=(13.5, 4.8))
        gs = GridSpec(1, 3, figure=fig, width_ratios=[1.0, 1.6, 0.28],
                      wspace=0.40)
        ax_cool = fig.add_subplot(gs[0])
        ax_scat = fig.add_subplot(gs[1])
        ax_hist = fig.add_subplot(gs[2])
    elif show_cooling and not show_histogram:
        fig = plt.figure(figsize=(11.5, 4.8))
        gs = GridSpec(1, 2, figure=fig, width_ratios=[1.0, 1.6], wspace=0.40)
        ax_cool = fig.add_subplot(gs[0])
        ax_scat = fig.add_subplot(gs[1])
        ax_hist = None
    elif (not show_cooling) and show_histogram:
        fig = plt.figure(figsize=(8.5, 4.8))
        gs = GridSpec(1, 2, figure=fig, width_ratios=[1.6, 0.28], wspace=0.12)
        ax_cool = None
        ax_scat = fig.add_subplot(gs[0])
        ax_hist = fig.add_subplot(gs[1])
    else:
        fig = plt.figure(figsize=(6.6, 4.8))
        ax_cool = None
        ax_scat = fig.add_subplot(1, 1, 1)
        ax_hist = None

    # Left: cooling schedule.
    if ax_cool is not None:
        ax_cool.plot(steps, temperature, color=_WARM, linewidth=1.8)
        ax_cool.set_xlabel("step")
        ax_cool.set_ylabel("temperature")
        ax_cool.set_title("Cooling schedule")
        ax_cool.grid(True, alpha=0.3)

    # Middle: scatter of (connectivity, edge_count), coloured by step.
    ax = ax_scat
    lo = min(connectivity) - 0.5
    hi = max(connectivity) + 0.5
    if ceiling is not None:
        boundary = ceiling + 0.5
        ax.axvspan(lo, boundary, color=_GREEN, alpha=0.10)
        ax.axvspan(boundary, hi, color=_RED, alpha=0.10)
        ax.axvline(boundary, color=_WARM, linestyle="--", linewidth=1.4)
        ax.set_xlim(lo, hi)
        # Labels centred over each shaded region, placed just above the axes box.
        # blended_transform mixes data-x (tracks the region) with axes-fraction-y
        # (1.03 is always just above the top of the box regardless of zoom level).
        xt = blended_transform_factory(ax.transData, ax.transAxes)
        ax.text((lo + boundary) / 2, 1.03, "feasible",
                transform=xt, ha="center", va="bottom",
                fontsize=8.5, color=_GREEN, fontweight="bold", clip_on=False)
        ax.text((boundary + hi) / 2, 1.03, "infeasible",
                transform=xt, ha="center", va="bottom",
                fontsize=8.5, color="#C03030", fontweight="bold", clip_on=False)

    # Nonlinear colour norm: gamma < 1 squashes large step values toward 1,
    # mapping the long converged tail (most points) to the BLUE end of RdYlBu
    # while only the first few hot steps appear in warm reds and yellows.
    max_step = max(steps) if steps else 1
    norm = PowerNorm(gamma=0.2, vmin=0, vmax=max_step)
    sc = ax.scatter(connectivity, edges, c=steps, cmap="RdYlBu",
                    norm=norm, s=16, alpha=0.75, linewidths=0)

    if optimum is not None:
        ax.axhline(optimum, color=_KUL_DARK, linestyle="--", linewidth=1.4,
                   label=f"certified optimum = {optimum}")
    if optimum is not None and ceiling is not None:
        ax.plot([ceiling], [optimum], "*", color="#D11A2A", markersize=20,
                markeredgecolor="white", markeredgewidth=0.9, zorder=5,
                label="densest feasible graph")
    ax.set_xlabel(connectivity_label + " of the visited graph")
    ax.set_ylabel(edge_label)
    # No panel title: the suptitle and the feasible/infeasible labels describe
    # the panel; a panel title would overlap with the labels above the axes box.
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(True, alpha=0.3)
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
    cbar = fig.colorbar(sc, ax=ax, shrink=0.92)
    cbar.set_label(r"step (cooling $\rightarrow$)")
    cbar.set_ticks([0, max_step // 4, max_step // 2,
                    3 * max_step // 4, max_step])

    # Right: horizontal histogram — visit density per edge-count level.
    # Sync y-limits with the scatter manually (avoids tight_layout warning
    # that sharey axes cause inside _save's plt.tight_layout() call).
    if ax_hist is not None:
        visit_counts = Counter(edges)
        arc_vals = sorted(visit_counts)
        ax_hist.barh(arc_vals, [visit_counts[a] for a in arc_vals],
                     height=0.72, color=_KUL_BLUE, alpha=0.75, linewidth=0)
        ax_hist.set_ylim(ax.get_ylim())
        ax_hist.set_xlabel("visits", fontsize=8)
        ax_hist.set_title("Distribution", fontsize=9)
        ax_hist.tick_params(axis="y", left=False, labelleft=False)
        ax_hist.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=3))
        ax_hist.tick_params(labelsize=7)
        ax_hist.grid(True, axis="x", alpha=0.3)

    fig.suptitle(title, fontsize=12, y=1.04)
    _save(path)


def draw_graph_with_sensitivity(
    graph: Graph,
    path: str | Path,
    layout: dict | None = None,
    show_sigma: bool = False,
    node_labels: dict | None = None,
) -> None:
    """Draw a directed multigraph with every parallel arc drawn, coloured by sigma.

    Each parallel copy of an adjacency is rendered as its own curved arc, so the
    multiplicity ``mu(u, v)`` is read by *counting* arcs rather than from a label,
    and the whole adjacency is coloured by its sensitivity ``sigma(e)`` -- how far
    ``lambda^max`` falls when the adjacency is deleted -- on a four-level
    cool-to-hot palette.  An over-provisioned adjacency (several parallel copies
    but a downstream bottleneck) therefore shows as a bundle of arcs in a cool
    colour: the visual point that multiplicity and load-bearing role differ.

    Pass a ``layout`` dict mapping vertex id to (x, y) and a ``node_labels`` dict
    to override the numeric labels.  ``show_sigma`` is accepted for backward
    compatibility and ignored (sigma is always shown).
    """

    sensitivities = sensitivity_map(graph)
    if layout is None:
        # Evenly spaced on the unit circle (the same picture nx.circular_layout
        # draws), computed directly so drawing needs no networkx.
        verts = list(graph.vertices())
        layout = {v: (math.cos(2 * math.pi * i / len(verts)),
                      math.sin(2 * math.pi * i / len(verts)))
                  for i, v in enumerate(verts)}
    labels = (node_labels if node_labels is not None
              else {v: str(v) for v in graph.vertices()})

    # Printed-size note: this figure is rendered at close to the width the
    # thesis actually gives it, so the point sizes below survive to paper
    # unshrunk. Enlarging the canvas here shrinks the labels in print.
    fig, ax = plt.subplots(figsize=(5.4, 3.9))

    for (u, v), sigma in sensitivities.items():
        mu = graph.multiplicity(u, v)
        colour = _SIGMA_PALETTE[min(sigma, len(_SIGMA_PALETTE) - 1)]
        # Symmetric fan of curvatures, one per parallel copy.
        if mu <= 1:
            rads = [0.0]
        else:
            spread = 0.13 * (mu - 1)
            rads = [-spread + 2 * spread * k / (mu - 1) for k in range(mu)]
        for rad in rads:
            ax.add_patch(FancyArrowPatch(
                layout[u], layout[v], connectionstyle=f"arc3,rad={rad}",
                arrowstyle="-|>", mutation_scale=13, lw=2.3, color=colour,
                shrinkA=13, shrinkB=13, zorder=1))
        # One sigma label per adjacency, at the chord midpoint.
        (x0, y0), (x1, y1) = layout[u], layout[v]
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, f"$\\sigma={sigma}$",
                fontsize=9, ha="center", va="center", zorder=3,
                bbox={"boxstyle": "round,pad=0.18", "fc": "white",
                      "ec": colour, "alpha": 0.9})

    xs = [p[0] for p in layout.values()]
    ys = [p[1] for p in layout.values()]
    ax.scatter(xs, ys, s=620, c=_KUL_DARK, edgecolors="white", linewidths=1.2,
               zorder=2)
    for v, (x, y) in layout.items():
        ax.text(x, y, str(labels.get(v, v)), color="white", fontweight="bold",
                ha="center", va="center", zorder=4)

    mx = (max(xs) - min(xs)) * 0.12 + 0.3
    my = (max(ys) - min(ys)) * 0.12 + 0.3
    ax.set_xlim(min(xs) - mx, max(xs) + mx)
    ax.set_ylim(min(ys) - my, max(ys) + my)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Parallel arcs drawn explicitly, coloured by sensitivity "
                 "$\\sigma$:\ncool ($\\sigma=0$, free) $\\to$ warm (load-bearing)",
                 fontsize=12)
    _save(path)


def _running_best_trace(result: SearchResult) -> tuple[list[float], list[int]]:
    """Best feasible edge count so far against wall-clock seconds, from a history.

    Reads the timed :class:`SearchStep` log (its ``best_feasible`` field already
    carries the densest feasible graph seen up to each step) and returns the timed
    convergence curve both engines record in their native fast modes.
    """
    xs = [record.seconds for record in result.history]
    ys = [record.best_feasible for record in result.history]
    return xs, ys


def _settle_time(xs: list[float], ys: list[int]) -> float:
    """Wall-clock second at which a trace first reached its own final best value.

    The convergence curves plateau long before the time budget runs out, so this
    is what the x-axis should track: cropping to the budget would leave a long
    flat tail and the cropped view would barely change when the budget does.
    """
    if not xs:
        return 0.0
    final = ys[-1]
    return next((x for x, y in zip(xs, ys) if y == final), xs[-1])


def plot_sa_vs_tabu_convergence(
    path: str | Path, *,
    cases: tuple[tuple[int, int], ...] = ((5, 3), (7, 3)),
    budget: float = 8.0,
    seed: int = 0,
    xmaxes: tuple[float, ...] | None = None,
    settle_margin: float = 1.3,
) -> None:
    """Best-feasible-value against wall-clock for annealing vs tabu search.

    For each ``(n, m)`` it runs one simulated-annealing schedule
    (:func:`search_for_dense_graph`) and one tabu schedule
    (:func:`tabu_search_for_dense_graph`) on the directed multigraph at an equal
    wall-clock ``budget``, and overlays their timed best-so-far traces against the
    conjectured optimum.  The chosen cases are where the two engines diverge: tabu
    assembles the bipartite extremiser and reaches the optimum while annealing
    plateaus a few arcs short.  The time axis is wall-clock, so this one figure is
    a representative timed run on the reference machine rather than a seed-exact
    reproduction like the others.

    By default each panel's x-axis stops shortly after the slower engine settles
    (``settle_margin`` times the later of the two plateau times), so the view
    tracks the actual run instead of a fixed window: cropping to a hard-coded
    second count leaves a long flat tail because both engines converge well
    inside one second.  Pass ``xmaxes`` to force fixed per-panel limits instead.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise RuntimeError("matplotlib is required for figures")
    fig, axes = plt.subplots(1, len(cases), figsize=(11, 4.3))
    if len(cases) == 1:
        axes = [axes]
    for i, (ax, (n, m)) in enumerate(zip(axes, cases)):
        sa = search_for_dense_graph(MULTI_DIRECTED, n, m, seed=seed, steps=10**7,
                                    deadline=time.time() + budget)
        tb = tabu_search_for_dense_graph(MULTI_DIRECTED, n, m, seed=seed,
                                         steps=10**7, deadline=time.time() + budget)
        settle = 0.0
        for res, label, colour in ((sa, "simulated annealing", _KUL_BLUE),
                                    (tb, "tabu search", _WARM)):
            xs, ys = _running_best_trace(res)
            ax.step(xs, ys, where="post", label=label, color=colour, linewidth=2.0)
            settle = max(settle, _settle_time(xs, ys))
        opt = directed_multigraph_arc(n, m)
        ax.axhline(opt, linestyle=":", color=_KUL_DARK, linewidth=1.6,
                   label=f"optimum $L_3^{{\\mathrm{{dir}}}}({n}) = {opt}$")
        ax.set_title(f"directed multigraph, $n = {n}$, $m = {m}$", fontsize=11)
        ax.set_xlabel("wall-clock seconds", fontsize=9.5)
        ax.set_ylabel("densest feasible arc count", fontsize=9.5)
        # Crop the long flat tail: stop just after the slower engine settles, so
        # the rise fills the panel instead of being squeezed against the y-axis.
        # A fixed second count cannot do this, since the settle time shifts run to
        # run; an explicit xmaxes overrides for a reproducible fixed window.
        if xmaxes is not None and i < len(xmaxes):
            ax.set_xlim(0, xmaxes[i])
        else:
            ax.set_xlim(0, max(settle * settle_margin, 0.5))
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8.5, loc="lower right")
        # Fewer x-ticks declutters the time axis: the action concentrates early
        # and dense ticks add noise.
        if MaxNLocator is not None:
            ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
    _save(path)


def _save(path: str | Path, *, tight: bool = True,
          bbox_tight: bool = True) -> None:
    """Tighten the layout, write the file, and close the figure.

    ``tight=False`` skips ``tight_layout`` for the 3-D figures, where it
    misbehaves with the projected axes (they manage their own spacing).

    ``bbox_tight=False`` skips the crop-to-content bounding box, so the saved
    image has exactly the figure's own aspect ratio.  Use it for a figure whose
    printed size is fixed in advance (a full sideways page): with the crop on,
    the saved aspect depends on how much whitespace the content left over, and a
    canvas sized to fit a page can be saved at an aspect that no longer does.
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if tight:
        # tight_layout can warn when figures contain colorbars or shared axes;
        # bbox_inches="tight" in savefig handles the actual bounding box so the
        # layout warning is cosmetic and safe to suppress.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            plt.tight_layout()
    plt.savefig(path, dpi=150,
                bbox_inches="tight" if bbox_tight else None)
    plt.close()  # release the figure so head-less runs don't leak memory


def plot_complexity_growth(path: str | Path) -> None:
    """The combinatorial explosion: number of graphs to enumerate, by direction.

    Two panels, directed (left) and undirected (right), sharing one axis range.
    Each plots, on a log scale, how many graphs blind enumeration must visit
    against the vertex count ``n``, for the simple model, two multigraph
    connectivity caps, and (dotted) the 3-uniform hypergraph, with a dashed line
    at a generous budget of 10^9 candidates.  The count does not depend on the
    edge-versus-vertex separation, because both search the very same set of
    graphs, so one pair of panels covers all of those variants at once.
    Direction doubles the number of cells to fill, which is the whole difference
    between the two panels.
    """
    ns = list(range(2, 13))

    def log10_pow(base: float, exponent: float) -> float:
        return exponent * math.log10(base)

    def curves(directed: bool):
        # Each model fills a number of off-diagonal cells; the candidate count is
        # (values per cell) ^ (number of cells).  Labels stay plain -- the precise
        # exponential forms live in the caption, not the legend.  Direction
        # multiplies the cell count: by 2 for graphs (ordered vs unordered pairs,
        # n(n-1) vs C(n,2)), but by 3 for 3-uniform hypergraphs, since a directed
        # hyperedge is a tail plus 2 heads (n*C(n-1,2) = 3*C(n,3) candidates).
        cells = (lambda n: n * (n - 1)) if directed else (lambda n: n * (n - 1) / 2)
        hyper_cells = ((lambda n: n * (n - 1) * (n - 2) / 2) if directed
                       else (lambda n: n * (n - 1) * (n - 2) / 6))
        return [
            ("simple / random", _KUL_BLUE, "-",
             [log10_pow(2, cells(n)) for n in ns]),
            ("multigraph $m=3$", _KUL_DARK, "-",
             [log10_pow(3, cells(n)) for n in ns]),
            ("multigraph $m=4$", _WARM, "-",
             [log10_pow(4, cells(n)) for n in ns]),
            ("$3$-uniform hypergraph", _VIOLET, ":",
             [log10_pow(2, hyper_cells(n)) for n in ns]),
        ]

    # Printed-size note: displayed at full text width (about 6.1in), so the
    # canvas is drawn at that width and the point sizes below reach paper
    # unshrunk.
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 3.1), sharey=True)
    for ax, directed, title in [(axes[0], True, "directed graphs"),
                                (axes[1], False, "undirected graphs")]:
        for label, colour, style, vals in curves(directed):
            ax.plot(ns, vals, style, color=colour, marker="o", markersize=3.5,
                    label=label)
        ax.axhline(9, color="gray", linestyle="--", linewidth=1,
                   label=r"$10^{9}$ budget")
        ax.set_title(title)
        ax.set_xlabel("vertices $n$")
        ax.grid(True, alpha=0.3)
    # Cap the shared vertical axis at 100 so the slowest curve (the directed
    # 3-uniform hypergraph) runs off the top instead of compressing every other
    # curve into a thin band near the bottom.  sharey=True propagates the limit.
    axes[0].set_ylim(0, 100)
    axes[0].annotate(r"$3$-uniform directed" + "\n" + r"continues off the top",
                     xy=(9.55, 99.3), xytext=(7.5, 92), fontsize=8, color=_VIOLET,
                     ha="center", va="center",
                     arrowprops=dict(arrowstyle="->", color=_VIOLET, lw=1.0))
    axes[0].set_ylabel(r"$\log_{10}$ (number of graphs)")
    # One legend serves both panels. It sits in the RIGHT panel because the
    # left one carries the "continues off the top" annotation in that corner,
    # and at the printed canvas size the two would overlap.
    axes[1].legend(fontsize=7.5, loc="upper left", title="model")
    fig.suptitle("Number of graphs blind enumeration must visit",
                 fontsize=12)
    _save(path)


def _circle_layout(n, hub=None):
    """Vertex positions for a panel: all on a unit circle, or the ``hub`` vertex
    at the centre and the rest on the circle, which draws stars and hub graphs
    far more clearly than a plain circle does."""
    if hub is None:
        angs = [math.pi / 2 - 2 * math.pi * k / n for k in range(n)]
        return [(math.cos(a), math.sin(a)) for a in angs]
    pos = [(0.0, 0.0) for _ in range(n)]
    others = [k for k in range(n) if k != hub]
    for idx, k in enumerate(others):
        a = math.pi / 2 - 2 * math.pi * idx / len(others)
        pos[k] = (math.cos(a), math.sin(a))
    return pos


def _draw_extremal_panel(ax, matrix, *, directed: bool, hub=None) -> None:
    """Draw one extremal multiplicity matrix on ``ax`` as a graph.

    Vertices sit on a circle (or, when ``hub`` is given, that vertex sits at the
    centre and the rest on the circle).  An adjacency of multiplicity one is a
    single line (an arrowed line when ``directed``), and a higher multiplicity is
    shown by a small count label rather than parallel curves, so the picture
    stays legible.  Opposite arcs of a bidirected pair are bent apart.

    Every named family the gallery draws is *uniform*: all its adjacencies carry
    one and the same multiplicity.  Repeating that count on every arc buries the
    structure under labels (worst on the bidirected ``K_4``, twelve labels over
    six crossing arcs), so a uniform multiplicity above one is stated once in a
    corner note, and the per-arc labels are kept only for the genuinely mixed
    case.  ``hub`` may also be an explicit list of ``(x, y)`` positions, used
    for the bipartite wall panel, where two columns read far better than a circle.
    """
    n = len(matrix)
    pos = hub if isinstance(hub, list) else _circle_layout(n, hub)
    mults = {int(matrix[i][j]) for i in range(n) for j in range(n)
             if i != j and matrix[i][j] > 0}
    uniform = mults.pop() if len(mults) == 1 else None
    per_arc_labels = uniform is None

    def edge(i, j, rad, arrow):
        ax.add_patch(FancyArrowPatch(
            pos[i], pos[j], connectionstyle=f"arc3,rad={rad}",
            arrowstyle=("-|>" if arrow else "-"), mutation_scale=12,
            lw=1.7, color=_KUL_BLUE, shrinkA=10, shrinkB=10, zorder=1))

    def mlabel(i, j, rad, mu):
        if mu <= 1:
            return
        mx, my = (pos[i][0] + pos[j][0]) / 2, (pos[i][1] + pos[j][1]) / 2
        dx, dy = pos[j][0] - pos[i][0], pos[j][1] - pos[i][1]
        length = math.hypot(dx, dy) or 1.0
        mx += (rad * 0.9 + 0.06) * (-dy) / length
        my += (rad * 0.9 + 0.06) * (dx) / length
        ax.text(mx, my, f"$\\times{mu}$", fontsize=8, ha="center", va="center",
                color=_KUL_DARK, zorder=3,
                bbox=dict(boxstyle="round,pad=0.08", fc="white", ec="none"))

    if directed:
        for i in range(n):
            for j in range(n):
                if i == j or matrix[i][j] == 0:
                    continue
                rad = 0.16 if matrix[j][i] else 0.0
                edge(i, j, rad, True)
                if per_arc_labels:
                    mlabel(i, j, rad, matrix[i][j])
    else:
        for i in range(n):
            for j in range(i + 1, n):
                if matrix[i][j] == 0:
                    continue
                edge(i, j, 0.0, False)
                if per_arc_labels:
                    mlabel(i, j, 0.0, matrix[i][j])
    for k, (x, y) in enumerate(pos):
        ax.scatter([x], [y], s=300, c="white", edgecolors=_KUL_BLUE,
                   linewidths=1.6, zorder=2)
        ax.text(x, y, str(k + 1), ha="center", va="center", fontsize=9,
                zorder=3, color=_KUL_DARK)
    if uniform is not None and uniform > 1:
        word = "arcs" if directed else "edges"
        ax.text(0.0, -1.34, f"all {word} $\\times{uniform}$", ha="center",
                va="center", fontsize=9, color=_KUL_DARK)
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)


# metro-line palette for hypergraph panels: red, blue, green, orange, purple, grey
_GALLERY_METRO = ["#C85050", "#1D8DB0", "#3CA050", "#DC8C28", "#8C50A0", "#787878"]


def _draw_hyper_panel(ax, hyperedges, n, *, directed: bool, hub=None) -> None:
    """Draw a hypergraph extremiser as a metro map: vertices on a circle (or a
    hub at the centre), each hyperedge a thick coloured line through its members
    when undirected, or a fan of coloured arrows from its tail when directed."""
    pos = _circle_layout(n, hub)
    for idx, he in enumerate(hyperedges):
        col = _GALLERY_METRO[idx % len(_GALLERY_METRO)]
        if directed:
            tail, heads = he
            tx, ty = pos[tail]
            for h in heads:
                hx, hy = pos[h]
                ax.add_patch(FancyArrowPatch(
                    (tx, ty), (hx, hy), arrowstyle="-|>", mutation_scale=11,
                    lw=2.4, color=col, alpha=0.85, shrinkA=11, shrinkB=11,
                    zorder=1, connectionstyle="arc3,rad=0.10"))
        else:
            pts = [pos[v] for v in sorted(he)]
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            pts.sort(key=lambda p: math.atan2(p[1] - cy, p[0] - cx))
            ax.plot([p[0] for p in pts], [p[1] for p in pts], "-", color=col,
                    lw=4.2, solid_capstyle="round", solid_joinstyle="round",
                    alpha=0.85, zorder=1)
    for k, (x, y) in enumerate(pos):
        ax.scatter([x], [y], s=300, c="white", edgecolors="#333333",
                   linewidths=1.5, zorder=2)
        ax.text(x, y, str(k + 1), ha="center", va="center", fontsize=9,
                zorder=3, color="#222222")
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)


def plot_extremal_gallery(path: str | Path, *,
                          gallery_json: str | Path | None = None) -> None:
    """A gallery of the named extremal graphs, drawn at a large representative size.

    These are the structured extremisers the analysis identifies, not the
    trivial small trees: the directed double and bidirected stars, the doubled
    bipartite wall, the dense bidirected complete graph, the multigraph star at
    full multiplicity, and the star hypertrees (drawn as metro maps). The
    program builds these named families directly. The ``gallery_json`` argument
    is accepted for backward compatibility and ignored.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise RuntimeError("matplotlib is required for figures")
    # dense bidirected complete graphs, built directly
    bidir_k4 = Graph(4, SIMPLE_DIRECTED)
    for i in range(4):
        for j in range(4):
            if i != j:
                bidir_k4.set_multiplicity(i, j, 1)
    # 2.B_{3,4}: the doubled one-directional bipartite wall, one of the three
    # proved 24-arc extremisers at n = 7, m = 3 (rem:odd-step-roadmap, fact (b)).
    # It ties the double star at the crossover, so the gallery shows both branches.
    bip_2b34 = Graph(7, MULTI_DIRECTED)
    for a in range(3):
        for b in range(3, 7):
            bip_2b34.set_multiplicity(a, b, 2)
    bip_pos = [(-0.85, 0.85), (-0.85, 0.0), (-0.85, -0.85),
               (0.85, 1.05), (0.85, 0.35), (0.85, -0.35), (0.85, -1.05)]
    multi_star = Graph(9, MULTI_UNDIRECTED)   # undirected star, mult 2
    for i in range(1, 9):
        multi_star.set_multiplicity(0, i, 2)
    dir_hypertree = [(0, frozenset({1, 2})), (0, frozenset({3, 4})),
                     (0, frozenset({5, 6}))]   # directed star hypertree on 7 vertices

    # ("g"/"h"/"hd", object, directed, hub, title)
    panels = [
        ("g", double_star(7, 3, directed=True), True, 0,
         "multigraph directed, arc\n$m=3$, $n=7$: double star ($24$ arcs)"),
        ("g", double_star(7, 2, directed=True), True, 0,
         "simple directed, arc\n$m=2$, $n=7$: bidirected star ($12$ arcs)"),
        ("g", multi_star, False, 0,
         "multigraph undirected, edge\n$m=3$, $n=9$: star at multiplicity $2$ ($16$ edges)"),
        ("g", bidir_k4, True, None,
         "simple directed, arc\n$m=4$, $n=4$: bidirected $K_4$ ($12$ arcs)"),
        ("g", bip_2b34, True, bip_pos,
         "multigraph directed, arc\n$m=3$, $n=7$: bipartite wall $2 \\cdot B_{3,4}$ ($24$ arcs)"),
        ("h", star_hypertree(10, 3), False, 0,
         "hypergraph, $r=3$\n$m=2$, $n=10$: star hypertree ($4$ hyperedges)"),
        ("h", star_hypertree(13, 4), False, 0,
         "hypergraph, $r=4$\n$m=2$, $n=13$: star hypertree ($4$ hyperedges)"),
        ("h", star_hypertree(16, 3), False, 0,
         "hypergraph, $r=3$\n$m=2$, $n=16$: star hypertree ($7$ hyperedges)"),
        ("hd", (dir_hypertree, 7), True, 0,
         "directed hypergraph, $r=3$\n$m=2$, $n=7$: tail-to-heads star"),
    ]
    fig, axes = plt.subplots(3, 3, figsize=(12, 12))
    for ax, (kind, obj, directed, hub, title) in zip(axes.flat, panels):
        if kind == "g":
            _draw_extremal_panel(ax, obj.mu.tolist(), directed=directed, hub=hub)
        elif kind == "h":
            _draw_hyper_panel(ax, list(obj.hyperedges), obj.num_vertices,
                              directed=False, hub=hub)
        else:  # "hd": (hyperedges, n)
            hes, nn = obj
            _draw_hyper_panel(ax, hes, nn, directed=True, hub=hub)
        ax.set_title(title, fontsize=9.5)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle("Extremal graphs of the named families, drawn large", fontsize=14)
    _save(path)



# The four questions every model row is asked, in column order.  They live above
# the columns because they are a property OF the column, not of the panel: naming
# them in all sixteen panel titles is what made those titles wider than the
# column could hold.
_VARIANT_COL_HEADERS = ("undirected, edge", "undirected, vertex",
                        "directed, arc", "directed, vertex")


def _status_colour(status: str):
    """Colour of the curve a panel's status word refers to.

    Matched on substrings rather than on equality because a row that inherits its
    value from another one says so first ("= simple, conjectured").
    """
    low = status.lower()
    if "conj" in low:
        return _RED
    if "open" in low:
        return _GUESS
    if "proved" in low:
        return _KUL_BLUE
    return _KUL_DARK


def plot_variant_grid(panels: list[dict], path: str | Path,
                      m: int | None = None,
                      row_range: tuple[int, int] | None = None,
                      fontsize_scale: float = 1.0,
                      subtitle: str | None = None) -> None:
    """All sixteen variants on one grid, in the proved/conjectured/guessed language.

    ``panels`` is a row-major list of sixteen dictionaries (rows = model simple,
    multi, hyper, multihyper; columns = undirected edge, undirected vertex,
    directed arc, directed vertex).  Each panel may carry any of:

    ``proved`` ``(xs, ys)`` solid blue line, a theorem holding for all ``n``;
    ``conj``   ``(xs, ys)`` solid red line, a conjecture formula;
    ``guess``  ``(xs, ys)`` solid yellow line, a bare extrapolation of the
               machine points where no formula is known;
    ``band``   ``(xs, lo, hi)`` the certain interval, an easy construction below
               and the trivial maximum edge count above;
    ``exact``  ``(xs, ys)`` filled squares, sizes the machine proved;
    ``search`` ``(xs, ys)`` open circles, the search lower bounds;
    ``status`` the one word this panel's value has earned ("proved",
               "conjectured", "open"), shown as a coloured chip inside the panel
               in the colour of the curve it refers to;
    ``ylabel`` what is being counted (edges, arcs, hyperedges, hyperarcs).

    Every panel is drawn from the same vocabulary, with no per-variant extras:
    a blue line is settled, a red line is conjectured, a yellow line is a guess,
    and the shaded band is the interval we are certain the truth lies in.  The
    directed arc panel used to add its two competing sub-branches as dotted
    lines, which made one panel of sixteen carry a mark the others did not.
    Where a conjecture is a maximum of two counts, the curve plotted is that
    maximum, and the branches are named in prose instead (author call,
    2026-08-26).

    ``row_range`` restricts the grid to a slice of the four model rows (e.g.
    ``(0, 2)`` for just simple and multigraph), so the sixteen panels can be
    split across two page-sized images instead of squeezed onto one.
    ``fontsize_scale`` raises every panel font to match the extra room a
    two-row half gives them (pass 1.2-1.3).
    """
    two_row = row_range is not None and (row_range[1] - row_range[0]) == 2

    row_labels = _VARIANT_ROW_LABELS
    if row_range is not None:
        lo, hi = row_range
        panels = panels[lo * 4:hi * 4]
        row_labels = row_labels[lo:hi]

    # Which marks this figure actually uses, read off the panels BEFORE anything
    # is drawn.  Collecting the flags inside ``draw_panel`` instead would set them
    # after the legend was built, since the scaffold draws the panels only once it
    # has been handed the key.
    def _uses(key):
        return any(panel.get(key) is not None for panel in panels)

    def _uses_points(key):
        return any(panel.get(key) is not None and len(panel[key][0])
                   for panel in panels)

    drawn = {"band": _uses("band"),
             "proved": _uses("proved"), "conj": _uses("conj"),
             "guess": _uses("guess"),
             "exact": _uses_points("exact"), "search": _uses_points("search")}

    def draw_panel(ax, panel):
        band = panel.get("band")
        if band is not None:
            xs, lo, hi = band
            ax.fill_between(xs, lo, hi, color=_WARM, alpha=0.10, linewidth=0)
            ax.plot(xs, hi, "-", color=_WARM, linewidth=0.7, alpha=0.55)
        for key, colour in (("proved", _KUL_BLUE), ("conj", _RED),
                            ("guess", _GUESS)):
            if panel.get(key) is not None:
                xs, ys = panel[key]
                ax.plot(xs, ys, "-", color=colour, linewidth=2.0,
                        solid_capstyle="round", zorder=2.5)
        if panel.get("search") is not None:
            xs, ys = panel["search"]
            if len(xs):
                # Hollow, and small enough that the curve reads THROUGH the ring
                # rather than under a chain of discs.  Where the search lands on
                # the curve that coincidence is the finding, so it has to be
                # visible; the old size-8 rings with a size-1.8 edge simply hid it.
                ax.plot(xs, ys, "o", mfc="none", mec=_VIOLET, mew=1.1,
                        markersize=5.2, zorder=3)
        if panel.get("exact") is not None:
            xs, ys = panel["exact"]
            if len(xs):
                ax.plot(xs, ys, "s", color=_GREEN, markersize=4.4, zorder=4)

        status = panel.get("status", "")
        if status:
            colour = _status_colour(status)
            # A row that inherits its value from another one says so first, and
            # the two facts stack rather than run: "= simple, conjectured" on one
            # line is wider than the panel it has to sit inside.
            ax.text(0.045, 0.945, status.replace(", ", "\n"),
                    transform=ax.transAxes,
                    ha="left", va="top", fontsize=6.9 * fontsize_scale,
                    color=colour, fontweight="bold", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.30", facecolor="white",
                              edgecolor=colour, linewidth=0.7, alpha=0.90))
        ax.set_ylabel(panel.get("ylabel", "edges"),
                      fontsize=8.0 * fontsize_scale, labelpad=2.5)
        ax.tick_params(labelsize=7.4 * fontsize_scale, length=2.5, pad=1.5)
        # Both axes count things, so neither ever wants a fractional tick.
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))
        ax.grid(True, alpha=0.25, linewidth=0.6)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        # Headroom above the curve for the status chip, which sits at 0.945 of
        # the axes height and must not land on the line at large n.
        ax.margins(x=0.05, y=0.14)

    def finish(fig, axes):
        # "vertices n" is the same on all eight panels, so it is written once per
        # column, under the bottom row.  Ticks stay on every panel: each has its
        # own y scale and is read on its own.
        for ax in axes[-1, :]:
            ax.set_xlabel("vertices $n$", fontsize=8.5 * fontsize_scale)

    # One figure-level key, in the order a reader meets the marks: the curve
    # kinds (what is claimed), then the point kinds (what was computed).  Only
    # the marks this figure actually draws are listed, so the hypergraph halves
    # stop advertising a red conjecture curve that appears in neither of them.
    key_specs = [
        ("proved", dict(color=_KUL_BLUE, lw=2.0, label="proved")),
        ("conj", dict(color=_RED, lw=2.0, label="conjectured")),
        ("guess", dict(color=_GUESS, lw=2.0, label="guess (interpolated)")),
        ("band", dict(color=_WARM, lw=4, alpha=0.35, label="certain interval")),
        ("exact", dict(color=_GREEN, marker="s", ls="none", markersize=4.4,
                       label="machine-checked (exact)")),
        ("search", dict(color=_VIOLET, marker="o", ls="none", markersize=5.2,
                        mfc="none", mew=1.1, label="search (lower bound)")),
    ]

    suptitle = "Erdős 915 across the sixteen variants"
    if m is not None:
        suptitle += fr",  $m = {m}$"
    if subtitle:
        # One line, not two: the second line of a two-line suptitle pushed the
        # column headers into the top row of panels.
        suptitle += f"   ·   {subtitle}"

    # Printed-size note, and the reason this figure sets its geometry by hand.
    # The thesis gives each half its own full sideways page, so the image is
    # placed at a width of 0.98\textheight (about 9.1in) and the height it may
    # occupy is what is left of the text WIDTH (about 6.1in) after the caption,
    # roughly 4.9in.  The canvas is therefore 9.2 x 4.9 and is saved WITHOUT a
    # crop-to-content bounding box, so that ratio survives to the page.  The old
    # 9.2 x 8.4 canvas was taller than the rotated page could hold and the
    # suptitle, the caption and half the legend were simply cut off the paper.
    key_handles = [mlines.Line2D([], [], **spec)
                   for key, spec in key_specs if drawn[key]]

    figsize = (9.2, 4.9) if two_row else (9.2, 9.4)
    adjust = dict(left=0.085, right=0.995,
                  top=0.845 if two_row else 0.925,
                  bottom=0.155 if two_row else 0.085,
                  wspace=0.30, hspace=0.34 if two_row else 0.45)
    _variant_panel_grid(draw_panel, configs=panels, suptitle=suptitle, path=path,
                        suptitle_fontsize=12.0,
                        figsize=figsize, row_labels=row_labels,
                        col_headers=_VARIANT_COL_HEADERS,
                        col_header_fontsize=9.5 * fontsize_scale,
                        row_label_fontsize=9.5 * fontsize_scale,
                        adjust=adjust, finish=finish,
                        legend_handles=key_handles,
                        legend_ncol=len(key_handles),
                        legend_fontsize=8.4,
                        legend_y=0.075 if two_row else 0.045,
                        bbox_tight=False)


# --- ENUMERATION LANDSCAPES: visit every labeled graph, collect (edges, lambda^max) ---

# The four models, in the row order every variant grid uses.  Two axes generate
# them, multiplicity (simple / multi) and arity (graph / hypergraph); the columns
# then split by direction and separation, giving the sixteen variants.
_VARIANT_ROW_LABELS = ("simple graph", "multigraph",
                       "hypergraph $r=3$", "multihypergraph $r=3$")

# Row-major table of all sixteen variants, matching gather_variant_grid.
# ``enum_n`` is the vertex count used for full enumeration.
# ``max_mult`` caps per-cell multiplicity for multigraph variants.
_VARIANT_ENUM_CONFIGS: list[dict] = [
    # row 1 — simple
    dict(key="simple_undirected_edge",   title="simple undirected edge",
         directed=False, simple=True,  hypergraph=False, r=3, separation="edge",
         enum_n=6, max_mult=1),
    dict(key="simple_undirected_vertex", title="simple undirected vertex",
         directed=False, simple=True,  hypergraph=False, r=3, separation="vertex",
         enum_n=6, max_mult=1),
    dict(key="simple_directed_edge",     title="simple directed arc",
         directed=True,  simple=True,  hypergraph=False, r=3, separation="edge",
         enum_n=4, max_mult=1),
    dict(key="simple_directed_vertex",   title="simple directed vertex",
         directed=True,  simple=True,  hypergraph=False, r=3, separation="vertex",
         enum_n=4, max_mult=1),
    # row 2 — multigraph
    dict(key="multi_undirected_edge",    title="multigraph undirected edge",
         directed=False, simple=False, hypergraph=False, r=3, separation="edge",
         enum_n=5, max_mult=2),
    dict(key="multi_undirected_vertex",  title="multigraph undirected vertex",
         directed=False, simple=False, hypergraph=False, r=3, separation="vertex",
         enum_n=5, max_mult=2),
    dict(key="multi_directed_edge",      title="multigraph directed arc",
         directed=True,  simple=False, hypergraph=False, r=3, separation="edge",
         enum_n=3, max_mult=5),
    dict(key="multi_directed_vertex",    title="multigraph directed vertex",
         directed=True,  simple=False, hypergraph=False, r=3, separation="vertex",
         enum_n=3, max_mult=5),
    # row 3 — SIMPLE r=3 hypergraph (no repeated hyperedge).  prop:hyper-edge and
    # thm:hyper-vertex-m3 are proved for MULTIhypergraphs and coincide with this
    # simple enumeration only under the conditions gated by
    # _hyper_edge_simple_proved / _hyper_vertex_simple_proved
    # (thm:simple-hyper-edge, rem:hyper-vertex-m3-scope). Outside those
    # conditions this enumeration's exact answer can be strictly smaller
    # than the closed form, e.g. (n,m,r)=(3,3,3): formula 2, enumeration 1.
    dict(key="hyper_undirected_edge",    title="hypergraph undirected edge",
         directed=False, simple=True,  hypergraph=True,  r=3, separation="edge",
         enum_n=5, max_mult=1),
    dict(key="hyper_undirected_vertex",  title="hypergraph undirected vertex",
         directed=False, simple=True,  hypergraph=True,  r=3, separation="vertex",
         enum_n=5, max_mult=1),
    dict(key="hyper_directed_edge",      title="hypergraph directed arc",
         directed=True,  simple=True,  hypergraph=True,  r=3, separation="edge",
         enum_n=4, max_mult=1),
    dict(key="hyper_directed_vertex",    title="hypergraph directed vertex",
         directed=True,  simple=True,  hypergraph=True,  r=3, separation="vertex",
         enum_n=4, max_mult=1),
    # row 4 — MULTIhypergraph r=3: a hyperedge may repeat, up to m-1 copies
    # (_hyper_multiplicity_cap).  Unlike the multigraph VERTEX rows this does NOT
    # collapse onto the simple rows: parallel copies of a hyperedge are routes
    # with empty interiors, so they raise kappa as well as lambda, and the
    # question stays a genuine one in both separations.  It is exactly the model
    # prop:hyper-edge / thm:hyper-vertex-m2 / thm:hyper-vertex-m3 are stated for.
    # One vertex smaller than the simple rows, since the sweep is (m)^C not 2^C.
    dict(key="multihyper_undirected_edge",   title="multihypergraph undirected edge",
         directed=False, simple=False, hypergraph=True,  r=3, separation="edge",
         enum_n=4, max_mult=2),
    dict(key="multihyper_undirected_vertex", title="multihypergraph undirected vertex",
         directed=False, simple=False, hypergraph=True,  r=3, separation="vertex",
         enum_n=4, max_mult=2),
    dict(key="multihyper_directed_edge",     title="multihypergraph directed arc",
         directed=True,  simple=False, hypergraph=True,  r=3, separation="edge",
         enum_n=3, max_mult=2),
    dict(key="multihyper_directed_vertex",   title="multihypergraph directed vertex",
         directed=True,  simple=False, hypergraph=True,  r=3, separation="vertex",
         enum_n=3, max_mult=2),
]


def _all_objects_of_variant(
    n: int, *,
    directed: bool,
    simple: bool,
    hypergraph: bool = False,
    r: int = 3,
    max_mult: int = 3,
):
    """Yield every labeled object of one variant on ``n`` vertices, one at a time.

    The single enumeration the two sweeps below share.  For a hypergraph each
    candidate hyperedge is present or absent; for a matrix model each cell runs
    over ``{0, 1}`` when simple and ``{0, ..., max_mult}`` when multi.  Isomorphic
    copies are included, which is what a distribution over the search space wants.
    Yielding rather than collecting keeps the whole space out of memory.
    """
    if hypergraph:
        candidates = _hyperedge_candidates(n, r, directed)
        for mask in product((0, 1), repeat=len(candidates)):
            chosen = [candidates[i] for i, flag in enumerate(mask) if flag]
            yield Hypergraph(n, chosen, directed=directed)
        return

    variant = _variant_for(directed, simple)
    cells = _matrix_cells(n, directed)
    span = 2 if simple else (max_mult + 1)
    base = Graph(n, variant)
    for values in product(range(span), repeat=len(cells)):
        candidate = base.copy()
        for (u, v), value in zip(cells, values):
            if value:
                candidate.set_multiplicity(u, v, value)
        yield candidate


def enumerate_all_graphs(
    n: int, *,
    directed: bool,
    simple: bool,
    hypergraph: bool = False,
    r: int = 3,
    max_mult: int = 3,
    separation: str = "edge",
) -> list[tuple[int, int]]:
    """Return ``(edge_count, lambda_max)`` for every labeled graph of this type on ``n`` vertices.

    For simple graphs each cell is 0/1; for multigraphs each cell ranges over
    ``{0,...,max_mult}``.  For hypergraphs each candidate hyperedge is present or
    absent.  The list covers the full labeled graph space (isomorphic copies
    included), which is what we want for the distribution over the search space.
    """
    if hypergraph:
        vertex_split = (separation == "vertex")
        def measure(obj):
            return max_hyper_connectivity(obj, vertex_split=vertex_split)
    else:
        measure = _connectivity_measure(separation)

    return [(obj.edge_count(), measure(obj))
            for obj in _all_objects_of_variant(
                n, directed=directed, simple=simple,
                hypergraph=hypergraph, r=r, max_mult=max_mult)]


def _pair_connectivities(obj, *, separation: str, hypergraph: bool) -> list[int]:
    """Local connectivity of every vertex pair of one graph or hypergraph.

    The same pair sweep ``max_connectivity`` runs, but keeping each value rather
    than only the maximum.  For the edge case the capacity matrix is built once
    and reused across pairs (as ``max_connectivity`` does); vertex and hypergraph
    cases reuse their named per-pair routines.
    """
    vsplit = (separation == "vertex")
    if hypergraph:
        return [hyper_connectivity(obj, s, t, vertex_split=vsplit)
                for s, t in _pairs(obj)]
    if not vsplit:
        csr = _csr(obj.mu, dtype=int)
        return [int(_csgraph_maxflow(csr, s, t).flow_value) for s, t in _pairs(obj)]
    return [local_connectivity(obj, s, t, vertex_split=True) for s, t in _pairs(obj)]


def enumerate_pair_connectivities(
    n: int, *,
    directed: bool,
    simple: bool,
    hypergraph: bool = False,
    r: int = 3,
    max_mult: int = 3,
    separation: str = "edge",
) -> dict[tuple[int, int], int]:
    """Pooled 2-D histogram ``{(lambda_max, pair_conn): count}`` over all graphs.

    For every labeled graph on ``n`` vertices and every vertex pair, record the
    pair's local connectivity tagged with the graph's own ``lambda^max``.  The
    result is a small threshold-independent table: at plot time a feasibility
    threshold ``T`` splits each pair-connectivity column into observations from
    graphs that stay at ``lambda^max <= T`` and those that exceed it.  Much
    smaller than the raw observation list (a few dozen entries per variant), so
    it pickles compactly even though the sweep itself enumerates every graph.
    """
    table: Counter = Counter()
    for obj in _all_objects_of_variant(n, directed=directed, simple=simple,
                                       hypergraph=hypergraph, r=r, max_mult=max_mult):
        pcs = _pair_connectivities(obj, separation=separation, hypergraph=hypergraph)
        lmax = max(pcs, default=0)
        for c in pcs:
            table[(lmax, c)] += 1
    return dict(table)


_CACHE_SCHEMA_VERSION = 2


def _cache_metadata(namespace: str, **settings) -> dict:
    """Fingerprint a cache by schema, source revision, and run configuration."""
    normalised = json.loads(json.dumps(settings, sort_keys=True, default=str))
    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return {
        "schema": _CACHE_SCHEMA_VERSION,
        "namespace": namespace,
        "source_sha256": source_hash,
        "settings": normalised,
    }


def compute_pair_enumeration_cache(
    cache_path: str | Path = "figures/pair_enumeration_cache.pkl",
    configs: list[dict] | None = None,
) -> dict[str, dict[tuple[int, int], int]]:
    """Per-variant pooled pair-connectivity tables, loading from cache if present.

    The pooled analogue of :func:`compute_enumeration_cache`: one
    ``{(lambda_max, pair_conn): count}`` table per variant.  Slow on first run
    (it re-sweeps the enumeration measuring every pair), cached thereafter.
    """
    cache_path = Path(cache_path)
    if configs is None:
        configs = _VARIANT_ENUM_CONFIGS

    meta = _cache_metadata("pair-enumeration", configs=configs)
    if cache_path.exists():
        with open(cache_path, "rb") as f:
            payload = pickle.load(f)
        cached = (payload.get("data", {})
                  if isinstance(payload, dict) and payload.get("_meta") == meta
                  else {})
    else:
        cached = {}

    changed = False
    for cfg in configs:
        key = cfg["key"]
        if key in cached:
            continue
        print(f"  pooling pairs for {cfg['title']} (n={cfg['enum_n']})...", flush=True)
        cached[key] = enumerate_pair_connectivities(
            cfg["enum_n"],
            directed=cfg["directed"], simple=cfg["simple"],
            hypergraph=cfg["hypergraph"], r=cfg["r"],
            max_mult=cfg["max_mult"], separation=cfg["separation"])
        changed = True

    if changed:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "wb") as f:
            pickle.dump({"_meta": meta, "data": cached}, f)

    return cached


def compute_enumeration_cache(
    cache_path: str | Path = "figures/enumeration_cache.pkl",
    configs: list[dict] | None = None,
) -> dict[str, list[tuple[int, int]]]:
    """Return the full enumeration for every variant, loading from cache if available.

    On first run this takes several minutes; subsequent runs load the pickle
    instantly.  The cache lives at ``cache_path`` relative to the caller's
    working directory.
    """
    cache_path = Path(cache_path)
    if configs is None:
        configs = _VARIANT_ENUM_CONFIGS

    meta = _cache_metadata("enumeration", configs=configs)
    if cache_path.exists():
        with open(cache_path, "rb") as f:
            payload = pickle.load(f)
        cached = (payload.get("data", {})
                  if isinstance(payload, dict) and payload.get("_meta") == meta
                  else {})
    else:
        cached = {}

    changed = False
    for cfg in configs:
        key = cfg["key"]
        if key in cached:
            continue
        print(f"  enumerating {cfg['title']} (n={cfg['enum_n']})...", flush=True)
        data = enumerate_all_graphs(
            cfg["enum_n"],
            directed=cfg["directed"],
            simple=cfg["simple"],
            hypergraph=cfg["hypergraph"],
            r=cfg["r"],
            max_mult=cfg["max_mult"],
            separation=cfg["separation"],
        )
        cached[key] = data
        changed = True

    if changed:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "wb") as f:
            pickle.dump({"_meta": meta, "data": cached}, f)

    return cached


def plot_scatter_lambda_edges(
    enum_data: dict[str, list[tuple[int, int]]],
    path: str | Path,
) -> None:
    """Extremal envelope of edge count against binding connectivity, all sixteen variants.

    For each variant the full enumeration is drawn as a faint grey cloud (one
    point per labeled graph) with the binding connectivity ``lambda^max`` on the
    horizontal axis and the edge count on the vertical, matching the
    edges-against-parameter layout of the all-variant grid.  The extremal
    envelope -- the densest feasible graph available at each connectivity level
    -- is overlaid as an integer staircase with one dot per level, so every
    connectivity value carries an exact extremal edge count and the frontier is
    read off without any interpolation between levels.
    """
    def draw_panel(ax, cfg):
        key = cfg["key"]
        data = enum_data.get(key, [])
        if not data:
            ax.set_title(cfg["title"], fontsize=9.5)
            return

        edges_arr = [e for e, _ in data]
        conn_arr  = [c for _, c in data]

        # Faint cloud of every graph: connectivity (x) against edge count (y).
        ax.scatter(conn_arr, edges_arr, s=1.5, c="grey", alpha=0.25,
                   linewidths=0, rasterized=True)

        # Extremal envelope e(lambda) = densest feasible graph with lambda^max
        # at most this level: a non-decreasing integer staircase.  Reading it at
        # lambda = m-1 gives the extremal value of Problem 915 at this n.
        levels = sorted(set(conn_arr))
        running, env_edges = 0, []
        for lv in levels:
            running = max(running, max(e for e, c in data if c == lv))
            env_edges.append(running)
        ax.step(levels, env_edges, where="mid", color=_KUL_BLUE, linewidth=1.8,
                zorder=3)
        ax.plot(levels, env_edges, "o", color=_KUL_BLUE, markersize=6,
                zorder=4, label="extremal envelope")

        ax.set_title(cfg["title"], fontsize=9.5)
        ax.set_xlabel(r"$\lambda^{\max}$", fontsize=8.5)
        ax.set_ylabel("edge count", fontsize=8.5)
        ax.tick_params(labelsize=8)
        # Both axes count discrete objects (independent routes, edges).
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(True, alpha=0.3)
        ax.text(0.02, 0.98, f"$n={cfg['enum_n']}$", transform=ax.transAxes,
                ha="left", va="top", fontsize=8, color="grey")

    _variant_panel_grid(
        draw_panel, path=path,
        suptitle=("Extremal envelope: edge count against binding connectivity "
                  "across all sixteen variants (full enumeration)"),
        suptitle_fontsize=13)


def _variant_panel_grid(draw_panel, *, suptitle: str, path: str | Path,
                        configs=None, suptitle_fontsize: float = 12.0,
                        row_label_fontsize: float = 12.0,
                        figsize: tuple[float, float] = (16, 14),
                        row_labels: tuple[str, ...] | None = None,
                        col_headers: tuple[str, ...] | None = None,
                        col_header_fontsize: float = 10.0,
                        adjust: dict | None = None,
                        finish=None,
                        legend_handles=None, legend_ncol: int = 6,
                        legend_fontsize: float = 10.0,
                        legend_y: float = 0.012,
                        bbox_tight: bool = True) -> None:
    """Shared scaffold for every sixteen-panel variant grid (four model rows by
    four columns): the distribution grids, the proved/conjectured bound grid, the
    sampled grid, and the extremal-envelope scatter.  Builds the axes, calls
    ``draw_panel(ax, cfg)`` on each panel config in turn, adds the per-row model
    labels and the suptitle, and saves.  Only the per-panel drawing and the panel
    configs differ between the grids, so the caller supplies both; everything else
    (layout, row labels, save) lives here once.  ``configs`` defaults to the
    sixteen enumeration variants but may be any 16-item list (e.g. the sampled
    configs or a precomputed ``panels`` list).

    ``col_headers`` names the four columns once above the top row, for grids whose
    columns ask the same four questions of every model row.  Repeating that naming
    inside all sixteen panel titles is what pushed the old titles to a width the
    column could not hold.

    ``adjust`` takes explicit ``subplots_adjust`` fractions instead of
    ``tight_layout``.  Prefer it wherever the figure's printed aspect ratio
    matters: ``tight_layout`` plus a tight save bounding box crops the canvas to
    its content, so the saved aspect is whatever the content happened to need,
    and a figure sized for a page can come back too tall for it.  Pass
    ``bbox_tight=False`` alongside, and the saved file is exactly ``figsize``.

    ``finish(fig, axes)`` runs after every panel is drawn, for touches that need
    to know a panel's place in the grid (an x label on the bottom row only).

    ``legend_handles`` puts ONE figure-level legend under the whole grid instead
    of repeating the same key inside all sixteen panels.  Sixteen copies of a
    six-entry key cost more area than the curves they explain, so prefer this
    wherever every panel shares one vocabulary.
    """
    if configs is None:
        configs = _VARIANT_ENUM_CONFIGS
    if row_labels is None:
        row_labels = _VARIANT_ROW_LABELS
    rows = len(row_labels)
    fig, axes = plt.subplots(rows, 4, figsize=figsize, squeeze=False)
    for cfg, ax in zip(configs, axes.flat):
        draw_panel(ax, cfg)
    if col_headers:
        for col, header in enumerate(col_headers):
            axes[0, col].set_title(header, fontsize=col_header_fontsize,
                                   fontweight="bold", color=_KUL_DARK, pad=7)
    if finish is not None:
        finish(fig, axes)
    fig.suptitle(suptitle, fontsize=suptitle_fontsize)
    if adjust is not None:
        fig.subplots_adjust(**adjust)
    else:
        fig.tight_layout(rect=(0.035, 0.0, 1.0, 0.97), w_pad=1.6, h_pad=1.35)
    # Row labels go outside everything the leftmost column already draws.  Their x
    # is MEASURED, not guessed: after a draw, ``get_tightbbox`` reports where that
    # column's tick labels and y label actually end, and the model name is hung
    # just left of it.  Guessing the offset in axes fractions (the old
    # ``xy=(-0.46, 0.5)``) scales with the panel width, so the same number that
    # cleared a narrow panel landed on top of the y label of a wide one.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = fig.transFigure.inverted()
    for row, name in enumerate(row_labels):
        ax0 = axes[row, 0]
        left = ax0.get_tightbbox(renderer).transformed(inv).x0
        pos = ax0.get_position()
        fig.text(max(left - 0.014, 0.004), pos.y0 + pos.height / 2, name,
                 rotation=90, ha="center", va="center",
                 fontsize=row_label_fontsize, fontweight="bold",
                 color=_KUL_DARK)
    if legend_handles:
        # The legend is anchored just BELOW the figure box rather than inside it.
        # Reserving a strip inside (via the tight_layout rect or subplots_adjust)
        # does not survive the tight bounding box the save uses, and the key lands
        # on the bottom row's "vertices n" labels.  Hanging it outside is robust:
        # the tight crop expands to include it, so it can never overlap an axis.
        # With ``bbox_tight=False`` there is no crop to expand, so the caller
        # reserves the strip through ``adjust`` and puts ``legend_y`` inside it.
        fig.legend(handles=legend_handles, loc="upper center", ncol=legend_ncol,
                   fontsize=legend_fontsize, frameon=False,
                   bbox_to_anchor=(0.5, legend_y),
                   columnspacing=1.6, handletextpad=0.6,
                   bbox_transform=fig.transFigure)
    # tight=False because the layout above is already final: _save would otherwise
    # run a second, rect-less tight_layout that discards the rect set here.
    _save(path, tight=False, bbox_tight=bbox_tight)


def plot_conn_dist_grid(
    enum_data: dict[str, list[tuple[int, int]]],
    m: int,
    path: str | Path,
    known_maxima: dict[str, int] | None = None,
) -> None:
    """16-panel histogram of lambda_max distribution, all variants, fixed m.

    Bars to the left of the feasibility boundary m-1 are coloured blue (the
    graphs we study); bars at or above m are coloured red (infeasible for this
    m).  A vertical dashed line marks the boundary, and a dotted line marks
    the known or conjectured maximum if supplied in ``known_maxima``.
    """
    threshold = m - 1  # feasible means lambda_max <= threshold

    def draw_panel(ax, cfg):
        key = cfg["key"]
        data = enum_data.get(key, [])
        if not data:
            ax.set_title(cfg["title"], fontsize=9)
            return

        conn_vals = [c for _, c in data]
        lo, hi = min(conn_vals), max(conn_vals)
        levels = list(range(lo, hi + 1))
        counts = [conn_vals.count(lv) for lv in levels]
        bar_colours = [_KUL_BLUE if lv <= threshold else _RED for lv in levels]
        ax.bar(levels, counts, color=bar_colours, edgecolor="white", linewidth=0.4)

        ax.axvline(threshold + 0.5, color=_WARM, linestyle="--", linewidth=1.8)
        if known_maxima and key in known_maxima:
            ax.axvline(known_maxima[key], color=_KUL_DARK, linestyle=":",
                       linewidth=1.6, label=f"known max = {known_maxima[key]}")

        ax.set_title(cfg["title"], fontsize=9.5)
        ax.set_xlabel(r"$\lambda^{\max}$", fontsize=8.5)
        ax.set_ylabel("graphs", fontsize=8.5)
        ax.tick_params(labelsize=8)
        # Connectivity is integer-valued: force integer ticks so the directed
        # panels stop showing spurious half-integer labels (0.5, 1.5, ...).
        ax.set_xticks(levels)
        ax.grid(True, axis="y", alpha=0.3)
        # The feasibility boundary is identical in all sixteen panels, so it is
        # explained once in the title and caption rather than repeated as a
        # legend in every panel. A legend is drawn only when a per-panel known
        # maximum line is present (a value that genuinely differs by panel).
        if known_maxima and key in known_maxima:
            ax.legend(fontsize=6.8, loc="upper right", framealpha=0.85)
        ax.text(0.02, 0.98, f"$n={cfg['enum_n']}$", transform=ax.transAxes,
                ha="left", va="top", fontsize=8, color="grey")

    suptitle = (fr"Connectivity distribution across all sixteen variants, $m = {m}$ "
                fr"(blue = feasible $\lambda^{{\max}} \leq {threshold}$, red = infeasible)")
    _variant_panel_grid(draw_panel, suptitle=suptitle, path=path,
                        row_label_fontsize=12)


def _midrange_lambda_threshold(hi: int) -> int:
    """A per-variant connectivity boundary at the midpoint of the achievable range.

    The distribution figures split graphs by ``lambda^max`` into a blue (low) and
    a red (high) population.  A single global boundary collapses some panels to one
    colour (every graph below it, or almost none), because the sixteen variants
    reach very different connectivity ranges at the sizes enumeration allows.
    Splitting instead at ``round(hi/2)`` -- the middle of what each enumeration can
    reach -- keeps both populations visible in every panel, scaled to what is
    possible there.  Floored at one so the boundary is never zero, which would
    push every graph above it and leave the blue (low) side empty.
    """
    return max(1, round(hi / 2))


def plot_pair_conn_dist_grid(
    pair_data: dict[str, dict[tuple[int, int], int]],
    path: str | Path,
) -> None:
    """12-panel histogram of per-PAIR connectivity, pooled over the full enumeration.

    Where :func:`plot_conn_dist_grid` plots one ``lambda^max`` per graph, this
    pools every vertex pair of every graph: one observation per (graph, pair).
    Each bar is split and STACKED by the connectivity of the graph the pair came
    from -- blue (bottom) for pairs from graphs whose ``lambda^max`` stays at or
    below the per-panel boundary ``T``, red (top) for pairs from graphs above it
    -- so the bar's full height is the true number of observations at that level.

    ``T`` is set per variant by :func:`_midrange_lambda_threshold`, not by a single
    global ``m``: at a fixed boundary some panels are entirely one colour, while the
    mid-range split keeps both populations visible everywhere.  Pairs whose own
    connectivity exceeds ``T`` can only come from graphs above ``T``, so those bars
    are wholly red; below ``T`` the colours mix, since a high-connectivity graph
    still has many low-connectivity pairs.
    """
    def draw_panel(ax, cfg):
        table = pair_data.get(cfg["key"], {})
        if not table:
            ax.set_title(cfg["title"], fontsize=9)
            return

        hi = max(lmax for (lmax, _pc) in table)
        T = _midrange_lambda_threshold(hi)
        levels = sorted({pc for (_lmax, pc) in table})
        blue = [sum(c for (lmax, pc), c in table.items()
                    if pc == lv and lmax <= T) for lv in levels]
        red = [sum(c for (lmax, pc), c in table.items()
                   if pc == lv and lmax > T) for lv in levels]

        ax.bar(levels, blue, color=_KUL_BLUE, edgecolor="white", linewidth=0.4,
               label=fr"from $\lambda^{{\max}}\!\leq\!{T}$")
        ax.bar(levels, red, bottom=blue, color=_RED, edgecolor="white",
               linewidth=0.4, label=fr"from $\lambda^{{\max}}\!>\!{T}$")
        ax.axvline(T + 0.5, color=_WARM, linestyle="--", linewidth=1.8)

        ax.set_title(cfg["title"], fontsize=9.5)
        ax.set_xlabel("pair connectivity", fontsize=8.5)
        ax.set_ylabel("pair observations", fontsize=8.5)
        ax.tick_params(labelsize=8)
        ax.set_xticks(levels)
        ax.grid(True, axis="y", alpha=0.3)
        ax.legend(fontsize=6.8, loc="upper right", framealpha=0.85)
        ax.text(0.02, 0.98, f"$n={cfg['enum_n']}$", transform=ax.transAxes,
                ha="left", va="top", fontsize=8, color="grey")

    suptitle = ("Pair-connectivity distribution across all sixteen variants "
                "(every vertex pair of every graph pooled, split at each variant's "
                r"mid-range $\lambda^{\max}$: blue from low-connectivity graphs, red from high)")
    _variant_panel_grid(draw_panel, suptitle=suptitle, path=path,
                        row_label_fontsize=12)


def plot_edge_dist_grid(
    enum_data: dict[str, list[tuple[int, int]]],
    path: str | Path,
) -> None:
    """12-panel histogram of edge count distribution, all variants.

    Each bar is split and STACKED by graph connectivity: blue (bottom) for graphs
    whose ``lambda^max`` stays at or below the per-panel boundary ``T``, red (top)
    for graphs above it, so the full bar height is the true number of graphs at
    that edge count.  ``T`` is the midpoint of each variant's achievable
    connectivity range (:func:`_midrange_lambda_threshold`); a single global
    boundary leaves some panels all one colour, the mid-range split keeps both
    populations visible.  A dotted line marks the densest graph at or below ``T``.
    """
    def draw_panel(ax, cfg):
        key = cfg["key"]
        data = enum_data.get(key, [])
        if not data:
            ax.set_title(cfg["title"], fontsize=9)
            return

        hi = max(c for _e, c in data)
        T = _midrange_lambda_threshold(hi)
        max_e = max(e for e, _ in data)
        levels = list(range(0, max_e + 1))
        blue = [0] * (max_e + 1)
        red = [0] * (max_e + 1)
        for e, c in data:
            (blue if c <= T else red)[e] += 1

        # Stacked, not overlaid: low-connectivity graphs (blue) on the bottom,
        # high-connectivity (red) on top, so the full height is the true count.
        ax.bar(levels, blue, color=_KUL_BLUE, edgecolor="white", linewidth=0.3,
               label=fr"$\lambda^{{\max}}\!\leq\!{T}$")
        ax.bar(levels, red, bottom=blue, color=_RED, edgecolor="white",
               linewidth=0.3, label=fr"$\lambda^{{\max}}\!>\!{T}$")

        # The densest graph in the lower-connectivity population: read straight
        # off the data, so it lands on the right edge of the blue mass.
        if any(blue):
            kmax = max(e for e in levels if blue[e])
            ax.axvline(kmax, color=_KUL_DARK, linestyle=":", linewidth=1.8,
                       label=fr"densest $\leq\!{T}$: {kmax}")

        ax.set_title(cfg["title"], fontsize=8.5)
        ax.set_xlabel("edge count", fontsize=7.5)
        ax.set_ylabel("graphs", fontsize=7.5)
        ax.tick_params(labelsize=7)
        # Edge counts are integers: keep the tick labels integer-valued.
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(True, axis="y", alpha=0.25)
        ax.legend(fontsize=6.2, loc="upper right", framealpha=0.8)
        ax.text(0.98, 0.02, f"$n={cfg['enum_n']}$", transform=ax.transAxes,
                ha="right", va="bottom", fontsize=7, color="grey")

    suptitle = ("Edge-count distribution across all sixteen variants "
                r"(stacked by connectivity, split at each variant's mid-range "
                r"$\lambda^{\max}$: blue low-connectivity graphs, red high)")
    _variant_panel_grid(draw_panel, suptitle=suptitle, path=path,
                        row_label_fontsize=11)


# --- 3-D BOUND SURFACE: cache solve() over (variant, n, m) grid; plot_variant_3d_surfaces draws it ---

# The two multigraph vertex problems reduce exactly to the simple ones: vertex
# mode is blind to parallel copies (see _split_capacity_matrix), so a multigraph
# and its underlying simple graph have the same vertex connectivity.  We mirror
# the simple-vertex surface into these keys rather than searching multigraphs,
# whose degenerate free-parallel fills would report a lower bound far above the
# true (simple) value and spike the plot.
_SURFACE_ALIASED_VERTEX = {
    "multi_undirected_vertex": "simple_undirected_vertex",
    "multi_directed_vertex":   "simple_directed_vertex",
}

# 12 variant configs for the surface computation.
_SURFACE_VARIANT_CONFIGS: list[dict] = [
    dict(key="simple_undirected_edge",   title="simple undirected edge",
         directed=False, simple=True,  hypergraph=False, r=3, separation="edge"),
    dict(key="simple_undirected_vertex", title="simple undirected vertex",
         directed=False, simple=True,  hypergraph=False, r=3, separation="vertex"),
    dict(key="simple_directed_edge",     title="simple directed arc",
         directed=True,  simple=True,  hypergraph=False, r=3, separation="edge"),
    dict(key="simple_directed_vertex",   title="simple directed vertex",
         directed=True,  simple=True,  hypergraph=False, r=3, separation="vertex"),
    dict(key="multi_undirected_edge",    title="multigraph undirected edge",
         directed=False, simple=False, hypergraph=False, r=3, separation="edge"),
    dict(key="multi_undirected_vertex",  title="multigraph undirected vertex",
         directed=False, simple=False, hypergraph=False, r=3, separation="vertex"),
    dict(key="multi_directed_edge",      title="multigraph directed arc",
         directed=True,  simple=False, hypergraph=False, r=3, separation="edge"),
    dict(key="multi_directed_vertex",    title="multigraph directed vertex",
         directed=True,  simple=False, hypergraph=False, r=3, separation="vertex"),
    dict(key="hyper_undirected_edge",    title="hypergraph undirected edge",
         directed=False, simple=True,  hypergraph=True,  r=3, separation="edge"),
    dict(key="hyper_undirected_vertex",  title="hypergraph undirected vertex",
         directed=False, simple=True,  hypergraph=True,  r=3, separation="vertex"),
    dict(key="hyper_directed_edge",      title="hypergraph directed arc",
         directed=True,  simple=True,  hypergraph=True,  r=3, separation="edge"),
    dict(key="hyper_directed_vertex",    title="hypergraph directed vertex",
         directed=True,  simple=True,  hypergraph=True,  r=3, separation="vertex"),
]


def _surface_known_value(vkey: str, n: int, m: int) -> int | None:
    """The proved exact value at ``(n, m)`` for ``vkey``, or ``None`` if open here.

    Returns the closed-form extremal value precisely in the regime where the
    thesis proves it, so the surface can colour those bars as exact (blue)
    rather than leaving every bar a search lower bound.  Outside the proved
    regime it returns ``None`` and the caller falls back to a discovery search
    (a purple lower bound).  Each value is capped at the trivial maximum for
    its model, since the closed form overshoots in the small-``n`` large-``m``
    corner where no graph that dense exists.
    """
    tri_simple = n * (n - 1) // 2
    tri_dir = n * (n - 1)
    tri_hyp = math.comb(n, 3)
    if vkey == "simple_undirected_edge":            # Mader, all m
        return min(simple_undirected_edge(n, m), tri_simple)
    if vkey == "simple_undirected_vertex":          # Leonard, m<=4
        return min(simple_undirected_edge(n, m), tri_simple) if m <= 4 else None
    if vkey == "simple_directed_edge":              # exact only at m=2
        return min(directed_arc_lower_bound(n, 2), tri_dir) if m == 2 else None
    if vkey == "simple_directed_vertex":            # exact only at m=2
        return min(directed_arc_lower_bound(n, 2), tri_dir) if m == 2 else None
    if vkey == "multi_undirected_edge":             # multi-tree bound, all m
        return min(multigraph_undirected_edge(n, m), (m - 1) * tri_simple)
    if vkey == "multi_undirected_vertex":           # = simple vertex, m<=4
        return min(simple_undirected_edge(n, m), tri_simple) if m <= 4 else None
    if vkey == "multi_directed_edge":               # thm:dir-multi-full, all n and m
        return min(directed_multigraph_arc(n, m), (m - 1) * tri_dir)
    if vkey == "multi_directed_vertex":             # = simple digraph, exact m=2
        return min(directed_arc_lower_bound(n, 2), tri_dir) if m == 2 else None
    if vkey == "hyper_undirected_edge":             # Gomory-Hu, simple-attaining iff m-1<=C(n-2,r-2)
        known = _hyper_edge_simple_proved(n, m, 3)
        return min(known, tri_hyp) if known is not None else None
    if vkey == "hyper_undirected_vertex":           # incidence-rank lemma; see _hyper_vertex_simple_proved
        known = _hyper_vertex_simple_proved(n, m, 3)
        return min(known, tri_hyp) if known is not None else None
    # hyper_directed_edge, hyper_directed_vertex: open (new model), no formula.
    return None


def compute_surface_cache(
    n_range: tuple[int, int] = (3, 9),
    m_range: tuple[int, int] = (2, 6),
    max_seconds: float = 20.0,
    cache_path: str | Path = "figures/surface_cache.json",
) -> dict:
    """Compute the optimal bound at every (variant, n, m) triple, save to a JSON cache.

    Returns the cache dict: ``{variant_key: {str(n): {str(m): {value, bound}}}}``.
    Where the value is proved (see :func:`_surface_known_value`) the bound is
    recorded as ``"exact"`` using the closed form; otherwise a discovery search
    supplies a ``"lower"`` bound.  Missing entries are skipped on later runs.
    """
    cache_path = Path(cache_path)
    meta = _cache_metadata(
        "surface", n_range=n_range, m_range=m_range,
        max_seconds=max_seconds, seed=0)
    invalidated = False
    if cache_path.exists():
        with open(cache_path) as f:
            cache = json.load(f)
        if cache.pop("_meta", None) != meta:
            cache = {}
            invalidated = True
    else:
        cache = {}

    changed = invalidated
    ns = list(range(n_range[0], n_range[1] + 1))
    ms = list(range(m_range[0], m_range[1] + 1))

    for cfg in _SURFACE_VARIANT_CONFIGS:
        vkey = cfg["key"]
        if vkey in _SURFACE_ALIASED_VERTEX:
            continue  # filled by mirroring its simple counterpart, below
        if vkey not in cache:
            cache[vkey] = {}
        for n in ns:
            sn = str(n)
            if sn not in cache[vkey]:
                cache[vkey][sn] = {}
            for m in ms:
                sm = str(m)
                known = _surface_known_value(vkey, n, m)
                if known is not None:
                    # Proved regime: use the closed form, mark it exact (blue).
                    # Always (re)write, so an older cache whose every cell was
                    # tagged "lower" is corrected here without recomputation.
                    entry = {"value": known, "bound": "exact"}
                    if cache[vkey][sn].get(sm) != entry:
                        cache[vkey][sn][sm] = entry
                        changed = True
                    continue
                if sm in cache[vkey][sn]:
                    continue  # metadata match: this cell used the same source and budget
                print(f"  surface: {cfg['title']}  n={n}  m={m}", flush=True)
                res = solve(
                    n, m,
                    directed=cfg["directed"],
                    simple=cfg["simple"],
                    hypergraph=cfg["hypergraph"],
                    r=cfg["r"],
                    exhaustive=False,
                    separation=cfg["separation"],
                    max_seconds=max_seconds,
                    seed=0,
                )
                cache[vkey][sn][sm] = {"value": res.value, "bound": res.bound}
                changed = True

    # Mirror the simple-vertex surfaces into their multigraph aliases, so the two
    # provably-equal problems show identical bars instead of two independent
    # (and possibly degenerate) searches.
    for multi_key, simple_key in _SURFACE_ALIASED_VERTEX.items():
        if simple_key in cache and cache.get(multi_key) != cache[simple_key]:
            cache[multi_key] = copy.deepcopy(cache[simple_key])
            changed = True

    if changed:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump({"_meta": meta, **cache}, f)

    return cache


def plot_variant_3d_surfaces(
    cache_path: str | Path,
    path: str | Path,
) -> None:
    """3-D bar chart of the optimal bound over the (n, m) grid, all sixteen variants.

    Each bar's height is the bound value; exact points are blue, lower-bound
    points are purple.  The 3x4 layout matches the flat grid figure.
    """
    with open(cache_path) as f:
        cache = json.load(f)

    fig = plt.figure(figsize=(20, 13))
    row_names = ("simple", "multigraph", "hypergraph $r=3$")

    for idx, cfg in enumerate(_SURFACE_VARIANT_CONFIGS):
        vkey = cfg["key"]
        ax = fig.add_subplot(3, 4, idx + 1, projection="3d")

        variant_data = cache.get(vkey, {})
        ns_exact, ms_exact, vs_exact = [], [], []
        ns_lower, ms_lower, vs_lower = [], [], []

        for sn, m_dict in sorted(variant_data.items(), key=lambda x: int(x[0])):
            n = int(sn)
            for sm, entry in sorted(m_dict.items(), key=lambda x: int(x[0])):
                m_val = int(sm)
                v = entry["value"]
                if entry["bound"] == "exact":
                    ns_exact.append(n)
                    ms_exact.append(m_val)
                    vs_exact.append(v)
                else:
                    ns_lower.append(n)
                    ms_lower.append(m_val)
                    vs_lower.append(v)

        dx = dy = 0.6
        if ns_lower:
            ax.bar3d(
                [x - dx / 2 for x in ns_lower],
                [y - dy / 2 for y in ms_lower],
                [0] * len(vs_lower),
                dx, dy, vs_lower,
                color=_VIOLET, alpha=0.7, shade=True,
                edgecolor="white", linewidth=0.25,
            )
        if ns_exact:
            ax.bar3d(
                [x - dx / 2 for x in ns_exact],
                [y - dy / 2 for y in ms_exact],
                [0] * len(vs_exact),
                dx, dy, vs_exact,
                color=_KUL_BLUE, alpha=0.9, shade=True,
                edgecolor="white", linewidth=0.25,
            )

        # Same camera for every panel so the sixteen are read side by side, and a
        # z-axis anchored at 0 so bar heights are comparable within a panel.
        ax.view_init(elev=24, azim=-58)
        peak = max(vs_exact + vs_lower, default=1)
        ax.set_zlim(0, peak * 1.05)
        for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
            pane.pane.set_alpha(0.04)

        ax.set_title(cfg["title"], fontsize=7.5, pad=2)
        ax.set_xlabel("$n$", fontsize=7, labelpad=2)
        ax.set_ylabel("$m$", fontsize=7, labelpad=2)
        ax.set_zlabel("bound", fontsize=7, labelpad=2)
        ax.tick_params(labelsize=6)

    # Row labels
    for row, name in enumerate(row_names):
        row_ax = fig.axes[row * 4]
        row_ax.text2D(-0.28, 0.5, name, transform=row_ax.transAxes,
                      rotation=90, ha="center", va="center",
                      fontsize=11, fontweight="bold", color=_KUL_DARK)

    # Manual legend patches
    legend_elems = [
        Patch(facecolor=_KUL_BLUE, alpha=0.85, label="exact (proved)"),
        Patch(facecolor=_VIOLET,   alpha=0.65, label="lower bound (search)"),
    ]
    fig.legend(handles=legend_elems, loc="lower center", ncol=2,
               fontsize=10, framealpha=0.9)

    fig.suptitle("Erdős 915: optimal bound over $(n, m)$, "
                 "blue where proved, purple where only a search lower bound is known",
                 fontsize=13, y=0.99)
    _save(path, tight=False)


# --- 3-D THRESHOLD HISTOGRAM: lambda^max distribution vs p for three variants ---


def plot_conn_threshold_3d(
    path: str | Path,
    n: int = 30,
    m: int = 3,
    p_values: list[float] | None = None,
    samples: int = 400,
    seed: int = 7,
) -> None:
    """3-D bar chart of the lambda_max distribution over density, for three variants.

    x = density in units of that model's OWN threshold, y = lambda_max value,
    z = fraction of samples.  Each panel is swept in units of its own p*, and the
    threshold line sits at 1 in all three, because the models do NOT share a
    density scale.  The threshold is where a vertex's expected degree reaches m,
    which for a graph is p*(n-1) = m, giving p* = m/n, but for an r-uniform
    binomial hypergraph is p*C(n-1, r-1) = m, giving p* = m/C(n-1, r-1) =
    Theta(m/n^(r-1)).  Plotting the hypergraph panel against m/n would put the
    line in the wrong place by a factor of order n^(r-2).  Only the graph panels
    are covered by thm:gnp-threshold; the hypergraph panel is an observation.

    Three panels: undirected edge (uses ``n``), directed arc (uses ``n``),
    hypergraph edge (uses min(n, 8) to keep flow computation fast).
    """
    # Sweep in units of the model's own threshold, so all three panels are
    # directly comparable and each transition is visible where it actually is.
    ratios = ([i / 5.0 for i in range(1, 20)] if p_values is None else None)

    rng = random.Random(seed)
    # Hypergraph flow computation scales poorly: cap n at 8 for that panel.
    n_hyper = min(n, 8)

    # The hypergraph threshold is m / C(n-1, r-1) with r = 3.  Write the binomial
    # with its arguments already evaluated: matplotlib's mathtext lays out
    # "\binom{8-1}{2}" so that the "-1" reads as a superscript on the 8, which
    # renders as a garbled binomial rather than "7 choose 2".
    hyper_top = n_hyper - 1
    hyper_pstar = math.comb(hyper_top, 2)
    variants_3d = [
        dict(label=f"undirected edge ($n={n}$)", directed=False, separation="edge",
             hypergraph=False, panel_n=n, p_star=m / n,
             star_text=f"$m/n = {m}/{n}$"),
        dict(label=f"directed arc ($n={n}$)",    directed=True,  separation="edge",
             hypergraph=False, panel_n=n, p_star=m / n,
             star_text=f"$m/n = {m}/{n}$"),
        dict(label=f"hypergraph edge ($r=3$, $n={n_hyper}$)", directed=False,
             separation="edge", hypergraph=True, panel_n=n_hyper,
             p_star=m / hyper_pstar,
             star_text=(fr"$m/\binom{{{hyper_top}}}{{2}} = "
                        fr"{m}/{hyper_pstar}$")),
    ]

    fig = plt.figure(figsize=(18, 6))

    for panel_idx, vdesc in enumerate(variants_3d):
        ax = fig.add_subplot(1, 3, panel_idx + 1, projection="3d")
        panel_n = vdesc["panel_n"]
        p_star = vdesc["p_star"]
        panel_ps = (p_values if p_values is not None
                    else [min(1.0, r * p_star) for r in ratios])

        all_conn_vals: list[int] = []
        dist_by_p: list[tuple[float, list[int]]] = []

        for p in panel_ps:
            conn_list: list[int] = []
            for _ in range(samples):
                if vdesc["hypergraph"]:
                    cands = _hyperedge_candidates(panel_n, 3, vdesc["directed"])
                    chosen = [e for e in cands if rng.random() < p]
                    h = Hypergraph(panel_n, chosen, directed=vdesc["directed"])
                    c = max_hyper_connectivity(h, vertex_split=False)
                else:
                    g = sample_random_graph(panel_n, p, vdesc["directed"], rng)
                    if vdesc["separation"] == "edge":
                        c = max_edge_connectivity(g)
                    else:
                        c = max_vertex_connectivity(g)
                conn_list.append(c)
            dist_by_p.append((p, conn_list))
            all_conn_vals.extend(conn_list)

        if not all_conn_vals:
            continue

        lo, hi = 0, max(all_conn_vals)
        levels = list(range(lo, hi + 1))

        # x is the density in units of this panel's own threshold.
        xs = [p / p_star for p, _ in dist_by_p]
        width = 0.9 * min((b - a) for a, b in zip(xs, xs[1:])) if len(xs) > 1 else 0.1
        for x, (_, conn_list) in zip(xs, dist_by_p):
            total = len(conn_list)
            for lv in levels:
                frac = conn_list.count(lv) / total
                if frac > 0:
                    ax.bar3d(x - width / 2, lv - 0.4, 0, width, 0.8, frac,
                             color=_KUL_BLUE, alpha=0.7, shade=True)

        # The threshold sits at 1 in these units, by construction.
        for lv in levels:
            ax.plot([1.0, 1.0], [lv - 0.4, lv + 0.4], [0, 0],
                    color=_WARM, linewidth=0.5, alpha=0.4)
        zmax = max(conn_list.count(lv) / len(conn_list)
                   for _, conn_list in dist_by_p
                   for lv in levels
                   if conn_list.count(lv) > 0)
        ax.plot([1.0, 1.0], [lo, hi], [zmax * 0.9, zmax * 0.9],
                color=_WARM, linewidth=2.5, linestyle="--", label="$p / p^* = 1$")

        ax.set_title(f"{vdesc['label']}\n$p^* = $ {vdesc['star_text']}", fontsize=9)
        ax.set_xlabel("$p / p^*$", fontsize=9)
        ax.set_ylabel(r"$\lambda^{\max}$", fontsize=9)
        ax.set_zlabel("fraction", fontsize=9)
        ax.tick_params(labelsize=7)

    fig.suptitle(
        fr"Distribution of $\lambda^{{\max}}$ against density, $m = {m}$, each model "
        fr"in units of its own threshold $p^*$ (the density at which a vertex's "
        fr"expected degree reaches $m$)",
        fontsize=11,
    )
    _save(path, tight=False)


# --- OPEN-VARIANT EXPLORATION: hypergraph vertex connectivity, fractional search tools ---


def max_hyper_vertex_connectivity(hypergraph: Hypergraph) -> int:
    """``kappa^max`` for the hypergraph vertex problem (readability wrapper)."""
    return max_hyper_connectivity(hypergraph, vertex_split=True)


def _hyper_codegree_ok(edges, bound: int) -> bool:
    """Necessary feasibility filter: two vertices in > ``bound`` common
    hyperedges already carry that many one-step disjoint Berge routes."""

    codegree: Counter = Counter()
    for edge in edges:
        for pair in combinations(sorted(edge), 2):
            codegree[pair] += 1
            if codegree[pair] > bound:
                return False
    return True


def hyper_vertex_feasible_exists(n: int, r: int, m: int, q: int,
                                 multi: bool = True) -> bool:
    """Exhaustively decide whether some ``r``-uniform (multi-)hypergraph on
    ``n`` vertices with ``q`` hyperedges has ``kappa^max <= m - 1``.

    Repeated hyperedges are allowed when ``multi`` is set (they are forced
    infeasible at m = 2 by the codegree filter, so m = 2 needs no repeats).
    Practical up to roughly C(C(n,r), q) ~ a few hundred thousand candidates.
    """
    all_edges = list(combinations(range(n), r))
    chooser = combinations_with_replacement if multi else combinations
    for sub in chooser(all_edges, q):
        if not _hyper_codegree_ok(sub, m - 1):
            continue
        candidate = Hypergraph(n, [frozenset(edge) for edge in sub])
        feasible = True
        for s in range(n):
            for t in range(s + 1, n):
                if hyper_connectivity(candidate, s, t, vertex_split=True) > m - 1:
                    feasible = False
                    break
            if not feasible:
                break
        if feasible:
            return True
    return False


def verify_hyper_vertex_value(n: int, r: int, m: int) -> bool:
    """Confirm exhaustively that the ``r``-uniform vertex value at ``(n, m)``
    equals ``floor((m-1)(n-1)/(r-1))``: the bound's witness is feasible
    (kappa^max <= m-1) and one more hyperedge never is."""
    target = ((m - 1) * (n - 1)) // (r - 1)
    if m == 2:
        witness = star_hypertree(n, r)
        attained = (len(witness.hyperedges) == target
                    and max_hyper_vertex_connectivity(witness) <= 1)
    else:
        attained = hyper_vertex_feasible_exists(n, r, m, target)
    return attained and not hyper_vertex_feasible_exists(n, r, m, target + 1)


def max_feasible_hyperedges(
    n: int, r: int, m: int,
    *, directed: bool = False, vertex_split: bool = False, kind: str = "forward",
    simple: bool = True, time_limit: float = 20.0, seed_lb: int = 0,
) -> tuple[int, bool]:
    """Largest number of ``r``-uniform hyperedges with Berge connectivity ``<= m-1``.

    Returns ``(value, exact)``.  ``exact`` is ``True`` when the branch and bound
    below proved optimality within ``time_limit`` (the value is then the true
    extremal number for that variant); otherwise ``value`` is the best feasible
    construction found, a lower bound.  ``kind`` selects the directed orientation
    model (forward / backward / general); for the undirected case it is ignored.

    The search is a depth-first include/exclude over the candidate hyperedges with
    two prunings.  Feasibility is monotone (adding a hyperedge never lowers any
    Berge connectivity), so once the active set is infeasible no superset can be
    feasible and the include branch is dropped; and a branch is cut once
    ``active + remaining`` cannot beat the best feasible count already seen.  A
    short randomised warm start raises that incumbent first, so the bound prune
    bites early.  ``seed_lb`` is a caller-certified feasible lower bound (e.g. the
    forward value when maximising over the general model, which contains every
    forward hypergraph).  Because it arrives without a witness, it is never used
    for pruning: it is merged only into an inexact timeout result.  A completed
    search either confirms it or rejects it, so an unverified number can never be
    reported as an exact optimum.
    """
    if seed_lb < 0:
        raise ValueError("seed_lb must be non-negative")
    deadline = time.time() + time_limit
    # Warm start: a short greedy randomised lower bound sharpens the bound prune;
    # kept brief so the branch and bound, which does the actual proving, keeps
    # the budget.
    warm_share = min(0.3 * time_limit, 1.5)
    lb, _ = _random_hypergraph_search(
        n, r, m, time.time() + warm_share, seed=0,
        directed=directed, vertex_split=vertex_split, kind=kind, simple=simple)

    candidates = _hyperedge_candidates(n, r, directed, kind=kind)
    cap = _hyper_multiplicity_cap(m, simple)
    total = len(candidates)
    best = [lb]
    timed_out = [False]
    active = Hypergraph(n, directed=directed)

    def dfs(pos: int, count: int) -> None:
        if timed_out[0]:
            return
        if count + cap * (total - pos) <= best[0]:
            return                                   # cannot beat the incumbent
        if time.time() > deadline:
            timed_out[0] = True
            return
        if pos == total:
            if count > best[0]:
                best[0] = count
            return
        # Give candidates[pos] each multiplicity from cap down to 0.  Feasibility
        # is monotone in multiplicity as well as in membership, so the moment one
        # multiplicity is infeasible every larger one is too and the rest of the
        # descending run is skipped.
        added = 0
        for q in range(1, cap + 1):
            active.add_hyperedge(candidates[pos])
            added += 1
            if max_hyper_connectivity(active, vertex_split=vertex_split) > m - 1:
                break
            dfs(pos + 1, count + q)
        for _ in range(added):
            active.hyperedges.pop()
        # Exclude candidates[pos] entirely.
        dfs(pos + 1, count)

    dfs(0, 0)
    exact = not timed_out[0]
    if exact and seed_lb > best[0]:
        raise ValueError(
            f"seed_lb={seed_lb} was claimed feasible, but exhaustive search "
            f"proved the optimum is only {best[0]}")
    return (best[0] if exact else max(best[0], seed_lb)), exact


def _c_flat(mu: np.ndarray) -> tuple[np.ndarray, "_ct.POINTER[_ct.c_int]"]:
    """Return a contiguous int32 copy of ``mu`` and a ctypes c_int pointer into it."""
    flat = np.ascontiguousarray(mu, dtype=np.int32)
    ptr = flat.ctypes.data_as(_ct.POINTER(_ct.c_int))
    return flat, ptr   # caller must keep flat alive while ptr is in use


def _tiny_maxflow(mu: np.ndarray, n: int, s: int, t: int, cap: int) -> bool:
    """Return True iff the integer max-flow from s to t under capacities ``mu``
    exceeds ``cap``.  Plain DFS augmentation (Ford-Fulkerson with a stack, not
    BFS/Edmonds-Karp); built for n <= 7, where it beats both the networkx call
    and scipy's C ``maximum_flow`` by orders of magnitude inside the hot
    enumeration/search loops (measured ~16x faster than scipy at n=7: the
    library calls' per-call sparse-matrix construction and dispatch overhead
    dominates at this size, while the ``cap`` lets this routine stop after
    cap+1 augmenting paths).  Correct for integer capacities: each augmentation
    increases flow by at least 1, so the loop terminates in at most
    max-flow-value iterations."""
    if _C is not None and n <= 7:
        flat, ptr = _c_flat(mu)
        return bool(_C.tiny_maxflow(ptr, n, s, t, cap))
    residual = mu.astype(int)          # astype already returns a fresh, mutable copy
    flow = 0
    while flow <= cap:
        parent = [-1] * n
        parent[s] = s
        queue = [s]
        while queue and parent[t] == -1:
            u = queue.pop()
            for v in range(n):
                if parent[v] == -1 and residual[u, v] > 0:
                    parent[v] = u
                    queue.append(v)
        if parent[t] == -1:
            return False  # flow is maximal and <= cap
        bottleneck = 10 ** 9
        v = t
        while v != s:
            bottleneck = min(bottleneck, residual[parent[v], v])
            v = parent[v]
        v = t
        while v != s:
            residual[parent[v], v] -= bottleneck
            residual[v, parent[v]] += bottleneck
            v = parent[v]
        flow += bottleneck
    return True


def _canonical_form(mu: np.ndarray) -> bytes:
    """A canonical key for the isomorphism class of a directed multigraph.

    The key is the lexicographically smallest flattened multiplicity matrix over
    all vertex relabellings: two multiplicity matrices have the same key iff one
    is a vertex permutation of the other.  This is the SOURCE OF TRUTH for
    isomorphism here, with no dependency on any external library, so the
    enumeration's correctness never rests on an outside binary.  For ``n=7`` it is
    5040 permutations per graph, which is cheap on CPU; storing one key per class
    is what bounds the enumeration's memory to the number of classes rather than
    the number of labelled copies.
    """
    # Canonical keys must not depend on the caller's native integer width.
    mu = np.ascontiguousarray(mu, dtype=np.int32)
    n = mu.shape[0]
    if _C is not None and n <= 7:
        flat, ptr = _c_flat(mu)
        out = np.empty(n * n, dtype=np.int32)
        out_ptr = out.ctypes.data_as(_ct.POINTER(_ct.c_int))
        _C.canonical_form_min(ptr, n, out_ptr)
        return out.tobytes()
    best: bytes | None = None
    for perm in permutations(range(n)):
        p = list(perm)
        cand = mu[np.ix_(p, p)].tobytes()
        if best is None or cand < best:
            best = cand
    assert best is not None  # n >= 1, so at least the identity permutation exists
    return best


def enumerate_extremal_directed_multigraphs(
    n: int, m: int, target_arcs: int, max_degree: int | None = None,
    up_to_iso: bool = True,
) -> list[np.ndarray]:
    """Exhaustively list the directed multigraphs on ``n`` vertices with
    multiplicities in {0..m-1}, ``lambda^max <= m-1``, exactly ``target_arcs``
    arcs and (optionally) maximum total degree at most ``max_degree``.

    This is the finite-base tool for the m = 3 chain (see claude.md and the
    commented rem:odd-step-roadmap): the characterisations at n = 4, 5 feed
    the recursion behind statement (b) at n = 7.  DFS in vertex-block order
    with three prunings: multiplicity capacity, the induced-subgraph arc bound
    on every completed prefix, and exact flow checks on completed prefixes
    (induced flows only grow, so a violation is final).

    SOUNDNESS: the induced-subgraph bound is a PROVED upper bound for j <= 6
    (from the cut-counting MILP; see ``known`` dict below).  For j >= 7 it
    falls back to the CONJECTURED bipartite bound floor(j^2/4), which is not
    yet proved.  Therefore this function is a sound complete search only for
    n <= 6.  For n >= 7 it is a heuristic lower-bound search: it may miss
    extremal graphs whose j=7 prefix exceeds the bipartite bound (if the
    conjecture is false) or whose search branch was pruned by it.
    Returns multiplicity matrices, deduplicated up to vertex permutation when
    ``up_to_iso`` is set.  Deduplication is STREAMED through a canonical form
    (:func:`_canonical_form`) as graphs are found, so peak memory is bounded by
    the number of isomorphism classes rather than the number of labelled copies
    (the previous buffer-everything approach exhausted RAM on n=7).  The returned
    list, and its order, are unchanged by this.
    """
    # Ordered pairs grouped so that all pairs inside {0..j} precede vertex j+1.
    order: list[tuple[int, int]] = []
    for j in range(1, n):
        for i in range(j):
            order.append((i, j))
            order.append((j, i))
    block_end = {j: 2 * ((j + 1) * j // 2) for j in range(1, n)}  # prefix length
    # SOUNDNESS NOTE: for j <= 6 the prefix cap (m-1)*M*(j) is a PROVED upper
    # bound, so pruning at that cap is safe.  For j >= 7, _PROVEN_MSTAR.get(j, 0) == 0
    # and we fall back to (m-1)*floor(j^2/4), which equals the conjectured
    # bipartite bound and is NOT yet proved.  Any call with n >= 7 therefore
    # uses an unverified pruning at the j=7 boundary: the enumeration is sound
    # as a lower-bound search but cannot certify completeness for n >= 7.
    # To produce a proof for n=7 the j=7 pruning must be disabled or replaced
    # by a proved bound (e.g. from the MILP once M*(7) is confirmed).
    prefix_cap = {j: (m - 1) * max(_PROVEN_MSTAR.get(j, 0), (j * j) // 4)
                  for j in range(2, n + 1)}

    mu = np.zeros((n, n), dtype=int)
    total_pairs = len(order)
    # Stream results straight into the deduplicated output instead of buffering
    # every labelled feasible matrix first.  Memory is then bounded by the number
    # of ISOMORPHISM CLASSES (one canonical key in `seen`, one representative in
    # the list), not by the number of labelled copies, which is what previously
    # blew up to tens of gigabytes on n=7.  The set of matrices returned, and
    # their order, are identical to the old buffer-then-dedup code.
    seen: set[bytes] = set()
    representatives: list[np.ndarray] = []

    def _record(matrix: np.ndarray) -> None:
        # The DFS only checked prefixes {0..j} for j < n, so confirm the full
        # n-vertex graph is feasible before keeping it (cheap, and done first so a
        # rejected graph never pays for the canonical form).
        if any(_tiny_maxflow(matrix, n, s, t, m - 1)
               for s in range(n) for t in range(n) if s != t):
            return
        if up_to_iso:
            canon = _canonical_form(matrix)
            if canon in seen:
                return
            seen.add(canon)
        representatives.append(matrix.copy())

    def dfs(pos: int, arcs: int) -> None:
        if arcs + (m - 1) * (total_pairs - pos) < target_arcs or arcs > target_arcs:
            return
        if pos == total_pairs:
            if arcs == target_arcs:
                _record(mu)
            return
        completed = next((j for j in range(1, n) if block_end[j] == pos), None)
        if completed is not None:
            j = completed + 1  # prefix {0..completed} has j vertices
            if arcs > prefix_cap.get(j, 10 ** 9):
                return
            for s in range(j):
                for t in range(j):
                    if s != t and _tiny_maxflow(mu, n, s, t, m - 1):
                        return
        u, v = order[pos]
        for value in range(m):
            mu[u, v] = value
            if max_degree is None or (mu[u, :].sum() + mu[:, u].sum() <= max_degree
                                      and mu[v, :].sum() + mu[:, v].sum() <= max_degree):
                dfs(pos + 1, arcs + value)
        mu[u, v] = 0

    dfs(0, 0)
    return representatives


def _geng_support_graphs(
    n: int, min_edges: int, max_edges: int, geng_path: str = "geng",
) -> Iterator[list[tuple[int, int]]]:
    """Yield one edge list per isomorphism class of simple graph on ``n``
    vertices with ``min_edges`` to ``max_edges`` edges, via nauty's ``geng``.

    Each edge is an ordered tuple ``(u, v)`` with ``u < v``; isolated vertices
    are kept (``geng`` always emits all ``n`` vertices).  ``geng`` writes the
    non-isomorphic graphs in graph6 to stdout and we parse each with _graph6_edges.
    Raises ``RuntimeError`` if ``geng`` is not on PATH.
    """
    exe = shutil.which(geng_path)
    if exe is None:
        raise RuntimeError(
            f"nauty's '{geng_path}' was not found on PATH.  Install nauty "
            "(e.g. the 'nauty' package) or pass geng_path=...; the "
            "generation enumerator needs it."
        )
    if max_edges < min_edges:
        return
    proc = subprocess.run(
        [exe, str(n), f"{min_edges}:{max_edges}"],
        capture_output=True, check=True,
    )
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        yield _graph6_edges(line)


def _graph6_edges(data: bytes) -> list[tuple[int, int]]:
    """Decode one graph6 line (geng's output format) into its ``(i, j)`` edges, ``i < j``.

    graph6 stores ``n`` in the first byte (offset 63), then the upper-triangle
    adjacency bits column by column (for ``j`` from 1, all ``i < j``), six bits per
    subsequent byte, high bit first.  We only ever generate ``n <= 12`` supports, so
    the single-byte header case is all that is needed and the format needs no
    networkx to read.
    """
    values = [byte - 63 for byte in data]
    n = values[0]
    bits = [(value >> shift) & 1 for value in values[1:] for shift in range(5, -1, -1)]
    index = 0
    edges: list[tuple[int, int]] = []
    for j in range(1, n):
        for i in range(j):
            if bits[index]:
                edges.append((i, j))
            index += 1
    return edges


def _decorate_support_worker(task: tuple) -> list[np.ndarray]:
    """Every feasible extremal decoration of ONE undirected support graph.

    Module-level and picklable, so :func:`enumerate_extremal_directed_multigraphs_via_generation`
    can fan the supports out across processes (each support is independent, and
    two non-isomorphic supports can never yield the same multigraph).  Returns one
    multiplicity matrix per decoration, deduplicated within this support when
    ``up_to_iso``.  The decoration logic and its pruning are identical to the
    sequential generator; only the ownership of the scratch arrays moves here.
    """
    n, m, target_arcs, max_degree, up_to_iso, edges = task
    per_edge_max = 2 * (m - 1)
    # Per-edge states (a, b) = (mu[u,v], mu[v,u]) excluding (0,0): a support edge
    # carries at least one arc in some direction.
    states = [(a, b) for a in range(m) for b in range(m) if (a, b) != (0, 0)]
    mu = np.zeros((n, n), dtype=int)
    deg = np.zeros(n, dtype=int)
    out_deg = np.zeros(n, dtype=int)
    in_deg = np.zeros(n, dtype=int)
    seen: set[bytes] = set()
    reps: list[np.ndarray] = []

    def feasible_prefix(j: int) -> bool:
        cap = m - 1
        for s in range(j):
            if out_deg[s] <= cap:
                continue
            for t in range(j):
                if s != t and in_deg[t] > cap and _tiny_maxflow(mu, n, s, t, cap):
                    return False
        return True

    # Decorate in vertex-block order: pairs sorted by larger endpoint, then
    # smaller, so after the last pair whose larger endpoint is w the induced
    # subgraph on {0..w} is complete and the prefix bound for size w+1 applies.
    sps = sorted(edges, key=lambda e: (e[1], e[0]))
    bound: list[int | None] = [None] * len(sps)
    for i, (_, w) in enumerate(sps):
        if i + 1 == len(sps) or sps[i + 1][1] > w:
            bound[i] = w + 1

    def decorate(idx: int, arcs: int) -> None:
        remaining = len(sps) - idx
        if arcs + remaining > target_arcs:
            return
        if arcs + remaining * per_edge_max < target_arcs:
            return
        if idx == len(sps):                       # every support edge decorated
            if arcs == target_arcs and feasible_prefix(n):
                if up_to_iso:
                    canon = _canonical_form(mu)
                    if canon in seen:
                        return
                    seen.add(canon)
                reps.append(mu.copy())
            return
        u, v = sps[idx]
        j = bound[idx]            # prefix size to verify after this edge, or None
        for a, b in states:
            s = a + b
            if arcs + s > target_arcs:
                continue
            if max_degree is not None and (deg[u] + s > max_degree
                                           or deg[v] + s > max_degree):
                continue
            mu[u, v] = a
            mu[v, u] = b
            deg[u] += s
            deg[v] += s
            out_deg[u] += a; in_deg[v] += a
            out_deg[v] += b; in_deg[u] += b
            ok = True
            if j is not None:     # block boundary: prefix {0..j-1} is complete
                cap = _PROVEN_MSTAR.get(j)        # j == prefix size
                if cap is not None and arcs + s > (m - 1) * cap:
                    ok = False                    # PROVED induced-arc bound
                elif not feasible_prefix(j):
                    ok = False
            if ok:
                decorate(idx + 1, arcs + s)
            deg[u] -= s
            deg[v] -= s
            out_deg[u] -= a; in_deg[v] -= a
            out_deg[v] -= b; in_deg[u] -= b
            mu[u, v] = 0
            mu[v, u] = 0

    decorate(0, 0)
    return reps


def enumerate_extremal_directed_multigraphs_via_generation(
    n: int, m: int, target_arcs: int, max_degree: int | None = None,
    up_to_iso: bool = True, geng_path: str = "geng", parallel: bool = True,
) -> list[np.ndarray]:
    """Sound, geng-seeded twin of :func:`enumerate_extremal_directed_multigraphs`.

    Lists every directed multigraph on ``n`` vertices with multiplicities in
    {0..m-1}, ``lambda^max <= m-1``, exactly ``target_arcs`` arcs and
    (optionally) maximum total degree ``<= max_degree``, deduplicated up to
    isomorphism.  Same object and same return format (multiplicity matrices) as
    the DFS enumerator.

    Following J. Goedgebeur's suggestion, the underlying undirected SUPPORT
    graph (the pairs carrying at least one arc) is generated once per
    isomorphism class by nauty's ``geng``; each support is then decorated, in
    vertex-block order, with a directed multiplicity pair ``(mu[u,v], mu[v,u])``
    in {0..m-1}^2 minus (0,0) per support edge.  Pruning is the running arc
    total, the degree cap, and -- at each completed prefix on ``j`` vertices --
    the PROVED induced-arc bound ``arcs(prefix) <= (m-1) M*(j)`` together with a
    prefix feasibility check (induced max-flows only grow, so a prefix that
    already exceeds the cap is dead).

    Soundness for every ``n``.  Two directed multigraphs with non-isomorphic
    supports are non-isomorphic, and every isomorphism class with a given
    support class has a labelling whose support equals geng's representative, so
    decorating every representative and canonical-deduplicating returns exactly
    one matrix per isomorphism class.  Crucially the induced-arc bound is used
    ONLY for ``j <= 6``, where ``M*(j)`` is proved; for ``j >= 7`` no arc bound
    is applied (only the global ``target_arcs`` and feasibility).  This is the
    difference from :func:`enumerate_extremal_directed_multigraphs`, which falls
    back to the CONJECTURED ``floor(j^2/4)`` at ``j >= 7`` and is therefore a
    complete search only for ``n <= 6``.  This generator is complete for all
    ``n`` (it never assumes an unproved value), so it can certify the finite
    ``n = 7`` classification once it finishes.

    Requires nauty's ``geng`` on PATH.  For ``n <= 6`` it returns the same set
    of isomorphism classes as :func:`enumerate_extremal_directed_multigraphs`;
    ``tests/test_solve`` checks that equality.

    With ``parallel`` (default) the supports are decorated concurrently across
    processor cores via a :class:`~concurrent.futures.ProcessPoolExecutor`, since
    each support is independent.  This is where the ``n = 7`` classification
    becomes practical on a multi-core machine: the work scales with the number of
    supports, which is exactly what fans out.  It falls back to a sequential run
    (with a warning) where multiprocessing is unavailable, and the result is
    identical either way.
    """
    if m < 1:
        raise ValueError("m must be >= 1")
    per_edge_max = 2 * (m - 1)            # most arcs one undirected pair can hold
    if per_edge_max == 0:                 # m == 1: only the empty graph is feasible
        return [np.zeros((n, n), dtype=int)] if target_arcs == 0 else []
    min_edges = (target_arcs + per_edge_max - 1) // per_edge_max
    max_edges = min(target_arcs, n * (n - 1) // 2)

    # geng emits each undirected support iso-class once, and decorating one
    # support is independent of the others (two non-isomorphic supports can never
    # yield the same multigraph), so the supports fan out across processes, each
    # with its own scratch arrays inside _decorate_support_worker.  The PROVED
    # M*(j) bound is applied there only for j <= 6; j >= 7 gets no arc bound, so
    # the search stays sound at every n.
    tasks = [(n, m, target_arcs, max_degree, up_to_iso, edges)
             for edges in _geng_support_graphs(n, min_edges, max_edges, geng_path)]

    representatives: list[np.ndarray] = []
    if parallel and len(tasks) > 1:
        try:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                # chunksize=1: supports vary wildly in cost, so hand them out one
                # at a time to keep every core busy to the end.
                for reps in executor.map(_decorate_support_worker, tasks,
                                         chunksize=1):
                    representatives.extend(reps)
        except (OSError, concurrent.futures.BrokenExecutor) as exc:
            warnings.warn(
                f"parallel support enumeration unavailable ({exc!r}); running "
                "sequentially", RuntimeWarning, stacklevel=2,
            )
            for task in tasks:
                representatives.extend(_decorate_support_worker(task))
    else:
        for task in tasks:
            representatives.extend(_decorate_support_worker(task))

    if up_to_iso:
        # Distinct geng supports give non-isomorphic multigraphs, so this final
        # canonical pass is only a safety net over the process-local per-support
        # dedup; it keeps exactly one representative per isomorphism class.
        seen: set[bytes] = set()
        unique: list[np.ndarray] = []
        for matrix in representatives:
            key = _canonical_form(matrix)
            if key not in seen:
                seen.add(key)
                unique.append(matrix)
        representatives = unique
    return representatives


# --- GALLERY: all non-isomorphic extremal graphs for small (n, m); entry point gallery_extremal_graphs ---


def _graph_from_mu(mu: np.ndarray, variant: Variant) -> Graph:
    """Wrap a multiplicity matrix in a fresh Graph (zero-copy)."""
    g = Graph(mu.shape[0], variant)
    g.mu[:] = mu
    return g


def _aut_count_matrix(mu: np.ndarray) -> int:
    """Count vertex permutations that preserve ``mu`` (equals |Aut(G)|)."""
    mu = np.ascontiguousarray(mu, dtype=np.int32)
    n = mu.shape[0]
    canon = _canonical_form(mu)
    count = sum(1 for perm in permutations(range(n))
                if mu[np.ix_(list(perm), list(perm))].tobytes() == canon)
    if count < 1:
        # The identity permutation is always an automorphism, so this is
        # unreachable unless _canonical_form and this scan disagree. Raise
        # rather than assert: callers divide by this count, and `python -O`
        # strips asserts.
        raise RuntimeError(f"automorphism count {count} < 1; "
                           "canonical form disagrees with the permutation scan")
    return count


def _dir_relabel_key(edge, p: list) -> tuple:
    """Permutation-relabelled key of one directed hyperedge.

    Both accepted storage forms are normalised to
    ``(tuple_of_tails, tuple_of_heads)``.  Besides making a legacy forward edge
    and its general-form equivalent canonicalise identically, the uniform shape
    lets a single collection safely contain both forms.
    """
    tails, heads = _dir_tails_heads(edge)
    return (tuple(sorted(p[t] for t in tails)),
            tuple(sorted(p[h] for h in heads)))


def _hyper_canonical(hyperedges: list, n: int, directed: bool) -> tuple:
    """Canonical key for a hyperedge collection under vertex permutation.

    Each edge is a frozenset (undirected) or a directed hyperedge in either the
    forward ``(tail, heads)`` or general ``(tails, heads)`` form.  Returns the
    lex-minimum over all n! relabellings.
    """
    best: tuple | None = None
    for perm in permutations(range(n)):
        p = list(perm)
        if directed:
            relabeled: tuple = tuple(sorted(_dir_relabel_key(edge, p) for edge in hyperedges))
        else:
            relabeled = tuple(sorted(
                tuple(sorted(p[v] for v in edge)) for edge in hyperedges
            ))
        if best is None or relabeled < best:
            best = relabeled
    return best  # type: ignore[return-value]


def _aut_count_hyper(hyperedges: list, n: int, directed: bool) -> int:
    """Count vertex permutations that preserve a hyperedge collection."""
    canon = _hyper_canonical(hyperedges, n, directed)

    def _relabel(p: list) -> tuple:
        if directed:
            return tuple(sorted(_dir_relabel_key(edge, p) for edge in hyperedges))
        return tuple(sorted(
            tuple(sorted(p[v] for v in edge)) for edge in hyperedges
        ))

    return sum(1 for perm in permutations(range(n))
               if _relabel(list(perm)) == canon)


def _hyper_to_lists(hyperedges: list, directed: bool) -> list:
    """Convert hyperedges to JSON-serialisable sorted integer lists.

    Forward edges keep their ``[tail, [heads]]`` shape; general edges use
    ``[[tails], [heads]]``.
    """
    if directed:
        out = []
        for edge in hyperedges:
            first, heads = edge
            if isinstance(first, (set, frozenset)):
                out.append([sorted(first), sorted(heads)])
            else:
                out.append([first, sorted(heads)])
        return out
    return [sorted(edge) for edge in hyperedges]


def _enum_matrix_extremals(
    variant: Variant,
    n: int,
    m: int,
    separation: str,
    target: int,
    deadline: float,
) -> tuple[list[np.ndarray], bool]:
    """DFS over all (variant, n, m) multiplicity matrices achieving exactly ``target`` edges.

    Generalises :func:`enumerate_extremal_directed_multigraphs` to all four
    matrix variants (simple/multi × directed/undirected) and to vertex as well
    as edge separation.  Returns ``(reps, timed_out)`` where ``reps`` are
    deduplicated representatives (one per isomorphism class).

    Pruning strategy: arc-count reachability at every step; prefix edge-
    connectivity check at each completed vertex block (edge separation only;
    vertex separation checks only the final graph because the per-node cost is
    too high for DFS).
    """
    max_mult = 1 if variant.simple else (m - 1)
    is_directed = variant.directed

    # Vertex-block order: all pairs involving vertex j before j+1 appears.
    order: list[tuple[int, int]] = []
    for j in range(1, n):
        for i in range(j):
            order.append((i, j))
            if is_directed:
                order.append((j, i))
    total = len(order)

    # Position at which the subgraph on {0..j} is fully decided.
    # Directed: j*(j+1) positions; undirected: j*(j+1)//2 positions.
    step_per_vertex = 2 if is_directed else 1
    block_end: dict[int, int] = {
        j: step_per_vertex * j * (j + 1) // 2 for j in range(1, n)
    }

    mu = np.zeros((n, n), dtype=int)
    seen: set[bytes] = set()
    reps: list[np.ndarray] = []
    timed_out = [False]

    def _feasible_full() -> bool:
        g = _graph_from_mu(mu, variant)
        if separation == "edge":
            return max_edge_connectivity(g) <= m - 1
        return max_vertex_connectivity(g) <= m - 1

    def dfs(pos: int, edges: int) -> None:
        if timed_out[0]:
            return
        if time.time() > deadline:
            timed_out[0] = True
            return
        if edges + max_mult * (total - pos) < target or edges > target:
            return
        if pos == total:
            if edges == target and _feasible_full():
                canon = _canonical_form(mu)
                if canon not in seen:
                    seen.add(canon)
                    reps.append(mu.copy())
            return
        # At each block boundary: prune if the prefix subgraph is already
        # infeasible (edge connectivity only — cheap with _tiny_maxflow).
        completed_j = next(
            (j for j in range(1, n) if block_end.get(j) == pos), None
        )
        if completed_j is not None and separation == "edge":
            sub_n = completed_j + 1
            if any(_tiny_maxflow(mu, n, s, t, m - 1)
                   for s in range(sub_n) for t in range(sub_n) if s != t):
                return
        u, v = order[pos]
        for val in range(max_mult + 1):
            mu[u, v] = val
            if not is_directed:
                mu[v, u] = val
            dfs(pos + 1, edges + val)
        mu[u, v] = 0
        if not is_directed:
            mu[v, u] = 0

    dfs(0, 0)
    return reps, timed_out[0]


def _enum_hyper_extremals(
    directed: bool,
    vertex_split: bool,
    r: int,
    n: int,
    m: int,
    target: int,
    deadline: float,
    *,
    kind: str = "forward",
) -> tuple[list[list], bool]:
    """DFS over all r-uniform hypergraphs on n vertices with exactly ``target`` edges.

    Iterates candidate hyperedges in order (include / exclude) and prunes
    immediately when adding a hyperedge pushes the connectivity above m-1
    (monotonicity: adding edges never decreases connectivity, so no superset
    can be feasible at that branch either).  ``kind`` selects the directed
    orientation model.  Returns ``(reps, timed_out)`` where each representative
    in ``reps`` is a list of JSON-serialisable sorted vertex lists.
    """
    candidates = _hyperedge_candidates(n, r, directed, kind=kind)
    total = len(candidates)
    active: list = []
    seen: set[tuple] = set()
    reps: list[list] = []
    timed_out = [False]

    def dfs(pos: int, count: int) -> None:
        if timed_out[0]:
            return
        if time.time() > deadline:
            timed_out[0] = True
            return
        if count + (total - pos) < target or count > target:
            return
        if pos == total:
            if count == target:
                canon = _hyper_canonical(active, n, directed)
                if canon not in seen:
                    seen.add(canon)
                    reps.append(_hyper_to_lists(active, directed))
            return
        # Include candidates[pos] and recurse only if still feasible.
        active.append(candidates[pos])
        h = Hypergraph(n, active, directed=directed)
        if max_hyper_connectivity(h, vertex_split=vertex_split) <= m - 1:
            dfs(pos + 1, count + 1)
        active.pop()
        # Exclude candidates[pos].
        dfs(pos + 1, count)

    dfs(0, 0)
    return reps, timed_out[0]


def gallery_extremal_graphs(
    max_n: int = 7,
    max_m: int = 4,
    r: int = 3,
    time_per_case: float = 3.0,
) -> dict:
    """Classify graphs attaining the best value found for all 12 variants.

    For each (variant, n, m) triple where the enumeration finishes within
    ``time_per_case`` seconds, the function:

    1. runs a short repeated search to discover the extremal edge count.
    2. exhaustively enumerates every graph achieving that count, without
       claiming that the search target itself is optimal.
    3. deduplicates by isomorphism class and records ``n! / |Aut(G)|`` (the
       number of labelled copies) per class.

    Returns a JSON-serialisable dict with structure::

        result[variant_key]["n={n}_m={m}"] = {
            "best_found_value": int,
            "classes": [{"repr": <matrix or edge list>, "labelled_count": int}],
            "total_labelled": int,   # sum of labelled_count over all classes
            "classification_complete": bool,
            "optimality_proved": bool,
        }

    For matrix variants ``repr`` is the multiplicity matrix (list of lists of
    int).  For hypergraph variants it is a list of hyperedges: each edge is a
    sorted list of vertex indices (undirected) or ``[tail, [head, ...]]``
    (directed).

    The twelve variant keys are:
    ``simple_undirected_{edge,vertex}``,
    ``simple_directed_{edge,vertex}``,
    ``multi_undirected_{edge,vertex}``,
    ``multi_directed_{edge,vertex}``,
    ``hyper_undirected_r{r}_{edge,vertex}``,
    ``hyper_directed_r{r}_{edge,vertex}``.

    The two ``multi_*_vertex`` keys report the reduced SIMPLE problem, because
    the thesis's vertex measure is blind to parallel copies and the variant
    collapses onto the simple one (see the config comment below).
    """
    # The two multi-vertex rows run on the SIMPLE variant: the checker's vertex
    # mode gives every adjacency capacity one, so parallel copies never change
    # kappa and a raw multigraph search would just fill every cell to m-1 for
    # free (it once reported a "36-arc extremal K_4 at multiplicity 3").  The
    # thesis reduces these variants to the simple ones (tab:summary), and the
    # gallery must report the reduced problem, exactly as the variant grids do.
    matrix_configs: list[tuple[str, Variant, str]] = [
        ("simple_undirected_edge",   SIMPLE_UNDIRECTED, "edge"),
        ("simple_undirected_vertex", SIMPLE_UNDIRECTED, "vertex"),
        ("simple_directed_edge",     SIMPLE_DIRECTED,   "edge"),
        ("simple_directed_vertex",   SIMPLE_DIRECTED,   "vertex"),
        ("multi_undirected_edge",    MULTI_UNDIRECTED,  "edge"),
        ("multi_undirected_vertex",  SIMPLE_UNDIRECTED, "vertex"),
        ("multi_directed_edge",      MULTI_DIRECTED,    "edge"),
        ("multi_directed_vertex",    SIMPLE_DIRECTED,   "vertex"),
    ]
    hyper_configs: list[tuple[str, bool, bool]] = [
        (f"hyper_undirected_r{r}_edge",   False, False),
        (f"hyper_undirected_r{r}_vertex", False, True),
        (f"hyper_directed_r{r}_edge",     True,  False),
        (f"hyper_directed_r{r}_vertex",   True,  True),
    ]

    result: dict = {}

    for key, variant, separation in matrix_configs:
        result[key] = {}
        for n in range(2, max_n + 1):
            for m in range(2, max_m + 1):
                case_deadline = time.time() + time_per_case
                # Step 1: discover the extremal value via repeated search.
                # 2000 steps/restart is enough to converge for n <= 6;
                # we run at least 3 seeds before the deadline to be robust
                # against unlucky single-seed runs.
                best_val = 0
                seed = 0
                while time.time() < case_deadline - 2.0 or seed < 3:
                    if time.time() > case_deadline - 0.5:
                        break
                    res = search_for_dense_graph(
                        variant, n, m, separation=separation,
                        steps=2000, seed=seed)
                    best_val = max(best_val, res.best_edge_count)
                    seed += 1
                # Step 2: enumerate all graphs at that value.
                enum_deadline = min(case_deadline, time.time() + 2.0)
                reps, timed_out = _enum_matrix_extremals(
                    variant, n, m, separation, best_val, enum_deadline)
                # Step 3: count automorphisms and labelled copies.
                fn = math.factorial(n)
                classes = [
                    {"repr": mu.tolist(),
                     "labelled_count": fn // _aut_count_matrix(mu)}
                    for mu in reps
                ]
                result[key][f"n={n}_m={m}"] = {
                    "best_found_value": best_val,
                    "classes": classes,
                    "total_labelled": sum(c["labelled_count"] for c in classes),
                    "classification_complete": not timed_out,
                    "optimality_proved": False,
                }

    for key, directed, vertex_split in hyper_configs:
        result[key] = {}
        for n in range(r, max_n + 1):
            for m in range(2, max_m + 1):
                case_deadline = time.time() + time_per_case
                # Brute-force search (small n): finds the extremal value.
                best_val, _, completed = _brute_force_hypergraph(
                    n, r, m, case_deadline,
                    directed=directed, vertex_split=vertex_split)
                if not completed:
                    result[key][f"n={n}_m={m}"] = {
                        "best_found_value": best_val, "classes": [],
                        "total_labelled": 0,
                        "classification_complete": False,
                        "optimality_proved": False,
                    }
                    continue
                # Enumerate all achieving best_val.
                enum_deadline = min(case_deadline, time.time() + 2.0)
                hyper_reps, timed_out = _enum_hyper_extremals(
                    directed, vertex_split, r, n, m, best_val, enum_deadline)
                fn = math.factorial(n)
                classes = []
                for edge_lists in hyper_reps:
                    raw = ([(row[0], frozenset(row[1])) for row in edge_lists]
                           if directed else [frozenset(e) for e in edge_lists])
                    classes.append({
                        "repr": edge_lists,
                        "labelled_count": fn // _aut_count_hyper(raw, n, directed),
                    })
                result[key][f"n={n}_m={m}"] = {
                    "best_found_value": best_val,
                    "classes": classes,
                    "total_labelled": sum(c["labelled_count"] for c in classes),
                    "classification_complete": not timed_out,
                    "optimality_proved": True,
                }

    return result


def save_gallery_json(gallery: dict, path: str | Path) -> None:
    """Write the gallery dict to a JSON file (pretty-printed)."""
    with open(path, "w") as f:
        json.dump(gallery, f, indent=2)


def prove_integral_arc_bound(n: int, m: int, target: int, *,
                               time_limit: float = 3000.0,
                               use_gurobi: bool | None = None,
                               show_solver_log: bool = False) -> str:
    """Decide by MILP whether some directed multigraph on ``n`` vertices with
    multiplicities in {0..m-1} and ``lambda^max <= m-1`` has >= ``target`` arcs.

    Returns "INFEASIBLE" (proving L_m^dir(n) < target), "FEASIBLE", or
    "LIMIT".  This is the integral companion of the fractional prover: the
    m = 3 chain (rem:odd-step-roadmap) needs only L_3^dir(7) = 24, i.e.
    INFEASIBLE at target 25, which is a far friendlier MILP than M*(7) because the
    weights themselves are integers.  Same exact :func:`_cut_counting_model` with
    cap = m-1 and integer multiplicities, all its proved-valid families on, plus the
    one constraint that the multiplicities total at least ``target``.
    """
    _require_pulp()
    prob, w = _cut_counting_model(
        n, cap=float(m - 1), integer=True, two_hop=True,
        symmetry=True, deletion=True, degree_pair=True,
    )
    prob += pulp.lpSum(w.values()) >= target        # the arc target
    prob += 0                                        # feasibility, no objective

    prob.solve(_pick_solver(time_limit, show_solver_log, use_gurobi))
    status = pulp.LpStatus[prob.status]
    if status == "Infeasible":
        return "INFEASIBLE"
    if status == "Optimal":
        return "FEASIBLE"
    return "LIMIT"


def _float_maxflow_value(capacity: np.ndarray, source: int, target: int,
                         eps: float = 1e-12) -> float:
    """Max-flow value for FLOAT capacities (Edmonds-Karp, shortest augmenting path).

    scipy's csgraph max-flow is integer-only, so the fractional check below needs
    its own tiny routine.  BFS augmenting paths give a polynomial bound independent
    of the capacity magnitudes, so the loop terminates even on irrational-looking
    floats; ``eps`` treats a near-zero residual as saturated.
    """
    n = capacity.shape[0]
    residual = capacity.astype(float).copy()
    flow = 0.0
    while True:
        parent = [-1] * n
        parent[source] = source
        queue = deque([source])
        while queue and parent[target] == -1:
            u = queue.popleft()                    # FIFO: shortest augmenting path
            for v in range(n):
                if parent[v] == -1 and residual[u, v] > eps:
                    parent[v] = u
                    queue.append(v)
        if parent[target] == -1:
            return flow
        bottleneck = float("inf")
        v = target
        while v != source:
            bottleneck = min(bottleneck, residual[parent[v], v])
            v = parent[v]
        v = target
        while v != source:
            residual[parent[v], v] -= bottleneck
            residual[v, parent[v]] += bottleneck
            v = parent[v]
        flow += bottleneck


def fractional_flows_feasible(weights: np.ndarray, tol: float = 1e-9) -> bool:
    """Check the scaled multigraph constraint: all pairwise max-flows <= 1.

    ``weights`` is an ``n x n`` matrix with entries in [0,1] (zero diagonal),
    the scaled multiplicity matrix mu/(m-1) of lem:scaling-reduction.
    """
    n = weights.shape[0]
    capacity = np.where(weights > 1e-12, weights, 0.0).astype(float)
    np.fill_diagonal(capacity, 0.0)
    for s in range(n):
        for t in range(n):
            if t != s and _float_maxflow_value(capacity, s, t) > 1 + tol:
                return False
    return True


def fractional_search(n: int, objective: str = "min_degree", steps: int = 6000,
                      seed: int = 0, start: str = "bipartite") -> tuple[np.ndarray, float]:
    """Hunt for a fractional counterexample to the odd-n directed multigraph
    statements (conj:min-degree and the total-weight bound).

    ``objective``: "min_degree" maximises the minimum weighted total degree
    (conjecture: cannot exceed k = (n-1)/2 for odd n); "total" maximises the
    total weight (conjecture: cannot exceed max(2(n-1), floor(n^2/4))).
    ``start``: "bipartite" (the conjectured extremiser), "zero", or "random".
    Returns the best weighting found and its objective value.  A value
    exceeding the conjectured ceiling would refute the conjecture for every
    m - 1 divisible by the weight denominators; none was found at n = 7, 9.
    """
    rng = random.Random(seed)
    weights = np.zeros((n, n))
    if start == "bipartite":
        for a in range(n // 2):
            for b in range(n // 2, n):
                weights[a, b] = 1.0
    elif start == "random":
        weights = np.array([[rng.random() if i != j else 0.0 for j in range(n)]
                            for i in range(n)])
        while not fractional_flows_feasible(weights):
            weights *= 0.85

    def score(w: np.ndarray) -> float:
        if objective == "total":
            return float(w.sum())
        degrees = w.sum(axis=0) + w.sum(axis=1)
        return float(degrees.min()) + 1e-3 * float(w.sum())

    current = score(weights)
    best, best_w = current, weights.copy()
    for it in range(steps):
        temperature = 0.08 * (1 - it / steps) + 1e-4
        u, v = rng.randrange(n), rng.randrange(n)
        if u == v:
            continue
        old = weights[u, v]
        weights[u, v] = min(1.0, max(0.0, old + (rng.random() * 2 - 1)
                                     * max(0.02, temperature)))
        if weights[u, v] == old:
            continue
        value = score(weights)
        accept = value > current or rng.random() < math.exp((value - current)
                                                            / temperature)
        if accept and fractional_flows_feasible(weights):
            current = value
            if value > best:
                best, best_w = value, weights.copy()
        else:
            weights[u, v] = old
    return best_w, best


# --- SELF-CHECK: python erdos915_unified.py runs every invariant; exits 0 on all-PASS ---

_failures = 0


def check(label: str, condition: bool) -> None:
    """Print a PASS/FAIL line and tally failures."""
    global _failures
    print(f"  {'PASS' if condition else 'FAIL'}  {label}")
    if not condition:
        _failures += 1


def section(title: str) -> None:
    """Print a section header."""
    print(f"\n{title}")


def _run_checks() -> int:
    """Run every invariant check; return 1 on any failure, else 0.

    This is the program checking itself end to end, using the bare top-level
    names defined above in this single file.
    """
    section("Checker: the directed m=2 values ell_2^dir(n) = 2, 4, 6, 8")
    for n, expected in [(2, 2), (3, 4), (4, 6), (5, 8)]:
        graph = double_star(n, m=2, directed=True)
        check(f"double star n={n}: {graph.edge_count()} arcs, lambda^max={max_edge_connectivity(graph)}",
              graph.edge_count() == expected and max_edge_connectivity(graph) == 1)

    section("Checker: one-directional bipartite is quadratic and feasible")
    for n in range(2, 8):
        graph = one_directional_bipartite(n)
        check(f"bipartite n={n}: {graph.edge_count()} arcs (floor(n^2/4)={ (n*n)//4 })",
              graph.edge_count() == (n * n) // 4 and max_edge_connectivity(graph) == 1)

    section("Checker: the undirected cycle is the infeasible witness for m=2")
    cycle = Graph(6, SIMPLE_UNDIRECTED)
    for v in range(6):
        cycle.add_edge(v, (v + 1) % 6)
    check(f"C_6 has lambda^max={max_edge_connectivity(cycle)}", max_edge_connectivity(cycle) == 2)

    if NETWORKX_AVAILABLE:
        section("Gomory-Hu shortcut agrees with brute-force lambda^max")
        tree = clique_tree(3, 4)
        check(f"GH={max_edge_connectivity_via_tree(tree)} vs direct={max_edge_connectivity(tree)}",
              max_edge_connectivity_via_tree(tree) == max_edge_connectivity(tree))
    else:
        section("Gomory-Hu shortcut skipped (optional networkx not installed)")

    section("Vertex connectivity: K_4-trees are globally 3-connected")
    for blocks in range(0, 5):
        ktree = clique_tree(4, blocks)
        check(f"K_4-tree on {ktree.num_vertices} vertices: kappa={min_vertex_connectivity(ktree)}",
              min_vertex_connectivity(ktree) == 3)

    section("Constructions: the augmented bipartite conjecture values")
    counterexample = augmented_bipartite(10, 3)
    check(f"m=3,n=10: {counterexample.edge_count()} arcs, lambda^max={max_edge_connectivity(counterexample)}",
          counterexample.edge_count() == 30 and max_edge_connectivity(counterexample) == 2)
    for n, m in [(8, 3), (10, 4), (12, 4), (10, 5)]:
        graph = augmented_bipartite(n, m)
        expected = (n + m - 2) ** 2 // 4
        check(f"n={n},m={m}: {graph.edge_count()} arcs (expected {expected}), lambda^max={max_edge_connectivity(graph)}",
              graph.edge_count() == expected and max_edge_connectivity(graph) == m - 1)

    section("Hypergraphs: Berge connectivity, exact and generalising the graph case")
    k43 = complete_uniform_hypergraph(4, 3)
    check(f"complete 3-uniform K_4^(3): Berge lambda^max = {max_hyperedge_connectivity(k43)} (expect 3)",
          max_hyperedge_connectivity(k43) == 3)
    for n in [3, 4, 5]:
        complete = complete_uniform_hypergraph(n, 2)
        check(f"2-uniform K_{n} reduces to edge-connectivity {max_hyperedge_connectivity(complete)} (expect {n-1})",
              max_hyperedge_connectivity(complete) == n - 1)
    for n, r in [(7, 3), (10, 4), (13, 4)]:
        star = star_hypertree(n, r)
        check(f"star hypertree n={n}, r={r}: {star.edge_count()} edges (expect {(n-1)//(r-1)}), "
              f"lambda^max={max_hyperedge_connectivity(star)}",
              star.edge_count() == (n - 1) // (r - 1) and max_hyperedge_connectivity(star) == 1)

    section("Hypergraphs: directed orientation models (forward / backward / general)")
    # The general gate admits a mixed arc {0,1} -> {2,3}: a route enters at a tail
    # and leaves at a head, so 0->2 carries one route and 2->0 carries none.
    mixed = Hypergraph(4, [(frozenset({0, 1}), frozenset({2, 3}))], directed=True)
    check("mixed arc {0,1}->{2,3}: lambda(0,2)=1 and lambda(2,0)=0",
          hyper_connectivity(mixed, 0, 2) == 1 and hyper_connectivity(mixed, 2, 0) == 0)
    # Backward is the arc-reversal dual of forward, so their extremal numbers agree.
    fwd, _ = max_feasible_hyperedges(4, 3, 3, directed=True, kind="forward", time_limit=1.5)
    bwd, _ = max_feasible_hyperedges(4, 3, 3, directed=True, kind="backward", time_limit=1.5)
    check(f"forward == backward at n=4, r=3, m=3 ({fwd} == {bwd})", fwd == bwd)
    # General contains forward and strictly beats it where vertices are scarce
    # (n = r); both values here are proved exact by the branch and bound.
    g3, e3 = max_feasible_hyperedges(3, 3, 3, directed=True, kind="general", time_limit=1.5)
    f3, _  = max_feasible_hyperedges(3, 3, 3, directed=True, kind="forward", time_limit=1.5)
    check(f"general 4 > forward 3 at n=3, r=3, m=3 (got {g3} vs {f3}, exact={e3})",
          g3 == 4 and f3 == 3 and e3)
    g4, e4 = max_feasible_hyperedges(4, 4, 4, directed=True, kind="general", time_limit=10.0)
    f4, _  = max_feasible_hyperedges(4, 4, 4, directed=True, kind="forward", time_limit=3.0)
    check(f"general 8 doubles forward 4 at n = r = 4, m = 4 ({g4} vs {f4}, exact={e4})",
          g4 == 8 and f4 == 4 and e4)

    section("Monte Carlo: the appearance probability crosses the m/n scale")
    n, m = 30, 3
    below = estimate_appearance_probability(n, 0.3 * m / n, m, trials=120, seed=1)
    above = estimate_appearance_probability(n, 1.8 * m / n, m, trials=120, seed=1)
    check(f"P[appears] rises from {below:.2f} (well below m/n) to {above:.2f} (well above)",
          below < 0.5 < above)

    section("Monte Carlo: vertex-connectivity never exceeds edge-connectivity (Whitney)")
    edge_dist = connectivity_distribution(20, 0.25, trials=40, separation="edge", seed=3)
    vertex_dist = connectivity_distribution(20, 0.25, trials=40, separation="vertex", seed=3)
    check("kappa^max <= lambda^max on every one of the 40 identical samples",
          all(kappa <= lam for kappa, lam in zip(vertex_dist, edge_dist)))

    section("Edge vs vertex in G(n,p): they agree at small m, part company at large m")
    lam_small, kap_small = edge_vertex_distribution(5, 0.5, trials=120, seed=7)
    small_gap = sum(k < l for k, l in zip(kap_small, lam_small))
    check("n=5: kappa^max = lambda^max on every sample (no gap)",
          small_gap == 0 and all(k <= l for k, l in zip(kap_small, lam_small)))
    lam_large, kap_large = edge_vertex_distribution(16, 0.25, trials=200, seed=7)
    large_gap = sum(k < l for k, l in zip(kap_large, lam_large))
    check(f"n=16: Whitney holds and kappa^max < lambda^max on {large_gap} of 200 samples",
          large_gap > 0 and all(k <= l for k, l in zip(kap_large, lam_large)))

    if not PULP_AVAILABLE:
        section("Prover sections skipped (optional pulp not installed)")
    else:
        section("Prover: cut-counting proves M*(n) = 2(n-1) optimal for small n")
        # The thesis (ch2) claims L_m^dir(n) = 2(n-1)(m-1) is proved for ALL n <= 6
        # via the cut-counting MILP (thm:dir-multi-small).  n=3,4,5 all finish in
        # well under 60 s and are verified here.  n=6 takes ~1315 s (~22 min) on a
        # typical laptop and is NOT included in this fast loop -- it must be
        # verified separately:
        #
        #   result = prove_directed_multigraph(6, time_limit=2000.0)
        #   assert result.solver_claims_optimal() and round(result.scaled_optimum) == 10
        #
        # The confirmed run (2026-06-13) is logged in program/logs/selftest_check.log
        # (search "n=6 OPTIMAL M*(6)=10 in 1315s").  Omitting n=6 from this loop is
        # not an error in the proof -- the proof ran -- but it means this self-test
        # alone does not reproduce the full n<=6 certification.
        for n in [3, 4, 5]:
            result = prove_directed_multigraph(n, time_limit=300.0)
            check(f"n={n}: status={result.status}, M*={result.scaled_optimum:.1f}, solver_optimal={result.solver_claims_optimal()}",
                  result.solver_claims_optimal() and round(result.scaled_optimum) == 2 * (n - 1))

        section("Prover: the valid inequalities sharpen but never move the optimum")
        # Turning the two-hop and symmetry-breaking rows off leaves the BARE exact
        # cut formulation, which must still prove the same M*(3) = 4.  If any row we
        # call a "valid inequality" were in fact invalid, it would cut a feasible
        # point and shift this optimum -- so this is the regression tripwire that
        # guards the prover's soundness, not just a re-run of the value.
        bare = prove_directed_multigraph(3, time_limit=120.0,
                                         use_two_hop=False, use_symmetry_breaking=False)
        check(f"M*(3) with the tighteners off = {bare.scaled_optimum:.1f} (expect 4), solver_optimal={bare.solver_claims_optimal()}",
              bare.solver_claims_optimal() and round(bare.scaled_optimum) == 4)

        section("Prover (integral): an INFEASIBLE verdict is a genuine upper-bound proof")
        # L_3^dir(4) = 12: a 12-arc multigraph exists, no 13-arc one does.  This
        # exercises the exact mechanism behind the thesis's L_3(7) = 24 result
        # (INFEASIBLE one above the optimum) on a value small enough to re-run here,
        # so a regression in the integral encoding cannot pass unnoticed.
        feasible_at_12 = prove_integral_arc_bound(4, 3, 12, time_limit=120.0)
        infeasible_at_13 = prove_integral_arc_bound(4, 3, 13, time_limit=120.0)
        check(f"target 12 -> {feasible_at_12} (expect FEASIBLE), "
              f"target 13 -> {infeasible_at_13} (expect INFEASIBLE)",
              feasible_at_12 == "FEASIBLE" and infeasible_at_13 == "INFEASIBLE")

    section("Search: rediscovering ell_2^dir(4) = 6 by random search")
    result = search_for_dense_graph(SIMPLE_DIRECTED, n=4, m=2, steps=6000, seed=0)
    check(f"best found = {result.best_edge_count} arcs, feasible lambda^max={max_edge_connectivity(result.best_graph)}",
          result.best_edge_count == 6 and max_edge_connectivity(result.best_graph) <= 1)

    section("Driver: one solve() call handles each kind of question")
    # Exhaustive directed: the cut-counting proves ell_2^dir(4) = 6 exactly.
    proved = solve(4, 2, directed=True, simple=True, exhaustive=True,
                   max_seconds=120.0)
    check(f"solve exhaustive simple-directed n=4,m=2: {proved.value} ({proved.bound})",
          proved.proven and proved.value == 6)
    # Discovery finds the same 6 arcs as a lower bound within a short budget.
    # The checks use sa (lighter); tabu is the default for actually solving.
    found = solve(4, 2, directed=True, simple=True, exhaustive=False,
                  max_seconds=3.0, method="sa")
    check(f"solve discovery simple-directed n=4,m=2: {found.value} ({found.bound})",
          found.bound == "lower" and found.value == 6)
    # The VERTEX separation is a separate question, not a corollary of the arc
    # one: Whitney's kappa <= lambda makes the vertex-feasible family the LARGER
    # of the two, so an arc upper bound does not restrict it.  thm:dir-vertex-m2
    # needs its own base cases, and these are the first three of them.
    for base_n, base_value in ((3, 4), (4, 6), (5, 8)):
        v_value, _, v_done = _exhaustive_directed(base_n, 2, "vertex",
                                                  time.time() + 120.0)
        check(f"exhaustive simple-directed VERTEX n={base_n},m=2: {v_value}",
              v_done and v_value == base_value)
    # The vertex flow helper must agree with the exact checker it stands in for.
    _vg = Graph(4, SIMPLE_DIRECTED)
    for _a, _b in ((0, 1), (0, 2), (1, 3), (2, 3)):
        _vg.mu[_a, _b] = 1
    _vout = [{_b for _b in range(4) if _vg.mu[_a, _b]} for _a in range(4)]
    check("vertex flow helper agrees with the exact checker on a theta digraph",
          _vertex_flow_at_least(_vout, 4, 0, 3, 2)
          and not _vertex_flow_at_least(_vout, 4, 0, 3, 3)
          and local_connectivity(_vg, 0, 3, vertex_split=True) == 2)
    # prop:dir-arc-stability, the unconditional quadratic bound.  Both the
    # load-bearing counting step (sum of d+ d- capped by m n(n-1)) and the bound
    # it yields are checked on sampled feasible digraphs.
    _rng = random.Random(3)
    _worst_slack = None
    _count_ok = True
    for _ in range(120):
        _sn, _sm = _rng.randint(3, 7), _rng.randint(2, 4)
        _sg = Graph(_sn, SIMPLE_DIRECTED)
        for _a in range(_sn):
            for _b in range(_sn):
                if _a != _b and _rng.random() < 0.6:
                    _sg.mu[_a, _b] = 1
        while max_edge_connectivity(_sg) > _sm - 1:   # prune down to feasible
            _present = [(a, b) for a in range(_sn) for b in range(_sn) if _sg.mu[a, b]]
            _a, _b = _rng.choice(_present)
            _sg.mu[_a, _b] = 0
        _dout = [int(_sg.mu[x].sum()) for x in range(_sn)]
        _din = [int(_sg.mu[:, x].sum()) for x in range(_sn)]
        # The sharp form of the counting step: (m-1) n(n-1), not m n(n-1).
        if sum(_dout[x] * _din[x] for x in range(_sn)) > (_sm - 1) * _sn * (_sn - 1):
            _count_ok = False
        _slack = ((_sn * _sn) // 4 + math.sqrt(_sm) * _sn ** 1.5
                  - int(_sg.mu.sum()))
        _worst_slack = _slack if _worst_slack is None else min(_worst_slack, _slack)
        # thm:dir-arc-linear-error, the O_m(n) bound.
        if int(_sg.mu.sum()) > (_sn * _sn) // 4 + 4 * (_sm - 1) * (_sn - 1):
            _count_ok = False
        # Case 2 of its proof: min total degree >= n/2 forces the linear bound
        # on the sum of the smaller half-degrees.
        if min(_dout[x] + _din[x] for x in range(_sn)) >= _sn / 2:
            if (sum(min(_dout[x], _din[x]) for x in range(_sn))
                    > 4 * (_sm - 1) * (_sn - 1)):
                _count_ok = False
    check("prop:dir-arc-stability and thm:dir-arc-linear-error hold on 120 "
          f"sampled feasible digraphs (tightest slack {_worst_slack:.1f})",
          _count_ok and _worst_slack >= 0)
    # sec:multi-vertex-standard: the OTHER counting convention is a different
    # problem, and the theta construction beats the thickened tree at m=5, n=4.
    _mv4, _, _mv4_done = max_multigraph_vertex_standard(4, 3)
    _mv5, _, _mv5_done = max_multigraph_vertex_standard(4, 5)
    check(f"multigraph vertex, other convention: K_3(4) = {_mv4} = (m-1)(n-1)",
          _mv4_done and _mv4 == 6)
    check(f"multigraph vertex, other convention: K_5(4) = {_mv5} > 12, the "
          "multigraph edge value, so the two problems differ",
          _mv5_done and _mv5 == 14)
    # Exhaustive undirected by brute force: ell_2(5) = n-1 = 4 (a spanning tree).
    tree = solve(5, 2, directed=False, simple=True, exhaustive=True,
                 max_seconds=30.0)
    check(f"solve exhaustive simple-undirected n=5,m=2: {tree.value} ({tree.bound})",
          tree.proven and tree.value == 4)
    # Hypergraph discovery returns a feasible lower bound for the r=3, m=2 case.
    hyper = solve(7, 2, hypergraph=True, r=3, exhaustive=False, max_seconds=3.0,
                  method="random-greedy")
    check(f"solve discovery 3-uniform hypergraph n=7,m=2: {hyper.value} ({hyper.bound})",
          hyper.bound == "lower" and hyper.value == 3)

    # --- open-variant exploration coverage --------------------------------
    # These three functions are the program's only handle on the OPEN parts of
    # the problem (hypergraph vertex value, the fractional relaxation behind the
    # odd-n conjectures).  The first author-reviewed draft of this block ran
    # exhaustive n>=7 sweeps and 6000-step searches, which added minutes; the
    # checks below cover the same code paths at n<=5 so they finish in ~2s.
    section("Open variants: hypergraph vertex value (kappa^max) at small n")
    # m=2 uses the incidence-rank/forest witness, m=3 the brute-force
    # feasibility sweep; both confirm value = floor((m-1)(n-1)/(r-1)).
    for n, r, m in [(4, 3, 2), (5, 3, 2), (4, 3, 3), (5, 3, 3)]:
        target = ((m - 1) * (n - 1)) // (r - 1)
        check(f"hypergraph vertex value at n={n}, r={r}, m={m} = {target}",
              verify_hyper_vertex_value(n, r, m))

    section("Open variants: the fractional [0,1]-weight checker is exact")
    # A directed path keeps every max-flow at 1 (feasible); two internally
    # disjoint s->t routes push the s->t flow to 2 (infeasible).  This is the
    # relaxation that fractional_search optimises over.
    path_w = np.zeros((4, 4))
    path_w[0, 1] = path_w[1, 2] = path_w[2, 3] = 1.0
    two_route = np.zeros((4, 4))
    two_route[0, 1] = two_route[0, 2] = two_route[1, 3] = two_route[2, 3] = 1.0
    check("path weighting feasible, two-route weighting infeasible",
          fractional_flows_feasible(path_w)
          and not fractional_flows_feasible(two_route))

    section("Open variants: fractional search respects the odd-n ceilings")
    # Short n=5 runs (the conjectured bipartite point is rigid).  The
    # min_degree score carries a 1e-3 * total-weight tie-breaker, so its
    # comparison allows that slack; a genuine refutation would clear the
    # ceiling by a full unit, far above it.
    _, total_best = fractional_search(5, "total", steps=1500, seed=1)
    check(f"fractional total weight at n=5 stays <= 8: {total_best:.3f}",
          total_best <= 8 + 1e-6)
    _, deg_best = fractional_search(5, "min_degree", steps=1500, seed=1)
    check(f"fractional min degree at n=5 stays <= k=2 (+tie-break slack): {deg_best:.3f}",
          deg_best <= 2 + 1e-3 * 5 * 5)

    print(f"\n{'ALL CHECKS PASSED' if _failures == 0 else f'{_failures} CHECK(S) FAILED'}")
    return 1 if _failures else 0


if __name__ == "__main__":
    print(f"C extension: {'LOADED (_erdos_fast.so)' if C_EXTENSION_LOADED else 'not found (pure Python)'}")
    raise SystemExit(_run_checks())

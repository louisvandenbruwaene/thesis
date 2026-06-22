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
stays at or below ``m - 1``.  Sixteen concrete variants fall out of these
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

  * PROVE.   The cut-counting method proves *upper* bounds for a fixed number of
    vertices: it shows that no graph on ``n`` vertices can be denser, with a
    zero optimality gap, so an optimal solution is a genuine proof.

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

import json
import math
import pickle
import random
import shutil
import statistics
import subprocess
import time
import warnings
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
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers the '3d' projection)
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    MaxNLocator = None
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
        new_value = self.mu[u, v] + count
        if self.variant.simple:
            new_value = min(new_value, 1)  # enforce the 0/1 simple-graph cap
        self._assign(u, v, new_value)

    def remove_edge(self, u: int, v: int, count: int = 1) -> None:
        """Remove ``count`` parallel edges or arcs (never below zero)."""
        self._require_distinct(u, v)
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
    """``ell_m(n) = floor(m (n-1) / 2)``.  Proved (Mader, 1973)."""
    return (m * (n - 1)) // 2


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
    """``k_5(n) = floor(8n/3) - 3`` for large ``n``.  Cited (Sorensen-Thomassen)."""
    return (8 * n) // 3 - 3


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
    bound for all ``m``; conjectured to be tight for ``m >= 3``
    (``conj:dir-arc``), proved tight for ``m = 2``.
    """
    hub_branch = m * (n - 1)
    bipartite_branch = (n + m - 2) ** 2 // 4
    return max(hub_branch, bipartite_branch)


def hypergraph_edge(n: int, m: int, r: int) -> int:
    """``floor((m-1)(n-1)/(r-1))`` hyperedges for the ``r``-uniform edge problem.

    Proved modulo the hypergraph Gomory-Hu theorem; the star hypertree attains
    the ``m = 2`` case and a sparse hypergraph attains the general bound.
    """
    return ((m - 1) * (n - 1)) // (r - 1)


def directed_multigraph_arc(n: int, m: int) -> int:
    """``L_m^dir(n) = 2(n-1)(m-1)``.  Proved for ``n <= 6`` (by counting cuts).

    Conjectured to continue to hold while the double star dominates the
    one-directional bipartite branch (small ``n``); for larger ``n`` the
    quadratic branch takes over.
    """
    double_star_branch = 2 * (n - 1) * (m - 1)
    bipartite_branch = (m - 1) * ((n * n) // 4)
    return max(double_star_branch, bipartite_branch)


# --- HYPERGRAPH: stored as incidence list; Berge-path connectivity via helper-node max-flow ---


class Hypergraph:
    """A hypergraph stored by its incidence (a list of hyperedges).

    An undirected hyperedge is a set of vertices, crossed in either direction.  A
    directed hyperedge (``directed=True``) splits an ``r``-set into one tail and
    ``r - 1`` heads, stored as ``(tail, frozenset(heads))``: a Berge route may
    enter it only at the tail and leave only at a head.  This one-tail / many-head
    reading is the simplest directed sense of an ``r``-uniform Berge edge, and it
    is the author's own modelling choice for an otherwise unexplored variant.
    """

    def __init__(self, num_vertices: int, hyperedges: Iterable = (),
                 *, directed: bool = False):
        self.num_vertices = num_vertices
        self.directed = directed
        # Each entry is a frozenset, or a ``(tail, frozenset(heads))`` pair.
        self.hyperedges: list = []
        for edge in hyperedges:
            self.add_hyperedge(edge)

    def add_hyperedge(self, edge) -> None:
        """Add an undirected vertex set, or a directed ``(tail, heads)`` pair."""
        if self.directed:
            tail, raw_heads = edge
            heads = frozenset(raw_heads)
            members = heads | {tail}
            if tail in heads or len(members) < 2:
                raise ValueError("a directed hyperedge needs a tail and a distinct head")
            if any(v < 0 or v >= self.num_vertices for v in members):
                raise ValueError("hyperedge refers to a vertex outside the graph")
            self.hyperedges.append((tail, heads))
        else:
            vertices = frozenset(edge)  # a hyperedge is a set of distinct vertices
            if len(vertices) < 2:
                raise ValueError("a hyperedge must contain at least two vertices")
            if any(v < 0 or v >= self.num_vertices for v in vertices):
                raise ValueError("hyperedge refers to a vertex outside the graph")
            self.hyperedges.append(vertices)

    def members(self, edge) -> frozenset:
        """The vertex set of a stored hyperedge, directed or not."""
        if self.directed:
            tail, heads = edge
            return heads | {tail}
        return edge

    def vertices(self) -> range:
        return range(self.num_vertices)

    def edge_count(self) -> int:
        """Number of hyperedges."""
        return len(self.hyperedges)

    def incident_hyperedges(self, v: int) -> list[int]:
        """Indices of the hyperedges containing vertex ``v``."""
        return [i for i, edge in enumerate(self.hyperedges) if v in self.members(edge)]


def _hyper_capacity_matrix(hypergraph: Hypergraph, *, vertex_split: bool = False):
    """Integer capacity matrix of the hypergraph flow network (one per variant).

    Each hyperedge becomes an in/out gate joined by a capacity-1 arc, so at most
    one disjoint Berge route may traverse it: this is the hyperedge-as-node trick.
    With ``vertex_split`` each ORIGINAL vertex is *also* split into an in/out pair
    of capacity one, so the flow counts internally vertex-disjoint Berge routes
    instead of edge-disjoint ones.  For a directed hypergraph the gate is entered
    only from the tail and left only toward a head; for an undirected one every
    member links to the gate both ways.  The four hypergraph variants are thus the
    same construction with two booleans flipped, not four separate measures.

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
            tail, heads = edge
            cap[leave(tail), gate_in] = _UNBOUNDED
            for head in heads:
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
    distinct.  At ``m = 2`` or ``m = 3`` the partition equals the balanced
    ``(floor(n/2), ceil(n/2))`` split and the formula reduces to
    ``floor(n^2/4) + (m-2)ceil(n/2)``.  At ``m >= 4`` the shifted partition
    gives strictly more arcs.  For ``m = 3, n = 10`` this is the 30-arc
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

def _split_capacity_matrix(graph: Graph) -> tuple[np.ndarray, int]:
    """The ``2n x 2n`` capacity matrix of the vertex-split network.

    The vertex-mode network as a plain matrix, consumed by both the exact measure
    (:func:`local_connectivity` via scipy max-flow) and the capped search predicate
    (:func:`exceeds_bound` via :func:`_tiny_maxflow`).  Vertex ``v`` becomes an
    in-copy ``2v`` and an out-copy ``2v+1`` joined by an internal arc of capacity
    one (so any route uses ``v`` at most once), and each adjacency ``u -> v``
    becomes a capacity-one arc ``(2u+1) -> (2v)`` (parallel edges do NOT raise
    vertex connectivity).  The caller uncaps the two endpoints' own in->out gates
    so Menger counts internally disjoint routes (see :func:`exceeds_bound`).
    """
    n = graph.num_vertices
    size = 2 * n
    cap = np.zeros((size, size), dtype=int)
    for v in range(n):
        cap[2 * v, 2 * v + 1] = 1            # internal gate: one route through v
    for u in range(n):
        for v in range(n):
            if u != v and graph.mu[u, v] > 0:
                cap[2 * u + 1, 2 * v] = 1     # adjacency u -> v, capacity one
    return cap, size


def exceeds_bound(graph: Graph, k: int, *, separation: str = "edge") -> bool:
    """``True`` iff ``lambda^max(G) > k`` (edge) or ``kappa^max(G) > k`` (vertex).

    Equivalent to ``max_connectivity(graph, vertex_split=(separation=='vertex')) > k``
    but with two early exits: each pair's capped flow stops after ``k+1`` augmenting
    paths, and the pair loop stops at the first violating pair.  On an infeasible
    graph this typically returns after a single pair.  The pair set is exactly the
    one :func:`max_connectivity` iterates, so the predicate matches it pair for pair.
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
        cap, size = _split_capacity_matrix(graph)
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


# --- PROVE: MILP for M*(n) via cut-counting (scipy/HiGHS or Gurobi backend) ---
# L_m^dir(n) = (m-1)*M*(n) where M*(n) = max sum(w) s.t. maxflow(s,t;w)<=1 all pairs.
# Flow constraint encoded exactly: choose a cut x in {0,1}^n per pair, cap crossing
# weight via p; zero MIP gap = proof.  Shared helpers build constraints for both backends.


@dataclass
class ProofResult:
    """The outcome of a proof run."""

    n: int
    status: str               # OPTIMAL, LIMIT, INFEASIBLE, UNBOUNDED, ...
    scaled_optimum: float     # M*(n) = max total weight, exact if status OPTIMAL
    relative_gap_zero: bool   # whether the solver closed the gap to zero
    solve_seconds: float
    weight_matrix: np.ndarray | None  # a witnessing matrix w, if one was found

    def value_for(self, m: int) -> int:
        """The proved directed multigraph value ``L_m^dir(n) = (m-1) M*(n)``."""
        # Undo the (m-1) scaling: one proved M*(n) yields every m.
        return (m - 1) * int(round(self.scaled_optimum))

    def is_proof(self) -> bool:
        """Whether this run is a genuine upper-bound proof (optimal, gap zero)."""
        # Only an OPTIMAL solve with a closed gap counts as a proof; a LIMIT
        # (timed out) result is merely a feasible lower bound, never a proof.
        return self.status == "OPTIMAL" and self.relative_gap_zero


def _ordered_pairs(n: int) -> list[tuple[int, int]]:
    return [(u, v) for u in range(n) for v in range(n) if u != v]


def _two_hop_triples(n: int) -> list[tuple[int, int, int]]:
    # All (source, middle, target) with three distinct vertices: the s -> x -> t
    # detours that the two-hop inequality reasons about.
    return [(s, x, t)
            for s in range(n) for t in range(n) if s != t
            for x in range(n) if x != s and x != t]


# Proved values of M*(k) for the deletion cuts below (proved: M*(k) =
# 2(k-1) for k <= 6, proved by this very optimisation with zero gap).
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
                "use_gurobi=True but no usable Gurobi was found. Install gurobipy "
                "and activate a licence, then retry."
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
        for (s, t) in pairs:           # d+(s) + d-(t) - w[s,t] <= (n-1)*cap
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

    Returns a :class:`ProofResult`.  When its :meth:`is_proof` is true the value
    is a proven upper bound, and ``value_for(m)`` gives ``L_m^dir(n)`` for every
    ``m``.  ``use_gurobi`` picks the solver (see :func:`_pick_solver`); the default
    uses Gurobi when its licence is active and CBC otherwise.
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
        relative_gap_zero=(status == "OPTIMAL"),
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
    connectivity only through the excess, and by monotonicity (Facts M1/M2 in the
    thesis) that excess is provably zero on most steps, so no flow is needed:

    - a removal from a feasible graph stays feasible (M1), excess 0;
    - an addition while ``lam_ub <= m-2`` stays feasible (M2), excess 0.

    Only when neither shortcut applies do we run one capped predicate, and only when
    that reports an infeasible proposal do we spend the exact ``measure_full`` to get
    the penalty term right.  The float returned is byte-for-byte the one ``_energy``
    would return (the same arithmetic on the same excess), so the search trajectory
    is unchanged.  The boolean is the EXACT feasibility of ``proposal``.
    """
    edges = proposal.edge_count()
    # Decide excess = max(0, measure(proposal) - (m-1)) with the least work.
    if (is_add and lam_ub <= m - 2) or (not is_add and feasible_current):
        excess = 0                       # M2 (add) or M1 (remove): provably feasible
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
    # Multiplicity cap: simple graphs are always 0/1; multigraphs default to m-1.
    cap = 1 if variant.simple else (max_multiplicity if max_multiplicity else m - 1)
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
    cap = 1 if variant.simple else (max_multiplicity if max_multiplicity else m - 1)

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
    complete: bool          # an exhaustive run that actually finished
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

    Used to exhibit a concrete graph attaining the proved value: the better
    of the double star and the (augmented) one-directional bipartite, or
    ``None`` if neither applies to this case.
    """
    candidates: list[Graph] = []
    if not (simple and m > 2):              # a simple star needs m == 2
        candidates.append(double_star(n, m, directed=True))   # 2(n-1)(m-1) arcs
    if m == 2:
        candidates.append(one_directional_bipartite(n))       # floor(n^2/4) arcs
    elif (m - 2) < (n - n // 2):            # augmented needs m-2 < ceil(n/2)
        candidates.append(augmented_bipartite(n, m))
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
    """
    measure = _connectivity_measure(separation)
    cells = _matrix_cells(n, variant.directed)
    span = 2 if variant.simple else m       # cell value lives in range(span)
    best_count, best_graph, completed = 0, None, True
    base = Graph(n, variant)
    for tick, values in enumerate(product(range(span), repeat=len(cells))):
        if tick % 256 == 0 and time.time() > deadline:
            completed = False               # ran out before exhausting the space
            break
        candidate = base.copy()
        for (u, v), value in zip(cells, values):
            if value:
                candidate.set_multiplicity(u, v, value)
        if measure(candidate) <= m - 1 and candidate.edge_count() > best_count:
            best_count, best_graph = candidate.edge_count(), candidate.copy()
    return best_count, best_graph, completed


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


def _hyperedge_candidates(n: int, r: int, directed: bool) -> list:
    """Every possible ``r``-uniform hyperedge, undirected sets or directed pairs."""
    if directed:
        # A directed hyperedge is one tail and r-1 heads chosen from the rest.
        return [(tail, frozenset(heads))
                for tail in range(n)
                for heads in combinations([v for v in range(n) if v != tail], r - 1)]
    return [frozenset(s) for s in combinations(range(n), r)]


def _brute_force_hypergraph(
    n: int, r: int, m: int, deadline: float,
    *, directed: bool = False, vertex_split: bool = False,
) -> tuple[int, Hypergraph | None, bool]:
    """Exhaustively maximise hyperedges over all ``r``-uniform hypergraphs.

    Each possible hyperedge is present or absent, so the search visits
    ``2 ** (#candidates)`` hypergraphs; only tiny ``(n, r)`` finish.  The
    ``directed`` and ``vertex_split`` flags select which of the four hypergraph
    measures decides feasibility, exactly as ``solve`` passes them through.
    """
    candidates = _hyperedge_candidates(n, r, directed)
    best_count, best_h, completed = 0, None, True
    for tick, mask in enumerate(product((0, 1), repeat=len(candidates))):
        if tick % 256 == 0 and time.time() > deadline:
            completed = False
            break
        chosen = [candidates[i] for i, on in enumerate(mask) if on]
        hypergraph = Hypergraph(n, chosen, directed=directed)
        if (max_hyper_connectivity(hypergraph, vertex_split=vertex_split) <= m - 1
                and hypergraph.edge_count() > best_count):
            best_count, best_h = hypergraph.edge_count(), hypergraph
    return best_count, best_h, completed


def _random_hypergraph_search(
    n: int, r: int, m: int, deadline: float, seed: int,
    *, directed: bool = False, vertex_split: bool = False,
) -> tuple[int, Hypergraph | None]:
    """Greedy randomised growth: add random hyperedges while feasible, restart.

    A discovery heuristic for the hypergraph model (search is matrix-only):
    each pass shuffles the candidate hyperedges and adds each one that keeps the
    Berge connectivity within ``m - 1``; the densest pass within budget wins.  The
    feasible hypergraph it returns is the easy construction behind a lower bound.
    """
    rng = random.Random(seed)
    candidates = _hyperedge_candidates(n, r, directed)
    best_count, best_h = 0, None
    while time.time() < deadline:
        order = candidates[:]
        rng.shuffle(order)
        hypergraph = Hypergraph(n, directed=directed)
        for edge in order:
            hypergraph.add_hyperedge(edge)
            if max_hyper_connectivity(hypergraph, vertex_split=vertex_split) > m - 1:
                hypergraph.hyperedges.pop()   # this one broke feasibility; undo
        if hypergraph.edge_count() > best_count:
            best_count, best_h = hypergraph.edge_count(), hypergraph
    return best_count, (best_h if best_h is not None else Hypergraph(n, directed=directed))


def _arc_flow_at_least(out_adj: list[set[int]], n: int, s: int, t: int,
                       k: int) -> bool:
    """True if there are at least ``k`` arc-disjoint ``s``-``t`` paths.

    A plain Ford--Fulkerson with unit capacities: find an augmenting path in the
    residual (forward arcs and the reverse arcs left by earlier augmentations),
    augment, and repeat at most ``k`` times.  Used as the inner feasibility test
    of the exhaustive digraph search, where the question is only whether the
    local connectivity has reached the forbidden value ``m`` (so ``k = m``).
    """
    cap: dict[tuple[int, int], int] = {}
    for a in range(n):
        for b in out_adj[a]:
            cap[(a, b)] = 1
    for _ in range(k):
        prev = {s: s}
        stack = [s]                       # DFS for any residual augmenting path
        while stack:
            x = stack.pop()
            if x == t:
                break
            for y in range(n):
                if y not in prev and cap.get((x, y), 0) > 0:
                    prev[y] = x
                    stack.append(y)
        if t not in prev:
            return False                  # no further path: fewer than k exist
        node = t                          # walk back, pushing one unit of flow
        while node != s:
            p = prev[node]
            cap[(p, node)] -= 1
            cap[(node, p)] = cap.get((node, p), 0) + 1
            node = p
    return True


def _exhaustive_directed(
    n: int, m: int, separation: str, deadline: float,
) -> tuple[int, Graph | None, bool]:
    """Prove the simple directed maximum by a pruned exhaustive search.

    This is the honest version of the thesis's base-case search: branch and bound
    over every simple digraph on ``n`` vertices, keeping the densest one whose
    connectivity stays within ``m - 1``.  Two prunes make it finish where naive
    enumeration cannot.  Feasibility is monotone, so the include branch adds an
    arc only when the digraph is still feasible (an infeasible prefix can never be
    rescued by adding more arcs), and the bound prune drops a subtree once even
    taking every remaining arc could not beat the best found.  For the edge
    separation the feasibility test asks directly whether the new arc created
    ``m`` arc-disjoint paths for any pair it could affect (those reaching its tail
    or reachable from its head); the rarer vertex separation falls back to the
    exact checker.  Returns ``(max_count, witness, completed)``; ``completed`` is
    False if the time budget ran out first, leaving the value a lower bound.
    """
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    total = len(pairs)
    out: list[set[int]] = [set() for _ in range(n)]
    inc: list[set[int]] = [set() for _ in range(n)]
    # Seed the best at one below a known construction so the bound prune bites
    # immediately; the search still records an actual witness when it ties it.
    # Only the edge constructions are guaranteed feasible here, so seed the
    # vertex search at zero to avoid over-pruning a genuinely smaller optimum.
    seed = _directed_witness(n, m, simple=True) if separation == "edge" else None
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

    def feasible_after(u: int, v: int) -> bool:
        if separation == "edge":
            for s in reaches_to(u):
                for t in reaches_from(v):
                    if s != t and _arc_flow_at_least(out, n, s, t, m):
                        return False       # this pair reached m disjoint paths
            return True
        graph = Graph(n, SIMPLE_DIRECTED)  # vertex case: lean on the checker
        for a in range(n):
            for b in out[a]:
                graph.mu[a, b] = 1
        return max_vertex_connectivity(graph) <= m - 1

    def recurse(idx: int, count: int) -> None:
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
    return best_count[0], witness, not timed_out[0]


def solve(
    n: int, m: int, *,
    directed: bool = False, simple: bool = True,
    hypergraph: bool = False, r: int = 3,
    exhaustive: bool = False, separation: str = "edge",
    max_seconds: float = 60.0, seed: int = 0, method: str = "sa",
) -> SolveResult:
    """The single driver: prove the exact value, or discover a dense example.

    Args:
        n, m: the vertices and the forbidden number of independent routes.
        directed, simple: the two matrix axes (ignored when ``hypergraph``).
        hypergraph, r: switch to the ``r``-uniform hypergraph model instead.
        exhaustive: ``True`` to PROVE the optimum, ``False`` to DISCOVER one.
        separation: ``"edge"`` or ``"vertex"`` disjointness (matrix models).
        max_seconds: wall-clock budget; always respected.
        seed: random seed for the discovery searches.

    Returns:
        A :class:`SolveResult` whose ``bound`` is ``"exact"`` (proved),
        ``"lower"`` (a witness), or ``"upper"`` (proved, no matching witness).
    """
    start = time.time()
    deadline = start + max_seconds

    # ----- the hypergraph model --------------------------------------------
    # Same driver, a different internal measure: the edge/vertex separation and
    # the direction pick which of the four Berge measures decides feasibility.
    if hypergraph:
        vertex_split = (separation == "vertex")
        label = f"{r}-uniform {'directed ' if directed else ''}hypergraph"
        if exhaustive:
            value, witness, done = _brute_force_hypergraph(
                n, r, m, deadline, directed=directed, vertex_split=vertex_split)
            bound = "exact" if done else "lower"
            method = "brute-force enumeration"
            note = "" if done else "budget ran out; value is only a lower bound"
        else:
            value, witness = _random_hypergraph_search(
                n, r, m, deadline, seed, directed=directed, vertex_split=vertex_split)
            bound, done, method = "lower", True, "randomised greedy search"
            note = "discovery only ever yields a lower bound"
        return SolveResult(n, m, label, separation, value, bound, method,
                           time.time() - start, done, witness, note)

    # ----- the matrix models -----------------------------------------------
    variant = _variant_for(directed, simple)
    label = variant.describe()

    # DISCOVER: search within the budget; the witness found is a lower bound.
    if not exhaustive:
        if method not in ("sa", "tabu"):
            raise ValueError("method must be 'sa' or 'tabu'")
        result = _search_within_budget(variant, n, m, separation, deadline, seed, method)
        method_label = "tabu search" if method == "tabu" else "random search"
        return SolveResult(
            n, m, label, separation, result.best_edge_count, "lower",
            method_label, time.time() - start, True,
            result.best_graph, "discovery only ever yields a lower bound")

    # EXHAUSTIVE, simple directed: a pruned exhaustive digraph search is exact.
    # This is the prover for the m=2 base cases of the directed theorem, and it
    # reaches n = 6, 7 where the cut-counting cannot close the gap in any sane time.
    if directed and simple:
        value, witness, done = _exhaustive_directed(n, m, separation, deadline)
        bound = "exact" if done else "lower"
        method = "exhaustive digraph search (branch and bound)"
        note = "" if done else "budget ran out; value is only a lower bound"
        return SolveResult(n, m, label, separation, value, bound, method,
                           time.time() - start, done, witness, note)

    # EXHAUSTIVE, directed MULTIGRAPH arc problem: the cut-counting is the prover.
    if directed and separation == "edge":
        budget = max(1.0, deadline - time.time())
        proof = prove_directed_multigraph(n, time_limit=budget)
        if proof.is_proof():
            # We only reach here for a multigraph, where (m-1) M*(n) IS the value.
            value = proof.value_for(m)          # (m-1) * M*(n)
            witness = _directed_witness(n, m, simple)
            return SolveResult(n, m, label, separation, value, "exact",
                               "cut-counting (gap zero)", time.time() - start,
                               True, witness, "")
        # Timed out: fall back to the best construction as a lower bound.
        witness = _directed_witness(n, m, simple)
        low = witness.edge_count() if witness else 0
        return SolveResult(
            n, m, label, separation, low, "lower",
            "cut-counting hit the time limit; reporting a construction",
            time.time() - start, False, witness,
            "raise max_seconds to let the cut-counting close the gap")

    # EXHAUSTIVE otherwise (undirected, or vertex separation): brute force.
    value, witness, done = _brute_force_matrix(
        variant, n, m, separation, deadline)
    bound = "exact" if done else "lower"
    method = "brute-force enumeration"
    note = ("" if done else "budget ran out; value is only a lower bound "
            "(no cut-counting exists for this case)")
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


def average_max_connectivity(
    n: int, p: float, *, trials: int = 200,
    separation: str = "edge", directed: bool = False, seed: int = 0,
) -> float:
    """Estimate the average of $\\lambda^{\\max}$ over samples of $G(n, p)$."""
    rng = random.Random(seed)
    measure = _connectivity_measure(separation)
    total = sum(measure(sample_random_graph(n, p, directed, rng)) for _ in range(trials))
    return total / trials


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
        """The proved location $p^{*} = m/n$."""
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

# Four-level sensitivity palette: cool (sigma=0) -> hot (sigma=max).
_SIGMA_PALETTE = ["#52BDEC", "#F9C74F", "#F4914B", "#DC8C28"]  # 0,1,2,3+


def plot_directed_crossover(m: int, max_n: int, path: str | Path) -> None:
    """Plot the two competing directed branches and their maximum versus ``n``.

    Shows how the linear hub branch ``m(n-1)`` is overtaken by the quadratic
    augmented-bipartite branch near ``n ~ 2m``: the heart of the directed story.
    """
    ns = list(range(2, max_n + 1))
    hub = [m * (n - 1) for n in ns]                         # linear hub branch
    bipartite = [(n * n) // 4 + (m - 2) * ((n + 1) // 2) for n in ns]  # quadratic branch
    envelope = [directed_arc_lower_bound(n, m) for n in ns]  # their pointwise max

    plt.figure(figsize=(7, 4.3))
    plt.plot(ns, hub, "--", color=_KUL_DARK, label=r"hub branch $m(n-1)$")
    plt.plot(ns, bipartite, "--", color=_WARM,
             label=r"bipartite branch $\lfloor n^2/4\rfloor+(m-2)\lceil n/2\rceil$")
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

    plt.figure(figsize=(8, 5))

    # m=2,3,4: edge == vertex -- one curve per m
    agree_palette = ["#AED9EE", "#5CB4D9", _KUL_DARK]
    for m_val, color in zip([2, 3, 4], agree_palette):
        vals = [simple_undirected_edge(n, m_val) for n in ns]
        plt.plot(ns, vals, "-", color=color, linewidth=1.8, alpha=0.9,
                 label=f"$m={m_val}$: edge $=$ vertex")

    # m=5: edge and vertex (same starting point, diverge from n=6 onwards)
    edge5 = [simple_undirected_edge(n, 5) for n in ns]
    vert5 = [simple_undirected_vertex_m5(n) for n in ns]
    plt.plot(ns, edge5, "--", color=_KUL_BLUE, linewidth=2.4,
             label=r"$m=5$: edge $\ell_5(n)=\lfloor 5(n-1)/2\rfloor$")
    plt.plot(ns, vert5, "-",  color=_WARM,     linewidth=2.4,
             label=r"$m=5$: vertex $k_5(n)=\lfloor 8n/3\rfloor-3$")
    # shade only where the gap is positive
    plt.fill_between(ns, edge5, vert5, where=[v > e for v, e in zip(vert5, edge5)],
                     alpha=0.15, color=_WARM)

    plt.xlabel("number of vertices $n$")
    plt.ylabel("maximum edges")
    plt.title("Agreement through $m \\leq 4$, first divergence at $m = 5$")
    plt.legend(fontsize=9, loc="upper left")
    plt.grid(True, alpha=0.3)
    _save(path)


def plot_appearance_threshold(
    cases: list[tuple[int, int]],
    path: str | Path,
    *,
    x_values: list[float] | None = None,
    trials: int = 120,
    seed: int = 7,
) -> None:
    """The appearance threshold ``p* = m/n``, with the density axis in units of ``p*``.

    For each ``(n, m)`` in ``cases`` the curve is the estimated probability that a
    sample of ``G(n, p)`` already contains a pair of edge-connectivity at least
    ``m``, plotted against ``x = p / p*`` so the proved threshold sits at ``x = 1``
    for every ``n`` and ``m``.  As the pair grows into the regime
    ``thm:gnp-threshold`` governs, the rise steepens and pushes up to one by
    ``x = 1``: above ``p*`` the forbidden configuration is present with high
    probability, and the single density ``m/n`` -- not the model or the
    separation -- is what decides the matter.
    """
    if x_values is None:
        x_values = [round(0.3 + 0.1 * i, 2) for i in range(14)]  # 0.3 .. 1.6
    palette = [_KUL_LIGHT, _KUL_BLUE, _KUL_DARK, _WARM]

    plt.figure(figsize=(7.2, 4.6))
    for (n, m), colour in zip(cases, palette):
        p_star = m / n
        probs = [
            estimate_appearance_probability(
                n, min(0.999, x * p_star), m,
                trials=trials, separation="edge", seed=seed)
            for x in x_values
        ]
        plt.plot(x_values, probs, "o-", color=colour, markersize=4, linewidth=1.9,
                 label=fr"$n={n}$, $m={m}$  ($p^*={p_star:.3f}$)")

    plt.axvline(1.0, color="black", linestyle="--", linewidth=1.6,
                label=r"proved threshold $p^*=m/n$")
    plt.axhline(0.5, color="gray", linestyle=":", linewidth=1.0, alpha=0.6)
    plt.xlabel(r"density as a multiple of the threshold $p^* = m/n$")
    plt.ylabel(r"$\hat{P}\,[\,\lambda^{\max}\geq m\,]$")
    plt.title(r"The appearance threshold $p^* = m/n$")
    plt.ylim(-0.03, 1.03)
    plt.legend(fontsize=8.5, loc="lower right")
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


def plot_connectivity_distribution(series: dict, n: int, p: float, path: str | Path) -> None:
    """Plot overlaid histograms of the binding connectivity for several models.

    ``series`` maps a label to a list of connectivity values (one per random
    sample), as produced by :func:`montecarlo.connectivity_distribution`.  The
    integer-valued histograms are drawn on shared integer bins so the shapes can
    be compared directly across the kinds of graph.
    """
    # Shared integer bins across every series so the shapes line up exactly.
    all_values = [value for values in series.values() for value in values]
    low, high = min(all_values), max(all_values)
    levels = list(range(low, high + 1))
    colours = [_KUL_BLUE, _WARM, _KUL_DARK, _KUL_LIGHT]
    group_count = len(series)
    bar_width = 0.8 / group_count  # split each integer slot among the series

    plt.figure(figsize=(7, 4.3))
    for index, ((label, values), colour) in enumerate(zip(series.items(), colours)):
        counts = [values.count(level) for level in levels]
        # Offset each series' bars so grouped bars sit side by side per level.
        offset = (index - (group_count - 1) / 2) * bar_width
        positions = [level + offset for level in levels]
        plt.bar(positions, counts, width=bar_width, color=colour, label=label,
                edgecolor="white", linewidth=0.4)
    plt.xticks(levels)
    plt.xlabel("binding connectivity")
    plt.ylabel("number of samples")
    plt.title(f"Connectivity over random graphs, $n = {n}$, $p = {p}$")
    plt.legend()
    plt.grid(True, axis="y", alpha=0.3)
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
    from collections import Counter
    from matplotlib.colors import PowerNorm
    from matplotlib.transforms import blended_transform_factory
    from matplotlib.gridspec import GridSpec

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
    from matplotlib.patches import FancyArrowPatch

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

    fig, ax = plt.subplots(figsize=(8.6, 6.2))

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


def plot_sa_vs_tabu_convergence(
    path: str | Path, *,
    cases: tuple[tuple[int, int], ...] = ((5, 3), (7, 3)),
    budget: float = 8.0,
    seed: int = 0,
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
        for res, label, colour in ((sa, "simulated annealing", _KUL_BLUE),
                                    (tb, "tabu search", _WARM)):
            xs, ys = _running_best_trace(res)
            ax.step(xs, ys, where="post", label=label, color=colour, linewidth=2.0)
        opt = directed_multigraph_arc(n, m)
        ax.axhline(opt, linestyle=":", color=_KUL_DARK, linewidth=1.6,
                   label=f"optimum $L_3^{{\\mathrm{{dir}}}}({n}) = {opt}$")
        ax.set_title(f"directed multigraph, $n = {n}$, $m = {m}$", fontsize=11)
        ax.set_xlabel("wall-clock seconds", fontsize=9.5)
        ax.set_ylabel("densest feasible arc count", fontsize=9.5)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8.5, loc="lower right")
        # Fewer x-ticks declutters the time axis: 4 on the first panel, 6 on the
        # second, since the action concentrates early and dense ticks add noise.
        if MaxNLocator is not None:
            ax.xaxis.set_major_locator(MaxNLocator(nbins=4 if i == 0 else 6))
    _save(path)


def _save(path: str | Path, *, tight: bool = True) -> None:
    """Tighten the layout, write the file, and close the figure.

    ``tight=False`` skips ``tight_layout`` for the 3-D figures, where it
    misbehaves with the projected axes (they manage their own spacing).
    """
    import warnings
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if tight:
        # tight_layout can warn when figures contain colorbars or shared axes;
        # bbox_inches="tight" in savefig handles the actual bounding box so the
        # layout warning is cosmetic and safe to suppress.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
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

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
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
    axes[0].legend(fontsize=8.5, loc="upper left", title="model")
    fig.suptitle("Number of graphs blind enumeration must visit",
                 fontsize=12)
    _save(path)


def _draw_extremal_panel(ax, matrix, *, directed: bool) -> None:
    """Draw one extremal multiplicity matrix on ``ax`` as a circular graph.

    Vertices sit on a circle, numbered from the top.  An adjacency of
    multiplicity one is a single line (an arrowed line when ``directed``), and a
    higher multiplicity is shown by a small count label rather than parallel
    curves, so the picture stays legible.  Opposite arcs of a bidirected pair
    are bent apart.
    """
    from matplotlib.patches import FancyArrowPatch
    n = len(matrix)
    angs = [math.pi / 2 - 2 * math.pi * k / n for k in range(n)]
    pos = [(math.cos(a), math.sin(a)) for a in angs]

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
                mlabel(i, j, rad, matrix[i][j])
    else:
        for i in range(n):
            for j in range(i + 1, n):
                if matrix[i][j] == 0:
                    continue
                edge(i, j, 0.0, False)
                mlabel(i, j, 0.0, matrix[i][j])
    for k, (x, y) in enumerate(pos):
        ax.scatter([x], [y], s=300, c="white", edgecolors=_KUL_BLUE,
                   linewidths=1.6, zorder=2)
        ax.text(x, y, str(k + 1), ha="center", va="center", fontsize=9,
                zorder=3, color=_KUL_DARK)
    ax.set_xlim(-1.45, 1.45)
    ax.set_ylim(-1.45, 1.45)


def plot_extremal_gallery(path: str | Path, *,
                          gallery_json: str | Path | None = None) -> None:
    """A gallery of machine-found extremal graphs across the matrix variants.

    Reads ``figures/extremal_gallery.json`` (produced by
    :func:`gallery_extremal_graphs`) and draws a curated spread of extremal
    multiplicity matrices, one panel each, annotated with the extremal value and
    the automorphism count ``|Aut|`` computed as ``n! / labelled_count`` for the
    drawn class.  This turns the enumeration's real output into a picture rather
    than leaving it in JSON.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise RuntimeError("matplotlib is required for figures")
    import json
    if gallery_json is None:
        gallery_json = Path(__file__).resolve().parent.parent / "figures" / "extremal_gallery.json"
    data = json.loads(Path(gallery_json).read_text())
    cells = [
        ("simple_undirected_edge",   "n=5_m=3", False, "simple undirected, edge\n$m=3$, $n=5$"),
        ("simple_undirected_edge",   "n=6_m=3", False, "simple undirected, edge\n$m=3$, $n=6$"),
        ("multi_undirected_edge",    "n=5_m=3", False, "multigraph undirected, edge\n$m=3$: star at full multiplicity"),
        ("multi_undirected_edge",    "n=4_m=4", False, "multigraph undirected, edge\n$m=4$, $n=4$"),
        ("simple_directed_edge",     "n=4_m=2", True,  "simple directed, arc\n$m=2$: bidirected star"),
        ("multi_directed_edge",      "n=4_m=3", True,  "multigraph directed, arc\n$m=3$: double star"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(11, 7.4))
    for ax, (var, key, directed, title) in zip(axes.flat, cells):
        cell = data[var][key]
        cls = cell["classes"][0]
        matrix = cls["repr"]
        n = len(matrix)
        aut = math.factorial(n) // cls["labelled_count"]
        _draw_extremal_panel(ax, matrix, directed=directed)
        sub = f"value $= {cell['extremal_value']}$,  $|\\mathrm{{Aut}}| = {aut}$"
        if len(cell["classes"]) > 1:
            sub += f"  (1 of {len(cell['classes'])})"
        ax.set_title(title, fontsize=10)
        ax.text(0.5, -0.04, sub, transform=ax.transAxes, ha="center", va="top",
                fontsize=9)
        ax.set_aspect("equal")
        ax.axis("off")
    fig.suptitle("Machine-found extremal graphs", fontsize=13)
    _save(path)


_GUESS_STYLE = (0, (1, 1))   # dense dots: "we are very much guessing"


def plot_variant_grid(panels: list[dict], path: str | Path,
                      m: int | None = None) -> None:
    """All twelve variants on one grid, in the proved/conjectured/guessed language.

    ``panels`` is a row-major list of twelve dictionaries (rows = model simple,
    multi, hyper; columns = undirected edge, undirected vertex, directed arc,
    directed vertex).  Each panel may carry any of:

    ``proved`` ``(xs, ys)`` solid blue line, a theorem holding for all ``n``;
    ``conj``   ``(xs, ys)`` solid red line, a conjecture formula;
    ``guess``  ``(xs, ys)`` solid yellow line, a bare extrapolation of the
               machine points where no formula is known;
    ``band``   ``(xs, lo, hi)`` the certain interval, an easy construction below
               and the trivial maximum edge count above;
    ``exact``  ``(xs, ys)`` filled squares, sizes the machine proved;
    ``search`` ``(xs, ys)`` open circles, the search lower bounds.

    The point is one honest picture, distinguished by colour rather than dash
    pattern: a blue line is settled, a red line is conjectured, a yellow line is
    a guess, and the shaded band is the interval we are certain the truth lies in.
    """
    def draw_panel(ax, panel):
        band = panel.get("band")
        if band is not None:
            xs, lo, hi = band
            ax.fill_between(xs, lo, hi, color=_WARM, alpha=0.12,
                            label="certain interval")
            ax.plot(xs, lo, "-", color=_WARM, linewidth=0.8, alpha=0.6)
            ax.plot(xs, hi, "-", color=_WARM, linewidth=0.8, alpha=0.6)
        for branch in panel.get("branches", []):
            bxs, bys, blabel = branch
            ax.plot(bxs, bys, ":", color=_KUL_LIGHT, linewidth=1.3, label=blabel)
        if panel.get("proved") is not None:
            xs, ys = panel["proved"]
            ax.plot(xs, ys, "-", color=_KUL_BLUE, linewidth=2.3, label="proved")
        if panel.get("conj") is not None:
            xs, ys = panel["conj"]
            ax.plot(xs, ys, "-", color=_RED, linewidth=2.0, label="conjectured")
        if panel.get("guess") is not None:
            xs, ys = panel["guess"]
            ax.plot(xs, ys, "-", color=_WARM, linewidth=2.0,
                    label="guess (interpolated)")
        if panel.get("exact") is not None:
            xs, ys = panel["exact"]
            if len(xs):
                ax.plot(xs, ys, "s", color=_GREEN, markersize=7,
                        label="machine-checked (exact)")
        if panel.get("search") is not None:
            xs, ys = panel["search"]
            if len(xs):
                ax.plot(xs, ys, "o", mfc="none", mec=_VIOLET, mew=1.8,
                        markersize=8, label="search (lower bound)")
        ax.set_title(panel["title"], fontsize=9.5)
        ax.set_xlabel("vertices $n$", fontsize=8.5)
        ax.set_ylabel(panel.get("ylabel", "edges"), fontsize=8.5)
        ax.tick_params(labelsize=8)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=6.8, loc="upper left", framealpha=0.85)

    # The line styles (solid / dashed / dotted) are named in the per-panel
    # legends and spelled out in the caption, so the suptitle stays short and
    # just records the variant family and the threshold m.
    suptitle = "Erdős 915 across the twelve variants"
    if m is not None:
        suptitle += fr",  $m = {m}$"
    _variant_panel_grid(draw_panel, configs=panels, suptitle=suptitle, path=path,
                        suptitle_fontsize=13)


# --- ENUMERATION LANDSCAPES: visit every labeled graph, collect (edges, lambda^max) ---

# Row-major table of all twelve variants, matching gather_variant_grid.
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
    # row 3 — hypergraph r=3
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
]


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
    results: list[tuple[int, int]] = []

    if hypergraph:
        vertex_split = (separation == "vertex")
        candidates = _hyperedge_candidates(n, r, directed)
        for mask in product((0, 1), repeat=len(candidates)):
            chosen = [candidates[i] for i, flag in enumerate(mask) if flag]
            h = Hypergraph(n, chosen, directed=directed)
            conn = max_hyper_connectivity(h, vertex_split=vertex_split)
            results.append((h.edge_count(), conn))
        return results

    variant = _variant_for(directed, simple)
    measure = _connectivity_measure(separation)
    cells = _matrix_cells(n, directed)
    span = 2 if simple else (max_mult + 1)
    base = Graph(n, variant)
    for values in product(range(span), repeat=len(cells)):
        candidate = base.copy()
        for (u, v), value in zip(cells, values):
            if value:
                candidate.set_multiplicity(u, v, value)
        conn = measure(candidate)
        results.append((candidate.edge_count(), conn))
    return results


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
    from collections import Counter
    table: Counter = Counter()

    def record(obj):
        pcs = _pair_connectivities(obj, separation=separation, hypergraph=hypergraph)
        lmax = max(pcs, default=0)
        for c in pcs:
            table[(lmax, c)] += 1

    if hypergraph:
        candidates = _hyperedge_candidates(n, r, directed)
        for mask in product((0, 1), repeat=len(candidates)):
            chosen = [candidates[i] for i, flag in enumerate(mask) if flag]
            record(Hypergraph(n, chosen, directed=directed))
        return dict(table)

    variant = _variant_for(directed, simple)
    cells = _matrix_cells(n, directed)
    span = 2 if simple else (max_mult + 1)
    base = Graph(n, variant)
    for values in product(range(span), repeat=len(cells)):
        candidate = base.copy()
        for (u, v), value in zip(cells, values):
            if value:
                candidate.set_multiplicity(u, v, value)
        record(candidate)
    return dict(table)


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

    if cache_path.exists():
        with open(cache_path, "rb") as f:
            cached = pickle.load(f)
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
            pickle.dump(cached, f)

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

    if cache_path.exists():
        with open(cache_path, "rb") as f:
            cached = pickle.load(f)
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
            pickle.dump(cached, f)

    return cached


def plot_scatter_lambda_edges(
    enum_data: dict[str, list[tuple[int, int]]],
    path: str | Path,
) -> None:
    """Extremal envelope of edge count against binding connectivity, all twelve variants.

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
                  "across all twelve variants (full enumeration)"),
        suptitle_fontsize=13)


def _variant_panel_grid(draw_panel, *, suptitle: str, path: str | Path,
                        configs=None, suptitle_fontsize: float = 12.0,
                        row_label_fontsize: float = 12.0) -> None:
    """Shared scaffold for every twelve-panel variant grid (three model rows by
    four columns): the distribution grids, the proved/conjectured bound grid, the
    sampled grid, and the extremal-envelope scatter.  Builds the axes, calls
    ``draw_panel(ax, cfg)`` on each panel config in turn, adds the per-row model
    labels and the suptitle, and saves.  Only the per-panel drawing and the panel
    configs differ between the grids, so the caller supplies both; everything else
    (layout, row labels, save) lives here once.  ``configs`` defaults to the
    twelve enumeration variants but may be any 12-item list (e.g. the sampled
    configs or a precomputed ``panels`` list).
    """
    if configs is None:
        configs = _VARIANT_ENUM_CONFIGS
    fig, axes = plt.subplots(3, 4, figsize=(16, 11))
    for cfg, ax in zip(configs, axes.flat):
        draw_panel(ax, cfg)
    for row, name in enumerate(("simple", "multigraph", "hypergraph $r=3$")):
        axes[row, 0].annotate(name, xy=(-0.32, 0.5), xycoords="axes fraction",
                              rotation=90, ha="center", va="center",
                              fontsize=row_label_fontsize, fontweight="bold",
                              color=_KUL_DARK)
    fig.suptitle(suptitle, fontsize=suptitle_fontsize)
    fig.tight_layout(rect=(0.02, 0.0, 1.0, 0.97))
    _save(path)


def plot_conn_dist_grid(
    enum_data: dict[str, list[tuple[int, int]]],
    m: int,
    path: str | Path,
    known_maxima: dict[str, int] | None = None,
) -> None:
    """12-panel histogram of lambda_max distribution, all variants, fixed m.

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
        # The feasibility boundary is identical in all twelve panels, so it is
        # explained once in the title and caption rather than repeated as a
        # legend in every panel. A legend is drawn only when a per-panel known
        # maximum line is present (a value that genuinely differs by panel).
        if known_maxima and key in known_maxima:
            ax.legend(fontsize=6.8, loc="upper right", framealpha=0.85)
        ax.text(0.02, 0.98, f"$n={cfg['enum_n']}$", transform=ax.transAxes,
                ha="left", va="top", fontsize=8, color="grey")

    suptitle = (fr"Connectivity distribution across all twelve variants, $m = {m}$ "
                fr"(blue = feasible $\lambda^{{\max}} \leq {threshold}$, red = infeasible)")
    _variant_panel_grid(draw_panel, suptitle=suptitle, path=path,
                        row_label_fontsize=12)


def _midrange_lambda_threshold(hi: int) -> int:
    """A per-variant connectivity boundary at the midpoint of the achievable range.

    The distribution figures split graphs by ``lambda^max`` into a blue (low) and
    a red (high) population.  A single global boundary collapses some panels to one
    colour (every graph below it, or almost none), because the twelve variants
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

    suptitle = ("Pair-connectivity distribution across all twelve variants "
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

    suptitle = ("Edge-count distribution across all twelve variants "
                r"(stacked by connectivity, split at each variant's mid-range "
                r"$\lambda^{\max}$: blue low-connectivity graphs, red high)")
    _variant_panel_grid(draw_panel, suptitle=suptitle, path=path,
                        row_label_fontsize=11)


# --- 3-D BOUND SURFACE: cache solve() over (variant, n, m) grid; plot_variant_3d_surfaces draws it ---

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
    if vkey == "multi_directed_edge":               # cut-counting proves n<=6
        return min(directed_multigraph_arc(n, m), (m - 1) * tri_dir) if n <= 6 else None
    if vkey == "multi_directed_vertex":             # = simple digraph, exact m=2
        return min(directed_arc_lower_bound(n, 2), tri_dir) if m == 2 else None
    if vkey == "hyper_undirected_edge":             # incidence-rank, all m
        return min(hypergraph_edge(n, m, 3), tri_hyp)
    if vkey == "hyper_undirected_vertex":           # incidence-rank lemma, m<=3
        return min(hypergraph_edge(n, m, 3), tri_hyp) if m <= 3 else None
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
    if cache_path.exists():
        with open(cache_path) as f:
            cache = json.load(f)
    else:
        cache = {}

    changed = False
    ns = list(range(n_range[0], n_range[1] + 1))
    ms = list(range(m_range[0], m_range[1] + 1))

    for cfg in _SURFACE_VARIANT_CONFIGS:
        vkey = cfg["key"]
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
                    continue  # open cell already searched; keep the lower bound
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

    if changed:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w") as f:
            json.dump(cache, f)

    return cache


def plot_variant_3d_surfaces(
    cache_path: str | Path,
    path: str | Path,
) -> None:
    """3-D bar chart of the optimal bound over the (n, m) grid, all twelve variants.

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

        # Same camera for every panel so the twelve are read side by side, and a
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
    from matplotlib.patches import Patch
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
    """3-D bar chart of the lambda_max distribution over p, for three representative variants.

    x = p (edge probability), y = lambda_max value, z = fraction of samples.
    Shows the threshold shift at p* = m/n clearly: the distribution moves from
    low connectivity to high connectivity as p crosses the threshold.
    Three panels: undirected edge (uses ``n``), directed arc (uses ``n``),
    hypergraph edge (uses min(n, 10) to keep flow computation fast).
    """
    if p_values is None:
        p_values = [i / 20.0 for i in range(1, 20)]  # 0.05, 0.10, ..., 0.95

    rng = random.Random(seed)
    # Hypergraph flow computation scales poorly: cap n at 8 for that panel.
    n_hyper = min(n, 8)

    variants_3d = [
        dict(label="undirected edge", directed=False, separation="edge",
             hypergraph=False, panel_n=n),
        dict(label="directed arc",    directed=True,  separation="edge",
             hypergraph=False, panel_n=n),
        dict(label=f"hypergraph edge ($r=3$, $n={n_hyper}$)", directed=False,
             separation="edge", hypergraph=True, panel_n=n_hyper),
    ]

    fig = plt.figure(figsize=(18, 6))

    for panel_idx, vdesc in enumerate(variants_3d):
        ax = fig.add_subplot(1, 3, panel_idx + 1, projection="3d")
        panel_n = vdesc["panel_n"]

        all_conn_vals: list[int] = []
        dist_by_p: list[tuple[float, list[int]]] = []

        for p in p_values:
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

        for p, conn_list in dist_by_p:
            total = len(conn_list)
            for lv in levels:
                frac = conn_list.count(lv) / total
                if frac > 0:
                    ax.bar3d(p - 0.02, lv - 0.4, 0, 0.04, 0.8, frac,
                             color=_KUL_BLUE, alpha=0.7, shade=True)

        # Threshold line at p* = m/panel_n
        p_star = m / panel_n
        for lv in levels:
            ax.plot([p_star, p_star], [lv - 0.4, lv + 0.4], [0, 0],
                    color=_WARM, linewidth=0.5, alpha=0.4)
        zmax = max(conn_list.count(lv) / len(conn_list)
                   for _, conn_list in dist_by_p
                   for lv in levels
                   if conn_list.count(lv) > 0)
        ax.plot([p_star, p_star], [lo, hi], [zmax * 0.9, zmax * 0.9],
                color=_WARM, linewidth=2.5, linestyle="--",
                label=f"$p^* = m/n = {m}/{panel_n}$")

        ax.set_title(vdesc["label"], fontsize=10)
        ax.set_xlabel("$p$", fontsize=9)
        ax.set_ylabel(r"$\lambda^{\max}$", fontsize=9)
        ax.set_zlabel("fraction", fontsize=9)
        ax.tick_params(labelsize=7)

    fig.suptitle(
        fr"Distribution of $\lambda^{{\max}}$ vs edge density $p$ in $G({n}, p)$, "
        fr"$m = {m}$ (threshold at $p^* = m/n$)",
        fontsize=12,
    )
    _save(path, tight=False)


# --- OPEN-VARIANT EXPLORATION: hypergraph vertex connectivity, fractional search tools ---


def hypergraph_vertex_m2(n: int, r: int) -> int:
    """``floor((n-1)/(r-1))`` hyperedges for the ``r``-uniform VERTEX problem at m=2.

    Proved (see the commented block in the appendix): kappa^max <= 1 holds iff
    the bipartite incidence graph is a forest, because a Berge cycle yields two
    routes that are hyperedge-disjoint and internally vertex-disjoint, and
    conversely.  A forest gives r*q <= n + q - 1, i.e. q <= (n-1)/(r-1), and
    the star hypertree attains the floor.  Hence the vertex and edge problems
    agree at m = 2 for every uniformity r.
    """
    return (n - 1) // (r - 1)


def max_hyper_vertex_connectivity(hypergraph: Hypergraph) -> int:
    """``kappa^max`` for the hypergraph vertex problem (readability wrapper)."""
    return max_hyper_connectivity(hypergraph, vertex_split=True)


def _hyper_codegree_ok(edges, bound: int) -> bool:
    """Necessary feasibility filter: two vertices in > ``bound`` common
    hyperedges already carry that many one-step disjoint Berge routes."""
    from collections import Counter

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
    non-isomorphic graphs in graph6 to stdout and we parse each with networkx.
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
    n = mu.shape[0]
    canon = _canonical_form(mu)
    return sum(1 for perm in permutations(range(n))
               if mu[np.ix_(list(perm), list(perm))].tobytes() == canon)


def _hyper_canonical(hyperedges: list, n: int, directed: bool) -> tuple:
    """Canonical key for a hyperedge collection under vertex permutation.

    Each edge is a frozenset (undirected) or a ``(tail, frozenset(heads))``
    pair (directed).  Returns the lex-minimum over all n! relabellings,
    represented as a tuple of sorted-tuple edge representations.
    """
    best: tuple | None = None
    for perm in permutations(range(n)):
        p = list(perm)
        if directed:
            relabeled: tuple = tuple(sorted(
                (p[tail], tuple(sorted(p[h] for h in heads)))
                for (tail, heads) in hyperedges
            ))
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
            return tuple(sorted(
                (p[tail], tuple(sorted(p[h] for h in heads)))
                for (tail, heads) in hyperedges
            ))
        return tuple(sorted(
            tuple(sorted(p[v] for v in edge)) for edge in hyperedges
        ))

    return sum(1 for perm in permutations(range(n))
               if _relabel(list(perm)) == canon)


def _hyper_to_lists(hyperedges: list, directed: bool) -> list:
    """Convert hyperedges to JSON-serialisable sorted integer lists."""
    if directed:
        return [[tail, sorted(heads)] for (tail, heads) in hyperedges]
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
) -> tuple[list[list], bool]:
    """DFS over all r-uniform hypergraphs on n vertices with exactly ``target`` edges.

    Iterates candidate hyperedges in order (include / exclude) and prunes
    immediately when adding a hyperedge pushes the connectivity above m-1
    (monotonicity: adding edges never decreases connectivity, so no superset
    can be feasible at that branch either).  Returns ``(reps, timed_out)``
    where each representative in ``reps`` is a list of JSON-serialisable
    sorted vertex lists.
    """
    candidates = _hyperedge_candidates(n, r, directed)
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
    """Collect every non-isomorphic extremal graph for all 12 variants at small n, m.

    For each (variant, n, m) triple where the enumeration finishes within
    ``time_per_case`` seconds, the function:

    1. runs a short repeated search to discover the extremal edge count;
    2. exhaustively enumerates every graph achieving that count;
    3. deduplicates by isomorphism class and records ``n! / |Aut(G)|`` (the
       number of labelled copies) per class.

    Returns a JSON-serialisable dict with structure::

        result[variant_key]["n={n}_m={m}"] = {
            "extremal_value": int,
            "classes": [{"repr": <matrix or edge list>, "labelled_count": int}],
            "total_labelled": int,   # sum of labelled_count over all classes
            "complete": bool,        # False when the deadline was hit
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
    """
    matrix_configs: list[tuple[str, Variant, str]] = [
        ("simple_undirected_edge",   SIMPLE_UNDIRECTED, "edge"),
        ("simple_undirected_vertex", SIMPLE_UNDIRECTED, "vertex"),
        ("simple_directed_edge",     SIMPLE_DIRECTED,   "edge"),
        ("simple_directed_vertex",   SIMPLE_DIRECTED,   "vertex"),
        ("multi_undirected_edge",    MULTI_UNDIRECTED,  "edge"),
        ("multi_undirected_vertex",  MULTI_UNDIRECTED,  "vertex"),
        ("multi_directed_edge",      MULTI_DIRECTED,    "edge"),
        ("multi_directed_vertex",    MULTI_DIRECTED,    "vertex"),
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
                    "extremal_value": best_val,
                    "classes": classes,
                    "total_labelled": sum(c["labelled_count"] for c in classes),
                    "complete": not timed_out,
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
                        "extremal_value": best_val, "classes": [],
                        "total_labelled": 0, "complete": False,
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
                    "extremal_value": best_val,
                    "classes": classes,
                    "total_labelled": sum(c["labelled_count"] for c in classes),
                    "complete": not timed_out,
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
        queue = [source]
        while queue and parent[target] == -1:
            u = queue.pop(0)                       # FIFO: shortest augmenting path
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
        #   assert result.is_proof() and round(result.scaled_optimum) == 10
        #
        # The confirmed run (2026-06-13) is logged in program/logs/selftest_check.log
        # (search "n=6 OPTIMAL M*(6)=10 in 1315s").  Omitting n=6 from this loop is
        # not an error in the proof -- the proof ran -- but it means this self-test
        # alone does not reproduce the full n<=6 certification.
        for n in [3, 4, 5]:
            result = prove_directed_multigraph(n, time_limit=300.0)
            check(f"n={n}: status={result.status}, M*={result.scaled_optimum:.1f}, proof={result.is_proof()}",
                  result.is_proof() and round(result.scaled_optimum) == 2 * (n - 1))

        section("Prover: the valid inequalities sharpen but never move the optimum")
        # Turning the two-hop and symmetry-breaking rows off leaves the BARE exact
        # cut formulation, which must still prove the same M*(3) = 4.  If any row we
        # call a "valid inequality" were in fact invalid, it would cut a feasible
        # point and shift this optimum -- so this is the regression tripwire that
        # guards the prover's soundness, not just a re-run of the value.
        bare = prove_directed_multigraph(3, time_limit=120.0,
                                         use_two_hop=False, use_symmetry_breaking=False)
        check(f"M*(3) with the tighteners off = {bare.scaled_optimum:.1f} (expect 4), proof={bare.is_proof()}",
              bare.is_proof() and round(bare.scaled_optimum) == 4)

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
    found = solve(4, 2, directed=True, simple=True, exhaustive=False,
                  max_seconds=3.0)
    check(f"solve discovery simple-directed n=4,m=2: {found.value} ({found.bound})",
          found.bound == "lower" and found.value == 6)
    # Exhaustive undirected by brute force: ell_2(5) = n-1 = 4 (a spanning tree).
    tree = solve(5, 2, directed=False, simple=True, exhaustive=True,
                 max_seconds=30.0)
    check(f"solve exhaustive simple-undirected n=5,m=2: {tree.value} ({tree.bound})",
          tree.proven and tree.value == 4)
    # Hypergraph discovery returns a feasible lower bound for the r=3, m=2 case.
    hyper = solve(7, 2, hypergraph=True, r=3, exhaustive=False, max_seconds=3.0)
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

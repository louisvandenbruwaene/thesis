"""The single solver: one solve() call handles every kind of question."""

import shutil
import time
import unittest
from unittest.mock import patch

import itertools

import numpy as np

import random

from erdos915_unified import (
    solve,
    Graph,
    Hypergraph,
    MULTI_DIRECTED,
    MULTI_UNDIRECTED,
    Variant,
    hyper_connectivity,
    local_vertex_connectivity,
    max_hyper_connectivity,
    max_multigraph_vertex,
    max_vertex_connectivity,
    directed_multigraph_arc,
    exceeds_bound,
    max_edge_connectivity,
    _brute_force_matrix,
    _connectivity_measure,
    _matrix_cells,
    enumerate_extremal_directed_multigraphs as _dfs_enum,
    enumerate_extremal_directed_multigraphs_via_generation as _gen_enum,
    _decorate_support_worker,
    _canonical_form,
    _aut_count_matrix,
    _directed_witness,
)


class Solve(unittest.TestCase):
    def test_exhaustive_simple_directed_is_exact(self):
        r = solve(4, 2, directed=True, simple=True, exhaustive=True, max_seconds=120.0)
        self.assertTrue(r.proven)
        self.assertEqual(r.bound, "exact")
        self.assertEqual(r.value, 6)

    def test_discovery_returns_a_lower_bound(self):
        # verification stays on sa; tabu is the default for solving the problems
        r = solve(4, 2, directed=True, simple=True, exhaustive=False,
                  max_seconds=3.0, method="sa")
        self.assertEqual(r.bound, "lower")
        self.assertEqual(r.value, 6)
        self.assertFalse(r.complete)

    def test_matrix_discovery_defaults_to_tabu(self):
        r = solve(3, 2, directed=True, simple=True, exhaustive=False,
                  max_seconds=0.0)
        self.assertEqual(r.method, "tabu search")
        self.assertEqual(r.bound, "lower")
        self.assertFalse(r.complete)

    def test_exhaustive_undirected_finds_the_spanning_tree(self):
        r = solve(5, 2, directed=False, simple=True, exhaustive=True, max_seconds=30.0)
        self.assertTrue(r.proven)
        self.assertEqual(r.value, 4)  # a spanning tree on 5 vertices

    def test_directed_multigraph_is_proved(self):
        # No pulp needed: solve() returns the closed form of thm:dir-multi-full
        # for this variant and checks it against a named witness.  It used to
        # route through the MILP certifier, and the skip that guarded that is
        # gone, so this branch is now covered on a minimal numpy+scipy install.
        r = solve(4, 3, directed=True, simple=False, exhaustive=True, max_seconds=120.0)
        self.assertTrue(r.proven)
        self.assertEqual(r.value, 12)  # L_3^dir(4) = 2(n-1)(m-1) = 12
        self.assertIn("closed form", r.method)

    def test_vertex_separation_undirected(self):
        # k_2(n) = n - 1: no cycle is allowed, so a spanning tree is extremal.
        r = solve(5, 2, directed=False, simple=True, separation="vertex",
                  exhaustive=True, max_seconds=30.0)
        self.assertTrue(r.proven)
        self.assertEqual(r.value, 4)

    def test_hypergraph_discovery(self):
        r = solve(7, 2, hypergraph=True, r=3, exhaustive=False, max_seconds=3.0,
                  method="random-greedy")
        self.assertEqual(r.bound, "lower")
        self.assertEqual(r.value, 3)
        self.assertFalse(r.complete)
        self.assertEqual(r.method, "randomised greedy search")

    def test_hypergraph_discovery_rejects_matrix_search_methods(self):
        with self.assertRaisesRegex(ValueError, "random-greedy"):
            solve(7, 2, hypergraph=True, r=3, exhaustive=False,
                  max_seconds=0.1, method="sa")

    def test_result_describe_is_readable(self):
        r = solve(4, 2, directed=True, simple=True, exhaustive=True, max_seconds=120.0)
        self.assertIn("value", r.describe())

    def test_invalid_separation_is_rejected(self):
        with self.assertRaises(ValueError):
            solve(4, 2, separation="edges")

    def test_named_multidigraph_witness_attains_the_proved_value(self):
        for n, m in ((6, 3), (8, 3), (9, 3), (8, 4), (10, 3)):
            with self.subTest(n=n, m=m):
                witness = _directed_witness(n, m, simple=False)
                self.assertIsNotNone(witness)
                self.assertEqual(witness.edge_count(), directed_multigraph_arc(n, m))
                self.assertLessEqual(max_edge_connectivity(witness), m - 1)

    def test_missing_closed_form_witness_raises_at_runtime(self):
        with patch("erdos915_unified._directed_witness", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "no named witness"):
                solve(6, 3, directed=True, simple=False, exhaustive=True)

    def test_wrong_closed_form_witness_raises_at_runtime(self):
        witness = _directed_witness(6, 3, simple=False)
        u, v, _ = next(witness.edges())
        witness.remove_edge(u, v)
        with patch("erdos915_unified._directed_witness", return_value=witness):
            with self.assertRaisesRegex(RuntimeError, "named witness has"):
                solve(6, 3, directed=True, simple=False, exhaustive=True)

    def test_simple_directed_witness_includes_the_hub(self):
        witness = _directed_witness(4, 3, simple=True)
        self.assertIsNotNone(witness)
        self.assertEqual(witness.edge_count(), 9)
        self.assertLessEqual(max_edge_connectivity(witness), 2)

    def test_automorphism_count_includes_identity(self):
        mu = np.zeros((4, 4), dtype=int)
        mu[0, 1] = mu[1, 0] = 1
        self.assertGreaterEqual(_aut_count_matrix(mu), 1)


@unittest.skipIf(shutil.which("geng") is None, "nauty's geng is not installed")
class GengGeneration(unittest.TestCase):
    """The geng-seeded enumerator must return exactly the same isomorphism
    classes as the DFS enumerator wherever the DFS one is a sound complete
    search (n <= 6).  This pins down the new generation pipeline against the
    method whose values are already in the thesis."""

    @staticmethod
    def _classes(reps):
        return {_canonical_form(mu) for mu in reps}

    def test_matches_dfs_at_n4(self):
        # n = 4, m = 3: full target range and a degree cap.  Fast, and the DFS
        # enumerator is provably complete here, so equality is the gold standard.
        for target, cap in [(12, None), (10, None), (8, None), (8, 6), (6, None)]:
            with self.subTest(target=target, cap=cap):
                a = self._classes(_dfs_enum(4, 3, target, max_degree=cap))
                b = self._classes(_gen_enum(4, 3, target, max_degree=cap))
                self.assertEqual(a, b)

    def test_extremal_is_the_doubled_spanning_trees(self):
        # At n <= 6 the extremal directed multigraphs are exactly the doubled
        # bidirected spanning trees, one per unlabelled tree: 2 on 4 vertices.
        reps = _gen_enum(4, 3, 12)            # L_3^dir(4) = 2(n-1)(m-1) = 12
        self.assertEqual(len(self._classes(reps)), 2)


class SupportWorker(unittest.TestCase):
    """The per-support decorator is the unit the generation enumerator fans out
    across processes.  Over every support it must reproduce the DFS classes, so
    the parallel refactor is covered here even without geng on PATH."""

    @staticmethod
    def _all_supports(n, min_e, max_e):
        # Every non-isomorphic simple graph on n vertices in the edge range, the
        # output geng would feed the enumerator, by brute force + canonical dedup.
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        seen, out = set(), []
        for mask in itertools.product((0, 1), repeat=len(pairs)):
            if not (min_e <= sum(mask) <= max_e):
                continue
            mu = np.zeros((n, n), dtype=int)
            edges = []
            for (i, j), bit in zip(pairs, mask):
                if bit:
                    mu[i, j] = mu[j, i] = 1
                    edges.append((i, j))
            key = _canonical_form(mu)
            if key not in seen:
                seen.add(key)
                out.append(edges)
        return out

    def test_worker_union_matches_dfs_at_n4(self):
        n, m, target = 4, 3, 12
        supports = self._all_supports(n, (target + 3) // 4, min(target, n * (n - 1) // 2))
        reps = []
        for edges in supports:
            reps.extend(_decorate_support_worker((n, m, target, None, True, edges)))
        worker = {_canonical_form(mu) for mu in reps}
        dfs = {_canonical_form(mu) for mu in _dfs_enum(n, m, target)}
        self.assertEqual(worker, dfs)


class MultigraphVertexIncidenceConvention(unittest.TestCase):
    """The two multigraph VERTEX variants under the incidence convention.

    A route is a path of the incidence graph and two routes may share neither an
    edge nor an intermediate vertex, so q parallel edges between u and v are q
    internally disjoint routes (sec:incidence-convention).  The multigraph
    vertex problem K_m(n) is then a problem of its own with every multiplicity
    capped at m - 1, exactly as in the edge separation, and solve() must treat
    it that way rather than fall back to the simple graph.  These tests pin the
    local measure, the unit step, the small exact values proved in the appendix,
    and the agreement of the graph checker with the hypergraph checker at r = 2,
    which is where the convention comes from.
    """

    @staticmethod
    def _as_hypergraph(graph):
        """The same multigraph as a 2-uniform multihypergraph, one hyperedge per copy."""
        n = graph.num_vertices
        directed = graph.variant.directed
        h = Hypergraph(n, directed=directed, r=2)
        for u in range(n):
            for v in range(u + 1 if not directed else 0, n):
                if u == v:
                    continue
                for _ in range(int(graph.mu[u, v])):
                    h.add_hyperedge((u, [v]) if directed else [u, v])
        return h

    def test_two_parallel_edges_are_two_routes(self):
        g = Graph(2, MULTI_UNDIRECTED)
        g.set_multiplicity(0, 1, 2)
        self.assertEqual(local_vertex_connectivity(g, 0, 1), 2)
        g.set_multiplicity(0, 1, 5)
        self.assertEqual(local_vertex_connectivity(g, 0, 1), 5)

    def test_one_parallel_edge_raises_the_local_value_by_exactly_one(self):
        rng = random.Random(3)
        for variant in (MULTI_UNDIRECTED, MULTI_DIRECTED):
            for _ in range(15):
                g = Graph(5, variant)
                for u in range(5):
                    for v in range(5):
                        if u != v and (variant.directed or u < v) and rng.random() < 0.5:
                            g.set_multiplicity(u, v, rng.randint(1, 3))
                u, v = rng.sample(range(5), 2)
                if g.mu[u, v] == 0:
                    continue
                before = local_vertex_connectivity(g, u, v)
                g.set_multiplicity(u, v, int(g.mu[u, v]) + 1)
                self.assertEqual(local_vertex_connectivity(g, u, v), before + 1)

    def test_one_parallel_edge_raises_kappa_max_by_at_most_one(self):
        # prop:monotone in the vertex separation for multigraphs: the new copy
        # is one more route between its own endpoints and can join at most one
        # route family between any other pair.
        rng = random.Random(4)
        for variant in (MULTI_UNDIRECTED, MULTI_DIRECTED):
            for _ in range(15):
                g = Graph(5, variant)
                for u in range(5):
                    for v in range(5):
                        if u != v and (variant.directed or u < v) and rng.random() < 0.5:
                            g.set_multiplicity(u, v, rng.randint(1, 2))
                before = max_vertex_connectivity(g)
                u, v = rng.sample(range(5), 2)
                g.set_multiplicity(u, v, int(g.mu[u, v]) + 1)
                after = max_vertex_connectivity(g)
                self.assertGreaterEqual(after, before)
                self.assertLessEqual(after, before + 1)

    def test_K_2_is_n_minus_one(self):
        # thm:hyper-vertex-m2 at r = 2: at m = 2 every multiplicity is at most
        # one, so K_2(n) = k_2(n) = n - 1, the spanning tree.
        for n in (2, 3, 4, 5):
            r = solve(n, 2, directed=False, simple=False, separation="vertex",
                      exhaustive=True, max_seconds=60.0)
            self.assertEqual(r.bound, "exact")
            self.assertEqual(r.value, n - 1)

    def test_K_3_is_twice_n_minus_one(self):
        # thm:hyper-vertex-m3 at r = 2: K_3(n) = 2(n - 1), the thickened tree,
        # and the exhaustive maximum must exhibit a multigraph witness with a
        # doubled edge, which the old reduction never could.
        for n in (2, 3, 4, 5):
            r = solve(n, 3, directed=False, simple=False, separation="vertex",
                      exhaustive=True, max_seconds=60.0)
            self.assertEqual(r.bound, "exact")
            self.assertEqual(r.value, 2 * (n - 1))
            self.assertEqual(int(r.witness.mu.max()), 2)
            self.assertLessEqual(max_vertex_connectivity(r.witness), 2)

    def test_K_5_of_4_exceeds_the_edge_value(self):
        # K_5(4) = 14 > 12 = L_5(4): the vertex and edge problems differ on
        # multigraphs, so neither is a relabelling of the other.
        r = solve(4, 5, directed=False, simple=False, separation="vertex",
                  exhaustive=True, max_seconds=120.0)
        self.assertEqual((r.bound, r.value), ("exact", 14))
        self.assertEqual(max_multigraph_vertex(4, 5)[:1], (14,))
        self.assertEqual(solve(4, 5, directed=False, simple=False,
                               separation="edge", exhaustive=True,
                               max_seconds=60.0).value, 12)

    def test_discovery_finds_multigraph_witnesses(self):
        # The tabu search runs on the multigraph move set with cap m - 1, so
        # it must at least reach the thickened tree.
        for directed in (False, True):
            r = solve(4, 3, directed=directed, simple=False, separation="vertex",
                      exhaustive=False, max_seconds=5.0, seed=0)
            self.assertGreaterEqual(r.value, (2 if directed else 1) * 2 * 3)
            self.assertLessEqual(max_vertex_connectivity(r.witness), 2)
            self.assertEqual(r.bound, "lower")

    def test_graph_and_hypergraph_checkers_agree_at_r_2(self):
        # The convention is the hypergraph one specialised to r = 2: one gate of
        # capacity mu per distinct hyperedge.  Both implementations must give the
        # same local and maximum values on random multigraphs, undirected and
        # directed alike.
        rng = random.Random(5)
        for variant in (MULTI_UNDIRECTED, MULTI_DIRECTED):
            for _ in range(20):
                n = rng.randint(3, 6)
                g = Graph(n, variant)
                for u in range(n):
                    for v in range(n):
                        if u != v and (variant.directed or u < v) and rng.random() < 0.6:
                            g.set_multiplicity(u, v, rng.randint(1, 3))
                h = self._as_hypergraph(g)
                for s_, t_ in itertools.permutations(range(n), 2):
                    self.assertEqual(
                        local_vertex_connectivity(g, s_, t_),
                        hyper_connectivity(h, s_, t_, vertex_split=True),
                        f"{variant.describe()} n={n} pair {(s_, t_)}\n{g.mu}")
                self.assertEqual(max_vertex_connectivity(g),
                                 max_hyper_connectivity(h, vertex_split=True))

    def test_directed_exact_values_at_m_2_and_3(self):
        # m = 2: K_2^dir(n) = M(n) (every multiplicity at most one).  m = 3: the
        # search-and-exhaust values K_3^dir(n) for n <= 4 equal (m-1) M(n),
        # the lower bound from the arc extremiser via kappa <= lambda.
        for n in (2, 3, 4):
            r = solve(n, 2, directed=True, simple=False, separation="vertex",
                      exhaustive=True, max_seconds=60.0)
            self.assertEqual((r.bound, r.value),
                             ("exact", max(2 * (n - 1), n * n // 4)))
            r = solve(n, 3, directed=True, simple=False, separation="vertex",
                      exhaustive=True, max_seconds=120.0)
            self.assertEqual((r.bound, r.value),
                             ("exact", 2 * max(2 * (n - 1), n * n // 4)))


class PrunedEnumerationMatchesBlind(unittest.TestCase):
    """The pruned enumerator returns exactly what a blind sweep would.

    ``_brute_force_matrix`` discards two kinds of branch: those whose partial
    graph already breaks the connectivity ceiling (no completion of it can be
    feasible, since adding edges never lowers a connectivity) and those whose
    best conceivable completion cannot beat the graph already in hand.  Neither
    can drop the true maximum.  This test is the guard on that argument: it runs
    the pruned search against a blind product sweep written separately below, on
    every variant and every size the blind one can still reach.
    """

    @staticmethod
    def _blind(variant, n, m, separation):
        """Every graph of the variant, measured, densest feasible one kept."""
        measure = _connectivity_measure(separation)
        cells = _matrix_cells(n, variant.directed)
        span = 2 if variant.simple else m
        best = 0
        for values in itertools.product(range(span), repeat=len(cells)):
            graph = Graph(n, variant)
            for (u, v), value in zip(cells, values):
                if value:
                    graph.set_multiplicity(u, v, value)
            if measure(graph) <= m - 1 and graph.edge_count() > best:
                best = graph.edge_count()
        return best

    def test_pruned_equals_blind_on_every_variant(self):
        variants = [Variant(directed=False, simple=True),
                    Variant(directed=False, simple=False),
                    Variant(directed=True, simple=True)]
        checked = 0
        for variant in variants:
            for separation in ("edge", "vertex"):
                if not variant.simple and separation == "vertex":
                    continue        # solve() reduces this to the simple problem
                for n in range(2, 6):
                    for m in (2, 3, 4):
                        span = 2 if variant.simple else m
                        if span ** len(_matrix_cells(n, variant.directed)) > 200000:
                            continue        # keep the blind sweep tractable
                        blind = self._blind(variant, n, m, separation)
                        value, witness, done = _brute_force_matrix(
                            variant, n, m, separation, time.time() + 120.0)
                        self.assertTrue(done)
                        self.assertEqual(
                            value, blind,
                            f"{variant} sep={separation} n={n} m={m}: "
                            f"pruned {value} against blind {blind}")
                        if witness is not None:
                            # the witness must really be feasible and really
                            # carry the reported count, not merely tie the number
                            self.assertEqual(witness.edge_count(), value)
                            self.assertFalse(exceeds_bound(
                                witness, m - 1, separation=separation))
                        checked += 1
        self.assertGreater(checked, 20)


if __name__ == "__main__":
    unittest.main()

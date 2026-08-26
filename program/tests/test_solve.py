"""The single solver: one solve() call handles every kind of question."""

import shutil
import time
import unittest
from unittest.mock import patch

import itertools

import numpy as np

from erdos915_unified import (
    solve,
    Graph,
    Variant,
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


class MultigraphVertexObjective(unittest.TestCase):
    """The two multigraph VERTEX variants count adjacencies, not multiplicity.

    sec:parallel-convention poses them that way because a parallel copy never
    raises kappa, so counted with multiplicity the maximum would be infinite and
    the question empty.  solve() must therefore report the simple value on the
    underlying graph.  It once reported Graph.edge_count() on a multigraph, which
    is (m-1) times too large and returns a witness whose parallel copies do no
    work; these tests pin the objective down in both modes and both directions.
    """

    def _check(self, *, directed, exhaustive, n, m, expected):
        r = solve(n, m, directed=directed, simple=False, separation="vertex",
                  exhaustive=exhaustive, max_seconds=30.0)
        self.assertEqual(r.value, expected)
        # The witness must be simple: every adjacency at multiplicity one, so
        # the reported count really is an adjacency count.
        mu = r.witness.mu
        self.assertTrue(((mu == 0) | (mu == 1)).all(), f"witness not simple:\n{mu}")
        # And the count must agree with the witness read as adjacencies.
        adjacencies = int((mu > 0).sum())
        if not directed:
            adjacencies //= 2
        self.assertEqual(r.value, adjacencies)
        self.assertIn("adjacencies", r.note)

    def test_exhaustive_undirected_counts_adjacencies(self):
        # K_3 has kappa^max = 2 = m - 1, so all three adjacencies are feasible.
        # Counting multiplicity instead would give 6 (every pair doubled).
        self._check(directed=False, exhaustive=True, n=3, m=3, expected=3)

    def test_exhaustive_directed_counts_adjacencies(self):
        # The same on ordered pairs: 6 adjacencies, not 12 arcs.
        self._check(directed=True, exhaustive=True, n=3, m=3, expected=6)

    def test_discovery_undirected_counts_adjacencies(self):
        self._check(directed=False, exhaustive=False, n=3, m=3, expected=3)

    def test_discovery_directed_counts_adjacencies(self):
        self._check(directed=True, exhaustive=False, n=3, m=3, expected=6)

    def test_value_matches_the_simple_variant_it_reduces_to(self):
        # The reduction is the whole claim of sec:parallel-convention: the
        # multigraph vertex question IS the simple vertex question.  Check the
        # two drivers agree rather than just checking a hardcoded number.
        for directed in (False, True):
            for n, m in ((4, 2), (4, 3), (5, 2)):
                multi = solve(n, m, directed=directed, simple=False,
                              separation="vertex", exhaustive=True, max_seconds=60.0)
                plain = solve(n, m, directed=directed, simple=True,
                              separation="vertex", exhaustive=True, max_seconds=60.0)
                self.assertEqual(multi.value, plain.value,
                                 f"directed={directed} n={n} m={m}")

    def test_the_value_never_exceeds_the_adjacencies_available(self):
        # The tell-tale of the old bug.  An adjacency count cannot exceed the
        # number of pairs there are, but a multiplicity count can and did: at
        # n=3, m=3 the driver reported 6 undirected "edges" on 3 vertices, which
        # offer only 3 pairs.  The bound below is trivially true of the right
        # objective and was violated by the wrong one at every m >= 3.
        # Kept to n <= 4: the old objective violated this at EVERY m >= 3 and
        # every n, so a small grid pins it, and the directed exhaustion at n = 5
        # cost more than the rest of this file put together.
        for directed in (False, True):
            for n in (3, 4):
                pairs = n * (n - 1) if directed else n * (n - 1) // 2
                for m in (3, 4, 5):
                    r = solve(n, m, directed=directed, simple=False,
                              separation="vertex", exhaustive=True, max_seconds=60.0)
                    self.assertLessEqual(
                        r.value, pairs,
                        f"directed={directed} n={n} m={m}: reported {r.value} "
                        f"against only {pairs} pairs")


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

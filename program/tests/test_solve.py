"""The single solver: one solve() call handles every kind of question."""

import shutil
import unittest

from erdos915_unified import (
    solve,
    enumerate_extremal_directed_multigraphs as _dfs_enum,
    enumerate_extremal_directed_multigraphs_via_generation as _gen_enum,
    _canonical_form,
)


class Solve(unittest.TestCase):
    def test_exhaustive_simple_directed_is_exact(self):
        r = solve(4, 2, directed=True, simple=True, exhaustive=True, max_seconds=120.0)
        self.assertTrue(r.proven)
        self.assertEqual(r.bound, "exact")
        self.assertEqual(r.value, 6)

    def test_discovery_returns_a_lower_bound(self):
        r = solve(4, 2, directed=True, simple=True, exhaustive=False, max_seconds=3.0)
        self.assertEqual(r.bound, "lower")
        self.assertEqual(r.value, 6)

    def test_exhaustive_undirected_finds_the_spanning_tree(self):
        r = solve(5, 2, directed=False, simple=True, exhaustive=True, max_seconds=30.0)
        self.assertTrue(r.proven)
        self.assertEqual(r.value, 4)  # a spanning tree on 5 vertices

    def test_directed_multigraph_is_proved(self):
        r = solve(4, 3, directed=True, simple=False, exhaustive=True, max_seconds=120.0)
        self.assertTrue(r.proven)
        self.assertEqual(r.value, 12)  # L_3^dir(4) = 2(n-1)(m-1) = 12

    def test_vertex_separation_undirected(self):
        # k_2(n) = n - 1: no cycle is allowed, so a spanning tree is extremal.
        r = solve(5, 2, directed=False, simple=True, separation="vertex",
                  exhaustive=True, max_seconds=30.0)
        self.assertTrue(r.proven)
        self.assertEqual(r.value, 4)

    def test_hypergraph_discovery(self):
        r = solve(7, 2, hypergraph=True, r=3, exhaustive=False, max_seconds=3.0)
        self.assertEqual(r.bound, "lower")
        self.assertEqual(r.value, 3)

    def test_result_describe_is_readable(self):
        r = solve(4, 2, directed=True, simple=True, exhaustive=True, max_seconds=120.0)
        self.assertIn("value", r.describe())


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


if __name__ == "__main__":
    unittest.main()

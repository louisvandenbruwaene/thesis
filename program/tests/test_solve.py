"""The single solver: one solve() call handles every kind of question."""

import unittest

from erdos915_unified import solve


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


if __name__ == "__main__":
    unittest.main()

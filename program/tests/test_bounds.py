"""The closed-form bounds library: every formula, on a range of inputs."""

import unittest

from erdos915_unified import (
    directed_arc_lower_bound,
    directed_arc_m2,
    directed_multigraph_arc,
    hypergraph_edge,
    multigraph_undirected_edge,
    simple_undirected_edge,
    simple_undirected_vertex_le4,
    simple_undirected_vertex_m5,
)


class Bounds(unittest.TestCase):
    def test_simple_undirected_edge(self):
        self.assertEqual(simple_undirected_edge(5, 3), 6)
        for n in range(2, 12):
            for m in range(2, 6):
                self.assertEqual(simple_undirected_edge(n, m), (m * (n - 1)) // 2)

    def test_multigraph_undirected_edge(self):
        for n in range(2, 12):
            for m in range(2, 6):
                self.assertEqual(multigraph_undirected_edge(n, m), (m - 1) * (n - 1))

    def test_vertex_le4_matches_edge_and_caps_at_four(self):
        for m in range(2, 5):
            self.assertEqual(simple_undirected_vertex_le4(10, m), simple_undirected_edge(10, m))
        with self.assertRaises(ValueError):
            simple_undirected_vertex_le4(10, 5)

    def test_vertex_m5(self):
        for n in range(6, 20):
            self.assertEqual(simple_undirected_vertex_m5(n), (8 * n) // 3 - 3)

    def test_directed_arc_m2_branches_and_crossover(self):
        self.assertEqual(directed_arc_m2(4), 6)   # linear hub branch wins
        self.assertEqual(directed_arc_m2(7), 12)  # the two branches meet
        self.assertEqual(directed_arc_m2(8), 16)  # quadratic branch wins
        for n in range(2, 20):
            self.assertEqual(directed_arc_m2(n), max(2 * (n - 1), (n * n) // 4))

    def test_directed_arc_lower_bound(self):
        self.assertEqual(directed_arc_lower_bound(10, 3), 30)  # the 30-arc graph
        self.assertEqual(directed_arc_lower_bound(4, 2), 6)
        for n in range(3, 14):
            for m in range(2, 5):
                expected = max(m * (n - 1), (n + m - 2) ** 2 // 4)
                self.assertEqual(directed_arc_lower_bound(n, m), expected)

    def test_hypergraph_edge(self):
        self.assertEqual(hypergraph_edge(7, 2, 3), 3)
        self.assertEqual(hypergraph_edge(13, 2, 4), 4)
        for n in range(3, 14):
            for m in range(2, 5):
                for r in range(2, 5):
                    self.assertEqual(hypergraph_edge(n, m, r), ((m - 1) * (n - 1)) // (r - 1))

    def test_directed_multigraph_arc(self):
        self.assertEqual(directed_multigraph_arc(4, 3), 12)
        self.assertEqual(directed_multigraph_arc(6, 2), 10)
        for n in range(2, 12):
            for m in range(2, 6):
                expected = max(2 * (n - 1) * (m - 1), (m - 1) * ((n * n) // 4))
                self.assertEqual(directed_multigraph_arc(n, m), expected)


if __name__ == "__main__":
    unittest.main()

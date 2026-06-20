"""The named extremal constructions: their exact sizes and connectivities."""

import unittest

from erdos915_unified import (
    augmented_bipartite,
    clique_tree,
    double_star,
    max_edge_connectivity,
    min_vertex_connectivity,
    one_directional_bipartite,
)


class Constructions(unittest.TestCase):
    def test_double_star_directed(self):
        for n in range(2, 7):
            for m in range(2, 5):
                g = double_star(n, m, directed=True)
                self.assertEqual(g.edge_count(), 2 * (n - 1) * (m - 1))
                self.assertEqual(max_edge_connectivity(g), m - 1)

    def test_double_star_undirected(self):
        for n in range(2, 7):
            for m in range(2, 5):
                g = double_star(n, m, directed=False)
                self.assertEqual(g.edge_count(), (m - 1) * (n - 1))
                self.assertEqual(max_edge_connectivity(g), m - 1)

    def test_one_directional_bipartite_is_quadratic_and_feasible(self):
        for n in range(2, 8):
            g = one_directional_bipartite(n)
            self.assertEqual(g.edge_count(), (n * n) // 4)
            self.assertEqual(max_edge_connectivity(g), 1)

    def test_augmented_bipartite_conjecture_values(self):
        self.assertEqual(augmented_bipartite(10, 3).edge_count(), 30)
        for n, m in [(8, 3), (10, 4), (12, 4), (10, 5)]:
            g = augmented_bipartite(n, m)
            self.assertEqual(g.edge_count(), (n + m - 2) ** 2 // 4)
            self.assertEqual(max_edge_connectivity(g), m - 1)

    def test_augmented_bipartite_guards_its_precondition(self):
        with self.assertRaises(ValueError):
            augmented_bipartite(3, 5)  # needs n >= m

    def test_clique_tree_is_globally_connected(self):
        for blocks in range(0, 5):
            self.assertEqual(min_vertex_connectivity(clique_tree(4, blocks)), 3)


if __name__ == "__main__":
    unittest.main()

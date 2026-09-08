"""The named extremal constructions: their exact sizes and connectivities."""

import unittest
from itertools import combinations

from erdos915_unified import (
    augmented_bipartite,
    clique_core,
    clique_tree,
    double_star,
    max_edge_connectivity,
    min_vertex_connectivity,
    one_directional_bipartite,
    six_vertex_multihypergraph,
    max_hyperedge_connectivity,
    max_hyper_connectivity,
    bounded_outdegree_hypergraph,
)


class Constructions(unittest.TestCase):
    def test_bounded_outdegree_forward_hypergraphs(self):
        for n, m in ((3, 3), (4, 6), (6, 6)):
            for simple in (True, False):
                graph = bounded_outdegree_hypergraph(n, m, simple=simple)
                out = min(m - 1, (n - 1) * (n - 2) // 2) if simple else m - 1
                self.assertEqual(graph.edge_count(), n * out)
                if simple:
                    self.assertEqual(len(set(graph.hyperedges)), graph.edge_count())
                for vertex in (False, True):
                    self.assertLessEqual(max_hyper_connectivity(graph, vertex_split=vertex), m - 1)

    def test_twelve_hyperedges_on_six_vertices(self):
        graph = six_vertex_multihypergraph()
        edges = graph.hyperedges
        self.assertEqual(len(edges), 12)
        self.assertEqual([sum(v in edge for edge in edges) for v in range(6)], [11, 5, 5, 5, 5, 5])
        self.assertEqual(max_hyperedge_connectivity(graph), 5)
        # Independent exhaustive cut calculation, without the flow helper.
        cuts = []
        for mask in range(1, 63):
            side = {v for v in range(6) if mask & (1 << v)}
            value = sum(bool(edge & side) and bool(edge - side) for edge in edges)
            cuts.append((side, value))
        self.assertEqual(max(min(value for side, value in cuts if (u in side) != (v in side))
                             for u, v in combinations(range(6), 2)), 5)
        from make_figures import gather_variant_grid, _panel_cell
        panel = gather_variant_grid(6)[12]
        self.assertEqual(dict(zip(*panel["construction"]))[6], 12)
        self.assertEqual(_panel_cell(panel, 6), ("12", "vtProved", False))

    def test_clique_core_count_and_feasibility(self):
        for m in range(2, 7):
            for n in range(m, 3 * m):
                graph = clique_core(n, m)
                self.assertEqual(graph.edge_count(), (n + m - 3) ** 2 // 4 + 2 * (m - 1))
                self.assertEqual(max_edge_connectivity(graph), m - 1)
        self.assertEqual(clique_core(12, 5).edge_count(), 57)

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

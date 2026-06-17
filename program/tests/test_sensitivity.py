"""Edge sensitivity: the load-bearing measure that guides the search."""

import random
import unittest

from erdos915_unified import (
    Graph,
    MULTI_DIRECTED,
    MULTI_UNDIRECTED,
    SIMPLE_DIRECTED,
    SIMPLE_UNDIRECTED,
    double_star,
    edge_sensitivity,
    max_edge_connectivity,
    max_vertex_connectivity,
    one_directional_bipartite,
    sensitivity_map,
)


def _random_graph(variant, n, rng, top):
    g = Graph(n, variant)
    cap = 1 if variant.simple else top
    for u in range(n):
        start = 0 if variant.directed else u + 1
        for v in range(start, n):
            if u != v:
                g.set_multiplicity(u, v, rng.randint(0, cap))
    return g


class Sensitivity(unittest.TestCase):
    def test_absent_edge_has_zero_sensitivity(self):
        g = Graph(3, SIMPLE_UNDIRECTED)
        self.assertEqual(edge_sensitivity(g, 0, 1), 0)

    def test_sensitivity_matches_its_definition(self):
        g = one_directional_bipartite(6)
        before = max_edge_connectivity(g)
        for (u, v), sigma in sensitivity_map(g).items():
            reduced = g.copy()
            reduced.set_multiplicity(u, v, 0)
            self.assertEqual(sigma, before - max_edge_connectivity(reduced))
            self.assertGreaterEqual(sigma, 0)  # removing an edge never raises lambda

    def test_map_covers_exactly_the_present_edges(self):
        g = double_star(5, 3, directed=True)
        self.assertEqual(len(sensitivity_map(g)), sum(1 for _ in g.edges()))

    def test_map_equals_per_edge_sensitivity(self):
        # The before-once refactor must return the IDENTICAL dict as the old
        # per-edge definition, across variants and both connectivity measures.
        variants = (SIMPLE_UNDIRECTED, MULTI_UNDIRECTED,
                    SIMPLE_DIRECTED, MULTI_DIRECTED)
        rng = random.Random(99)
        for variant in variants:
            for measure in (max_edge_connectivity, max_vertex_connectivity):
                for _ in range(6):
                    g = _random_graph(variant, 5, rng, top=2)
                    expected = {(u, v): edge_sensitivity(g, u, v, measure)
                                for u, v, _ in g.edges()}
                    self.assertEqual(sensitivity_map(g, measure), expected)


if __name__ == "__main__":
    unittest.main()

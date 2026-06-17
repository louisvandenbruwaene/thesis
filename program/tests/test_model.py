"""The graph model: the multiplicity matrix and every operation on it."""

import unittest

from erdos915_unified import (
    Graph,
    MULTI_DIRECTED,
    MULTI_UNDIRECTED,
    SIMPLE_DIRECTED,
    SIMPLE_UNDIRECTED,
)


class VariantBooleans(unittest.TestCase):
    def test_the_two_booleans(self):
        self.assertEqual((SIMPLE_UNDIRECTED.directed, SIMPLE_UNDIRECTED.simple), (False, True))
        self.assertEqual((MULTI_UNDIRECTED.directed, MULTI_UNDIRECTED.simple), (False, False))
        self.assertEqual((SIMPLE_DIRECTED.directed, SIMPLE_DIRECTED.simple), (True, True))
        self.assertEqual((MULTI_DIRECTED.directed, MULTI_DIRECTED.simple), (True, False))

    def test_describe_is_nonempty(self):
        for variant in (SIMPLE_UNDIRECTED, MULTI_UNDIRECTED, SIMPLE_DIRECTED, MULTI_DIRECTED):
            self.assertTrue(variant.describe())


class EmptyGraph(unittest.TestCase):
    def test_fresh_graph_is_empty(self):
        g = Graph(5, SIMPLE_UNDIRECTED)
        self.assertEqual(g.num_vertices, 5)
        self.assertEqual(list(g.vertices()), list(range(5)))
        self.assertEqual(g.edge_count(), 0)
        self.assertEqual(list(g.edges()), [])
        self.assertFalse(g.has_edge(0, 1))


class UndirectedModel(unittest.TestCase):
    def test_add_edge_is_symmetric(self):
        g = Graph(3, SIMPLE_UNDIRECTED)
        g.add_edge(0, 1)
        self.assertTrue(g.has_edge(0, 1))
        self.assertTrue(g.has_edge(1, 0))
        self.assertEqual(g.multiplicity(0, 1), 1)
        self.assertEqual(g.multiplicity(1, 0), 1)
        self.assertEqual(g.edge_count(), 1)
        self.assertEqual(list(g.edges()), [(0, 1, 1)])

    def test_simple_graph_saturates_at_one(self):
        g = Graph(3, SIMPLE_UNDIRECTED)
        g.add_edge(0, 1)
        g.add_edge(0, 1)
        self.assertEqual(g.multiplicity(0, 1), 1)
        self.assertEqual(g.edge_count(), 1)

    def test_multigraph_keeps_parallel_edges(self):
        g = Graph(3, MULTI_UNDIRECTED)
        g.add_edge(0, 1, 3)
        self.assertEqual(g.multiplicity(0, 1), 3)
        self.assertEqual(g.multiplicity(1, 0), 3)
        self.assertEqual(g.edge_count(), 3)
        self.assertEqual(g.degree(0), 3)
        self.assertEqual(g.degree(1), 3)

    def test_undirected_degree_counts_incident_multiplicity(self):
        g = Graph(3, MULTI_UNDIRECTED)
        g.add_edge(0, 1, 2)
        g.add_edge(0, 2, 1)
        self.assertEqual(g.degree(0), 3)
        self.assertEqual(g.edge_count(), 3)


class DirectedModel(unittest.TestCase):
    def test_arc_is_one_directional(self):
        g = Graph(3, SIMPLE_DIRECTED)
        g.add_edge(0, 1)
        self.assertTrue(g.has_edge(0, 1))
        self.assertFalse(g.has_edge(1, 0))
        self.assertEqual(g.edge_count(), 1)
        self.assertEqual(g.out_degree(0), 1)
        self.assertEqual(g.in_degree(1), 1)
        self.assertEqual(g.in_degree(0), 0)
        self.assertEqual(g.degree(0), 1)
        self.assertEqual(g.degree(1), 1)

    def test_directed_multiplicities_are_independent(self):
        g = Graph(3, MULTI_DIRECTED)
        g.add_edge(0, 1, 2)
        g.add_edge(1, 0, 1)
        self.assertEqual(g.multiplicity(0, 1), 2)
        self.assertEqual(g.multiplicity(1, 0), 1)
        self.assertEqual(g.edge_count(), 3)
        self.assertEqual(g.out_degree(0), 2)
        self.assertEqual(g.in_degree(0), 1)
        self.assertEqual(g.degree(0), 3)

    def test_edges_yields_both_arc_directions(self):
        g = Graph(3, SIMPLE_DIRECTED)
        g.add_edge(0, 1)
        g.add_edge(1, 0)
        self.assertEqual(sorted(g.edges()), [(0, 1, 1), (1, 0, 1)])


class Mutation(unittest.TestCase):
    def test_remove_never_goes_below_zero(self):
        g = Graph(3, MULTI_UNDIRECTED)
        g.add_edge(0, 1, 3)
        g.remove_edge(0, 1, 5)
        self.assertEqual(g.multiplicity(0, 1), 0)
        self.assertFalse(g.has_edge(0, 1))

    def test_set_multiplicity_directly(self):
        g = Graph(3, MULTI_DIRECTED)
        g.set_multiplicity(0, 1, 4)
        self.assertEqual(g.multiplicity(0, 1), 4)
        self.assertEqual(g.multiplicity(1, 0), 0)

    def test_simple_rejects_multiplicity_above_one(self):
        g = Graph(3, SIMPLE_UNDIRECTED)
        with self.assertRaises(ValueError):
            g.set_multiplicity(0, 1, 2)

    def test_negative_multiplicity_rejected(self):
        g = Graph(3, MULTI_UNDIRECTED)
        with self.assertRaises(ValueError):
            g.set_multiplicity(0, 1, -1)

    def test_self_loops_rejected(self):
        g = Graph(3, MULTI_UNDIRECTED)
        with self.assertRaises(ValueError):
            g.add_edge(1, 1)

    def test_copy_is_independent(self):
        g = Graph(3, MULTI_UNDIRECTED)
        g.add_edge(0, 1, 2)
        clone = g.copy()
        clone.add_edge(0, 2, 1)
        self.assertEqual(g.edge_count(), 2)
        self.assertEqual(clone.edge_count(), 3)


if __name__ == "__main__":
    unittest.main()

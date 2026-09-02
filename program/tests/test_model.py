"""The graph model: the multiplicity matrix and every operation on it."""

import unittest
from unittest.mock import patch

from erdos915_unified import (
    Graph,
    MULTI_DIRECTED,
    MULTI_UNDIRECTED,
    SIMPLE_DIRECTED,
    SIMPLE_UNDIRECTED,
    local_connectivity,
    thickened_one_directional_bipartite,
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


class Endpoints(unittest.TestCase):
    """A connectivity call names two distinct vertices, or it is not a question."""

    def setUp(self):
        self.g = Graph(3, MULTI_UNDIRECTED)
        self.g.add_edge(0, 1)

    def test_equal_endpoints_are_refused_in_both_separations(self):
        for vertex_split in (False, True):
            with self.subTest(vertex_split=vertex_split):
                with self.assertRaises(ValueError):
                    local_connectivity(self.g, 0, 0, vertex_split=vertex_split)

    def test_an_index_outside_the_graph_is_refused(self):
        for source, target in [(-1, 0), (0, -1), (3, 0), (0, 3)]:
            with self.subTest(pair=(source, target)):
                with self.assertRaises(IndexError):
                    local_connectivity(self.g, source, target)

    def test_a_real_pair_still_answers(self):
        self.assertEqual(local_connectivity(self.g, 0, 1), 1)


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

    def test_negative_add_and_remove_counts_rejected(self):
        for variant in (SIMPLE_UNDIRECTED, MULTI_UNDIRECTED):
            with self.subTest(variant=variant.name, operation="add"):
                with self.assertRaises(ValueError):
                    Graph(3, variant).add_edge(0, 1, -1)
            with self.subTest(variant=variant.name, operation="remove"):
                with self.assertRaises(ValueError):
                    Graph(3, variant).remove_edge(0, 1, -1)

    def test_thickened_wall_uses_guarded_mutation(self):
        calls = []
        original = Graph.set_multiplicity

        def tracked(graph, u, v, value):
            calls.append((u, v, value))
            return original(graph, u, v, value)

        with patch.object(Graph, "set_multiplicity", new=tracked):
            wall = thickened_one_directional_bipartite(6, 3)
        self.assertGreater(len(calls), 0)
        self.assertEqual(wall.edge_count(), 18)

    def test_thickened_wall_rejects_invalid_m(self):
        with self.assertRaises(ValueError):
            thickened_one_directional_bipartite(6, 1)

    def test_self_loops_rejected(self):
        g = Graph(3, MULTI_UNDIRECTED)
        with self.assertRaises(ValueError):
            g.add_edge(1, 1)

    def test_vertex_indices_do_not_wrap_through_numpy(self):
        g = Graph(3, MULTI_UNDIRECTED)
        for u, v in [(-1, 0), (0, -1), (3, 0), (0, 3)]:
            with self.subTest(pair=(u, v)):
                with self.assertRaises(IndexError):
                    g.add_edge(u, v)
        self.assertEqual(g.edge_count(), 0)

    def test_a_fractional_count_is_rejected_before_it_is_laundered(self):
        """The trap: a simple graph saturates at one, so min(mu + 1.9, 1) is 1.

        The bad input is a clean integer by the time it reaches the matrix, so a
        guard on the assignment alone cannot see it. Both counts are therefore
        checked before the arithmetic that normalises them.
        """
        for variant in (SIMPLE_UNDIRECTED, MULTI_UNDIRECTED):
            with self.subTest(variant=variant.name):
                with self.assertRaises(TypeError):
                    Graph(3, variant).add_edge(0, 1, 1.9)
                with self.assertRaises(TypeError):
                    Graph(3, variant).remove_edge(0, 1, 1.9)
                self.assertEqual(Graph(3, variant).edge_count(), 0)

    def test_booleans_are_not_accepted_as_numbers(self):
        """``True`` is an ``int`` in Python, so it passes every naive check."""
        g = Graph(3, MULTI_UNDIRECTED)
        with self.assertRaises(TypeError):
            g.add_edge(0, 1, True)
        with self.assertRaises(TypeError):
            g.set_multiplicity(0, 1, True)
        with self.assertRaises(TypeError):
            g.add_edge(True, 0)
        with self.assertRaises(TypeError):
            Graph(True, MULTI_UNDIRECTED)
        self.assertEqual(g.edge_count(), 0)

    def test_a_non_integer_multiplicity_is_rejected(self):
        with self.assertRaises(TypeError):
            Graph(3, MULTI_UNDIRECTED).set_multiplicity(0, 1, 2.5)

    def test_copy_is_independent(self):
        g = Graph(3, MULTI_UNDIRECTED)
        g.add_edge(0, 1, 2)
        clone = g.copy()
        clone.add_edge(0, 2, 1)
        self.assertEqual(g.edge_count(), 2)
        self.assertEqual(clone.edge_count(), 3)


if __name__ == "__main__":
    unittest.main()

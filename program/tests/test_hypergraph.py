"""The hypergraph model and Berge connectivity by the helper-point network."""

import unittest

from erdos915_unified import (
    Hypergraph,
    complete_uniform_hypergraph,
    hyperedge_connectivity,
    max_hyperedge_connectivity,
    star_hypertree,
)


class BergeConnectivity(unittest.TestCase):
    def test_single_hyperedge_carries_one_route(self):
        h = Hypergraph(3, [[0, 1, 2]])
        self.assertEqual(h.edge_count(), 1)
        self.assertEqual(hyperedge_connectivity(h, 0, 1), 1)
        self.assertEqual(hyperedge_connectivity(h, 0, 2), 1)
        self.assertEqual(hyperedge_connectivity(h, 1, 2), 1)

    def test_two_hyperedges_give_two_routes(self):
        h = Hypergraph(4, [[0, 1, 2], [0, 1, 3]])
        self.assertEqual(h.edge_count(), 2)
        self.assertEqual(hyperedge_connectivity(h, 0, 1), 2)
        self.assertEqual(len(h.incident_hyperedges(0)), 2)
        self.assertEqual(len(h.incident_hyperedges(2)), 1)

    def test_complete_three_uniform_k4(self):
        self.assertEqual(max_hyperedge_connectivity(complete_uniform_hypergraph(4, 3)), 3)

    def test_two_uniform_reduces_to_edge_connectivity(self):
        for n in (3, 4, 5):
            self.assertEqual(max_hyperedge_connectivity(complete_uniform_hypergraph(n, 2)), n - 1)

    def test_star_hypertree(self):
        for n, r in [(7, 3), (10, 4), (13, 4)]:
            h = star_hypertree(n, r)
            self.assertEqual(h.edge_count(), (n - 1) // (r - 1))
            self.assertEqual(max_hyperedge_connectivity(h), 1)

    def test_bad_hyperedge_size_rejected(self):
        with self.assertRaises(ValueError):
            star_hypertree(7, 1)


if __name__ == "__main__":
    unittest.main()

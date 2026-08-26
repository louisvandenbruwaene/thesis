"""The hypergraph model and Berge connectivity by the helper-point network."""

import unittest

from erdos915_unified import (
    Hypergraph,
    complete_uniform_hypergraph,
    hyper_connectivity,
    hyperedge_connectivity,
    max_feasible_hyperedges,
    max_hyperedge_connectivity,
    star_hypertree,
    _hyperedge_candidates,
    _hyper_canonical,
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


class DirectedOrientationModels(unittest.TestCase):
    """Forward / backward / general directed hyperedge models."""

    def test_general_gate_is_one_way(self):
        # A mixed arc {0,1} -> {2,3}: a route enters at a tail, leaves at a head.
        h = Hypergraph(4, [(frozenset({0, 1}), frozenset({2, 3}))], directed=True)
        self.assertEqual(sorted(h.members(h.hyperedges[0])), [0, 1, 2, 3])
        self.assertEqual(hyper_connectivity(h, 0, 2), 1)   # tail -> head
        self.assertEqual(hyper_connectivity(h, 2, 0), 0)   # head -> tail: none

    def test_forward_legacy_equals_general_form(self):
        legacy = Hypergraph(3, [(0, frozenset({1, 2}))], directed=True)
        general = Hypergraph(3, [(frozenset({0}), frozenset({1, 2}))], directed=True)
        for s, t in [(0, 1), (0, 2), (1, 2)]:
            self.assertEqual(hyper_connectivity(legacy, s, t),
                             hyper_connectivity(general, s, t))

    def test_canonical_form_accepts_mixed_storage_forms(self):
        legacy = (0, frozenset({1, 2}))
        general = (frozenset({0}), frozenset({1, 2}))
        self.assertEqual(_hyper_canonical([legacy], 3, True),
                         _hyper_canonical([general], 3, True))
        mixed = _hyper_canonical([legacy, general], 3, True)
        self.assertEqual(len(mixed), 2)
        self.assertEqual(mixed[0], mixed[1])

    def test_candidate_counts_split_at_r3(self):
        # At r = 3 every split has a singleton side, so general = forward + backward.
        fwd = _hyperedge_candidates(4, 3, True, kind="forward")
        bwd = _hyperedge_candidates(4, 3, True, kind="backward")
        gen = _hyperedge_candidates(4, 3, True, kind="general")
        self.assertEqual(len(fwd), 12)
        self.assertEqual(len(bwd), 12)
        self.assertEqual(len(gen), 24)

    def test_forward_backward_duality(self):
        # Arc reversal makes backward the dual of forward: same extremal numbers.
        for n, m in [(3, 3), (4, 3), (4, 2)]:
            f, _ = max_feasible_hyperedges(n, 3, m, directed=True, kind="forward", time_limit=2.0)
            b, _ = max_feasible_hyperedges(n, 3, m, directed=True, kind="backward", time_limit=2.0)
            self.assertEqual(f, b)

    def test_general_beats_forward_when_vertices_scarce(self):
        # n = r is the regime where the richer orientation set packs more arcs.
        g3, e3 = max_feasible_hyperedges(3, 3, 3, directed=True, kind="general", time_limit=2.0)
        f3, _ = max_feasible_hyperedges(3, 3, 3, directed=True, kind="forward", time_limit=2.0)
        self.assertTrue(e3)
        self.assertEqual((g3, f3), (4, 3))

    def test_general_contains_forward(self):
        # General can never be worse than forward (forward hypergraphs are general).
        for n, m in [(4, 3), (5, 2)]:
            f, _ = max_feasible_hyperedges(n, 3, m, directed=True, kind="forward", time_limit=2.0)
            g, _ = max_feasible_hyperedges(n, 3, m, directed=True, kind="general",
                                           time_limit=3.0, seed_lb=f)
            self.assertGreaterEqual(g, f)

    def test_unverified_seed_cannot_be_reported_as_exact(self):
        with self.assertRaisesRegex(ValueError, "claimed feasible"):
            max_feasible_hyperedges(
                4, 3, 2, directed=True, kind="forward",
                time_limit=10.0, seed_lb=5,
            )


if __name__ == "__main__":
    unittest.main()

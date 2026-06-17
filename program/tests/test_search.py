"""The temperature search: it rediscovers the known small extremal values.

The search is seeded, so these outcomes are deterministic and reproducible.
"""

import unittest

from erdos915_unified import (
    MULTI_DIRECTED,
    MULTI_UNDIRECTED,
    SIMPLE_DIRECTED,
    SIMPLE_UNDIRECTED,
    best_of_searches,
    max_connectivity,
    max_edge_connectivity,
    search_for_dense_graph,
)


class Search(unittest.TestCase):
    def test_search_rediscovers_directed_m2(self):
        result = search_for_dense_graph(SIMPLE_DIRECTED, n=4, m=2, steps=6000, seed=0)
        self.assertEqual(result.best_edge_count, 6)  # ell_2^dir(4) = 6
        self.assertTrue(result.feasible_found)
        self.assertLessEqual(max_edge_connectivity(result.best_graph), 1)

    def test_acceptance_rate_is_a_fraction(self):
        result = search_for_dense_graph(SIMPLE_DIRECTED, n=4, m=2, steps=6000, seed=0)
        self.assertTrue(0.0 <= result.acceptance_rate() <= 1.0)
        self.assertEqual(len(result.history), 6000)

    def test_search_rediscovers_undirected_m3(self):
        # ell_3(n) = floor(3(n-1)/2): n=4 -> 4, n=5 -> 6.
        for n, expected in [(4, 4), (5, 6)]:
            result = best_of_searches(SIMPLE_UNDIRECTED, n, 3, restarts=6, steps=3000, seed=0)
            self.assertEqual(result.best_edge_count, expected)
            self.assertLessEqual(max_edge_connectivity(result.best_graph), 2)


class FastPathEquivalence(unittest.TestCase):
    """The fast (capped + monotone) search must reproduce the slow exact search
    step for step.  This is the "nothing under the rug" guarantee: the speedup
    changes no reported value because it changes no single step of the walk.
    """

    def test_fast_path_matches_exact(self):
        variants = (SIMPLE_UNDIRECTED, MULTI_UNDIRECTED,
                    SIMPLE_DIRECTED, MULTI_DIRECTED)
        for variant in variants:
            for n in (3, 4, 5):
                for m in (2, 3):
                    for sep in ("edge", "vertex"):
                        for seed in range(2):
                            opts = dict(separation=sep, steps=300, seed=seed)
                            ref = search_for_dense_graph(
                                variant, n, m, reference_mode=True, **opts)
                            fast = search_for_dense_graph(variant, n, m, **opts)
                            tag = (f"{variant.name} n={n} m={m} sep={sep} "
                                   f"seed={seed}")
                            # Bit-for-bit: same energies, same accept/reject
                            # decisions, same density at every step.
                            self.assertEqual(
                                [s.energy for s in fast.history],
                                [s.energy for s in ref.history], tag)
                            self.assertEqual(
                                [s.accepted for s in fast.history],
                                [s.accepted for s in ref.history], tag)
                            self.assertEqual(
                                [s.edge_count for s in fast.history],
                                [s.edge_count for s in ref.history], tag)
                            self.assertEqual(
                                fast.best_edge_count, ref.best_edge_count, tag)
                            self.assertTrue(
                                (fast.best_graph.mu == ref.best_graph.mu).all(),
                                tag)
                            # The returned witness is genuinely feasible by the
                            # exact checker (certified, not just flagged).
                            split = sep == "vertex"
                            self.assertLessEqual(
                                max_connectivity(fast.best_graph,
                                                 vertex_split=split),
                                m - 1, tag)


if __name__ == "__main__":
    unittest.main()

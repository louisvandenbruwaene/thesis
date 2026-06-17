"""The random model: the appearance threshold and the Whitney relation.

All sampling is seeded, so these outcomes are deterministic.
"""

import unittest

from erdos915_unified import (
    connectivity_distribution,
    edge_vertex_distribution,
    estimate_appearance_probability,
    threshold_curve,
)


class MonteCarlo(unittest.TestCase):
    def test_appearance_probability_crosses_m_over_n(self):
        n, m = 30, 3
        below = estimate_appearance_probability(n, 0.3 * m / n, m, trials=120, seed=1)
        above = estimate_appearance_probability(n, 1.8 * m / n, m, trials=120, seed=1)
        self.assertLess(below, 0.5)
        self.assertGreater(above, 0.5)

    def test_whitney_holds_on_every_sample(self):
        edge = connectivity_distribution(20, 0.25, trials=40, separation="edge", seed=3)
        vertex = connectivity_distribution(20, 0.25, trials=40, separation="vertex", seed=3)
        self.assertEqual(len(edge), 40)
        for kappa, lam in zip(vertex, edge):
            self.assertLessEqual(kappa, lam)

    def test_edge_and_vertex_agree_at_small_n(self):
        lam, kap = edge_vertex_distribution(5, 0.5, trials=120, seed=7)
        self.assertEqual(sum(k < l for k, l in zip(kap, lam)), 0)  # no gap at n = 5
        self.assertTrue(all(k <= l for k, l in zip(kap, lam)))  # Whitney

    def test_edge_and_vertex_part_company_at_larger_n(self):
        lam, kap = edge_vertex_distribution(16, 0.25, trials=200, seed=7)
        gap = sum(k < l for k, l in zip(kap, lam))
        self.assertGreater(gap, 0)
        self.assertTrue(all(k <= l for k, l in zip(kap, lam)))

    def test_threshold_curve_reports_the_predicted_threshold(self):
        curve = threshold_curve(20, 2, [0.05, 0.2], trials=20, seed=0)
        self.assertAlmostEqual(curve.predicted_threshold, 2 / 20)
        self.assertEqual(len(curve.probabilities), 2)


if __name__ == "__main__":
    unittest.main()

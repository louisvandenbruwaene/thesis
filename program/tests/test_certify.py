"""The cut-counting prover: a zero-gap solve is a genuine upper-bound proof."""

import os
import unittest

import numpy as np

from erdos915_unified import (
    MULTI_DIRECTED,
    PULP_AVAILABLE,
    Graph,
    _canonical_form,
    enumerate_extremal_directed_multigraphs,
    max_edge_connectivity,
    prove_directed_multigraph,
)


@unittest.skipUnless(PULP_AVAILABLE, "the MILP certifier needs the optional pulp")
class Prover(unittest.TestCase):
    def test_small_optima_are_proved(self):
        # M*(n) = 2(n-1), optimal with zero gap, for the reachable sizes.
        for n in (3, 4, 5):
            result = prove_directed_multigraph(n, time_limit=120.0)
            self.assertTrue(result.is_proof())
            self.assertEqual(result.status, "OPTIMAL")
            self.assertEqual(round(result.scaled_optimum), 2 * (n - 1))

    def test_one_solve_settles_every_m(self):
        result = prove_directed_multigraph(4, time_limit=120.0)
        self.assertTrue(result.is_proof())
        for m in (2, 3, 4, 5):
            # L_m^dir(4) = (m-1) * M*(4) = (m-1) * 6.
            self.assertEqual(result.value_for(m), (m - 1) * 2 * (4 - 1))


class EnumerationDedup(unittest.TestCase):
    """The streamed canonical-form dedup keeps one representative per iso-class
    and returns exactly the known small extremal sets.

    The active path stays at n in {3, 4} (sub-second).  The n=5 enumeration is
    minutes long (the DFS, not the dedup), so its known count is checked only when
    ``RUN_SLOW_ENUM`` is set; the dedup logic it exercises is identical to n=4.
    """

    # m=3 directed multigraph, target = 4(n-1) arcs: the doubled bidirected
    # spanning trees.  Known counts (claude.md): n=3 -> 1 (path), n=4 -> 2
    # (star, path), n=5 -> 3 (star, broom, path).
    FAST_COUNTS = {3: 1, 4: 2}

    def test_known_iso_class_counts(self):
        for n, expected in self.FAST_COUNTS.items():
            reps = enumerate_extremal_directed_multigraphs(n, 3, 4 * (n - 1))
            self.assertEqual(len(reps), expected, f"n={n}")

    def test_representatives_are_distinct_and_feasible(self):
        for n in self.FAST_COUNTS:
            reps = enumerate_extremal_directed_multigraphs(n, 3, 4 * (n - 1))
            keys = [_canonical_form(mu) for mu in reps]
            # One representative per class: all canonical keys distinct.
            self.assertEqual(len(set(keys)), len(keys), f"n={n}")
            for mu in reps:
                g = Graph(n, MULTI_DIRECTED)
                g.mu = mu.copy()
                self.assertEqual(g.edge_count(), 4 * (n - 1))
                self.assertLessEqual(max_edge_connectivity(g), 2, f"n={n}")

    def test_dedup_preserves_the_iso_classes(self):
        # The deduped run must cover exactly the iso-classes of the full labelled
        # run: no class invented, none dropped.
        for n in self.FAST_COUNTS:
            labelled = enumerate_extremal_directed_multigraphs(
                n, 3, 4 * (n - 1), up_to_iso=False)
            deduped = enumerate_extremal_directed_multigraphs(n, 3, 4 * (n - 1))
            self.assertEqual(
                {_canonical_form(mu) for mu in labelled},
                {_canonical_form(mu) for mu in deduped},
                f"n={n}")
            # Every labelled matrix is itself one of the kept iso-classes.
            kept = {_canonical_form(mu) for mu in deduped}
            for mu in labelled:
                self.assertIn(_canonical_form(mu), kept, f"n={n}")

    def test_canonical_form_is_permutation_invariant(self):
        rng = np.random.default_rng(0)
        for n in (3, 4, 5, 6):
            mu = rng.integers(0, 3, size=(n, n))
            np.fill_diagonal(mu, 0)
            key = _canonical_form(mu)
            for _ in range(5):
                p = rng.permutation(n)
                self.assertEqual(_canonical_form(mu[np.ix_(p, p)]), key, f"n={n}")

    @unittest.skipUnless(os.environ.get("RUN_SLOW_ENUM"),
                         "n=5 enumeration is minutes long; set RUN_SLOW_ENUM=1")
    def test_n5_known_count(self):
        reps = enumerate_extremal_directed_multigraphs(5, 3, 16)
        self.assertEqual(len(reps), 3)  # star, broom, path


if __name__ == "__main__":
    unittest.main()

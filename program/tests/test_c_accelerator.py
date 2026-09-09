"""The optional C helper agrees with the pure-Python routines it replaces.

Chapter 2 states that the helper changes how long a search runs and never what
it reports. That claim is only as good as a comparison, so each of the three
routines is run both ways on the same random inputs. Without a built
``_erdos_fast.so`` there is nothing to compare and the cases skip.
"""

import unittest
from unittest.mock import patch

import numpy as np
import erdos915_unified as e

from erdos915_unified import (
    MULTI_DIRECTED,
    SIMPLE_UNDIRECTED,
    C_EXTENSION_LOADED,
    Graph,
    _canonical_form,
    _tiny_maxflow,
    exceeds_bound,
)


def _random_graph(rng, n, variant, m):
    graph = Graph(n, variant)
    for u in range(n):
        for v in range(n):
            if u != v:
                graph.set_multiplicity(u, v, int(rng.integers(0, m)))
    return graph


@unittest.skipUnless(C_EXTENSION_LOADED, "needs a built _erdos_fast.so")
class Accelerator(unittest.TestCase):
    def test_capped_max_flow_agrees(self):
        rng = np.random.default_rng(11)
        for _ in range(300):
            n = int(rng.integers(2, 8))
            mu = np.ascontiguousarray(rng.integers(0, 4, size=(n, n)), dtype=np.int32)
            np.fill_diagonal(mu, 0)
            s, t = 0, n - 1
            cap = int(rng.integers(0, 5))
            fast = _tiny_maxflow(mu, n, s, t, cap)
            with patch.object(e, "_C", None):
                self.assertEqual(fast, _tiny_maxflow(mu, n, s, t, cap))

    def test_pairwise_predicate_agrees(self):
        rng = np.random.default_rng(12)
        for variant in (SIMPLE_UNDIRECTED, MULTI_DIRECTED):
            for _ in range(120):
                n = int(rng.integers(2, 8))
                m = 2 if variant.simple else 4
                graph = _random_graph(rng, n, variant, m)
                k = int(rng.integers(0, 4))
                fast = exceeds_bound(graph, k)
                with patch.object(e, "_C", None):
                    self.assertEqual(fast, exceeds_bound(graph, k), f"n={n} k={k}")

    def test_canonical_form_agrees(self):
        rng = np.random.default_rng(13)
        for _ in range(200):
            n = int(rng.integers(1, 8))
            mu = np.ascontiguousarray(rng.integers(0, 3, size=(n, n)), dtype=np.int32)
            np.fill_diagonal(mu, 0)
            fast = _canonical_form(mu)
            with patch.object(e, "_C", None):
                self.assertEqual(fast, _canonical_form(mu))

    def test_wide_entries_take_the_python_path(self):
        # The key is a byte encoding, so an int64 matrix must not be narrowed to
        # the helper's int32 width: the two widths order relabellings differently.
        big = np.int64(np.iinfo(np.int32).max) + 1
        mu = np.array([[0, big], [1, 0]], dtype=np.int64)
        with patch.object(e, "_C", None) as _:
            expected = _canonical_form(mu)
        self.assertEqual(_canonical_form(mu), expected)


if __name__ == "__main__":
    unittest.main()

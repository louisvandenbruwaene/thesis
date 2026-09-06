"""Regression tests for the claim markers and the cross-model floor."""

import math
import unittest
from unittest.mock import patch

import make_figures

from make_figures import (
    _reconcile_panel,
    _panel_cell,
    dir_block_bouquet_lower_bound,
    gather_variant_grid,
    block_bouquet_lower_bound,
)


class BlockBouquetLowerBound(unittest.TestCase):
    """The K_m(n) construction curve is the block bouquet, not the thickened tree.

    thm:clique-chain-vertex proves the thickened tree is not extremal from
    m = 5 on, so plotting it as the lower bound understated the panel the
    appendix works hardest on. The numbers below come from the independent
    block sweep in scripts/multi_vertex_blocks.py, which enumerates all
    2-connected graphs with geng and solves the knapsack of
    thm:multi-vertex-blocks. They are reproduced here as literals so the test
    needs neither geng nor networkx.

    An earlier version of this class pinned 45 at n = 8 against a curve built
    from theta blocks alone. The theta family stops at b = m+1 = 7, so it never
    saw g_6(8) = 47, and the pinned literal recorded the truncation rather than
    the sweep it names. The value below is the sweep's own.
    """

    # scripts/multi_vertex_blocks.py, blocks up to 8 vertices, m = 6: the row
    # g_6 = (5, 12, 19, 26, 33, 40, 47) of tab:multi-vertex-blocks, whose
    # per-vertex rate rises with b, so each n below is one single block.
    BLOCK_SWEEP_M6 = {2: 5, 3: 12, 4: 19, 5: 26, 6: 33, 7: 40, 8: 47}

    def test_it_matches_the_independent_block_sweep_at_m6(self):
        for n, expected in self.BLOCK_SWEEP_M6.items():
            self.assertEqual(block_bouquet_lower_bound(n, 6), expected, f"n={n}")

    def test_it_is_the_thickened_tree_where_the_tree_is_optimal(self):
        # K_m(n) = (m-1)(n-1) for m <= 3 (thm:hyper-vertex-m2/m3 at r = 2), and
        # the block sweep shows the two tie at m = 4.
        for m in (2, 3, 4):
            for n in range(2, 17):
                self.assertEqual(block_bouquet_lower_bound(n, m),
                                 (m - 1) * (n - 1), f"m={m}, n={n}")

    def test_it_never_falls_below_the_thickened_tree(self):
        for m in range(2, 9):
            for n in range(2, 17):
                self.assertGreaterEqual(block_bouquet_lower_bound(n, m),
                                        (m - 1) * (n - 1), f"m={m}, n={n}")

    def test_it_never_exceeds_the_trivial_maximum(self):
        # Every pair at multiplicity m-1 is the ceiling for any multigraph.
        for m in range(2, 9):
            for n in range(2, 17):
                self.assertLessEqual(block_bouquet_lower_bound(n, m),
                                     (m - 1) * (n * (n - 1) // 2), f"m={m}, n={n}")

    def test_it_rises_with_n(self):
        # An isolated vertex keeps a feasible multigraph feasible.
        for m in range(2, 9):
            values = [block_bouquet_lower_bound(n, m) for n in range(2, 17)]
            self.assertEqual(values, sorted(values), f"m={m}")


class DirectedBlockBouquetLowerBound(unittest.TestCase):
    """K_m^dir's curve is the better of the arc extremiser and the block bouquet.

    prop:dir-multi-vertex-blocks makes the directed incidence value additive over
    blocks, and the thickened complete digraph on b <= m vertices carries
    b(b-1)(m+1-b) arcs. Plotting the arc extremiser (m-1)M(n) alone understated
    the panel while n is small against m: at m=6, n=4 it read 34 against a
    checked 36. Every value below was realised as an explicit multidigraph and
    confirmed feasible by the program's own checker.
    """

    # max(arc extremiser, block bouquet), verified against the checker.
    EXPECTED_M6 = {2: 10, 3: 24, 4: 36, 5: 48, 6: 60, 7: 72, 8: 84, 9: 100}

    def _arc_extremiser(self, n, m):
        return (m - 1) * max(2 * (n - 1), n * n // 4)

    def test_the_panel_matches_the_verified_values_at_m6(self):
        panel = gather_variant_grid(m=6)[7]
        published = dict(zip(*panel["construction"]))
        for n, expected in self.EXPECTED_M6.items():
            self.assertEqual(published[n], expected, f"n={n}")

    def test_it_never_falls_below_the_arc_extremiser(self):
        # kappa <= lambda, so thm:dir-multi-full's extremiser is always available.
        for m in range(2, 9):
            for n in range(2, 17):
                self.assertGreaterEqual(
                    max(self._arc_extremiser(n, m),
                        dir_block_bouquet_lower_bound(n, m)),
                    self._arc_extremiser(n, m), f"m={m}, n={n}")

    def test_the_bouquet_is_the_thickened_tree_at_m3(self):
        # At m=3 the best block is the bidirected edge, so the bouquet is the
        # thickened bidirected tree with 2(m-1)(n-1) arcs.
        for n in range(2, 17):
            self.assertEqual(dir_block_bouquet_lower_bound(n, 3), 4 * (n - 1), f"n={n}")

    def test_no_lower_bound_sits_above_a_proved_optimum(self):
        for m in (3, 6):
            panel = gather_variant_grid(m=m)[7]
            exact = dict(zip(*panel["exact"]))
            for n, value in zip(*panel["construction"]):
                if n in exact:
                    self.assertLessEqual(value, exact[n], f"m={m}, n={n}")


class DirectedHypergraphLowerBound(unittest.TestCase):
    """The multihypergraph directed rows may not use the simple model's range.

    prop:dir-hyper-first splits V into alpha tails and n-alpha heads and hangs
    a head family of maximum degree m-1 off every tail. For the SIMPLE model the
    head edges must be distinct, which at r=3 caps alpha at n-m. The MULTI model
    reads the cyclic word in blocks of r-1 and repeats freely, so it needs only
    r-1 <= n-alpha, capping alpha at n-r+1. Using the simple cap on the multi
    rows understated them: at m=6, n=9 it gave 45 where the proposition proves
    50.
    """

    def _prop_bound(self, n, m, r=3):
        """prop:dir-hyper-first for the multi model, computed independently."""
        best = max((a * ((m - 1) * (n - a) // (r - 1))
                    for a in range(1, n - r + 2)), default=0)
        return min(best, n * math.comb(n - 1, 2))

    def test_no_multi_directed_hypergraph_cell_sits_below_the_proposition(self):
        for m in (3, 6):
            panels = gather_variant_grid(m=m)
            for idx in (14, 15):        # multihypergraph directed arc, vertex
                for n, value in zip(*panels[idx]["construction"]):
                    self.assertGreaterEqual(
                        value, self._prop_bound(n, m),
                        f"m={m}, panel {idx}, n={n}")

    def test_the_cell_that_was_wrong(self):
        panels = gather_variant_grid(m=6)
        for idx in (14, 15):
            published = dict(zip(*panels[idx]["construction"]))
            self.assertGreaterEqual(published[9], 50, f"panel {idx}")


class VariantTableClaims(unittest.TestCase):
    def _bound_panel(self, attained):
        return {
            "proved": ([6], [12]),
            "proved_is_bound": True,
            "exact": ([], []),
            "search": ([6], [attained]),
        }

    def test_matching_construction_turns_a_proved_bound_into_an_exact_value(self):
        self.assertEqual(
            _panel_cell(self._bound_panel(12), 6),
            ("12", "vtProved", False),
        )

    def test_unmatched_proved_bound_keeps_its_upper_bound_marker(self):
        self.assertEqual(
            _panel_cell(self._bound_panel(11), 6),
            (r"$\le$12", "vtProved", False),
        )


class EvidenceSeparation(unittest.TestCase):
    def test_every_panel_preserves_its_raw_search(self):
        original = make_figures._search_points
        for m in (3, 6):
            observed = []
            def capture(*args, **kwargs):
                result = original(*args, **kwargs)
                observed.append((list(result[0]), list(result[1])))
                return result
            with patch("make_figures._search_points", side_effect=capture):
                panels = gather_variant_grid(m)
            self.assertEqual(len(observed), 16)
            for panel, raw in zip(panels, observed):
                self.assertEqual(panel["search"], raw)

    def test_underperformance_is_not_replaced_or_smoothed(self):
        panel = dict(exact=([3], [5]), search=([3, 4, 5], [2, 1, 3]),
                     construction=([3, 4, 5], [5, 6, 7]))
        self.assertEqual(_reconcile_panel(panel)["search"][1], [2, 1, 3])

    def test_contradictions_raise_instead_of_clamping(self):
        for source in ("search", "construction"):
            with self.assertRaises(ValueError):
                _reconcile_panel(dict(exact=([4], [5]), **{source: ([4], [6])}))

    def test_closed_form_dispatch_is_not_an_enumeration_point(self):
        for m in (3, 6):
            self.assertEqual(gather_variant_grid(m)[6]["exact"], ([], []))

    def test_known_construction_can_close_gap_without_replacing_search(self):
        panel = dict(exact=([], []), proved=([6], [12]), proved_is_bound=True,
                     search=([6], [9]), construction=([6], [12]))
        self.assertEqual(_panel_cell(panel, 6), ("12", "vtProved", False))
        self.assertEqual(panel["search"][1], [9])


if __name__ == "__main__":
    unittest.main()

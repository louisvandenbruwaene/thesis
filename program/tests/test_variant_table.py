"""Regression tests for the claim markers and the cross-model floor."""

import math
import unittest

from make_figures import (
    _lift_multi_above_simple,
    _panel_cell,
    dir_block_bouquet_lower_bound,
    gather_variant_grid,
    theta_bouquet_lower_bound,
)


class ThetaBouquetLowerBound(unittest.TestCase):
    """The K_m(n) construction curve is the theta bouquet, not the thickened tree.

    thm:clique-chain-vertex proves the thickened tree is not extremal from
    m = 5 on, so plotting it as the lower bound understated the panel the
    appendix works hardest on. The numbers below come from the independent
    block sweep in scripts/multi_vertex_blocks.py, which enumerates all
    2-connected graphs with geng and solves the knapsack of
    thm:multi-vertex-blocks. They are reproduced here as literals so the test
    needs neither geng nor networkx.
    """

    # scripts/multi_vertex_blocks.py, blocks up to 7 vertices, m = 6.
    BLOCK_SWEEP_M6 = {2: 5, 3: 12, 4: 19, 5: 26, 6: 33, 7: 40, 8: 45}

    def test_it_matches_the_independent_block_sweep_at_m6(self):
        for n, expected in self.BLOCK_SWEEP_M6.items():
            self.assertEqual(theta_bouquet_lower_bound(n, 6), expected, f"n={n}")

    def test_it_is_the_thickened_tree_where_the_tree_is_optimal(self):
        # K_m(n) = (m-1)(n-1) for m <= 3 (thm:hyper-vertex-m2/m3 at r = 2), and
        # the block sweep shows the two tie at m = 4.
        for m in (2, 3, 4):
            for n in range(2, 17):
                self.assertEqual(theta_bouquet_lower_bound(n, m),
                                 (m - 1) * (n - 1), f"m={m}, n={n}")

    def test_it_never_falls_below_the_thickened_tree(self):
        for m in range(2, 9):
            for n in range(2, 17):
                self.assertGreaterEqual(theta_bouquet_lower_bound(n, m),
                                        (m - 1) * (n - 1), f"m={m}, n={n}")

    def test_it_never_exceeds_the_trivial_maximum(self):
        # Every pair at multiplicity m-1 is the ceiling for any multigraph.
        for m in range(2, 9):
            for n in range(2, 17):
                self.assertLessEqual(theta_bouquet_lower_bound(n, m),
                                     (m - 1) * (n * (n - 1) // 2), f"m={m}, n={n}")

    def test_it_rises_with_n(self):
        # An isolated vertex keeps a feasible multigraph feasible.
        for m in range(2, 9):
            values = [theta_bouquet_lower_bound(n, m) for n in range(2, 17)]
            self.assertEqual(values, sorted(values), f"m={m}")


class DirectedBlockBouquetLowerBound(unittest.TestCase):
    """K_m^dir's curve is the better of the arc extremiser and the block bouquet.

    prop:dir-multi-vertex-blocks makes the directed incidence value additive over
    blocks, and the thickened complete digraph on b <= m+1 vertices carries
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
        published = dict(zip(*panel["search"]))
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
            for n, value in zip(*panel["search"]):
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
                for n, value in zip(*panels[idx]["search"]):
                    self.assertGreaterEqual(
                        value, self._prop_bound(n, m),
                        f"m={m}, panel {idx}, n={n}")

    def test_the_cell_that_was_wrong(self):
        panels = gather_variant_grid(m=6)
        for idx in (14, 15):
            published = dict(zip(*panels[idx]["search"]))
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


class MultiDominatesSimple(unittest.TestCase):
    """A simple object is the multi object with every multiplicity one.

    So a simple witness is a multi witness, and no multi lower bound can sit
    below its simple counterpart. The raw searches did exactly that at m = 6 on
    the hypergraph vertex panel, at six of ten sizes, because the multi space is
    (m - 1) times larger per edge and the same budget explores less of it.
    """

    def _panels(self, simple_ys, multi_ys):
        """Sixteen panels, all trivial but for one simple/multi column pair."""
        blank = lambda: {"search": ([3, 4, 5], [0, 0, 0]), "exact": ([], [])}
        panels = [blank() for _ in range(16)]
        panels[9]["search"] = ([3, 4, 5], list(simple_ys))
        panels[13]["search"] = ([3, 4, 5], list(multi_ys))
        return panels

    def test_a_weaker_multi_bound_is_raised_to_the_simple_one(self):
        panels = _lift_multi_above_simple(self._panels([1, 15, 17], [5, 13, 16]))
        self.assertEqual(panels[13]["search"][1], [5, 15, 17])

    def test_a_stronger_multi_bound_is_left_alone(self):
        panels = _lift_multi_above_simple(self._panels([1, 4, 8], [5, 7, 10]))
        self.assertEqual(panels[13]["search"][1], [5, 7, 10],
                         "the multi model genuinely does better here")

    def test_the_simple_panel_is_never_touched(self):
        panels = _lift_multi_above_simple(self._panels([1, 15, 17], [5, 13, 16]))
        self.assertEqual(panels[9]["search"][1], [1, 15, 17])

    def test_the_published_grids_satisfy_the_inclusion(self):
        """The invariant on the real record, for every model pair and both m."""
        for m in (3, 6):
            panels = gather_variant_grid(m=m)
            for start in (0, 8):
                for column in range(4):
                    simple = panels[start + column]
                    multi = panels[start + 4 + column]
                    for series in ("search", "exact"):
                        floor = dict(zip(*simple[series]))
                        for n, value in zip(*multi[series]):
                            if n in floor:
                                with self.subTest(m=m, panel=start + column,
                                                  series=series, n=n):
                                    self.assertGreaterEqual(value, floor[n])


if __name__ == "__main__":
    unittest.main()

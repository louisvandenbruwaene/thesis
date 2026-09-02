"""Regression tests for the claim markers and the cross-model floor."""

import unittest

from make_figures import _lift_multi_above_simple, _panel_cell, gather_variant_grid


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

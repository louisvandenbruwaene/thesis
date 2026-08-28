"""Regression tests for the claim markers in the generated variant table."""

import unittest

from make_figures import _panel_cell


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


if __name__ == "__main__":
    unittest.main()

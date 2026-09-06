"""Printed comparisons must retain the unaided outcomes verbatim."""

import unittest

from scripts.benchmark_tables import detailed


class BenchmarkTables(unittest.TestCase):
    def test_construction_does_not_raise_printed_search(self):
        rows = [dict(variant=i, n=6, m=3, key=str(i), search_min=4,
                     search_median=5, search_max=6, qualified_seeds=3) for i in range(8)]
        data = dict(rows=rows, variant_labels={str(i): f"variant {i}" for i in range(8)})
        baseline = dict(cells={str(i): dict(construction=10) for i in range(8)})
        table = detailed(data, baseline, 3, 0)
        self.assertEqual(table.count("6 & 4 & 5 & 6 & 10 & 3"), 8)
        self.assertEqual(table.count("variant "), 8)

    def test_larger_search_is_not_clamped_to_construction(self):
        rows = [dict(variant=i, n=12, m=6, key=str(i), search_min=31,
                     search_median=33, search_max=36, qualified_seeds=3) for i in range(8,16)]
        data = dict(rows=rows, variant_labels={str(i): f"variant {i}" for i in range(8,16)})
        baseline = dict(cells={str(i): dict(construction=30) for i in range(8,16)})
        self.assertEqual(detailed(data, baseline, 6, 8).count("12 & 31 & 33 & 36 & 30 & 3"), 8)

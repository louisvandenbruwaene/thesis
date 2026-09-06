"""Bugs reproduced during the September audit, without expensive benchmarks."""

import time
import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

import numpy as np
import erdos915_unified as e


class IntegerArithmetic(unittest.TestCase):
    def test_large_multiplicities_are_not_truncated(self):
        for directed in (False, True):
            g = e.Graph(2, e.Variant(directed=directed, simple=False))
            g.set_multiplicity(0, 1, 2**32)
            for separation in ("edge", "vertex"):
                self.assertTrue(e.exceeds_bound(g, 1, separation=separation))
                self.assertFalse(e.exceeds_bound(g, 2**32, separation=separation))
                self.assertEqual(e.max_connectivity(g, vertex_split=separation == "vertex"), 2**32)

    def test_large_capacities_do_not_collide_with_empty_canonical_key(self):
        g = e.Graph(3, e.MULTI_DIRECTED)
        empty = e._canonical_form(g.mu)
        g.set_multiplicity(0, 1, 2**32)
        self.assertNotEqual(e._canonical_form(g.mu), empty)
        p = [2, 0, 1]
        self.assertEqual(e._canonical_form(g.mu), e._canonical_form(g.mu[np.ix_(p, p)]))

    def test_accumulated_flow_and_objective_do_not_overflow(self):
        q = 2**63 - 1
        g = e.Graph(3, e.MULTI_DIRECTED)
        for u, v in ((0, 1), (0, 2), (2, 1), (1, 0)):
            g.set_multiplicity(u, v, q)
        self.assertEqual(g.edge_count(), 4 * q)
        self.assertEqual(g.out_degree(0), 2 * q)
        self.assertEqual(e.local_connectivity(g, 0, 1), 2 * q)
        with self.assertRaises(ValueError):
            g.add_edge(0, 1)
        self.assertEqual(g.multiplicity(0, 1), q)


class Budgets(unittest.TestCase):
    def test_solve_does_not_use_calendar_clock_for_duration(self):
        with patch.object(e.time, "time", side_effect=AssertionError("calendar clock used")):
            for hyper in (False, True):
                for simple in (False, True):
                    for directed in (False, True):
                        for separation in ("edge", "vertex"):
                            for exhaustive in (False, True):
                                result = e.solve(3, 3, hypergraph=hyper, r=3, simple=simple,
                                                 directed=directed, separation=separation,
                                                 exhaustive=exhaustive, max_seconds=0.005)
                                self.assertGreaterEqual(result.seconds, 0)

    def test_legacy_absolute_deadlines_and_monotonic_deadlines(self):
        with patch.object(e.time, "time", return_value=99), \
             patch.object(e.time, "monotonic", return_value=10):
            self.assertFalse(e._deadline_passed(100))
            self.assertTrue(e._deadline_passed(99))
            self.assertFalse(e._deadline_passed(e._DurationDeadline(11)))
            self.assertTrue(e._deadline_passed(e._DurationDeadline(10)))
            self.assertFalse(e._deadline_passed(None))

    def test_invalid_budgets_are_rejected(self):
        for budget in (-1, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                e.solve(3, 3, max_seconds=budget)

    def test_zero_budget_returns_empty_feasible_discovery(self):
        for method in ("sa", "tabu"):
            result = e.solve(3, 3, max_seconds=0, method=method)
            self.assertEqual(result.value, 0)
            self.assertEqual(result.witness.edge_count(), 0)

    def test_hypergraph_growth_checks_deadline_inside_sweep(self):
        calls = []
        def expired_after_first_check(*args, **kwargs):
            calls.append(1)
            return 0
        with patch.object(e, "max_hyper_connectivity", side_effect=expired_after_first_check), \
             patch.object(e.time, "time", side_effect=[0, 0, 2, 2]):
            value, witness = e._random_hypergraph_search(5, 3, 3, 1, 0)
        self.assertEqual(len(calls), 1)
        self.assertEqual(value, witness.edge_count())
        self.assertEqual(value, 1)


class RecordedEvidence(unittest.TestCase):
    def test_fresh_records_save_raw_values_and_replayable_witnesses(self):
        from make_figures import MachineValues
        with tempfile.TemporaryDirectory() as directory:
            ledger = MachineValues(Path(directory) / "published.json", rebuild=True)
            for hyper in (False, True):
                for simple in (False, True):
                    for directed in (False, True):
                        for separation in ("edge", "vertex"):
                            kw = dict(hypergraph=hyper, simple=simple, directed=directed,
                                      separation=separation, r=3)
                            result = e.solve(4, 3, max_seconds=0.05, seed=0, **kw)
                            check = e.max_hyper_connectivity if hyper else e.max_connectivity
                            self.assertLessEqual(check(result.witness, vertex_split=separation == "vertex"), 2)
                            value = ledger.get_or_run("search", 4, 3, 0.05, kw, lambda: result)
                            self.assertEqual(value, result.value)
                            key = ledger.key("search", 4, 3, 0.05, kw)
                            saved = json.loads(ledger.candidate.read_text())["runs"][key]
                            self.assertEqual(saved["value"], result.witness.edge_count())
                            self.assertFalse(saved["construction_seeded"])
                            self.assertIsNotNone(saved["witness"])
                            self.assertEqual(saved["elapsed_seconds"], result.seconds)

    def test_saved_rediscovery_witnesses_are_feasible_stars(self):
        path = Path(__file__).resolve().parents[1] / "data" / "rediscovery.json"
        for key, run in json.loads(path.read_text())["runs"].items():
            matrix = np.array(run["witness"]["multiplicity_matrix"])
            n = len(matrix)
            m = int(key.split("|m=")[1].split("|")[0])
            variant = e.Variant(directed="directed=True" in key, simple="simple=True" in key)
            graph = e.Graph(n, variant)
            graph.mu = matrix
            self.assertEqual(graph.edge_count(), run["value"])
            self.assertLessEqual(e.max_edge_connectivity(graph), m - 1)
            support = matrix > 0
            self.assertTrue(np.array_equal(support, support.T))
            self.assertEqual(sorted(support.sum(axis=1).tolist()), [1] * (n - 1) + [n - 1])
            self.assertTrue(np.all(matrix[support] == m - 1))


if __name__ == "__main__":
    unittest.main()

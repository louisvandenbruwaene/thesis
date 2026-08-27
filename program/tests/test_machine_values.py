"""The machine-value cache: a refresh may confirm or improve it, never degrade it.

These entries are *timed* measurements, so a slower or busier machine returns
worse numbers for reasons that have nothing to do with the mathematics.  The
reconciliation rule in :meth:`MachineValues._reconcile` is what stops that from
reaching the published figures, and it is the rule these tests pin.
"""

import json
import tempfile
import unittest
from pathlib import Path

from make_figures import MachineValues


class Reconciliation(unittest.TestCase):
    def _cache(self, published):
        """A cache whose file already holds ``published``, opened in refresh mode."""
        tmp = Path(tempfile.mkdtemp()) / "machine_values.json"
        tmp.write_text(json.dumps({"meta": {}, "values": published}))
        return MachineValues(tmp, refresh=True)

    # --- exact: a completed exhaustion is the true maximum -------------------

    def test_a_timeout_never_overwrites_a_recorded_exact_value(self):
        key = "exact|n=4|m=3|budget=4|directed=True"
        mv = self._cache({key: 8})
        got = mv.get_or_run("exact", 4, 3, 4, {"directed": True}, lambda: None)
        self.assertEqual(got, 8, "a run that ran out of budget must not erase a value")
        self.assertEqual(mv.values[key], 8)
        self.assertTrue(mv.kept)
        self.assertIn("keeping the recorded 8", mv.kept[0])

    def test_finishing_where_the_record_timed_out_is_an_improvement(self):
        key = "exact|n=5|m=3|budget=4|directed=True"
        mv = self._cache({key: None})
        got = mv.get_or_run("exact", 5, 3, 4, {"directed": True}, lambda: 14)
        self.assertEqual(got, 14)
        self.assertTrue(mv.improved)
        self.assertFalse(mv.contradictions)

    def test_two_different_exact_values_are_reported_not_applied(self):
        key = "exact|n=4|m=3|budget=4|directed=True"
        mv = self._cache({key: 8})
        got = mv.get_or_run("exact", 4, 3, 4, {"directed": True}, lambda: 9)
        self.assertEqual(got, 8, "the record stands until a human looks at it")
        self.assertTrue(mv.contradictions)
        self.assertIn("recorded 8, recomputed 9", mv.contradictions[0])
        self.assertIn("CONTRADICTIONS", mv.report())

    def test_agreement_is_silent(self):
        key = "exact|n=4|m=3|budget=4|directed=True"
        mv = self._cache({key: 8})
        self.assertEqual(
            mv.get_or_run("exact", 4, 3, 4, {"directed": True}, lambda: 8), 8)
        self.assertFalse(mv.kept or mv.improved or mv.contradictions)

    # --- search: a lower bound, so it only ever climbs -----------------------

    def test_a_weaker_search_result_is_not_applied(self):
        key = "search|n=10|m=3|budget=0.4|directed=True"
        mv = self._cache({key: 16})
        got = mv.get_or_run("search", 10, 3, 0.4, {"directed": True}, lambda: 13)
        self.assertEqual(got, 16, "a witnessed lower bound cannot regress")
        self.assertTrue(mv.kept)

    def test_a_stronger_search_result_is_applied(self):
        key = "search|n=10|m=3|budget=0.4|directed=True"
        mv = self._cache({key: 16})
        got = mv.get_or_run("search", 10, 3, 0.4, {"directed": True}, lambda: 19)
        self.assertEqual(got, 19)
        self.assertTrue(mv.improved)

    # --- entries the record has never seen -----------------------------------

    def test_a_new_key_is_taken_as_it_comes(self):
        mv = self._cache({})
        self.assertEqual(
            mv.get_or_run("exact", 9, 9, 4, {"directed": False}, lambda: 3), 3)
        self.assertFalse(mv.kept or mv.contradictions)

    def test_refresh_still_recomputes_every_entry(self):
        key = "exact|n=4|m=3|budget=4|directed=True"
        mv = self._cache({key: 8})
        calls = []
        mv.get_or_run("exact", 4, 3, 4, {"directed": True},
                      lambda: calls.append(1) or 8)
        self.assertEqual(len(calls), 1,
                         "refresh must not serve the published value from cache")

    def test_without_refresh_the_file_is_served_and_nothing_reruns(self):
        key = "exact|n=4|m=3|budget=4|directed=True"
        tmp = Path(tempfile.mkdtemp()) / "machine_values.json"
        tmp.write_text(json.dumps({"meta": {}, "values": {key: 8}}))
        mv = MachineValues(tmp, refresh=False)
        def boom():
            raise AssertionError("should not have been called")
        self.assertEqual(
            mv.get_or_run("exact", 4, 3, 4, {"directed": True}, boom), 8)
        self.assertEqual(mv.hits, 1)


if __name__ == "__main__":
    unittest.main()

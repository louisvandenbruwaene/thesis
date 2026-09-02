"""The machine-value record: rendering reads it, rebuilding remakes it.

The two acts are deliberately separate.  These entries are *timed* measurements,
so a rerun on a slower or busier machine can return a different, still honest,
number for reasons that have nothing to do with the mathematics.  A render that
quietly recomputed would therefore redraw the thesis differently on a different
laptop, which is what these tests pin: rendering never computes, rebuilding never
publishes, and what moved between the two is reported for a person to read.
"""

import json
import tempfile
import unittest
from pathlib import Path

from make_figures import MachineValues, MissingMachineValue

KEY = "exact|n=4|m=3|budget=4|directed=True"
SEARCH_KEY = "search|n=10|m=3|budget=0.4|directed=True"


def _record(published):
    """A published record holding ``published``, in its own temporary directory."""
    tmp = Path(tempfile.mkdtemp()) / "machine_values.json"
    tmp.write_text(json.dumps({"meta": {}, "values": published}))
    return tmp


class Rendering(unittest.TestCase):
    """No flag: the frozen record is the only source of a number."""

    def test_the_record_is_served_and_nothing_reruns(self):
        mv = MachineValues(_record({KEY: 8}))

        def boom():
            raise AssertionError("rendering must not compute")

        self.assertEqual(mv.get_or_run("exact", 4, 3, 4, {"directed": True}, boom), 8)
        self.assertEqual(mv.hits, 1)

    def test_a_missing_value_is_an_error_not_a_fresh_run(self):
        """The defect this replaces: a missing key used to start a timed search.

        A value computed here would be drawn beside values measured on another
        machine at another time, and nothing in the figure would say so.
        """
        mv = MachineValues(_record({}))
        with self.assertRaises(MissingMachineValue) as caught:
            mv.get_or_run("exact", 4, 3, 4, {"directed": True}, lambda: 8)
        self.assertIn("--rebuild", caught.exception.args[0])

    def test_rendering_never_writes(self):
        path = _record({KEY: 8})
        before = path.read_text()
        mv = MachineValues(path)
        mv.get_or_run("exact", 4, 3, 4, {"directed": True}, lambda: 8)
        self.assertEqual(path.read_text(), before)
        self.assertFalse(mv.candidate.exists())


class Rebuilding(unittest.TestCase):
    """--rebuild: recompute everything from scratch, publish nothing."""

    def test_every_entry_is_recomputed_and_the_record_is_untouched(self):
        path = _record({KEY: 8})
        before = path.read_text()
        mv = MachineValues(path, rebuild=True)
        calls = []
        mv.get_or_run("exact", 4, 3, 4, {"directed": True},
                      lambda: calls.append(1) or 9)
        self.assertEqual(len(calls), 1, "a rebuild must not serve the record")
        self.assertEqual(path.read_text(), before,
                         "the published record is untouched by a rebuild")
        self.assertTrue(mv.candidate.exists())
        self.assertEqual(json.loads(mv.candidate.read_text())["values"], {KEY: 9})

    def test_the_candidate_records_what_produced_it(self):
        mv = MachineValues(_record({}), rebuild=True)
        mv.get_or_run("exact", 4, 3, 4, {"directed": True}, lambda: 9)
        meta = json.loads(mv.candidate.read_text())["meta"]
        self.assertEqual(meta["program_sha256"], mv.program_hash)
        for field in ("source_commit", "python", "platform", "computed", "entries"):
            self.assertIn(field, meta)

    def test_an_interrupted_rebuild_resumes(self):
        path = _record({KEY: 8})
        first = MachineValues(path, rebuild=True)
        first.get_or_run("exact", 4, 3, 4, {"directed": True}, lambda: 9)

        resumed = MachineValues(path, rebuild=True)
        self.assertEqual(resumed.resumed, 1)

        def must_not_run():
            self.fail("a recovered value was recomputed")

        self.assertEqual(
            resumed.get_or_run("exact", 4, 3, 4, {"directed": True}, must_not_run), 9)

    def test_a_candidate_from_another_program_is_discarded(self):
        path = _record({KEY: 8})
        mv = MachineValues(path, rebuild=True)
        mv.get_or_run("exact", 4, 3, 4, {"directed": True}, lambda: 9)
        stale = json.loads(mv.candidate.read_text())
        stale["meta"]["program_sha256"] = "0" * 64
        mv.candidate.write_text(json.dumps(stale))

        fresh = MachineValues(path, rebuild=True)
        self.assertEqual(fresh.resumed, 0)
        self.assertEqual(fresh.values, {},
                         "half-finished work from another program is not resumed")


class Comparing(unittest.TestCase):
    """--compare: say what moved, judge nothing."""

    def _candidate(self, published, computed):
        path = _record(published)
        mv = MachineValues(path, rebuild=True)
        for cache_key, value in computed.items():
            kind, n, m, budget = cache_key.split("|")[:4]
            mv.values[cache_key] = value
        mv.save()
        return MachineValues(path)

    def test_agreement_is_silent(self):
        self.assertEqual(self._candidate({KEY: 8}, {KEY: 8}).compare(), [])

    def test_two_completed_exhaustions_disagreeing_is_called_out(self):
        report = self._candidate({KEY: 8}, {KEY: 9}).compare()
        self.assertEqual(len(report), 1)
        self.assertIn("8 -> 9", report[0])
        self.assertIn("DISAGREE", report[0],
                      "a completed exhaustion cannot legitimately change")

    def test_a_timeout_is_reported_as_a_fact_about_the_machine(self):
        report = self._candidate({KEY: 8}, {KEY: None}).compare()
        self.assertIn("did not finish", report[0])
        self.assertNotIn("DISAGREE", report[0])

    def test_a_moved_search_bound_says_which_way_it_moved(self):
        self.assertIn("reached less", self._candidate(
            {SEARCH_KEY: 16}, {SEARCH_KEY: 13}).compare()[0])
        self.assertIn("reached more", self._candidate(
            {SEARCH_KEY: 16}, {SEARCH_KEY: 19}).compare()[0])

    def test_entries_only_one_side_has_are_reported(self):
        added = self._candidate({}, {KEY: 8}).compare()
        self.assertIn("'absent' -> 8", added[0])
        dropped = self._candidate({KEY: 8}, {}).compare()
        self.assertIn("8 -> 'absent'", dropped[0])


class Promoting(unittest.TestCase):
    """--promote: the one act that changes the published record."""

    def test_promotion_replaces_the_record_and_clears_the_candidate(self):
        path = _record({KEY: 8})
        mv = MachineValues(path, rebuild=True)
        mv.get_or_run("exact", 4, 3, 4, {"directed": True}, lambda: 9)
        mv.promote()
        published = json.loads(path.read_text())
        self.assertEqual(published["values"], {KEY: 9})
        self.assertEqual(published["meta"]["program_sha256"], mv.program_hash)
        self.assertFalse(mv.candidate.exists())

    def test_promoting_nothing_is_refused(self):
        with self.assertRaises(SystemExit):
            MachineValues(_record({KEY: 8})).promote()


if __name__ == "__main__":
    unittest.main()

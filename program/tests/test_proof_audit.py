"""Finite checks of proof-audit helpers, not substitutes for the proofs."""

import subprocess
import unittest
from unittest.mock import patch

from scripts import review_simplified_proofs as review


class SeparatingPairBookkeeping(unittest.TestCase):
    def test_all_torso_bookkeeping_cases(self):
        # The separating vertices are 0 and 1. Each side is a two-edge path.
        # These fixtures exercise the torso operation, not a minimum-degree-3 core.
        edges = {(0, 2), (1, 2), (0, 3), (1, 3)}
        for x_set, retained in (({2, 3}, False), ({0, 2, 3}, False),
                                ({0, 1, 2, 3}, False), ({0, 2, 3}, True)):
            with self.subTest(x_set=x_set, retained=retained):
                pairs = edges | ({(0, 1)} if retained else set())
                graph = review.MG(range(4), {frozenset(e): 1 for e in pairs}, x_set)
                self.assertTrue(review.hypotheses(graph))
                s = len(x_set & {0, 1})
                left, right, mode = review.torsos(graph, 0, 1, {2}, {3}, s)
                for torso in (left, right):
                    self.assertTrue(torso.connected())
                    self.assertTrue(review.hypotheses(torso))
                    self.assertLess(torso.rank(), len(torso.X))
                rank_sum = left.rank() + right.rank()
                self.assertEqual(graph.rank(), rank_sum if retained else rank_sum - 1)
                added_x = 1 if retained else (s or 2)
                self.assertEqual(len(left.X) + len(right.X), len(x_set) + added_x)
                self.assertEqual(mode, "retained" if retained else
                                 ("temp-edge" if s else "fresh-vertex"))

    def test_failed_generator_is_not_reported_as_an_empty_search(self):
        failure = subprocess.CalledProcessError(1, ["geng"])
        with patch.object(subprocess, "run", side_effect=failure) as run:
            with self.assertRaises(subprocess.CalledProcessError):
                review.check_core_vacuity(4)
        self.assertTrue(run.call_args.kwargs["check"])

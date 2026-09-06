"""Failure reporting and independently retained block witnesses."""

from contextlib import redirect_stdout
import io
import itertools
import unittest
from unittest.mock import patch

try:
    import networkx as nx
    from scripts import multi_vertex_blocks_b9 as sweep
    from scripts.multi_vertex_blocks import kappa_simple, W
except ImportError:
    nx = None


@unittest.skipUnless(nx is not None, "networkx is optional")
class BlockAudit(unittest.TestCase):
    def test_generator_failure_cannot_report_exact(self):
        with patch.object(sweep.subprocess, "Popen") as popen:
            popen.return_value.stdout = iter(())
            popen.return_value.wait.return_value = 1
            with self.assertRaisesRegex(RuntimeError, "does not prove"):
                sweep.main()

    def test_exclusion_threshold_is_not_an_attained_value(self):
        with patch.object(sweep.subprocess, "Popen") as popen, redirect_stdout(io.StringIO()) as out:
            popen.return_value.stdout = iter(())
            popen.return_value.wait.return_value = 0
            sweep.main()
        self.assertIn("g_6(9) <= 52", out.getvalue())
        self.assertNotIn("g_6(9) = 52", out.getvalue())

    def test_retained_nine_vertex_witness(self):
        import erdos915_unified as engine
        graph = nx.from_graph6_bytes(b"H??EDz}")
        self.assertEqual(graph.number_of_nodes(), 9)
        self.assertEqual(graph.number_of_edges(), 14)
        self.assertTrue(nx.is_biconnected(graph))
        self.assertEqual(W(graph, 6), 54)
        witness = engine.Graph(9, engine.MULTI_UNDIRECTED)
        for u, v in graph.edges():
            witness.set_multiplicity(u, v, 6 - kappa_simple(graph, u, v))
        self.assertEqual(witness.edge_count(), 54)
        self.assertEqual(engine.max_vertex_connectivity(witness), 5)

    def test_incidence_rank_lemma_on_small_simple_graphs(self):
        checked = 0
        for graph in nx.graph_atlas_g():
            n = graph.number_of_nodes()
            if not 1 <= n <= 6 or not nx.is_connected(graph):
                continue
            kappa = {(u, v): kappa_simple(graph, u, v)
                     for u, v in itertools.combinations(graph.nodes(), 2)}
            for mask in range(1 << n):
                z = {v for v in graph if mask & (1 << v)}
                x = set(graph) - z
                if any(graph.degree(v) < 2 for v in z):
                    continue
                if any(u in z and v in z for u, v in graph.edges()):
                    continue
                if any(kappa[u, v] > 2 for u, v in itertools.combinations(sorted(x), 2)):
                    continue
                checked += 1
                self.assertLessEqual(graph.number_of_edges() - n + 1, len(x) - 1)
        self.assertGreater(checked, 100)


if __name__ == "__main__":
    unittest.main()

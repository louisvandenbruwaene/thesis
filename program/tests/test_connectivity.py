"""The connectivity checker (edge and vertex) and the Gomory-Hu shortcut."""

import random
import unittest

from erdos915_unified import (
    Graph,
    MULTI_DIRECTED,
    MULTI_UNDIRECTED,
    NETWORKX_AVAILABLE,
    SIMPLE_DIRECTED,
    SIMPLE_UNDIRECTED,
    exceeds_bound,
    local_edge_connectivity,
    local_vertex_connectivity,
    max_connectivity,
    max_edge_connectivity,
    max_edge_connectivity_via_tree,
    max_vertex_connectivity,
    sample_random_graph,
)


def random_multigraph(variant, n, rng, max_mult=2):
    """A random graph of ``variant`` on ``n`` vertices for predicate testing.

    Simple variants take multiplicities in ``{0, 1}``; multigraph variants in
    ``{0, ..., max_mult}``.  Directed variants fill every ordered pair, undirected
    variants the upper triangle (``set_multiplicity`` mirrors the lower half).
    """
    g = Graph(n, variant)
    top = 1 if variant.simple else max_mult
    for u in range(n):
        start = 0 if variant.directed else u + 1
        for v in range(start, n):
            if u != v:
                g.set_multiplicity(u, v, rng.randint(0, top))
    return g


def complete_graph(n, variant=SIMPLE_UNDIRECTED):
    g = Graph(n, variant)
    for u in range(n):
        for v in range(u + 1, n):
            g.add_edge(u, v)
    return g


def star(n):
    g = Graph(n, SIMPLE_UNDIRECTED)
    for leaf in range(1, n):
        g.add_edge(0, leaf)
    return g


def cycle(n):
    g = Graph(n, SIMPLE_UNDIRECTED)
    for v in range(n):
        g.add_edge(v, (v + 1) % n)
    return g


class EdgeConnectivity(unittest.TestCase):
    def test_tree_is_one(self):
        self.assertEqual(max_edge_connectivity(star(6)), 1)

    def test_cycle_is_two(self):
        self.assertEqual(max_edge_connectivity(cycle(6)), 2)

    def test_complete_graph(self):
        for n in (3, 4, 5):
            self.assertEqual(max_edge_connectivity(complete_graph(n)), n - 1)
            self.assertEqual(local_edge_connectivity(complete_graph(n), 0, 1), n - 1)

    def test_parallel_edges_count_as_routes(self):
        g = Graph(3, MULTI_UNDIRECTED)
        g.add_edge(0, 1, 4)
        self.assertEqual(local_edge_connectivity(g, 0, 1), 4)
        self.assertEqual(max_edge_connectivity(g), 4)

    def test_directed_arc_disjoint_routes(self):
        g = Graph(3, SIMPLE_DIRECTED)
        g.add_edge(0, 1)  # direct route
        g.add_edge(0, 2)  # detour 0 -> 2 -> 1
        g.add_edge(2, 1)
        self.assertEqual(local_edge_connectivity(g, 0, 1), 2)

    def test_removing_an_edge_never_raises_lambda(self):
        rng = random.Random(11)
        for _ in range(20):
            g = sample_random_graph(8, 0.4, False, rng)
            before = max_edge_connectivity(g)
            for u, v, _count in list(g.edges()):
                reduced = g.copy()
                reduced.set_multiplicity(u, v, 0)
                self.assertLessEqual(max_edge_connectivity(reduced), before)


class VertexConnectivity(unittest.TestCase):
    def test_complete_graph(self):
        for n in (3, 4, 5):
            self.assertEqual(max_vertex_connectivity(complete_graph(n)), n - 1)
            self.assertEqual(local_vertex_connectivity(complete_graph(n), 0, 1), n - 1)

    def test_whitney_inequality_on_random_graphs(self):
        rng = random.Random(0)
        for _ in range(40):
            g = sample_random_graph(12, 0.3, False, rng)
            self.assertLessEqual(max_vertex_connectivity(g), max_edge_connectivity(g))


@unittest.skipUnless(NETWORKX_AVAILABLE, "Gomory-Hu trees need the optional networkx")
class GomoryHu(unittest.TestCase):
    def test_tree_matches_direct_sweep(self):
        for g in (cycle(6), complete_graph(5), star(7)):
            self.assertEqual(max_edge_connectivity_via_tree(g), max_edge_connectivity(g))

    def test_multigraph_matches(self):
        g = Graph(4, MULTI_UNDIRECTED)
        g.add_edge(0, 1, 3)
        g.add_edge(1, 2, 2)
        g.add_edge(2, 3, 1)
        g.add_edge(0, 3, 2)
        self.assertEqual(max_edge_connectivity_via_tree(g), max_edge_connectivity(g))


class CappedPredicate(unittest.TestCase):
    """``exceeds_bound`` must agree with the exact checker, pair set for pair set.

    This pins the cheap capped predicate the search relies on to the trusted
    exact ``max_connectivity`` over every variant, separation and threshold.
    """

    def test_predicate_matches_exact_value(self):
        variants = (SIMPLE_UNDIRECTED, MULTI_UNDIRECTED,
                    SIMPLE_DIRECTED, MULTI_DIRECTED)
        rng = random.Random(2024)
        for variant in variants:
            for n in (3, 4, 5):
                for _ in range(8):
                    g = random_multigraph(variant, n, rng)
                    for sep in ("edge", "vertex"):
                        split = sep == "vertex"
                        exact = max_connectivity(g, vertex_split=split)
                        for k in range(-1, exact + 2):
                            self.assertEqual(
                                exceeds_bound(g, k, separation=sep),
                                exact > k,
                                msg=f"{variant.name} n={n} sep={sep} k={k} "
                                    f"exact={exact}",
                            )

    def test_predicate_does_not_mutate_the_graph(self):
        rng = random.Random(7)
        g = random_multigraph(MULTI_DIRECTED, 5, rng)
        before = g.mu.copy()
        exceeds_bound(g, 1, separation="vertex")
        exceeds_bound(g, 1, separation="edge")
        self.assertTrue((g.mu == before).all())


if __name__ == "__main__":
    unittest.main()

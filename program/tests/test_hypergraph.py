"""The hypergraph model and Berge connectivity by the helper-point network."""

import itertools
import random
import unittest

import numpy as np

from erdos915_unified import (
    Hypergraph,
    complete_uniform_hypergraph,
    hyper_connectivity,
    hyperedge_connectivity,
    max_feasible_hyperedges,
    max_hyperedge_connectivity,
    star_hypertree,
    _hyperedge_candidates,
    _hyper_canonical,
    _csgraph_maxflow,
    _csr,
    _dir_tails_heads,
    _UNBOUNDED,
)


class BergeConnectivity(unittest.TestCase):
    def test_single_hyperedge_carries_one_route(self):
        h = Hypergraph(3, [[0, 1, 2]])
        self.assertEqual(h.edge_count(), 1)
        self.assertEqual(hyperedge_connectivity(h, 0, 1), 1)
        self.assertEqual(hyperedge_connectivity(h, 0, 2), 1)
        self.assertEqual(hyperedge_connectivity(h, 1, 2), 1)

    def test_two_hyperedges_give_two_routes(self):
        h = Hypergraph(4, [[0, 1, 2], [0, 1, 3]])
        self.assertEqual(h.edge_count(), 2)
        self.assertEqual(hyperedge_connectivity(h, 0, 1), 2)
        self.assertEqual(len(h.incident_hyperedges(0)), 2)
        self.assertEqual(len(h.incident_hyperedges(2)), 1)

    def test_complete_three_uniform_k4(self):
        self.assertEqual(max_hyperedge_connectivity(complete_uniform_hypergraph(4, 3)), 3)

    def test_two_uniform_reduces_to_edge_connectivity(self):
        for n in (3, 4, 5):
            self.assertEqual(max_hyperedge_connectivity(complete_uniform_hypergraph(n, 2)), n - 1)

    def test_star_hypertree(self):
        for n, r in [(7, 3), (10, 4), (13, 4)]:
            h = star_hypertree(n, r)
            self.assertEqual(h.edge_count(), (n - 1) // (r - 1))
            self.assertEqual(max_hyperedge_connectivity(h), 1)

    def test_bad_hyperedge_size_rejected(self):
        with self.assertRaises(ValueError):
            star_hypertree(7, 1)


class DirectedOrientationModels(unittest.TestCase):
    """Forward / backward / general directed hyperedge models."""

    def test_general_gate_is_one_way(self):
        # A mixed arc {0,1} -> {2,3}: a route enters at a tail, leaves at a head.
        h = Hypergraph(4, [(frozenset({0, 1}), frozenset({2, 3}))], directed=True)
        self.assertEqual(sorted(h.members(h.hyperedges[0])), [0, 1, 2, 3])
        self.assertEqual(hyper_connectivity(h, 0, 2), 1)   # tail -> head
        self.assertEqual(hyper_connectivity(h, 2, 0), 0)   # head -> tail: none

    def test_forward_legacy_equals_general_form(self):
        legacy = Hypergraph(3, [(0, frozenset({1, 2}))], directed=True)
        general = Hypergraph(3, [(frozenset({0}), frozenset({1, 2}))], directed=True)
        for s, t in [(0, 1), (0, 2), (1, 2)]:
            self.assertEqual(hyper_connectivity(legacy, s, t),
                             hyper_connectivity(general, s, t))

    def test_canonical_form_accepts_mixed_storage_forms(self):
        legacy = (0, frozenset({1, 2}))
        general = (frozenset({0}), frozenset({1, 2}))
        self.assertEqual(_hyper_canonical([legacy], 3, True),
                         _hyper_canonical([general], 3, True))
        mixed = _hyper_canonical([legacy, general], 3, True)
        self.assertEqual(len(mixed), 2)
        self.assertEqual(mixed[0], mixed[1])

    def test_candidate_counts_split_at_r3(self):
        # At r = 3 every split has a singleton side, so general = forward + backward.
        fwd = _hyperedge_candidates(4, 3, True, kind="forward")
        bwd = _hyperedge_candidates(4, 3, True, kind="backward")
        gen = _hyperedge_candidates(4, 3, True, kind="general")
        self.assertEqual(len(fwd), 12)
        self.assertEqual(len(bwd), 12)
        self.assertEqual(len(gen), 24)

    def test_forward_backward_duality(self):
        # Arc reversal makes backward the dual of forward: same extremal numbers.
        for n, m in [(3, 3), (4, 3), (4, 2)]:
            f, _ = max_feasible_hyperedges(n, 3, m, directed=True, kind="forward", time_limit=2.0)
            b, _ = max_feasible_hyperedges(n, 3, m, directed=True, kind="backward", time_limit=2.0)
            self.assertEqual(f, b)

    def test_general_beats_forward_when_vertices_scarce(self):
        # n = r is the regime where the richer orientation set packs more arcs.
        g3, e3 = max_feasible_hyperedges(3, 3, 3, directed=True, kind="general", time_limit=2.0)
        f3, _ = max_feasible_hyperedges(3, 3, 3, directed=True, kind="forward", time_limit=2.0)
        self.assertTrue(e3)
        self.assertEqual((g3, f3), (4, 3))

    def test_general_contains_forward(self):
        # General can never be worse than forward (forward hypergraphs are general).
        for n, m in [(4, 3), (5, 2)]:
            f, _ = max_feasible_hyperedges(n, 3, m, directed=True, kind="forward", time_limit=2.0)
            g, _ = max_feasible_hyperedges(n, 3, m, directed=True, kind="general",
                                           time_limit=3.0, seed_lb=f)
            self.assertGreaterEqual(g, f)

    def test_unverified_seed_cannot_be_reported_as_exact(self):
        with self.assertRaisesRegex(ValueError, "claimed feasible"):
            max_feasible_hyperedges(
                4, 3, 2, directed=True, kind="forward",
                time_limit=10.0, seed_lb=5,
            )


def _per_copy_capacity_matrix(hg, *, vertex_split=False):
    """The gate network with ONE CAPACITY-ONE GATE PER COPY.

    This is the construction ``_hyper_capacity_matrix`` used before it merged
    parallel copies into a single gate of capacity ``mu``.  It is kept here, and
    only here, as the reference the merged version is held to.
    """
    n = hg.num_vertices
    base = 2 * n if vertex_split else n
    size = base + 2 * len(hg.hyperedges)
    cap = np.zeros((size, size), dtype=int)
    leave = (lambda v: 2 * v + 1) if vertex_split else (lambda v: v)
    enter = (lambda v: 2 * v) if vertex_split else (lambda v: v)
    if vertex_split:
        for v in range(n):
            cap[2 * v, 2 * v + 1] = 1
    for index, edge in enumerate(hg.hyperedges):
        gate_in, gate_out = base + 2 * index, base + 2 * index + 1
        cap[gate_in, gate_out] = 1
        if hg.directed:
            tails, heads = _dir_tails_heads(edge)
            for tail in tails:
                cap[leave(tail), gate_in] = _UNBOUNDED
            for head in heads:
                cap[gate_out, enter(head)] = _UNBOUNDED
        else:
            for vertex in edge:
                cap[leave(vertex), gate_in] = _UNBOUNDED
                cap[gate_out, enter(vertex)] = _UNBOUNDED
    return cap, leave, enter


def _per_copy_connectivity(hg, source, target, *, vertex_split=False):
    cap, leave, enter = _per_copy_capacity_matrix(hg, vertex_split=vertex_split)
    if vertex_split:
        cap[2 * source, 2 * source + 1] = _UNBOUNDED
        cap[2 * target, 2 * target + 1] = _UNBOUNDED
    return int(_csgraph_maxflow(_csr(cap, dtype=int),
                                leave(source), enter(target)).flow_value)


class MergedGateMatchesPerCopy(unittest.TestCase):
    """One gate of capacity mu must measure what mu capacity-one gates measured.

    The checker gives each DISTINCT hyperedge one gate whose capacity is its
    multiplicity, which is the network ``fig:hyper-gadget`` draws and
    ``thm:menger-hyper`` proves.  Giving every copy its own capacity-one gate puts
    parallel arcs between the same two nodes, and combining parallel arcs into one
    arc of their summed capacity leaves every cut alone, so the two networks have
    the same min cut and the same max flow.  This test is that argument checked
    rather than asserted, over both separations, both orientations, and both
    directed storage spellings.
    """

    def _cases(self, trials, seed):
        rng = random.Random(seed)
        for _ in range(trials):
            n = rng.randint(2, 6)
            r = rng.randint(2, min(4, n))
            directed = rng.random() < 0.5
            candidates = list(itertools.combinations(range(n), r))
            edges = []
            for _ in range(rng.randint(0, 6)):
                base = rng.choice(candidates)
                if not directed:
                    edges.append(frozenset(base))
                    continue
                members = list(base)
                tails = frozenset(rng.sample(members, rng.randint(1, r - 1)))
                heads = frozenset(x for x in members if x not in tails)
                if not heads:
                    continue
                # exercise the legacy forward spelling as well as the general one,
                # since the merge key has to see through the difference
                if len(tails) == 1 and rng.random() < 0.5:
                    edges.append((next(iter(tails)), heads))
                else:
                    edges.append((tails, heads))
            yield Hypergraph(n, edges, directed=directed)

    def test_agrees_with_the_per_copy_network(self):
        compared = with_repeats = 0
        for hg in self._cases(trials=400, seed=20260827):
            keys = {(_dir_tails_heads(e) if hg.directed else frozenset(e))
                    for e in hg.hyperedges}
            if len(keys) != len(hg.hyperedges):
                with_repeats += 1
            for source, target in itertools.permutations(range(hg.num_vertices), 2):
                for vertex_split in (False, True):
                    merged = hyper_connectivity(hg, source, target,
                                                vertex_split=vertex_split)
                    per_copy = _per_copy_connectivity(hg, source, target,
                                                      vertex_split=vertex_split)
                    self.assertEqual(
                        merged, per_copy,
                        msg=(f"n={hg.num_vertices} directed={hg.directed} "
                             f"split={vertex_split} pair=({source},{target}) "
                             f"edges={hg.hyperedges}"))
                    compared += 1
        self.assertGreater(compared, 5000)
        # the test is worthless if nothing ever had a copy to merge
        self.assertGreater(with_repeats, 20)

    def test_a_repeated_hyperedge_carries_one_route_per_copy(self):
        triple = frozenset({0, 1, 2})
        for copies in (1, 2, 3, 4):
            h = Hypergraph(3, [triple] * copies)
            self.assertEqual(hyperedge_connectivity(h, 0, 1), copies)
            self.assertEqual(hyper_connectivity(h, 0, 1, vertex_split=True), copies)



if __name__ == "__main__":
    unittest.main()

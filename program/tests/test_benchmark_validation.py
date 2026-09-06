"""Hand-counted witnesses for the independent benchmark validator."""

import copy
import itertools
import random
import unittest

from scripts.equal_budget_benchmark import VARIANTS
try:
    from scripts.validate_benchmark import validate
except ModuleNotFoundError as error:
    if error.name != "networkx":
        raise
    validate = None


@unittest.skipIf(validate is None, "Independent witness validation requires NetworkX")
class IndependentValidation(unittest.TestCase):
    def test_flow_matches_direct_route_packing(self):
        # A second reference enumerates routes and packs disjoint resource sets.
        # It uses no flow algorithm and includes each parallel copy separately.
        rng = random.Random(915)
        for variant in VARIANTS:
            for sample in range(12):
                n, copies = 4, []
                if variant["hypergraph"]:
                    for members in itertools.combinations(range(n), 3):
                        tails = members if variant["directed"] else (None,)
                        for tail in tails:
                            edge = ([tail], [v for v in members if v != tail]) if tail is not None else (members, members)
                            copies.extend([edge] * rng.randrange(2 if variant["simple"] else 3))
                    witness = dict(hyperedges=[list(map(list, e)) if variant["directed"] else list(e[0]) for e in copies])
                else:
                    matrix = [[0]*n for _ in range(n)]
                    pairs = itertools.permutations(range(n), 2) if variant["directed"] else itertools.combinations(range(n), 2)
                    for u, v in pairs:
                        q = rng.randrange(2 if variant["simple"] else 3)
                        matrix[u][v] = q
                        if not variant["directed"]:
                            matrix[v][u] = q
                        copies.extend([((u,), (v,)) if variant["directed"] else ((u,v), (u,v))]*q)
                    witness = dict(multiplicity_matrix=matrix)
                maximum = 0
                for source, target in itertools.permutations(range(n), 2):
                    resources = set()
                    def visit(v, vertices, edges):
                        if v == target:
                            mask = sum(1 << e for e in edges)
                            if variant["separation"] == "vertex":
                                mask |= sum(1 << (len(copies)+x) for x in vertices - {source, target})
                            resources.add(mask)
                            return
                        for index, (tails, heads) in enumerate(copies):
                            if v in tails and index not in edges:
                                for w in heads:
                                    if w not in vertices:
                                        visit(w, vertices | {w}, edges | {index})
                    visit(source, {source}, set())
                    packings = {0: 0}
                    for mask in resources:
                        for used, count in list(packings.items()):
                            if not used & mask:
                                packings[used | mask] = max(packings.get(used | mask, 0), count+1)
                    maximum = max(maximum, max(packings.values()))
                record = dict(trial=dict(n=n, m=maximum+1, **variant), witness=witness,
                              value=len(copies), max_connectivity=maximum)
                with self.subTest(variant=variant, sample=sample):
                    self.assertEqual(validate(record)["max_connectivity"], maximum)

    def record(self, variant):
        q = 1 if variant["simple"] else 2
        trial = dict(n=3, m=6, **variant)
        if variant["hypergraph"]:
            edge = [[0], [1, 2]] if variant["directed"] else [0, 1, 2]
            witness = dict(hyperedges=[edge]*q)
            value, connectivity = q, q
        else:
            matrix = [[0, q, q], [0, 0, q], [0, 0, 0]]
            if not variant["directed"]:
                matrix[1][0] = matrix[2][0] = matrix[2][1] = q
            witness = dict(multiplicity_matrix=matrix)
            value = 3*q
            connectivity = q+1 if variant["separation"] == "vertex" else 2*q
        return dict(trial=trial, witness=witness, value=value, max_connectivity=connectivity)

    def test_all_sixteen_models(self):
        for variant in VARIANTS:
            with self.subTest(variant=variant):
                record = self.record(variant)
                self.assertEqual(validate(record)["max_connectivity"], record["max_connectivity"])
                altered = copy.deepcopy(record)
                altered["value"] += 1
                with self.assertRaises(ValueError):
                    validate(altered)
                altered = copy.deepcopy(record)
                altered["trial"]["m"] = record["max_connectivity"]
                with self.assertRaises(ValueError):
                    validate(altered)

    def test_interior_vertex_is_shared_but_edges_are_not(self):
        matrix = [[0]*5 for _ in range(5)]
        for u, v in ((0,1), (0,2), (2,1), (1,3), (1,4), (4,3)):
            matrix[u][v] = 1
        # This illustrates a local difference. The maximum over all pairs is 2
        # in either model, so it is not evidence that the extremal values differ.
        for separation in ("edge", "vertex"):
            record = dict(trial=dict(n=5,m=3,hypergraph=False,simple=True,
                                    directed=True,separation=separation),
                          witness=dict(multiplicity_matrix=matrix), value=6,max_connectivity=2)
            self.assertEqual(validate(record)["value"], 6)

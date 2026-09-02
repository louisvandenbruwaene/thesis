"""Numerical checks behind SIMPLIFIED_AI_PROOFS_REVIEW.md.

Three independent checks, each against the thesis program's own checker where a
connectivity value is needed:

1. the cut induction of the review's Lemma 18, on random NON-UNIFORM
   multihypergraphs, which is the generality its induction actually runs in;
2. the degree-smoothing lemma, by running its own exchange step to a fixed
   point from random starts and confirming the fixed point is balanced and has
   maximum degree exactly ceil(re/n);
3. the cyclic-word construction, by direct enumeration.

Run with the repo virtualenv:  .venv/bin/python3 program/scripts/review_simplified_proofs.py
"""

import itertools
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "program"))

from erdos915_unified import (Graph, Hypergraph, Variant,  # noqa: E402
                              local_connectivity, max_hyperedge_connectivity)

UND = Variant(directed=False, simple=False)


def check_cut_induction(trials: int = 4000, seed: int = 20260831) -> None:
    """sum_e (|e| - 1) <= k (n - 1) for every multihypergraph with lambda^max <= k."""
    rng = random.Random(seed)
    violations = 0
    tight = 0
    for _ in range(trials):
        n = rng.randint(2, 7)
        edges = [frozenset(rng.sample(range(n), rng.randint(2, n)))
                 for _ in range(rng.randint(1, 7))]
        k = max_hyperedge_connectivity(Hypergraph(n, edges))
        lhs = sum(len(e) - 1 for e in edges)
        rhs = k * (n - 1)
        violations += lhs > rhs
        tight += lhs == rhs
    print(f"cut induction: {violations} violations in {trials} trials, "
          f"{tight} attained with equality")
    assert violations == 0


def check_degree_smoothing(max_n: int = 8, seed: int = 7) -> None:
    """The minimiser of sum deg^2 is balanced, with max degree exactly ceil(re/n)."""
    rng = random.Random(seed)
    failures = 0
    for n in range(2, max_n + 1):
        for r in range(1, n + 1):
            sets = [frozenset(s) for s in itertools.combinations(range(n), r)]
            for e in range(len(sets) + 1):
                family = set(rng.sample(sets, e))
                for _ in range(4000):
                    deg = Counter()
                    for s in family:
                        deg.update(s)
                    hi = max(range(n), key=lambda v: deg[v])
                    lo = min(range(n), key=lambda v: deg[v])
                    if deg[hi] - deg[lo] < 2:
                        break
                    # The lemma's claim: such an exchange always exists.
                    for a in list(family):
                        if hi in a and lo not in a and (a - {hi}) | {lo} not in family:
                            family.discard(a)
                            family.add((a - {hi}) | {lo})
                            break
                    else:
                        print(f"  stuck at n={n} r={r} e={e}")
                        failures += 1
                        break
                deg = Counter()
                for s in family:
                    deg.update(s)
                spread = max(deg[v] for v in range(n)) - min(deg[v] for v in range(n))
                if spread > 1:
                    print(f"  unbalanced at n={n} r={r} e={e}")
                    failures += 1
                if e and max(deg[v] for v in range(n)) != -(-r * e // n):
                    print(f"  wrong max degree at n={n} r={r} e={e}")
                    failures += 1
    print(f"degree smoothing: {failures} failures up to n={max_n}")
    assert failures == 0


def check_cyclic_word(max_b: int = 11, max_d: int = 11) -> None:
    """Blocks of k consecutive letters of the round-robin word have degree <= d."""
    failures = 0
    for b in range(2, max_b + 1):
        for k in range(1, b + 1):
            for d in range(max_d + 1):
                e = (d * b) // k
                word = [i % b for i in range(e * k)]
                blocks = [word[i * k:(i + 1) * k] for i in range(e)]
                if any(len(set(block)) != k for block in blocks):
                    print(f"  repeated vertex at b={b} k={k} d={d}")
                    failures += 1
                deg = Counter(v for block in blocks for v in block)
                if blocks and max(deg.values()) > d:
                    print(f"  degree {max(deg.values())} > {d} at b={b} k={k}")
                    failures += 1
    print(f"cyclic word: {failures} failures up to b={max_b}")
    assert failures == 0




# ---------------------------------------------------------------------------
# Second pass: the incidence-rank lemma of the revision dossier, executed.
#
# The dossier replaces the lemma's Tutte/SPQR case by a split along a separating
# pair.  The code below walks the dossier's own case analysis on real instances
# and asserts every claim it makes: that each recursive sub-instance still
# satisfies (1)-(4), that the rank and |X| identities hold in each branch, and
# that the bound comes out.
#
# TWO TRAPS, both hit while writing this:
#  * condition (iv) is the NON-COLLAPSING kappa, as the lemma's own two-vertex
#    base case shows when it caps a multiplicity at two.  The program's
#    vertex mode collapses parallel copies (sec:parallel-convention) and returns
#    1 for every multiplicity, so kappa has to be rebuilt as mu + pi through
#    lem:multi-vertex-split.
#  * blocks cannot be found by unioning edges that share a non-cut vertex: a
#    four-cycle with a pendant at two opposite vertices splits into two false
#    blocks that way.  Use a real biconnected-components routine.
# ---------------------------------------------------------------------------

class MG:
    """Multigraph as {frozenset({u,v}): mult}, vertices a sorted tuple, X a set."""
    def __init__(self, verts, mult, X):
        self.V = tuple(sorted(verts)); self.mu = dict(mult); self.X = set(X)
    def deg(self, v):
        return sum(m for e, m in self.mu.items() if v in e) + \
               sum(m for e, m in self.mu.items() if len(e) == 1 and v in e)
    def nbrs(self, v):
        return {w for e in self.mu for w in e if v in e and w != v}
    def E(self):  return sum(self.mu.values())
    def rank(self): return self.E() - len(self.V) + 1
    def Z(self):  return set(self.V) - self.X
    def connected(self):
        seen = {self.V[0]}; stack = [self.V[0]]
        while stack:
            v = stack.pop()
            for w in self.nbrs(v):
                if w not in seen: seen.add(w); stack.append(w)
        return len(seen) == len(self.V)
    def minus(self, drop):
        keep = [v for v in self.V if v not in drop]
        mu = {e: m for e, m in self.mu.items() if not (e & set(drop))}
        return MG(keep, mu, self.X & set(keep))
    def to_graph(self):
        idx = {v: i for i, v in enumerate(self.V)}
        g = Graph(len(self.V), UND)
        for e, m in self.mu.items():
            u, v = tuple(e); g.mu[idx[u], idx[v]] = m; g.mu[idx[v], idx[u]] = m
        return g, idx

def kappa(G, u, v):
    """Non-collapsing kappa, the reading lem:incidence-rank (iv) uses.

    By lem:multi-vertex-split, kappa(u,v) = mu(u,v) + pi(u,v), where pi counts
    internally disjoint routes of length at least two in the underlying SIMPLE
    graph.  The program's own vertex mode collapses parallel copies
    (sec:parallel-convention), so it cannot be called directly here.
    """
    idx = {w: i for i, w in enumerate(G.V)}
    g = Graph(len(G.V), UND)
    for e in G.mu:                       # underlying simple graph, uv deleted
        a, b = tuple(e)
        if {a, b} == {u, v}: continue
        g.mu[idx[a], idx[b]] = 1; g.mu[idx[b], idx[a]] = 1
    pi = local_connectivity(g, idx[u], idx[v], vertex_split=True)
    return G.mu.get(frozenset({u, v}), 0) + pi

def kappa_pairs_ok(G):
    """(iv): kappa(x,x') <= 2 for all distinct x,x' in X."""
    return all(kappa(G, x, y) <= 2
               for x, y in itertools.combinations(sorted(G.X), 2))

def hypotheses(G):
    if not G.V or not G.connected(): return False
    for e in G.mu:                                    # (i) Z independent
        u, v = tuple(e)
        if u not in G.X and v not in G.X: return False
    for e, m in G.mu.items():                         # (ii) no parallel at Z
        u, v = tuple(e)
        if m > 1 and (u not in G.X or v not in G.X): return False
    for z in G.Z():                                   # (iii)
        if G.deg(z) < 2: return False
    return kappa_pairs_ok(G)                          # (iv)

def cut_vertices(G):
    out = []
    for v in G.V:
        if len(G.V) > 1 and not G.minus({v}).connected(): out.append(v)
    return out

def blocks(G):
    """Blocks as sub-multigraphs, via networkx biconnected components.

    Multiplicities ride along: parallel copies of one pair are in one block.
    """
    import networkx as nx
    H = nx.Graph()
    H.add_nodes_from(G.V)
    H.add_edges_from(tuple(e) for e in G.mu)
    out = []
    for comp in nx.biconnected_components(H):
        mu = {e: m for e, m in G.mu.items() if e <= comp}
        if mu:
            out.append(MG(comp, mu, G.X & comp))
    return out

def separating_pairs(G):
    return [p for p in itertools.combinations(G.V, 2)
            if len(G.V) > 2 and not G.minus(set(p)).connected()]

STATS = Counter()

def bound(G, depth=0):
    """Run the document's proof; assert every claim; return rank(G)."""
    assert hypotheses(G), ("sub-instance violates (1)-(4)", G.V, G.mu, G.X)
    n, r, x = len(G.V), G.rank(), len(G.X)

    if n <= 2:
        STATS["base"] += 1
        assert r <= x - 1, ("base fails", G.V, G.mu, G.X, r, x)
        return r

    cuts = cut_vertices(G)
    if cuts:
        STATS["cut vertex"] += 1
        Bs = blocks(G)
        for B in Bs:
            if B.E() == 1 and len(B.V) == 2:      # bridge block: handled directly
                assert B.rank() == 0 and len(B.X) >= 1, "bridge block has no X-vertex"
                STATS["bridge block"] += 1
            else:
                assert all(B.deg(z) >= 2 for z in B.Z()), "2-connected block has a Z-leaf"
                bound(B, depth + 1)
        assert r == sum(B.rank() for B in Bs), "rank not additive over blocks"
        bcount = Counter(v for B in Bs for v in B.V)
        assert sum(len(B.X) for B in Bs) == x + sum(bcount[v] - 1 for v in G.X if v in cuts)
        assert len(Bs) == 1 + sum(bcount[v] - 1 for v in cuts)
        assert r <= x - 1, ("cut-vertex branch fails", G.V, G.mu, G.X)
        return r

    z2 = [z for z in G.Z() if G.deg(z) == 2]
    if z2:
        STATS["suppress Z"] += 1
        z = z2[0]; a, b = sorted(G.nbrs(z))
        mu = {e: m for e, m in G.mu.items() if z not in e}
        key = frozenset({a, b}); mu[key] = mu.get(key, 0) + 1
        H = MG(set(G.V) - {z}, mu, G.X)
        assert H.rank() == r and len(H.X) == x, "suppression changed rank or |X|"
        bound(H, depth + 1)
        assert r <= x - 1
        return r

    x2 = [v for v in G.X if G.deg(v) == 2]
    if x2:
        STATS["delete X"] += 1
        H = G.minus({x2[0]})
        assert H.rank() == r - 1 and len(H.X) == x - 1, "deletion arithmetic wrong"
        bound(H, depth + 1)
        assert r <= x - 1
        return r

    # 2-connected, minimum degree >= 3.
    STATS["min-degree-3 core REACHED"] += 1
    assert all(G.deg(v) >= 3 for v in G.V)
    simple = all(m == 1 for m in G.mu.values())
    STATS["core simple" if simple else "core NOT simple"] += 1
    seps = separating_pairs(G)
    if not seps:
        STATS["core 3-connected"] += 1
        assert False, ("3-connected core survived, contradiction expected", G.V, G.mu, G.X)
    a, b = seps[0]
    comps = components(G.minus({a, b}))
    U = set(comps[0]); W = set().union(*comps[1:])
    s = len({a, b} & G.X)
    GU, GW, mode = torsos(G, a, b, U, W, s)
    ru, rw = bound(GU, depth + 1), bound(GW, depth + 1)
    if mode == "retained":
        assert s == 1, "retained ab edge with s != 1"
        assert r == ru + rw and len(GU.X) + len(GW.X) == x + 1
    else:
        assert r == ru + rw - 1
        assert len(GU.X) + len(GW.X) == x + (s if mode == "temp-edge" else 2)
    assert r <= x - 1
    return r

def components(G):
    seen, out = set(), []
    for v in G.V:
        if v in seen: continue
        comp, stack = {v}, [v]
        while stack:
            u = stack.pop()
            for w in G.nbrs(u):
                if w not in comp: comp.add(w); stack.append(w)
        seen |= comp; out.append(comp)
    return out

def torsos(G, a, b, U, W, s):
    key = frozenset({a, b})
    def side(S, fresh):
        keep = S | {a, b}
        mu = {e: m for e, m in G.mu.items() if e <= keep}
        X = (G.X & keep)
        if key in G.mu:
            return MG(keep, mu, X), "retained"
        if s >= 1:
            mu = dict(mu); mu[key] = 1
            return MG(keep, mu, X), "temp-edge"
        mu = dict(mu); mu[frozenset({a, fresh})] = 1; mu[frozenset({fresh, b})] = 1
        return MG(keep | {fresh}, mu, X | {fresh}), "fresh-vertex"
    GU, mode = side(U, ("c", 0)); GW, _ = side(W, ("c", 1))
    return GU, GW, mode



def check_incidence_rank(nmax: int = 5, maxmult: int = 3) -> None:
    checked = 0
    for n in range(2, nmax + 1):
        pairs = list(itertools.combinations(range(n), 2))
        for Xmask in range(1 << n):
            X = {v for v in range(n) if Xmask >> v & 1}
            allowed = [p for p in pairs if p[0] in X or p[1] in X]
            caps = [maxmult if (p[0] in X and p[1] in X) else 1 for p in allowed]
            for choice in itertools.product(*[range(c + 1) for c in caps]):
                mu = {frozenset(p): m for p, m in zip(allowed, choice) if m}
                if not mu:
                    continue
                G = MG(range(n), mu, X)
                if hypotheses(G):
                    bound(G)
                    checked += 1
    print(f"incidence rank: {checked} instances (n<={nmax}, multiplicity<={maxmult}), "
          f"every branch verified")
    print(f"  branch counts: {dict(sorted(STATS.items()))}")
    assert STATS["min-degree-3 core REACHED"] == 0, (
        "the separating-pair case fired; it was expected to be unreachable")


def check_core_vacuity(nmax: int = 7) -> None:
    """The 2-connected, minimum-degree-3 core is empty, so the dossier's
    separating-pair recursion can never be exercised by a computation."""
    import subprocess

    def decode(g6, n):
        bits = "".join(f"{ord(c) - 63:06b}" for c in g6[1:])
        E, k = [], 0
        for j in range(1, n):
            for i in range(j):
                if bits[k] == "1":
                    E.append((i, j))
                k += 1
        return E

    found = 0
    for n in range(4, nmax + 1):
        out = subprocess.run(["geng", "-q", "-c", "-C", "-d3", str(n)],
                             capture_output=True, text=True).stdout
        total = 0
        for line in out.splitlines():
            E = decode(line.strip(), n)
            total += 1
            G = MG(range(n), {frozenset(e): 1 for e in E}, set(range(n)))
            ok = {frozenset((x, y)) for x, y in itertools.combinations(range(n), 2)
                  if kappa(G, x, y) <= 2}
            for size in range(n, 1, -1):
                for X in itertools.combinations(range(n), size):
                    Xs = set(X)
                    if any(frozenset((x, y)) not in ok
                           for x, y in itertools.combinations(X, 2)):
                        continue
                    if any(u not in Xs and v not in Xs for u, v in E):
                        continue
                    print(f"  CORE INSTANCE n={n} X={sorted(Xs)} E={E}")
                    found += 1
        print(f"core vacuity: n={n}, {total} two-connected graphs of minimum degree 3")
    print(f"core vacuity: {found} instances satisfying (1)-(4) with |X| >= 2")
    assert found == 0

if __name__ == "__main__":
    check_cut_induction()
    check_degree_smoothing()
    check_cyclic_word()
    check_incidence_rank()
    check_core_vacuity()
    print("ALL CHECKS PASSED")

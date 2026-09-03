# The hypergraph vertex problem at m = 4: no counterexample, but the surrounding claim has a boundary (2026-07-31)

**Status: two findings, one PROVED, one VERIFIED-negative.**

1. **PROVED.** The general formula `k_m^(r)(n) = floor((m-1)(n-1)/(r-1))`
   cannot hold for all `m` and `r`: it already fails at `r = 2` for every
   `m >= 5` and every `n >= 3`, as a corollary of `thm:clique-chain-vertex`.
   The reason is an identification the thesis states in one direction only.
2. **VERIFIED (no counterexample).** At `m = 4` the formula survives an
   exhaustive check at eleven `(n, r)` pairs, both halves (target attained,
   target+1 infeasible), well beyond the single previously-known cell
   `k_4^(3)(5) = 6`.

## 1. r = 2 IS the multigraph vertex problem, so the clique chains apply

`rem:hyper-vertex-m3-scope` already notes that at `r = 2` the hypergraph
vertex theorem "speaks of multigraphs under the hyperedge-as-gate convention".
The identification runs both ways, which the remark did not spell out:

**Claim.** At `r = 2`, the hypergraph vertex measure equals the multigraph
vertex measure of `sec:multi-vertex-standard`, i.e. `kappa(u,v) = mu(u,v) +
pi(u,v)` (`lem:multi-vertex-split`).

*Proof.* The hypergraph measure counts Berge routes that are pairwise
hyperedge-disjoint **and** internally vertex-disjoint. At `r = 2` hyperedges
are edges. The `mu(u,v)` parallel copies of `uv` are pairwise edge-disjoint
(distinct copies) and internally vertex-disjoint (empty interior), so all of
them count. Any two internally-vertex-disjoint paths of length `>= 2` are
automatically edge-disjoint: a shared edge incident to `u` would put its other
endpoint in both interiors, and a shared edge further along would likewise
share interior vertices. So the edge-disjointness requirement bites only among
the length-one routes, where it is exactly what makes parallel copies count
separately. Hence the two measures agree. []

Consequently `k_m^(2)(n) = K_m^multi(n)`, and `thm:clique-chain-vertex`
applies verbatim. Taking `r = 3` blocks in that theorem (a triangle at
multiplicity `m-2` plus pendant edges at `m-1`) gives, for every `m >= 5` and
`n >= 3`, a feasible multigraph with

```
(m-1)(n-1) + floor(n/3)*(m-4)  >  (m-1)(n-1) = floor((m-1)(n-1)/(2-1)),
```

so the formula fails at `r = 2` by a margin growing linearly in `n`.

This also matches the thesis's own `tab:multi-vertex`, whose bold entries
(value 14 at `m=5,n=4` and 19 at `m=5,n=5`, against the formula's 12 and 16)
are exactly this failure seen at small `n`. Independently re-derived here: the
incidence-graph search of Section 3, run at `r = 2`, finds the formula holds at
`m = 3, 4` and fails at `m = 5`, and the witness it returns at `m=5, n=5` is
a triangle at multiplicity 3 with two pendant edges at multiplicity 4, i.e.
precisely the clique-chain shape, found without being told to look for it.

**Consequence for the open problem.** The live question is not "is the formula
true for all `m`, `r`" (it is not) but "does `r >= 3` postpone the failure past
`m = 4`". The `m = 4` row below is therefore right at the boundary, which is
what makes it worth testing hard rather than assuming.

## 2. m = 4: exhaustive, no counterexample at eleven sizes

A counterexample at `(n, r, m)` is a feasible `r`-uniform multihypergraph with
`floor((m-1)(n-1)/(r-1)) + 1` hyperedges. The arithmetic reason is exact: for a
connected incidence graph with `b` hyperedges of size `r` on `n` vertices,

```
rank(I) = b(r-1) - n + 1,   so   rank(I) > (m-2)(n-1)  <=>  b > (m-1)(n-1)/(r-1),
```

so "one hyperedge past the formula" and "rank past the conjectured bound" are
the same condition. Searching for that is therefore a direct test of the
missing `4`-connectivity rank bound, not a proxy for it.

Result at `m = 4`, all exhaustive, both halves confirmed (`floor(3(n-1)/(r-1))`
attained, one more infeasible):

| (n, r) | target | (n, r) | target | (n, r) | target |
|--------|--------|--------|--------|--------|--------|
| (4,3)  | 4      | (6,5)  | 3      | (8,7)  | 3      |
| (5,3)  | 6      | (7,5)  | 4      | (9,7)  | 4      |
| (5,4)  | 4      | (7,6)  | 3      | (9,8)  | 3      |
| (6,4)  | 5      | (8,6)  | 4      |        |        |

No counterexample. This is evidence, not proof: the missing ingredient is
still a `4`-connectivity analogue of the Tutte/SPQR decomposition that
`lem:incidence-rank` uses at `m = 3`.

## 3. Method

`scripts/hyper_vertex_m4_search.py`, self-contained (standard library only, own
Edmonds-Karp, own incidence-graph model, no dependence on the thesis program it
corroborates). Depth-first over multisets of `r`-sets with two prunings:
feasibility is monotone under adding hyperedges, so an infeasible prefix is
cut, and a codegree filter drops any prefix in which two vertices already lie
in `m` common hyperedges (those give `m` one-step routes on their own).

Cross-validation: run at `r = 2` it reproduces the multigraph vertex values of
`tab:multi-vertex`, including the `m = 5` failure and its witness, which is an
independent re-derivation of `thm:clique-chain-vertex` from a completely
different search space.

## 4. What is still open

- The `4`-connectivity rank bound `kappa_X <= 3 => rank <= 2(|X|-1)` for
  incidence graphs, which would give `m = 4` for all `n, r`. Untouched here.
- Where the formula first breaks for `r >= 3`. A search at `m = 5, 6` for
  `r = 3, 4, 5` was launched but had not returned within the session's budget
  (the looser codegree cap at higher `m` widens the space sharply). This is the
  natural next computation, and the `r = 2` result says the answer is not
  "never".

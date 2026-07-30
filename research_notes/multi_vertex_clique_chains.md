# conj:multi-vertex is FALSE for every m >= 5: clique-chain construction (2026-07-31)

**Status: PROVED (refutation + new lower bound).** `conj:multi-vertex`
(app_proofs.tex, `sec:multi-vertex-standard`) claims `K_m^multi(n) =
(m-1)(n-1)` for all `n >= m+2`, i.e. that the thickened tree is optimal past
the small-n regime where the thickened theta wins. This is false for every
`m >= 5`: chaining disjoint `K_r` cliques (thickened at the per-block-optimal
multiplicity) through single bridge vertices beats the thickened tree by an
amount that is *linear in n*, not a bounded correction. The true value of
`K_m^multi(n)` grows like `Theta(n m^2)` as `n -> infinity` for large fixed
`m`, not `Theta(n m)` as the withdrawn conjecture assumed.

## 1. The construction

Fix `3 <= r <= m+1`. A **`K_r`-block** is a clique on `r` vertices with every
edge at multiplicity `q = m + 1 - r` (this is exactly the thesis's own
"thickened complete graph" construction, `sec:multi-vertex-standard`, applied
locally to `r` vertices rather than to all of `n`).

**Chain construction.** Partition (as many as possible of) the `n` vertices
into `k = floor(n/r)` disjoint `K_r`-blocks `B_1, ..., B_k`. Fix a *port*
vertex `p_i` in each block `B_i` (any vertex will do; take the first).
Connect `p_i` to `p_{i+1}` by a single edge at multiplicity `m - 1`, for
`i = 1, ..., k-1`. Attach the `n - rk` leftover vertices as a pendant path off
`p_k`, each edge again at multiplicity `m - 1`. This is a simple generalization
of the thesis's own "thickened tree", replacing some of the tree's edges with
`K_r`-blocks wherever a block fits.

## 2. Exact multiplicity count

Let `gain(r, m) := (r-1)(r-2)(m-1-r)/2` (an integer, since `(r-1)(r-2)` is
always even). The chain construction's total multiplicity is *exactly*

```
K(n, m, r) = (m-1)(n-1) + floor(n/r) * gain(r, m).
```

**Derivation.** By `lem:multi-vertex-split` (already in the thesis),
`kappa_G(u,v) = mu(u,v) + pi(u,v)` splits cleanly, so a feasible multigraph on
top of a fixed simple graph `G_0` maximizes total multiplicity by setting
`mu(u,v) = m - 1 - pi(u,v)` on every edge, giving total multiplicity
`(m-1)|E(G_0)| - sum_e pi(e)`. With `|E(G_0)| = n - 1 + rank(G_0)` (connected),
this is `(m-1)(n-1) + (m-1) rank(G_0) - sum_e pi(e)`.

For the chain: only the `k` cliques contribute rank (bridges and pendant
edges are bridges, rank 0 each), each `K_r` contributing rank
`C(r,2) - r + 1 = (r-1)(r-2)/2`, so `rank(G_0) = k(r-1)(r-2)/2`. Only clique
edges have nonzero `pi` (bridges have `pi = 0`, proved below), and inside a
`K_r`, every edge `uv` has `pi(u,v) = r - 2` exactly: `K_r` minus the edge `uv`
still connects `u,v` through each of the other `r-2` vertices (`r-2` pairwise
internally-disjoint 2-paths), and by Menger this is the maximum, since
removing those same `r-2` vertices is a cut of that size and no smaller cut
works (any single remaining common neighbor still connects them). So
`sum_e pi(e) = k * C(r,2) * (r-2) = k * r(r-1)(r-2)/2`. Substituting,

```
K(n,m,r) = (m-1)(n-1) + (m-1) k (r-1)(r-2)/2 - k r(r-1)(r-2)/2
         = (m-1)(n-1) + k (r-1)(r-2)[(m-1) - r]/2
         = (m-1)(n-1) + k * gain(r, m).
```

This matches the definition of `gain` and confirms the formula, independent
of the numerical check below.

## 3. Feasibility, proved by hand

Two claims cover every pair.

**Within a block.** For `u, v` in the same block `B_i` (an edge, multiplicity
`q`), `kappa_G(u,v) = q + pi(u,v)`. Any path of length >= 2 between `u,v` not
using edge `uv` cannot leave `B_i`: leaving would require crossing a bridge
edge, and a simple path cannot use a bridge edge twice (once out, once back),
so it would have to end outside `B_i`, contradicting that it returns to `v`
inside `B_i`. Hence all such paths stay inside `K_r`, where `pi(u,v) = r - 2`
exactly (Section 2). So `kappa_G(u,v) = (m+1-r) + (r-2) = m - 1`, exactly at
the cap, never over.

**Across blocks, or touching a bridge/pendant edge.** Every bridge and pendant
edge is a genuine graph bridge (its removal disconnects the graph, since the
chain-of-blocks structure has no other route between consecutive blocks), so
both of its endpoints are cut vertices. For `u` in `B_i` and `v` in `B_j`
(`i != j`), removing the port vertex adjacent to `u`'s side (or `v`'s side, if
`u` itself is that port) disconnects `u` from `v` with a single vertex, so
`pi(u,v) <= 1` and `mu(u,v) = 0` (no edge between different blocks unless one
is literally the bridge pair), giving `kappa_G(u,v) <= 1 \ll m - 1`. The same
argument bounds any pair touching the pendant path. So the binding constraint
is always inside a block, confirmed by both computational checks below (the
reported worst pair is always an edge of the first block).

## 4. Where this refutes the conjecture

`gain(r, m) = (r-1)(r-2)(m-1-r)/2`. At `r = 3` (the simplest block, a
triangle): `gain(3, m) = m - 4`. This is `0` at `m = 4` (consistent with the
thesis's own finding that `m <= 4` has no counterexample: a triangle buys
nothing there) and **strictly positive for every `m >= 5`**. So a single
triangle, glued onto a thickened tree anywhere, already beats
`(m-1)(n-1)` by `m - 4` for every `m >= 5`, refuting `conj:multi-vertex` as a
universal statement for `n >= m+2`. Packing `k = floor(n/3)` disjoint triangles
instead of one multiplies the gain by `k`, so the excess over the conjectured
value grows *linearly in n*, not as a bounded correction.

## 5. The true growth rate: Theta(n m^2), not Theta(n m)

`gain(r,m)` is *not* maximized at `r = 3` once `m` is large enough: treating
`r` as continuous, `gain(r,m)/r` (the gain rate per vertex used) has a maximum
near `r ~ m/2`, where `gain(r,m)/r = Theta(m^2)`. Concretely (exact integer
optimum, `scripts/multi_vertex_clique_check.py`):

| m  | best r | gain per block | gain rate per vertex |
|----|--------|-----------------|-----------------------|
| 5  | 3      | 1               | 0.33                  |
| 10 | 6      | 30              | 5.00                  |
| 20 | 11     | 360             | 32.73                 |
| 30 | 16     | 1365            | 85.31                 |
| 50 | 26     | 6900            | 265.38                |

So for `n -> infinity` at fixed large `m`, `K_m^multi(n) / n -> (m-1) +
Theta(m^2)`, i.e. the leading behaviour in `m` is quadratic, not linear. This
is a *qualitatively* different growth rate from what `conj:multi-vertex`
(and the surrounding prose, which reads the `m <= 4` data as suggesting the
tree wins past `n = m+2`) assumed.

## 6. What is still open

This is a new, proved *lower bound*
`K_m^multi(n) >= (m-1)(n-1) + floor(n/r*) * gain(r*, m)` (any fixed `r`
gives a valid bound; optimizing `r` gives the best one this family offers).
It is **not** known to be tight:

- Whether same-size clique chains are optimal among *all* feasible
  multigraphs is open. Mixed block sizes, blocks connected by more than one
  bridge, or a fundamentally different topology are not ruled out.
- The exact optimal `r*(m)` has no closed form derived here beyond the
  asymptotic `r* ~ m/2`; the table above is exact integer optimization, not
  a closed-form theorem.
- No matching upper bound is attempted. The true value of `K_m^multi(n)`
  for `n >= m+2` is now a genuinely open problem again, not (as the
  withdrawn conjecture claimed) a settled one modulo a single inequality.

## Verification

Two independent implementations agree exactly on every tested case (never
just close, always the same integer):
- `erdos915_unified.py`'s own `exceeds_bound(..., separation="vertex",
  parallel_routes=True)` (the thesis's exact checker for this convention).
- A from-scratch max-flow on a hand-built vertex-split network using
  `networkx.maximum_flow_value`, sharing no code with the thesis program.

`scripts/multi_vertex_clique_check.py` builds the chain construction, checks
feasibility both ways, and confirms the exact formula `K(n,m,r) =
(m-1)(n-1) + floor(n/r) gain(r,m)` at a spread of `(m, r, k, n)`, plus the
exact-optimal-`r` table above.

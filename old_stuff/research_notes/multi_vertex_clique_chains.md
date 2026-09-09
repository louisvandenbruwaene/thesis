# conj:multi-vertex is FALSE for every m >= 5 (2026-07-31)

**Status: PROVED (refutation + a lower bound of the right order, NOT the exact
value).** `conj:multi-vertex` claimed `K_m^multi(n) = (m-1)(n-1)` for all
`n >= m+2`, i.e. that the thickened spanning tree is optimal once past the
small-`n` regime where the thickened theta wins. It is false for every
`m >= 5`. Thickened cliques glued at a shared vertex beat the tree by an amount
*linear in n*, so the excess is not a bounded correction, and the growth rate
in `m` is `Theta(m^2)` rather than the `Theta(m)` the tree gives.

The construction below is **not** claimed to be optimal. See section 6.

> **SUPERSEDED AS A CONSTRUCTION (2026-08-14).** The refutation stands and the
> thesis keeps `thm:clique-chain-vertex`, but thickened cliques are no longer the
> best known family, and, more to the point, no longer the right *shape*: the
> computed extremal blocks are dense and **bipartite-like**, while unbalanced
> complete bipartite graphs give the best proved asymptotic construction.
> Thickened `K_{s,t}` beats the clique bouquet by a factor
> `8(3-2sqrt2) ~ 1.373`, and the value is now
> known to be exactly a block knapsack, which settles it for all `n <= 8`,
> `m <= 8`. See [`multi_vertex_blocks.md`](multi_vertex_blocks.md).

## 1. The construction (bouquet form)

Fix `3 <= r <= m` and set `q = m + 1 - r >= 1`. A **`K_r`-block** is a clique
on `r` vertices with every edge at multiplicity `q`, which is exactly the
thesis's own "thickened complete graph", applied locally to `r` vertices rather
than to all of `n`.

**Bouquet.** Take `k` copies of `K_r` that all share ONE common vertex and are
otherwise disjoint, and attach any leftover vertices as a pendant path at
multiplicity `m-1`. Because the shared vertex is reused by every block,

```
k  may be as large as  floor((n-1)/(r-1)).
```

*Range note.* `r <= m`, not `r <= m+1`, so that `q >= 1` and every block edge is
actually present. At `r = m+1` we would get `q = 0`, the blocks would carry no
edges, and the graph would fall into isolated vertices, breaking the
connectivity that the count `|E| = n-1+rank` assumes. The formula survives that
degeneracy by an algebraic accident but the proof does not. Nothing is lost: a
positive gain needs `r <= m-2` anyway.

*Superseded variant.* An earlier version of this note used disjoint blocks
joined by single **bridge edges**. That fits only `floor(n/r)` blocks, because
each bridge spends a whole vertex on the join and nothing else, and it is
strictly dominated: at `m=10, r=6, n=11` the bouquet carries 150 against the
chain's 120. The per-block gain is identical in the two; only the number of
blocks that fit changes. Kept here because the thesis's git history refers to
the chain form.

## 2. Exact multiplicity count

With `gain(r, m) := (r-1)(r-2)(m-1-r)/2` (an integer, since `(r-1)(r-2)` is
even), the total multiplicity is exactly

```
K(n, m, r, k) = (m-1)(n-1) + k * gain(r, m),      k <= floor((n-1)/(r-1)).
```

**Derivation.** By `lem:multi-vertex-split`, `kappa_G(u,v) = mu(u,v) + pi(u,v)`
splits cleanly, so on a fixed connected simple graph `G_0` the maximum total
multiplicity is `(m-1)|E(G_0)| - sum_e pi(e)`, attained by setting
`mu = m-1-pi` on every edge. With `|E(G_0)| = n - 1 + rank(G_0)` this is
`(m-1)(n-1) + (m-1)rank(G_0) - sum_e pi(e)`.

Only the `k` blocks contribute: pendant edges are bridges, so they have
`pi = 0` and lie in no cycle. Each `K_r` has rank `(r-1)(r-2)/2`, and each of
its `C(r,2)` edges has `pi = r-2` exactly (see section 3), so
`sum_e pi(e) = k * C(r,2) * (r-2)`. Substituting,

```
(m-1)(n-1) + (m-1)k(r-1)(r-2)/2 - k*r(r-1)(r-2)/2
  = (m-1)(n-1) + k(r-1)(r-2)[(m-1) - r]/2
  = (m-1)(n-1) + k*gain(r,m).
```

## 3. Feasibility, proved by hand

**Inside a block.** For an edge `uv` of a block, `K_r` minus `uv` joins `u,v`
through each of the other `r-2` block vertices, giving `r-2` pairwise
internally-disjoint two-step routes, and by Menger no more, since those same
`r-2` vertices form a cut of that size. No route of length `>= 2` can leave the
block and return: the only way out is the shared vertex, and a simple path
cannot pass through it twice. So `pi(u,v) = r-2` exactly and
`kappa_G(u,v) = q + (r-2) = (m+1-r) + (r-2) = m-1`, exactly at the cap and
never over.

**Everything else.** For `u, v` in different blocks the shared vertex alone
separates them, and for a pair touching the pendant path a single path vertex
does, so `kappa_G(u,v) <= 1`, far below the cap. The binding constraint is
therefore always inside a block, which both computational checks confirm: the
reported worst pair is always a block edge.

## 4. Why it refutes the conjecture

At `r = 3`, `gain(3,m) = m-4`. That is `0` at `m = 4`, consistent with the
thesis's exhaustive table finding no counterexample there, and strictly
positive for every `m >= 5`. So a single triangle glued onto a thickened tree
already beats `(m-1)(n-1)`, for every `m >= 5` and every `n >= 3`. Taking `k`
maximal multiplies the excess by `floor((n-1)/2)`, so the gap grows linearly
in `n`.

Smallest hand-checkable witness: `m=5, n=7` (the first size the conjecture
covered). A triangle at multiplicity 3 plus a four-edge pendant path at
multiplicity 4 gives `3*3 + 4*4 = 25` against the conjectured 24.

## 5. Growth rate: Theta(m^2), not Theta(m)

The gain per vertex used is `gain(r,m)/(r-1)`, which as a continuous function
peaks near `r ~ (m+1)/2` at `Theta(m^2)`. Exact integer optima
(`scripts/multi_vertex_clique_check.py`):

| m  | best r | gain per block | gain rate per vertex |
|----|--------|----------------|----------------------|
| 5  | 3      | 1              | 0.33                 |
| 10 | 6      | 30             | 5.00                 |
| 20 | 11     | 360            | 32.73                |
| 30 | 16     | 1365           | 85.31                |
| 50 | 26     | 6900           | 265.38               |

So `K_m^multi(n)/n -> (m-1) + Theta(m^2)`, a different order in `m` from the
withdrawn conjecture.

## 6. What is open (the bouquet is NOT optimal)

The exhaustive branch and bound, stopped by its time limit rather than
finishing, found a feasible multigraph with **28** at `m=5, n=7`, where the
bouquet gives **27** and the tree gives 24. So a better construction exists and
has not been identified. Mixed block sizes, several shared vertices, or a
different topology entirely are all still open, and no upper bound has been
attempted. What sections 1 to 5 establish is a lower bound of the right order
in both `n` and `m`, not the extremal number.

## Verification

`scripts/multi_vertex_clique_check.py` builds the bouquet, confirms the exact
formula, and checks feasibility **two independent ways**: the thesis program's
own `exceeds_bound(..., parallel_routes=True)`, and a from-scratch max-flow on
a hand-built vertex-split network via `networkx`, sharing no code with the
checker being tested. Both agree exactly on every case.

A third, fully independent confirmation arrived from a different direction: the
incidence-graph search in [`hyper_vertex_m4.md`](hyper_vertex_m4.md), run at
`r = 2`, rediscovers this construction without being told to look for it, since
`r = 2` of that problem *is* this problem.

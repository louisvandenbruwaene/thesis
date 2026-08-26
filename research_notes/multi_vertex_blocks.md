# The multigraph vertex problem is a block problem

**Status: PROVED and VERIFIED. In the thesis as `lem:multi-vertex-objective`,
`thm:multi-vertex-blocks`, `thm:multi-vertex-bipartite`, `tab:multi-vertex-exact`
(section A.9.1).** This note records the derivation, the numbers, and what is
still open.

Script: `scripts/multi_vertex_blocks.py` (needs nauty's `geng` and networkx;
cross-checks against the thesis program's own exhaustive routine).

Supersedes nothing. `thm:clique-chain-vertex` stays true, it is simply not the
best construction and, as it turns out, not the right shape either.

## 0. What was open

`sec:multi-vertex-standard` had a lower bound (a bouquet of thickened cliques,
rate `(1/8)m^2` per vertex), an upper bound (`< 2(m-1)^2 n`, rate `2m^2`), a gap
of a factor 16, and no idea what an extremiser looks like. The exact value was
open. The recorded evidence was that at `m=5, n=7` the bouquet gives 27 while an
unfinished search had found 28.

TASKS.md said to attack the first inequality of `prop:multi-vertex-upper`,
"it charges every edge the full `m-1` and throws away the `-sum(pi)` correction
entirely". Recovering that correction exactly is what starts this off.

## 1. The objective in closed form

`lem:multi-vertex-split` gives `kappa_G = mu + pi`, so the best multigraph over a
fixed simple `G0` sets `mu = m-1-pi` on every edge. The section already said
that. One step further: on an **edge**, `kappa_{G0}(u,v) = 1 + pi(u,v)`, because
the routes of `G0` between adjacent vertices are the edge plus the routes of
length at least two. So `m-1-pi = m - kappa_{G0}`, and

    K_m(n) = max { W_m(G0) : G0 simple on n vertices, kappa^max(G0) <= m-1 },
    W_m(G0) = sum over edges uv of ( m - kappa_{G0}(u,v) ).

This is an **equality**, not a bound. Two things to check and both hold: `G0` is
itself feasible for the simple vertex problem (already the middle step of
`prop:multi-vertex-upper`), and the chosen multiplicities are all `>= 1`, so no
edge silently vanishes and the underlying graph really is `G0`
(`kappa_{G0} <= m-1` on an edge gives `pi <= m-2`, hence `mu >= 1`).

## 2. The objective is additive over blocks

`W_m` is a sum of **local** terms, and locality is exactly what blocks control.
If `u,v` are adjacent they lie in one block `B`, and no `u`-`v` path leaves `B`:
it would have to leave through a cut vertex and come back through the same one.
So `kappa_{G0}(u,v) = kappa_B(u,v)`, every edge lies in exactly one block, and

    W_m(G0) = sum over blocks B of W_m(B).

Each block inherits feasibility. Block sizes satisfy `sum (b_i - 1) <= n-1`.
Conversely any multiset of blocks is realised by hanging them all off **one
shared vertex** (pairs split between two blocks are separated by it, so their
kappa is at most 1). Hence, with `g_m(b)` the best a single 2-connected block
(or single edge) on `b` vertices scores,

    K_m(n) = max { sum_i g_m(b_i) : b_i >= 2, sum_i (b_i - 1) <= n-1 },

a knapsack. The search space stops being "all feasible multigraphs on n
vertices" and becomes "2-connected simple graphs on b <= n vertices", which
`geng -C` enumerates directly.

## 3. Exact values

Sweeping all 2-connected graphs on `b <= 8` vertices (1, 1, 3, 10, 56, 468,
7123) and solving the knapsack:

| m\n | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|
| 2 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| 3 | 2 | 4 | 6 | 8 | 10 | 12 | 14 |
| 4 | 3 | 6 | 9 | 12 | 15 | 18 | 21 |
| 5 | 4 | 9 | 14 | 19 | 24 | **29** | 34 |
| 6 | 5 | 12 | 19 | 26 | 33 | 40 | 47 |
| 7 | 6 | 15 | 24 | 33 | 42 | 52 | 62 |
| 8 | 7 | 18 | 30 | 42 | 54 | 66 | 79 |

Cross-checked against the thesis program's own exhaustive
`max_multigraph_vertex_standard`, which shares no reasoning with the block
argument. It **proved** 23 of these cells within its time limit, namely every
`(m,n)` with `m=2` and `n<=7`, `m=3` and `n<=6`, and `m in {4,5,6}` with `n<=5`,
and all 23 agree exactly. The five that hit the cap returned lower bounds, all
consistent: `(3,7)->12`, `(4,6)->15`, `(4,7)->18`, `(5,6)->24` all match, and
`(5,7)->27` sits below the knapsack's 29, which is the expected behaviour of an
unfinished branch and bound rather than a disagreement.

**`K_5^multi(7) = 29`**, not 27 and not 28. The bouquet was 2 short and the
unfinished search 1 short. The witness was rebuilt as an explicit multigraph and
confirmed feasible both by the thesis program's `exceeds_bound(...,
parallel_routes=True)` and by an independent networkx vertex-split max-flow.

A clean split in the knapsack, worth stating:

- `m <= 3`: the **thickened tree** wins, every block a single edge.
- `m = 4`: tie, every split of the vertices scores the same.
- `m >= 5` and `3 <= n <= 8`: a **single 2-connected block** strictly beats
  every split in the computed table. At `n=2` the single-edge block and the
  thickened tree are the same object. So the bouquet is a construction, not
  the shape of the answer.

## 4. The blocks are bipartite-like, not complete

Read off the winners: `m=5,n=6` is exactly `K_{2,4}`; `m=6,n=7` is exactly
`K_{2,5}`; `m=7` and `m=8` at `n=7` are `K_{3,4}` plus two edges inside the
smaller side; the 29-witness at `m=5,n=7` is `K_{2,4}` with one further edge
subdivided onto it. Unbalanced bipartite, sometimes decorated.

**Thickened `K_{s,t}`** (`1 <= s <= t <= m-1`, multiplicity `m-s` on every edge)
is feasible with total `st(m-s)` on `s+t` vertices. The connectivities:
`kappa = t` inside the `s`-side, `= s` inside the `t`-side, and `= s` on an edge
(delete `uv`; both `T\{v}` and `S\{u}` separate, and the `s-1` routes
`u, v_i, u_i, v` attain it). As a bouquet the rate per vertex is
`st(m-s)/(s+t-1)`.

Optimising with `t = m-1` and `s = alpha*m`, the rate is
`alpha(1-alpha)/(1+alpha) * m^2 + O(m)`, maximised at `alpha = sqrt(2)-1`, value
`3-2sqrt2 ~ 0.1716`, against the clique bouquet's `1/8 = 0.125`.

    improvement factor  8(3-2sqrt2) = 24-16sqrt2 ~ 1.3726
    gap to the upper bound falls from 16 to 2/(3-2sqrt2) = 6+4sqrt2 ~ 11.66

The trade-off is visible in the formula: a larger `s` buys `st` edges and costs
route capacity `m-s` on each. The clique is the degenerate case where the two
sides are forced equal to each other and to the whole block, and letting them
differ is the entire gain. The optimum is lopsided: one side at the ceiling
`m-1`, the other at about `0.41 m`.

## What is still open

- The constant, between `3-2sqrt2` and `2`. The **upper** bound is now the side
  to attack: it still charges every edge the full `m-1`. With the closed form of
  section 1 the honest target is a bound on `W_m(B)` for a 2-connected feasible
  `B`, i.e. on `sum (m - kappa)` rather than on `|E| * (m-1)`.
- Whether `K_{s,t}` plus edges inside the small side is the true block family.
  The `m=7,8` cells at `n=7` say the extras help; nothing says by how much in
  general.
- Whether `g_m(b)/(b-1)` is eventually constant in `b` for fixed `m`. It is
  still increasing at `b=8` in every row, so the exact values above do **not**
  extrapolate, and larger `n` needs larger blocks enumerated, not the same ones
  repeated.

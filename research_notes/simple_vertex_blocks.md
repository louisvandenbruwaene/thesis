# The 1974 problem as a block problem, and why computation cannot see it

**Status: the reduction is PROVED; the degeneracy question is OPEN with
evidence.** In the thesis as `thm:simple-vertex-blocks` and
`rem:vertex-degeneracy` (app_proofs.tex, section A.2.1).

Scripts: `scripts/simple_vertex_blocks.py` (block table via nauty `geng`),
`scripts/vertex_min_degree.py` (the degeneracy search),
`scripts/st_construction.py` (rebuilds and verifies the Sorensen-Thomassen
witness).

## 0. State of the art, checked against the primary source

`k_m(n)` = largest edge count of a simple graph on `n` vertices with
`kappa^max <= m-1` (this thesis's AVOIDING convention; the Erdos Problems
database uses the FORCING convention, one larger).

- `m <= 4`: `k_m(n) = floor(m(n-1)/2)` (Bartfai, Bollobas, Leonard).
- `m = 5`: `k_5(n) = floor(8n/3) - 4` for `n >= 6`, `n != 7, 12` (Sorensen-
  Thomassen; the thesis already corrected the database's range and constant
  from the paper).
- `m >= 6`: OPEN. Two facts, both read off the primary source (JCTB 17(2),
  p.144), not just the database:
  - Bollobas and Erdos conjectured `n` copies of `K_m` sharing one vertex are
    optimal, i.e. `c_m := lim k_m(n)/(n-1) = m/2`. **Mader disproved it for
    every `m >= 6`**: `k_m(n) - mn/2` is unbounded.
  - **Sorensen-Thomassen lower bound**: `c_m >= (m(m-1)-2)/(2m-3)`, which is
    `m/2 + 1/4 + O(1/m)`.
- The only general UPPER bound is `k_m(n) < 2(m-1)n`, from Mader's density
  theorem via the weak consequence that a feasible graph has no `m`-connected
  subgraph. So the rate is pinned only to within a factor of about **four**.

## 1. The block reduction (proved)

Adjacent `u,v` share a block and no `u-v` path leaves it, so
`kappa_G(u,v) = kappa_B(u,v)`; every edge is in exactly one block; block sizes
satisfy `sum (b_i - 1) <= n-1`; and any multiset of blocks is realised by a
bouquet at one shared vertex. Hence, with `h_m(b)` the best 2-connected block,

    k_m(n) = max { sum_i h_m(b_i) : b_i >= 2, sum_i (b_i - 1) <= n-1 },

so `k_m` is superadditive and, by Fekete, `c_m = sup_b h_m(b)/(b-1)`.

Three checks that the reformulation says something:

- **`m = 3` falls out.** A block with `kappa^max <= 2` is an edge or a cycle,
  so `h_3(b) = b` for `b >= 3`, the rate `b/(b-1)` peaks at `b = 3`, and the
  knapsack packs triangles: `k_3(n) = floor(3(n-1)/2)`. Correct.
- **`m = 4` falls out.** `h_4(b) = 2(b-1)` for `b >= 4` (attained by `K_4`), so
  `c_4 = 2` and `k_4(n) = 2(n-1)`. Correct.
- **The Bollobas-Erdos conjecture is exactly the case `b = m`**:
  `h_m(m) = C(m,2)`, rate `m/2`. Their conjecture says no block beats `K_m`.

## 2. Why exhaustive search sees nothing

Computed `h_m(b)` for all 2-connected graphs on `b <= 9` (1, 1, 3, 10, 56, 468,
7123, 194066 of them) and every `m <= 8`: **the rate `m/2` is attained and never
exceeded.** Since a bouquet's rate is a weighted average of its blocks' rates, a
counterexample needs one block beating `m/2` alone, hence at least 10 vertices.

The reason is structural. The Sorensen-Thomassen witness is built by a
recursion: `G^0 = K_m - e`, and `G^j` glues two fresh copies of `G^0` to
`G^{j-1}` by identifying one vertex of each with one of the next, **the three
identifications arranged in a CYCLE**. A cyclic gluing has no cut vertex, so
`G^j` is 2-connected: it is a SINGLE block, of size `m + (2m-3)j`. The block
reduction sees it as one indivisible object and gets no purchase.

What `G^j` does have is 2-cuts (each copy is separated by its pair of
identification vertices). **So the refinement the reformulation asks for is the
triconnected (Tutte/SPQR) decomposition, along 2-cuts rather than cut
vertices** -- the same machinery `lem:incidence-rank` already uses in this
thesis on incidence graphs. That is the concrete next step.

Sizes, which explain the gap between theory and computation: the recursion beats
rate `m/2` only for `j > 2/(m-4)`, so the smallest member outrunning a bouquet of
`K_m`s has **26 vertices at `m=5`, 24 at `m=6`, 18 at `m=7`** -- against the 9
that exhaustion reaches.

VERIFIED (`st_construction.py`): rebuilt `G^j` for `m = 5,6,7` and `j <= 3`.
Vertex and edge counts match `m + (2m-3)j` and `(m(m-1)-2)(j + 1/2)` exactly,
every member is 2-connected, and every member has `kappa^max = m-1` exactly, so
each is feasible and contains no `m`-rail.

## 3. The degeneracy question (open, with evidence)

The upper bound `2(m-1)n` uses only "no `m`-connected subgraph". Feasibility says
much more, e.g. adjacent vertices have at most `m-2` common neighbours.

> **Question.** Does every feasible graph have a vertex of degree `<= m-1`?

Feasibility passes to induced subgraphs, so a YES makes feasible graphs
`(m-1)`-degenerate and gives

    k_m(n) <= (m-1)n - C(m,2),

**halving the constant in the only general upper bound known.**

- TRUE at `m = 3`, classically: min degree `>= 3` forces a `K_4` subdivision,
  whose branch vertices carry 3 internally disjoint paths.
- Exhaustive search over ALL graphs with min degree `>= m` finds no feasible one
  for `m <= 6` and `n <= 10` (the `m=4, n=10` row alone is 1249972 graphs).

Stated as a question, not a conjecture: the sizes reached are well below the
26-vertex scale at which the Bollobas-Erdos conjecture itself first fails, so
this evidence is weaker than it looks.

## What to try next

1. The triconnected refinement of section 2. This is the step the reduction
   actually points at, and the SPQR machinery is already in the thesis.
2. The degeneracy question of section 3, which is the cheapest available factor
   of two on the upper bound.
3. Push `h_m(b)` to `b = 10` (9.7M 2-connected graphs). Still below the
   crossing sizes, so a negative result there would be expected, not
   informative.

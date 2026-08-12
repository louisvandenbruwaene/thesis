# The two-step budget, and three results it unlocks

**Status: PROVED and VERIFIED. All four statements are now in the thesis**
(`lem:two-step-budget`, `thm:dir-vertex-linear-error`, `thm:dir-hyper-constant`,
`prop:multi-vertex-upper`). This note records the derivation and the dead ends,
which the thesis text compresses.

Script: `scripts/two_step_budget_check.py` (standard library only, own
max-flow, no dependence on the thesis program).

## 0. The observation

`prop:dir-arc-stability` and `thm:dir-arc-linear-error` use feasibility exactly
once, in Step 1, to cap one explicit family of routes. Everything afterwards is
arithmetic on in-degrees and out-degrees. So the real theorem is about digraphs
satisfying that cap, whatever supplies it:

> **Lemma (counting core).** If every ordered pair of a simple digraph `D`
> satisfies `1_{(u,v) in A} + p_2(u,v) <= C`, then
> `|A(D)| <= floor(n^2/4) + 4C(n-1)`.

The only extra check is that the hypothesis passes to induced subdigraphs, which
it does trivially: deleting a vertex removes arcs and midpoints and adds
neither. Three different arguments supply the cap.

## 1. The directed vertex problem (easy, and previously missed)

The family Step 1 exhibits is the direct arc plus the two-step detours. Their
interiors are the empty set and distinct singletons, so the family is
**internally vertex-disjoint**, not merely arc-disjoint. Hence `C = m-1` under
`kappa^max <= m-1` as well, giving

    k_m^dir(n) <= floor(n^2/4) + 4(m-1)(n-1),   so  k_m^dir(n) = n^2/4 + Theta_m(n).

This is legitimate despite Whitney running the wrong way, and it is worth being
precise about why, because the thesis is repeatedly careful here and was right
to be. An arc *upper bound* says nothing about the larger vertex-feasible
family. What transfers is not the bound but the *construction*: a family of
routes that happens to be disjoint in the stronger sense can be measured against
the stronger parameter. Nowhere does the argument use the arc value.

The thesis had recorded this row as untouched by the arc case, which was true of
the bound and, it turns out, not true of the method.

## 2. The directed hypergraph constant (the real one)

The thesis stated `conj:dir-hyper-constant` and named the obstacle: a hyperedge
carries `r-1` heads, so two-step routes through different midpoints may enter
through the same hyperedge and are not edge-disjoint. That obstacle is real. The
resolution is not to remove it but to **pay it and check where the payment
lands**.

Let `R` be the one-step shadow (arc `u -> v` when some hyperedge has tail `u` and
head `v`) and `cod(u,v)` the number of hyperedges realising it.

- **Step 1.** Those `cod(u,v)` hyperedges are one-step routes, pairwise
  hyperedge-disjoint and with empty interiors, so `cod(u,v) <= kappa(u,v) <= m-1`.
  Counting each hyperedge once per head, `(r-1)|E| = sum cod <= (m-1)|A(R)|`.
  This is `prop:dir-hyper-first`'s count stopped one step early. That proof then
  used `|A(R)| <= n(n-1)`, which is exactly where its factor of four was lost.
- **Step 2.** Fix `(u,v)` and let `T` be `{v}` (if `(u,v)` is a shadow arc)
  together with the `p_2(u,v)` midpoints. Every `t` in `T` is a head of some
  hyperedge with tail `u`. In the bipartite graph joining targets to those
  hyperedges, a maximum matching `M` satisfies `|M| >= |T|/(r-1)`: an unmatched
  target has all its hyperedges matched (else `M` extends), so every target lies
  in a hyperedge used by `M`, and each holds at most `r-1` targets. Reading `M`
  as routes gives a pairwise hyperedge-disjoint, internally vertex-disjoint
  family, so `|T| <= (r-1) kappa(u,v) <= (r-1)(m-1)`. So `R` is
  `(r-1)(m-1)`-budgeted.
- **Step 3.** The lemma gives `|A(R)| <= floor(n^2/4) + 4(r-1)(m-1)(n-1)`, and
  substituting into Step 1,

      |E| <= (m-1)/(r-1) * floor(n^2/4) + 4(m-1)^2 (n-1).

**Why it works.** Two factors of `r-1` appear and they are unrelated. The one
lost in the packing (Step 2) enters only the *linear* error term of the lemma,
never the `n^2/4`. The one gained in the codegree count (Step 1) divides the
leading term. Only one of them is paid where the constant lives.

Because Step 1 and Step 2 both hold against `kappa`, the theorem covers the
edge- and vertex-disjoint separations at once, so it settles the leading
constant for two of the twelve variants.

**Not covered: the general orientation model.** The single tail is used twice,
for the entering and the leaving hyperedges. With several tails allowed, two
routes may *leave* through one shared hyperedge, and Step 2 needs a second
matching on that side, on a family whose conflicts run both ways at once. A
greedy independent-set argument in the conflict graph looks like it would give
`C = O(r)(m-1)`, which would be enough, but this was not worked out or checked
and is not claimed.

## 3. The multigraph vertex upper bound (repairing an overclaim)

`sec:multi-vertex-standard` said the bouquet of `thm:clique-chain-vertex` was
"a lower bound of the right order in both `n` and `m`", and wrote
`K_m^multi(n)/n -> (m-1) + Theta(m^2)`. Neither was supported: there was no
upper bound at all, so "right order" and the limit were both unearned.

The missing bound is short and does not go through cycle rank, which is what
made it hard to see. By `lem:multi-vertex-split`, `kappa = mu + pi`, so:

- every multiplicity is at most `m-1`, giving `total <= (m-1)|E(G_0)|`;
- the underlying simple graph `G_0` is itself feasible for the **simple** vertex
  problem, since `kappa_{G_0}(u,v) = 1 + pi <= mu + pi <= m-1` on edges and
  `= pi <= m-1` off them. So `|E(G_0)| <= k_m(n)`.
- `k_m(n) < 2(m-1)n` by Mader's density theorem (average degree `>= 4k` forces a
  `(k+1)`-connected subgraph, in which every pair has `kappa >= k+1`).

So `K_m^multi(n) <= (m-1)k_m(n) < 2(m-1)^2 n`, and with the bouquet's
`(1/8 + o(1))m^2 n` the order `Theta(m^2 n)` is genuine. The constants are 16
apart. The first inequality is the interesting one and is tight at `m = 2`.

## What is still open

- The exact value of `K_m^multi(n)` (the `28` against the bouquet's `27` at
  `m=5, n=7` still stands), and the constant factor of 16.
- The exact directed hypergraph value at finite `n`, and whether the general
  orientation model shares the leading constant.
- The linear coefficient in both directed simple problems, arc and vertex.
- Everything the two-step budget cannot see. It is a *local* count, blind to
  anything beyond radius two, which is why it fixes leading terms and never
  linear ones. `rem:case2-tight` is the sharp form of that limitation.

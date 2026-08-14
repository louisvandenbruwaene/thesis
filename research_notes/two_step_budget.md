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

**The general orientation model: NOW COVERED (2026-08-14).** This section used
to end by saying the single tail is used twice, for the entering and the leaving
hyperedges, so with several tails two routes may *leave* through one shared
hyperedge (and, from `r >= 4`, one mixed hyperedge may be one target's entrance
and another's exit), leaving Step 2 needing a second matching on a family whose
conflicts run both ways at once. It guessed that a greedy independent set would
give `C = O(r)(m-1)`.

The right move is not a second matching and not a greedy set. It is to stop
*building* a family and take a **maximum** one, then ask what stopped it.

> Let `T` be the targets as above. Consider families of routes indexed by
> distinct targets, one hyperedge for the target `v`, an entrance and an exit for
> a midpoint, all hyperedges distinct. Take a maximum such family `F`, of size
> `M`, serving `S`, using hyperedge set `U`, so `|U| <= 2M` and (interiors empty
> or distinct singletons) `M <= kappa(u,v) <= m-1`.
> Any `t` in `T \ S` with an unused entrance and, if a midpoint, an unused exit
> would extend `F`: the two are distinct because no hyperedge is both an entrance
> and an exit for the same `t` (that would need `t` in its tail set and its head
> set at once). So every entrance of `t` is in `U`, or every exit is, and either
> way **`t` lies on a hyperedge of `U`**:
>
>     T \ S  subset  union over e in U of (T_e u H_e),
>     |T| <= M + sum over U of (|T_e| + |H_e|) = M + r|U| <= (2r+1)M.

Two points. The sides are counted **together**, using `|T_e| + |H_e| = r`
exactly, which is what keeps the constant at `r` and not `2(r-1)`. And the
argument never needs the entering and leaving families to be independent, which
is precisely what the general model denies, so it covers forward, backward and
general at once.

Hence `R` is `(2r+1)(m-1)`-budgeted and the assembly is unchanged:

    |E| <= (m-1)/(r-1) floor(n^2/4) + 4(2r+1)(m-1)^2/(r-1) (n-1).

So the general model shares the leading constant, and the orientation axis
collapses asymptotically. In the thesis as `thm:dir-hyper-general-constant`.

The constant `2r+1` is **not** sharp and is not claimed to be: it comes from the
crude `|U| <= 2M`. Adversarial instances in which every target shares both its
entrance and its exit with another never push `|T|/kappa` above `r-1`, the
forward model's own constant. Nothing rests on the gap, since the whole point of
the budget lemma is that this constant lands in the linear term.

Script: `scripts/general_orientation_check.py` (standard library only, own
max-flow, own model). Checks (i) the budget on random general hypergraphs
against exact `kappa`, (ii) the mechanism `M <= kappa` and the containment
`T \ S subset union of U`, against a brute-force MAXIMUM family rather than a
greedy one, (iii) Step 1 and the assembled bound on grown feasible instances,
and (iv) the deliberate worst cases. Zero violations. Cross-checked against the
thesis program's own `hyper_connectivity` on 300 feasible general hypergraphs
and 5989 ordered pairs, also zero.

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
- The exact directed hypergraph value at finite `n`, for every orientation. (The
  general model's leading constant is settled, see above; what the asymptotics
  cannot see is the finite comparison at `n ~ r`, where general is strictly
  denser.)
- The linear coefficient in both directed simple problems, arc and vertex.
- Everything the two-step budget cannot see. It is a *local* count, blind to
  anything beyond radius two, which is why it fixes leading terms and never
  linear ones. `rem:case2-tight` is the sharp form of that limitation.

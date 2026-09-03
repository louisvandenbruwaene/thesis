# Directed arc problem, m = 3: reduction to a single hypothesis on sources

> **NOT FOR THE THESIS OR THE PROGRAM.** This note is research scratch.
>
> **STATUS 2026-06-30: (H) IS FALSE.** The centrepiece hypothesis (H) is REFUTED
> by an explicit infinite family of extremisers (section 0 below), so this
> reduction does NOT close `conj:dir-arc` and its characterisation claim is wrong.
> Nothing here belongs in the thesis or in `erdos915_unified.py`. The thesis
> already states `conj:dir-arc` as a conjecture with its own backward-arc framing,
> and this refutation does not change any proved thesis content -- keep the thesis
> as it is. The sections below are kept for the record, with (H) now marked FALSE.

**Topic.** Proving the quadratic branch of `conj:dir-arc` for `m = 3`:
`ell_3^dir(n) <= Q(n) := floor((n+1)^2/4)` for `n` in the quadratic regime
(`n >= 9`, where `Q(n) > 3(n-1)`).

**Bottom line (SUPERSEDED).** The original plan reduced the upper bound AND the
extremiser characterisation to one structural hypothesis:

> **(H)** Every `m = 3` extremiser contains a *source adjacent to every
> non-source* (equivalently, its non-source set induces maximum in-degree `<= 1`).

> **(H) is FALSE.** See section 0. So the reduction does not prove the upper bound,
> and the extremisers are NOT only the augmented-bipartite family. The value
> conjecture `ell_3^dir(n) = Q(n)` is UNHARMED (the new family attains `Q(n)` but
> never exceeds it); what is refuted is the characterisation and the (H)-based
> kill of the even case.

Reproduce: `python3 program/scripts/h_counterexample.py` (the refutation),
`characterisation_checks.py` (arc partition, the source lemma, the conditional
bound), `attach_check.py` (the min-degree arithmetic).

---

## 0. (H) IS FALSE: an infinite family of non-augmented-bipartite extremisers

Reproduce: `python3 program/scripts/h_counterexample.py` (verified with a
self-contained max-flow AND the thesis program's `max_edge_connectivity`).

For every odd `n = 2k - 1` with `k >= 5` (so `n >= 9`, the quadratic regime), put
`A = {0,...,k-2}` (size `k-1`), `B = {k-1,...,2k-2}` (size `k`), and take

- the complete layer `A -> B` (every `a -> b`), `(k-1)k` arcs, and
- one head vertex `beta0 in B` pointing to one tail `a0 in A` AND to every other
  vertex of `B`, that is `beta0 -> a0` and `beta0 -> b` for all `b in B\{beta0}`,
  which is `1 + (k-1) = k` more arcs.

Total `(k-1)k + k = k^2 = Q(2k-1)`, and `lambda^max = 2` (FEASIBLE, checked two
independent ways at `n = 9, 11, 13, 15, 17`). The single arc `beta0 -> a0` makes
`a0` a non-source, after which both `a0` and `beta0` point to every other
`B`-vertex, so each such `b` has IN-DEGREE 2 inside `R`. The sources are
`A \ {a0}`, only `sigma = k - 2` of them, and NONE is adjacent to all of `R`
(none reaches `a0` or `beta0`). So **(H) fails in both forms**, at the extremal
arc count `Q(n)`, for every odd `n >= 9`.

Concrete `n = 9` witness (`k = 5`): `A = {0,1,2,3}`, `B = {4,5,6,7,8}`,
`beta0 = 5`, `a0 = 1`, with arcs `{0,1,2,3} x {4,5,6,7,8}` plus `5 -> 1,4,6,7,8`.
The sources are `{0,2,3}`, the non-sources are `R = {1,4,5,6,7,8}`, and the
`R`-vertices `4,6,7,8` each have in-degree 2.

**Consequences.**
- The characterisation "extremisers are exactly the augmented-bipartite family"
  is FALSE: this family is a second, structurally distinct extremal family
  (one fewer source, a head that fans out). `directed_arc_m3_extremisers.md`'s
  completeness claim and its attachment refutation both rested on (H) and are
  therefore void as a route to the even case.
- The (H)-conditional bound 2.3 is still a correct CONDITIONAL (these graphs
  simply violate its hypothesis: `a = k^2 > (n-sigma)(sigma+1) = k^2 - 1` here),
  as are the complete-layer proposition 2.4.3 and the summed inequality 2.5.1.
  What collapses is the claim that (H)'s hypothesis holds on extremisers.
- The VALUE upper bound for odd `n >= 11` via the min-degree deletion of section 1
  does NOT use (H) and is unaffected. The even case, which needed the
  characterisation, is again open.

Everything from section 1 on is kept for the record, now read in the light of
section 0.

---

## 1. The min-degree-deletion reduction (PROVED, modulo the IH and seam)

The thesis proves the `m = 2` value (`thm:dir-arc-m2-exact`) by deleting a
minimum-degree vertex and inducting. Apply the **same** engine at `m = 3`. Let
`D` be feasible (`lambda^max <= 2`) on `n` vertices with `a` arcs; choose `v0` of
minimum total degree, so `d(v0) <= 2a/n`; `D - v0` is feasible on `n - 1`
vertices, so `a - d(v0) <= ell_3^dir(n-1)`. Hence
`a <= (n/(n-2)) * ell_3^dir(n-1)`.

Using the true bound `ell_3^dir(n-1) = max(3(n-2), Q(n-1))`, the overshoot
`floor(n/(n-2) ell(n-1)) - Q(n)` is (script `attach_check.py`):

| n  | Q(n) | overshoot |
|----|------|-----------|
| 9  | 25   | +2 (crossover seam: `ell(8)=21` is linear) |
| 10 | 30   | +1 |
| 11 | 36   | **+0** |
| 12 | 42   | +1 |
| 13 | 49   | **+0** |
| 14 | 56   | +1 |
| 15 | 64   | **+0** |
| 16 | 72   | +1 |
| 17 | 81   | **+0** |

So:
- **Odd `n >= 11`** closes for free by integrality, given the bound at `n - 1`.
- **Even `n >= 10`** is off by exactly `+1`.
- **`n = 9`** is off by `+2` (the seam).

**The whole `m = 3` quadratic upper bound reduces to killing one `+1` of slack at
even `n`, plus the seam bases `n = 9, 10`.** Structurally this mirrors the
directed-*multigraph* `thm:odd-step` + `lem:attachment` in the thesis: odd levels
close from even, and a slack is removed by an extremal-structure argument.

### Forced structure of the `+1` even case (PROVED)
If `a = Q(2k) + 1 = k^2 + k + 1` then (script `attach_check.py`): every vertex
has degree `>= k + 1`; `D` is `(k+1)`-regular up to total degree-excess exactly
`2`; and every degree-`(k+1)` vertex deletes to an **exact extremiser on `2k-1`
vertices** (`k^2` arcs). The residual task is to show no such `D` exists -- killed
by the attachment refutation (see `directed_arc_m3_extremisers.md`) *given* the
extremiser characterisation, which is where (H) enters.

---

## 2. The conditional structure theorem (PROVED)

This is the load-bearing reduction. Let `D` be feasible at `m = 3`, with source
set `S` (`d^- = 0`), `sigma = |S|`, and non-sources `R = V \ S`.

### 2.1 Arc partition (PROVED)
Sources have in-degree `0`, so there is **no arc into `S`** (no `S -> S`, no
`R -> S`). Every arc is `S -> R` or internal to `R`:
`a = e(S,R) + e(R)`, with `e(S,R) <= sigma(n - sigma)`.
(Sanity: `0` arcs into a source over 300 random feasible digraphs.)

### 2.2 Source-neighbourhood Lemma (PROVED)
> **Lemma.** In any digraph with `lambda^max <= 2`, for a source `s` the
> subdigraph induced on `N^+(s)` has maximum in-degree `<= 1`.

*Proof.* If distinct `x_1, x_2 in N^+(s)\{w}` both point to `w in N^+(s)`, then
`s->w`, `s->x_1->w`, `s->x_2->w` are three arc-disjoint `s`-`w` routes (distinct
first arcs, distinct second arcs), contradicting `lambda(s,w) <= 2`. ∎

Verified: `0` violations over 300 random feasible digraphs
(`characterisation_checks.py`). Consequently a **universal source** (one adjacent
to all of `R`) forces `R` to have internal maximum in-degree `<= 1`.

### 2.3 Conditional bound (PROVED)
> **Theorem.** If `R` induces maximum in-degree `<= 1` (e.g. if `D` has a
> universal source), then `e(R) <= |R| = n - sigma`, so
> `a <= sigma(n-sigma) + (n - sigma) = (n - sigma)(sigma + 1) <= Q(n)`,
> in **both** parities. Equality forces a complete `S -> R` layer and `R` a
> fixed-point-free permutation, i.e. the augmented-bipartite family
> (`directed_arc_m3_extremisers.md`).

*Proof.* The count is immediate from 2.1 and the hypothesis. The maximum of
`(n-sigma)(sigma+1)` over `sigma` is `Q(n)`, attained at `sigma = (n-1)/2` for
odd `n = 2k-1` (value `k^2`) and at `sigma in {k-1, k}` for even `n = 2k` (value
`k^2 + k`). Verified for `n = 7..19` (`characterisation_checks.py`). Equality
needs both `e(S,R) = sigma(n-sigma)` (complete layer) and `e(R) = n - sigma`
(every `R`-vertex internal in-degree exactly `1`). ∎

**So (H) implies the quadratic upper bound for all `n` (both parities) AND pins
the extremisers to the augmented-bipartite family.**

---

## 2.4 Self-similarity and the complete-layer case (PROVED, 2026-06-30)

Two unconditional facts that locate (H) precisely. Reproduce with
`program/scripts/lemma_check.py` (partition, the lemma, the proposition)
and the overshoot table below (`probe_overshoot.py`).

### 2.4.1 Self-similarity lemma (PROVED)
> **Lemma (L).** In any feasible `D`, the non-source set `R` induces a feasible
> sub-digraph: `lambda^max(D[R]) <= 2`. Hence `e(R) <= ell_3^dir(|R|)`.

*Proof.* A source has in-degree `0`, so it can never be an internal vertex of a
directed path (an internal vertex carries an incoming path arc). Every directed
`u`-`v` path with `u, v in R` therefore stays inside `R`, so
`lambda_D(u, v) = lambda_{D[R]}(u, v)` for all `u, v in R`. Feasibility of `D`
restricts to `D[R]`, and the arc bound is the definition of `ell_3^dir`. ∎
Verified: `lambda(D[R]) <= 2` on the augmented-bipartite family `k = 3..8` and on
many random maximal feasible digraphs (`lemma_check.py`, all OK).

### 2.4.2 The recursion alone is not enough
Lemma (L) yields the recursion
`ell_3^dir(n) <= max_{sigma >= 1} [ sigma(n - sigma) + ell_3^dir(n - sigma) ]`
(taking `sigma = |S| >= 1`, with the source-free case handled separately). It
OVERSHOOTS `Q(n)`:

| n | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|----|----|----|----|----|----|
| recursion-only bound | 33 | 39 | 46 | 53 | 61 | 70 | 80 |
| over `Q(n)` | +8 | +9 | +10 | +11 | +12 | +14 | +16 |

The slack comes from the argmax choosing a SMALL dense inner `R` (a linear-regime
extremiser) underneath a near-complete source layer. Feasibility forbids exactly
that pairing, and that is what the source-neighbourhood coupling (2.2) controls.
So the recursion and the coupling have to be used together. (H) is the assertion
that the coupling wins.

### 2.4.3 The complete-layer case (PROVED)
> **Proposition.** If a feasible `D` has at least one source and a COMPLETE source
> layer (every source points to every non-source), then (H) holds, hence
> `a = sigma*rho + e(R) <= rho(sigma + 1) <= Q(n)`.

*Proof.* Suppose some `w in R` had two `R`-in-neighbours `x, x'`. Take any source
`s`. The complete layer gives `s -> w`, `s -> x`, `s -> x'`, so `w` has in-degree
`2` inside `N^+(s)`, contradicting the source-neighbourhood Lemma (2.2). Hence `R`
has maximum in-degree `<= 1` (that is (H)), so `e(R) <= rho` and
`a <= sigma*rho + rho = rho(sigma + 1) <= max_sigma (n - sigma)(sigma + 1) = Q(n)`. ∎

The augmented-bipartite extremisers have a complete layer, so this recovers their
optimality with no exchange. The open case is an extremiser whose source layer has
GAPS: a missing arc `s -> x` could in principle pay for an extra `R`-arc into some
`w`. Showing the gaps can never overpay (`e(R) - rho <= sigma*rho - e(S, R)`) is
exactly the full bound `a <= rho(sigma + 1)`, so it is equivalent to (H)'s core,
not a way around it.

## 2.5 The summed coupling, and why counting alone cannot work (2026-06-30)

Reproduce with `program/scripts/coupling_inequality.py`.

### 2.5.1 The summed-coupling inequality (PROVED)
Summing the source-neighbourhood Lemma (2.2) over all sources gives one global
inequality.
> **(star)** `sum_{R-arcs (x,y)} c(x,y) <= e(S, R)`, where
> `c(x,y) = #{ s in S : s -> x and s -> y }` is the number of common source
> in-neighbours of the endpoints.

*Proof.* For each source `s`, `D[N^+(s)]` has maximum in-degree `<= 1` (2.2), so it
has at most `|N^+(s)|` arcs. An `R`-arc `(x,y)` lies inside `N^+(s)` exactly when
`s -> x` and `s -> y`. Summing `#arcs(N^+(s)) <= |N^+(s)|` over `s` gives the left
side as `sum_{R-arcs} c(x,y)` and the right side as `sum_s |N^+(s)| = e(S,R)`. ∎
In the complete-layer case `c(x,y) = sigma` for every `R`-arc, so (star) becomes
`sigma*e(R) <= sigma*rho`, i.e. `e(R) <= rho`, recovering 2.4.3. Verified: 0
failures over 280 random feasible digraphs.

### 2.5.2 Counting alone cannot prove (H) -- extremality is required (PROVED)
The conditional bound `a <= (n - sigma)(sigma + 1)` is NOT a theorem about all
feasible digraphs: it FAILS, even with `sigma >= 1`, on non-extremal `D` (95 of
280 random feasible digraphs, e.g. `n = 9`, one source, `a = 21 > 16`). The reason
is structural: `sigma` counts only the GLOBAL sources, but `D[R]` can itself be a
dense linear-regime digraph carrying its own internal sources, so a single source
plus a heavy `R` already overshoots `(n-sigma)(sigma+1)` while staying feasible and
below `Q(n)`. Consequently NO inequality of the "sum local constraints over the
whole digraph" type can give (H): any proof must use that `a` is MAXIMAL (an
extremiser), which is exactly why every viable attack on (H) is an exchange or a
deletion argument, never a pure count. This rules out a class of attempts and
re-focuses the work on attack 1 (the exchange) in section 3.

---

## 3. Status and the open residue

- **(H) is FALSE (section 0).** The reduction does not close `conj:dir-arc`. What
  remains correct:
- PROVED (and still true, but they no longer combine into a proof of the bound,
  since (H) does not hold): arc partition; source-neighbourhood Lemma; the
  conditional bound 2.3 and its equality case (as a CONDITIONAL); the min-degree
  reduction (odd from even by integrality); the `+1` forced structure;
  self-similarity Lemma (L) and the complete-layer Proposition (2.4); the
  summed-coupling inequality (star) (2.5.1).
- OPEN, value: the upper bound `ell_3^dir(n) <= Q(n)` for odd `n >= 11` follows
  from the min-degree deletion of section 1 WITHOUT (H), so it survives. The EVEN
  case relied on the characterisation (= (H)) and is open again.
- DEAD as stated: the characterisation "extremisers = augmented-bipartite" and the
  attachment refutation of the even `+1` (`directed_arc_m3_extremisers.md`), both
  of which assumed (H).
- OPEN, finite: seam bases `ell_3^dir(9) = 25`, `ell_3^dir(10) = 30` (certifier /
  Gurobi -- analogue of the thesis's finite `n=7` multigraph facts).
- `m >= 4`: redo the reduction (overshoot pattern differs) and expect the known
  odd-uniqueness hole (`rem:odd-step-roadmap`).

### Where to go now that (H) is dead
1. The right characterisation must include BOTH families (augmented-bipartite and
   the section-0 fan-out family) and probably more. A correct invariant has to be
   satisfied by both: both attain `Q(n)`, both have a complete `A -> B` layer on
   SOME bipartition, both keep `e(R)` small relative to the layer. The clean common
   feature is bipartite-like layering, not "R max in-degree <= 1".
2. For the VALUE alone, the min-degree deletion (section 1) already gives odd
   `n >= 11`; the even case needs a different kill than the (now void) attachment
   argument. The thesis's own backward-arc framing (with `A` = sources, where there
   is no back-arc) may be the more robust route after all.
3. The seam bases via Gurobi are still needed and are independent of all this.

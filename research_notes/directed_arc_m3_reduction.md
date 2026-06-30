# Directed arc problem, m = 3: reduction to a single hypothesis on sources

**Topic.** Proving the quadratic branch of `conj:dir-arc` for `m = 3`:
`ell_3^dir(n) <= Q(n) := floor((n+1)^2/4)` for `n` in the quadratic regime
(`n >= 9`, where `Q(n) > 3(n-1)`).

**Bottom line.** Modulo finitely many seam base cases, this upper bound -- and
the extremiser characterisation -- follow from one concrete structural
hypothesis:

> **(H)** Every `m = 3` extremiser contains a *source adjacent to every
> non-source* (equivalently, its non-source set induces maximum in-degree `<= 1`).

(H) is **OPEN**. Everything reducing to it is **PROVED / VERIFIED** below. This
sidesteps the non-monotone "delete-and-compensate" exchange that stalls the
backward-arc framing of the thesis (ch4, `app_proofs`).

Reproduce: `python3 research_notes/scripts/characterisation_checks.py`
(arc partition, the Lemma, the conditional bound) and `attach_check.py`
(the min-degree arithmetic).

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
`research_notes/scripts/lemma_check.py` (partition, the lemma, the proposition)
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
(taking `sigma = |S| >= 1`; the source-free case is separate). It OVERSHOOTS `Q(n)`:

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

---

## 3. Status and the open residue

- PROVED: arc partition; source-neighbourhood Lemma; conditional bound + equality;
  the min-degree reduction (odd from even by integrality); the `+1` forced
  structure; self-similarity Lemma (L) and the complete-layer Proposition (2.4).
- OPEN, load-bearing: **(H)**. Proving it closes the value and the
  characterisation at one stroke; with the attachment refutation made uniform
  (`directed_arc_m3_extremisers.md`) and the seam bases, it settles `m = 3`.
  2.4 narrows it: the complete-layer case is done, so (H) is now precisely the
  claim that a source layer with GAPS cannot overpay for a denser `R`.
- OPEN, finite: seam bases `ell_3^dir(9) = 25`, `ell_3^dir(10) = 30` (certifier /
  Gurobi -- analogue of the thesis's finite `n=7` multigraph facts).
- `m >= 4`: redo the reduction (overshoot pattern differs) and expect the known
  odd-uniqueness hole (`rem:odd-step-roadmap`).

### Concrete attacks on (H)
1. Exchange argument: show a vertex `w in R` of internal in-degree `>= 2` always
   permits an arc-count-preserving reshuffle toward more sources, so an
   extremiser can be taken with `R` internally max-in-degree `<= 1`.
2. Direct: prove an extremiser has `>= (n-1)/2` sources and that some source is
   universal (the Lemma already controls each source's out-neighbourhood).

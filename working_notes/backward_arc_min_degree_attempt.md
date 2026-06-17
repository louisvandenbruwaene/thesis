# Backward-arc lemma: a min-degree / attachment line of attack

**Status: IN PROGRESS, not a proof.** This note records a fresh angle on the
flagship open problem (turn `conj:dir-arc` into a theorem for `m >= 3`). It is
NOT verified end to end and must NOT enter the thesis text uncommented. All
arithmetic and the small-case structural claims below are mechanically checked
by `working_notes/attach_check.py` (self-contained, no external deps).

Date: 2026-06-17. Author: Claude (Opus), at Louis's request to "go deep" on the
top TASKS.md item.

## The problem and the existing framing

`conj:dir-arc`: for simple digraphs and `m >= 2`,
`ell_m^dir(n) = max( m(n-1), floor((n+m-2)^2/4) )`. The lower bound and the
`m = 2` case are theorems; the linear ("hub") branch upper bound is a theorem
(`thm:directed-upper`). What is open is the **quadratic-branch upper bound for
`m >= 3`**.

The thesis localises the gap as the **backward-arc lemma**: an extremal non-hub
digraph admits a complete `A -> B` partition with no arc from `B` back to `A`,
after which `prop:two-hop-bipartite` gives the bound. The named obstacle
(ch4 / app_proofs, and TASKS.md) is that the natural delete-and-compensate
exchange proving "no back-arc" is **non-monotone** -- a back-arc can manufacture
a third route (the refuted 30-arc counterexample). Two prior attempts
(route-counting; repartitioning, 2026-06-15) stalled on exactly this.

## A different reduction: min-degree deletion (the `m = 2` engine)

`thm:dir-arc-m2-exact` proves the `m = 2` value by **minimum-degree deletion +
induction**: pick `v0` of minimum total degree, so `d(v0) <= 2a/n`; `D - v0` is
feasible on `n-1` vertices, so `a - d(v0) <= ell(n-1)`; hence
`a <= (n/(n-2)) * ell(n-1)`, and integrality closes it against `floor(n^2/4)`.

Apply the **same** engine to `m = 3` in the quadratic regime
(`Q(n) := floor((n+1)^2/4)`, dominant for `n >= 9`). Using the true bound
`ell(n-1) = max(3(n-1), Q(n-1))`, the overshoot `floor(n/(n-2) ell(n-1)) - Q(n)`
is (verified in `attach_check.py`):

| n  | target Q(n) | ell(n-1) | min-deg bound | overshoot |
|----|-------------|----------|---------------|-----------|
| 9  | 25          | 21       | 27            | **+2** (crossover seam) |
| 10 | 30          | 25       | 31            | **+1** |
| 11 | 36          | 30       | 36            | **+0** |
| 12 | 42          | 36       | 43            | **+1** |
| 13 | 49          | 42       | 49            | **+0** |
| 14 | 56          | 49       | 57            | **+1** |
| 15 | 64          | 56       | 64            | **+0** |
| 16 | 72          | 64       | 73            | **+1** |
| 17 | 81          | 72       | 81            | **+0** |

So, for `m = 3`:

- **Odd `n >= 11`: the upper bound closes for free** by integrality, *given* the
  bound at the even predecessor `n-1`.
- **Even `n >= 10`: off by exactly `+1`.**
- **`n = 9`: off by `+2`** -- the crossover seam, where the predecessor value
  `ell(8) = 21` sits on the *linear* branch.

**Net: the entire `m = 3` quadratic upper bound reduces to (i) killing one `+1`
of slack at even `n`, and (ii) finitely many seam base cases near `n = 9`.**
This is structurally identical to the directed-*multigraph* story already in the
thesis (`thm:odd-step` + `lem:attachment`: odd levels close from even, and a
slack is removed by an extremal-uniqueness/attachment argument). The simple case
has simply never been pushed through this engine -- the prior attempts worked the
backward-arc framing instead. This angle sidesteps the non-monotone-exchange
obstacle entirely.

## The forced structure when the slack is `+1` (even `n = 2k`)

Suppose `a = Q(2k) + 1 = k^2 + k + 1`. Then (all proved, see `attach_check.py`
for the arithmetic):

- Every vertex has `d(v) >= a - Q(2k-1) = k + 1` (delete `v`; `D - v` is feasible
  on `2k-1` vertices so has `<= Q(2k-1) = k^2` arcs).
- `sum_v d(v) = 2a = 2k(k+1) + 2`, so `D` is `(k+1)`-regular **up to total
  degree-excess exactly 2** (two vertices of degree `k+2`, or one of degree
  `k+3`).
- Every degree-`(k+1)` vertex `v` satisfies `a - d(v) = k^2 = Q(2k-1)`, so
  `D - v` is an **exact odd extremiser** on `2k - 1` vertices.

Hence the `+1` case is exactly: *an odd extremiser on `2k-1` vertices, with one
extra vertex `v` of degree `k+1` attached, staying feasible.* Because the
extremiser's `A`-vertices have degree `k`, the forced minimum `k+1` makes `v`
**adjacent to every `A`-vertex**; the remaining `2` incident arcs of `v` are the
degree-excess.

## The attachment is refuted for `k = 4, 5, 6`

Taking the odd extremiser to be the augmented bipartite `B_{k-1,k}` plus one
directed `k`-cycle in `B` (its known form), `attach_check.py` enumerates **every**
way to attach a degree-`(k+1)` vertex `v` (each `A`-vertex's arc direction, times
the two excess arcs, to/from `B` or a second arc to `A`) and checks `lambda^max`
with an exact unit-capacity max-flow. **For `k = 4, 5, 6` no attachment stays
feasible.** So the `+1` configuration is impossible at `n = 8, 10, 12` -- modulo
the uniqueness assumption below.

Why it fails, informally: routing through the complete `A -> B` layer is so rich
that the new vertex cannot absorb `k+1` arcs without creating a third
arc-disjoint route. E.g. if `v` sends arcs into several `A`-vertices, then
`v -> a_i -> b` are many disjoint `v -> b` routes; if `v` collects from two
`B`-vertices `b1, b2`, then for any `a`: `a -> v`, `a -> b1 -> v`, `a -> b2 -> v`
are three disjoint routes. Every placement of the last arcs trips a similar
obstruction. (This is a sketch, not yet a uniform proof.)

## What is proved vs. open

**Proved / verified here:**
- The min-degree reduction: `m = 3` quadratic upper bound for all `n >= 11`
  follows from the even-`n` cases plus seam bases (`n = 9, 10`), by integrality.
- In the even `+1` case the structure is forced as above.
- The attachment is infeasible for `k = 4, 5, 6` (mechanical, exact).

**Open (the remaining gaps -- do not claim the lemma):**
1. **Odd-extremiser uniqueness.** The refutation assumes the only odd extremiser
   on `2k-1` vertices is the augmented bipartite `B_{k-1,k}` + one `k`-cycle. If
   other (non-isomorphic) feasible digraphs reach `k^2` arcs, the attachment must
   be ruled out for each. *Most important sub-goal.* The multigraph analogue
   needed exactly such a characterisation (`thm:extremal-char`).
2. **All `k`, uniformly.** `k = 4, 5, 6` is evidence, not a proof. Promote the
   informal "third-route" obstruction to a uniform argument (likely a clean
   counting/Menger statement: a degree-`(k+1)` vertex over a complete `A -> B`
   layer forces some `lambda >= 3`).
3. **Seam bases `n = 9, 10`.** Need `ell_3^dir(9) = 25` and `ell_3^dir(10) = 30`
   directly. The pruned exhaustion / certifier of `ch:certify` is the tool; this
   is the simple-digraph analogue of the multigraph "finite `n = 7` facts".
4. **`m >= 4`.** The same reduction should be redone (the overshoot pattern will
   differ); and odd-level *uniqueness* for `m >= 4` is the known hole
   (`rem:odd-step-roadmap`), so expect the same wall as the multigraph case.

## Next steps

- Settle gap (1): characterise the `2k-1`-vertex odd extremisers (start by
  enumerating/searching `n = 5, 7` simple directed at the quadratic value with
  the program's `solve`/search, then attempt a hand characterisation mirroring
  `thm:extremal-char`).
- Turn gap (2) into a one-line Menger lemma if possible.
- Get gaps (3) from the certifier (a Gurobi-backed run, per the BIG-COMPUTATIONS
  note in TASKS.md, is the realistic route at `n = 9, 10`).

Reproduce everything: `python3 working_notes/attach_check.py`.

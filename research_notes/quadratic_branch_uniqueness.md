# Extremal uniqueness on the quadratic branch (2026-08-14)

**Status: PROVED for `n >= max(8, 2m)`, open below that.** In the thesis as
`lem:equality-forces`, `lem:skeleton-shallow`, `thm:dir-multi-uniqueness`
(app_proofs.tex, section A.5.3).

Script: `scripts/quadratic_branch_uniqueness.py` (standard library only, own
capped max-flow).

## 0. What was open

`thm:dir-multi-full` gives the value `L_m^dir(n) = (m-1)M(n)` for every `n` and
`m`. `lem:saturated-attachment` gives the extremal family on the LINEAR branch
(doubled bidirected trees). On the quadratic branch the only thing known was
`rem:n7-classification`, a single machine classification at `n=7, m=3`.

ch4 recorded the reason it looked hard: the reachability-skeleton proof "is
silent on it by design, since it never needs to know which digraph it is peeling
apart".

## 1. The reframing

That silence is a property of the proof read FORWARDS. Read BACKWARDS, from the
assumption that its bound is met exactly, the same construction is rigid. Two
bookkeeping steps become determinations:

- The skeleton count `f(q) = 2(n-q) + floor(q^2/4)`, over the number `q` of
  strongly connected components, was bounded by `max(f(1), f(n))` via convexity.
  On the quadratic branch `f(n) - f(n-1) = -2 + floor(n/2) >= 2` for `n >= 8`, so
  a convex function strictly increasing at its right end cannot repeat that value
  earlier. **Equality forces `q = n`, i.e. the extremiser is ACYCLIC.**
- The skeleton's underlying graph was shown triangle-free only to apply Mantel's
  bound. At equality it has exactly `floor(n^2/4)` edges, so **Mantel's EQUALITY
  case pins it to `K_{ceil(n/2),floor(n/2)}`**.

## 2. The new step: minimality makes the skeleton shallow

The skeleton `Q` is inclusion-minimal, which had been used only to make it small.
It also makes it **shallow**:

> **No directed path with three arcs.** If `u -> v -> w -> x`, then `u` and `x`
> are on opposite sides (paths alternate), so the COMPLETE bipartite underlying
> graph puts an arc between them; acyclicity rules out `x -> u`; so `u -> x` is in
> the skeleton and is redundant, since `u` already reaches `x` along the path.
> That contradicts minimality.

This costs nothing and is what makes the theorem work.

## 3. The theorem

For `n >= max(8, 2m)`: equality forces `D = (m-1) * B_{ceil(n/2),floor(n/2)}`,
unique up to relabelling and which side is larger.

Chain: no 3-arc path (section 2) => a 2-arc path `a -> b -> a'` forces `a` to be a
source and `a'` a sink in the skeleton (any in-arc at `a` would extend the path to
three arcs), so by completeness `a -> b'' -> a'` for EVERY `b''` in `B`, giving
`lambda(a,a') >= floor(n/2) >= m`, against feasibility => no 2-arc path => every
vertex is a source or a sink => one-directional => the skeleton's reachability
(only the pairs `A x B`, each by a single arc) leaves no room for any other arc in
`D` => all `floor(n^2/4)` pairs at multiplicity exactly `m-1`.

**`n >= 2m` is used exactly once**, in converting a 2-arc path into `floor(n/2)`
arc-disjoint routes, which only beats the budget `m-1` when `floor(n/2) >= m`.

## 4. Regularity, and the exhaustive check

Equality also forces degrees, which is what makes a check finite in practice:
deleting a vertex leaves at most `(m-1)M(n-1)` arcs, so every vertex has degree
`>= (m-1)floor(n/2)`, and for even `n` the degree sum `2(m-1)floor(n^2/4) =
n(m-1)(n/2)` leaves no slack, so every degree is EXACTLY `(m-1)n/2`.

With acyclicity (fix a topological order, all arcs forward, no generality lost)
plus exact regularity plus the monotone-feasibility prune, the extremisers can be
enumerated outright. Results:

| n | m | covered by the proof? | extremisers found |
|---|---|---|---|
| 8 | 2 | yes | 1, `= B(4,4)` |
| 8 | 3 | yes | 1, `= 2B(4,4)` |
| 8 | 4 | yes (`2m = 8`, the boundary) | 1, `= 3B(4,4)` |

Larger `m` at `n = 8` widens the multiplicity cap and the enumeration slows
sharply (the `m=4` row already took 3.5M DFS nodes); the `m >= 5` rows are in
flight and are NOT claimed here until they return. Those are the ones that
matter for the open range, since `2m > 8` puts them outside the proof.

## What is still open

- The range `n < 2m`. To close it, Step 1 needs a different contradiction: with
  `floor(n/2) < m` a source-to-sink fan of `floor(n/2)` routes is affordable, so
  something other than that fan has to be counted.
- Odd `n`. The theorem covers it (the proof never assumes parity), but the
  exact-regularity shortcut of section 4 does not, so the exhaustive check above
  is even-`n` only.
- The linear/quadratic tie at `n = 7`, where `rem:n7-classification` shows THREE
  classes, so uniqueness genuinely fails at the seam. That is consistent: `n = 7`
  is not on the quadratic branch, `M(7) = max(12,12)` is a tie, and the theorem
  starts at `n >= 8`.

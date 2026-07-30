# Case 2 of thm:dir-arc-linear-error is already tight for its own inequality (2026-07-30)

**Status: PROVED (negative result).** The remark at the end of the proof of
`thm:dir-arc-linear-error` (app_proofs.tex) diagnoses Case 2 as "the wasteful
half" of the O_m(n) error-term proof, since it charges every vertex the worst
case of `lem:small-side` even though the conjectured extremiser has
`min(d+,d-) = 0` on a whole side, and suggests exploiting that to cut the
constant from `4(m-1)` towards the conjectured `(m-2)/2`. This note shows that
specific idea does not work: Case 2's bound is the exact maximum extractable
from the one inequality it is allowed to use (the aggregate two-step-route
budget of Step 2, `sum_x d+(x)d-(x) <= (m-1)n(n-1)`, plus the per-vertex floor
`d(x) >= n/2`). No amount of cleverness applied *to that inequality alone* can
beat the constant 4. Closing the gap toward `(m-2)/2` needs a strictly new
inequality, not a sharper use of the existing one.

## 1. The reformulation

Case 2 bounds `sum_x t_x` where `t_x = min(d+(x), d-(x))`, using only two facts
about a feasible digraph `D` on `n` vertices with `lambda^max <= m-1`:

- **(Budget)** `sum_x d+(x) d-(x) <= Q := (m-1) n(n-1)` (Step 2 of
  `prop:dir-arc-stability`, proved unconditionally by counting arc-disjoint
  two-step routes through each vertex as a midpoint).
- **(Floor)** `d(x) = d+(x) + d-(x) >= n/2` for every `x` (the Case 2
  hypothesis).

`lem:small-side` converts (Floor) into a per-vertex cost: at a vertex with
`d+(x) = a`, `d-(x) = b`, `a+b = s >= n/2`, achieving `min(a,b) = t` costs
`ab = t(s-t)`, which is minimized over `s >= n/2` at `s = n/2` (increasing `t`
fixed, `t(s-t)` is increasing in `s` for `s > t`). So the *cheapest* way to buy
`min = t` at any vertex obeying the Floor is to sit exactly on it:
`d+(x)=t, d-(x) = n/2-t`, costing exactly
```
c(t) = t (n/2 - t),   0 <= t <= n/4.
```
The question Case 2's proof implicitly answers is: **given a shared budget `Q`
spent as `sum_x c(t_x) <= Q` over `n` vertices each with `t_x` in `[0, n/4]`,
how large can `sum_x t_x` be?** This is an exact reformulation of what the
Budget + Floor facts allow (not merely an analogy): every digraph obeying
Budget and Floor gives a feasible point of this relaxation, and every feasible
point of the relaxation is realized in the limit by some digraph's degree
sequence (e.g. a disjoint union of bidirected-ish gadgets tuned to the target
`t_x`, degree sequence realizability is not the bottleneck here since we only
need an upper bound on the relaxation to upper bound the true quantity).

## 2. The relaxation is solved by concentration, not spreading

**Concentration lemma.** Let `c : [0, tau] -> R_{>=0}` be concave with
`c(0) = 0` (our `c(t) = t(n/2-t)` qualifies: `c'' = -2 < 0`, `c(0)=0`). For any
two values `0 < a <= b < tau`, replacing `(a, b)` by `(a - eps, b + eps)` for
small `eps > 0` preserves `a + b` and changes the cost by
```
d/d(eps) [c(a-eps) + c(b+eps)]|_{eps=0} = c'(b) - c'(a) <= 0,
```
strictly negative when `a < b`, since `c' (t) = n/2 - 2t` is strictly
decreasing. So moving mass from the smaller of two interior values to the
larger one strictly *lowers* cost while preserving the sum. Repeating this
exchange, a cost-minimizing allocation for a fixed total sum has **at most one
vertex strictly between 0 and `tau`**; every other active vertex sits at the
cap `tau = n/4`.

Equivalently: for a fixed **cost budget** `Q`, the sum-maximizing allocation is
"bang-bang" — push as many vertices as the budget allows to `t_x = n/4`
(costing `c(n/4) = n^2/16` each), leave the rest at `t_x = 0`, with at most one
vertex fractional. Confirmed independently by a constrained nonlinear solver
(SLSQP, `scripts/case2_tightness_check.py`) against the closed-form bang-bang
value at several `(n, m)`, agreement to solver tolerance in every case.

## 3. The bang-bang value equals the theorem's constant, exactly

With `Q = (m-1)n(n-1)` and `tau = n/4`, the number of vertices pushed to the
cap is `k = floor(Q / (n^2/16)) = floor(16(m-1)(n-1)/n)`. For fixed `m` and
`n -> infinity`, `k -> 16(m-1)`, a **constant** (not growing with `n`), so for
`n` large enough `k < n` and the budget, not the vertex count, binds. The
bang-bang value is then
```
sum t_x  =  k * (n/4) + (fractional remainder)  ~  4 Q / n  =  4(m-1)(n-1),
```
which is *exactly* the constant `thm:dir-arc-linear-error` derives via the
crude per-vertex substitution `2 d+(x) d-(x) / d(x) <= 4 d+(x) d-(x) / n`
(valid since `d(x) >= n/2`) followed by summing. This is not a coincidence:
`lem:small-side`'s bound `min <= 2 d+ d- / d` is tight exactly at `d+ = d-`,
and the further substitution `d(x) -> n/2` is tight exactly at `d(x) = n/2`.
Both hold simultaneously exactly at `d+(x) = d-(x) = n/4` — precisely the
vertex profile the bang-bang optimum concentrates on. **The crude bound and
the sharp joint optimum are tight at the same point**, so summing the crude
per-vertex bound loses nothing asymptotically.

Numerically (`scripts/case2_tightness_check.py`): at `n=80, m=6` the bang-bang
optimum and the theorem's `4(m-1)(n-1)` agree exactly (1580 = 1580); at smaller
`n` relative to `m` the two differ by lower-order terms from integer rounding
of `k`, never by anything that grows with `n`.

## 4. What this rules out, and what is left

The remark's intuition — "the conjectured extremiser has `min(d+,d-)=0` on a
whole side, so charging every vertex the worst case wastes the bound" — is true
of the *conjectured extremiser*, but it is also true of the relaxation's own
worst case: the bang-bang optimum has only `O(1)` (namely `~16(m-1)`) vertices
active at all, and every other vertex sits at `t_x = 0`. So "most vertices have
`min = 0`" is not extra information the current proof fails to use; it is
already the structure of the bound's own tight point. Knowing it in advance
buys nothing further **from this inequality**.

Concretely ruled out: any attempt to improve Case 2's constant by re-deriving
or re-weighting `lem:small-side` and Step 2's budget more cleverly, keeping
the aggregate two-step-route count `sum_x d+(x) d-(x) <= (m-1)n(n-1)` as the
only structural input. That avenue is exhausted (proved, not just tried).

What would work: a **second, independent inequality** that specifically
constrains configurations with a bounded number (`Theta(m)`) of near-balanced,
degree-`~n/4` vertices — i.e. something that catches interference *among*
the `O(m)` expensive vertices themselves, not just between each one and the
rest of the graph. Candidate direction (not attempted here): the `O(m)`
balanced vertices each have `~n/4` in-neighbours and `~n/4` out-neighbours;
if two of them share several common neighbours, three-step routes or
additional two-step routes between *other* pairs appear that Step 1's
single-midpoint count does not see. Formalizing that is genuinely new work,
on par with the structure `open:decomposition` already asks for, not a local
patch to Case 2.

## Verification

`scripts/case2_tightness_check.py`: closed-form bang-bang value vs. a
constrained nonlinear solver (scipy SLSQP, multi-start) across several
`(n, m)`, and vs. the theorem's `4(m-1)(n-1)`. Self-contained
(numpy + scipy only, no dependency on the thesis program).

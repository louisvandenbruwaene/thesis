# Directed arc problem, m = 3: the extremiser family and the attachment refutation

> **SUPERSEDED 2026-06-30: this family is NOT the complete extremal set.** The
> companion note's hypothesis (H) is FALSE (see section 0 of
> [`directed_arc_m3_reduction.md`](directed_arc_m3_reduction.md)): there is a
> second infinite family of extremisers (complete `A -> B` plus one head fanning
> out to a tail and the rest of `B`) attaining `Q(n)` for every odd `n >= 9` with
> a non-source of in-degree 2. So "the extremiser family" below is incomplete, and
> the attachment refutation of the `+1` even case rested on (H) and no longer
> applies. Kept for the record. Reproduce the refutation with
> `python3 research_notes/scripts/h_counterexample.py`.

Companion to [`directed_arc_m3_reduction.md`](directed_arc_m3_reduction.md).
Describes exactly which digraphs attain the conjectured quadratic value, and
refutes the residual `+1` even case from the min-degree reduction.

Reproduce: `python3 research_notes/scripts/attach_check_all_perms.py`.

---

## 1. The extremiser family (PROVED feasible; attains Q; NOT unique)

Take `A` of size `k - 1` and `B` of size `k`. Put every arc `A -> B` (complete,
`k(k-1)` arcs), no arc inside `A`, no arc `B -> A`, and inside `B` the arcs of an
arbitrary **fixed-point-free permutation** of `B` (each vertex one in-arc and one
out-arc inside `B`: `k` arcs). Total `k^2`. This is the odd extremiser on
`n = 2k - 1` vertices; the even analogue on `2k` is `B_{k,k}` (or `B_{k-1,k+1}`)
plus a fixed-point-free permutation, attaining `k^2 + k`.

- **Feasible for every permutation** (`lambda^max = 2`): for `a in A`, `b in B`,
  `lambda(a,b) = 1 (direct) + 1 (a -> pi^{-1}(b) -> b) = 2`; sources are
  unreachable and `B` cannot reach `A`. Verified for all cycle types at
  `k = 4,5,6`.
- **Non-isomorphic members = partitions of `k` into parts `>= 2`**
  (`p_{>=2}(k)`): `k=4 -> {4},{2,2}`; `k=5 -> {5},{2,3}`;
  `k=6 -> {6},{2,4},{3,3},{2,2,2}`. So the extremiser is **not unique**. The
  thesis's `const:augmented-bipartite` (single `k`-cycle) is one member; the
  other cycle types are equally extremal. (This corrects the natural assumption
  that the cycle is forced -- only `B` being a fixed-point-free *permutation* is.)

By the conditional theorem (2.3 of the companion note), these are exactly the
equality cases **given (H)**.

---

## 2. The attachment refutation (VERIFIED for k = 4,5,6, all types)

The `+1` even case reduces to: an odd extremiser on `2k-1` vertices, plus one
extra vertex `v` of degree `k+1`, still feasible. Because each `A`-vertex has
degree `k` in the extremiser and `>= k+1` is forced, `v` must be adjacent to
**every** `A`-vertex; the remaining `2` incident arcs of `v` are the
degree-excess.

> **Claim (VERIFIED, k=4,5,6).** For every `B`-permutation cycle type, no
> degree-`(k+1)` attachment of `v` keeps `lambda^max <= 2`. Hence the `+1` even
> case is impossible at `n = 8, 10, 12` -- provided every odd extremiser is of the
> family above (i.e. provided (H)).

`attach_check_all_perms.py` enumerates, per cycle type, every attachment (each
`A`-vertex's arc direction `x` the two excess arcs) and checks `lambda^max` by
exact max-flow; none is feasible.

### Why (informal, uniform reason -- a clean all-`k` proof is OPEN)
Routing through the complete `A -> B` layer is too rich for `v` to absorb `k+1`
arcs:
- If `v` sends arcs into `>= 3` sources `a_i`, then for any `b in B` the routes
  `v -> a_1 -> b`, `v -> a_2 -> b`, `v -> a_3 -> pi^{-1}(b) -> b` are three
  arc-disjoint `v`-`b` routes.
- If `v` collects in-arcs from `>= 2` vertices `b_1, b_2 in B`, then for any
  source `a`: `a -> v`, `a -> b_1 -> v`, `a -> b_2 -> v` are three arc-disjoint.
The narrow surviving window (mostly `a -> v` in-arcs, `<= 1` arc touching `B`)
cannot reach degree `k+1`. The machine confirms this exhaustively at `k=4,5,6`;
promoting it to a uniform Menger lemma is the open step.

---

## 3. Open

1. **(H)** (companion note) -- the single load-bearing hypothesis; gives both the
   value and that the family is the complete extremiser set.
2. Uniform-in-`k` proof of the attachment claim (Menger lemma per the sketch).
3. Seam bases `ell_3^dir(9) = 25`, `ell_3^dir(10) = 30`.

## 4. Tooling note (search)

`odd_extremiser_search.py` is a self-contained simulated annealer written to
probe (H) empirically. It does **not** reliably reach the optimum at `n = 9, 11`
(best found 24/34 vs `Q = 25/36`) -- a search-strength limitation, not a statement
about the value (the construction attains `Q`). The thesis's own annealer would
reach it but needs `networkx`/`scipy`. The conditional theorem makes the
empirical probe secondary: (H) is the target.

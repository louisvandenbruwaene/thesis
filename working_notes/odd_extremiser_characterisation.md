# Characterising the extremisers (m = 3 simple directed arc)

**Status: a clean conditional theorem (proved), reducing both the quadratic
*value* and the *characterisation* to ONE structural hypothesis; that hypothesis
is the remaining open heart.** Nothing here is in the thesis text yet (rule:
proof-check first).

Reproduce: `python3 working_notes/attach_check_all_perms.py`,
and the arithmetic/sanity checks in this note's commit message / below.

## Setup and an automatic arc partition

`D` simple, feasible at `m = 3` (`lambda^max <= 2`), `n` vertices, `a` arcs. Let
`S` = sources (in-degree 0), `sigma = |S|`, and `R = V \ S` the non-sources.

Since sources have in-degree 0, **there is no arc into `S`** (no `S -> S`, no
`R -> S`). So every arc is either `S -> R` or internal to `R`:
`a = e(S,R) + e(R)`, with `e(S,R) <= sigma(n - sigma)`. (Sanity-checked: 0 arcs
into a source over hundreds of random feasible digraphs.)

## The proved structural Lemma

> **Lemma.** In any digraph with `lambda^max <= 2`, for a source `s` the
> subdigraph induced on `N^+(s)` has maximum in-degree `<= 1`.

*Proof.* If distinct `x_1, x_2 in N^+(s)\{w}` both point to `w in N^+(s)`, then
`s->w`, `s->x_1->w`, `s->x_2->w` are 3 arc-disjoint `s`-`w` routes, contra
`lambda(s,w) <= 2`. ∎  (Verified: 0 violations over 300 random feasible digraphs.)

So if some source is **universal** (adjacent to all of `R`), then `R` itself has
internal maximum in-degree `<= 1`.

## The conditional theorem (proved)

> **Theorem.** If the non-source set `R` induces a subdigraph of maximum
> in-degree `<= 1` (in particular, if `D` has a universal source), then
> `e(R) <= |R| = n - sigma`, hence
> `a <= sigma(n-sigma) + (n-sigma) = (n-sigma)(sigma+1) <= floor((n+1)^2/4) = Q(n)`,
> in BOTH parities. Equality forces: `sigma = (n-1)/2` (odd `n`) [or
> `sigma in {k-1,k}` for even `n=2k`], the layer `S -> R` complete, and `R` a
> fixed-point-free permutation. That is exactly the augmented-bipartite family
> below.

*Checks (this commit):* `max_sigma (n-sigma)(sigma+1)` equals `k^2` at
`sigma=k-1` for every odd `n=2k-1`, and `k^2+k` for even `n=2k` -- i.e. `= Q(n)`
in both parities. The bound is a two-line count given the in-degree hypothesis.

**This is the key reframing:** the entire `m = 3` quadratic upper bound AND the
characterisation follow from the single structural fact

> **(H)** an `m=3` extremiser's non-sources induce maximum in-degree `<= 1`
> (equivalently, it has a source adjacent to every non-source).

(H) is open. It is the honest residue of the backward-arc lemma in this
language, but it is far more concrete: it is a statement about *sources*, not
about a partition with no back-arc, and it sidesteps the non-monotone exchange.

## The extremiser family (proved feasible, attains Q)

`A` of size `k-1`, `B` of size `k`: all `A -> B`, none inside `A`, none `B -> A`,
and inside `B` an arbitrary **fixed-point-free permutation** (`k` internal arcs).
Total `k^2`.

- Feasible for every permutation (`lambda^max = 2`): verified for all cycle types
  at `k = 4,5,6` (`attach_check_all_perms.py`).
- Non-isomorphic members = integer partitions of `k` into parts `>= 2`
  (`p_{>=2}(k)`): `k=4 -> {4, 2+2}`, `k=5 -> {5, 2+3}`,
  `k=6 -> {6,2+4,3+3,2+2+2}`. So the extremiser is **not unique**; the thesis
  construction (single `k`-cycle) is one member. (Even `n=2k`: the balanced
  `B_{k,k}` + permutation, and also `B_{k-1,k+1}` + permutation, both attain
  `k^2+k`.)

## The attachment refutation covers the whole family

`attach_check_all_perms.py`: for `k = 4,5,6` and **every** `B`-cycle type, no
degree-`(k+1)` vertex attaches to the extremiser keeping `lambda^max <= 2`. So in
the `+1` even case the deleted vertex cannot be reattached -- provided every odd
extremiser is of this family, i.e. provided (H). Uniform-in-`k` reason sketched
(third route via the complete `A->B` layer); a clean Menger proof is pending.

## What is open

1. **(H): extremisers have a universal source** (equivalently non-sources induce
   max-in-degree `<= 1`). Proving (H) closes BOTH the value and the
   characterisation via the conditional theorem, and -- with the attachment
   refutation made uniform -- the `+1` even case and hence (with the min-degree
   reduction + seam bases) the whole `m=3` quadratic upper bound. This is now the
   single load-bearing statement.
2. **Uniform-in-`k` attachment refutation** (Menger lemma).
3. **Seam bases** `ell_3^dir(9)=25`, `ell_3^dir(10)=30` (certifier / Gurobi).

## Note on tooling

A homemade simulated annealer (`odd_extremiser_search.py`) was written to probe
(H) empirically, but it does not reliably reach the optimum at `n = 9, 11`
(best found 24/34 vs Q = 25/36) -- a search-strength limitation, NOT evidence
about the value, which the construction attains. The thesis's own annealer would
reach it but needs `networkx`/`scipy` (not installed in this environment). The
conditional theorem makes the empirical question secondary: (H) is the target.

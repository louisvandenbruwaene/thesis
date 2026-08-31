# Applied simplifications for the AI-labelled proofs

This file is a standalone revision dossier and is not included by `main.tex`.
It records the four replacements now applied to the thesis because they make
the appendix genuinely shorter or remove difficult machinery. Existing proofs
not named here were retained: shortening them further mostly removes the
explanation a reader needs without changing the underlying argument.

The applied versions incorporate the independent review and its second-pass
corrections in `SIMPLIFIED_AI_PROOFS_REVIEW.md`.

## 1. Scope and citation policy

Only AI-labelled results are candidates for shortening or replacement. Unbadged
proofs are outside this pass. In particular, the full Gomory--Hu proof of
Mader's theorem stays exactly as it is.

Within an AI-labelled proof, quote an established result when that is shorter
than rebuilding it, provided the thesis states the result clearly and gives its
source. The useful changes are therefore:

- replace the AI-labelled hypergraph Gomory--Hu theorem by the elementary cut
  induction below;
- replace the AI-labelled use of Baranyai by degree smoothing;
- replace the AI-labelled Tutte/SPQR case of the incidence-rank lemma by a
  direct split along a separating pair; and
- replace the AI-labelled copies-plus-remainder count in the first directed
  hypergraph construction by the cyclic round-robin construction.

These are the four thesis-facing replacements supported by the independent
review. They simplify genuine dependencies without shortening unlabelled
material.

## 2. Archived alternate-convention material

Former Appendix A.10 has been removed from the compiled thesis and preserved
verbatim in
`research_notes/alternate_multigraph_vertex_convention.tex`. Its duplicated
block-knapsack proof is therefore no longer a thesis-facing simplification
target. The proposed shared block lemma remains mathematically sound, but it
would no longer shorten the submitted appendix and is not recommended for
insertion.

## 3. Elementary cut induction for the hypergraph edge bound

This replaces A.51, the hypergraph Gomory--Hu theorem, and the Steiner-tree
double count in the proof of Proposition 1.8. The ordinary Gomory--Hu theorem
may remain where independently useful, but the hypergraph version is no longer
needed anywhere.

### Lemma: cut induction for non-uniform multihypergraphs

Let `H` be a multihypergraph on `n>=1` vertices, not assumed uniform, and
suppose every pair has hyperedge-copy connectivity at most `k`. Then, summing
over hyperedge copies,

```text
sum_e (|e|-1) <= k(n-1).
```

**Proof.** Induct on `n`. At `n=1`, every possible hyperedge has size one and
both sides are zero.

Let `n>=2` and fix distinct vertices `u,v`. Hypergraph Menger, already proved
from the helper network in the thesis, gives a set `F` of at most `k`
hyperedge copies whose deletion separates `u` from `v`. Let `S` be the set of
vertices reachable from `u` after deleting `F`, and put `T=V\S`. Then `u` lies
in `S`, `v` lies in `T`, and every hyperedge copy meeting both sides belongs to
`F`. Thus both sides are nonempty and at most `k` copies cross.

Form the trace multihypergraph on `S` by replacing each original copy `e` by
`e intersection S` and discarding traces of size zero or one. Form the trace on
`T` similarly. A Berge route in a trace lifts, copy by copy, to a Berge route
in the original hypergraph. Distinct trace copies come from distinct original
copies. Therefore each trace still has maximum connectivity at most `k`, and
induction applies to both.

A noncrossing copy contributes its entire `|e|-1` on one side. A crossing copy
satisfies

```text
|e|-1 = (|e intersection S|-1)
      + (|e intersection T|-1) + 1,
```

where a bracket is zero exactly when that trace was discarded. Hence

```text
sum_e (|e|-1)
 <= k(|S|-1) + k(|T|-1) + number of crossing copies
 <= k(n-2)+k
 =  k(n-1).
```

This completes the induction. ∎

### Proposition 1.8

In an `r`-uniform hypergraph every copy contributes `r-1`, so the lemma at
`k=m-1` immediately gives

```text
(r-1)|E(H)| <= (m-1)(n-1).
```

Divide by `r-1` and round down. The lower constructions already in the thesis
remain unchanged.

At `r=2`, the same lemma gives the multigraph-edge upper bound
`|E(G)|<=(m-1)(n-1)`; the thickened tree gives equality. This does not prove
Mader's sharper simple-graph theorem, whose factor two requires additional
information.

## 4. Degree smoothing instead of Baranyai

This replaces A.54 and the present proof of A.55. It is elementary and supplies
exactly the sparse uniform family used later.

### Lemma: sparse uniform hypergraphs exist

Let `r>=1`, `n>=r`, and
`0<=d<=binom(n-1,r-1)`. There is a simple `r`-uniform hypergraph on `n`
vertices with

```text
e = floor(dn/r)
```

hyperedges and maximum degree at most `d`.

**Proof.** The identity

```text
(n/r) binom(n-1,r-1) = binom(n,r)
```

shows that at least `e` distinct `r`-sets are available. Among all families of
exactly `e` distinct `r`-sets, choose one minimizing the sum of squared vertex
degrees.

Suppose `deg(x)>=deg(y)+2`. Let `a` be the number of selected edges containing
`x` but not `y`, and `b` the number containing `y` but not `x`. Then
`a>=b+2`. The map

```text
A -> A-x+y
```

sends an edge of the first kind to a set of the second kind. If every image
were already selected, this injection would give `b>=a`, impossible. Hence
some selected `A` has `A-x+y` unselected. Exchange those two sets. The family
remains simple and keeps size `e`, while the squared-degree sum changes by

```text
(deg(x)-1)^2 + (deg(y)+1)^2 - deg(x)^2 - deg(y)^2
 = 2(deg(y)-deg(x))+2
 <= -2,
```

contradicting minimality. Therefore all degrees differ by at most one. Their
sum is `re`, so the largest is `ceil(re/n)<=d`. ∎

This proof contains all existence information needed by A.52 and the simple
part of A.60. Baranyai can be removed completely unless it is retained for
historical interest rather than necessity.

## 5. Incidence rank without Tutte or SPQR

This retains the existing proof of A.58 through the cut-vertex and degree-two
reductions, then replaces its final triconnected-decomposition case. A complete
version is recorded here so the replacement can be checked independently.

### Incidence-rank lemma

Let a connected multigraph `G` have vertex set `X union Z` such that:

1. `Z` is independent;
2. no edge incident with `Z` has a parallel copy;
3. every `z in Z` has degree at least two; and
4. `kappa_G(x,x')<=2` for distinct `x,x' in X`.

Then

```text
rank(G)=|E(G)|-|V(G)|+1 <= |X|-1.
```

**Proof.** Induct on `|V|+|E|`. The cases with at most two vertices are
immediate. With one vertex the hypotheses force one `X`-vertex and rank zero.
With two vertices, a `Z`-vertex cannot have degree two because parallel edges
at `Z` are forbidden. Thus both vertices lie in `X`, and condition 4 allows at
most two parallel edges, giving rank at most one.

If `G` has a cut vertex, apply induction separately to its nontrivial blocks;
a bridge block has rank zero and contains an `X`-vertex. Cycle rank adds over
blocks. If `b(v)` is the number of blocks containing a cut vertex `v`, then

```text
sum_B |X intersection B|
 = |X| + sum over X-cut-vertices x of (b(x)-1),

number of blocks
 = 1 + sum over all cut vertices v of (b(v)-1).
```

Subtracting gives a total block bound at most `|X|-1`.

We may now assume `G` is 2-connected. If a `Z`-vertex has degree two, suppress
it by replacing its two incident edges by one edge between its two
`X`-neighbours. Rank is unchanged, and paths using the new edge correspond
exactly to paths through the suppressed vertex. If an `X`-vertex has degree
two, delete it. The graph remains connected, rank and `|X|` both fall by one,
and its neighbouring `Z`-vertices retain degree at least two because the
degree-two `Z` case was already exhausted. Induction handles both reductions.

It remains to consider a 2-connected graph of minimum degree at least three.
First it is simple. Parallel edges could only join two vertices `x,x' in X`.
Two parallel edges are two `x-x'` paths with empty interior. Because the graph
is 2-connected and has a third vertex, there is also an `x-x'` path with a
nonempty interior: connect through the rest of the graph after deleting one
endpoint at a time, and simplify the resulting walk. These three paths violate
condition 4. Thus there are no parallel edges. A simple graph of minimum degree
at least three has at least four vertices.

If `G` is 3-connected, it contains at least two `X`-vertices: otherwise
independence of `Z` and the absence of parallel incidences would give every
`Z`-vertex degree at most one. Menger then gives three internally disjoint paths
between two `X`-vertices, again contradicting condition 4.

Otherwise choose a separating pair `{a,b}`. Delete it and divide the remaining
components into two nonempty groups with vertex sets `U,W`. Since `G` is
2-connected, each of `a,b` has a neighbour on each side and each side contains
an `a-b` path. Put `s=|X intersection {a,b}|` and make two torsos:

- If `ab` is already an edge, retain it in both torsos.
- If `ab` is absent and `s>=1`, add one temporary edge `ab` to each torso.
- If `s=0`, add to each torso a fresh `X`-vertex and a temporary two-edge path
  from `a` through that vertex to `b`.

The cases are exhaustive because `Z` is independent. If `ab` exists, then
`s=1`: with both endpoints in `X`, the edge and one path through each side
would already be three internally disjoint `a-b` paths.

Each torso satisfies conditions 1--4. Temporary edges never join two old
`Z`-vertices, and a temporary direct edge is added only when no `ab` edge
exists, so conditions 1 and 2 hold. An internal `Z`-vertex keeps all its
neighbours. A separator in `Z` keeps at least one neighbour on its side and
also has the temporary connection, so condition 3 holds. A fresh `X`-vertex
has degree two. For two old `X`-vertices, an internally disjoint family uses a
temporary connection at most once. Replace that connection by an `a-b` path
through the opposite side. Its new internal vertices lie outside the torso, so
this replacement turns any three internally disjoint torso paths into three in
`G`. Condition 4 therefore holds in each torso. Both torsos are smaller in the
induction measure: the omitted side contains a vertex of degree at least three,
more than the number of temporary edges added.

Write `r_U,r_W` for the torso ranks.

- If `ab` exists, it is counted twice, so
  `rank(G)=r_U+r_W`. Here
  `|X_U|+|X_W|=|X|+1`, and induction gives `rank(G)<=|X|-1`.
- If a temporary direct edge is added, then
  `rank(G)=r_U+r_W-1` and
  `|X_U|+|X_W|=|X|+s`, where `s` is one or two. Induction gives
  `rank(G)<=|X|+s-3<=|X|-1`.
- If both separators lie in `Z`, then
  `rank(G)=r_U+r_W-1` and the two fresh vertices give
  `|X_U|+|X_W|=|X|+2`. Induction again gives `rank(G)<=|X|-1`.

This exhausts the cases. ∎

The proof of Theorem 1.10 from this rank bound remains unchanged. The cap two
enters numerically throughout the rank proof. Two parallel edges plus a detour
already exceed it, as do three internally disjoint paths. The conclusion itself
fails at cap three: two `X`-vertices joined by three parallel edges have rank
two, exceeding `|X|-1=1`. Thus the `m=4` problem needs a different bound rather
than a stronger version of the same torso argument.

## 6. Round-robin construction for A.60

This replaces the copies-plus-remainder construction inside the proof of the
first directed-hypergraph bounds.

Let the head set be `B={0,...,b-1}`, put `k=r-1`, `d=m-1`, and

```text
e = floor(db/k).
```

Read the infinite cyclic word

```text
0,1,...,b-1,0,1,...
```

in consecutive blocks of length `k`, and take the first `e` blocks as
hyperedges, allowing a whole block to recur. Because `k<=b`, every block has
`k` distinct vertices. The first `e` blocks consume `ek` consecutive positions
of the cyclic word, so each vertex occurs either `floor(ek/b)` or
`ceil(ek/b)` times. Since `ek<=db`, the maximum degree is at most `d`.

Give each of the `alpha` tail vertices its own copy of this head-set family.
No head is a tail, so every directed Berge route has one step. A tail-head pair
is served at most `d=m-1` times, and the construction is feasible with

```text
alpha floor((m-1)(n-alpha)/(r-1))
```

hyperedges. When simplicity is required, use the degree-smoothing lemma from
Section 4 under the range already stated in A.60.

## 7. What should not be replaced

The remaining compressed proofs in the earlier version of this dossier should
not replace the appendix. They reproduce the same arguments with less
explanation. In particular:

- Keep Mader's unbadged Gomory--Hu proof in full.
- Keep the reachability-skeleton proof and its figure.
- Keep the directed two-step discussion, `lem:small-side`, and
  `rem:case2-tight`. If reorganized, put the general budget lemma first but do
  not delete those explanations.
- Keep the full directed-multigraph equality and classification arguments
  unless the classification is separately removed as a scope decision.
- Keep the existing directed-hypergraph shadow proof.

The four changes above remove genuine machinery from AI-labelled proofs.
Further reductions should come from explicit scope decisions, not from
compressing proofs until their verification steps disappear.

## 8. Scope decisions

The section formerly called "the multigraph vertex problem under the other
convention" was not one of the main sixteen problems. It has now been moved
verbatim to the repository-only archive named in Section 2. Removing it changes
no result among the main sixteen variants.

The quadratic-branch classification is an AI-labelled secondary result. It
classifies the extremisers, not merely the extremal value, on the quadratic
branch of the directed-multigraph theorem. It should stay until the author
decides whether that extra uniqueness result is worth its space.

The historical optimization section recorded the older fractional/cut-counting
MILP and solver history. It was not load-bearing for any theorem and has now
been preserved verbatim in
`research_notes/historical_m_free_optimization.tex`, outside the compiled
thesis.

## 9. Measured length effect

At commit `e38a8fa`, after former Appendix A.10 had been archived, the appendix
occupied 54 pages, physical pages 43--96 of the PDF. After applying the four
proof replacements and archiving the historical optimization subsection, the
clean build occupies 53 pages, physical pages 43--95. The measured saving is
one page, against the two projected before the replacements were written.
Mader's proof and the quadratic classification remain in the thesis.

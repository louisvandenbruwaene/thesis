# The saturated attachment lemma (linear-branch analogue of lem:attachment)

Status: **PROVED** (full proof below, exhaustively machine-verified at m = 3 on
all nine doubled trees with 5 and 6 vertices by
`scripts/saturated_attachment_check.py`). Written 2026-07-02.

The thesis's attachment lemma (lem:attachment) bounds the degree of a vertex
glued onto the BIPARTITE extremiser. This note proves the exact analogue for
the LINEAR branch: gluing onto any everywhere-saturated multigraph, in
particular onto any doubled bidirected tree, caps the new degree at 2(m-1),
and equality is exactly "grow the tree by one leaf". It explains structurally
why the doubled spanning trees form the closed extremal family on the linear
branch, and it collapses two case analyses in the thesis (the n = 8 seam and
the degree-4 case of fact (b) in rem:odd-step-roadmap) to one-line corollaries.

## Statement

Call a directed multigraph D0 on at least 2 vertices **everywhere-saturated**
(at level m) if lambda_{D0}(x, y) = m - 1 for EVERY ordered pair of distinct
vertices. (Every doubled bidirected tree at multiplicity m-1 is
everywhere-saturated: the m-1 routes run along the tree path, and cutting the
path's one doubled edge is an (m-1)-arc cut.)

**Lemma.** Let m >= 2, let D0 be everywhere-saturated, and let D be obtained
from D0 by adding one new vertex v together with any multiset of arcs incident
to v. If lambda^max(D) <= m - 1, then

    d(v) <= 2(m - 1),

and if d(v) = 2(m - 1) then all arcs at v join v to a SINGLE vertex u, with
mu(v, u) = mu(u, v) = m - 1. In that case D is again everywhere-saturated, so
the everywhere-saturated family is closed under maximal attachment, and
iterating from a single doubled edge generates exactly the doubled bidirected
trees.

## Proof

**Step 1 (no mixed pair).** Suppose v has an in-arc from u and an out-arc to
w with u != w. D0 carries m - 1 pairwise arc-disjoint u-to-w routes (Menger,
saturation). The route u -> v -> w uses only arcs incident to v, so it is
arc-disjoint from all of them, giving lambda_D(u, w) >= m. Contradiction.
Hence v is a pure source, a pure sink, or all arcs at v touch one single
vertex u (if an in-arc from u and an out-arc to w coexist, then u = w for
every such pair, which pins every arc at v to that one vertex).

**Step 2 (a pure source has d(v) <= m - 1).** Let t = sum_x mu(v, x) = d(v)
and fix any u with mu(v, u) >= 1. Claim:

    lambda_D(v, u) >= mu(v, u) + min(t - mu(v, u), m - 1).

Take any v-u cut (S, S-bar) with v in S, u in S-bar. Its capacity is
sum_{x in S-bar} mu(v, x) + e_{D0}(S minus v, S-bar). If S contains some
vertex x of D0, then e_{D0}(S minus v, S-bar) >= lambda_{D0}(x, u) = m - 1,
and the first sum is >= mu(v, u) (u lies in S-bar), so the capacity is at
least mu(v, u) + (m - 1). If S = {v}, the capacity is t. Both cases are at
least the claimed bound, and max-flow min-cut gives the claim.

Feasibility says lambda_D(v, u) <= m - 1. If t - mu(v, u) >= m - 1 the claim
forces mu(v, u) + (m - 1) <= m - 1, i.e. mu(v, u) = 0, a contradiction; so
t - mu(v, u) < m - 1 for every u in N+(v), and then the claim reads
t <= m - 1. Hence d(v) = t <= m - 1.

**Step 3 (a pure sink has d(v) <= m - 1).** Reverse every arc. The reverse of
an everywhere-saturated multigraph is everywhere-saturated
(lambda_{D0^R}(x, y) = lambda_{D0}(y, x) = m - 1), a pure sink becomes a pure
source, and Step 2 applies.

**Step 4 (single partner).** If all arcs at v touch one vertex u, then
parallel arcs are already that many arc-disjoint one-step routes, so
mu(v, u) <= m - 1 and mu(u, v) <= m - 1, giving
d(v) = mu(v, u) + mu(u, v) <= 2(m - 1).

**Step 5 (equality).** d(v) = 2(m - 1) > m - 1 rules out the pure cases (m >=
2), so v has a single partner u at full multiplicity both ways. The result is
feasible: a route through v must enter and leave through u, so it contributes
nothing to any x-to-y flow with x, y in D0, and lambda_D(x, v) =
min(lambda_{D0}(x, u), mu(u, v)) = m - 1, symmetrically lambda_D(v, x) = m -
1. The same computation shows D is everywhere-saturated. Starting from a
single doubled edge (everywhere-saturated on 2 vertices) and iterating, each
equality step attaches a new leaf at full multiplicity to an arbitrary
existing vertex, which generates exactly the doubled bidirected trees. QED

## What it buys the thesis

1. **The n = 8 seam (rem:odd-step-roadmap), shortened.** The seam argument
   needed: an 8-regular extremiser D on 8 vertices cannot have D - v equal to
   the doubled path P_7 (it excluded this via the doubled-C_8 collapse case
   check). The lemma kills it instantly: d(v) = 8 > 4 = 2(m - 1) exceeds any
   feasible attachment to a doubled tree.

2. **Fact (b), the degree-4 case, shortened.** If a 24-arc feasible
   multigraph on 7 vertices with max degree <= 8 has a vertex of degree 4,
   then D - v is a 20-arc extremiser on 6 vertices with max degree <= 8, which
   the completed enumeration (2026-07-02, geng pipeline, sound at every n)
   shows is ONLY the doubled path P_6. The lemma then forces v to attach at
   full multiplicity to a single vertex u of P_6, i.e. D = doubled (P_6 +
   pendant at u); the degree cap 8 admits only the path's two ends (interior
   vertices already have doubled degree 8), so D is the doubled P_7. No
   orientation-split case check needed.

3. **Structure of the linear branch.** Doubled trees are exactly the closure
   of the doubled edge under maximal attachment. Note the lemma does NOT by
   itself classify the linear-branch extremisers for all n: an extremiser
   with 2(n-1)(m-1) arcs has min degree >= 2(m-1) by the deletion bound, but
   all degrees >= 2(m-1)+1 is arithmetically consistent (the same counting
   hole as at odd levels for m >= 4), so the induction closes only where a
   degree-2(m-1) vertex is forced or the base is enumerated (n <= 6:
   machine-checked; the extremisers there are exactly the doubled spanning
   trees).

4. **Toward fact (a) (L_3^dir(7) = 24).** In a hypothetical 25-arc feasible
   multigraph on 7 vertices, every degree is >= 25 - 20 = 5 (deletion), and a
   degree-5 vertex would delete to a 20-arc extremiser on 6 vertices. IF the
   full (uncapped) n = 6 classification is exactly the doubled trees, the
   lemma gives d(v) <= 4 < 5, so min degree >= 6; the remaining cases d(v) in
   {6, 7} delete to 19- and 18-arc feasible multigraphs, which are NOT
   extremal, so closing fact (a) by hand along this route needs a
   near-extremal (19/18-arc) classification at n = 6. Left open here; the
   uncapped n = 6 enumeration run is the first step and is queued.

## Verification

`scripts/saturated_attachment_check.py` (2026-07-02): all 3^(2n) attachment
patterns against all 3 doubled trees on 5 vertices and all 6 on 6 vertices at
m = 3. Result: maximum feasible d(v) = 4 = 2(m-1) in all nine cases, and the
degree-4 feasible patterns are exactly the n single-partner full-multiplicity
attachments (one per choice of partner), matching Step 5. Runtime ~31 s.

# Closing the m = 4 odd-uniqueness hole (and the m = 5 value gap)

Status 2026-07-04: PROVED at the level of this note, machine-verified in all
non-arithmetic ingredients (`scripts/deficiency_attachment_check.py`, ALL
CHECKS PASSED), NOT yet in the thesis. The result removes the hole named in
rem:odd-step-roadmap ("at an odd extremal level the counting no longer
forces a vertex of degree (m-1)k") for m = 4 at every level n = 2k+1 with
k >= 5, and kills the m = 5 value escape (the j = 1 case that made
thm:odd-step stop at m = 4). Everything is conditional exactly as the m = 3
chain was: on the value and uniqueness one and two levels down, which the
induction supplies for n >= 11 once finite bases at n = 7, 8, 9, 10 are
established by machine.

Notation as in the thesis: level m means multiplicities in {0, ..., m-1} and
feasible means lambda^max <= m-1 (a pair multiplicity >= m is infeasible on
its own, so the cap is automatic, not an assumption). d(v) is total degree
(in plus out), w(u, v) = mu(u, v) + mu(v, u) the number of arcs between u
and v in both directions. B_{p,q} is the one-directional complete bipartite
digraph, A the source side (|A| = p), B the sink side (|B| = q).
L(n) = L_m^dir(n). Q-branch values: L(2k) = (m-1)k^2,
L(2k+1) = (m-1)k(k+1).

## 1. Even value is free (all m)

**Lemma E.** For every m >= 2 and k >= 2: if L(2k-1) = (m-1)k(k-1) then
L(2k) = (m-1)k^2.

**Proof.** The lower bound is (m-1)B_{k,k}. Suppose A = (m-1)k^2 + j arcs
are feasible on 2k vertices with j >= 1. Deleting any vertex leaves a
feasible multigraph on 2k-1 vertices, so every degree satisfies
d(v) >= A - L(2k-1) = (m-1)k + j. But the average degree is
2A/(2k) = (m-1)k + j/k, and j <= j/k forces j(k-1) <= 0, so j = 0. QED

(Update 2026-08-09: this step was flagged here as "implicit in the thesis's
m = 3 chain" but was never actually ported into app_proofs.tex, so the
thesis's own even-levels paragraph asserted its conclusion without proof.
A full audit re-deriving every proof in app_proofs.tex from scratch caught
this as a genuine gap. Fixed: Lemma E is now in the thesis verbatim, stated
generally for all m (not just m = 3), extended with the regularity and
per-vertex-reduction consequence the roadmap's even-levels paragraph
actually needs (every vertex hits the degree floor exactly, not just some
vertex, so every single-vertex deletion lands on an odd-level extremiser),
as Theorem thm:even-step right before rem:odd-step-roadmap. The rest of
this note, sections 2 onward (Corollary D1, Theorem U4, the full m = 4
closure), is still research only and not in the thesis.)

## 2. The deficiency-1 attachment corollary

**Corollary D1.** Let m >= 3 and D0 = (m-1)B_{p,q} with q > p >= 2 and
q >= 3. Let D = D0 + v be feasible with d(v) = (m-1)q - 1. Then v is a pure
source, its arcs all point into B, and its out-multiplicity profile over B
is (m-1, ..., m-1, m-2): every sink receives at least m-2 >= 1 arcs from v,
all but one receive m-1. The mirror statement holds for p > q >= 2,
p >= 3: v is a pure sink fed by A with in-profile (m-1, ..., m-1, m-2).

**Proof.** Write iA, iB, oA, oB for the total multiplicity of v's arcs in
from A, in from B, out to A, out to B. We re-run the case analysis of
lem:attachment and check which cases can carry (m-1)q - 1. Throughout note
that (m-1)q - 1 > 2(m-1), because (m-1)(q-2) > 1 for q >= 3, m >= 3.

Case iA >= 1, say mu(a, v) >= 1. An out-arc v -> b would give the route
a -> v -> b on top of the m-1 parallel a -> b arcs, so oB = 0. An out-arc
v -> a' with a' != a would give a -> v -> a' -> b, three fresh arcs, an m-th
a-to-b route, impossible. So v's out-arcs, if any, all go to this single a.
If mu(v, a) >= 1 then an in-arc from a different source a' is impossible
(a' -> v -> a -> b is an m-th a'-to-b route), so all in-arcs from A come
from a itself, and the flow estimate
lambda(a, v) >= mu(a, v) + iB (the routes a -> b -> v, arc-disjoint across
sinks and from the direct arcs) caps mu(a, v) + iB <= m-1, giving
d(v) = (mu(a, v) + iB) + mu(v, a) <= 2(m-1), too small. So v is a pure
sink: d(v) = iA + iB. For every source a the same estimate gives
mu(a, v) <= (m-1) - iB, hence d(v) <= p(m-1) - iB(p-1) <= p(m-1). Since
q > p this is at most (m-1)q - (m-1) < (m-1)q - 1, too small. So iA = 0.

Case iB >= 1 and oB >= 1. If the in-arc and some out-arc use different
sinks b != b', the route a -> b -> v -> b' is an m-th a-to-b' route,
impossible. So both live on a single sink b, and
lambda(v, b) >= mu(v, b) + oA (routes v -> a -> b) <= m-1 gives
d(v) = mu(b, v) + (mu(v, b) + oA) <= 2(m-1), too small.

Case iB >= 1, oB = 0 (in-arcs from B, out-arcs only to A): iB <= m-1 from
lambda(b, v) and oA <= m-1 from lambda(v, b'), so d(v) <= 2(m-1), too
small.

The only case left is iA = iB = 0, a pure source. For every sink b the
routes v -> a -> b give lambda(v, b) >= mu(v, b) + oA <= m-1, so
mu(v, b) <= (m-1) - oA for every b, hence
d(v) = oB + oA <= q(m-1) - oA(q-1). With d(v) = (m-1)q - 1 this forces
oA(q-1) <= 1, and q >= 3 gives oA = 0. The out-profile over B sums to
(m-1)q - 1 with every entry at most m-1, which means exactly one entry is
m-2 and the rest are m-1. The mirror case is arc reversal. QED

Machine check (exhaustive over ALL attachment patterns): at
(m; p, q) = (4; 2, 3), (4; 3, 2), (4; 2, 4), (4; 3, 4), (5; 2, 3) the
feasible attachments at degree (m-1)max(p, q) - 1 are exactly the
max(p, q) predicted patterns (one per choice of the light partner), and at
degree (m-1)max(p, q) exactly the one full pattern of
cor:attachment-equality.

## 3. Tight pairs

**Lemma T.** Let D be feasible on 2k+1 vertices with A arcs and suppose
L(2k-1) = (m-1)k(k-1). Then every pair satisfies
w(u, v) <= d(u) + d(v) - (A - (m-1)k(k-1)), and if equality holds
("(u, v) is tight") then D - u - v is feasible on 2k-1 vertices with
exactly (m-1)k(k-1) arcs, an odd-level extremiser.

**Proof.** Deleting u and v removes d(u) + d(v) - w(u, v) arcs (the arcs
between u and v are counted in both degrees). The remainder is feasible on
2k-1 vertices, so A - d(u) - d(v) + w(u, v) <= (m-1)k(k-1), which is the
inequality, and equality is exactly the extremal remainder. QED

## 4. The m = 4 theorem

**Theorem U4.** Let m = 4, k >= 5. Assume
 (i)   L(2k) = 3k^2,
 (ii)  L(2k-1) = 3k(k-1), and
 (iii) the extremisers at 2k-1 are exactly 3B_{k,k-1} and 3B_{k-1,k}.
Then every feasible multigraph D on 2k+1 vertices with 3k(k+1) arcs has a
vertex of degree exactly 3k.

Consequently, given additionally even uniqueness at 2k (extremiser
3B_{k,k}), the existing rebuild argument (delete the degree-3k vertex, land
on 3B_{k,k} by (i) plus uniqueness, rebuild by cor:attachment-equality)
gives odd uniqueness at 2k+1: D = 3B_{k+1,k} or 3B_{k,k+1}.

**Proof.** Deletion against (i) gives d(v) >= 3k(k+1) - 3k^2 = 3k for every
v. The degree sum is 6k(k+1) and the average is 3k + 3k/(2k+1) < 3k + 2, so
the minimum degree is 3k or 3k+1. Suppose, for contradiction, that it is
3k+1.

Write d(v) = 3k+1+e_v with e_v >= 0. The total excess is
sum e_v = 6k(k+1) - (2k+1)(3k+1) = k-1. Let T = {v : e_v = 0}, t = |T|,
and let r = 2k+1-t count the outside vertices, each with e_x >= 1, so
r <= k-1 and t >= k+2.

By Lemma T with A = 3k(k+1): w(u, v) <= d(u) + d(v) - 6k for every pair.
In particular w <= 2 for T-pairs, and w(u, x) <= 2 + e_x for u in T,
x outside.

Case 1: some T-pair (u, v) has w(u, v) = 2. The pair is tight, so
D0 = D - u - v is an odd extremiser on 2k-1 vertices, and by (iii) it is
3B_{k,k-1} or 3B_{k-1,k}. Note k >= 5 matters here: at k = 4 the level
2k-1 = 7 is the linear-quadratic tie (3k(k-1) = 36 = 6(2k-2)) and (iii)
would be false as stated, the extremal set is richer. Both D - v = D0 + u
and D - u = D0 + v are feasible one-vertex attachments with attachment
degree d(u) - w = d(v) - w = 3k - 1 = 3max(k, k-1) - 1, so Corollary D1
applies to each, with the same D0 hence the same orientation. Suppose the
orientation is q = k > p = k-1 (sinks B, |B| = k), so u and v are both pure
sources into B with profiles (3, ..., 3, 2): every sink receives at least 2
from each of u and v, and at least k-1 >= 2 sinks receive the full 3 from
u. Now w(u, v) = 2 means an arc between u and v exists. If mu(u, v) >= 1,
pick b with mu(u, b) = 3: the route u -> v -> b is arc-disjoint from the
three direct u -> b arcs, so lambda(u, b) >= 4 > 3. If mu(v, u) >= 1,
symmetric with a full sink of v. Either way infeasible. The mirror
orientation (both pure sinks fed by A) fails the same way through a full
source of u or v. Contradiction, so Case 1 is impossible.

Case 2: every T-pair has w <= 1. Count the arcs at T. The degrees give
2e(T) + e(T, out) = t(3k+1), where e(T) is the number of arcs inside T and
e(T, out) the number between T and outside (both directions). Inside T,
w <= 1 gives e(T) <= t(t-1)/2. Between T and outside, call a pair (u, x)
tight when w(u, x) = 2 + e_x, and let s be the number of tight mixed
pairs. Then e(T, out) <= t(r + sum_x e_x) + s = t(r + k - 1) + s, because a
non-tight pair carries at most 1 + e_x. Substituting, and using
t - 1 + r + k - 1 = 3k - 1:

    t(3k+1) <= t(t-1) + t(r + k-1) + s = t(3k-1) + s,

so s >= 2t. (The arithmetic is verified as an exact identity for
k = 2..300 in the script.) If every outside vertex were in at most one
tight mixed pair we would have s <= r <= k-1 < 2(k+2) <= 2t, so some
outside vertex x is tight with two distinct u1, u2 in T.

Both (u1, x) and (u2, x) are tight, so D0 = D - u1 - x and
D0' = D - u2 - x are odd extremisers, equal to 3B_{k,k-1} or 3B_{k-1,k} by
(iii). The attachment degree of x onto D0 inside D - u1 is
d(x) - w(u1, x) = (3k+1+e_x) - (2+e_x) = 3k-1, deficiency 1, so Corollary
D1 pins x. Suppose D0 has orientation q > p (sinks B, |B| = k). Then x is
a pure source into B. The vertex u2 lies in D0. If u2 were a source of D0
its D0-degree would be 3k, and d(u2) = 3k + w(u2, u1) + w(u2, x) >=
3k + w(u2, x) >= 3k+3 > 3k+1 (tightness gives w(u2, x) = 2 + e_x >= 3),
impossible. So u2 is a sink of D0, and since x is a pure source,
w(u2, x) = mu(x, u2) <= 3, forcing e_x = 1, w(u2, x) = 3 = mu(x, u2), and
d(x) = 3k+2. The degree of the sink u2 in D0 is 3(k-1), so
d(u2) = 3(k-1) + w(u2, x) + w(u2, u1) forces w(u2, u1) = 1. Symmetrically
(via D0'), u1 is a sink of D0', mu(x, u1) = 3, and w(u1, u2) = 1
(consistent). If D0 and D0' had opposite orientations, x would be a pure
source toward B minus u2 (nonempty, k >= 2) and simultaneously a pure sink
on the common part D - u1 - u2 - x, impossible. So both orientations
agree, and the two bipartitions coincide on E = D - u1 - u2 - x: E is the
complete one-directional 3B on (A, B0) with |A| = |B0| = k-1, whose
bipartition is unique, so D is pinned completely:

    A -> B0 complete at 3, A -> u1 and A -> u2 complete at 3,
    x -> u1 and x -> u2 at 3, x -> B0 with profile (3, ..., 3, 2),
    and one arc between u1 and u2,

which has exactly 3k(k+1) arcs. If the arc is u2 -> u1 then
x -> u2 -> u1 joins the three direct x -> u1 arcs: lambda(x, u1) >= 4. If
it is u1 -> u2 then lambda(x, u2) >= 4. Infeasible either way (machine
check: every profile placement and both directions at k = 3, 4, 5, 6). The
mirror orientation (x a pure sink) is arc reversal. Contradiction, so Case
2 is impossible.

Both cases being impossible, the minimum degree is 3k. QED

## 5. What this does to the m = 4 chain

With Lemma E, Theorem U4, thm:odd-step (valid at m = 4), the even
regularity argument, and cor:attachment-equality, value and uniqueness
propagate at m = 4 in both parities for every n = 2k, 2k+1 with k >= 5,
by the same joint induction as m = 3:

* odd value+uniqueness at 2k-1 give even value at 2k (Lemma E) and even
  uniqueness at 2k (3k-regularity forces every deletion extremal at 2k-1,
  then (iii) and the equality corollary rebuild 3B_{k,k}),
* even value+uniqueness at 2k give odd value at 2k+1 (thm:odd-step, m = 4)
  and odd uniqueness at 2k+1 (Theorem U4 forces a degree-3k vertex, the
  rebuild argument finishes).

The induction therefore rests on finite bases at m = 4, exactly as m = 3
rested on n = 7, 8:

* (a4) L_4^dir(7) = 36 and the full 36-arc extremal classification on 7
  vertices (the linear-quadratic tie level, like n = 7 at m = 3),
* (b4) the seam n = 8: 12-regularity plus the n = 7 classification (the
  tripled trees among the deletions die instantly against
  lem:saturated-attachment since 12 > 2(m-1) = 6),
* (c4) n = 9 and n = 10: k = 4 sits below the k >= 5 threshold because
  2k-1 = 7 is the tie level, so odd uniqueness at 9 needs the richer n = 7
  extremal set in Case 1/2 (bipartite members die by the argument above,
  tripled trees by the saturated lemma, any further members need checking
  once (a4) is computed), and n = 10 then follows by regularity.

These are machine targets of the same kind as facts (a) and (b), one size
class up (multiplicities {0..3}).

## 6. The m = 5 value gap also closes (value only)

thm:odd-step stops at m = 4 because at m = 5 the averaging window fails
for j = 1: a hypothetical A = 4k(k+1) + 1 could have every degree
>= 4k + 2. But then the degree sum forces exact (4k+2)-regularity
((2k+1)(4k+2) = 2A precisely), and Lemma T gives w <= 3 for every pair
with tightness landing on the 2k-1 extremiser. The total arc mass forces
tight pairs to exist: A - 2 * C(2k+1, 2) = 2k+1 > 0, so at least 2k+1
pairs have w = 3. For a tight pair both attachment degrees are
(4k+2) - 3 = 4k - 1, deficiency 1 at (m-1)max(p, q) = 4k, so Corollary D1
makes both endpoints pure sources (or sinks) with profiles (4, ..., 4, 3),
and the w = 3 >= 1 arc between them creates a fifth route through a full
partner, infeasible (machine check at k = 3, 4, 5, every split). The j = 1
escape is dead, and j >= 2 already dies by the averaging window as in
thm:odd-step. So for m = 5, k >= 5: even value+uniqueness at 2k and odd
value+uniqueness at 2k-1 give L_5^dir(2k+1) = 4k(k+1).

**Honest residue at m = 5:** odd UNIQUENESS does not yet propagate. The
delta = 4k+1 analysis goes through Case 1 verbatim, but in Case 2 the
excess is 2k-1 rather than k-1, so T is only guaranteed t >= 2 and the
pigeonhole s >= 2t > r can fail for small t. The m = 5 chain therefore
still stalls at uniqueness, now for a precisely delimited reason (the
excess outgrows the T-count), not for lack of a value step. For m = 6 the
minimum degree can also reach (m-1)k + 2, which needs a deficiency-2
corollary (the same proof gives oA(q-1) <= 2, still forcing oA = 0 for
q >= 4, with profiles (5, ..., 5, 3) or (5, ..., 4, 4), every sink still
covered), so the machinery plausibly extends, with growing case counts.

## 7. Verification

`scripts/deficiency_attachment_check.py` (self-contained, own capped
Edmonds-Karp): exhaustive Corollary D1 at five (m; p, q) sets including
both orientations and the equality case, every Case-1 structure (all
w-splits, all profile placements, k = 3..6), every Case-2 structure (both
arc directions, all profile placements, k = 3..6, arc count = 3k(k+1)
asserted), every m = 5 j = 1 structure (all w = 3 splits, k = 3..5), and
the counting identities for k = 2..300. ALL CHECKS PASSED, 2026-07-04.

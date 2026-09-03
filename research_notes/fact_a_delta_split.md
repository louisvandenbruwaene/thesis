# Fact (a) by the delta-split route: L_3^dir(7) = 24

Status 2026-07-04, END OF DAY: **fact (a) is PROVED along this route.**
L_3^dir(7) = 24, M*(7) = 12, and with facts (a) and (b) both settled the
entire m = 3 directed multigraph chain of rem:odd-step-roadmap closes.

The numbers, for the record:

* Classification (sound geng enumerator, uncapped, 10 cores): exactly
  **55** isomorphism classes of feasible 6-vertex multigraphs with 19 arcs
  (2549 s) and **565** with 18 arcs (1576 s). Files
  `program/logs/n6_t{19,18}_classes.npz`, log
  `program/logs/n6_near_extremal_20260704.log`.
* Cross-check: all 620 classes re-verified for arc count and feasibility by
  BOTH the thesis checker and this note's independent Edmonds-Karp, 0
  disagreements. The observed minimum degrees (>= 3 at 19 arcs, >= 2 at 18)
  match the floors predicted below from L_3^dir(5) = 16.
* Attachment check: in case A, 27 of 55 classes pass the degree floor and
  286 attachment patterns survive the filters to reach the full all-pairs
  max-flow, every one infeasible. In case B, 28 of 565 classes pass the
  floor, 154 patterns reach the full check, every one infeasible. NO
  SURVIVOR in either case, so no 25-arc feasible multigraph on 7 vertices
  exists.

Nothing enters the thesis yet, per the verification ladder: the direct
uncapped n = 7, target 25 run (route 2, which shares only the enumerator
core with route 1) was relaunched detached 2026-07-04 17:05, log
`program/logs/geng_a_n7_t25.log`. Its EMPTY output is the independent
confirmation that unlocks the thesis write-up.

Everything below is at m = 3: multiplicities mu(x, y) on ordered pairs of
distinct vertices, feasible means lambda^max <= 2. Note mu <= 2 is automatic
for feasible multigraphs (mu(x, y) >= 3 already gives lambda(x, y) >= 3),
not an assumption.

## The reduction

**Lemma D (delta split).** Let D be a feasible directed multigraph on 7
vertices with 25 arcs. Then its minimum total degree delta(D) is 6 or 7,
and:

* if delta = 6, deleting a degree-6 vertex leaves a feasible 6-vertex
  multigraph with 19 arcs,
* if delta = 7, the degree sequence of D is (7,7,7,7,7,7,8) and deleting a
  degree-7 vertex leaves a feasible 6-vertex multigraph with 18 arcs.

**Proof.** Deleting any vertex v removes exactly d(v) arcs and leaves a
feasible multigraph on 6 vertices, which has at most L_3^dir(6) = 20 arcs
(machine-proved twice: fractional M*(6) = 10 OPTIMAL and integral target-21
INFEASIBLE, both 2026-06-12). So d(v) >= 25 - 20 = 5 for every v. If some
d(v) = 5 then D - v has exactly 20 arcs, so it is extremal at n = 6, and the
uncapped n = 6 classification (sound geng enumerator, 2026-07-02) says it is
one of the six doubled bidirected spanning trees. Doubled trees are
everywhere-saturated, so the saturated attachment lemma
(lem:saturated-attachment) caps any feasible attachment at
d(v) <= 2(m-1) = 4 < 5, a contradiction. Hence every degree is at least 6.
The degree sum is 2 * 25 = 50 < 56 = 7 * 8, so some degree is at most 7 and
delta is 6 or 7. If delta = 7 the only degree sequence with sum 50 and
minimum 7 on seven vertices is (7,7,7,7,7,7,8). The arc counts 25 - 6 = 19
and 25 - 7 = 18 are immediate. QED

**Lemma F (mixed-pair filter).** Let D be feasible, v a vertex, H = D - v.
If D contains an arc u -> v and an arc v -> w with u != w, then
lambda_H(u, w) <= 1.

**Proof.** The lambda_H(u, w) pairwise arc-disjoint u-to-w routes of H use
no arc incident to v. The route u -> v -> w uses only arcs incident to v, so
it is arc-disjoint from all of them and lambda_D(u, w) >= lambda_H(u, w) + 1.
Feasibility caps the left side at 2. QED

**Theorem (conditional on the two classifications).** Fact (a),
L_3^dir(7) = 24, holds if and only if the attachment check reports no
survivor. Precisely: let T19 and T18 be complete lists of the isomorphism
classes of feasible 6-vertex multigraphs with exactly 19 and 18 arcs. Then a
25-arc feasible 7-vertex multigraph exists iff some H in T19 admits an
attachment of a new vertex v with d(v) = 6 and all seven degrees >= 6
keeping lambda^max <= 2, or some H in T18 admits one with d(v) = 7 and all
seven degrees >= 7.

**Proof.** Forward direction: by Lemma D a witness D with delta = 6 has a
degree-6 vertex v whose deletion lands on some H isomorphic to a member of
T19, and re-attaching v is exactly an attachment of the stated kind
(min degree 6 in D is the degree condition). Same for delta = 7 with T18,
where the degree condition is >= 7. Backward direction: any survivor IS a
25-arc feasible multigraph on 7 vertices. So the check decides fact (a) in
both directions, it is not a one-sided test. QED

Remarks recorded for the write-up:

* In case A every vertex of H has degree >= 3, and in case B >= 2, because
  deleting it from H would leave a feasible 5-vertex multigraph, capped at
  L_3^dir(5) = 16 (integral target-17 INFEASIBLE, 2026-06-12). The checker
  does not use this, it is a sanity property of the classifications.
* attach(u) = mu(u, v) + mu(v, u) <= 4, so the degree floor
  attach(u) >= dmin - deg_H(u) already kills every H with a vertex of
  degree < dmin - 4, and the floors must sum to at most d(v).
* Lemma F is what makes the attachment enumeration cheap: in a 19-arc H
  most ordered pairs have lambda_H = 2, and every such pair (u, w) forbids
  the coexistence of an in-arc from u and an out-arc to w.

## The computation

1. Classifications (running): `enumerate_extremal_directed_multigraphs_via_generation(6, 3, t)`
   for t = 19, 18, uncapped, saved to `program/logs/n6_t{19,18}_classes.npz`.
   The enumerator is sound at every n (proved M*(j <= 6) prunes only), so
   the lists are complete by the same argument that certified fact (b).
2. Attachment check: `scripts/fact_a_attachment_check.py`. Self-contained
   capped Edmonds-Karp, independent of the thesis program. Filters are
   exactly the degree floor and Lemma F, then a full all-pairs max-flow on
   every survivor of the filters.
3. Controls (all pass, 2026-07-04):
   * doubled P_6 + degree-4 vertex returns exactly the 6 single-partner
     full-multiplicity patterns, reproducing the saturated attachment
     lemma's equality case through the whole pipeline,
   * 2B(3,3) + degree-7 vertex returns nothing, matching lem:attachment's
     cap (m-1) max(p, q) = 6 < 7,
   * doubled P_7 judged feasible, doubled C_7 judged infeasible.
4. Cross-check mode (`--crosscheck`): every loaded class re-verified for
   arc count and feasibility by BOTH the script's own max-flow and the
   thesis program's checker.

## Verification ladder (what "independently verified" will mean)

1. This route: sound enumerator + self-contained attachment checker with
   controls and cross-checks. Decides fact (a) either way.
2. The direct machine route: uncapped
   `enumerate_extremal_directed_multigraphs_via_generation(7, 3, 25)`,
   empty output = fact (a). Slower by far but shares no reduction logic
   with route 1 (only the enumerator core). To be relaunched detached when
   the n = 6 runs free the cores.
3. The MILP route: `prove_integral_arc_bound(7, 3, 25, use_gurobi=True)`
   INFEASIBLE, on the author's Gurobi licence. Shares nothing with either
   enumeration.

If routes 1 and 2 agree, the thesis can record fact (a) with the same
standard fact (b) already met (sound enumerator + exact re-verification).
Route 3 remains the nicest external certificate.

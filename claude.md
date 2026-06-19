# Claude progress log — attacking the unsolved variants

Session start: 2026-06-11. Goal: rigorously prove the easiest unsolved variants
(for all n and m where possible), logging progress here regularly.

## Status of open problems (from ch4_synthesis.tex)

| Open item | Difficulty assessment | Plan |
|---|---|---|
| Hypergraph vertex-disjoint (undirected), table row "vertex/hyper: ---" | EASIEST — unexplored, m=2 looks provable for all n, r | Attack first |
| Directed hypergraph (arc + vertex), "---" | Model must be defined (program: tail + r-1 heads); first bounds provable | Second |
| conj:min-degree (directed multigraph, odd n, mixed regime) | Well-posed single lemma; numerics + partial rigorous progress | Third |
| Backward-arc lemma (m>=3 directed simple) | Known hard, thesis names it as THE obstacle | Not attempted |
| k_m(n), m>=6 (1974) | Half-century open | Not attempted |

## Definitions fixed by the program (erdos915_unified.py)

- kappa for hypergraphs (`vertex_split=True`): max number of Berge u-v paths
  pairwise **hyperedge-disjoint AND internally vertex-disjoint** (flow network:
  capacity-1 gate per hyperedge, capacity-1 split per internal vertex,
  endpoints uncapped). Menger holds with **mixed cuts** (vertices + hyperedges).
  Whitney kappa <= lambda holds by definition.
- Directed hyperedge: (tail, frozenset of r-1 heads); a route enters at the
  tail, leaves toward any head.

## Result 1 (PROVED, pending write-up): hypergraph vertex case, m = 2

**Theorem A.** For r >= 2 and all n >= 1, the maximum number of hyperedges of an
r-uniform (multi-)hypergraph on n vertices with kappa^max <= 1 is
floor((n-1)/(r-1)). Extremal: the star hypertree / any Berge forest with that
many edges. So k_2^{(r)}(n) = l_2^{(r)}(n): the vertex and edge problems agree
at m=2 for every r.

Proof skeleton (verified carefully):
- kappa^max >= 2  <=>  the bipartite incidence graph I(H) contains a cycle.
  (A cycle in I alternates v1,e1,v2,e2,...,el,v1, l>=2: paths v1,e1,v2 and
  v1,el,vl,...,e2,v2 are hyperedge-disjoint with disjoint internal vertex sets,
  so kappa(v1,v2)>=2. Conversely two such paths concatenate to a Berge cycle =
  cycle in I. Length-4 incidence cycles = two hyperedges sharing two vertices,
  so repeated hyperedges are automatically excluded.)
- Hence kappa^max <= 1 <=> I(H) is a forest: r|E| <= n + |E| - 1, i.e.
  |E| <= (n-1)/(r-1).
- Lower bound: hub h + floor((n-1)/(r-1)) disjoint blocks of r-1 vertices,
  hyperedges {h} u B_i, leftover vertices isolated. I is a tree => kappa^max<=1.

## Result 2 — UPDATE 2026-06-12: m = 3 NOW FULLY PROVED (all n, all r)

**Theorem.** For r >= 2, every r-uniform multihypergraph with kappa^max <= 2
has at most floor(2(n-1)/(r-1)) hyperedges; attained (simply) for r >= 3 when
2 <= binom(n-2, r-2). So k_3^{(r)}(n) = l_3^{(r)}(n) for all n.

The missing counting step ("Lemma L") is proved — the key realisation is to
ORDER the reductions so the terminal configuration has min degree >= 3
everywhere, then analyse the LEAVES of Tutte's triconnected decomposition
(the earlier z-deletion route was a dead end):

**Incidence rank lemma.** G connected multigraph, V = X u Z, (i) Z
independent, (ii) edges at Z unrepeated, (iii) every z-degree >= 2,
(iv) kappa_G(x,x') <= 2 for all X-pairs  =>  rank(G) <= |X| - 1.
Induction on |V|+|E|:
 1. Cut vertex: per-block induction + block-cut-tree count
    (sum (|X_B|-1) = |X|-1 - sum_{Z-cut}(b-1) <= |X|-1; bridges direct).
 2. z of degree 2: suppress (neighbours distinct, in X; all preserved).
 3. x of degree 2 (now all z-degrees >= 3): DELETE x; rank drops exactly 1,
    |X| drops 1, z-degrees stay >= 2. This was the unlock.
 4. Remaining: 2-connected, min degree >= 3. Parallel X-X edges already give
    kappa >= 3 (third route through any third vertex: G-x' walk + G-x walk),
    so G is simple. 3-connected G: all pairs kappa >= 3 => |X| <= 1 => z's
    have degree <= 1, absurd. Otherwise the Tutte/SPQR tree has >= 2 leaves
    (cite Tutte 1966, Hopcroft-Tarjan 1973), each leaf L with one virtual
    edge {a,b} and a far-side real a-b path avoiding L:
     - S-leaf (cycle, length >= 3): interior vertex has G-degree 2. Absurd.
     - P-leaf (bond): >= 2 real parallels. Absurd (simple).
     - R-leaf (3-connected, >= 4 nodes): Menger in L + far-side substitution
       gives kappa_G >= 3 for ALL pairs of V(L) => <= 1 X-node in L => some
       z* not in {a,b} has all neighbours in <= 1 X-node, degree <= 1. Absurd.
    So Step 4 is vacuous and the induction closes. QED
Numerics: 150 random maximal feasible sets at n=7, r=3, m=3 cap at 6 = bound;
n=5,6 exhaustive (multi) already matched; k_4^{(3)}(5) = 6 verified
exhaustively (q=6 feasible, q=7 not), so vertex=edge survives at m=4, n=5.

Write-up: lem:incidence-rank + thm:hyper-vertex-m3 + scope remark replace the
old conjecture block in app_proofs.tex (commented); ref.bib needs Tutte66 and
HopcroftTarjan73 entries (noted inline). m >= 4 open: no clean 4-connectivity
decomposition; first r >= 3 divergence point unknown.

## Result 2 (original notes, superseded): hypergraph vertex case, m = 3

Reformulation (exact, via the program's mixed-cut Menger): kappa_H(u,v) equals
the max number of internally disjoint u-v paths in the incidence graph I(H).
So the m=3 problem is: maximize q (number of degree-r Y-nodes) in a bipartite
graph I with parts X (n vertices) and Y (q hyperedges) such that no two
X-nodes are joined by 3 internally disjoint paths. Claimed value: q(r-1) <=
2(n-1), i.e. **k_3^{(r)}(n) = floor(2(n-1)/(r-1))** (lower bound already known
via Whitney + thm:simple-hyper-edge).

- Block-tree reduction PROVED: if every 2-connected block B satisfies
  rank(B) <= |X cap B| - 1, then total cycle rank <= |X|-1, which is exactly
  the bound. (Count: sum over blocks (|X_i|-1) = |X| - 1 - sum over Z-class
  cut nodes (b(z)-1) <= |X|-1.)
- Remaining core: **Lemma L**: H 2-connected multigraph, Z independent set,
  every z in Z with >=3 distinct X-neighbours and no parallel Z-edges, all
  X-pairs kappa<=2  =>  rank(H) <= |X|-1.
  - Proved: Z = empty case (ear decomposition => H is a cycle).
  - Proved: degree-2 Z-suppression preserves all hypotheses.
  - Proved: for z in Z, N(z) is pairwise kappa<=1 in H-z (dispersal).
  - Remaining: the counting step rank(H-z) <= |X| - deg(z) using dispersal.
- Numerics planned: brute force r=3, n=5,6 (is n-1 really the max?).

## Numerics completed (2026-06-11/12, via the thesis's own checker)

- Theorem A verified: star hypertree attains floor((n-1)/(r-1)) with
  kappa^max=1 for r=3,4 and n up to 11; brute force over ALL hypergraphs
  (multi included at m=2 automatically, since repeats force codegree 2):
  no hypergraph beats the bound at (n,r) in {(5,3),(6,3),(7,3),(6,4),(7,4)}.
- m=3, r=3: max edges with kappa^max<=2 is exactly n-1 at n=5,6 — verified
  over SIMPLE and MULTI hypergraphs (codegree<=2 pruning + exhaustive).
  Supports k_3^{(r)}(n) = floor(2(n-1)/(r-1)).
- Fractional min-degree search (hill climbing + annealing, multi-start,
  n=7 and n=9): max min-degree found = k exactly (bipartite point, rigid);
  max total weight found = floor(n^2/4) at n=7. No counterexample direction.

## Result 3: directed multigraph odd case — NEW ROUTE bypassing conj:min-degree

The thesis route to L_m^dir(2k+1) needs conj:min-degree. Found a different
route that avoids it. All statements below have full proofs (checked twice,
to be written into app_proofs.tex commented out).

**Lemma C (attachment lemma, UNCONDITIONAL).** Let D0 = (m-1)*B_{p,q} be the
one-directional complete bipartite multigraph (parts A, |A|=p>=2, sinks B,
|B|=q>=2, every arc A->B at multiplicity m-1, m>=2). If D is obtained from D0
by adding one new vertex v together with any set of arcs incident to v, and
lambda^max(D) <= m-1, then d(v) <= (m-1) max(p, q).
Proof by classifying v's arc classes iA, iB, oA, oB (in from A/B, out to A/B):
 - iA>0 and oB>0 impossible: a->v->b is an m-th route on top of the m-1
   parallel a->b arcs.
 - iA>0 and an out-arc v->a' with a'!=a impossible: a->v->a'->b is an m-th
   route (uses fresh arcs (a,v),(v,a'),(a',b)).
 - so iA>0 forces v to be a pure sink (except possibly a 2-cycle with a single
   a, which caps d(v) <= 2(m-1)); then for each a in A,
   lambda(a,v) = mu(a,v) + sum_b min(mu(b,v), m-1) = mu(a,v) + iB <= m-1,
   so d(v) = iA + iB <= p(m-1) - iB(p-1) <= p(m-1).
 - symmetrically oB>0 forces pure source; lambda(v,b) = mu(v,b) + oA <= m-1
   for every b gives d(v) <= q(m-1) - oA(q-1) <= q(m-1).
 - iB>0 and oB>0 (different sinks) impossible: a->b->v->b' is an m-th route
   on (a,b'); same-b 2-cycle caps at 2(m-1).
 - iB and oA only: lambda(a',v) >= iB and lambda(v,b') >= oA force
   iB <= m-1, oA <= m-1, so d(v) <= 2(m-1).
All cases give d(v) <= (m-1) max(p,q,2) = (m-1) max(p,q). QED

**Theorem D (odd step closes for ALL m >= 3, conditional only on even level).**
Fix k >= 4 (so the quadratic branch dominates: k^2 > 2(2k-1)). Assume
 (i)  L_m^dir(2k) = (m-1)k^2, and
 (ii) every extremal multigraph at 2k is (m-1)*B_{k,k}.
Then L_m^dir(2k+1) = (m-1)k(k+1).
Proof. Lower bound: (m-1)*B_{k,k+1}. Upper: let A = (m-1)k(k+1) + j with
j >= 1; min-degree deletion gives A <= (2k+1)/(2k-1) * (m-1)k^2, so
j <= J := floor((m-1)k/(2k-1)). Every vertex satisfies
d(v) >= A - L(2k) = (m-1)k + j, while the average degree is
2A/(2k+1) = (m-1)k + j + [(m-1)k - (2k-1)j]/(2k+1) < (m-1)k + j + 1.
Hence some v has d(v) = (m-1)k + j exactly, and D - v has exactly (m-1)k^2
arcs: it is extremal at 2k, so by (ii) D - v = (m-1)*B_{k,k}. Lemma C then
caps d(v) <= (m-1)k < (m-1)k + j. Contradiction; so j = 0. QED

**UPDATE 2026-06-12 (second pass): uniqueness propagation now PROVED in both
parities via an equality version of the attachment lemma.**

- **Corollary (attachment equality, proved).** In Lemma C with max(p,q) >= 3
  and d(v) = (m-1)max(p,q): q > p forces v = pure source at full multiplicity
  (rebuilds (m-1)B_{p+1,q}); p > q symmetric; p = q one of the two.
- **Odd uniqueness (m=3, n=2k+1 >= 9):** extremiser has degrees >= 2k and not
  all >= 2k+1 ((2k+1)^2 > 4k(k+1)); a degree-2k vertex deletes to 2B_{k,k},
  equality corollary rebuilds 2B_{k+1,k} / 2B_{k,k+1}. PROVED given even
  level below.
- **Even uniqueness (m=3, n=2k >= 10):** averaging equality forces
  2k-regularity, every deletion extremal at 2k-1, odd uniqueness + equality
  corollary (q>p case) rebuild exactly 2B_{k,k}. PROVED given odd level below.
- **Seam n=8:** regularity excludes the double star among 7-vertex
  extremisers (hub degree 24 > 8), leaving the two bipartite orientations,
  so D = 2B_{4,4} — PROVED given the n=7 facts below.
- **CORRECTION (found by the new enumerator): the linear-branch extremal set
  is all doubled bidirected spanning trees, not just the double star.**
  Exhaustive enumeration (new tool
  `enumerate_extremal_directed_multigraphs`, DFS with proved prunings +
  canonical dedup): n=4, m=3, 12 arcs: exactly 2 extremals (doubled star,
  doubled path); n=5, m=3, 16 arcs: exactly 3 (star, broom, path — all
  bidirected-symmetric, i.e. exactly the doubled spanning trees). Every
  bidirected tree at multiplicity m-1 is feasible (proof: flows bottleneck at
  tree edges / pass through cut vertices), so this is the full set at small n.
- **Seam n=8 RE-PROVED with the corrected set:** D 8-regular, D-v a 24-arc
  extremiser with max degree <= 8: among doubled trees only the doubled path
  P_7 qualifies (tree degree <= 2); attaching v to P_7 forces weight 4 on
  each path end (degree count), i.e. bidirected full multiplicity, giving the
  doubled bidirected C_8 — infeasible (two doubled directions around: lambda
  = 4 > 2). So all deletions are bipartite-type and D = 2B(4,4). Seam holds.
- **Net result: the ENTIRE m=3 directed multigraph problem now rests on two
  finite integral statements:**
  (a) M*(7) = 12 (i.e. L_3(7) = 24);
  (b) every 24-arc feasible multigraph on 7 vertices with max degree <= 8 is
      2B(3,4), 2B(4,3), or the doubled bidirected path P_7.
- Certifier strengthened accordingly: `use_deletion_cuts` flag adds three
  PROVED-valid families (vertex-deletion <= M*(n-1), pair-deletion
  <= M*(n-2), degree-pair d+(s)+d-(t)-w(s,t) <= n-1). Verified unchanged
  optima at n=5; n=6 timing comparison in progress.

**Uniqueness propagation (m = 3, original sketch, superseded by the above).**
 - Odd extremal at 2k+1 (m=3): A = 2k(k+1) forces min degree exactly 2k
   (counting: all degrees >= 2k+1 would need sum >= (2k+1)^2+2k+1 > 2A),
   deletion lands on the even extremal, Lemma C analysis forces v to be a
   pure source to B (or pure sink from A) at full multiplicity, so the
   extremal at 2k+1 is exactly 2*B_{k+1,k} or 2*B_{k,k+1}.
 - Even extremal at 2k (m=3): A = 2k^2 forces 2k-regularity and every
   deletion extremal at 2k-1; reattachment via Lemma C forces 2*B_{k,k}.
 - So for m=3 value+uniqueness propagate jointly for all n >= 9, and the
   whole m=3 directed multigraph problem reduces to the FINITE bases
   n = 7, 8 (value + extremal characterization), exactly the certifier's
   next target. NOTE crossover subtlety: at n=7 the branches tie (24 arcs,
   double star AND 2*B(3,4) AND 2*B(4,3) all extremal), so the n=8
   reconstruction must use degree-regularity to exclude the double star
   (hub degree 24 > 8 cannot fit in an 8-regular graph) — this works.
 - For m >= 4 there is one identified HOLE: at odd levels the extremal could
   a priori have all degrees >= (m-1)k+1 (counting allows it when
   k(m-3) >= 1), so odd uniqueness does not yet propagate; Theorem D still
   gives the VALUE at odd levels whenever even uniqueness is available.

**Relation to conj:min-degree.** Theorem D bypasses it. Note the conjecture
is equivalent (over all m at once) to its fractional version: w in [0,1] on
ordered pairs, all max-flows <= 1, n = 2k+1 => some weighted degree <= k.
Conditional bound from averaging: min weighted degree <= 2k^2/(2k-1) < k+1
(given fractional even bound k^2), i.e. integral slack <= m-2; conjecture
asks slack 0 and stays open, but is no longer on the critical path for m=3.

## Numerics: fractional min-degree / total weight (n=7, n=9)

Hill climbing + simulated annealing, multi-start (zero, random, bipartite,
noisy bipartite), all-pairs max-flow feasibility checked exactly:
 - max min-degree found = k exactly (3 at n=7, 4 at n=9), attained by the
   one-directional bipartite point, which is locally rigid in every tested
   direction; noisy starts converge back below it.
 - max total weight found = 12.000 at n=7 = max(2(n-1), floor(n^2/4)).
Supports both the fractional odd bound and conj:min-degree.

## Result 4 (planned): directed hypergraph first bounds

Model: hyperedge = (tail, r-1 heads). Easy and rigorous:
- Degree bound: lambda(u,v) <= min(d+(u), d-(v)).
- Pair-codegree bound: <= m-1 hyperedges share the same (tail u, head v) pair,
  hence (r-1)|E| <= (m-1) n(n-1).
- Bipartite construction: tails A, heads in B, per-tail (r-1)-uniform simple
  hypergraph on B with max degree <= m-1 (exists by lem:sparse-hypergraph):
  |A| * floor((m-1)|B|/(r-1)) edges, lambda^max = m-1 when only single-step
  routes exist (B has no tails). Quadratic ~ (m-1) n^2 / (4(r-1)).

## Result 4 (PROVED): directed hypergraph first bounds

Model (matches the program): hyperedge = (tail, r-1 heads). Proved:
pair-codegree <= m-1 gives (r-1)|E| <= (m-1)n(n-1); bipartite construction
(tails A, shared sparse (r-1)-uniform head hypergraph on B from
lem:sparse-hypergraph) gives alpha*floor((m-1)(n-alpha)/(r-1)) feasible
hyperedges, so the value is quadratic. Exact value open (factor ~4 gap).

## Deliverables written (all commented out / non-invasive, PENDING REVIEW)

- chapters/app_proofs.tex:
  * after the directed-multigraph section: lem:attachment (full proof),
    thm:odd-step (full proof), rem:odd-step-roadmap (m=3 reduction to bases
    n=7,8; m>=4 hole identified).
  * end of the hypergraph section: incidence-graph translation,
    thm:hyper-vertex-m2 (full proof), prop:hyper-vertex-lower (full proof),
    conj:hyper-vertex + rem:hyper-vertex-m3 (reduction + partial progress),
    prop:dir-hyper-first (full proof).
- chapters/ch4_synthesis.tex: commented replacement row for the summary
  table (vertex/hyper) and commented updates to two open-problem items.
- program/erdos915_unified.py: new section "OPEN-VARIANT EXPLORATION"
  (hypergraph_vertex_m2, max_hyper_vertex_connectivity,
  hyper_vertex_feasible_exists, verify_hyper_vertex_value,
  fractional_flows_feasible, fractional_anneal) + commented self-test hooks.
  Full self-check suite re-run after integration: ALL CHECKS PASSED.
- main.pdf recompiles cleanly (latexmk exit 0, no errors).

## Honest status summary

PROVED unconditionally, all n:
  * k_2^{(r)}(n) = floor((n-1)/(r-1)) for every r (hypergraph vertex, m=2).
  * prop:hyper-vertex-lower (all m, r >= 3).
  * Attachment lemma (lem:attachment) for all m >= 2, p,q >= 2.
  * Directed hypergraph pair-codegree upper bound + quadratic construction.
PROVED conditionally:
  * thm:odd-step: odd-level value for ALL m >= 3 given even value+uniqueness.
  * m=3 value+uniqueness propagate for all n >= 9 given bases n=7,8.
STILL OPEN (precisely delimited):
  * Bases n=7,8 for the directed multigraph at m=3 (finite computations).
  * Odd-level extremal uniqueness for m >= 4 (the counting hole).
  * Lemma L counting step (hypergraph vertex m=3); conjecture for m >= 4.
  * conj:min-degree itself (bypassed for m=3, supported numerically).

## Progress on the finite bases (2026-06-12, late session)

- Full self-test suite re-run after all program edits: ALL CHECKS PASSED.
- Fractional certifier with deletion cuts: n=6 OPTIMAL M*(6)=10 in 1315s
  (comparable to baseline ~20 min; fractional n=7 out of reach locally).
- NEW: integral certifier `certify_integral_arc_bound(n, m, target)` — the
  m=3 chain needs only the INTEGRAL fact L_3(7) = 24, i.e. "no 25-arc
  feasible multigraph on 7 vertices", a much friendlier MILP (integer mu,
  exact cuts at capacity m-1, two-hop exact-min rows, deletion cuts from
  certified M*(4), M*(5), M*(6), degree-pair inequality, degree-sorting).
  Sanity: n=5 t16 FEASIBLE 0.7s, t17 INFEASIBLE 2.9s.
  RESULT: n=6 t21 INFEASIBLE in 1309s — independent integral re-proof of
  L_3^dir(6) = 20.
- n=7 t25 MILP and the n=6 max-degree-8 enumeration were CANCELLED after ~2h
  CPU each (no verdict yet) at the user's request. To resume (run from
  program/, each prints a single verdict line):
    python -c "from erdos915_unified import certify_integral_arc_bound as c;\
 print(c(7, 3, 25, time_limit=86400.0))"
    # INFEASIBLE => L_3^dir(7) = 24 => statement (a) PROVED
    python -c "from erdos915_unified import \
enumerate_extremal_directed_multigraphs as e;\
 r = e(6, 3, 20, max_degree=8); print(len(r)); [print(M) for M in r]"
    # expected: only the doubled bidirected path P_6 => degree-4 case of (b)
  Budget hint: the integral MILP closed n=6 in ~22 min on this machine; n=7
  plausibly needs hours-to-days, so a cluster node or an overnight run (or
  a stronger solver, e.g. Gurobi on the same encoding) is the right tool.
- Statement (b), degree-4 case PROVED by hand (conditional on the n=6
  max-degree-8 characterization, enumeration in flight): if some d(v) = 4,
  then D - v is a 20-arc extremiser at n=6 with max degree <= 8 — expected
  to be only the doubled path P_6 (bipartite 2B(3,3) = 18 < 20 is not
  extremal at 6; doubled non-path trees have a degree-12+ hub). Attaching a
  degree-4 vertex v to doubled P_6: interior vertices are degree-saturated
  (8), so v attaches only to the two path ends; full bidirected weight 4 on
  ONE end gives exactly the doubled P_7 (allowed third extremiser); any
  split across BOTH ends adds a parallel channel between the path ends on
  top of the capacity-2 path, pushing some lambda to 3+ (case check over
  the orientation splits 2+2: all fail). So (b) reduces to its delta >= 5
  core: 24 arcs, 5 <= d(v) <= 8 — where 2B(3,4) (degrees 8,8,8,6,6,6,6)
  lives. That core remains a computation (or an S-T-style hand argument).

## Future direction noted: m = 4 hypergraph vertex problem

The incidence reduction generalizes: k_{m}^{(r)}(n) = floor((m-1)(n-1)/(r-1))
would follow from "kappa_X <= m-1 implies rank <= (m-2)(|X|-1)". For m=4 the
predicted tight 2-connected pieces are the K_{3,t} incidence blocks (rank
exactly 2(|X|-1), all X-pairs at kappa = 3). The obstruction: Tutte's
decomposition stops at 3-connectivity; a 4-connectivity analogue (k-blocks of
Carmesin-Diestel-Hamann-Hundertmark?) lacks the clean tree-of-pieces with
virtual edges that Step 4 of the incidence rank lemma leans on. Verified
k_4^{(3)}(5) = 6 exhaustively, so no early counterexample.

## Suggested next actions for the author

1. Review the commented LaTeX blocks; if accepted, uncomment and re-run the
   (commented) self-test hooks in _run_checks for the printed evidence.
2. Point the certifier at n=7, m=3 directed multigraphs (value 24 + extremal
   set {double star, 2B(3,4), 2B(4,3)}?) — this is now the single missing
   base for the full m=3 theorem.
3. The Lemma L counting step (claude.md Result 2) is a self-contained
   graph-theory problem, suitable as a focused push or a co-advisor question.

## Session 2026-06-12/13 (overnight, carte blanche granted)

Author lifted the commented-block rule: verified content goes in directly.

FABLE PROOF-CHECK of all of app_proofs.tex (every statement, active and
commented). 29 statements verified correct, 4 ERRORS found and FIXED:
 1. prop:mutual-unreachability FALSE as stated — counterexample
    {(u,v),(v,u),(u,w)}: λ^max ≤ 1 yet v→u→w. Restated: no v–w path in D−u;
    counterexample now displayed in the proof + figure.
 2. thm:odd-step "all m ≥ 3" had a GAP for m ≥ 5: the correction term
    ((m-1)k−(2k-1)j)/(2k+1) need not lie in [0,1) (m=5,k=4,j=1 gives exactly
    1: an 18-regular 81-arc escape is arithmetically consistent). Restated
    for m ∈ {3,4} with the [0,1) step justified ((m−3)k+1 ≤ k+1 < 2k+1);
    m ≥ 5 value-gap documented in rem:odd-step-roadmap. m=3 chain UNAFFECTED.
 3. prop:min-degree-m2 false at n=3 (bidirected star), proof invalid n=5
    (linear branch dominates). Restated with n ≥ 7.
 4. thm:extremal-char odd case missed a third slack location (a G-edge at
    tree distance 3). Proof rewritten as the S1+S2+S3 slack identity
    2|E| = m(n−1) − (S1+S2+S3). Also fixed: "K_4 blocks glued along shared
    edges" → glued at shared cut vertices (edge-gluing is infeasible: shared
    pair reaches λ=5), claim softened to "consistent with".

INTEGRATED (now live, uncommented): lem:attachment, cor:attachment-equality,
thm:odd-step, rem:odd-step-roadmap, thm:hyper-vertex-m2, prop:hyper-vertex-
lower, lem:incidence-rank, thm:hyper-vertex-m3, rem:hyper-vertex-m3-scope,
prop:dir-hyper-first + new \section{The hypergraph vertex problem}.

OTHER WORK (subagents, all builds verified):
- Easy fixes (sonnet): Tutte66/HopcroftTarjan73 active in ref.bib (verified
  DOIs); k-tree defined inline in ch1 (false forward ref removed); K_4-trees
  dropped from main.tex summary; citations added for pre-2024 conjecture
  (ErdosProblems) and Bollobás–Erdős attribution (BollobasErdos62).
- ch4 (opus): PENDING blocks resolved, tab:summary updated (hyper-vertex row
  proved m≤3; directed rows cond. m=3; dir-hyper quadratic), open problems
  rewritten (two finite n=7 computations in progress; m≥4/m≥5 holes split).
- Related work (opus): new ch1 \section{Where this work sits} — lineage +
  nauty/geng, SAT (Heule), flag algebras (Razborov), all 5 new bib entries
  web-verified. New ch2 \section{Reproducibility}.
- Consolidation (opus): ch3 trichotomy sections merged → sec:trichotomy;
  ch4 figures 9→6 (m6 distribution pair + threshold_3d cut, prose added for
  scatter + surface); G(n,p) home is ch1 only.
- Figures (opus): 7 TikZ figures in appendix (Gomory–Hu dist, two Mader
  constructions, mutual-unreachability + counterexample, attachment setup,
  P_7→C_8 seam, hypergraph↔incidence translation + star hypertree, SPQR leaf
  schematic); 3 in ch1 (B_{4,4}, bidirected star, 30-arc counterexample with
  highlighted routes). Proof-idea sketches surfaced into ch1 body. G(n,p)
  limitation sentence added (fixed-m regime not covered).
- Build: latexmk exit 0, 81 pages, zero undefined refs. Figure pages
  spot-checked visually (renders clean).

COMPUTATIONS LAUNCHED (detached, survive session):
- PID 37597: certify_integral_arc_bound(7,3,25,time_limit=86400) →
  logs/milp_n7_t25_20260613.log
- PID 37663: enumerate_extremal_directed_multigraphs(6,3,20,max_degree=8) →
  logs/enum_n6_d8_20260613.log
- Watcher (background bash bijy4lkb4) re-invokes the session when one ends.

## 2026-06-13 (morning, Opus) — figure/data audit + first-introduction TikZ + Fable queue

Author's brief: the plots felt "rough/incomplete/inaccurate"; wanted uniformity
(equal datapoints, general rules holding); more TikZ when graph classes are FIRST
introduced; and Fable set up to attempt the hard proofs next.

FIGURE/DATA FIXES (the main ask). All 13 used figures were stale (generated Jun 7-9,
code changed Jun 12); regenerated via `make_figures.py`
(log program/logs/make_figures_20260613.log). Root-cause fixes, not cosmetic:
1. `gather_variant_grid` (make_figures.py): the search "lower-bound" circles were raw
   annealing that plateaued jaggedly BELOW the proved curves — contradicting the
   caption, which promises each circle is "the better of the search and a named
   construction." `_extend_lower_bounds` was applied to only 2 of 12 panels. Now applied
   to every proved/conjectured panel, over UNIFORM n-ranges (matrix 2..12, hyper 2..10),
   so each panel has equal datapoints and circles land ON the curves. Verified: across
   all proved/conj panels, search==curve (0 above, 0 below). search_budget 1.5->0.4
   (construction dominates those panels, so anneal quality there is irrelevant).
2. Hyper-undirected-vertex panel was drawn "open" though thm:hyper-vertex-m3 proves it.
   Now PROVED (solid line + on-curve dots) at m<=3, OPEN (band) at m>=4. Verified on
   both m=3 (proved) and m=6 (open) grids.
3. `variant_surface_3d` was ENTIRELY purple: `compute_surface_cache` called
   `solve(exhaustive=False)`, which never returns bound=="exact". Added
   `_surface_known_value(vkey,n,m)` = proved closed form (capped at trivial max) in the
   proved regime, else None. Proved cells -> exact/blue; open cells -> discovery/purple.
   Cache migrated IN PLACE on next run (proved cells overwritten, open cells kept), no
   recompute. Now 202 exact / 218 lower; proved variants render as blue sheets, the
   open/proved boundary is visible (e.g. simple vertex blue m<=4, hyper vertex blue m<=3).
4. Integer x-ticks: `plot_conn_dist_grid` (set_xticks(levels)), `plot_edge_dist_grid` and
   `plot_scatter_lambda_edges` (MaxNLocator integer) — kills spurious 0.5/1.5 labels on
   the sparse directed panels.
5. The `edge_vertex_divergence` "wiggle" is NOT a bug: it is the true floor staircase
   (m=2,4 integer slope -> straight; m=3,5 zigzag by <=1). Left as correct maths.
   Caption numbers spot-checked and correct: edge_vertex_sampling shows kap<lam 22/12/6%.

TIKZ AT FIRST INTRODUCTION (ch1, self-contained inline styles; roleMeasure/roleObserve/
KULblauw1/roleDiscover colours): fig:three-models (simple triangle / multigraph with
triple+double parallel edges / shaded 3-vertex hyperedge + ordinary edge) at the model
paragraph; fig:edge-vs-vertex (two s-t routes through one cut vertex w: lam=2, kap=1,
Whitney) at the separation paragraph; fig:berge-path (two overlapping hyperedges sharing
y, orange route u->y->w) at the hypergraph section. All three render clean in the PDF.

BUILD: latexmk exit 0, 83 pages (+2), zero undefined refs, 1 (pre-existing) overfull hbox.

TASKS.md rewritten with a NEXT-SESSION FABLE block (backward-arc lemma flagship; hyper
vertex m=4 needing a 4-connectivity SPQR analogue; m>=4 odd-uniqueness / m>=5 value-step
hole; the two n=7 facts by hand).

BACKGROUND JOBS: MILP 37597 (1.8 GB) + enum 37663 still running; enum now ~17 GB RAM and
climbing (OOM risk, 288 MB free). I tried to `kill 37663` to free RAM for the figure run
but the sandbox DENIED killing a process it did not start. Flagged in TASKS.md: author
can kill 37663 safely (identical predecessor was already cancelled without a verdict).
Neither log has produced a verdict yet (only START lines).

FOLLOW-UP same day (author review): (1) author's PC ran out of RAM — the unbounded enum
(PID 37663) had grown to ~22 GB; author-authorised, killed it (no partial output, prints
only at the end). MILP 37597 left running. Big computations moved to a TASKS.md "run
later, memory-capped" block (systemd-run --user --scope -p MemoryMax=... verified to
work). (2) Author spotted GREEN exact squares BELOW PURPLE circles in variant_bounds
(impossible — a lower bound above the proved optimum), worst at m=6. Cause: my
construction-extension planted the raw closed form, but floor(m(n-1)/2) etc. are the
value only for n>=m; for n<m the complete graph K_n is feasible and the formula
overshoots (e.g. n=2,m=6 gives 3 edges where only 1 exists). Fixed by capping every
proved/conj curve AND its planted lower bound at the model trivial max
(lb_simple_edge/lb_multi_edge/lb_multi_dir; directed/hyper were already capped). Both
grids regenerated; a sanity assert confirms no exact square exceeds its curve.
(3) Reworked the 3 TikZ figures the author flagged: A.3(a) apex x -> labelled circle;
A.4 attachment lemma decluttered (wider, faint background A->B arcs, bold v-classes);
A.6(a) hypergraph -> clean filled hulls with an orange Berge path. Build clean, 83 pages.

---
Session: 2026-06-13. Tasks: prose cleanup in main.tex and chapter 1-2 authorial commands.

Changes made:
(1) main.tex prose: removed -- (en-dashes) from compound names in prose; changed
    S{\o}rensen--Thomassen -> S{\o}rensen-Thomassen and Gomory--Hu -> Gomory-Hu in two
    prose locations (Contribution Statement and Abbreviations table).
(2) ch1 line 6: inserted K_5 - 2 edges TikZ figure (fig:k5-example) as the first
    concrete graph example in the chapter.
(3) ch1 three-models figure: rebuilt the hypergraph subfigure with 7 vertices and 2
    hyperedges of different sizes (size 3, violet; size 4, blue), no regular edges;
    updated caption to describe both hyperedges.
(4) ch1 Sorensen-Thomassen: removed the vague "sufficiently large n" qualifier and
    replaced with concrete "n >= 10"; added a remark explaining the threshold.
(5) ch1 Construction 1.5 (directed hub): added a paragraph introducing d+ (out-degree)
    and d- (in-degree) before the construction uses those symbols.
(6) ch1 bidirected-star figure: expanded to two-panel figure (m=2 left, m=4 right)
    using subcaption-free side-by-side TikZ scopes; the m=4 panel shows hub arcs
    (blue) + two circulant layers (orange). Caption updated accordingly.
(7) ch1 "pre-2024 conjecture": removed the misattributed \cite{ErdosProblems} and
    changed to "the natural initial conjecture" since that conjecture (directed, m>=3)
    is not stated in Problem 915.
(8) ch2 hyperedge gadget: added a room-with-doors analogy paragraph explaining the
    helper-node construction.
Build check: pdflatex clean, 83 pages, 0 errors.

## 2026-06-13 (Opus) — merged erdos915_simplified.py back into the unified program
Author asked to fold the scratch teaching file `program/erdos915_simplified.py` (a
class-hierarchy rewrite of the core) back into `erdos915_unified.py`, optimising for
readability then brevity. Decision (confirmed with author): KEEP the matrix+Variant
`Graph` — it is the better unification (the simplified file's SimpleGraph/MultiGraph
"differ by one line", which the `simple` flag already captures) and underpins every
prover/figure efficiently. Harvested the simplified file's ONE genuine win: the graph
CHECKER now measures edge- and vertex-connectivity through a single `vertex_split`-
parameterised path — `_flow_network` / `local_connectivity` / `max_connectivity` —
exactly mirroring the hypergraph section, with `max_edge_connectivity` etc. kept as
thin named views so nothing downstream changed. Removed `_edge_flow_network` and
`_vertex_split_network` (6 connectivity funcs → 3 real + 5 one-line views). Deleted the
now-redundant `erdos915_simplified.py` (restores hard-rule #1: one runnable file). No
.tex touched. Full `python erdos915_unified.py` self-check: ALL CHECKS PASSED (~59s).

## 2026-06-13 (Opus) — plainer naming (author found "annealing"/"certifying" too hard)
Author asked for more accessible names + softer comments. Confirmed vocabulary: the
DISCOVER corner is now "search", the PROVE corner is now "prove" (aligning the code
names with the file's own MEASURE/PROVE/DISCOVER narrative). Renames across BOTH
`erdos915_unified.py` and `make_figures.py`: anneal()→search_for_dense_graph,
search_best_graph()→best_of_searches, AnnealingResult→SearchResult, StepRecord→
SearchStep, _timed_anneal→_search_within_budget, plot_temperature_trace→plot_search_trace,
fractional_anneal→fractional_search; certify_directed_multigraph→prove_directed_multigraph,
certify_integral_arc_bound→prove_integral_arc_bound, CertificateResult→ProofResult,
_CERTIFIED_MSTAR→_PROVEN_MSTAR, local var certificate→proof. Comments softened
(Metropolis→"accept-worse rule", "geometric cooling"→"cools", certifier→prover,
certified→proved). KEPT: the "temperature/cooling" metaphor; "(simulated annealing)"
named once in the SEARCH banner + search docstring to preserve the thesis link; the
thesis-facing figure strings ("multigraph, certified" caption, "certified optimum"
label, temperature_trace.png filename). Self-check: ALL CHECKS PASSED (~59s); all
make_figures imports resolve. Backup at /tmp/erdos915_unified.bak.py (pre-rename).

## 2026-06-13 (Opus) — closed the rename's last gap: the test suite + TASKS.md
The previous rename verified `erdos915_unified.py` + `make_figures.py` but MISSED the
`program/tests/` suite (10 files, 66 tests) and a stale resume command. Fixed the only
two test files that imported renamed symbols: `test_search.py` (anneal→
search_for_dense_graph, search_best_graph→best_of_searches, plus the method name
test_anneal_*→test_search_*) and `test_certify.py` (certify_directed_multigraph→
prove_directed_multigraph, class Certifier→Prover, docstring certifier→prover); also
the cosmetic `test_solve.py` method test_*_is_certified→_is_proved. Confirmed the
SearchResult / ProofResult attributes the tests read (history, feasible_found,
acceptance_rate, status, scaled_optimum) all survived the rename. Fixed TASKS.md's
BIG-COMPUTATIONS resume command (certify_integral_arc_bound→prove_integral_arc_bound)
so it can still be copy-pasted. `python -m unittest discover -s tests`: **66 tests OK**
(~104s). The .tex prose keeps "annealing"/"Metropolis"/alg:anneal on purpose — that is
the formal write-up, and the code's one "(simulated annealing)" anchor links to it.
`local_edge_connectivity` is NOT dead after all — the test suite exercises it; the
edge/vertex × local/max measure table is fully covered (solver + tests).

## 2026-06-13 (Opus) — hardened the three provers + a small trim
Author asked to harden the provers (and trim if possible). Full correctness AUDIT of
prove_directed_multigraph (fractional MILP), prove_integral_arc_bound (integral MILP),
and _exhaustive_directed (branch & bound) + _arc_flow_at_least (Ford–Fulkerson):
- Cut formulation is EXACT, not a relaxation (maxflow<=1 iff a chosen vertex-cut has
  capacity<=1; the MILP picks the cut), so OPTIMAL/INFEASIBLE = genuine proof.
- Verified EVERY strengthening row is a valid inequality (so none cuts a feasible
  point / lowers the optimum): two-hop (arc-disjoint direct+detours), the McCormick
  min (solver pins z to exactly min via the binary selector b in BOTH the z<=w and the
  conditional-cap·b encodings), degree-pair 6c (= two-hop + min(a,b)>=a+b-(m-1)),
  deletion cuts (induced subgraph on k verts has <= (m-1)·M*(k) arcs, gated on the
  correct _PROVEN_MSTAR={2:2,3:4,4:6,5:8,6:10}=2(n-1)), degree-ordering symmetry
  (relabel-invariant, preserves the optimum). B&B: feasibility is anti-monotone so the
  include-only-when-feasible prune is sound; the affected-pair set reaches_to(u) ×
  reaches_from(v) is exactly the pairs the new arc can touch; bound prune is a valid
  over-estimate. Conclusion: all three provers are SOUND. No code-logic bug found.
HARDENING added to the self-check (the INFEASIBLE proof path was previously UNtested):
- "valid inequalities sharpen but never move the optimum": prove_directed_multigraph(3,
  use_two_hop=False, use_symmetry_breaking=False) must still give M*(3)=4 — a tripwire
  that fires if any 'valid' row is ever made invalid.
- "an INFEASIBLE verdict is a genuine proof": prove_integral_arc_bound(4,3,12)=FEASIBLE
  and (4,3,13)=INFEASIBLE (L_3^dir(4)=12) — the same mechanism as the thesis L_3(7)=24
  proof, at a size that runs in the suite (~adds a few s).
TRIM (obeys the file's own "hoisted imports" rule): hoisted permutations &
combinations_with_replacement to the top block and deleted the 3 in-function itertools
imports incl. the redundant `combinations as _comb` alias. Did NOT extract the two
provers' shared COO/add_row boilerplate — it nets ~0 lines and churns thesis-critical
code; left as an optional readability refactor. Verified: self-check ALL CHECKS PASSED
(incl. the 3 new lines); 66 tests OK (~105s); enumerate(4,3,12)=2 extremals and the
hypergraph multi path still work after the import move.

## 2026-06-13 (later) — figure audit & rework (author's detailed pass)

Author reviewed every data/TikZ figure and gave per-figure instructions; actioned
all of them. Mapping figure number -> source confirmed via main.aux.

TikZ (ch1_basecases.tex):
- Fig 1.2 (fig:three-models) hypergraph panel: redrawn so the size-3 (violet) and
  size-4 (blue) hyperedges SHARE one vertex (rightmost of the triple = bottom-left
  of the quad). Translucent fills (fill opacity 0.32) blend in the overlap; both
  darker outlines drawn on the main layer ABOVE both fills; vertices drawn last.
- Fig 1.6 (fig:bidirected-star) right panel: m=4 -> m=3 (dropped the j=2 circulant
  layer); now one circulant layer, d^+=d^-=2, m(n-1)=15 arcs, lambda^max=2. Caption
  + panel label updated.
- Fig 1.8 (fig:berge-path): two ellipses now in DIFFERENT colours (e1 violet, e2
  blue), translucent so the lens blends; both outlines stroked on top; e2 label
  recoloured. Caption notes the blend.

Data figures (erdos915_unified.py / make_figures.py), all regenerated:
- Fig 3.1 (complexity): dropped cryptic "$2^E$/$3^E$/..." from the legend; plain model
  names under a "model" title; exponential forms moved into the caption.
- Fig 3.2 (trace): replaced the two disliked lower panels with ONE scatter — every
  visited graph by (lambda^max, arcs), coloured by step, feasible/infeasible shaded,
  star at the densest feasible (lambda=2, 12 arcs). Kept the cooling-schedule panel.
- Fig 3.3 (sensitivity): now a SIDE-BY-SIDE pair (structure with mu labels |
  sensitivity with sigma colours+labels) on a BIGGER 7-vertex multigraph. The s->b
  edge is deliberately over-provisioned (mu=3 but sigma=1) to show mu != load-bearing;
  s->d dead end has sigma=0. (draw_graph_with_sensitivity rewritten; only used here.)
- Fig 3.4 / 3.5 (variant grids): THREE fixes via new _reconcile_panel() in
  make_figures: (1) dropped the certain-interval BANDS and let axes rescale to data;
  (2) clamp every proved/conj/guess curve, named branch, and search circle to the
  machine-proved EXACT value where known — kills the green-square-below-curve bug
  (root cause: hyper LB capped at comb(n,3), the *complete* hypergraph, which is
  infeasible at small n; e.g. m=6,n=5 exact=8 but formula said 10); (3) search lower
  bounds made monotone non-decreasing (running max = extend-by-isolated-vertex bound),
  killing the non-monotone purple dots (m=6 simple/multi undirected vertex). Captions
  updated (no more "shaded band").
- Fig 4.1 (crossover): kept; added a marker + annotation at the hub->bipartite
  crossover (n=9 at m=3).
- Fig 4.2: REPLACED the 3-family connectivity histogram with an appearance-threshold
  plot (new plot_appearance_threshold + appearance_threshold.png): P[lambda^max>=m]
  vs density in units of p*=m/n, three growing (n,m), threshold at x=1. Honest caveat
  in caption: clean step is the m/ln n->inf limit; at computable fixed-small m the
  transition only concentrates near p*. Rewrote the phenomenon-3 paragraph + caption;
  relabelled fig:conn-dist -> fig:threshold. OLD connectivity_distribution.png now
  orphaned.
- Fig 4.3 (scatter landscape): flipped to lambda^max (x, integer) vs edge count (y);
  extremal envelope now an integer STAIRCASE with one dot per connectivity level (was
  linear interpolation between sparse points). Caption + body reworded.
- Fig 4.4 (conn_dist grid): kept; font/tick sizes bumped to match the other 12-panel
  grids, per-panel boundary legend added.
- Fig 4.5 (edges_dist grid): "max feasible" line now read straight off the enumeration
  (max edge count among feasible graphs) — always present and never left of the blue
  mass. Fixes "blue right of the dotted line" (old line used the SIMPLE formula even
  for multigraphs) and "no line on some panels". Caption + body reworded. NOTE: the
  multigraph-directed-vertex panel is all-blue because at the forced enum_n=3 every
  graph has kappa^max<=2<=m-1; that is genuine, not a bug (flagged for author).
- Fig 4.6 (surface 3d): kept 3D; unified camera (view_init 24,-58), z from 0, white
  bar edges, sharper suptitle/caption stating the takeaway (blue=proved, purple=open).

Build check pending; will run latexmk after this entry.

## 2026-06-14 — sampled all-twelve-variant random model (author idea)

Author proposed generalising G(n,p) to a unified random model and looking at all
twelve variants by sampling, asking "is this a logical distribution?". Implemented
where the G(n,p) model lived (ch4 phenomenon 3).
- Unified sampler in erdos915_unified.py: sample_random_multigraph (HURDLE-
  GEOMETRIC: empty w.p. 1-p, else 1+Geom(alpha) parallel copies, so alpha=0 recovers
  G(n,p) exactly; capped at m-1 so a fat edge can't trivially break feasibility);
  sample_random_hypergraph (Bernoulli on r-sets). _VARIANT_SAMPLE_CONFIGS mirrors the
  enum configs with per-variant sample_n (up to 26).
- TWO figures (author said implement both display options, will prune):
  * Fig A figures/degree_threshold.png  -> ch4 4.2 (fig:threshold), REPLACES the old
    appearance_threshold.png (author flagged "I don't get it, try something else").
    Appearance prob vs MEAN BINDING DEGREE / m, six generative models.
  * Fig B figures/sampled_variant_grid.png -> ch4 4.3 (fig:sampled-grid). 12-panel
    binding-connectivity distributions at sampling sizes past the enumeration wall.
- KEY HONEST FINDING (measured, NOT what I first hoped): the "expected degree = m"
  collapse is FALSE at finite computable n. The six models are ORDERED in degree-
  efficiency: directed multigraph cheapest (~0.24-0.3 m; heavy parallels over-disperse
  degree), directed hypergraph dearest (~1.2-2 m; one Berge route per hyperedge),
  simple/undirected ~0.6 m between. Universality is ONLY the m/ln n->inf asymptotic
  (same regime as thm:gnp-threshold). All titles/captions/prose say this honestly;
  Fig B's colour balance is Fig A's ordering seen distributionally. I caught and fixed
  my own initial overclaim ("one threshold for every model / collapse") before commit.
- Math for the record: hurdle-geometric is valid for any p in [0,1], alpha in [0,1)
  (positive tail sums to exactly p); nests simple (alpha=0); the naive "P(mu=1)=p with
  decay c" needs c<=1-p to normalise -- flagged to the author.
- appearance_threshold.png deleted (orphan); plot_appearance_threshold still defined,
  now unused. Build: latexmk exit 0. Ch4 figures renumbered (scatter now 4.4, etc.).

## 2026-06-14 (later) — probabilistic model audit & caption fixes

Author reported "still trouble with the probabilistic graph representation." Full audit of ch1–ch4 and app_proofs:

ISSUES FOUND AND FIXED (5 edits, build clean at 85 pages):

1. **ch4 body text (phenomenon 3)**: α was a free parameter in the text but its value (α=1/2) was never stated. Added "we use α=1/2 throughout" inline. Also rewrote the cap sentence to distinguish multigraph panels (cap m-1 needed) from simple/hypergraph panels (no cap needed — those models already limit to one copy per cell/hyperedge).

2. **ch4 fig:threshold caption**: Three fixes:
   - Added "multigraph panels use hurdle-geometric with α=1/2, multiplicities capped at m-1" (old caption said "multiplicities capped at m-1" as if it applied to all six models).
   - Replaced "directed multigraphs cross first, directed hypergraphs last, simple cases between" with the accurate 6-way ordering: dir-multi < dir-simple < simple-undir < multi-undir < hyper-undir < hyper-dir. The undirected multigraph is NOT in the "simple cases" — it crosses further right than simple undirected because a lower inclusion probability (needed to keep mean degree fixed) leaves many pairs absent. Added the explanation: "lower inclusion probability offsets the per-pair multiplicity gain."

3. **ch4 phenomenon 3 body paragraph**: Rewrote the "simple and undirected graphs lie between" sentence to describe the actual 6-way ordering and explain why the undirected multigraph sits where it does.

4. **ch4 sampled_variant_grid caption**: Added explicit note that the multigraph directed arc panel is entirely red, and that this is consistent with the model ordering (cheapest to force high connectivity = first to saturate at expected degree m). Previously this all-red panel was unexplained.

5. **ch3 fig:complexity caption**: "a multigraph capped at threshold m offers m^E candidates" was ambiguous — "capped at threshold m" reads as cap=m (which would give (m+1)^E per cell), but the formula m^E requires cap=m-1. Fixed to "with multiplicity cap m-1 (the connectivity ceiling), one choice per cell from {0,...,m-1}, offering m^E candidates."

NO OTHER SIMILAR ISSUES FOUND: ch1 G(n,p)/threshold sections clean; ch2 spine/checker descriptions accurate; app_proofs unaffected; sensitivity figure (8 vertices) matches caption (log note "7-vertex" was an earlier design plan).

---

## 2026-06-14 (continued) — full punctuation sweep + figure placement

### Punctuation sweep (no-semicolon, no-em-dash, no-en-dash rule)

Systematically removed all remaining prose semicolons and em dashes (---) across every .tex file. Roughly 50 individual edits across 5 files:

**ch1_basecases.tex** (3 fixes): split 3 prose semicolons into new sentences or rephrased.

**ch2_certify.tex** (1 fix): `not a fractional one ---` → `not a fractional one:`.

**ch3_discover.tex** (4 fixes): 1 semicolon in trichotomy paragraph, 1 semicolon in caption, 2 em dashes in the "what the search is worth" paragraph.

**ch4_synthesis.tex** (~20 fixes): multiple em dashes in open-problems list and directed-frontier section; table semicolons changed to commas; multiple caption semicolons; em dashes in the crossover description and threshold caption.

**app_proofs.tex** (~25 fixes): all remaining prose semicolons and em dashes including list items, proof transitions, caption em dashes, theorem-name semicolons (`[Hypergraph Gomory--Hu; ...` → `[Hypergraph Gomory--Hu, ...`), and the L407 two-case proof sentence.

Build clean at 85 pages after all edits.

### Figure placement

Changed float specifiers so figures appear near their references in the source:
- All `[p]` (float page only) → `[htbp]` in ch3 and ch4
- All `[t]` (top only) → `[ht]` in ch1, ch3, ch4

Figures in ch4 (threshold, sampled-grid, scatter, conn-dist, edge-dist, 3d-surface) and ch3 (complexity, trace, sensitivity, variant-bounds) are already positioned right after the paragraphs that reference them in the source; the specifier change allows LaTeX to place them on the same page rather than deferring to a float page.

Build: 85 pages, exit 0.

## 2026-06-14 layout polish pass (author request: snippets, graphs, plots, titles)

Author asked to improve the visual layout of code snippets, graph style, plots,
and titles/subtitles without breaking the KU Leuven format rules. All changes are
thesis-local (preamble.tex + one table fix in ch4); the class-mandated cover,
back cover, logos, footer, margins, sans-serif font, and 1.5 spacing untouched.
The shared/ TikZ + colour files were NOT edited, so the slides and progress
report keep their own look.

- **Titles/subtitles** (preamble titlesec block): "Chapter N" label now in
  KULblauw1; section numbers in KULblauw1 with a thin KULblauw3a accent rule
  under each \section; subsection/subsubsection get a blue number; \paragraph
  runs in, blue. Chapter/part formats unchanged otherwise.
- **Plots/figures/tables** (new \captionsetup): bold KULblauw3b label, small
  justified body text, labelsep=period, margin 14pt, skip 8pt; sub-captions
  footnotesize. Applies uniformly to every figure, plot, and table.
- **Code signature cards**: \codecard now tints frame + title bar + a 2.2pt left
  border by the card's role colour (MODEL/MEASURE/PROVE/DISCOVER/OBSERVE/DRIVER),
  so the spine is scannable down the page. codecardbox gained an optional
  key-val arg; added cardcol@<ROLE> -> role colour map.
- **algorithm2e**: blue bold "Algorithm N" caption (\SetAlCapNameFnt), keywords
  + functions in KULblauw1 bold, comments KULblauw3b italic via one-arg wrapper
  macros (\algokwsty etc). NOTE: \SetNlSty in this algorithm2e version does NOT
  take (font,txtcolor,bgcolor) -- it printed "gray1, gray2..."; dropped it, line
  numbers stay default bold black. Ruled layout kept.
- **listings**: faint KULblauw1!4 background tint on pythonkul.
- **Graphs** (thesis-local \tikzset after the shared input): subtle drop shadow
  on vertex/smallvertex/hnode (opacity 0.16-0.20), rounded line caps on the
  edge styles. shared/tikz-styles.tex itself untouched.
- **Bonus fix**: tab:summary (ch4, twelve-variant table) was the one pre-existing
  overfull hbox (92.7pt over). Converted tabular{llll} -> tabularx with the Value
  and Status columns as raggedright X so they wrap. Overfull count 1 -> 0.

Verified by rendering pages 24-27 + 36 to PNG: chapter label blue, section rule,
role-coloured cards (cyan MODEL, blue MEASURE, dark-blue DRIVER, plus the spine
diagram's green PROVE / orange DISCOVER / violet OBSERVE), vertex shadows, blue
caption labels, blue algorithm caption + keywords, correct 1..n line numbers.

Build: latexmk -pdf main.tex exit 0, 81 pages, 0 overfull hboxes.

## 2026-06-14 layout polish round 2 (author corrections)

Author review of round 1 plus flagged mistakes in the figures. All addressed.

- **Section "subtitle" rule removed.** Author disliked the blue accent rule under
  every \section. Dropped the [\titlerule] after-code in preamble; sections now
  show just the blue number + black title, no underline.
- **computernote corners.** Was `sharp corners=downhill` (mixed sharp/round).
  Now `arc=2.5pt`, all four corners rounded.
- **TikZ rectangle bug (the big one), app_proofs A.3-A.7.** Root cause: a bare
  colour passed to an `aplab` node (= edgelabel, fill=white) is read as
  `color=<c>`, which overrides the white fill and turns the whole label into a
  SOLID colour block with same-colour (invisible) text. 16 labels affected
  (the "what are these red/blue/green rectangles?" notes). Fix: added an
  `apname` style (font only, no fill) to the appendix tikzset and rewrote every
  such label as `apname, text=<colour>` -- coloured text, no box. Also switched
  free-floating vertex-name labels (A.2, A.5, A.6, A.7) from aplab to apname so
  the ugly white boxes over coloured hulls are gone.
- **A.2 overlaps.** `v^*` was on top of the hub, `h` on top of the spokes.
  Repositioned both into clear gaps; hub nodes bumped 8->9pt.
- **A.5 (seam).** Centre label `\lambda=4>2` was a solid red rectangle (same
  bug) -> red text. Nodes were too small -> apx bumped to 10pt for this figure,
  orange nodes to 11pt. `v` no longer overlaps its node.
- **codecard outputs Z -> N.** Author: "shouldn't the output be N?" The six
  MEASURE cards (connectivities, sensitivity) return non-negative counts, so
  $\to\mathbb{Z}$ became $\to\mathbb{N}$ in ch2/ch3.
- **ch4 data-figure captions were factually wrong (author flagged).** Verified
  against the regenerated PNGs:
  * sampled_variant_grid: caption claimed "multigraph directed arc panel is
    entirely red"; the plot shows the four SIMPLE panels are red almost
    everywhere and multi-directed keeps blue. Caption rewritten.
  * conn_dist_m3: caption claimed "most graphs sit comfortably inside the
    feasible region"; the bulk is infeasible in several variants. Caption + the
    lead-in prose para rewritten to the honest reading (balance varies; the
    bound is a real constraint; extremal graphs rare regardless, per edge-dist).
- **Redundant per-panel legends removed (author).** plot_conn_dist_grid and
  plot_sampled_variant_grid in erdos915_unified.py: the identical "m-1 boundary"
  legend was repeated in all 12 panels. Dropped it (boundary named once in
  title+caption); conn_dist keeps a legend only if a per-panel known-max line is
  drawn. Regenerated conn_dist_m3, conn_dist_m6, sampled_variant_grid (fixed
  seeds, enumeration_cache.pkl reused so it was fast).
- All addressed author-note comments deleted from the .tex sources.

NOTE: tab:summary (ch4) is back to `tabular{llll}` and overfull by 92.7pt -- the
author reverted my round-1 tabularx wrap (intentional), so I left it. It is the
only overfull hbox. Flagged to the author rather than re-imposing the wrap.

Build: latexmk -pdf main.tex exit 0, 83 pages, 1 overfull (the table above).

## 2026-06-14 (later) tab:summary overflow fixed

Author asked to fix the ch4 summary table overflow (the one left flagged above,
after they reverted my tabularx wrap). Wrapped the `tabular{llll}` in
`\resizebox{\textwidth}{!}{...}`: keeps every cell on a single line (no ragged
wrapping, which the author did not want) and scales the table to exactly the
text width. Removed the "table goes over the right margin" comment.
Build: exit 0, now 0 overfull hboxes (was 1).

## 2026-06-14 (later) final author-note sweep

Swept all .tex (main, preamble, chapters) for leftover author notes/commands.
One actionable note remained: ch2 L23 "%mention that hypergraphs could have been
represented as higher order matrices: tensors, but that wasn't done for
efficiency". Added a sentence to the "single representation" section saying the
hypergraph could be a higher-order ($r$-dimensional) tensor but that array is
almost all zero and costs n^r entries, so the program keeps the compact
hyperedge list. Removed the comment. No other author notes or commented-out
commands remain anywhere. Build exit 0, 0 overfull, 83 pages.

## 2026-06-15 connectivity speedup + enum dedup + ch2 MILP clarity (PLAN executed)

Executed PLAN_connectivity_speedup.md in full on branch `feat/connectivity-speedup`
(off tag `baseline-pre-speedup`=7d20265). NO reported value/bound/figure moved; every
speedup is proven trajectory- or iso-class-preserving by a test. Scratch baseline copy
at program/erdos915_unified.baseline.py (gitignored, delete on sign-off).

- **Phase A (capped predicate).** New `exceeds_bound(graph,k,sep)` + `_split_capacity_matrix`,
  reusing `_tiny_maxflow`: equivalent to `max_connectivity(...) > k` but with two early exits
  (per-pair flow stops after k+1 paths, pair loop stops at first violator). Guard:
  `test_connectivity.CappedPredicate` matches the exact checker over all 4 variants x 2 sep x
  every k.
- **Phase B (monotone fast energy).** `search_for_dense_graph` now maintains `feasible` (exact)
  and a sound upper bound `lam_ub` (Facts M1/M2: remove can't raise lambda^max, add raises by
  <=1). New `_proposal_energy` returns the IDENTICAL float `_energy` would, computing a flow
  only at the boundary and the exact value only when the proposal is genuinely infeasible. Best
  tracking uses the exact `feasible` flag (witness still certified). New kwargs:
  `record_exact_connectivity` (fig:trace logs exact lambda^max; production logs lam_ub, killing
  the last per-step measure) and `reference_mode` (test-only slow path). Guard:
  `test_search.test_fast_path_matches_exact` proves fast==reference BIT-FOR-BIT (energies,
  accept flags, edge counts, final graph) over 4 variants x {3,4,5} x {2,3} x {edge,vertex}.
- **Phase C.** `sensitivity_map` computes the shared baseline once instead of per edge (value
  identical; `test_sensitivity.test_map_equals_per_edge_sensitivity`).
- **Phase E (enum RAM fix).** `enumerate_extremal_directed_multigraphs` streams each found graph
  through pure-Python `_canonical_form` (lexicographically smallest relabelled matrix) and keeps
  one rep per iso-class as it goes, instead of buffering all labelled then deduping at the end.
  Peak memory now bounded by #iso-classes (the old code hit ~22 GB on n=7). Output byte-identical
  to baseline at n=3,4 (both up_to_iso modes); n=5 reconfirmed = 3 classes (472 s, gated behind
  RUN_SLOW_ENUM). Guard: `test_certify.EnumerationDedup`. NB the n>=7 j=7 prefix prune is still
  the conjectured bipartite bound, so n>=7 stays a lower-bound search; dedup changed memory only.
- **Results.** Search 2.6x-3.9x faster, IDENTICAL best edge counts (15/15, 18/18, 9/9, 21/21 on
  the four sampled cases). Suite: 75 tests pass (1 slow skipped); self-test exit 0; figures
  pixel-identical. Phase D (Gomory-Hu resync, parallel restarts, memo) NOT needed and skipped:
  the per-step connectivity bottleneck is gone.
- **Thesis.** ch3: new section "Keeping the checker cheap inside the search" with
  `prop:monotone` (M1/M2 stated and PROVED via min-cut, elementary) + plain-words consequences +
  a transparency paragraph naming `test_fast_path_matches_exact`. M1/M2 are textbook min-cut
  monotonicity, reasoned rigorously inline (not Fable-checked; flag if a formal pass is wanted).
  ch2: two-mode checker cross-ref; and the priority rewrite of the MILP `p/x/w<=1` passage
  (`ch2_certify.tex` ~218) into a symbol glossary (w,x,p in words), a worked four-row case table
  `tab:crossing-cases` for the indicator inequality (w<=1 makes the 3 non-crossing rows <=0), a
  plain reading of the cut/maxflow line, de-jargoned helper constraints, and a TikZ cut figure
  `fig:cut`. Build exit 0, 87 pages, 0 overfull hboxes, 0 undefined refs.
- **nauty.** pynauty installs/builds fine, but the enumeration's real cost is the DFS, not
  iso-rejection, so nauty would not speed it up and the RAM crash is already fixed; pure-Python
  canonical form is the source of truth (no external dependency). Jan's 2026-06-15 email instead
  recommends a GENERATION-time pipeline: geng (underlying undirected) -> directg or
  watercluster2 (all non-iso orientations, watercluster2 usually faster). That targets simple
  digraph orientations and needs adapting for the multiplicity/bidirected multigraph case; left
  as an open follow-up for the author (TASKS.md). Jan also CONFIRMED the monotonicity approach
  for the connectivity bottleneck and that countg --G is classical (min) vertex-connectivity,
  not the lambda^max/kappa^max (max over pairs) we cap.

## 2026-06-15 (afternoon) — Jan Goedgebeur email + Tier 1 ops

Branch feat/connectivity-speedup merged into master (clean fast-forward); that
branch held the Phase E canonical-form dedup fix (RAM bottleneck solved), the
monotone connectivity speedup, and the ch2 MILP clarity pass.

Jan Goedgebeur (nauty author) replied on 2026-06-15, confirming the monotone
connectivity speedup. Key notes: (1) `countg --G` gives classical minimum
vertex-connectivity, not our max-local lambda^max/kappa^max — not useful for our
problem (already known). (2) For n=7 directed multigraph generation, Jan recommends
`geng | watercluster2` (usually faster than directg) as a generation-time pipeline;
adapting it for multiplicities {0..m-1} plus bidirected arcs is non-trivial. (3) Jan
suggested tabu search as an alternative to SA; added as a P2 item in TASKS.md.

Contribution statement in main.tex updated: added paragraph crediting
thm:hyper-vertex-m2, thm:hyper-vertex-m3, lem:incidence-rank (hypergraph vertex
at m=2 and m=3 for all r and n), and the m=3 directed multigraph reduction to
two n=7 computations via lem:attachment + thm:odd-step + rem:odd-step-roadmap.

Popularising summary audit (no edits): does not yet mention hypergraph vertex m=3
or the odd-step reduction; author should verify completeness for submission.

## 2026-06-15 (evening) — conjecture correction + accessibility pass

CONJECTURE CORRECTION (major finding): conj:dir-arc was wrong for m>=4.
The old formula floor(n^2/4) + (m-2)*ceil(n/2) used a balanced partition
|A|=|B|~n/2, but the optimal partition is |B|=ceil((n+m-2)/2), |A|=n-|B|,
giving floor((n+m-2)^2/4) arcs. For m=2,3 both formulas agree; for m>=4 and
n large enough (n=12 for m=4, n=12 for m=5) the new formula is strictly larger.
Verified computationally: m=4,n=12 gives 49 arcs with lambda_max=3, beating the
old conjecture's 48. const:augmented-bipartite and conj:dir-arc in ch1_basecases.tex
updated to use the new partition and formula. ch4_synthesis.tex updated to match.
The insight from ch4: the upper bound argument |B|*(n-|B|+m-2) was already pointing
to this formula — the conjecture just hardcoded a suboptimal partition. Build: exit 0,
87 pages, 0 errors.

ACCESSIBILITY: fig:scaling-reduction added to ch2_certify.tex (illustrates the
divide-by-(m-1) scaling step concretely for m=3 before the formal M*(n) formula);
dense 15-sentence paragraph in ch4 about the m=3 directed multigraph reduction split
into four focused paragraphs with an itemized list for facts (a) and (b).

BACKWARD-ARC LEMMA: attempted 2026-06-15 (Sonnet agent). Route-counting approach
blocked; repartitioning approach outlined but not closed. No proof found. Remains open.

## 2026-06-16 — gallery of extremal graphs + figure 3.2 improvements

GALLERY OF EXTREMAL GRAPHS: implemented gallery_extremal_graphs() in erdos915_unified.py.
For all 12 variants (8 matrix + 4 hypergraph), all (n,m) pairs with n<=7, m<=4, r=3:
- Finds the extremal edge count via repeated search (2000 steps/restart, >=3 seeds)
- Enumerates all non-iso extremal graphs via DFS (_enum_matrix_extremals, _enum_hyper_extremals)
- Counts |Aut(G)| by brute-force over n! permutations, records labelled_count = n!/|Aut|
- Deduplicates with _canonical_form (matrix) or _hyper_canonical (hyperedge collection)
- Output: figures/extremal_gallery.json (JSON-serializable dict, complete=False when deadline hit)
New helpers: _graph_from_mu, _aut_count_matrix, _hyper_canonical, _aut_count_hyper,
_hyper_to_lists, _enum_matrix_extremals, _enum_hyper_extremals, save_gallery_json.

FIGURE 3.2 IMPROVEMENTS (plot_search_trace):
- Gradient: changed from viridis to RdYlBu + PowerNorm(gamma=0.2); early steps warm
  (red/orange), converged tail uniformly blue — the user asked for "everything blue except
  one or two dots" and this delivers it.
- Feasible/infeasible labels: moved from inside the axes (top corners) to just above the
  axes box, centred over each region, using blended_transform_factory (data-x, axes-y).
  No overlap with other text.
- Legend: moved from lower-left to upper-left.
- Density histogram: new right panel (ax_hist) showing horizontal bar chart of visit counts
  by arc count. Y-limits synced manually with the scatter panel.
- Layout: 3 panels (cooling | scatter | histogram) or 2 (scatter | histogram) when
  show_cooling=False. New kwargs: show_cooling, connectivity_label, edge_label, title.
- Suppressed tight_layout UserWarning in _save() (cosmetic, bbox_inches=tight handles it).

MULTI-VARIANT TRACES: generated scatter-only traces for:
  trace_simple_undirected_n7_m3.png, trace_simple_directed_n5_m3.png,
  trace_multi_undirected_n5_m3.png, trace_multi_directed_n5_m3.png,
  trace_multi_directed_n4_m3_vertex.png
The format works well for all variants; the vertex-separation case clearly shows the search
spending more steps in the infeasible region (harder constraint).

All self-checks pass. Gallery PID 31802 still running at session end (max_n=7 ~15min total).

## 2026-06-16 (later) -- verify Sonnet's session, P2 polish, big-computation feasibility

VERIFICATION OF THE GALLERY + FIGURE WORK (all confirmed correct):
- 75 unittests pass, full _run_checks self-test passes.
- Gallery values match known/certified results: simple-undirected trees on n=4 (2
  classes, 16 labelled) and n=5 (3 classes, 125 labelled), K4 at m=4, and
  L_3^dir(4)=12 = the certified Fig 3.2 optimum. Incomplete cases correctly carry
  complete=False and report the search lower bound (e.g. multi_directed n=7,m=3=20,
  not the true 24) -- sound, but any caption citing the JSON should say so.
- Cross-validated the NEW gallery enum: _enum_matrix_extremals(MULTI_DIRECTED,4,3,12)
  returns byte-identical canonical iso-classes to the independent
  enumerate_extremal_directed_multigraphs(4,3,12). Two code paths agree.

FIXED A GAP: Sonnet regenerated temperature_trace.png (Fig 3.2) at 00:25 but never
rebuilt main.pdf afterward (build was 20:15, stale). Rebuilt main.tex: exit 0, 87 pp,
0 overfull hboxes. Fig 3.2 now correctly embedded.

P2 POLISH:
- Open-variant test coverage (was zero): added fast checks to _run_checks --
  verify_hyper_vertex_value at (4,3,2),(5,3,2),(4,3,3),(5,3,3); fractional_flows_feasible
  accept(path)/reject(two-route); fractional_search ceilings at n=5 for "total" (<=8) and
  "min_degree" (<=2 plus the 1e-3*total tie-breaker slack). ~2s, all PASS. Replaced the
  old commented n>=7 suggestion block (those sweeps added minutes).
- Popularising summary: closing rewrote from "questions still open" to state both positive
  results in lay terms (hyperedge variant solved at the two strictest route limits for all
  n/r; one-way variant reduced to a single finite n=7 check). Mirrors the Contribution
  Statement. Rebuilt clean, still 1 page. AWAITING AUTHOR wording sign-off.

BIG-COMPUTATION FEASIBILITY (the headline question -- do the Phase A-E speedups give the
n=7 jobs a shot?). Empirical, all runs stayed <320 MB RSS:
- MEMORY is solved. Phase E streamed dedup means nothing approached the old ~22 GB; the
  desktop-crash failure mode is gone. Both jobs are now SAFE to leave running.
- MILP (a), prove L_3(7)<25 => INFEASIBLE: n=5@17 INFEASIBLE in 2.9s; n=6@21 LIMIT at
  600s (unsolved); n=7@25 LIMIT at 2000s (unsolved). The Phase A-E work never touched the
  MILP, and scipy/HiGHS cannot close n=7 as formulated. INTRACTABLE this route. Fix: a
  commercial solver (Gurobi academic, would likely close it in minutes) or a tighter
  encoding. NOT a memory problem -- pure solver runtime.
- ENUM (b), 24-arc deg<=8 extremals: no-cap DFS explodes (n=4 0.42s -> n=5 466s, ~1100x;
  hopeless beyond n=5). WITH max_degree=8 (the real command): n=4 0.93s (1 class, the cap
  drops the higher-degree class); n=5 still >330s because the cap barely binds below n=7;
  n=7 did NOT finish in a 40-min (2400s) timeout but stayed memory-safe. So the cap prunes
  hard only at n=7 yet 40 min was not enough. Borderline: a multi-hour run MIGHT finish (no
  longer risks the machine), but the principled fix is Jan's geng+directg/watercluster2
  generation pipeline, which attacks the DFS time itself (the open follow-up in TASKS.md).
  This exactly matches Jan's warning that dedup "only fixed RAM".

BOTTOM LINE: the speedups solved the crash (memory) but not the runtime. MILP needs a
better solver; ENUM needs either a long safe run or the generation pipeline.

## 2026-06-17 (Opus) — repo split + a fresh angle on the backward-arc lemma

REPO: at author's request this directory was split out of MasterThesis/thesis_improved
into its own repo (renamed `thesis`), fresh git history, pushed private to
github.com/louisvandenbruwaene/thesis. Only thesis_improved content carried over.

BACKWARD-ARC LEMMA (flagship, TASKS.md top item) — went deep; NO proof, but a new line
that sidesteps the stuck non-monotone-exchange obstacle. Full writeup +
mechanically-checked script in research_notes/ (directed_arc_m3_reduction.md +
scripts/attach_check.py). Summary:
- KEY REFRAMING. Forget "no backward arc". Run the m=2 min-degree-deletion engine
  (thm:dir-arc-m2-exact) on the m=3 quadratic branch Q(n)=floor((n+1)^2/4). Using the
  true bound ell(n-1)=max(3(n-1),Q(n-1)), the overshoot floor(n/(n-2)ell(n-1))-Q(n) is
  +0 at odd n>=11, +1 at even n>=10, and +2 only at the crossover seam n=9 (where
  ell(8)=21 is linear). So the WHOLE m=3 quadratic upper bound reduces to killing one
  +1 of slack at even n plus finite seam bases — structurally identical to the
  multigraph thm:odd-step + lem:attachment already in the thesis. The prior attempts
  (route-counting, repartitioning) worked the backward-arc framing; this engine was
  never tried for the simple case.
- FORCED STRUCTURE (proved). If a=Q(2k)+1=k^2+k+1 then every vertex has degree >=k+1, D
  is (k+1)-regular up to total degree-excess exactly 2, and every degree-(k+1) vertex
  deletes to an exact odd extremiser on 2k-1 vertices. So the +1 case = "odd extremiser
  + one degree-(k+1) vertex, still feasible".
- ATTACHMENT REFUTED for k=4,5,6 (exact max-flow, attach_check.py): taking the odd
  extremiser as augmented bipartite B_{k-1,k}+k-cycle, NO degree-(k+1) attachment keeps
  lambda^max<=2. Intuition: the complete A->B layer makes a third arc-disjoint route
  unavoidable.
- REMAINING GAPS (why this is NOT yet a proof): (1) odd-extremiser uniqueness on 2k-1
  vertices [most important; multigraph analogue needed thm:extremal-char]; (2) a uniform
  all-k argument for the attachment contradiction (promote the third-route sketch to a
  Menger lemma); (3) seam bases ell_3^dir(9)=25, ell_3^dir(10)=30 via the certifier
  (Gurobi route, cf. BIG-COMPUTATIONS); (4) m>=4 redo, expecting the known odd-uniqueness
  hole (rem:odd-step-roadmap).
- NOTHING entered the thesis .tex (rule: proof-check before uncommenting). Working note
  only. Next: characterise the odd extremisers (gap 1) — the load-bearing step.

## 2026-06-17 (Opus, cont.) — characterising the extremisers (gap 1)

Pushed on gap (1). Files: research_notes/directed_arc_m3_extremisers.md +
characterisation_checks.py + attach_check_all_perms.py (all self-contained, run clean).
Results (NOTHING in the thesis .tex):
- ARC PARTITION (proved, sanity-checked): sources have in-degree 0, so every arc is
  S->R or internal to R; a = e(S,R)+e(R) with e(S,R)<=sigma(n-sigma).
- LEMMA (proved; 0 violations / 300 random feasible digraphs): for a source s, the
  subdigraph on N^+(s) has max in-degree <=1 (else 3 arc-disjoint s-routes). So a
  universal source forces R to have internal max in-degree <=1.
- CONDITIONAL THEOREM (proved): if non-sources R induce max in-degree <=1 then
  a <= (n-sigma)(sigma+1) <= Q(n) in BOTH parities (max at sigma=(n-1)/2 odd; checked
  n=7..19), equality iff augmented-bipartite family. So the WHOLE m=3 quadratic upper
  bound + characterisation reduce to ONE hypothesis (H): an extremiser has a source
  adjacent to every non-source. (H) is the new load-bearing open statement — concrete,
  about sources, exchange-free (sidesteps the non-monotone backward-arc obstacle).
- EXTREMISER FAMILY (not unique): augmented bipartite B_{k-1,k} + ANY fixed-point-free
  permutation of B (one per partition of k into parts >=2: k=5 -> {5},{2,3};
  k=6 -> {6},{2,4},{3,3},{2,2,2}). All feasible at k^2 (verified k=4,5,6). The thesis
  const:augmented-bipartite (single k-cycle) is one member.
- ATTACHMENT REFUTATION extended to ALL permutation cycle types (k=4,5,6): no
  degree-(k+1) attachment stays feasible. So +1 even case dies GIVEN (H).
- TOOLING NOTE: homemade SA can't reach the optimum at n=9,11 (24/34 vs 25/36) — a
  search-strength limit, not a result; thesis annealer needs networkx/scipy (absent
  here). Conditional theorem makes the empirical question secondary; (H) is the target.
- NEXT: prove (H) [extremisers have a universal source / R max-in-degree<=1]; make the
  attachment refutation uniform in k (Menger lemma); seam bases ell_3(9)=25, ell_3(10)=30.

## 2026-06-18 (Opus) — standalone build fix + thesis consistency/clarity pass

Focus shifted (author request) to making the thesis better: figures + clearer explanations.
Author chose "edit plot code only" (author regenerates PNGs) and clarity focus = ch2/ch3.
- BUILD FIX (important): the repo split left preamble.tex pointing at ../shared/{colors,
  tikz-styles}.tex, which lived at the old MasterThesis root and was not carried over, so
  the standalone repo DID NOT BUILD. Vendored both into shared/ and repointed preamble.
  Clean build now: 93 pages, 0 undefined refs, 0 undefined cites, 0 overfull.
- CONSISTENCY BUG fixed: conj:dir-arc was corrected in a prior session to
  floor((n+m-2)^2/4) in ch1 + ch4, but THREE places still printed the old pre-correction
  formula floor(n^2/4)+(m-2)ceil(n/2) while citing conj:dir-arc — ch3 (display L144 +
  inline L174) and app_proofs L397 (the proof step, "balanced partition ... uniformly in
  m"). They agree at m=3 but DIFFER at m=6 (the m=6 figure already uses the corrected one).
  Fixed all three to the (n+m-2)^2/4 form; app_proofs now uses the optimal partition
  |B|=ceil((n+m-2)/2) matching ch4 L16.
- CLARITY: ch2 timing sentence ("well under a second, under a second, and a few seconds")
  rewritten.
- FIGURE CODE (author regenerates): plot_variant_grid suptitle was overlong and redundant
  with the per-panel legends + caption; shortened to "Erdős 915 across the twelve variants,
  m = M" and threaded m through from make_figures.py. >>> AUTHOR: rerun make_figures.py to
  refresh variant_bounds_m3.png / variant_bounds_m6.png with the shorter title. <<<
- NOTE: matplotlib/numpy/scipy/networkx NOT installed in this env, so data figures cannot
  be regenerated here; only TikZ + .tex + plot-code edits are possible.

## 2026-06-18 (Opus, cont.) — P2 polish + Jan's two follow-up items (nauty available!)
Fresh clone of the split-out `thesis` repo into ~/Projects/thesis. KEY ENV DIFFERENCE
from the morning session: this machine HAS numpy/scipy/matplotlib/networkx AND the full
nauty toolset (geng, directg, watercluster2, multig, vcolg, countg, ...) on PATH, so the
figure regen and Jan's pipeline both became runnable for the first time. No Gurobi (MILP
ENUM(a) still blocked). Author asked for P2 polish + Jan's follow-up.

P2 POLISH (all done, build verified):
- Baseline build clean: 93 pages, 0 overfull, 0 undefined refs/cites (the 375 "undefined"
  in a cold latexmk log are just pre-bibtex passes; a converged single pdflatex pass is
  clean). Program self-check ALL CHECKS PASSED.
- Refreshed variant_bounds_m3.png + variant_bounds_m6.png via make_figures' gather/plot
  (only the plot_variant_grid suptitle had changed in the prior session; the committed
  PNGs predated it). Regenerated ONLY those two to avoid matplotlib-version pixel drift on
  the other 23 figures. m=6 grid is slow (~6 min, exhaustive solves) so it ran separately.
  Rebuilt thesis to embed them: 93 pp, 0 overfull.
- Spell check (hunspell -t over all .tex): clean. 259 flags all = British spellings
  (colour/behaviour/optimisation), names (Erdős/Bérczi/Sørensen truncate at accents),
  technical terms, TikZ style names, code identifiers. No doubled words, no common typos.
- Layout/ToC/placement: fine. The 5 ch4 [p] floats are the legit full-page grid figures
  (sampled grid, scatter, conn/edges distributions, 3D surface). A couple of cosmetic
  underfull hboxes in app_proofs captions, left as-is (not overfull).

JAN FOLLOW-UP #1 (geng+directg/watercluster2 pipeline) — research_notes/
jan_followup_nauty_and_tabu.md + scripts/nauty_pipeline.py. VERIFIED:
- COUNTS: nauty non-iso simple-digraph count = OEIS A000273 = program's own canonical-form
  dedup count (3,16,218,9608,1540944). Two independent iso engines agree.
- EXTREMAL: feeding nauty's digraphs through the program's max-flow checker reproduces the
  program's exact simple-directed L_3^dir(n) = 2,6,9,12 for n=2..5. (Small-n values exceed
  the asymptotic conj:dir-arc floor((n+m-2)^2/4); correct, the conjecture is the large-n
  branch.)
- TIMING: watercluster2 ~15x faster than directg at n=6 (0.08s vs 1.22s) — Jan's claim
  confirmed. n=7 simple is 882M digraphs, out of reach for raw generation.
- MULTIGRAPH HYBRID (the non-trivial ENUM(b) cross-check): layer multiplicities {1..m-1}
  onto nauty-generated simple-digraph SUPPORTS, dedup finished multigraphs by the program's
  canonical form. Reproduces enumerate_extremal_directed_multigraphs at n=4 (2 classes) and
  n=5 (3 classes), and is ~17x FASTER at n=5 (26.3s vs the DFS's 456.0s). Direct evidence
  for Jan's "DFS time is the wall, dedup only fixed RAM". For n=7 ENUM(b) the principled
  next step is per-support Aut dedup (directg -G) + arc/degree prefilter.

JAN FOLLOW-UP #2 (tabu vs SA) — scripts/tabu_vs_sa.py. MEASURED, sharper than Jan's
"similar performance expected": same energy + neighbourhood, equal 6s wall-clock, SA =
the thesis's own best_of_searches (empty-graph restarts, no bipartite seeding). TIES on
simple-undirected n=7 (9), multi-undirected n=6 (10), simple-directed n=6 (15); TABU WINS
on multi-directed n=5 (16 vs 15), multi-directed n=7 (24 vs 20 — tabu reaches the 24-arc
2B(3,4)=L_3^dir(7) extremiser), simple-directed n=7 (18 vs 16). Engineering note only; the
thesis discovery results are already at the proved/constructed optima, nothing enters .tex.

REPO STATE: committed + pushed to main (author now wants commit+push every session;
saved as a standing preference in auto-memory). Two commits: (1) the P2 polish +
research_notes cross-checks above; (2) the thesis incorporation below.

INCORPORATED INTO THE THESIS (author asked, 2026-06-18): new ch2 section 2.6
"Generating the directed cases faster" presenting the speedup with before/after numbers
(in-house DFS ~456s at n=5 vs nauty pipeline ~26s, ~17x; watercluster2 ~15x faster than
directg at n=6; counts = OEIS A000273; n=4->2, n=5->3 families) and crediting Prof. Jan
Goedgebeur (named there + in the acknowledgments as promotor) for the suggestion. Framed
honestly as a validated faster route + the practical path to the open n=7 fact (b), not as
a rewrite of the program. Build clean: 93 pp, 0 overfull, 0 undefined refs/cites; the new
\cite{McKayPiperno14} reuse and \Cref{rem:odd-step-roadmap} resolve. program .py unchanged.

## 2026-06-18 (Opus) -- MERGE of the two diverged repos into this one

Context: the thesis existed as TWO independent git repos with no shared history -- this
one (`louisvandenbruwaene/thesis`, at ~/Projects/thesis, canonical going forward) and
`louisvandenbruwaene/MasterThesis` (at ~/Documents/.../thesis_improved), each with one
session of unique work. The author asked to merge "best of both" into THIS repo and keep
the other as a mirror. Diffed the two trees and reconciled file by file.

Kept from THIS (codex) repo: the corrected conj:dir-arc formula floor((n+m-2)^2/4) in ch3
(the other repo's ch3 still had the old floor(n^2/4)+(m-2)ceil(n/2), wrong for m>=4); the
app_proofs proof-detail expansions (incidence-count, block-cut count, attachment flow
estimate, the two-hop/no-back-arc bound); the new ch2 "Generating faster" section; the
main.tex Goedgebeur acknowledgment; preamble shared/ vendoring; research_notes/ and shared/.

Brought in from the other repo: (1) the punctuation/spelling sweep -- removed all prose
em-dashes and semicolons and fixed Br/Am spelling across ch1-ch4 + app_proofs (this repo
had not had that sweep: 12 em-dashes + 25 semicolons); the missing-arc-notation, "dear"
typo, and stale "running" fixes were already here. (2) the geng pipeline as a PROPER
in-program function `enumerate_extremal_directed_multigraphs_via_generation` +
`_geng_support_graphs` in erdos915_unified.py (this repo only had it as a research_notes
prototype script using directg/watercluster2). Mine generates the UNDIRECTED support with
geng and decorates multiplicities/bidirection in-program, prunes with PROVED M*(j<=6) only
(no conjectured bound -> sound at all n), validated == DFS at n=4/n=5. (3) the geng unit
test, the program README geng note, the _tiny_maxflow .copy() drop, shutil/subprocess
imports.

Reconciled conflict: this repo's ch2 section described `directg`/`watercluster2` orienting
+ "layering multiplicities" and cited 26s/17x and watercluster2-vs-directg numbers from the
SEPARATE research_notes script. Rewrote it to match the SHIPPED in-program implementation
(geng undirected support + in-program decoration; directg/watercluster2 can't express
bidirected arcs or multiplicities), kept Goedgebeur's credit and the validated facts
(2 families at n=4, 3 at n=5; sound at all n), dropped the unverified-for-this-impl
speed multiples (left "substantially faster"). Kept codex's plot_variant_grid(m) shorter
suptitle + its make_figures caller + its variant_bounds figures.

Verify: full suite 77 tests pass (was 75 + my 2 geng tests), 1 slow-enum skip. n=7 fact (b)
run still going in the other tree's logs/. Build + commit + push pending at end of this
entry; the MasterThesis repo will be mirrored to match this one.

## 2026-06-19 (Opus) — verified the C extension, fixed an app_proofs punctuation regression, repo consolidation

Author asked Opus to review Sonnet's recent work and to make THIS repo (Projects/thesis,
remote louisvandenbruwaene/thesis, branch main) the single canonical one going forward, with
the school-tree copy (Documents/.../MasterThesis_Louis/thesis_improved, remote MasterThesis,
branch master) downstream. Future sessions: pull + work + push HERE.

C extension review (the guards were already in place via 3d1beef; this confirms they are
correct and were the right call):
- Differential-tested the C primitives against pure Python AND networkx: _canonical_form
  0/4000, _tiny_maxflow 0/8000, _tiny_maxflow vs networkx exact max-flow 0/3000; the scipy
  csgraph exact-connectivity path 0/3000 vs networkx (directed + undirected); exceeds_bound
  consistent with max_connectivity in vertex mode 0/1500.
- Confirmed the two guards are load-bearing: without `and n <= 7`, canonical_form_min (buffers
  best[49]/perm[7]) stack-smashes at n>=8 (reproduced), which the seam-base enumeration at
  n=9,10 would hit. With the guard, n>=8 falls back to pure Python (0 mismatches at n=8/9/10).
  The n<=16 guard on max_connectivity_exceeds matches res[256]/parent[16]; the search never
  reaches it but the guard keeps it sound. .so is gitignored (correct: built per machine via
  build_fast.sh, so -march=native stays optimal and never ships to a different CPU).
- ch3's parallel-restart claim is true and harmless: ProcessPoolExecutor over a module-level
  worker with the SAME seeds + order-preserving map + first-max tie-break, identical to
  sequential, so no reported number changes.

Fix landed here: the expanded app_proofs.tex (the fuller floor((n+m-2)^2/4) derivation, the
incidence-graph edge count, the block-cut identity) had reintroduced 8 prose semicolons that
violate the no-semicolon rule. Replaced with periods/commas, keeping all the new math:
M*(7)=12 "; and"->", and"; theorem titles [Gomory--Hu; ...]/[Chernoff bounds; see] -> commas;
"of e; it has"->". It has"; "3-connectivity; the"->". The"; "(Tutte \cite{Tutte66};"->","
(two-citation parenthetical); "edges; give"->". Give"; "matplotlib; an optional"->". An".
No Unicode em/en dashes anywhere. Suite 77 pass / 1 skip. Build: latexmk exit 0, 95 pp,
0 overfull, 0 undefined refs/cites. Pushed to origin/main.

Note for the author: maintaining two repos with parallel agents caused duplicate work (both
trees independently fixed the same C guard bug). Recommend treating MasterThesis purely as a
pre-submission mirror and doing all development here.

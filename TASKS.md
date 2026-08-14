# Task queue (read this first; keep under ~80 lines)

Status: TODO | IN PROGRESS | BLOCKED(by) | AWAITING AUTHOR | DONE→delete after logging
Completed 2026-06 blocks (SA-vs-tabu, parallel geng, conj:min-degree numerics, review
fixes, C extension, Jan follow-up, P2 polish) and the 2026-07-30 review-fix/phase-2
batch (Whitney inversion, five overclaims, error term to O_m(n), multigraph vertex
alt-convention, Case 2 tightness, S-T threshold, Leonard citation fix) are all logged
in claude.md and deleted here.

## OPEN — multigraph vertex, alternate convention (new section A.8)
- [x] **conj:multi-vertex REFUTED for all m>=5 (2026-07-31).** thm:clique-chain-vertex:
      chaining thickened K_r blocks (r~m/2 optimal) through single bridge
      vertices beats the thickened tree by an amount growing LINEARLY in n
      (a single triangle already does it, gain=m-4 per triangle, for every
      m>=5). True growth rate in m is Theta(m^2), not Theta(m). Proved by hand
      (cut-vertex argument) + double-checked (program's exceeds_bound AND an
      independent from-scratch networkx max-flow). research_notes/
      multi_vertex_clique_chains.md. The m=5/m=6 tab:multi-vertex sweep below
      is now secondary (still useful data, but no longer tests a live
      conjecture) -- check its PID before relaunching.
- [ ] **Extend the m=5 and m=6 rows of tab:multi-vertex.** Command:
      max_multigraph_vertex_standard(n, m). RUNNING as of 2026-07-30 22:50,
      PID 79194 (background, outside this session): (3,7),(4,6),(6,5),
      (5,6),(5,7),(4,7) each capped at 5400s.
- [x] **The value is a BLOCK problem (2026-08-14), thm:multi-vertex-blocks.**
      Recovering the discarded -sum(pi) correction exactly gives the closed form
      K_m(n) = max over feasible simple G0 of sum_{uv in E}(m - kappa_{G0}(u,v)),
      an EQUALITY (on an edge kappa = 1+pi, and mu = m-1-pi >= 1 so no edge
      vanishes). That objective is a sum of LOCAL terms, adjacent vertices share
      a block and no route between them leaves it, so it is additive over blocks
      and K_m(n) is a knapsack over the best 2-connected block of each size.
      Search space becomes "2-connected graphs on b <= n vertices" (geng -C).
      EXACT VALUES for all n <= 8, m <= 8 (tab:multi-vertex-exact); agrees with
      every cell the program had proved. K_5^multi(7) = 29, not the bouquet's 27
      nor the unfinished search's 28. Clean split: thickened trees win for m<=3,
      tie at m=4, and from m=5 a SINGLE 2-connected block beats every split, so
      the bouquet is not the shape of the answer.
- [x] **Better construction (2026-08-14), thm:multi-vertex-bipartite.** The
      winning blocks are bipartite, not complete. Thickened K_{s,t} at
      multiplicity m-s is feasible with total st(m-s); as a bouquet the rate is
      st(m-s)/(s+t-1), optimised at t=m-1, s~(sqrt2-1)m, giving (3-2sqrt2)m^2
      against the clique's m^2/8. Factor 8(3-2sqrt2)~1.373; the gap to the upper
      bound falls from 16 to 6+4sqrt2~11.66. research_notes/
      multi_vertex_blocks.md + scripts/multi_vertex_blocks.py.
- [ ] **Still open: the remaining constant, between 3-2sqrt2 and 2.** The UPPER
      bound is now the side to attack, and the closed form says what to prove:
      bound sum_{uv in E(B)}(m - kappa_B(u,v)) for a 2-connected feasible B,
      rather than |E| times (m-1). Also open: whether K_{s,t} plus edges inside
      the small side is the true block family (the m=7,8 cells at n=7 say the
      extras help), and whether g_m(b)/(b-1) is eventually constant in b. It is
      still INCREASING at b=8 in every row, so tab:multi-vertex-exact does not
      extrapolate: larger n needs larger blocks enumerated.

## RESOLVED 2026-08-13: the Sorensen-Thomassen constant
The author obtained the paper (JCTB 17(2) 1974, 143-159, sorensen.pdf, gitignored
as it is copyrighted). Both open questions are settled from the primary source.
- CONVENTION. p.143 defines f_k(n) as "the least integer r so that every graph
  with n vertices and r or more edges contains a k-rail", i.e. the FORCING
  convention, one more than this thesis's k_m(n). So the thesis value is
  floor(8n/3) - 4, not the -3 the database prints. Applied.
- RANGE. Theorem 4 (p.158) covers n >= 6 except n = 7 and n = 12, not the
  n >= 13 the database records (that is just the clean tail). The two exceptional
  values are given in the paper: f_5(7)=16 and f_5(12)=28, i.e. k_5(7)=15 and
  k_5(12)=27 here. Applied.
- DIVERGENCE POINT. The paper proves f_5(n) = floor(5(n-1)/2) + 1 throughout
  6 <= n <= 13, which in this thesis's convention is exactly l_5(n). So the edge
  and vertex problems AGREE up to n = 13 and first separate at n = 14. The old
  text claimed n >= 13 by comparing a forcing k_5 against an avoiding l_5, a
  half-converted comparison. Note that k_5 > l_5 is invariant under the shift
  (both sides move by one), so no internal check can catch this. Applied.

## RESOLVED 2026-08-14: uniqueness on the QUADRATIC branch (thm:dir-multi-uniqueness)
ch4 had listed this as open because thm:dir-multi-full "is silent on it by
design, since it never needs to know which digraph it is peeling apart". True of
the proof read FORWARDS; read BACKWARDS from equality it is rigid.
- f(q) = 2(n-q)+floor(q^2/4) is UNIQUELY maximised at q=n on the quadratic
  branch (convex, and f(n)-f(n-1) = -2+floor(n/2) >= 2 for n >= 8), so equality
  forces every SCC to be a single vertex: the extremiser is ACYCLIC.
- The skeleton's triangle-freeness, previously used only to apply Mantel's
  BOUND, becomes at equality Mantel's EQUALITY CASE: the skeleton is an acyclic
  orientation of K_{ceil(n/2),floor(n/2)}.
- NEW STEP (lem:skeleton-shallow): inclusion-minimality also makes the skeleton
  SHALLOW, no directed path of three arcs. A 3-arc path has its ends on opposite
  sides, the complete bipartite graph supplies an arc between them, acyclicity
  fixes its direction, and that arc is then redundant.
- Chain: no 3-arc path => a 2-arc path forces a source and a sink => a fan of
  floor(n/2) arc-disjoint routes => contradiction once floor(n/2) >= m => no
  2-arc path => one-directional => no room for any other arc => every
  multiplicity exactly m-1. So D = (m-1)B for n >= max(8, 2m).
- Equality ALSO forces exact regularity (degree (m-1)n/2 for even n), which with
  acyclicity makes an exhaustive enumeration finite; it finds a unique
  extremiser at every size reached. research_notes/quadratic_branch_uniqueness.md
- [ ] STILL OPEN: the range n < 2m. Step 1 is the only place n >= 2m is used;
      below it a source-to-sink fan of floor(n/2) routes is affordable, so a
      different contradiction is needed. Enumeration finds no other extremiser
      there, so the hypothesis looks like an artefact of the argument.

## OPEN — the 1974 problem (undirected vertex, m >= 6), reframed 2026-08-14
STATE OF THE ART, read off the PRIMARY source (sorensen.pdf p.144), not just the
database: Bollobas-Erdos conjectured c_m := lim k_m(n)/(n-1) = m/2 (n copies of
K_m at a shared vertex). MADER DISPROVED IT for every m >= 6 (k_m(n) - mn/2 is
unbounded). S-T give c_m >= (m(m-1)-2)/(2m-3) = m/2 + 1/4 + O(1/m). The only
general UPPER bound is 2(m-1)n from Mader's density theorem, so the rate is
pinned only within a factor of ~4.
- [x] **thm:simple-vertex-blocks: k_m(n) is a knapsack over 2-connected blocks**,
      so c_m = sup_b h_m(b)/(b-1) (superadditive + Fekete). Reproves m=3 (blocks
      are edges and cycles, triangles win) and m=4 (K_4 wins) in two lines, and
      identifies the Bollobas-Erdos conjecture as exactly "K_m is the best
      block". No block on <= 9 vertices beats it, for any m <= 8 (all 194066
      2-connected 9-vertex graphs checked).
- [x] **WHY computation cannot see the truth.** The S-T witness glues copies of
      K_m - e in a CYCLE, so it has NO cut vertex: it is a single 2-connected
      block and the block reduction is blind to it. It does have 2-CUTS, so the
      refinement wanted is the TRICONNECTED (Tutte/SPQR) decomposition, the same
      machinery lem:incidence-rank already uses. Smallest member beating the
      conjecture: n=26 at m=5, 24 at m=6, 18 at m=7, against the 9 exhaustion
      reaches. Construction rebuilt and VERIFIED (counts, 2-connectivity,
      kappa^max = m-1) at m=5,6,7, j<=3.
- [ ] **NEXT: the triconnected refinement.** Decompose along 2-cuts and ask for
      the best "3-block" rate. This is the step the reduction points at and the
      SPQR tooling is in hand.
- [ ] **CHEAPEST GAIN, rem:vertex-degeneracy: does a feasible graph always have
      a vertex of degree <= m-1?** YES would make feasible graphs
      (m-1)-degenerate and give k_m(n) <= (m-1)n - C(m,2), HALVING the constant
      in the only general upper bound. Classical at m=3 (min degree 3 forces a
      K_4 subdivision). No counterexample for m <= 6, n <= 10 (exhaustive over
      all min-degree->=m graphs). Deliberately a QUESTION, not a conjecture: the
      sizes reached are far below the 26-vertex scale where the Bollobas-Erdos
      conjecture itself first fails. research_notes/simple_vertex_blocks.md

## OPEN — directed vertex problem at m >= 3
- [x] **Leading constant and second-order ORDER settled 2026-08-12**
      (thm:dir-vertex-linear-error): k_m^dir(n) = n^2/4 + Theta_m(n)
      unconditionally, so this row now sits exactly where the arc row does, and
      the two agree to first order. NOT a transfer of the arc bound, which
      would be illegitimate: the route family that prop:dir-arc-stability
      counts (direct arc plus two-step detours) has empty and distinct-singleton
      interiors, so it is internally vertex-disjoint and can be counted against
      kappa directly. What remains open is below.
- [ ] Genuinely open row, not a corollary of the arc case (Whitney's
      kappa<=lambda makes vertex-feasible the larger family). Exhaustive at
      m=3 agrees with the arc value at every n reached (n<=6). Single-arc-
      addition to the arc-optimal witness finds no kappa<=2 survivor at
      n=6..12 (2026-07-31, cheap check); a stronger remove-1-add-2 swap also
      finds none at n=8,9,10 (slower, ~30 min total). Both are local-rigidity
      evidence, not a proof. Wanted: the first digraph where kappa < lambda on
      some pair AND that slack buys extra arcs, or a proof it cannot.

## RESOLVED 2026-08-11: the directed MULTIGRAPH arc problem is now a closed theorem
Stijn showed the author `directed_multigraph_extremal_revised.pdf` (a ChatGPT-produced
proof), for the DIRECTED MULTIGRAPH problem (L_m^dir(n), arcs counted with multiplicity;
NOT the simple-digraph conj:dir-arc below, which is a different, still-open problem).
Checked by hand line by line (no errors found) and cross-validated three independent
ways against the thesis's own tools at cases never previously computed (m=4,5 at n=5,6):
the thesis's exhaustive B&B solver, the MILP certifier, and the hand proof all agree
exactly with (m-1)*M(n). Integrated into the thesis as thm:dir-multi-full
(chapters/app_proofs.tex): a "reachability-preserving spanning subgraph" (never more than
M(n) arcs, built from strongly connected components + an in/out-arborescence per
component + Mantel's theorem on the condensation) whose deletion is guaranteed to drop
every pairwise connectivity by exactly one, so peeling off m-1 of them proves the bound
for EVERY n and EVERY m at once, no parity split, no minimum-degree conjecture. This
SUPERSEDES: lem:attachment, cor:attachment-equality, thm:odd-step, thm:even-step,
rem:odd-step-roadmap, conj:min-degree, rem:min-degree-obstruction, prop:min-degree-m2,
lem:scaling-reduction, prop:dir-multi-even (all removed from app_proofs.tex). KEPT:
lem:saturated-attachment/rem:saturated-closure (linear-branch uniqueness, genuinely
separate from the value and not implied by the new proof) and the n=7 machine
classification (now rem:n7-classification, a standalone fact, not a step in the proof).
Also closes fact (a) (L_3^dir(7)=24) BY HAND, so the items below that were chasing it by
computation are now moot:

- [x] ~~Directed-arc m=3 even case (flagship)~~ — superseded, see above. The
      delta-split hand-proof route in research_notes/fact_a_delta_split.md and the
      "seam bases ell_3(9)=25, ell_3(10)=30 need Gurobi" line are no longer needed:
      thm:dir-multi-full gives L_3^dir(9)=(3-1)*20=40, L_3^dir(10)=(3-1)*25=50, etc.
      directly, for every n, no solver.
- [ ] **Hypergraph vertex at m=4.** lem:incidence-rank needs a 4-connectivity
      analogue of the Tutte/SPQR decomposition. STATUS 2026-07-31: no
      counterexample at m=4 across ELEVEN (n,r) pairs, both halves exhaustive
      (was: the single cell k_4^(3)(5)=6). But the surrounding formula is now
      PROVED to have a boundary: at r=2 this problem IS the multigraph vertex
      problem, so thm:clique-chain-vertex breaks it for every m>=5, n>=3.
      So m=4 sits right at the edge. research_notes/hyper_vertex_m4.md.
- [ ] **Where does the formula first break for r >= 3?** The r=2 answer is
      m=5 exactly. A search at m=5,6 for r=3,4,5 was launched 2026-07-31 but
      did not return within the session (the looser codegree cap at higher m
      widens the space sharply). Natural next computation; needs either a
      longer run on a quiet machine or a better-pruned search.
      Command: research_notes/scripts/hyper_vertex_m4_search.py (edit the
      case list) or the same DFS with symmetry reduction added.
- [x] ~~m=4 base facts~~ — moot. thm:dir-multi-full gives L_4^dir(7) =
      (4-1)*M(7) = 3*12 = 36 directly (matching the target this item was
      chasing by computation), and the n=8,9,10 seam arguments it planned are
      unnecessary: the general theorem covers every n at m=4 (and every other
      m) with the same three-line proof. research_notes/
      m4_odd_uniqueness_closed.md is now historical, not a dependency.

## MACHINE TARGETS (geng installed 2026-07-02 via brew; 10-core box)
No fact (a) confirmation run needed any more (was: geng_a_n7_t25, an uncapped
n=7 search for a 25-arc witness; last attempt died silently, no process
running as of 2026-08-11 per `ps`). thm:dir-multi-full proves L_3^dir(7)=24 by
hand, superseding both this run and the delta-split route in
research_notes/fact_a_delta_split.md (that note is now historical). The n=7
generation-enumeration run (fact (b), the extremal-graph CLASSIFICATION, a
genuinely separate question from the value) already completed successfully
and its result is in the thesis as rem:n7-classification.

## RESOLVED 2026-08-12: the directed hypergraph leading constant
conj:dir-hyper-constant is now thm:dir-hyper-constant: the maximum is
(1+o(1))(m-1)n^2/(4(r-1)) for fixed r and m, under the edge- AND the
vertex-disjoint separation, so the bipartite construction of prop:dir-hyper-first
is asymptotically optimal and TWO of the twelve rows change status. The named
obstacle (a hyperedge carries r-1 heads, so two-step routes through different
midpoints need not be disjoint) is not removed but paid: a matching argument
thins the family at a cost of r-1, which lands only in the LINEAR error term of
lem:two-step-budget, while a second and unrelated factor r-1 divides the leading
term when the auxiliary one-step shadow digraph is traded back for hyperedges.
Two upper bounds now coexist and neither dominates: prop:dir-hyper-first's
(m-1)n(n-1)/(r-1) is smaller until n is around 16(m-1)(r-1)/3.
- [x] **The GENERAL orientation model DOES share the constant (2026-08-14),
      thm:dir-hyper-general-constant.** Neither a second matching nor a greedy
      independent set: take a MAXIMUM family of two-step routes and ask what
      stopped it. Every unserved target is blocked by a hyperedge the family
      already spent, and a hyperedge has only r vertices to block with, counting
      tails and heads TOGETHER (|T_e|+|H_e| = r exactly, which is what keeps the
      constant at r rather than 2(r-1)). Gives C = (2r+1)(m-1), so
      |E| <= (m-1)/(r-1) floor(n^2/4) + 4(2r+1)(m-1)^2/(r-1)(n-1). The argument
      never needs the entering and leaving sides to be independent, which is
      exactly what the general model denies, so it covers all three orientations.
      Verified two ways (own max-flow + the program's), 0 violations. The
      constant 2r+1 is NOT sharp (nothing found above r-1); it lands in the
      linear term, so nothing rests on it. research_notes/two_step_budget.md.
- [ ] **Exact values at finite n** for the directed hypergraph, both
      separations. The constant is settled, the value is not.

## WRITE-UP QUEUE
- [x] Directed multigraph arc problem upgraded from conjecture/conditional to
      THEOREM across tab:summary, ch4 open problems, the contribution
      statement, and the lay summary's closing sentence (2026-08-11).

## Deferred figure polish (two items left deliberately, author's call)
- fig:cut (ch2) keeps its deliberate two-tone highlight (gray=not counted,
  blue=counted); revisit only if strict opacity uniformity is wanted.
- Body vs appendix vertex convention (big labelled circles vs small dots with
  side labels): both defensible; unify only on an author decision.

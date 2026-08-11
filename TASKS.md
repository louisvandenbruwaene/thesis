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
- [ ] **New open problem (replaces the old one): is a same-size K_r chain
      optimal, and what IS K_m^multi(n)?** thm:clique-chain-vertex is a lower
      bound only. Mixed block sizes, multi-bridge connections, or a different
      topology entirely are not ruled out. No upper bound attempted.

## AUTHOR DECISION NEEDED — the Sorensen-Thomassen constant
- [ ] **thm:sorensen-thomassen may be off by one; needs the original paper.**
      The thesis defines k_m/l_m as the MAXIMUM with no m-connected pair.
      erdosproblems.com states everything as the MINIMUM that FORCES one,
      which is one more. Verified on six shared entries (k_2, k_3, k_4, l_5,
      l_6, and the conjecture form), and the thesis convention is confirmed by
      exhaustive search (k_3(4)=4, k_3(5)=6, k_4(5)=8). Under that shift the
      database's k_5(n)=floor(8n/3)-3 becomes floor(8n/3)-4 here, but the
      thesis prints -3, i.e. the database figure unadjusted. BOTH candidates
      satisfy k_5 >= l_5, so internal arithmetic cannot decide it. Recorded
      as rem:threshold-convention rather than silently changed, since it is a
      cited external result. Nothing in the thesis depends on which is right.
      Resolve by reading SorensenThomassen74 directly and noting ITS
      convention.

## OPEN — directed vertex problem at m >= 3
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

## WRITE-UP QUEUE
- [x] Directed multigraph arc problem upgraded from conjecture/conditional to
      THEOREM across tab:summary, ch4 open problems, the contribution
      statement, and the lay summary's closing sentence (2026-08-11).

## Deferred figure polish (two items left deliberately, author's call)
- fig:cut (ch2) keeps its deliberate two-tone highlight (gray=not counted,
  blue=counted); revisit only if strict opacity uniformity is wanted.
- Body vs appendix vertex convention (big labelled circles vs small dots with
  side labels): both defensible; unify only on an author decision.

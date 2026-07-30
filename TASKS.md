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

## OPEN — directed vertex problem at m >= 3
- [ ] Genuinely open row, not a corollary of the arc case (Whitney's
      kappa<=lambda makes vertex-feasible the larger family). Exhaustive at
      m=3 agrees with the arc value at every n reached (n<=6). Single-arc-
      addition to the arc-optimal witness finds no kappa<=2 survivor at
      n=6..12 (2026-07-31, cheap check); a stronger remove-1-add-2 swap also
      finds none at n=8,9,10 (slower, ~30 min total). Both are local-rigidity
      evidence, not a proof. Wanted: the first digraph where kappa < lambda on
      some pair AND that slack buys extra arcs, or a proof it cannot.

## OPEN PROOF TARGETS (genuine attempts; verify before anything enters the .tex)
- [ ] **Directed-arc m=3 even case (flagship).** The min-degree-deletion engine
      gives the quadratic bound at odd n (given the even level below); the even
      case overshoots by +1 and hypothesis (H) that would kill it is FALSE
      (2026-06-30, explicit infinite family; research_notes section 0). The value
      conjecture ell_3(n)=Q(n) is unharmed. A correct odd-extremiser
      characterisation must include both known families; the thesis's own
      backward-arc framing may be the more robust route. Seam bases
      ell_3(9)=25, ell_3(10)=30 still need a solver (Gurobi).
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
- [ ] **m=4 base facts** (research_notes/m4_odd_uniqueness_closed.md closes
      the m=4 odd-uniqueness hole for k >= 5 and the m=5 value gap): (a4)
      L_4^dir(7) = 36 + the 36-arc extremal classification on 7 vertices; then
      n = 8, 9, 10 seam arguments. With those, the WHOLE m=4 problem closes
      like m=3. Gurobi or a long geng run at m=4 (16 states per pair)
      required. DEFERRED while the machine is busy with the fact (a)
      confirmation run below and the multi-vertex sweep above.

## MACHINE TARGETS (geng installed 2026-07-02 via brew; 10-core box)
- [ ] **Fact (a) confirmation run: RUNNING as of 2026-07-30 23:10** (relaunch
      of the 2026-07-04 attempt, which died silently after a BrokenProcessPool
      warning with no verdict). Uncapped n=7, target 25; EMPTY output
      independently confirms the delta-split hand proof (below) and unlocks
      the thesis write-up. Log: program/logs/geng_a_n7_t25_20260730.log
      (only prints a START line until it finishes; check `ps` for the live
      process, not just the log, before assuming it died). Budget hint: fact
      (b) took ~7h on 10 cores WITH the degree-8 cap; this run has no cap, so
      expect substantially longer.
- [ ] Fact (a) by MILP stays the Gurobi route (KU Leuven academic licence over
      eduroam; prove_integral_arc_bound(7,3,25, use_gurobi=True) INFEASIBLE).
      CBC cannot close it (measured 2026-06-16).
- Fact (a) already has a hand proof (delta-split route, both n=6
  classifications done, attachment check reports NO SURVIVOR): L_3^dir(7)=24.
  research_notes/fact_a_delta_split.md. AWAITING the machine confirmation run
  above before anything enters the .tex.

## WRITE-UP QUEUE
- [ ] If fact (a) lands (run above): upgrade conj status to THEOREM for the
      m=3 directed multigraph problem across tab:summary, ch4 open problems,
      rem:odd-step-roadmap, contribution statement, and the lay summary's
      closing sentence.

## Deferred figure polish (two items left deliberately, author's call)
- fig:cut (ch2) keeps its deliberate two-tone highlight (gray=not counted,
  blue=counted); revisit only if strict opacity uniformity is wanted.
- Body vs appendix vertex convention (big labelled circles vs small dots with
  side labels): both defensible; unify only on an author decision.

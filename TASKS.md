# Task queue (read this first; keep under ~80 lines)

Status: TODO | IN PROGRESS | BLOCKED(by) | AWAITING AUTHOR | DONE→delete after logging
Completed 2026-06 blocks (SA-vs-tabu, parallel geng, conj:min-degree numerics, review
fixes, C extension, Jan follow-up, P2 polish) are logged in claude.md and deleted here.

## REVIEW FIXES 2026-07-30 (external review; all landed, see claude.md for the audit)
- [x] **Whitney direction was inverted** in the proof of thm:dir-vertex-m2-exact
      (app_proofs) and in the ch1/ch4 prose. arc-feasible SUBSET vertex-feasible,
      so an arc upper bound does not restrict the vertex problem. Theorem is
      TRUE: the induction transfers (kappa is deletion-monotone) and the base
      cases n<=7 were re-run under the vertex test, giving 2,4,6,8,10,12 again.
      New rem:whitney-direction, new transcript, program vertex path made fast.
- [x] **prop:dir-arc-stability added**: |A| <= floor(n^2/4) + sqrt(m) n^{3/2}
      unconditionally, so ell_m^dir(n) = n^2/4 + O_m(n^{3/2}) with NO structural
      hypothesis. Came out of the external review, so the author must decide on
      an acknowledgment line. Sharpening the error to O_m(n) is the natural next
      target and would leave only a bounded discrepancy from conj:dir-arc.
- [x] The "one missing lemma" framing was too generous: the count assumed four
      things, now stated as open:decomposition (partition exists, A->B complete,
      nothing inside A, nothing back to A).
- [ ] **Directed VERTEX problem at m >= 3 is a genuinely open row**, not a
      corollary of the arc case. Exhaustive at m=3 agrees with the arc value at
      every n reached. Wanted: the first digraph where kappa < lambda on some
      pair AND that slack buys arcs, or a proof it cannot.
- [ ] **Multigraph vertex under the standard convention** (parallel copies as
      distinct one-step routes) is a new extremal problem; this thesis uses the
      collapsing convention and counts adjacencies (sec:parallel-convention).
      Wanted: exact values at m=3, small n, and a structural conjecture.
- [ ] **Sorensen-Thomassen range**: the thesis says k_5(n) = floor(8n/3) - 3 for
      n >= 10 with a worked justification in ch1. An external review claims the
      current Erdos Problems record says n >= 13. NOT resolvable from here (the
      paper is paywalled and erdosproblems.com 403s). CHECK AGAINST THE PAPER.

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
      analogue of the Tutte/SPQR decomposition. No early counterexample:
      k_4^(3)(5)=6 machine-checked.
- [x] **m=4 odd-level uniqueness / m=5 value step: CLOSED at research-note
      level 2026-07-04** (research_notes/m4_odd_uniqueness_closed.md, machine
      verification ALL CHECKS PASSED): deficiency-1 attachment corollary +
      tight-pair analysis force a degree-3k vertex at odd levels, k >= 5.
      Remaining: m=5 odd uniqueness (excess outgrows the min-degree count,
      documented), m>=6 (needs deficiency-2 corollaries), the m=4 finite
      bases (machine block below), and author review before any .tex entry.
- [x] **Fact (a) PROVED 2026-07-04 (delta-split route).** The 19-arc (55
      classes, 2549 s) and 18-arc (565 classes, 1576 s) n=6 classifications
      completed (sound geng enumerator, npz in program/logs), and the
      attachment check (research_notes/scripts/fact_a_attachment_check.py,
      control-tested, both-checker crosscheck 0 failures) reports NO SURVIVOR
      in either case: L_3^dir(7) = 24. AWAITING independent confirmation by
      the direct run below before anything enters the .tex. Route + proofs:
      research_notes/fact_a_delta_split.md.
- [ ] **m=4 base facts** (new, from research_notes/m4_odd_uniqueness_closed.md,
      which closes the m=4 odd-uniqueness hole for k >= 5 and the m=5 value
      gap): (a4) L_4^dir(7) = 36 + the 36-arc extremal classification on 7
      vertices; then n = 8, 9, 10 seam arguments. With those, the WHOLE m=4
      problem closes like m=3. Gurobi or a long geng run at m=4 (16 states
      per pair) required.

## MACHINE TARGETS (geng installed 2026-07-02 via brew; 10-core box)
- [x] n=6, target 20, max_degree=8: DONE 2026-07-02, exactly 1 class, the
      doubled bidirected P_6 (352 s). Closes the input of fact (b)'s degree-4 case.
- [x] **Fact (b) PROVED 2026-07-02**: n=7, target 24, max_degree=8 via the
      sound generation enumerator, 25895 s on 10 cores: exactly 3 classes,
      2B(3,4), 2B(4,3), doubled P_7, each re-verified by the exact checker.
      Recorded in rem:odd-step-roadmap, ch2, ch4, contribution statement.
- [x] **Uncapped n=6 PROVED 2026-07-02** (2187 s): exactly the 6 doubled
      spanning trees. With the saturated attachment lemma this makes the
      min-degree >= 6 bound on any fact-(a) witness unconditional (recorded
      in rem:odd-step-roadmap).
- [ ] **Fact (a) by machine (now the CONFIRMATION run)**: uncapped n=7,
      target 25; EMPTY output independently confirms the delta-split proof
      above and unlocks the thesis write-up. RELAUNCHED 2026-07-04 17:05,
      properly detached (nohup, main-guarded runner), PID 848, log
      program/logs/geng_a_n7_t25.log. Diagnosis of the 2026-07-02 loss:
      the parent died with the session and left orphaned idle workers
      (killed 2026-07-04). Budget hint: fact (b) took ~7 h on 10 cores WITH
      the degree-8 cap; this run has no cap, expect substantially longer.
- [ ] Fact (a) by MILP stays the Gurobi route (KU Leuven academic licence over
      eduroam; prove_integral_arc_bound(7,3,25, use_gurobi=True) INFEASIBLE).
      CBC cannot close it (measured 2026-06-16).

## WRITE-UP QUEUE
- [x] Saturated attachment lemma integrated (lem:saturated-attachment, A.30) and
      the seam shortened; fact (b) + uncapped n=6 recorded across
      rem:odd-step-roadmap, ch2, ch4, tab:summary caption, contribution
      statement (all 2026-07-02).
- [ ] If fact (a) lands (run above): upgrade conj status to THEOREM for the
      m=3 directed multigraph problem across tab:summary, ch4 open problems,
      rem:odd-step-roadmap, contribution statement, and the lay summary's
      closing sentence.

## Deferred figure polish (from the A.5-A.8 pass; two items left deliberately)
- [x] Faint-edge widths unified 2026-07-02 (bgarc/abk/attachment inherit gdirfaint).
- [x] Sub-captions ragged-right; star-hypertree hubs orange (caption said orange);
      gallery multiplicities stated once per panel (2026-07-02).
- fig:cut (ch2) keeps its deliberate two-tone highlight (gray=not counted,
  blue=counted); revisit only if strict opacity uniformity is wanted.
- Body vs appendix vertex convention (big labelled circles vs small dots with
  side labels): both defensible; unify only on an author decision.

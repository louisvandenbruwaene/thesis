# Task queue (read this first; keep under ~80 lines)

Status: TODO | IN PROGRESS | BLOCKED(by) | AWAITING AUTHOR | DONE→delete after logging
Completed 2026-06 blocks (SA-vs-tabu, parallel geng, conj:min-degree numerics, review
fixes, C extension, Jan follow-up, P2 polish) are logged in claude.md and deleted here.

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
- [ ] **m>=4 odd-level uniqueness / m>=5 value step** (thm:odd-step,
      rem:odd-step-roadmap): the counting no longer forces a low-degree vertex;
      needs an arithmetic or structural input averaging lacks. The same hole
      blocks a full linear-branch classification for general n (see
      research_notes/saturated_attachment_lemma.md, item 3).
- [ ] **Fact (a) by hand, delta>=6 core.** With the saturated attachment lemma
      (PROVED 2026-07-02) and the uncapped n=6 classification (run below), a
      25-arc feasible multigraph on 7 vertices has min degree >= 6; the d(v) in
      {6,7} cases delete to 19/18-arc n=6 multigraphs, so the hand route needs a
      near-extremal classification at n=6 (or the machine route below).

## MACHINE TARGETS (geng installed 2026-07-02 via brew; 10-core box)
- [x] n=6, target 20, max_degree=8: DONE 2026-07-02, exactly 1 class, the
      doubled bidirected P_6 (352 s). Closes the input of fact (b)'s degree-4 case.
- [ ] **Fact (b)**: n=7, target 24, max_degree=8 via
      enumerate_extremal_directed_multigraphs_via_generation (sound at all n).
      IN PROGRESS 2026-07-02 (~1-1.5 h expected on 10 cores). Expected classes:
      2B(3,4), 2B(4,3), doubled P_7.
- [ ] **Uncapped n=6, target 20** (no degree cap): would prove the n=6 extremal
      set is exactly the 6 doubled spanning trees (currently known only n<=5)
      and feed fact (a)'s d(v)=5 kill. QUEUED after fact (b).
      `python -c "from erdos915_unified import enumerate_extremal_directed_multigraphs_via_generation as e; r=e(6,3,20); print(len(r)); [print(M) for M in r]"`
- [ ] **Fact (a) by machine**: uncapped n=7, target 25; EMPTY output = proof of
      L_3^dir(7)=24 and the whole m=3 directed multigraph problem closes with
      fact (b). Runtime unknown (no degree cap, prefix M*(j<=6) prunes only);
      try after the queue above, kill if it thrashes.
      `python -c "from erdos915_unified import enumerate_extremal_directed_multigraphs_via_generation as e; r=e(7,3,25); print(len(r))"`
- [ ] Fact (a) by MILP stays the Gurobi route (KU Leuven academic licence over
      eduroam; prove_integral_arc_bound(7,3,25, use_gurobi=True) INFEASIBLE).
      CBC cannot close it (measured 2026-06-16).

## WRITE-UP QUEUE (after the runs above land)
- [ ] Integrate the saturated attachment lemma into app_proofs (full proof in
      research_notes/saturated_attachment_lemma.md), shorten the n=8 seam and
      the fact (b) degree-4 case in rem:odd-step-roadmap, and record the n=6
      cap-8 classification as completed rather than expected.
- [ ] If fact (b) lands: update rem:odd-step-roadmap + ch4 open problems
      (fact (b) machine-verified, only fact (a) open) + tab:summary status.

## Deferred figure polish (from the A.5-A.8 pass; two items left deliberately)
- [x] Faint-edge widths unified 2026-07-02 (bgarc/abk/attachment inherit gdirfaint).
- [x] Sub-captions ragged-right; star-hypertree hubs orange (caption said orange);
      gallery multiplicities stated once per panel (2026-07-02).
- fig:cut (ch2) keeps its deliberate two-tone highlight (gray=not counted,
  blue=counted); revisit only if strict opacity uniformity is wanted.
- Body vs appendix vertex convention (big labelled circles vs small dots with
  side labels): both defensible; unify only on an author decision.

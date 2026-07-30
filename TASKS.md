# Task queue (read this first; keep under ~80 lines)

Status: TODO | IN PROGRESS | BLOCKED(by) | AWAITING AUTHOR | DONE→delete after logging
Completed 2026-06 blocks (SA-vs-tabu, parallel geng, conj:min-degree numerics, review
fixes, C extension, Jan follow-up, P2 polish) and the 2026-07-30 review-fix/phase-2
batch (Whitney inversion, five overclaims, error term to O_m(n), multigraph vertex
alt-convention, Case 2 tightness, S-T threshold, Leonard citation fix) are all logged
in claude.md and deleted here.

## OPEN — multigraph vertex, alternate convention (new section A.8)
- [ ] **Extend the m=5 and m=6 rows of tab:multi-vertex.** m=5 n=6,7 and m=6 n=5
      would test conj:multi-vertex at the first sizes past the theta regime.
      Command: max_multigraph_vertex_standard(n, m). RUNNING as of 2026-07-30
      22:50, PID 79194 (background, outside this session): (3,7),(4,6),(6,5),
      (5,6),(5,7),(4,7) each capped at 5400s. Check for a printed verdict line
      before relaunching.
- [ ] **Prove sum_{uv} pi(u,v) >= (m-1) rank(G_0) for n >= m+2**, which closes
      conj:multi-vertex in general (currently verified m<=4 only). Same shape
      as lem:incidence-rank, so the triconnected decomposition is the tool to
      try.

## OPEN — directed vertex problem at m >= 3
- [ ] Genuinely open row, not a corollary of the arc case (Whitney's
      kappa<=lambda makes vertex-feasible the larger family). Exhaustive at
      m=3 agrees with the arc value at every n reached. Wanted: the first
      digraph where kappa < lambda on some pair AND that slack buys extra
      arcs, or a proof it cannot.

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

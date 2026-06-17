# Task queue (read this first; keep under ~80 lines)

Status: TODO | IN PROGRESS | BLOCKED(by) | AWAITING AUTHOR | DONE→delete after logging

## NEXT SESSION — FABLE (genuine proof attempts; author asked Fable to try these for real)
Pick ONE and go deep; these are the thesis's own open problems (ch4 §"Open problems").
Verify any result with a Fable proof-check before it enters the text uncommented.
- [ ] **Backward-arc lemma (flagship).** Prove an extremal non-hub digraph has no arc
      from $B$ to $A$. This turns conj:dir-arc into a THEOREM for all $m\ge3$ (and the
      directed vertex case with it). Obstacle named in ch4 §3 / app_proofs: the natural
      delete-and-compensate exchange is non-monotone (a back-arc can manufacture a 3rd
      route — see the refuted 30-arc counterexample). Attempted 2026-06-15: route-
      counting approach blocked; repartitioning approach outlined but not closed. No
      proof found. Look for a non-exchange argument (potential/charging, global flow).
- [ ] **Hypergraph vertex at $m=4$.** lem:incidence-rank drives $k_m^{(r)}=\ell_m^{(r)}$
      via Tutte/SPQR exactly where $\kappa\le2$. For $m=4$ it needs a 4-connectivity
      analogue of the triconnected decomposition. No early counterexample: $k_4^{(3)}(5)=6
      =\lfloor3\cdot4/2\rfloor$ (machine-checked). Concrete structural target.
- [ ] **$m\ge4$ odd-level uniqueness / $m\ge5$ value step** (thm:odd-step, rem:odd-step-
      roadmap). For $m=4$ the value step holds but counting no longer forces a degree
      $(m-1)k$ vertex (all degrees $\ge(m-1)k+1$ is consistent). For $m\ge5$ even the
      value step stalls (degree-regular surplus extremiser escapes the deletion bound).
      Needs an arithmetic/structural input the averaging argument lacks.
- [ ] **The two finite $n=7$ facts, by hand** (a) $L_3^{\mathrm{dir}}(7)=24$, (b) the only
      24-arc deg$\le8$ extremals are $2B_{3,4},2B_{4,3}$, doubled $P_7$. The MILP/enum
      (below) attack these numerically; a clean structural proof would be stronger and
      is independently interesting. (m=3 directed multigraph closes the moment these land.)

## BIG COMPUTATIONS — MEMORY SOLVED, RUNTIME IS THE WALL (measured 2026-06-16)
Phase E fixed the crash: every measurement below stayed <320 MB RSS, the ~22 GB
blow-up is gone, both jobs are now SAFE to leave running. But runtime, not RAM, is
the bottleneck and the Phase A-E speedups did not touch it. Empirical n-scaling:
- MILP (a) L_3(7)<25: n=5@17 INFEASIBLE 2.9s | n=6@21 LIMIT 600s | n=7@25 LIMIT 2000s.
  scipy/HiGHS CANNOT close n=7 as formulated. The speedups never touched the MILP.
  - [ ] Fix: Gurobi (KU Leuven academic licence; same model should close in minutes via
        milp->Gurobi), or a tighter encoding. Pure runtime, not memory.
    `timeout 3600 python -c "from erdos915_unified import prove_integral_arc_bound as c; \
      print(c(7,3,25,time_limit=3600))"`  INFEASIBLE => update rem:odd-step-roadmap + ch4.
- ENUM (b) 24-arc deg<=8: no-cap explodes (n=4 0.42s -> n=5 466s); WITH max_degree=8 the
  cap only bites at n=7 (n=5 still >330s, the cap barely binds there) and n=7 did NOT
  finish in a 40-min timeout, but stayed memory-safe. Borderline.
  - [ ] Option 1: a long SAFE run (no longer risks the PC):
    `timeout 14400 python -c "from erdos915_unified import \
      enumerate_extremal_directed_multigraphs as e; print(e(7,3,24,max_degree=8))"`
  - [ ] Option 2 (principled): Jan's geng+directg/watercluster2 generation pipeline
        (attacks DFS time itself; see FOLLOW-UP below). His "dedup only fixed RAM" warning
        is now empirically confirmed.

## FOLLOW-UP (from Jan's 2026-06-15 email)
Jan Goedgebeur (nauty author) confirmed our speedup and added these notes:
- `countg --G` gives classical minimum vertex-connectivity, NOT our max-local
  lambda^max/kappa^max. countg is not useful for our problem (already knew this).
- For n=7 directed multigraph generation: use `geng | directg` or `geng |
  watercluster2`. Jan confirms watercluster2 is usually faster than directg.
  This is a GENERATION-TIME pipeline (alternative to our DFS enumerator); it
  would need adapting for multiplicities {0..m-1} + bidirected arcs (non-trivial).
- [ ] P2: Explore geng+watercluster2 pipeline as a cross-check for ENUM (b) if
      DFS time remains the bottleneck after the Phase E speedup.
- [ ] P2: Compare tabu search vs SA (Jan's suggestion): implement
      `search_for_dense_graph` in tabu mode, compare quality and speed on a few
      benchmark cases (e.g. n=7, m=3). Similar performance expected but worth
      quantifying if time permits.

## DONE (logged in claude.md, detail there)
- 2026-06-16 later: verified Sonnet's gallery+Fig 3.2 (tests pass, values match,
  enum cross-validated); rebuilt stale main.pdf (0 overfull); big-computation feasibility
  measured (see section above). P2: open-variant tests + popularising summary done.
- 2026-06-16: gallery_extremal_graphs() + extremal_gallery.json (204 cases); Fig 3.2
  rewrite + 5 variant traces.
- 2026-06-15: feat/connectivity-speedup merged; contribution statement; Jan email notes.

## AWAITING AUTHOR — RESOLVED 2026-06-17 (author delegated these sign-offs to Claude)
- [x] 3 ch1 TikZ (fig:three-models, fig:edge-vs-vertex, fig:berge-path): APPROVED.
      Captions accurate, build clean (0 overfull). Judged from code + caption.
- [x] Regenerated data figures: APPROVED. variant_bounds_m3 squares sit ON the
      proved/conjectured curves and the hypergraph row is proved at m=3; the surface
      is blue(proved)/purple(open) with simple-undirected-vertex correctly purple at
      m>=5.
- [x] Figure-audit pass. (a) Fig 4.2 appearance-threshold + finite-m caveat: APPROVED.
      (b) stark all-blue multigraph-directed-vertex panel (n=3 forces kappa<=2): KEEP.
      conn_dist/edges_dist are "all twelve variants" atlas grids; dropping one panel
      breaks the uniform 3x4 and the captions already say the blue/red balance varies
      by panel. Genuine and honest, left as-is.
- [x] Carte-blanche overhaul (appendix proofs etc.): APPROVED for presentation and
      integration (Fable-checked earlier, 4 errors fixed, build clean). Mathematical
      responsibility stays the author's per the Contribution Statement.
- [x] 2026-06-14 layout polish: APPROVED (cosmetic, tab:summary wraps, 0 overfull).
- Found while judging: the variant_surface_3d suptitle carried an em dash; removed it
  to match the no-em-dash rule and regenerated the figure from surface_cache.json.

## P2 — remaining polish
- [x] popularising_summary closing: SIGNED OFF 2026-06-17. Lay terms, names both
      positive results, no jargon, no em dash or semicolon. Approved as-is.
- [ ] Final pass: overfull hboxes (main build is 0 overfull as of 2026-06-16),
      figure placement, ToC, spell check.

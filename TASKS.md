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
      counting approach blocked; repartitioning approach outlined but not closed.
      NEW ANGLE 2026-06-17 (see research_notes/directed_arc_m3_reduction.md +
      attach_check.py): drop the backward-arc framing; use the m=2 min-degree-deletion
      engine on the m=3 quadratic branch. Overshoot is +1 at even n, +0 at odd n (n=9
      seam is +2). So the whole m=3 quad upper bound reduces to killing one +1 at even n
      — exactly the multigraph thm:odd-step/lem:attachment pattern. In the +1 case D is
      (k+1)-regular up to degree-excess 2 and every deg-(k+1) vertex deletes to an odd
      extremiser; the degree-(k+1) re-attachment is mechanically REFUTED for k=4,5,6.
      GAP (1) ADVANCED 2026-06-17 (research_notes/directed_arc_m3_extremisers.md):
      CONDITIONAL THEOREM proved — if non-sources R induce max in-degree <=1 then
      a<=(n-sigma)(sigma+1)<=Q(n) in BOTH parities, equality = augmented-bipartite family
      (B_{k-1,k}+ANY fpf permutation of B; not unique). Attachment now refuted for ALL
      permutation types (k=4,5,6). So the whole m=3 quad upper bound reduces to ONE
      hypothesis (H): an extremiser has a source adjacent to every non-source.
      REMAINING GAPS: (1) PROVE (H) [load-bearing; about sources, exchange-free];
      (2) make the attachment refutation uniform in k (Menger lemma); (3) seam bases
      ell_3(9)=25, ell_3(10)=30 via certifier; (4) m>=4 redo + odd-uniqueness hole.
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

## ERRORS FOUND 2026-06-20 (by Claude Code review of all chapters)

- [ ] **ch1:184 wrong term "arcs" in undirected context (prop:leonard-m2 proof).**
      "any two vertices on that cycle are joined by the two **arcs** of the cycle"
      -- "arcs" is directed-graph terminology. Should be "**paths** along the cycle"
      (or "the two path segments of the cycle"). Simple one-word fix.

- [ ] **ch3:148 misattributed citation `\cite{ErdosProblems}` for "pre-2024 conjecture".**
      Line reads: "that overturned the naive pre-2024 conjecture `\cite{ErdosProblems}`".
      The 2026-06-13 session removed this exact citation from ch1 because the directed
      m>=3 conjecture is not stated in Problem 915. The ch1 version now says "the natural
      initial conjecture" with no citation; ch3 still has the old misattributed text.
      Fix: remove the citation and reword to "the natural initial conjecture" to match ch1.

- [ ] **ch1:387 false claim "first at n = m + 8 for m = 4".**
      Text: "the new formula strictly exceeds floor(n^2/4)+(m-2)ceil(n/2) at even n
      large enough (first at n = m+8 for m = 4)."
      WRONG: the new quadratic formula floor((n+m-2)^2/4) exceeds the old balanced-
      partition formula floor(n^2/4)+(m-2)ceil(n/2) by EXACTLY 1 at EVERY even n for
      m=4 (verified: diff=1 at n=2,4,6,8,10,12). What is "first at n=12" is that the
      full conjectured value max(m(n-1), floor((n+m-2)^2/4)) first exceeds the old full
      value max(m(n-1), floor(n^2/4)+(m-2)ceil(n/2)) -- because the hub term m(n-1)
      dominates both before n=12, making them equal until then. The sentence needs to
      compare the full max-formulas, not just the quadratic branches in isolation.

## C EXTENSION DONE 2026-06-19 (commit 5c00dd8, both repos pushed)
_erdos_fast.c + build_fast.sh: tiny_maxflow (~2x dense), max_connectivity_exceeds (2.2x),
canonical_form_min (147x). Pure-Python fallback intact; 77/77 tests pass with C loaded.
Rebuild: `cd program && bash build_fast.sh`. Next: parallel sensitivity_map + parallel geng
enumeration (plan: dazzling-finding-codd.md steps 3–4, each ~4–6x additional gain).

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
  - [x] Option 2 (principled) NOW IN-PROGRAM + SOUND (2026-06-18 merge): the geng
        support pipeline is implemented in erdos915_unified.py itself as
        `enumerate_extremal_directed_multigraphs_via_generation` (+ `_geng_support_graphs`),
        not just a research_notes script. geng emits each undirected support iso-class
        once; we decorate each support edge with a directed multiplicity pair
        (directg/watercluster2 are NOT used: they emit one orientation per edge and
        cannot express bidirected arcs or multiplicities). Prunes with the PROVED
        M*(j<=6) prefix bound only (no conjectured j>=7 bound), so it is a SOUND complete
        search at every n, unlike the DFS. Validated == DFS iso-class set at n=4 (all
        targets/caps) and n=5 (doubled P_5; 3 doubled trees). Degree-gated feasibility
        (flow<=min(outdeg,indeg)) + dropped a redundant _tiny_maxflow .copy() cut n=5
        cap=8 from 91s to 41s. Unit test tests/test_solve.GengGeneration.
  - [ ] n=7 fact (b) NOT yet closed; the wall is now empirically > 6 HOURS.
        A clean single-threaded geng run (e(7,3,24,max_degree=8)) was launched
        2026-06-19 09:35 and TIMED OUT at the 6h cap (rc=124, memory-safe the whole
        time, ~126 MB RSS, so it never risks the desktop). Scaling: n=5 cap=8 ~31-41s,
        n=6 cap=8 several min, n=7 > 6h. So a plain re-run will NOT finish in a normal
        sitting. Real options, in order of effort:
        (1) PARALLELISE the generation enumerator across CPU cores at the support level
            (geng emits supports independently; decorate+dedup per support is embarrassingly
            parallel). TASKS already flags ~4-6x; on this box that could bring 6h+ under ~1-1.5h.
            Add per-support Aut dedup (directg -G) + arc/degree prefilter so work scales with
            non-iso MULTIGRAPHS, not labelled prefixes. Needs care (keep the canonical-dedup
            source of truth; validate == DFS set at n=4,5 before trusting n=7).
        (2) Run it overnight/uninterrupted with a larger cap, or on the KU Leuven cluster.
        (3) Fact (a) via Gurobi MILP (academic licence) - independent of (b).
        Expect {2B_{3,4}, 2B_{4,3}, doubled P_7}. Runtime, not soundness, is the obstacle.
        Plain relaunch (will exceed 6h):
        `cd program && nohup timeout 36000 python -u -c "from erdos915_unified import \
          enumerate_extremal_directed_multigraphs_via_generation as e; \
          print(e(7,3,24,max_degree=8))" > logs/geng_n7_$(date +%Y%m%d).log 2>&1 &`

## FOLLOW-UP (from Jan's 2026-06-15 email)
Jan Goedgebeur (nauty author) confirmed our speedup and added these notes:
- `countg --G` gives classical minimum vertex-connectivity, NOT our max-local
  lambda^max/kappa^max. countg is not useful for our problem (already knew this).
- For n=7 directed multigraph generation: use `geng | directg` or `geng |
  watercluster2`. Jan confirms watercluster2 is usually faster than directg.
  This is a GENERATION-TIME pipeline (alternative to our DFS enumerator); it
  would need adapting for multiplicities {0..m-1} + bidirected arcs (non-trivial).
- [x] P2 DONE 2026-06-18 (nauty now installed locally): pipeline built + verified.
      counts = OEIS A000273 = program; simple-dir extremal = program solve;
      watercluster2 ~15x faster than directg (n=6). Multigraph HYBRID (support via
      nauty + multiplicity layering) reproduces the DFS enum at n=4 (2) and n=5 (3)
      and is ~17x faster at n=5 (26s vs 456s) -> confirms DFS-time is the wall.
      See research_notes/jan_followup_nauty_and_tabu.md + scripts/nauty_pipeline.py.
      NEXT for ENUM(b) n=7: add per-support Aut dedup (directg -G) + arc/degree
      prefilter so work scales with non-iso multigraphs (pieces all present).
- [x] P2 DONE 2026-06-18: tabu vs SA benchmarked (scripts/tabu_vs_sa.py). Sharper
      than expected: TIES on undirected + small directed, but tabu BEATS the thesis
      annealer on the harder directed cases at equal 6s budget -- reaches the
      L_3^dir(7)=24 extremiser (SA stalls at 20), multi-dir n=5 16 vs 15, simple-dir
      n=7 18 vs 16. Engineering note only (not in thesis text).

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
- [x] Final pass DONE 2026-06-18: build 0 overfull / 0 undefined refs+cites / 93pp;
      spell check clean (British English, only names+technical+code flagged); ToC and
      figure placement fine (the 5 ch4 [p] floats are legit full-page grids). Also
      refreshed variant_bounds_m3/m6.png with the shortened plot title (author's note).

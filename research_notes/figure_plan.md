# Figure plan: proposed visual aids (planning only, not yet drawn)

Goal: make the thesis followable by a beginner mathematician by showing a
concrete picture of every object and every route-type before the first proof
that uses it, and by turning the research and coding output we already have
into figures. This document lists proposed figures with location, type, a
detailed description of what to draw, the beginner purpose, and the data
source for the data figures. Nothing here is drawn yet.

Guiding principle adopted from the author's brief: show one concrete worked
instance of each object (graph, digraph, multigraph, hypergraph) and each
route notion (edge-disjoint, vertex-disjoint, hyperedge-disjoint Berge) the
first time it matters, then reuse the same running example in the proofs.

Style note: reuse the existing thesis conventions so additions match the
look. Vertices apx / smallvertex (KULblauw1 blue), hubs vertexorange,
forbidden objects vertexred / apredarc, highlighted routes vertexgreen,
second route vertexpurple, hyperedge hulls as filled translucent regions or
apz squares in the incidence picture, arcs aparc, edges apgedge. Role colours
roleMeasure / roleObserve / roleDiscover / roleProve for the pipeline cartoons.

Priority key: P1 high (fills a real comprehension gap the brief named),
P2 useful, P3 nice to have.

---

## Already covered (do not duplicate)

- ch1: K5 example, three models, edge-vs-vertex (one cut vertex, lam=2 kap=1),
  one-directional bipartite digraph, bidirected star / directed hub,
  augmented bipartite, a single Berge path, G(n,p) edge-vs-vertex sampling.
- ch2: spine, matrix representation, vertex-split network, hyperedge gadget,
  scaling reduction, the cut indicator.
- ch3 (data only): complexity growth, one temperature trace, sensitivity on
  an 8-vertex multigraph, SA vs tabu convergence, two variant-bounds grids.
- ch3 (data only): crossover, scatter landscape, pair-conn distribution,
  edge-count distribution, 3D surface.
- appendix: Gomory-Hu distance, Mader lower-bound constructions,
  mutual-unreachability + counterexample, attachment setup, P7-to-C8 seam,
  incidence translation + star hypertree, SPQR leaf schematic, plus the
  trace gallery, conn-dist at m=6, threshold 3D.

---

## A. Foundational concept figures (the brief's explicit asks)

### A1. Edge-disjoint versus vertex-disjoint routes, side by side  (P1)
- Where: ch1, at the separation paragraph near fig:edge-vs-vertex (line ~159),
  either replacing or sitting beside the existing one.
- Type: TikZ, two panels of the SAME small graph (about 6 vertices).
- Draw: a graph where a pair (s,t) carries three edge-disjoint s-t paths but
  only two internally vertex-disjoint ones, because two of the three routes
  are forced through one shared interior vertex w. Left panel: the three
  edge-disjoint routes in three colours, with the shared vertex w circled.
  Right panel: the two vertex-disjoint routes, w used by only one, the third
  route greyed out. Annotate lec(s,t)=3, kap(s,t)=2.
- Purpose: the whole thesis hangs on lec versus kap. The existing figure only
  shows lam=2 kap=1 through a single cut vertex. A case where the two numbers
  genuinely differ by more than one, with the routes drawn, makes Whitney's
  inequality and the "shared interior vertex" mechanism concrete. The same
  mechanism reappears in prop:leonard-m2 and the m=5 divergence.

### A2. A worked directed graph with lambda read off it  (P1)
- Where: ch1 directed section opener (near const:bipartite, line ~224), and
  reused at the head of the appendix directed section (before
  thm:dir-arc-m2-exact, line ~262 area).
- Type: TikZ, one small digraph (4 or 5 vertices), plus a tiny inset.
- Draw: a concrete digraph with a handful of arcs. Pick a pair (s,t). Show
  the two arc-disjoint directed routes from s to t in two colours, and draw
  the minimum arc-cut as a dashed line crossing exactly those two arcs, so
  Menger is visible: lambda(s,t) = 2 = size of the cut. Label out-degree and
  in-degree on s and t to preview the degree bound lambda <= min(d+,d-).
- Purpose: the brief asked for "an example of the directed graph before using
  it in a proof". Readers meet arc-disjoint routes, a directed cut, and the
  degree bound on one picture before any directed argument starts.

### A3. Berge routes: hyperedge-disjoint and the hyperedge cut  (P1)
- Where: ch1 hypergraph section (near fig:berge-path, line ~424) or appendix
  near thm:menger-hyper (line ~760).
- Type: TikZ, one small 3-uniform hypergraph with translucent hyperedge hulls.
- Draw: extend the existing single Berge path to TWO hyperedge-disjoint Berge
  u-v routes in two colours, sharing no hyperedge, then a third picture or
  overlay marking the minimum set of hyperedges whose removal separates u from
  v (the Menger-for-hypergraphs cut). Optionally a small inset of the same
  routes in the incidence graph, tying to fig:incidence.
- Purpose: the brief asked for a Berge path example and the disjointness
  notions. This shows what "hyperedge-disjoint" means and why a single
  hyperedge touching all pairs at once is the subtlety the checker handles.

### A4. The four models on one row  (P2)
- Where: ch1, fig:three-models already shows three. Consider a fourth panel.
- Type: TikZ, add a directed multigraph panel (parallel arcs both directions)
  so all four object classes used in the twelve variants appear together.
- Purpose: the twelve variants come from model x direction x separation. A
  single legend-like strip of all object types orients the reader before the
  variant table.

---

## B. Chapter 3 (search) schematics  (currently zero TikZ here)

### B1. Why the walk is allowed to go infeasible: a three-step swap  (P1)
- Where: ch3, the "why above the ceiling" paragraphs (line ~50).
- Type: TikZ, three small panels of the same vertex set.
- Draw: (a) a locally maximal feasible graph at lambda = m-1, every addable
  edge marked with a red cross because it would create a forbidden pair.
  (b) one such edge added: now infeasible, highlight the offending pair and
  the extra route that pushed lambda to m, the added edge in red.
  (c) a different load-bearing edge removed: feasible again at lambda = m-1
  and strictly denser than (a). Arrows (a)->(b)->(c) labelled "add", "remove".
- Purpose: the prose explains tunnelling through infeasibility in words only.
  This is the single most load-bearing idea of the chapter and has no picture.

### B2. Edge sensitivity on a tiny worked example  (P2)
- Where: ch3, sensitivity section (near fig:sensitivity, line ~80), as a small
  hand-computable companion to the 8-vertex data figure.
- Type: TikZ, one 4 or 5 vertex graph.
- Draw: label each edge with sigma(e) = lambda(G) - lambda(G-e). Show one
  load-bearing edge (sigma > 0, on the tightest cut, drawn bold) and one free
  edge (sigma = 0, drawn faint), with the one-line computation of each beside
  it. Colour by the same scale as fig:sensitivity.
- Purpose: the real sensitivity figure is dense and large. A 4-vertex version
  with sigma computed by hand teaches the definition before the big picture.

### B3. The energy landscape and the Metropolis crossing  (P3)
- Where: ch3, near the energy definition (line ~20) or alg:anneal.
- Type: TikZ cartoon, a 1-D energy curve.
- Draw: energy on the vertical axis over a schematic configuration axis, with
  a local basin (locally maximal feasible graph), a small barrier (the
  infeasible swap), and a deeper basin (the extremiser). A hard-wall walk
  stops at the barrier, the cooled walk crosses it. Temperature shown as the
  height of accepted uphill steps shrinking over time.
- Purpose: turns "simulated annealing escapes local optima" into a picture.

---

## C. Chapter 3 (synthesis) schematics  (currently zero TikZ here)

### C1. The directed frontier reduction and the forbidden backward arc  (P1)
- Where: ch3, the single-open-lemma section (lines 16 to 18).
- Type: TikZ, two panels.
- Draw: (a) an extremal-looking digraph split into part A (left) and part B
  (right), every arc running A to B, B lightly thickened with a few internal
  arcs (the m-2 budget). Label the count |A||B| + (m-2)|B|. (b) the same with
  one backward arc b -> a added in red, and the NEW third arc-disjoint route
  it manufactures between two vertices of B traced in green, pushing lambda
  over the ceiling. This is exactly the counterexample the checker refuted.
- Purpose: ch3's whole open problem is "an extremiser has no backward arc".
  The reader currently has only prose. This shows the partition the proof
  wants and precisely why a single backward arc breaks the count.

### C2. The quadratic phenomenon: undirected wall versus directed wall  (P2)
- Where: ch3, "two principal phenomena", quadratic phenomenon (line ~44).
- Type: TikZ, two panels.
- Draw: (a) an undirected graph near Mader's ceiling, every vertex degree
  bounded, edge count linear, annotate floor(m(n-1)/2). (b) the directed
  bipartite wall, all arcs one way, annotate floor(n^2/4) arcs at lambda = 1.
  A small arrow noting "same vertices, quadratically more arcs, still
  connectivity one".
- Purpose: makes "direction buys a quadratic term" visual, the geometric
  reason the directed cases are the hardest.

### C3. The m=3 reduction chain as a roadmap diagram  (P1)
- Where: ch3, where the m=3 reduction to two n=7 facts is stated (lines 26-32).
- Type: TikZ flow diagram (boxes and arrows), not a graph drawing.
- Draw: boxes for lem:attachment and thm:odd-step feeding "value + extremal
  characterisation propagate through both parities (rem:odd-step-roadmap)",
  which funnels down to the two finite boxes (a) L_3(7)=24 and (b) the three
  24-arc extremisers. Side branches show the m>=4 uniqueness hole and the
  m>=5 value hole as dashed offshoots. Colour proved boxes blue (roleProve),
  open boxes red.
- Purpose: ch3's hardest narrative is the dependency structure of the m=3
  result. A dependency diagram makes "the whole problem rests on two finite
  facts" legible at a glance.

---

## D. Appendix proof figures (proofs currently without one)

### D1. Min-degree deletion step of thm:dir-arc-m2-exact  (P2)
- Where: appendix, the inductive step (line ~297).
- Type: TikZ, two panels.
- Draw: (a) a digraph D on n vertices, the minimum total-degree vertex v0
  highlighted, its degree counted, with the averaging note d(v0) <= 2a/n.
  (b) D - v0 on n-1 vertices boxed as "induction hypothesis applies", with
  the recombination a <= d(v0) + M(n-1). A small number line showing the
  even case landing exactly on n^2/4 and the odd case overshooting by the
  sub-unit fraction k/(2k-1) that integrality removes.
- Purpose: the induction is "peel the lightest vertex". One picture plus the
  number line turns the two-regime arithmetic we just expanded into a glance.

### D2. The two incidence-rank reductions, before and after  (P1)
- Where: appendix, lem:incidence-rank Steps 2 and 3 (lines ~1007 to 1019),
  the proof we just expanded.
- Type: TikZ, two before-after pairs.
- Draw: Step 2: a degree-2 hyperedge node z0 between two X-vertices x, x',
  then suppressed into a single X-X edge, with |E| and |V| both dropping by
  one so rank is unchanged. Step 3: a degree-2 X-vertex x0 deleted, rank
  dropping by exactly one. Use apx for X (blue circles), apz for Z (squares),
  matching fig:incidence.
- Purpose: the inductive engine of the hardest lemma is two local moves.
  Showing the moves makes the bookkeeping ("rank preserved", "rank drops by
  one") obvious rather than asserted.

### D3. Block-cut tree and the counting identity  (P2)
- Where: appendix, lem:incidence-rank Step 1 (line ~992).
- Type: TikZ, two panels.
- Draw: (a) a graph with two or three blocks glued at cut vertices, blocks
  shaded in different tints, cut vertices ringed. (b) the block-cut tree
  beside it, block nodes and cut-vertex nodes alternating, illustrating
  c = 1 + sum (b(v)-1) and how each X-vertex is counted once per block.
- Purpose: supports the one genuinely algebraic step of the lemma.

### D4. Hypergraph edge bound: charging a hyperedge to its subtree  (P2)
- Where: appendix, proof of prop:hyper-edge (line ~768), companion to the
  graph version fig:gomory-hu-dist.
- Type: TikZ, a hypergraph Gomory-Hu tree T* with one hyperedge e and its
  smallest spanning subtree ST(e) highlighted, showing ST(e) has at least
  r-1 edges and e crosses each of those tree cuts.
- Purpose: makes the charging argument (r-1)|E| <= sum c*(t) visual, the
  hypergraph analogue of the Mader double count the reader already saw.

### D5. Chernoff two-halves of the appearance threshold  (P3)
- Where: appendix, proof of thm:gnp-threshold (line ~1204), or ch1 near the
  threshold statement.
- Type: data plot or schematic, two panels.
- Draw: (a) c<1: the degree distribution Binomial(n-1, p) concentrated below
  m, with the union-bound tail shaded, so Delta < m whp. (b) c>1: the edge
  count distribution concentrated above Mader's floor(m(n-1)/2), shaded, so a
  high pair is forced. Mark p* = m/n as the crossover.
- Purpose: the proof is "degrees stay low below, edges grow above". Two
  concentration pictures make the union bound and Mader contrapositive
  tangible. Can be generated from the sampler we already have.

---

## E. Data figures from the research and coding (the brief invites these)

### E1. Gallery of extremal graphs across the variants  (P1)
- Where: app_gallery (new section), or ch3 near the scarcity discussion.
- Type: data-driven TikZ or matplotlib multi-panel, drawn from real output.
- Draw: the actual extremal (densest feasible) graphs the program enumerated,
  one small panel per (variant, n) for a chosen slice, each annotated with
  edge or arc count, lambda^max or kappa^max, and the automorphism count
  |Aut(G)|. Show, for instance, the simple-undirected tree at n=4,5, the
  multigraph star at full multiplicity, the bidirected star, the
  one-directional bipartite wall, and a 3-uniform star hypertree.
- Data source: figures/extremal_gallery.json (already computed by
  gallery_extremal_graphs over all twelve variants for n<=7, m<=4, r=3, with
  |Aut| and labelled counts). Currently sits unused as JSON.
- Purpose: the thesis argues extremisers are rare and structured. Showing the
  real ones, machine-found, is the most direct evidence and is concrete for a
  beginner. Directly answers "data from the research is allowed".

### E2. The linear extremal family is richer than the double star  (P2)
- Where: ch3, the linear-branch paragraph (line ~34), or appendix near
  rem:odd-step-roadmap.
- Type: TikZ from enumerator output.
- Draw: the complete extremal sets the enumerator found, the 2 doubled
  bidirected spanning trees at n=4 (doubled star, doubled path) and the 3 at
  n=5 (star, broom, path), each as a small bidirected multigraph at
  multiplicity m-1 = 2, all reaching 2(n-1)(m-1) arcs.
- Data source: enumerate_extremal_directed_multigraphs(4,3,12) and (5,3,16),
  which return exactly these classes.
- Purpose: backs the claim that the linear branch is not just the double star,
  the correction the new enumerator found, with the actual catalogue.

### E3. Proved versus open across the twelve variants, as a map  (P2)
- Where: ch3 near tab:summary, or replacing part of the 3D surface story.
- Type: data, a coloured grid or small-multiples heatmap.
- Draw: the (variant, n, m) cube collapsed to a readable map, each cell blue
  if the value is proved, green if certified, purple if only searched, using
  the same proved-vs-open data behind variant_surface_3d. A flat heatmap is
  easier for a beginner than the 3D surface.
- Data source: figures/surface_cache.json (already holds exact-vs-discovery
  status per cell, 202 exact / 218 lower at last count).
- Purpose: a flat, legible companion to fig:surface-3d that many readers find
  hard to parse in perspective.

### E4. Certifier and search reaching the same optimum  (P2)
- Where: ch3 rediscovery section (near tab:rediscovery, line ~120), or ch2.
- Type: data, one panel per a few variants.
- Draw: for a variant in the certified range, plot the search lower bound
  climbing over steps and the certified upper bound as a horizontal line, the
  two meeting at the extremal value, the "settled" moment visible. Reuses the
  trace data and the certificate values.
- Data source: search traces plus certificate_log.txt and the proved values.
- Purpose: shows the proved-meets-discovered discipline of the trichotomy in
  one picture rather than across two separate figures.

### E5. Enumeration wall and where each method stops  (P3)
- Where: ch3, the wall section (near fig:complexity, line ~5).
- Type: data, an annotated version of complexity_growth.
- Draw: the existing explosion curves with vertical markers for the last n
  that brute enumeration closes, that the cut-counting certifier closes
  (n=6 for the directed multigraph, about twenty minutes), and that the
  search still reaches, so the reader sees the three reaches on one axis.
- Data source: certificate_log.txt timings, basecase_search_log.txt, plus the
  known per-method limits recorded in the logs.
- Purpose: makes "each tool reaches a few vertices further" quantitative.

### E6. Solver and speedup timings  (P3)
- Where: ch2 (certifier) and ch3 (the cheap-checker section, line ~85).
- Type: data, small bar or line charts.
- Draw: (a) certifier solve time versus n (n=3..6) showing the ~20 minute
  wall at n=6. (b) search wall-clock with versus without the monotone fast
  path and capped predicate (the 2.6x to 3.9x speedup), and SA versus tabu to
  optimum at n=7. (c) optional, the nauty generation pipeline versus the DFS
  at n=5 (about 17x).
- Data source: certificate_log.txt, the speedup numbers in the dev logs, and
  tabu_vs_sa / nauty_pipeline scripts in program/scripts.
- Purpose: substantiates the engineering claims with measured numbers. Note
  timings are machine-specific and should be regenerated on the reference
  machine before inclusion.

---

## Suggested order of execution (when ready to draw)

1. P1 concept figures first: A1, A2, A3 (the brief's explicit asks), then the
   chapter-3 swap B1 and chapter-4 backward-arc C1 and reduction-chain C3,
   then the incidence reductions D2 and the extremal gallery E1.
2. P2 next: A4, B2, C2, D1, D3, D4, E2, E3, E4.
3. P3 last: B3, D5, E5, E6.

Most P1 and P2 graph figures are small hand-laid TikZ in the existing style.
The data figures E1 to E6 should be added as functions in make_figures.py so
they regenerate from the caches and logs already in figures/, keeping the
single-source-of-truth discipline the thesis describes.

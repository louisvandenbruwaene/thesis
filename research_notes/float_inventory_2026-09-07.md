# Float inventory, 7 September 2026

A label-indexed record of every figure and table in `main.tex`, replacing the
running totals of earlier passes. Those totals did not reconcile with their own
lists: one said twelve of sixteen tables were checked while eight distinct
tables were named as outstanding.

The thesis has **42 floats: 26 figures and 16 tables.** The eight tables named
as outstanding are the four equal-budget detail tables and the four
search-evidence tables. Every one of them is verified below.

## What was verified in this pass

**Generated tables, checked against their source data without the renderer.**
A separate script parsed each rendered `.tex` and rebuilt every printed cell
from the frozen record.

- The four equal-budget detail tables: 128 rows, all six columns. The search
  minimum, median, maximum and seed count come from
  `program/data/equal_budget_2026-09-06/report.json`, and the construction
  column from `manuscript_baseline.json` in the same directory. Zero
  mismatches. The construction column differs from `report.json`'s own
  `supplied_construction` field in 12 of the 128 cells, which is the two-baseline
  split that `sec:equal-budget-details` already states in print: the tables
  compare against the manuscript snapshot, and `comparison_baseline.json` holds
  the earlier one. Neither file is read by the search runner.
- The four search-evidence tables: 208 printed search cells and 208 printed
  construction cells. Every search cell traces to a record in
  `program/data/search_evidence.json`, and every one of those records carries
  the value of the corresponding `search|...` key in
  `program/data/machine_values.json` unchanged. Zero mismatches, so no search
  value was lifted to a construction, an enumeration or a neighbouring order.
  In eight cells the search beats the construction, printed unadjusted as the
  caption states.
- `tab:variant-values`: all 32 status words and every bold machine-exact cell
  agree with the figure driver's panels at both $m = 3$ and $m = 6$. One bold
  cell has no entry in `machine_values.json`, the simple undirected edge
  hypergraph at $(m, n, r) = (6, 6, 3)$ reading 11. It comes from the
  standalone enumeration in `program/scripts/hyper_edge_m6_n6_gap.py`, which was
  rerun in this pass: 125970 twelve-hyperedge families walked in 180 seconds
  with none feasible, and an eleven-hyperedge family exhibited at
  $\lambda^{\max} = 5$. The value is 11 against the bound of 12.

**The two $m = 6$ grids.** `variant_bounds_m6_graphs.png` and
`variant_bounds_m6_hypergraphs.png` were read against the panel data and
`tab:variant-values`. Status badges, exact squares, and the presence or absence
of a curve agree panel by panel. The multigraph directed arc panel at $m = 6$
carries a conjectural curve and no exact squares, which matches its row in the
table and the caption's statement that the formula is drawn as a conjecture.
The simple undirected edge hypergraph panel shows the square at $n = 6$ sitting
one below the curve, which is the $(6, 6, 3)$ gap.

**`fig:skeleton-example`.** Read in the built PDF against its caption. The
drawn $D$ carries the three bidirected pairs and the three crossing arcs the
caption names, the redundant $a_1 \to c_2$ is the one annotated and dropped, and
$R$ keeps exactly the arcs the caption lists.

**All 42 floats, mechanically.** Every one carries a label and a caption, every
file it pulls in exists, and every one is now referenced by at least one
`\Cref`. Eleven were not: `fig:spine`, the four variant-bound grids, the two
$m = 6$ equal-budget tables and the four search-evidence tables. Each sits on
its own `[p]` page, so a reader could reach it only by wherever LaTeX floated
it. Cross-references were added at the four places the prose already introduced
them. `check_consistency.sh` now gates all four float conditions, verified by
removing one reference and watching the gate fail.

## The four carried-forward checks, closed

The pass above verified the two $m = 6$ grids and `fig:skeleton-example` and
carried four floats forward on earlier verification: the $m = 3$ hypergraph
grid, `fig:spine`, `fig:vertex-split` and `fig:scaling-reduction`. Each is now
checked against what it claims rather than against its label and caption.

**The variant-bound grids, all four of them.**
`program/scripts/verify_variant_grids.py` reads the panel data from the frozen
machine record and asks three separate questions of each grid. Whether the
eight panels agree with `tab:variant-values` cell by cell, matching a bold
`vtExact` cell to a completed enumeration at that order and the same value, a
`vtProved` or `vtConjectured` cell to the drawn curve, and a `vtOpen` cell to a
witness at least as large as the printed lower bound. Whether the panels obey
what the captions say a panel means, so a conjectured panel carries a curve, an
open panel carries none, no square, circle or plus sits above a curve the
caption calls an upper bound, and no search circle sits above a completed
enumeration. And whether the committed PNG is the file that panel data draws,
by redrawing each grid and comparing SHA-256. No mismatches on any of the four,
and all four PNGs are byte-identical to their redraws. The table and the
figures both read `gather_variant_grid` and neither reads the other, so the
agreement is between two renderings of one record.

Read against the figure, the $m = 3$ hypergraph grid shows the construction
marks sitting on the conjectured curve in all four undirected panels and no
exact square anywhere below it, which is the state its caption describes: the
bound is not shown unattainable at $m = 3$. The two directed hypergraph panels
carry no curve, exact squares at $n = 3$ and $n = 4$ only, and the downward
circle steps at $n = 10$ that `sec:variant-grids` states are weaker timed runs
rather than a decreasing extremal function.

**`fig:spine`. One defect, fixed.** The diagram itself matches: MODEL feeds
MEASURE, MEASURE feeds both PROVE and DISCOVER, and those four are the shape of
Chapter 2, which runs Modelling, Measuring, the two certification sections and
then the heuristic search. The caption's last sentence was not. It read "The
badge colours on the code cards match the boxes here", and the code cards were
cut from the thesis in a shortening pass. `\codecard` is defined in
`preamble.tex` and used in `offcuts.tex` alone, `\rolebadge` appears in no
chapter source, and `pdftotext main.pdf` finds MEASURE and DISCOVER only inside
the spine diagram itself. The colours still match, because both the boxes and
the badges read the same four `roleModel`/`roleMeasure`/`roleProve`/
`roleDiscover` definitions, but the caption pointed the reader at objects the
thesis no longer prints. The sentence is removed. A caption and label sweep
cannot find this, since the caption is present, well formed and attached to the
right figure. Nothing is lost by the removal: `offcuts.tex` archives the
caption's earlier form carrying that same sentence, at the head of the block of
code cards it was describing, so the archive already holds both halves of what
the live caption was pointing at.

**`fig:vertex-split`.** The drawn transformation is the standard one and the
picture carries it out: both incoming arcs enter $v^{\mathrm{in}}$, both
outgoing arcs leave $v^{\mathrm{out}}$, and the only arc drawn as a unit is the
internal one, which is what makes vertex-disjointness into edge-disjointness.
The caption's qualification that an adjacency keeps capacity $\mu(u,v)$ and a
hyperedge keeps its gate matches `sec:transformations` and the gate network of
`fig:hyper-gadget-example`.

**`fig:scaling-reduction`.** Checked with an exact-rational max flow written for
the check, not with the program's. The drawn multigraph has $A \to B$ of
multiplicity two, $A \to C$ of multiplicity one and $B \to C$ absent, so
$\lambda^{\max} = 2$, which is $m - 1$ at the $m = 3$ the caption names, so the
object is feasible at that threshold rather than merely drawn. Dividing by
$m - 1 = 2$ gives the weights $1$ and $\tfrac{1}{2}$ printed on the right, and
the scaled $\lambda^{\max}$ is exactly $1$, matching the caption's "pairwise
maximum flow at most one". Its total weight is $\tfrac{3}{2}$, which is the
three arcs of $D$ divided by $m - 1$, the identity the sentence introducing the
figure states.

## Not re-checked in this pass

Carried from earlier passes rather than redone here: `fig:divergence`,
`fig:complexity`, `fig:crossover`, and the TikZ diagrams other than
`fig:skeleton-example`, `fig:spine`, `fig:vertex-split` and
`fig:scaling-reduction`. The two $m = 3$ grids are no longer on this list, the
section above closes them. `fig:gomory-hu-dist` had two wrong
tree-distance comments in its source corrected on 2026-09-04, with the drawn
tree itself verified a genuine Gomory-Hu tree.

## The inventory

| Label | File | Kind |
|---|---|---|
| `fig:augmented-wall` | ch3_synthesis.tex | TikZ |
| `fig:complexity` | ch2_machine.tex | PNG complexity_growth.png |
| `fig:crossover` | ch3_synthesis.tex | PNG directed_crossover.png |
| `fig:directed-lambda` | ch1_basecases.tex | TikZ |
| `fig:divergence` | ch1_basecases.tex | PNG edge_vertex_divergence.png |
| `fig:edge-vs-vertex` | ch1_basecases.tex | TikZ |
| `fig:eight-models` | ch1_basecases.tex | TikZ |
| `fig:gomory-hu-dist` | app_proofs.tex | TikZ |
| `fig:hyper-gadget-example` | ch2_machine.tex | TikZ |
| `fig:hyper-star` | ch1_basecases.tex | TikZ |
| `fig:incidence-berge` | app_proofs.tex | TikZ |
| `fig:k5-example` | ch1_basecases.tex | TikZ |
| `fig:matrix-rep` | ch2_machine.tex | TikZ |
| `fig:menger` | ch1_basecases.tex | TikZ |
| `fig:prune` | ch2_machine.tex | TikZ |
| `fig:rediscovery-gallery` | ch2_machine.tex | TikZ |
| `fig:scaling-reduction` | ch2_machine.tex | TikZ |
| `fig:simple-digraph-m2` | ch1_basecases.tex | TikZ |
| `fig:skeleton-example` | app_proofs.tex | TikZ |
| `fig:spine` | ch2_machine.tex | TikZ |
| `fig:variant-bounds-m3-graphs` | app_proofs.tex | PNG variant_bounds_m3_graphs.png |
| `fig:variant-bounds-m3-hyper` | app_proofs.tex | PNG variant_bounds_m3_hypergraphs.png |
| `fig:variant-bounds-m6-graphs` | app_proofs.tex | PNG variant_bounds_m6_graphs.png |
| `fig:variant-bounds-m6-hyper` | app_proofs.tex | PNG variant_bounds_m6_hypergraphs.png |
| `fig:variant-tree-status` | ch3_synthesis.tex | TikZ |
| `fig:vertex-split` | ch2_machine.tex | TikZ |
| `tab:basecase-search` | app_proofs.tex | hand tabular |
| `tab:equal-budget-m3-graphs` | app_proofs.tex | generated equal_budget_m3_graphs.tex |
| `tab:equal-budget-m3-hypergraphs` | app_proofs.tex | generated equal_budget_m3_hypergraphs.tex |
| `tab:equal-budget-m6-graphs` | app_proofs.tex | generated equal_budget_m6_graphs.tex |
| `tab:equal-budget-m6-hypergraphs` | app_proofs.tex | generated equal_budget_m6_hypergraphs.tex |
| `tab:equal-budget-summary` | ch2_machine.tex | generated equal_budget_summary.tex |
| `tab:generating-benchmark` | ch2_machine.tex | generated generating_benchmark_table.tex |
| `tab:multi-vertex-blocks` | app_proofs.tex | hand tabular |
| `tab:notation` | ch1_basecases.tex | hand tabular |
| `tab:rediscovery` | ch2_machine.tex | generated rediscovery_table.tex |
| `tab:search-evidence-m3-graphs` | app_proofs.tex | generated search_evidence_m3_graphs.tex |
| `tab:search-evidence-m3-hypergraphs` | app_proofs.tex | generated search_evidence_m3_hypergraphs.tex |
| `tab:search-evidence-m6-graphs` | app_proofs.tex | generated search_evidence_m6_graphs.tex |
| `tab:search-evidence-m6-hypergraphs` | app_proofs.tex | generated search_evidence_m6_hypergraphs.tex |
| `tab:summary` | ch3_synthesis.tex | hand tabular |
| `tab:variant-values` | app_proofs.tex | generated variant_table_all.tex |

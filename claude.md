# Claude progress log — Erdős Problem 915 thesis

This file used to be a full session-by-session log (3700+ lines, back to
2026-06-11). It has been condensed (2026-08-26) into a current-state summary.
The full history is not lost: `git log` has every session's commit, and
`research_notes/` keeps the self-contained write-ups and verification scripts
for each result below. Do not re-derive that history from memory; if you need
the reasoning behind a specific past decision, `git log -p -- <file>` or grep
`research_notes/` first.

## What this repo is

A KU Leuven master's thesis on Erdős Problem 915 (the general connectivity
threshold problem, extended across sixteen graph/digraph/hypergraph variants,
in two separations — edge/arc and vertex). `main.tex` is the thesis,
`chapters/app_proofs.tex` carries every proof, `program/erdos915_unified.py`
is the single-file companion program (checker, provers, search, figures),
`research_notes/` holds working notes for results developed outside the
thesis-writing loop before being integrated, `offcuts.tex` archives every
passage cut during the 2026-08 shortening passes with restore anchors.

## Current build state

- `main.pdf`: ~115 pages, `latexmk -pdf main.tex` exits 0, 0 overfull boxes,
  0 undefined refs/citations.
- `program/`: single file `erdos915_unified.py`. Core needs only numpy+scipy;
  pulp (MILP prover), networkx (Gomory–Hu view only) and matplotlib (figures)
  are optional and guarded. `nauty`/`geng` optional for faster enumeration.
- Tests: `cd program && python -m unittest discover -s tests` — currently
  103 tests, 1 expected skip on a minimal (no-pulp) install.
- Standard of done before calling anything finished: rebuild the PDF clean,
  run the test suite, run the program's own `_run_checks` self-test, and
  re-verify any numeric claim against at least one independent implementation
  (own from-scratch Edmonds–Karp scripts in `research_notes/scripts/` are the
  usual second opinion).

## What's proved (current, load-bearing — supersedes any older note)

- **Directed multigraph arc problem (thm:dir-multi-full), fully closed.**
  `L_m^dir(n) = (m-1) * max(2(n-1), floor(n^2/4))` for *every* n>=2, m>=2, one
  proof (reachability-preserving skeleton + Mantel), no parity split, no
  minimum-degree conjecture. This retired the old attachment-lemma / odd-step
  machinery and the machine-computed "fact (a)/(b)" route entirely.
- **Directed simple-graph arc/vertex problems: leading term + Theta_m(n)
  second order, unconditionally**, via `lem:two-step-budget`
  (`thm:dir-arc-linear-error`, `thm:dir-vertex-linear-error`). Exact value for
  m>=3 (`conj:dir-arc`) is still open; see below.
- **Directed hypergraph leading constant proved** (`thm:dir-hyper-constant`,
  `thm:dir-hyper-general-constant`): (1+o(1))(m-1)n²/(4(r-1)), all three
  orientation models (forward/backward/general), both separations.
- **Hypergraph vertex problem: m=2 and m=3 proved for all n, r**
  (`thm:hyper-vertex-m2`, `thm:hyper-vertex-m3`, via `lem:incidence-rank`).
  m>=4 open (needs a 4-connectivity SPQR analogue) — see below.
- **Multigraph vertex problem, alternate ("collapsing") convention**: solved
  as a block/knapsack problem (`thm:multi-vertex-blocks`), asymptotically
  Theta(m²n) with matching upper bound (`prop:multi-vertex-upper`, via Mader).
  Exact constant between the K_{s,t} construction and 2 is still open.
- **Undirected simple vertex problem (Mader/Leonard/Sørensen–Thomassen)**:
  standard results hold for n>=m; k_5 divergence point (edge vs. vertex) is
  n=14, resolved 2026-08-13/24 from the primary Sørensen–Thomassen paper
  (JCTB 17(2) 1974) after finding both a convention mismatch and a range
  error in the secondary source (erdosproblems.com) that had been trusted
  earlier. The general m>=6 problem (Bollobás–Erdős, 1974) remains open;
  `thm:simple-vertex-blocks` reduces it to a block/knapsack problem too, and
  the next lever (triconnected/SPQR refinement) is identified but unexecuted.

## What's still open (see TASKS.md for the live queue)

1. `conj:dir-arc` exact value/classification for m>=3, simple digraphs. The
   old route via hypothesis (H) ("every extremiser has a universal source")
   was *refuted* by an explicit counterexample family (2026-06-17) — that
   route is dead, not just unfinished. `lem:two-step-budget` gives the best
   unconditional bound (n²/4 + Theta_m(n)); closing the gap needs a genuinely
   new idea.
2. Hypergraph vertex problem at m=4 and beyond. No counterexample at m=4
   across eleven (n,r) cells; the r=2 case of this same problem *is* the
   multigraph vertex problem and is known to fail at m=5, so m=4 sits right
   at the edge. Where r>=3 first breaks is an open computation.
3. Multigraph vertex problem (alternate convention): tighten the constant
   between (3-2√2)m² and 2m² (`thm:multi-vertex-bipartite` vs.
   `prop:multi-vertex-upper`).
4. Undirected simple vertex problem, m>=6 (the 1974 Bollobás–Erdős question):
   triconnected/SPQR block refinement not yet attempted; a degeneracy
   question (`rem:vertex-degeneracy`) that would halve the known upper-bound
   constant has no counterexample up to m<=6, n<=10 but is unproven.
5. `k_m(n)`, m>=6, undirected simple graphs, general classification: the
   original 1974 open problem, not attempted (half-century open; out of
   scope for a rigorous attack here).

Numeric constants, search commands and partial-progress detail for all five
live in `TASKS.md` and the matching `research_notes/*.md` file — do not
duplicate that detail here; update those files directly when progress is made
and only touch this summary if the *status* (proved/open) changes.

## Standing conventions (do not relitigate without cause)

- **One self-contained program file.** The thesis prose sells this as a
  reproducibility property; keep `erdos915_unified.py` a single file and
  consolidate in place rather than splitting into a package (author decision,
  2026-06-19/20).
- **No em-dashes, en-dashes, or prose semicolons** anywhere in the thesis
  (author's standing style rule). Semicolons inside table cells or math
  notation are fine.
- **British spelling** throughout the thesis (colour, optimise, etc.).
- **Never claim a computation finished when it didn't.** A past session's
  worst mistake (2026-08-11 audit) was three places asserting a MILP run
  "returns INFEASIBLE" when it had actually been abandoned unfinished.
  State plainly what ran to completion and what did not.
- **Reversible shortening.** Anything cut from the thesis during a
  length-reduction pass goes into `offcuts.tex` with a provenance header
  (source file, restore anchor, reason) — never delete thesis content outright
  without archiving it there first.
- **Commit and push at the end of each session** (standing author
  preference).
- **Run `program/sync_code_appendix.py`** after any edit to
  `erdos915_unified.py` — Appendix C reproduces the source verbatim with
  hardcoded line ranges that this script keeps in sync.
- Before trusting a numeric or bibliographic claim inherited from an older
  note in this file's history, re-verify it — several "settled" facts in
  earlier sessions turned out to rest on a convention mismatch (Whitney
  direction, forcing-vs-avoiding, parallel-edge convention) that silently
  flipped a value by exactly one or by a sign. See `git log --grep=convention`
  for the pattern if you suspect another one.

## Known loose ends, flagged not fixed

- `ref.bib`'s `ErdosProblems` entry lists Paul Erdős as the author of
  erdosproblems.com, which is Thomas Bloom's site. Not verified/fixed
  (the site blocks automated fetches); leave for the author.
- `gurobi_handoff/` is vestigial since `thm:dir-multi-full` closed the
  problem it was built for by hand. Left in place, not deleted.

## 2026-08-26 (Opus) — the fourth model: sixteen variants, and the author's chapter rewrite actioned

The author rewrote Chapter 1 and the opening of Chapter 2 by hand, commenting out
large passages and leaving inline instructions. This session executed those, added
the fourth model, and repaired what the rewrite broke.

**THE REWRITE BROKE 22 CROSS-REFERENCES AND LATEX NEVER SAID SO.** Commenting out
the constructions left seven labels undefined (`const:directed-hub`,
`const:bipartite`, `const:augmented-bipartite`, `rem:counterexample-m3`,
`prop:leonard-m2`, `sec:parallel-convention`, `thm:dir-vertex-m2-exact`), cited
from 22 places. `latexmk -g` exited 0 with **zero warnings** and the PDF printed
`??` at all 22. Cleveref's fallback emits `??` without a "Reference undefined"
line, so the build log is not a sufficient check here.
**Use `pdftotext main.pdf - | grep -c '??'` as the real gate.**
Repaired by restoring only what is genuinely needed, per the author's own calls:
`prop:leonard-m2` deleted outright (subsumed by `thm:leonard` at m<=4, so restating
it was redundant); `rem:counterexample-m3` folded into `const:augmented-bipartite`
as its m=3, n=10 instance with the three citations repointed;
`sec:parallel-convention` attached to the live convention paragraph in ch2; the
three constructions and the m=2 vertex theorem restated compactly in ch1.
Both directed constructions were re-verified numerically before writing them
(hub hits m(n-1) at lambda=m-1 for (7,2),(6,3),(8,3),(9,4),(7,5); bipartite hits
floor(n^2/4) at lambda=1 for n=6..9; augmented bipartite hits floor((n+m-2)^2/4)
at lambda=m-1 for seven (n,m) including the 30-arc n=10,m=3 case).

**THE FOURTH MODEL: TWELVE VARIANTS -> SIXTEEN.** The author's new ch1
`fig:eight-models` and `tab:notation` already carried multiplicity as an axis on
hypergraphs; the rest of the thesis had not caught up. This is a real split, not
a relabelling, and it does NOT collapse the way the multigraph vertex rows do:
q parallel copies of a hyperedge give q Berge routes with EMPTY interiors, so they
are pairwise hyperedge-disjoint AND internally vertex-disjoint, raising kappa as
well as lambda. Multiplicity is therefore capped at m-1 in both separations and
all four multihypergraph cells are genuine. Machine-confirmed at the smallest
witness, n=r=m=3: simple maximum 1, multi maximum 2, exactly the split
`prop:hyper-edge` predicts (simple attains when m-1 <= C(n-2,r-2), multi when
(r-1)|(n-1)). Program: `_hyper_multiplicity_cap`, a `simple` axis threaded through
`_brute_force_hypergraph`, `_random_hypergraph_search`, `max_feasible_hyperedges`
and `solve`; `_VARIANT_ENUM_CONFIGS` 12 -> 16; `gather_variant_grid` 12 -> 16
panels; `_variant_panel_grid` 3x4 -> 4x4. Thesis: `tab:summary` 6 -> 8 rows,
`fig:variant-tree-status` 3 -> 4 model blocks, and the count swept through ch2,
ch4, app_proofs, both READMEs and this file.

**A BUG I INTRODUCED AND CAUGHT BEFORE PUBLISHING.** The new multihypergraph
panels capped their curve at `C(n,r)`, the SIMPLE trivial maximum. A
multihypergraph may take each hyperedge up to m-1 times, so its ceiling is
`(m-1) C(n,r)`. At n=r=m=3 the wrong cap reads 1 where the true value is 2, which
would have put an exact square ABOVE its own curve, the exact artefact the author
caught in June. Fixed with `lb_multihyper_edge`; the regeneration now carries an
inline assert that no exact point exceeds its proved/conjectured curve.

**PRUNING NOW APPLIES TO EVERY VARIANT, AS THE TEXT CLAIMS.** The author asked
"we prune for all variants and not just directed arc m2 right?" The honest answer
was no: only `_exhaustive_directed` pruned, while `_brute_force_matrix` and the
hypergraph sweep were blind `product` walks. Rather than soften the text,
`_brute_force_matrix` was rewritten as a depth-first search with the same two
prunings. **Writing the argument out caught two real defects in my own code:**
the headroom was `(total - i - 1) * (span - 1)` where the undecided count is
`total - i`, which under-estimates and would have pruned branches that could still
beat the incumbent (silently returning values too small); and `separation` is
keyword-only, so the call would have raised TypeError. Both fixed before testing.
Guarded by `PrunedEnumerationMatchesBlind` in `tests/test_solve.py`, which runs
the pruned search against a separately written blind sweep over every variant and
every reachable size (53 cells, 0 mismatches) and also asserts each witness is
really feasible and really carries its reported count.

**ANNEALING REMOVED FROM THE THESIS NARRATIVE** (author's instruction). ch2's
search sections are now built on tabu search, with annealing named once as the
measured-weaker alternative (ties undirected, loses 24 vs 20 and 18 vs 16 on the
directed cases) and retained only as the self-test cross-check. The temperature
and cooling exposition is gone; edge sensitivity survives as a diagnostic, since
tabu does not use it as a removal dial.

**THE FIGURE LEGEND.** `plot_variant_grid` drew a six-entry legend inside EVERY
panel, which at sixteen panels occupied more area than the curves. Replaced by one
figure-level key. Three attempts failed before the cause surfaced: **`_save()` runs
a SECOND, rect-less `plt.tight_layout()`**, discarding any `rect` or
`subplots_adjust` reservation the caller made. The grid now passes
`_save(path, tight=False)` and hangs the legend below the figure box, where the
tight bounding box expands to include it.

VERIFY: 115 tests OK (was 103, +12 from the new differential test), 1 expected
skip; program self-check ALL CHECKS PASSED; `latexmk` exit 0, 102 pp, 0 overfull,
0 undefined refs, and 0 occurrences of `??` in the extracted PDF text.

NOTE: the standing rule above about running `program/sync_code_appendix.py` is
STALE. Appendix C was removed in the 2026-08-24 shortening pass and no chapter
inputs `app_code.tex` any more, so there are no line ranges left to sync.

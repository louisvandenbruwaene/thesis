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
- **Mader's theorem stays proved in full in the appendix.** It is about four
  printed pages and it is the only classical result the thesis reproves rather
  than cites, which makes it the standing candidate whenever someone asks for a
  shorter appendix. The author was asked directly on 2026-08-26 and chose to
  keep it: it is the answer to the headline undirected edge problem, and its
  Gomory--Hu double count is the move the multigraph and hypergraph arguments
  reuse, so a reader who cannot check it there cannot check them either. Do not
  reopen this without the author.
- **The body states and draws, the appendix defines and proves.** A chapter
  carries theorem statements, figures, and a few sentences of what makes each
  result work. Formal constructions, verification of a construction's
  connectivity, optimisation models, algorithmic bookkeeping and counting
  conventions all live in \Cref{app:proofs}, however short they are, and the
  body names the shape in words instead ("a hub joined to every other vertex in
  both directions") with a pointer to the definition. Author instruction,
  2026-08-26: the main story should read quickly and visually. When a body
  passage grows a formal display that is not a headline result, move it rather
  than shorten it, and check `??` afterwards, because every construction is
  cross-referenced from three files.
- **The prose states facts, it does not rate them.** Chapter 1 is the author's
  own hand and sets the register for the whole thesis: say what a thing IS,
  never what it is WORTH. Out: "it is worth noting/saying/recording", "the
  point is", "what it buys is", "nothing here is deep", "a good test of
  whether", "that is not a defect", "earns its keep", "deserves a statement of
  its own", "the deepest in the thesis", and the intensifiers "genuinely",
  "honest/honestly", "plainly". Out too: rhetorical setups ("what the table
  hides is", "the first thing to notice is", "two things stand out") and
  retrospective participial cascades ("The journey set out from one clean
  theorem and followed it across sixteen variants, proving..., building...").
  KEEP every epistemic status fact: proved vs conjectured vs open vs
  search-only, which computations finished and which were abandoned, which
  bounds are attained. "The search proves no upper bounds" is a fact about the
  method and stays. "Stating its limits is part of the honesty the thesis
  insists on" is the thesis praising itself and goes. Technical uses of the
  same words stay ("genuinely fractional" as against integral, "the
  restriction is essential" followed by a counterexample). Author instruction,
  2026-08-26.
- **Never claim a computation finished when it didn't.** A past session's
  worst mistake (2026-08-11 audit) was three places asserting a MILP run
  "returns INFEASIBLE" when it had actually been abandoned unfinished.
  State plainly what ran to completion and what did not.
- **The multigraph VERTEX variants are posed on the underlying simple graph,
  and that is why two rows of `tab:summary` read "= simple".** Parallel copies
  never raise kappa, since a second copy of an edge is a route with an empty
  interior between vertices that are already adjacent. So counted with
  multiplicity the extremal question has no finite answer at all: thicken any
  feasible graph and kappa never moves. The thesis therefore counts adjacencies
  for those two cells (`sec:parallel-convention` in ch2), which collapses them
  onto the simple problem. This is NOT what happens one arity up: q parallel
  copies of a HYPEREDGE give q Berge routes with empty interiors between any two
  of its members, so multiplicity does raise kappa there, the cap is m-1 in both
  separations, and all four multihypergraph cells are genuine
  (`_hyper_multiplicity_cap`). Restored 2026-08-27 from the review record; it had
  survived only in the git log after the condensation.

- **The hypergraph witness is gated at the source by proved attainment, never
  clamped downstream.** `prop:hyper-edge` is an upper bound that a simple
  hypergraph attains only when `m-1 <= C(n-2, r-2)` and a multihypergraph only
  when `(r-1) | (n-1)`. Outside those ranges the closed form is a number nobody
  has exhibited, so plotting it as a witness asserts a hypergraph that need not
  exist, and sometimes does not: at `n = 6, m = 6, r = 3` it reads 12 while all
  125970 twelve-hyperedge simple 3-uniform hypergraphs on six vertices are
  infeasible and the true maximum is 11. `attained_hyper_edge` and
  `attained_hyper_vertex` therefore return 0 outside the proved range and leave
  the search's own value alone. The tempting alternative, letting
  `_reconcile_panel`'s exact-value clamp catch it downstream, does not work: that
  clamp can only fire where exhaustion actually finished inside its budget, which
  at exactly this cell it does not. Restored 2026-08-27.

- **Reversible shortening.** Anything cut from the thesis during a
  length-reduction pass goes into `offcuts.tex` with a provenance header
  (source file, restore anchor, reason) — never delete thesis content outright
  without archiving it there first.
- **Commit and push at the end of each session** (standing author
  preference).
- **`program/sync_code_appendix.py` is DEAD.** It kept Appendix C's verbatim
  source listing in step with hardcoded line ranges. Appendix C was removed in
  the 2026-08-24 shortening pass and no chapter inputs `app_code.tex` any more,
  so there are no ranges left to sync and nothing to run after editing the
  program. This entry used to instruct the opposite and a later session note
  contradicted it; the rule itself is corrected here (2026-08-27) so nobody
  follows a dead one.
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

## 2026-08-26 (Opus, second session) — the variant grids were being CUT OFF the page

The author's complaint was that the sixteen-variant grids "look horrible". They
did, and the worst of it was not a styling problem.

**THE FIGURES OVERFLOWED THE ROTATED PAGE AND LATEX SAID NOTHING.** The canvas
was 9.2 x 8.4in and each half is placed at `width=0.98\textheight` inside a
`sidewaysfigure`, so on the page it was 9.14in wide by 8.35in tall while the
rotated page has the text WIDTH, 6.10in, to give. Roughly 2.2in ran off the
paper: the suptitle, the caption and the bottom half of the legend were simply
not there in the built PDF, and `latexmk` exited 0 with no overfull box and no
float warning. **`grep Overfull` is not a sufficient check for a sideways
figure. Render the page (`pdftoppm -f <page> -r 55 -png main.pdf out`) and look
at it.** The canvas is now 9.2 x 4.9in, sized backwards from what the rotated
page has left after the caption, and it is saved with `bbox_tight=False` so the
crop-to-content bounding box cannot silently change that ratio again. Verified
by rendering all four pages.

**THE ROW LABEL WAS GUESSING WHERE THE Y LABEL ENDED.** `annotate(xy=(-0.46,
0.5), xycoords="axes fraction")` scales with panel width, so the offset that
cleared a narrow panel landed on top of a wide one's y label. It now MEASURES:
after `fig.canvas.draw()`, `get_tightbbox` says where the leftmost column's
labels actually end and the model name hangs just left of that. This fixed the
other four grids that share `_variant_panel_grid` at the same time.

Other figure changes, all in `plot_variant_grid`: the four column identities
moved out of sixteen long panel titles into four column headers, leaving each
panel a one-word coloured status chip ("proved" / "conjectured" / "open", and
the inherited rows stack "= simple" above the word); markers shrank (rings 8 ->
5.2, mew 1.8 -> 1.1) so the curve reads THROUGH a search circle that lands on
it, which is the whole point of those circles; the legend is built from the
marks the figure actually draws, so the hypergraph halves stopped advertising a
red conjecture curve neither of them has; the named branch is labelled on the
curve instead of in the caption, and only where it is visibly separate from the
curve it feeds.

**THE MACHINE-VALUE CACHE** (`figures/machine_values.json`, 480 entries,
committed like the other caches). The four grids ran several hundred `solve`
calls on every regeneration: 26 minutes, and it is now 3 seconds.
`make_figures.py --grids-only` redraws just these four,
`make_figures.py --refresh` recomputes every value. The stored fingerprint
covers the program only ABOVE its chapter 4 banner, which is everything `solve`
runs. Hashing the whole file would have fired on every edit to the plotting code
below, and a warning that always fires is one nobody reads. A mismatch is
reported and the values are reused. Caching the timed searches also pins the
published figures to the run that produced them, which the reproducibility
appendix now states.

**FOUR OTHER FIGURES WERE STILL THE TWELVE-VARIANT ONES.** Not stale numbers,
a missing ROW: `conn_dist_m6`, `edges_dist`, `pair_conn_dist` and
`scatter_lambda_edges` on disk were 3x4 grids with no multihypergraph row at
all, because `figures/enumeration_cache.pkl` and
`figures/pair_enumeration_cache.pkl` still held twelve keys and nothing had
rebuilt them when `_VARIANT_ENUM_CONFIGS` went 12 -> 16. Both caches are
regenerated (the twelve shared entries came back byte-identical, checked, so
only the four new rows are new data) and all four figures redrawn at 4x4. If a
variant is ever added again, those two pickles must be rebuilt in the same
commit.

Also fixed while in there, both pre-existing: `\Cref{sec:search-wall}` in ch2
pointed at a label the chapter rewrite deleted (one `??` in the PDF, repointed
to `fig:complexity`), and thirteen strings still said "twelve variants" after
the fourth model landed, four of them PRINTED as figure suptitles.

VERIFY: 116 tests OK, 1 expected skip; self-check ALL CHECKS PASSED; `latexmk`
exit 0, 104 pp, 0 overfull, 0 occurrences of `??`; all four sideways pages
rendered and inspected.

## 2026-08-26 (Opus, third pass) — the tone of chapters 2, 4 and the appendix

The author asked how chapter 1's prose compares with the rest, then asked for
the rest to match it. Reading all four files first mattered, because the
obvious hypothesis was wrong: sentence length is nearly identical everywhere
(mean about 25 words, median 21 to 24), the no-semicolon rule is kept
throughout (the prose-only semicolons a first count found were tikz statements
and `\;` math spacing), and British spelling holds. The difference is not
complexity or house style, it is STANCE. Chapter 1 says what things are. The
drafted material rates them as well, and the rating is what the author wanted
gone. The rule is now a standing convention above.

Fifty-seven passages rewritten across `ch2_machine.tex`, `ch4_synthesis.tex`
and `app_proofs.tex`. The heaviest were chapter 4's opening participial
cascade, its closing "that, finally, is the use of building the microscope",
"Its limits are as clear as its reach, and stating them is part of the honesty
the thesis insists on", and the appendix's "Nothing here is deep" and "That is
not a defect of the computation".

**THE LINE THAT MATTERS WHEN DOING THIS AGAIN: a verdict about the WORK goes,
an epistemic fact about a RESULT stays.** Every proved/conjectured/open marker,
every "the search proves no upper bounds", every "the machine route was
abandoned unfinished and the hand proof replaced it", and every "the gap is not
closed" survived intact and was re-grepped afterwards to confirm it. Two
rewrites had to be redone because the first attempt replaced one tic with
another ("what matters here", "the two halves separate") or left a dangling
antecedent ("that boundary" with nothing to refer back to).

Also left alone deliberately: the author's own sentences in his hand-written
chapter 1 and the opening of chapter 2, including "It is the single most
important routine in the program", which is a verdict but is his.

VERIFY: `latexmk` exit 0, 104 pp unchanged, 0 overfull, 0 occurrences of `??`,
0 em-dashes, en-dashes or new prose semicolons on any changed line.

## 2026-08-26 (Opus, fourth pass) — constructions and machinery moved to the appendix

Author instruction: the main story should be quick, easy and visual, with the
constructions and the convoluted math appendixed, and the appendix ordered and
free of repetition. Body 36pp -> 33pp, appendix 55pp -> 59pp, total unchanged at
104pp, which is what a move rather than a cut looks like.

MOVED OUT OF THE BODY (every one a move, no label deleted, `??` still 0):
- ch1's three directed constructions (`const:directed-hub`, `const:bipartite`,
  `const:augmented-bipartite`) with their connectivity verifications, into a new
  `sec:dir-constructions` that now opens Part II. The body names each shape in
  words beside `fig:simple-digraph-m2` instead. These are the "cyclical graphs"
  the author singled out: the hub's ring arcs and the augmented wall's cyclic
  predecessors.
- ch1's `rem:threshold-convention`, MERGED into the appendix's
  `rem:threshold-audit`, which already opened by saying it completed it. Both
  labels are kept on the merged remark.
- ch2's mixed-integer model for $M^{*}(n)$: the six-line program, the cut-label
  discussion, the linearisation, `fig:cut` and `thm:dir-multi-small`, into
  `sec:mstar-model` at the END of the directed multigraph section, since
  `cor:mstar-integral` superseded it. The body keeps the scaling idea and
  `fig:scaling-reduction`, which is the visual half.
- ch2's "keeping the checker cheap" case analysis and regression-test detail
  into `sec:cheap-checker` in Part IV.
- ch4's `thm:multi-vertex-blocks` statement, down to sit with its own proof.

REPETITION REMOVED: Menger was stated in full in ch1, again in ch2 and again in
the appendix; ch2 now cites `thm:menger`. ch1 announced the $n=7$ tie three
times over (bridge paragraph, figure caption, following paragraph).

TWO LATENT TYPOS FIXED, both unbalanced parentheses in ch1 that had survived
every earlier pass: `(\Cref{fig:divergence}.` and the Gomory-Hu sketch's
unclosed `(`. `grep`-style paren balancing over prose lines found no others.

WHAT I DID NOT CUT, on inspection: `rem:case2-tight` looks like a digression but
proves that four is the best universal coefficient obtainable from the two facts
Case 2 uses, with a matching construction. That is mathematics, not commentary.
The appendix is 17k words of non-proof against 12k of proof, but most of the
non-proof is theorem statements, figures and the glosses that orient a reader
between arguments, not recap.

VERIFY: latexmk exit 0, 104pp, 0 overfull, 0 undefined refs, 0 occurrences of
`??`, 147 labels each declared exactly once, no em-dashes or en-dashes added.

## 2026-08-26 (Opus, fifth pass) — the variant grids: flipped, and one vocabulary

Two author calls on the four sixteen-variant grids.

**ROTATED 180 DEGREES.** They were turned so the figure's top sat at the left
edge of the page. `\usepackage[figuresright]{rotating}` changed NOTHING, because
the package default already behaves that way; only `figuresleft` flips it. The
option names do not read the way you expect, so **verify a sideways float by
rendering the page (`pdftoppm -f <page> -r 45 -png main.pdf out`), never by
reading the option name.** These four are the only sideways floats in the
thesis, so the preamble option affects exactly them.

**NO PER-PANEL SPECIAL CASE.** The simple directed arc panel drew the two
competing sub-branches of `conj:dir-arc` as dotted lines with an inline label,
which made one panel of sixteen carry a mark the other fifteen did not. The
`branches` key is gone from `gather_variant_grid`, from `plot_variant_grid` and
from `_reconcile_panel`, and the shared key lost its "named construction" entry
(four entries now, not five). Where a conjecture is a maximum of two counts, the
curve plotted is that maximum. The branches are named in prose in
`sec:dir-constructions` instead, which is where the constructions themselves now
live after the fourth pass. `ch2_machine.tex`'s caption no longer describes a
dotted line.

VERIFY: grids redrawn in 3s from the machine-value cache (484 entries, 0
computed), latexmk exit 0, 104pp, 0 overfull, 0 undefined refs, 0 `??`, program
self-check ALL CHECKS PASSED, all four figure pages rendered and inspected.

## 2026-08-26 (Opus, sixth pass) — figure 2.4, and where the appendix pages actually go

`plot_complexity_growth`: suptitle removed (the caption already says what is
counted), the key moved out of the right panel to one row under both, and the
"continues off the top" note moved into the empty upper-left corner with an
arrow, renamed to match the key exactly ("$3$-uniform hypergraph", not
"$3$-uniform directed"). Same `_save(tight=False, bbox_tight=True)` pattern as
the variant grids: no second rect-less `tight_layout` to discard the adjust, but
the tight save box still crops the surplus white the legend strip leaves.

**MEASURED THE APPENDIX RATHER THAN GUESSING.** 59 physical pages, split:
Part I classical machinery 9, directed arc $m=2$ 5, structural propositions 6,
directed multigraph chain 12 (skeleton 7, classification 3, historical model 1),
hypergraph bounds 4, hypergraph vertex 5, **directed hypergraph 11**, multigraph
vertex other convention 4, cheap checker 1, audit 2.

The author asked whether citing other people's results more often would save
space. **It would not, because that is already the practice**: `thm:menger` and
`thm:gomory-hu` are stated with citations and NOT reproved ("its standard
submodular-cut construction is proved in \cite{GomoryHu61}"), and the only proofs
in that section are the three-line degree bound and `prop:monotone`, which is the
thesis's own lemma that the search depends on. The one classical result reproved
in full is **Mader's theorem, about 4 printed pages**, and that is the single
real lever left. It is a scholarly call about self-containedness, not a cleanup,
so it went to the author, who chose to KEEP it in full. Recorded as a standing
convention above. The appendix therefore stays at 59 pages and there is no
further safe cut in it.

Other things checked and found NOT to be levers: only 5 figures in the whole
appendix; no theorem is stated twice (checked by label and by title); the
12k proof words against 17k non-proof words look lopsided but the non-proof is
theorem statements, figure captions and the glosses that orient a reader between
arguments; and the one genuine internal repetition (the tail-head count derived
in both `prop:dir-hyper-general` and `thm:dir-hyper-general-constant`) is six
lines that the second proof needs in a different form, and it already says so.

VERIFY: latexmk exit 0, 104pp, 0 overfull, 0 `??`, 116 tests OK with 1 expected
skip.

## 2026-08-27 (Opus) — a full read for mistakes, then the audit item and the cache

The author asked for a read of the whole thesis to find and fix mistakes, then
for the two open `REVIEW_STATUS.md` items. Everything below is verified against
the program rather than against an earlier note.

**NINE DEFECTS FROM THE FULL READ.** The heaviest cluster was left by the pass
that swapped annealing for tabu in the narrative: the argument was rewritten and
the vocabulary was not. `tab:rediscovery`'s caption said the Search column came
from annealing and called it "the temperature search", while ch2 two pages
earlier said every discovery value comes from tabu, which is what `solve`
actually defaults to for matrix models. Four more leftovers ("the cooled search"
twice, "repeated cooling runs", ch4's "one cooled search"). ch2 cited
`const:directed-hub` for the doubled star the multigraph runs land on, but that
construction is a SIMPLE digraph with m(n-1) arcs, 9 at n=4 m=3, where the table
prints the thickened tree's 12. ch2 said a digraph has "twice as many
possibilities" as the undirected graph on the same vertices, where it is the
square. Plus: `thm:hyper-vertex-m2` named a multihypergraph maximum with the
simple-hypergraph symbol, two "In words" glosses had drifted away from the
statements they gloss, `lem:reach-skeleton` had no proof environment, the SA
abbreviation was defined and never used, and an answered author question sat in
the source.

**THE MATHEMATICS WAS NOT THE PROBLEM.** The S-T exceptions, the n=14
divergence, the m=3 n=10 refutation, every crossover, Mader's double count, the
skeleton convexity argument, `lem:incidence-rank`, the bipartite-block
optimisation and the 194066 two-connected graphs on nine vertices all check out.
Every defect was in the seam between prose and code, which is where both review
batches also found theirs.

**REVIEW_STATUS ITEM 1, the hypergraph curve, CLOSED.** `_reconcile_panel`
invariant 1 capped every `proved=` curve to any machine-exact value, which is
right for a curve carrying a closed-form VALUE and wrong for one carrying
`prop:hyper-edge`, an upper BOUND. Measured before fixing: the clamp fired at ONE
plotted point in the thesis. That note's estimate that a fix touches every panel
in `gather_variant_grid` was wrong by twelve panels. Fixed with a per-panel
`clamp_formula=False` on the four hypergraph panels, and the key now says "proved
upper bound" in a grid whose every blue curve is one, which is a property of the
figure and needs no per-panel mark.

**REVIEW_STATUS ITEM 2, the sixteen-variant rewrite, AUDITED.** The count is
clean. Two defects. `tab:summary` claimed repeats close cases the simple model
misses at m=3, which is true but had no theorem behind it: added
`prop:hyper-vertex-lower-multi`. And **the cap-mu gate was backwards from the
prediction**: `thm:menger-hyper` and the code agreed at capacity one, one gate
per COPY, while the two gadget figures and the ch2 prose described a capacity-mu
gate nothing built. On the author's call the CODE moved to the text:
`_hyper_capacity_matrix` now gives each distinct hyperedge one gate of capacity
mu. Merging is the parallel-arc reduction, so no value can change, and that is
checked rather than asserted (149532 measurements, 0 mismatches) and pinned by
`MergedGateMatchesPerCopy`, which keeps the old construction as its reference.

**THE CACHE COULD SILENTLY DEGRADE THE FIGURES, AND NOW CANNOT.** A refresh run
while the test suite was competing for CPU came back with 123 changed values. The
checker was not the cause (benchmarked at 1.006x, and the differential test
proves the values). They are TIMED measurements, and the record itself needed
more budget than it granted: four completed exhaustions in it take about 8.4s
against a 4s budget, so they returned "did not finish", and `_exact_points` stops
at the first one and dropped four more sizes behind them.

Two changes. `MachineValues._reconcile` now holds every recomputed value against
the published one: a `None` never overwrites a recorded exact value, a weaker
search result never overwrites a stronger one, and two DIFFERENT exact values are
reported as a contradiction rather than applied. So a refresh can confirm the
figures or improve them and has no path to making them worse, and every departure
is printed. Nine tests in `tests/test_machine_values.py`. And the exhaustion
budget went 4s to 60s, chosen by probing all 23 unfinished entries at 45s: two of
them finish, at 24.3s and 28.6s, and 21 do not, so anything under about 30s
leaves a completed exhaustion marginal. Search budgets deliberately unchanged,
since raising those moves witnesses rather than reproducing them.

**THE BUDGET IS PART OF THE CACHE KEY**, so raising it would orphan all 128 exact
entries and bypass the guard exactly when it is needed. The completed ones were
relabelled (a finished exhaustion's value does not depend on how long it was
allowed) and the 23 unfinished ones dropped and recomputed, since "did not finish
in 4s" is not the same claim as "did not finish in 60s".

## 2026-08-27 (Opus, seventh pass) — the author's two inline comments in ch2

Two instructions left as source comments in `chapters/ch2_machine.tex`, executed.

**THE SPINE DIAGRAM.** `%change the picture: remove 'cut-counting, search' and
'annealing'` sat after `fig:spine`. The `\spinediagram` macro (`preamble.tex`)
gave its PROVE node the subtitle "cut-counting, search" and its DISCOVER node
"annealing, tabu". Annealing left the thesis narrative in an earlier pass
(tabu is the only search method described now) and the historical cut-counting
MILP is no longer PROVE's headline route, so the PROVE node lost its subtitle
entirely and DISCOVER's now reads "tabu" alone. Comment deleted.

**THE GENERATING-SEARCH BENCHMARK TABLE**, requested by
`%include a small table (of different runs for values (n,m) to compare before
and after) for ggenerating search here and also with and without pruning` at
the end of `\subsection{Generating search}`. Timed three ways of proving
$\ell_2^{\mathrm{dir}}(n)$ on a single core, $n = 3..7$: a blind sweep with no
pruning at all (reference sweep from `tests/test_solve.py`, reimplemented
standalone), the in-house pruned search (`_exhaustive_directed`), and the
geng-generated pipeline (`enumerate_extremal_directed_multigraphs_via_generation`,
`parallel=False` for a fair single-core comparison). Numbers are real
measurements from this machine, not invented: blind 0.05s/6.3s at $n=3,4$ then
abandoned (2^{n(n-1)} makes $n=5$ tens of minutes with this reference
implementation); pruned 0.003s/0.008s/0.22s/14.5s/1156.6s at $n=3..7$; geng
0.009s/0.008s/0.039s/0.73s/17.0s. Below $n=5$ both are overhead-noise (a
Python call against a subprocess spawn); from $n=5$ generation pulls ahead by
5.5x, 20x, 68x. New `\Cref{tab:generating-benchmark}` with two sentences of
prose, sourced from `figures/generating_benchmark_table.tex`, matching
`tab:rediscovery`'s `\input`-a-tabular house style. The benchmark script is
saved at `research_notes/scripts/generating_search_benchmark.py` for
reproduction, following the same sys.path pattern as the other standalone
scripts in that directory.

**ONE MORE DEFECT FOUND IN PASSING.** The same author hand-edit that added the
two comments also introduced `\Cref{FordFulkerson56}` where the surrounding
sentence cites a paper, not a labelled float. Fixed to `\cite{FordFulkerson56}`;
this would have printed a `??` inline (cleveref has no bibkey to resolve) had
it survived to build.

**A STASH RECOVERY, FOR THE RECORD.** Baselining the pre-change build via
`git stash` and a rebuild-then-pop briefly diverged the working tree: the pop
reported a conflict on one file yet silently dropped the edits to two others.
Nothing was lost because the stash itself still held everything from the
moment of stashing; `git checkout stash@{0} -- <path>` per file, verified
against the stash's own diff before dropping it, is the recovery. Lesson for
next time: don't stash a dirty tree that mixes the author's own uncommitted
prose with in-progress edits just to get a baseline build. A worktree or a
plain `git diff` against HEAD on the specific changed hunks would have gotten
the same baseline without touching the working tree at all.

VERIFY: `latexmk -C` then a clean rebuild, exit 0, 106pp, 0 overfull, 0
occurrences of `??` in the extracted PDF text (an intermediate build before the
`-C` clean exited 12 on a corrupted `\@writefile` from stale aux/toc state left
over by the stash episode above; the clean rebuild fixed it, source content was
never the cause). 127 tests OK, 5 expected skips (optional deps not installed
in this environment). Self-check ALL CHECKS PASSED. No em-dashes, en-dashes or
new prose semicolons on any changed line; no banned verdict-prose phrases.

## 2026-08-27 (Sonnet) — the double star was wrong, four more ch2 comments, a full-thesis read

Four remaining author comments in `ch2_machine.tex`, found after the previous
session's commit (`cfc5a7f`) had already executed two others.

**THE DOUBLE STAR PARAGRAPH WAS NOT JUST WONKY, IT WAS WRONG.** The author's
comment called the reasoning wonky and asked for a better explanation, not a
rewrite of the math. Reading it against the rest of the thesis turned up an
actual defect: the paragraph's own inline definition of "double star" (two
distinct vertices $a,b$, a one-directional in-star to $a$ and out-star from
$b$) gives $2n-3$ arcs by direct count, not the $2(n-1)$ every other mention
of the double star needs. `program/erdos915_unified.py`'s `double_star()` is
one hub bidirected to every leaf, and the thesis's own worked example two
paragraphs later (36 arcs at $n=7,m=4$) only checks out against $2(n-1)(m-1)$
with the single-hub shape. Rewritten to name the correct construction via
`\Cref{const:dir-multi-lower}` rather than redefine it inline, and to fix the
logic the wrong definition was papering over: the double star only witnesses
$M^*(n)$ through the $n=7$ crossover, past it the bipartite construction
takes over, so the old "such an integral optimum exists for every $n$"
overstated what `cor:mstar-integral` actually proves. What generalises to
every $n$ is not the double-star shape but the bare existence of *some*
$\{0,1\}$ maximiser, proved by a different argument entirely (clearing
denominators from a rational optimum).

**THE OTHER THREE.** "Measuring only on the possible bounds" is now a
`\subsection` of "The heuristic search" rather than its own section: the
author guessed it belonged next to Pruned/Generating search instead, which
checked out false, its running-bound bookkeeping needs the walk's add/remove
move structure and does not exist on the DFS-based exhaustive code paths.
The benchmark-table question (add this bookkeeping trick as a fourth
compared method?) is answered by leaving the table alone, for the same
reason. `tab:rediscovery` gets a `Variant` column naming each row's symbol
($\ell_m(n)$, $L_m(n)$, $\ell_m^{\mathrm{dir}}(n)$, $L_m^{\mathrm{dir}}(n)$),
found by a background full-thesis pass since the two comments requesting it
(`%no need to put the m values in the names` and the variant-symbol ask)
don't match the imperative-verb grep used to find the other three.

**A FULL READ FOUND NOTHING ELSE.** A background pass read every remaining
chapter (`ch1_basecases`, the rest of `ch2_machine`, `ch4_synthesis`,
`app_proofs`) against its own cited definitions and theorems, the same
diligence the double-star fix used, and confirmed no second case of that
shape. Two items read but not re-derived line by line: the directed
hypergraph section and the hypergraph-vertex block primer, both dense
multi-step proofs with no surface inconsistency found.

**BUNDLED WITH THIS COMMIT, NOT THIS SESSION'S WORK:** the edge-sensitivity
section's archival to `offcuts.tex` (author instruction, same day) was
already staged when this session started. `\sigma(e)` was an annealer-only
removal bias that tabu, the source of every reported value, never uses.
Recorded here only because it shipped in the same push.

VERIFY: `latexmk -pdf` exit 0, 104pp, 0 overfull/underfull, 0 undefined refs,
0 occurrences of `??` in extracted text.

## 2026-08-27 (Sonnet, second session) — n=2 in the four variant grids

The author flagged two things about `figures/variant_bounds_m{3,6}_{graphs,
hypergraphs}.png`: n=2 looked too trivial as a starting point, and the
leftmost plotted point in two of the four figures showed a search-found
lower bound where it should have shown a proved value.

**BOTH TRACED TO `make_figures.py:gather_variant_grid`.** Panel 7
(multigraph directed arc, proved for every n>=2 by `thm:dir-multi-full`) computed
its machine-checked points with `ex7 = _exact_points(range(3, 6), ...)`, the
only "proved" panel among the sixteen whose exact range excludes n=2. Every
sibling proved panel (`ex`, `ex2`, `ex5`, `ex9`, `ex13`) starts at `range(2,
...)`. Since the search curve (`se7`) does cover n=2, that panel's leftmost
point rendered as a bare open circle with no green square backing it, in
both `variant_bounds_m3_graphs.png` and `variant_bounds_m6_graphs.png` (the
two figures carrying the graph-model row). Confirmed by cropping the
rendered PNG before and after: before, n=2 was circle-only; after
`range(2, 6)`, it is the same green square every other proved panel gets.

Separately, the eight hypergraph/multihypergraph panels (r=3) are
structurally zero at n=2, since no 3-element subset exists on 2 vertices.
Not a bug, but the author judged it an uninformative point rather than a
real one, and asked (via clarifying question, since it touches the code's
"same range for every panel" invariant) to drop it for the hypergraph rows
only, keeping the graph-model rows at n=2 where the value is real (K_2 has
1 edge). `hyper_ns` moved to `range(3, 13)`, and the eight matching exact
ranges (`ex9`..`ex16`) each shifted their lower endpoint from 2 to 3 to
match. `matrix_ns` (graph-model rows) is unchanged.

VERIFY: `make_figures.py --grids-only` regenerated all four grids (453/454
values from cache, 1 newly computed); all four inspected. `latexmk -pdf`
exit 0, 0 overfull, 0 undefined refs, 0 occurrences of `??` in extracted
text.

## 2026-08-27 (Sonnet, third session) — exact-value tables beside the four variant grids, and the thesis renamed

**RENAME.** `\title` and `pdftitle` (which had drifted from each other and
from the cover page's rendered text) both moved to "Maximizing Edge Density
Subject to Connectivity Constraints"; `pdfsubject`'s stale "twelve
structural variants" corrected to "sixteen" while in there.

**THE TABLES.** The author asked for the four variant-bounds grids'
numbers in table form, exact values a reader can read off rather than a
curve position to eyeball, same colour code, and to run the code to find
m/n ranges that land mostly inside what is actually known. `gather_variant_grid`
already carries everything needed (it feeds the plots), so
`program/make_figures.py:variant_value_tables()` reuses it directly: no new
solving, only formatting, confirmed by the 3-second `--tables-only` run
pulling almost everything from `figures/machine_values.json`.

Four new colours in `preamble.tex` (`vtProved`/`vtConjectured`/`vtOpen`/
`vtExact`/`vtSearch`) are the LITERAL hex codes `plot_variant_grid` uses
(`_KUL_BLUE`/`_RED`/`_GUESS`/`_GREEN`/`_VIOLET`), not the visually-close but
not-identical `regimeProved`/`regimeConjectured`/`regimeOpen` already used
by `fig:variant-tree-status` -- kept those alone rather than retuning an
existing figure nobody asked to change.

**GETTING THE EPISTEMIC STATUS OF EACH CELL RIGHT WAS THE ACTUAL WORK.**
A number's colour is its row's curve colour (blue/red/gold); a bold GREEN
override means the machine independently confirmed it exact, exactly like
a filled square in the figure. Everything else needed a prefix to stay
honest: a proved GRAPH row (Mader, `thm:dir-multi-full`, ...) gets no
prefix past its exhausted range, because the closed form IS the value for
every n, not a bound merely reached at small sizes. The four hypergraph
"proved" rows are different -- `_reconcile_panel` already marks them
`proved_is_bound=True` because `prop:hyper-edge` is a proved upper bound,
attained only inside stated ranges -- so those get `$\le$` past their exact
range, not a bare number. Conjectured and open rows get `$\ge$`: the
number is a verified construction, optimality is not proved. Missing this
distinction would have silently overclaimed exactly the thing
`ch2_machine.tex`'s existing prose already warns about (the $m=6,n=6,r=3$
cell reading $12$ where the truth is $11$) -- and the generated table's
`n=6` cell for that row does read `$\le12$`, not a bare `12`, confirming
the gating works.

Row metadata (`_VARIANT_ROW_META`) reuses `tab:rediscovery`'s own symbols
for the eight graph rows ($\ell_m(n)$, $k_m(n)$, $\ell_m^{\mathrm{dir}}(n)$,
$k_m^{\mathrm{dir}}(n)$, $L_m(n)$, $L_m^{\mathrm{dir}}(n)$); the eight
hypergraph rows have no standing short symbol elsewhere in the thesis and
none was invented for them.

n-ranges (`_GRAPH_TABLE_NS = 2..8`, `_HYPER_TABLE_NS = 3..8`) were picked
after printing every panel's actual `exact_ns` at $m=3,6$ (not guessed):
graph rows mostly exhaust to $n=5$-$8$, hypergraph rows to $n=3$-$5$
(the two multihypergraph directed rows only to $n=3$), so both ranges run
a couple of sizes past that into formula/lower-bound territory, giving
each table a dense proved/exact core that thins into qualified entries,
the tabular analogue of a plot whose squares run out before its circles
do.

Four tables (`tab:variant-values-m{3,6}-{graphs,hyper}`), each `\input` right
after its matching `sidewaysfigure`, `\resizebox{\textwidth}{!}` for safety
against the 9-10 column width, `\multirow` grouping the model column exactly
as the figure groups rows. LaTeX's float placement packed three of the four
onto one page and left the fourth alone on the next, which is `[p]` behaving
normally (a floats-only page, not one float per page) and not a placement
bug.

VERIFY: `make_figures.py --tables-only` wrote all four fragments from cache
(no new solving). `latexmk -pdf` exit 0, 106pp, 0 overfull, 0 undefined
refs, 0 occurrences of `??`. All four rendered pages inspected directly
(not just the log) and cross-checked against three independent facts
already stated elsewhere: $\ell_3(2)=1$ (Mader's floor), $L_3^{\mathrm{dir}}(2)=4$
(the n=2 fix from the second session above, now shown bold green rather
than a bare circle), and the $m=6,n=5/6,r=3$ hypergraph values ($8$ exact,
$\le12$ not $12$) against `ch2_machine.tex`'s own stated $11$.

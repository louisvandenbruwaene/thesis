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
  127 tests, 1 expected skip on a minimal (no-pulp) install.
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
- **THE AI MEDAL. Every proof-carrying result the model wrote carries
  `\aimedal` in its theorem head, and a new one must be stamped too.**
  Author instruction, 2026-08-28: he has not verified them all and for some is
  not qualified to, so the badge says "conjecture with a probably-correct proof
  attached", not "theorem I vouch for". The macro is at the bottom of
  `preamble.tex`; usage is `\begin{lemma}[Title,\aimedal]` for a named result
  and `\begin{theorem}[\aimedal]` for an unnamed one. It goes on
  theorem/proposition/lemma/corollary/claim only. It does NOT go on: results
  quoted from the literature with a citation and no proof here (Menger,
  Gomory--Hu, Baranyai, Mader, Leonard, Sorensen--Thomassen); the Gomory--Hu
  double count of `sec:mader-gomory-hu` that proves `thm:mader` and
  `thm:multigraph-edge` out of `lem:dist-1-count`, `lem:sum-dist` and
  `lem:double-count`, which the author worked through himself; or definitions,
  constructions, remarks, notation, conjectures and questions, which state
  nothing a proof could settle. The rule is written out in three places that
  must stay in step: the Contribution Statement, the abbreviations table, and
  the appendix's "How to read this appendix" paragraph. `thm:hyper-gomory-hu`
  IS badged even though it is a transported classical construction, because
  the hypergraph statement is asserted here rather than quoted verbatim.
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
ch3, app_proofs, both READMEs and this file.

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

Fifty-seven passages rewritten across `ch2_machine.tex`, `ch3_synthesis.tex`
and `app_proofs.tex`. The heaviest were chapter 3's opening participial
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
- ch3's `thm:multi-vertex-blocks` statement, down to sit with its own proof.

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
twice, "repeated cooling runs", ch3's "one cooled search"). ch2 cited
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
chapter (`ch1_basecases`, the rest of `ch2_machine`, `ch3_synthesis`,
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

**MERGED TO ONE TABLE**, same session, on the author's follow-up request.
`variant_value_tables()` now writes a single `figures/variant_table_all.tex`
instead of four: one shared column grid (`_TABLE_NS = 2..8`, the graph rows'
range) for every row, an `$m=3$`/`$m=6$` `\multicolumn` section header
before each half, and `_panel_cell` returns `None` (an empty cell, not a
value) wherever `n` sits outside a panel's curve range at all -- the one
new case being every hypergraph/multihypergraph row's `n=2` column, since
`hyper_ns` starts at 3. `ch2_machine.tex` collapsed to one
`table` environment (`\label{tab:variant-values}`) after the fourth
`sidewaysfigure`, replacing all four `tab:variant-values-m{3,6}-*` labels
and their per-table captions with one caption covering every distinction
the four used to split across themselves (bound-vs-value, lower-bound
witness, the m=6 Leonard cutoff, the blank-cell convention).

**A REAL BUILD FAILURE ON THE WAY, UNRELATED TO THE CONTENT CHANGE.** After
deleting the four old fragments and editing the chapter, `latexmk` came
back exit 12 with pdflatex choking on null bytes (`^^@`) reading what
should have been `main.aux`, and 40 references reported undefined as a
result. This is the exact failure mode `CLAUDE.md` already documents from
two sessions ago ("latexmk -C then a clean rebuild"): stale/corrupted
aux state from a prior run, not a defect in the new table or chapter edit.
`latexmk -C` followed by a plain rebuild fixed it immediately, and the
result matches the git diff exactly, confirming the source was never the
cause.

VERIFY: `latexmk -C` then `latexmk -pdf` exit 0, 106pp, 0 overfull, 0
undefined refs, 0 occurrences of `??`. The merged table's page rendered
and inspected directly: all thirty-two rows fit on one page with room to
spare, section headers and blank n=2 hypergraph cells both render as
intended.

## 2026-08-27 (Sonnet, fourth session) — moved conj:dir-arc and four theorems between chapters, then fixed the fallout of a half-finished author edit

Two requests in one session. First, move `conj:dir-arc` (then in ch1's
"Conjectured bounds" section) to the final chapter, and move the four
theorems the final chapter stated (`thm:dir-arc-linear-error`,
`thm:dir-vertex-linear-error`, `thm:dir-multi-full`,
`thm:dir-hyper-constant`) to chapter 1's "Proven bounds", each moved with
its explanatory prose rather than just the bare statement. ch3 keeps a
one-sentence bridge at each former site, referencing the relocated result
by label, so the surrounding synthesis argument still reads without
restating what moved. Committed as `e166fab`.

Second request, "fix all errors in the pdf". The build itself was already
clean (0 `??`, 0 overfull), so the errors were in content coherence. The
working tree held an uncommitted author edit that commented out ch2's
"Results and evidential status" section with a note that it belongs in the
final chapter and needs rephrasing, and the removal had been left
half-done: `tab:variant-values`'s own caption said its $m=6,n=6,r=3$ claim
was "established by the full enumeration in the paragraph above" with no
such paragraph left above it (the 125,970-hypergraph exhaustion that
justified it was inside the deleted block), and "certifier" / "replayable"
were used in ch3 and the appendix without ever being defined anywhere
still visible.

**FOUND THIS IS DIFFERENT FROM STALE-AUX.** The first rebuild attempt after
picking this up exited 12 with 121 undefined refs, matching the exact
symptom this file already documents for stale `.aux` state. `latexmk -C`
then a clean rebuild fixed it, confirming the source was never the cause,
same as the two prior occurrences of this failure mode.

Rather than restore the deleted block verbatim (much of it duplicated
material already stated elsewhere: the crossover/counterexample recap now
sits in ch3's own `conj:dir-arc` discussion, and the colour-code legend is
already in each figure's own caption), split what remained genuinely
missing by where it belongs. The evidential-status vocabulary
(checker measures, exhaustion proves, certifier is a finite check without
a replayable bound, search only witnesses) now sits in ch3's
"Contributions and limitations" section, next to where that vocabulary was
already being used undefined. The specific $m=3$ exhausted values
($6,9,12,15$ for $n=3..6$) now back the `conj:dir-arc` discussion, replacing
the vague "small $m=3$ cases". The hypergraph exhaustion fact is restored
immediately above the table that cites it, so "the paragraph above" is true
again.

**TWO STANDING STYLE VIOLATIONS FOUND WHILE IN THERE**, both in
`tab:variant-values`'s own caption: an en-dash (`--`) used as parenthetical
punctuation, and a prose semicolon. Both fixed; neither was related to the
comment-out.

Also folded in a proofreading pass that was already sitting uncommitted in
ch1/main.tex/ref.bib/this file when the session started (small wording
fixes, a `\Cref` retarget, a `@misc` bibtex-type fix) since it was correct
and the resulting whole-tree state needed committing together to stay
buildable from a clean checkout.

VERIFY: `latexmk -C` then `latexmk -pdf` exit 0, 104pp, 0 overfull/
underfull, 0 occurrences of `??`, 0 undefined refs, no duplicate labels,
no banned verdict-prose phrases, no new em-dashes/en-dashes/prose
semicolons. Committed as `b17ae67`.

## 2026-08-27 (Sonnet, fifth session) — a third external review, one real
## machine-value bug, and a plotting-crash environment gotcha

A third external review found nine issues. Eight were prose-only (a Mader
equality claim false at `n=2, m=3` with `K_2`, a "doubles" complexity claim
that should say "squares", `M^*(n)`'s definition missing `s \ne t`, the
integrality proof crediting the wrong half of the argument to the wrong
technique, the energy function and "toggling an arc" both narrower than the
section they sit in, the opening graph definition conflating graphs and
hypergraphs, a misattributed "matching upper bound is open" paragraph, and a
cluster of grammar fixes), all fixed directly in `ch1_basecases.tex` and
`ch2_machine.tex`, plus a missing `\texorpdfstring` on `sec:mstar-model`'s
heading (the likely PDF-bookmark warning source, matching the pattern
already fixed at two other headings).

**THE NINTH WAS A REAL BUG, THE SAME SHAPE AS THE 2026-08-27 MACHINE-VALUE
BUDGET BUG BUT AT A DIFFERENT CELL.** `rem:dir-vertex-m3` (`app_proofs.tex`)
states `\ell_3^{\mathrm{dir}}(6) = k_3^{\mathrm{dir}}(6) = 15`, "every entry
proved complete." `variant_table_all.tex`'s `n=6` cell on both directed rows
of the `m=3` simple-graph block read `\ge 15`, unbolded and conjectured-red,
because `gather_variant_grid`'s panels (3) and (4) shared `_EXACT_BUDGET`
(60s), calibrated for the hypergraph panels and nowhere near enough for
this pair: measured directly with `solve(6, 3, exhaustive=True, ...)`, the
edge separation takes 544.2s and the vertex separation 1422.7s on this
machine. `n = 7` does not finish even in the appendix's own hour and a half,
so raising the shared budget outright would have made every regeneration
(at both `m = 3` and `m = 6`, since the two panels are built once per `m`)
risk burning up to two more multi-thousand-second timeouts trying `n = 7`
for nothing. Fixed with a dedicated `dir_simple_exact_budget = 1800.0` and
the range capped at `range(2, 7)`, so `n = 7` is never attempted at all
regardless of `m`, which reproduces exactly the boundary the appendix
already proves and cannot regress into a multi-hour rebuild. `m = 6`'s
own `n \le 6` values needed fresh cache entries too (the budget is part of
the cache key) but complete quickly, so the only visible output change is
`variant_bounds_m3_graphs.png` and the three affected table rows; the other
three grids and every other row are byte-for-byte unchanged, confirming the
fix is exactly as narrow as intended.

**A SESSION CONVENTION WORTH RECORDING: THIS REPO'S BARE `python3` IS NOT
THE RIGHT INTERPRETER FOR ANYTHING FIGURE-RELATED.** The first regeneration
attempt ran under the system `python3`, which has no matplotlib installed at
all. `erdos915_unified.py`'s import guard sets `plt`, `mlines` and every
other matplotlib name to `None` together on any `ImportError` in that block,
so the module loads fine and every non-figure function (the solver, the
checker, the test suite) works normally, and `plot_variant_grid` runs for
most of its length before failing late, on `mlines.Line2D`, deep inside
legend construction, rather than immediately on `plt`. A hundred-plus line
traceback that only fails at the very end of a plotting function is a sign
of a missing optional dependency, not a code defect, and the fix is to use
**`.venv/bin/python3`**, this repo's own virtualenv, which has matplotlib
3.11.0 and every other optional dependency installed. Every command in this
file that touches `program/make_figures.py`, `plot_*`, or anything under
the FIGURES section of `erdos915_unified.py` should invoke that interpreter,
not the bare `python3` on PATH.

VERIFY: `solve(6, 3, exhaustive=True, ...)` independently confirms 15 for
both separations (544.2s edge, 1422.7s vertex, matching the appendix).
`make_figures.py --grids-only` then `--tables-only` under `.venv/bin/python3`
regenerate cleanly (442 cache hits, 10 fresh computes, all in the `m=3`
directed simple-arc/vertex panels). `latexmk -pdf` exit 0, 104pp, 0
overfull/underfull, 0 undefined refs, 0 occurrences of `??`. 127 tests OK,
1 expected skip. Program self-check ALL CHECKS PASSED.

## 2026-08-27 (Sonnet, sixth session) — three more inline author comments in ch2

Three remaining author comments in `ch2_machine.tex`, none touching the
program, all prose/placement only.

**THE "WEIRD BULLSHIT" PASSAGE.** Two commented-out paragraphs sat dead in
`sec:rediscovery` (never printed, since both were themselves `%`-commented),
sandwiching the author's judgment: "this just seems like some weird bullshit
i don't wanna read ... extract the things that need to be said, and say it
better and or elsewhere." Read against the rest of the thesis first: the
first paragraph's per-model rediscovery facts (spanning tree, multigraph
star, thickened star, bidirected star, the $n=7$ tie) are stated nowhere
else, so they were rewritten and printed. The second paragraph's headline
numbers (the $n=8$ wall's $16$ against the hub's $14$, the $m=3,n=10$
augmented-bipartite $30$ against $27$) turned out to be **already stated**
in `ch3_synthesis.tex`'s "Two principal phenomena" section, so restating them
here would have violated the thesis's own repetition-removed convention.
Kept only what that section does not carry: the tabu search's own stall at
$n=8,m=2$ (a fact about the search, which is this section's actual subject)
and the $n=7,m=4$ double-star witness ($36$ arcs). Both new paragraphs are
now live prose, checked against the no-em/en-dash and no-prose-semicolon
rule and the banned-verdict-phrase list.

**THE SIDEWAYS FIGURES, MOVED.** `%move these sideways figures to the last
chapter, alongside their exlpanation` sat before the four
`variant_bounds_m{3,6}_{graphs,hypergraphs}` grids. Moved them, their design-
rationale comments, the `tab:variant-values` table, and the two paragraphs
between them, out of ch2's rediscovery section and into ch3's own "Summary
of the sixteen variants" section, right after `tab:summary` and
`fig:variant-tree-status`, which is the coarse version of the exact same
sixteen-variant status these four grids and this table give as numbers. One
new bridging sentence introduces them there. All four labels
(`fig:variant-bounds-m{3,6}-{graphs,hyper}`) and `tab:variant-values` are
unchanged, so the one cross-reference to them from `app_proofs.tex` still
resolves without edits. Rendered all five relocated pages after the rebuild
(the `.aux` label page numbers do not match `pdftoppm`'s physical page
index, since front matter uses roman numerals; used `pdftotext` per-page
splitting to find the true physical pages instead) and confirmed all four
grids and the table still fit inside their sideways/portrait pages at the
new location.

**THE "WTF" COMMENT.** `%wtf: you can't prove something for all values and
then just say: oh we found one that doesn't work, but don't worry` sat
before the $m=6,n=6,r=3$ hypergraph-exception paragraph. The paragraph was
never actually contradictory, `\Cref{prop:hyper-edge}` is proved as an upper
BOUND, not as an attained value, but "the curve's $12$ overstates the true
maximum of $11$" read like a theorem failing rather than a bound simply not
being tight. Reworded to lead with what the theorem does and does not claim
(bounds from above, does not claim attainment outside its stated ranges)
before stating the $m=6$ non-attainment fact, so the paragraph now reads as
one proved fact about non-attainment rather than a theorem-vs-counterexample
tension.

**A SEMICOLON SLIPPED INTO MY OWN FIRST DRAFT OF THE BRIDGING SENTENCE**,
caught by grepping the diff before committing rather than after. Two-sentence
split instead.

VERIFY: `latexmk -C` then `latexmk -pdf` exit 0, 104pp, 0 overfull, 0
undefined refs, 0 occurrences of `??`. No em-dashes, en-dashes or prose
semicolons in the diff (checked directly against `git diff`, not by eye). No
duplicate labels introduced. All three executed comments deleted from the
source (they no longer exist in `ch2_machine.tex`).

**FOLLOW-UP, SAME SESSION: the rediscovery paragraphs named shapes with no
picture.** The author pushed back on where the rediscovery prose lived (ch2
vs ch3), which was the right call to leave alone (see the author's own
answer, kept as a standing convention below), then separately objected to
the prose itself: it named constructions ("thickened star", "double star")
with no figure, reading as unmotivated jargon. Checked first whether a
picture already existed: `fig:simple-digraph-m2` (ch1) already draws the
bidirected star and the one-directional wall tying at $n=7$, so those two
mentions now `\Cref` it directly instead of describing it blind. The other
three named shapes (the spanning tree, the doubled undirected multigraph
star, the doubled bidirected directed-multigraph double star) had no
figure anywhere, so a new compact one, `fig:rediscovery-gallery`, draws all
three side by side, each sized to the exact `(n,m)` that `tab:rediscovery`
reports for it, reusing the shared TikZ vocabulary (`gvertex`, `gvhub`,
`gline`, `gdir`, `gcurve`/`gcurveR`) so it matches the rest of the thesis's
look rather than inventing a new one. The multiplicity-doubling convention
(parallel bent lines, not a numeric label) follows `fig:scaling-reduction`'s
existing precedent.

**ONE ITERATION NEEDED ON THE NEW FIGURE.** The double-star panel's first
draft used bend angles of $14°$ and $5°$ for the two arcs each direction,
which is what the multigraph-star panel uses successfully for its two
undirected arcs. Rendered and inspected: with four arcs instead of two, that
spread was too tight, the four collapsed into what read as a single thick
spoke with no visible multiplicity or direction. Widened to $30°$/$11°$,
rendered again, and now all four arcs and both arrowheads per spoke are
individually visible. The lesson generalizes: a bend spread tuned for a
2-line pair does not automatically carry over to a 4-line bundle, check by
rendering rather than by reusing a working angle from a lower-multiplicity
panel.

VERIFY: `latexmk -pdf` exit 0, 104pp, 0 overfull, 0 occurrences of `??`, 0
undefined refs. New figure's page rendered at 110dpi and inspected directly,
twice (before and after the bend-angle fix). No duplicate labels, no banned
verdict phrases, no em/en-dashes or prose semicolons in the diff.

## 2026-08-28 (Opus) — the author's inline comments in the last chapter, and ch4 -> ch3

Eleven instructions left as source comments in what was `chapters/ch4_synthesis.tex`,
executed, plus the rename the author asked for in the same message.

**THE RENAME.** The chapter has been the THIRD `\chapter` in `main.tex` for some
time, so `\Cref{ch:synthesis}` already printed "Chapter 3" and the PDF was never
wrong. What still said four was the filename and the human-readable strings:
`chapters/ch4_synthesis.tex` -> `chapters/ch3_synthesis.tex` (git mv, so history
follows), and every `ch4` in `main.tex`, `offcuts.tex` provenance headers,
`README.md`, `TASKS.md`, `REVIEW_STATUS.md`, `research_notes/`, `preamble.tex`
comments and this file. **Left alone deliberately: `program/erdos915_unified.py`'s
own CHAPTER 3 / CHAPTER 4 banners.** Those are the PROGRAM's internal divisions,
not the thesis's, and `MachineValues`' cache fingerprint is defined as the hash of
everything above the chapter 4 banner. Renaming them would have orphaned the
cache for no gain.

**THE BACKWARD-ARC PANEL, DELETED.** The author's objection was that it redraws
the $A \to B$ construction the reader has already seen and adds one arc. The
mathematical content, that a single returning arc lets a route escape $B$ through
$A$ and blow the internal $m-2$ budget, is one sentence and is now one sentence.
`fig:directed-frontier-pair` and `fig:backward-arc` are gone (nothing outside the
chapter referenced either), and `fig:crossover` is now a plain figure.

**THE CROSSOVER PLOT.** `plt.title` removed from `plot_directed_crossover` (the
caption already carries it) and `make_figures.py` calls it with `max_n=15` instead
of `24`. At $m = 3$ the crossover is at $n = 9$, so 15 leaves the transition in
the middle of the frame instead of in the first third.

**A NEW FIGURE WHERE THE OLD PANEL WAS.** The author asked for constructions of
extremal graphs in this chapter, and `const:augmented-bipartite` is the shape the
whole quadratic argument turns on and had never been drawn.
`fig:augmented-wall` draws its $m = 3$, $n = 10$ instance: $|A| = 4$, $|B| = 6$,
24 faint arcs $A \to B$, and the $m - 2 = 1$ cyclic in-arc per vertex of $B$.
**FIRST DRAFT HAD B AS A SECOND COLUMN AND IT FAILED THE SAME WAY THE
`fig:rediscovery-gallery` bend angles did.** Six arcs between consecutive vertices
of a vertical column, all bending the same way, render as one thick orange stroke
with no separable arrowheads. Redrawn with $B$ as an actual hexagonal ring, which
is what a cyclic predecessor relation IS, and all six arcs and arrowheads are
individually legible. Rendered and inspected both times.

**THE EMPTY `\section{}`** is now "Why direction makes the value quadratic", and
the chapter gained two subsections under the sixteen-variant summary, so its
structure matches chapters 1 and 2. The commented-out "first phenomenon"
(the $m = 5$ edge/vertex divergence) stays deleted: the author was right that
`thm:sorensen-thomassen` and `fig:divergence` already carry it in chapter 1.

**FAILED CONJECTURES, OUT.** Two places framed a result by what it refutes. The
$m = 2$, $n = 8$ count is now stated as why the linear ceiling does not survive
the change of model, in one sentence, with no naive guess named; and the summary
intro no longer explains which status category was live in earlier drafts.

**THE FOURTH REGIME COLOUR.** `regimePartial` (`vertexpurple`) in `preamble.tex`,
and the legend of `fig:variant-tree-status` is now a 2x2 grid with it beside the
amber entry, as asked. It is applied to the four UNDIRECTED VERTEX leaves, not
just the simple one the author named: the multigraph row IS the simple value by
`sec:parallel-convention`, and the hypergraph and multihypergraph vertex rows are
exact at $m = 2$, bounded at $m = 3$ and open at $m \ge 4$, so colouring one of
the four differently would contradict the table. **The direction row is now
neutral.** It was coloured before, which forced a single status onto a pair of
leaves that no longer share one, and it was already wrong in one place: the
multigraph directed node was red while its edge child was blue.

**`tab:summary` REBUILT.** Grouped under italic `Undirected` / `Directed`
subheadings with a rule between, ragged-right X columns (the justified ones were
stretching `at $m = 2$ and $\le$` across half a line), the Model column reduced to
the model alone, and the two cells that broke mid-math or hyphenated as
`multihy-pergraphs` fixed with `\mbox` and a reword.

**WHAT I DID NOT REMOVE, and the author should confirm.** The comment
"don't talk about problems we don't handle, remove text about multigraph vertex
different version" sat on an already-commented-out subsection, which is deleted.
But `K_m^multi(n)` is listed as one of the author's own contributions in the
Contribution Statement, has three theorems in the appendix, and holds a row in
`tab:open-problems`. Those are left standing, on the reading that the instruction
was about the chapter's discussion of it and not about the result. Likewise the
general tail/head split of a directed hyperedge: the orientation subsection no
longer discusses the multiple-tail case, but `thm:dir-hyper-general-constant` is
still named in one clause, because it is a listed contribution and
`app_proofs.tex` cites `sec:orientation-models` for exactly that axis.

VERIFY: `latexmk -C` then `latexmk -pdf` exit 0, 106pp, 0 overfull/underfull, 0
undefined refs, 0 occurrences of `??`, no duplicate labels. 127 tests OK, 1
expected skip. Pages 31 to 33 and 38 rendered and inspected directly, plus the
tree figure cropped at 250dpi to confirm the four legend tints are separable in
print. No em-dashes, en-dashes or prose semicolons in the diff (every semicolon
hit is TikZ or a table cell), no banned verdict-prose phrases.

## 2026-08-28 (Opus) — the AI medal, and an audit of the uncommitted grammar pass

Two jobs: check what was sitting uncommitted in the tree, then stamp every
model-written proof with a provenance badge.

**WHAT WAS UNCOMMITTED, AND WHETHER IT WAS RIGHT.** A grammar pass (semicolons
split into sentences, "an arc", "the densest graph found") plus one real
semantic change and its new test. The semantic change is in
`_panel_cell`: a hypergraph row's `$\le$` prefix is now dropped where the
`search` series already reaches the proved bound, since a construction that
meets an upper bound makes the cell exact. **Verified rather than assumed**:
regenerating `figures/variant_table_all.tex` from the cache reproduced the
working-tree file byte for byte (452 hits, 0 computed, cache untouched), and
every de-prefixed cell was checked against the attainment conditions by hand.
At `m=6, r=3` the simple row drops the prefix at `n=7,8`, exactly where
`m-1 <= C(n-2,1)` first holds, and keeps `<=12` at `n=6`, which is the cell
where the true maximum is 11. The multihypergraph row drops it at `n=5,7`
(where `2 | (n-1)`) and also at `n=8`, where the gate returns 0 and the number
came from the timed search instead.

**ONE DEFECT FOUND IN THAT PASS.** `tab:variant-values`'s new caption said a
plain hypergraph entry is exact because "a proved construction reaches the
row's upper bound". For several cells (`m=3` multihypergraph at even `n`,
`m=6` multihypergraph at `n=8`) `attained_multihyper_edge` returns 0 and the
attaining object is a checker-verified search witness, not the attainment
theorem's own star hypertree. The caption now names both sources, and
`_panel_cell`'s docstring says the same thing.

Two other things checked and found CORRECT rather than defective: the new
`(n,m)=(2,3)` exception to Mader slackness below `n<m` (the only equality
there, since `floor(m(n-1)/2) = C(n,2)` forces `n=2`), and the new `r\ge3`
qualifier on the "neither range contains the other" claim of
`prop:hyper-vertex-lower-multi` (at `r=2` the simple gate is empty, so the
unqualified claim was false, and for every `r\ge3` the two ranges separate at
`n=r` and `n=r+1`).

**THE MEDAL.** `\aimedal` (bottom of `preamble.tex`) is a violet badge inside
the theorem head. 56 results carry it: 9 in `ch1_basecases.tex` and 47 in
`app_proofs.tex`. The scope rule is a standing convention above. The four
decisions the author was asked for, all confirmed: badge in the head rather
than a right-flushed stamp or a tinted frame (nearly every result gets one, so
it has to be light); no badge on cited classics; proof-carrying environments
only; and the two Gomory--Hu proofs excluded as he asked.

The explanation lives in the Contribution Statement, one line in the
abbreviations table, and one sentence in "How to read this appendix". The
appendix section holding the excluded proof gained a label,
`sec:mader-gomory-hu`, so those sentences can point at it.

The badge started at `\rb`'s 7pt, which rendered as an illegible violet
smudge at 400dpi. It is its own 8pt box now. **Render and crop the badge
before believing it, the way the bend angles and the sideways figures had to
be.**

VERIFY: `latexmk -C` then `latexmk -pdf` exit 0, 106pp, 0 overfull/underfull,
0 undefined refs, 0 occurrences of `??`. All 56 badges present in the
extracted PDF text. 129 tests OK, 1 expected skip. Self-check ALL CHECKS
PASSED. Pages 4, 7, 41 and 42 rendered and inspected. No em-dashes, en-dashes
or prose semicolons in the diff (every `--` hit is `Gomory--Hu`,
`path--separator` or `$u$--$v$`, every `;` is TikZ).

## 2026-08-29 (Opus) — Stijn's first-section review actioned, and the k_5 statement corrected

Twenty-odd points from the promotor's read of the front matter and the first
section of chapter 1. Most were wording. One was mathematics.

**THE ONE REAL CONTENT FIX: `thm:sorensen-thomassen` IS NOW STATED IN TWO
RANGES AND HAS NO EXCEPTIONS.** Stijn found it odd that the two exceptional
sizes deviate in OPPOSITE directions ($k_5(7) = 15$ against the formula's 14,
$k_5(12) = 27$ against its 28) and guessed the statement should be split by
range instead. Checked against `sorensen.pdf` itself rather than against the
old note: their Theorem 4 gives $f_5(n) = \floor{8n/3} - 3$ for $n \ge 6$ apart
from $n = 7, 12$, supplies $f_5(7) = 16$ and $f_5(12) = 28$ separately, and
then closes with $f_5(n) = \floor{5(n-1)/2} + 1$ throughout $6 \le n \le 13$,
which covers both. Converted to this thesis's avoiding convention that is
\[ k_5(n) = \floor{5(n-1)/2} = \ell_5(n) \ (6 \le n \le 13), \qquad
   k_5(n) = \floor{8n/3} - 4 \ (n \ge 14). \]
The two exceptions are then not exceptions at all, they are the only two points
of the small range where the large-$n$ formula misses the small-$n$ one. Every
value is unchanged, so this is a restatement and not a correction of numbers.
Swept through `ch1_basecases.tex` (statement plus a new paragraph naming where
the paper's own two forms come from), `ch3_synthesis.tex` (`tab:summary` cell
and caption), `app_proofs.tex` (`rem:threshold-convention`'s closing
paragraph), and `program/erdos915_unified.py`'s
`simple_undirected_vertex_m5`, which is now written as the same two ranges and
returns identical values at every $n$ (the four existing tests in
`tests/test_bounds.py` pin both readings and still pass unchanged).
`figures/edge_vertex_divergence.png` regenerated for its legend.

**TWO OTHER MATHEMATICAL POINTS HE RAISED, BOTH CHECKED.**
$2 \le \binom{n-2}{r-2} \iff 2 < r < n$, so `thm:hyper-vertex-m3` and the three
places that restate its hypothesis now carry the readable form. And
`prop:hyper-edge` does NOT follow from `thm:multigraph-edge`: replacing each
hyperedge by a spanning star gives a multigraph of size $(r-1)|E(\HH)|$, but
two routes may then take two star edges of one hyperedge, which Berge
disjointness forbids, so the star multigraph can carry MORE connectivity than
the hypergraph and feasibility does not transfer. A short paragraph in ch1 now
says so, because a reader will try the same reduction.

**THE `ceiling` METAPHOR IS NOW `cap`,** 31 occurrences across four files plus
`offcuts.tex`. It clashed with $\ceil{\cdot}$, which is introduced two
sentences after one of its uses. The word `ceiling` now appears exactly once in
the thesis, where the rounding brackets are defined. The three flow-gadget
labels in `fig:vertex-split` and `fig:hyper-gadget` moved the other way, from
`cap $1$` and `cap $\mu$` to `capacity`, so the figures cannot be read as the
connectivity cap. Rendered both pages to confirm the longer labels do not
collide.

**FRONT MATTER.** Cover and foreword: Promotor is Dr. Stijn Cambie, Reader is
Prof. Jan Goedgebeur (the roles were swapped and Stijn was given the wrong
title). "the connections they entail" became "size". **The exact faculty label
for Jan's role is the author's to confirm** ("Reader" was chosen over "Lezer"
or "Assessor" without a template to check against).

**WHAT I DID NOT DO, DELIBERATELY.** Stijn suggested the author work through a
few more proofs himself while revising the appendix, `thm:dir-arc-m2-exact`
(Theorem 1.6) in particular, which would drop its `\aimedal`. That is his call
to make and not something a session can assert on his behalf, so the badge
stands. **A contradiction that predates this session, RESOLVED on the author's
call the same day**: `app_proofs.tex` line 369 said the proof of
`thm:dir-arc-m2-exact` and its three supporting lemmas "are the author's own",
yet all four carry the badge and the "How to read this appendix" paragraph says
the badge is on everything except the cited classics and the Gomory--Hu double
count. The author chose the badge, so that sentence now says the lemmas and the
proof carry \aimedal{} like the rest of the appendix, and what remains the
author's own there is the program run that verified the base cases.

**REST OF THE LIST, ALL APPLIED:** the opening definition is now a
`(multi)graph` with $\mu(u,v)$ and `size` defined up front and `simple` defined
as $\mu \le 1$ (a parallel edge also joins exactly two vertices, so the old
wording did not separate the two notions), loops named as excluded, "severed"
to "separated", `fig:directed-lambda`'s "matching" cut to "corresponding" (the
thesis uses "matching" in its technical sense elsewhere), "The lower bound is a
spanning tree" to "is attained by", "while $m$ stays small" to "for $m \le 4$",
"Two shapes" to "Two constructions" plus the non-uniqueness of the linear
branch (any bidirected tree reaches $2(n-1)$, the star is one case),
`prop:hyper-edge` stated in terms of `size` with "there are simple hypergraphs
attaining it when" rather than "a simple hypergraph attains it whenever", the
bare "The proposition counts hyperedges" pointed at `\Cref{prop:hyper-edge}`
(it sat three theorems downstream of the proposition it names), and the
"route family the count uses" sentence split in two.

`fig:eight-models`' repeated hyperedge is drawn in two shades of the same red
in both multihypergraph panels, with a caption line saying they are two copies
of one hyperedge, since one colour read as a single thick line undirected and
as two different hyperedges directed. Rendered and inspected.

Theorem 1.6's proof now points at `\Cref{sec:dir-arc-m2}` (a new label on the
appendix section that holds it) rather than at the appendix as a whole, at the
author's request.

**ONE PRE-EXISTING STYLE VIOLATION FIXED IN PASSING:** an em-dash in
`ch2_machine.tex`'s complexity paragraph. **ONE FLAGGED, NOT FIXED:** the same
paragraph calls a matrix entry a "cell", which the author's own word-choice
rule rules out.

**EXPECTED NEW NOISE:** editing `simple_undirected_vertex_m5` changes the
source hash above the chapter 4 banner, so figure regeneration now prints the
`machine_values.json was written by a different version` note. The cached
values are unaffected (that helper is a cited closed form, `solve` never calls
it) and the note clears on the next `--refresh`.

VERIFY: `latexmk -pdf` exit 0, 108pp, 0 overfull/underfull, 0 undefined refs, 0
occurrences of `??`. 129 tests OK, 1 expected skip. `k_5` recomputed at
$n = 6, 7, 12, 13, 14, 15$ against the paper's own $f_5$ values minus one.
Pages 13, 14, 15, 22 and 23 rendered and inspected. No em-dashes, en-dashes or
prose semicolons in the diff (every semicolon hit is TikZ).

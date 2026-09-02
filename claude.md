# Claude working notes — Erdős Problem 915 thesis

Current state and standing rules only. The session-by-session log that used to
fill this file was condensed away on 2026-09-02; `git log` has every session's
commit with its full message, `research_notes/` keeps the self-contained
write-ups, and `program/CLAUDE.md` carries the program's own history. Do not
re-derive past reasoning from memory: `git log -p -- <file>` first.

## What this repo is

A KU Leuven master's thesis on Erdős Problem 915, the general connectivity
threshold problem, extended across sixteen graph/digraph/hypergraph variants in
two separations (edge/arc and vertex). `main.tex` is the thesis,
`chapters/app_proofs.tex` carries every proof, `program/erdos915_unified.py` is
the single-file companion program, `research_notes/` holds working notes, and
`offcuts.tex` archives every passage cut in a shortening pass with a restore
anchor.

The hand-in is `main.pdf` plus the `program/` directory, and nothing else. Every
path the thesis prints begins with `program/`.

## Current build state (2026-09-02)

- `main.pdf`: 111 pages. `latexmk -pdf -g main.tex` exits 0 with 0 overfull, 0
  underfull, 0 undefined refs, 0 LaTeX warnings, 0 occurrences of `??`.
- Recorded revision: tag `submitted-2` at `47ba4a0bd9ba`, printed in the
  computational audit. The tag is pushed and `record_revision.sh` will not move
  it, so the next recorded build is `submitted-3`.
- `program/`: one file, `erdos915_unified.py`. Core needs numpy and scipy only;
  pulp, networkx and matplotlib are optional and guarded. `geng` optional.
- Tests: `cd program && ../.venv/bin/python3 -m unittest discover -s tests`,
  currently 157 tests with 1 expected skip.
- Standard of done: rebuild the PDF clean, run the suite, run the program's
  `_run_checks` self-test, and re-verify any numeric claim against a second
  implementation (`program/scripts/` holds the independent ones).

## What is proved (load-bearing, supersedes any older note)

- **Directed multigraph arc, closed.** `L_m^dir(n) = (m-1) max(2(n-1),
  floor(n^2/4))` for every n>=2, m>=2 (`thm:dir-multi-full`), one proof, no
  parity split.
- **Directed simple arc/vertex:** leading term plus Theta_m(n) second order,
  unconditionally, via `lem:two-step-budget`. The exact value for m>=3
  (`conj:dir-arc`) is open.
- **Directed hypergraph leading constant:** (1+o(1))(m-1)n^2/(4(r-1)), all three
  orientation models, both separations.
- **Hypergraph vertex:** m=2 and m=3 for all n, r, via `lem:incidence-rank`.
- **Multigraph vertex** (`K_m(n)`, incidence convention): exact at m<=3, solved
  as a block/knapsack problem, asymptotically Theta(m^2 n) with a matching upper
  bound. The exact constant is open.
- **Undirected simple vertex:** the classical Mader / Leonard /
  Sørensen–Thomassen results. The k_5 edge-vertex divergence point is n=14,
  taken from the primary paper after the secondary source proved wrong.

## What is still open (detail in TASKS.md, not here)

1. `conj:dir-arc` exact value for m>=3. The hypothesis-(H) route was *refuted*
   by an explicit counterexample family, so it is dead, not unfinished.
2. Hypergraph vertex at m>=4. No counterexample at m=4 across eleven (n,r)
   cells, and the r=2 case of the same problem fails at m=5.
3. Multigraph vertex constant, between (3-2*sqrt(2))m^2 and 2m^2.
4. Undirected simple vertex at m>=6, the 1974 Bollobás–Erdős question. The
   triconnected/SPQR block refinement is identified and unattempted.
5. `k_m(n)` general classification, m>=6. Half a century open, out of scope.

## Standing conventions (do not relitigate without cause)

- **One self-contained program file.** Consolidate in place; never split
  `erdos915_unified.py` into a package. The thesis sells this as a
  reproducibility property.
- **No em-dashes, en-dashes or prose semicolons** anywhere in the thesis.
  Semicolons in table cells and math notation are fine, as are en-dashes in
  name compounds (Gomory–Hu), vertex pairs and page ranges.
- **British spelling** throughout.
- **The prose states facts, it does not rate them.** Say what a thing IS, never
  what it is WORTH. Out: "it is worth noting/saying/recording", "the point is",
  "what it buys is", "nothing here is deep", "that is not a defect", "earns its
  keep", "the deepest in the thesis", the intensifiers "genuinely",
  "honest(ly)", "plainly", rhetorical setups ("the first thing to notice is",
  "two things stand out") and retrospective participial cascades. KEEP every
  epistemic status fact: proved vs conjectured vs open vs search-only, what
  finished and what was abandoned, which bounds are attained. Technical uses of
  the banned intensifiers stay ("genuinely fractional" as against integral).
- **Never claim a computation finished when it did not.** A past session's worst
  mistake was three places asserting a MILP "returns INFEASIBLE" when the run
  had been abandoned unfinished.
- **The body states and draws, the appendix defines and proves.** Constructions,
  connectivity verifications, optimisation models and counting conventions all
  live in `app:proofs` however short they are; the body names the shape in words
  with a pointer. Move a passage rather than shorten it, then check `??`.
- **Mader's theorem stays proved in full.** Four printed pages, the only
  classical result reproved rather than cited, and the standing candidate
  whenever someone wants a shorter appendix. The author was asked and chose to
  keep it. Do not reopen without him.
- **One convention for vertex separation, in every model: the incidence graph**
  (`sec:incidence-convention`). A route is a path of I(H), so q parallel edges
  are q separated routes exactly as q copies of a hyperedge are, multiplicity is
  capped at m-1 in both separations, and the two multigraph vertex cells are
  problems of their own. They are NOT the underlying simple graph: K_5(4)=14
  against L_5(4)=12. Adopted 2026-09-02, replacing the collapsing convention;
  anything older saying a second copy never moves kappa is superseded.
- **The hypergraph witness is gated at the source by proved attainment**, never
  clamped downstream. `prop:hyper-edge` is an upper bound attained only in
  stated ranges, so `attained_hyper_*` returns 0 outside them. At n=6, m=6, r=3
  the bound reads 12 while the true maximum is 11.
- **A multi lower bound never sits below its simple counterpart.** Every simple
  object is the multi object with all multiplicities one, so a simple witness is
  a multi witness. `_lift_multi_above_simple` enforces it across all eight model
  pairs, the cross-model twin of `_extend_lower_bounds` within a panel.
- **Machine values are rendered, not recomputed.** `make_figures.py` with no
  flag reads the frozen record and never calls `solve`; a missing key is an
  error. `--rebuild` recomputes from scratch into a candidate, `--compare` shows
  what moved, `--promote` publishes. Provenance is recorded, never enforced: a
  hash answers "did any byte change", never "did any answer change".
- **Reversible shortening.** Anything cut in a length pass goes to `offcuts.tex`
  with a provenance header first. Never delete thesis content outright.
- **THE AI MEDAL marks what the author has NOT checked, and he curates it.**
  `\aimedal` goes on theorem/proposition/lemma/corollary/claim only, by default
  on any new proof-carrying result a model writes. It comes off only when he
  says he has worked through that proof. Never remove one on your own reasoning
  and never add one to a result he has cleared. It does NOT go on cited classics
  (Menger, Gomory–Hu, Baranyai, Mader, Leonard, Sørensen–Thomassen), on the
  Gomory–Hu double count of `sec:mader-gomory-hu`, or on definitions,
  constructions, remarks, conjectures and questions. Badges live on the
  environments, so appendix NUMBERS shift when results are added or removed: any
  numeric badge list in an old note must not be replayed against a later build.
  The rule is written out in three places that must stay in step: the
  Contribution Statement, the abbreviations table, and "How to read this
  appendix".
- **Commit and push at the end of each session.**
- **Re-verify any numeric or bibliographic claim inherited from an older note.**
  Several "settled" facts turned out to rest on a convention mismatch that
  flipped a value by one or by a sign. `git log --grep=convention`.

## Gotchas that each cost a session

- **Use `.venv/bin/python3`, never bare `python3`.** The system interpreter has
  no matplotlib, and the import guard sets every plotting name to None together,
  so a figure call runs most of its length and fails late inside legend
  construction with a hundred-line traceback that looks like a code defect.
- **`grep -c` returns blank in this shell even on matching input.** Use
  `grep ... | wc -l`.
- **`??` is the real build gate, not the log.** Cleveref's fallback prints `??`
  with no warning and `latexmk` exits 0. Check
  `pdftotext main.pdf - | grep '??' | wc -l`.
- **`latexmk -C` then a clean rebuild** fixes the recurring exit 12 with null
  bytes in `main.aux` and mass undefined refs. It is stale aux state, never the
  source.
- **`record_revision.sh` needs `latexmk -pdf -g` afterwards.** `preamble.tex`
  reads the generated file with `\InputIfFileExists`, so a build made while it
  was absent recorded a lookup that FAILED, not a file to watch. Without `-g`
  latexmk returns exit 0 in 0.06s and leaves a PDF still saying "not recorded".
- **Render a figure before believing it.** Option names lie (`figuresright` is
  already the default; only `figuresleft` flips a sideways float), a sideways
  figure can overflow the page with no overfull warning, `_save()` runs a second
  rect-less `tight_layout` that discards any reservation the caller made (pass
  `tight=False`), and a bend spread tuned for two arcs collapses into one thick
  stroke at four.

## Known loose ends, flagged not fixed

- Git stamps every commit in this repository as `chief@mba.local`, because
  neither `user.name` nor `user.email` is set and git falls back to
  username@hostname. Setting them fixes future commits only. Rewriting the past
  is not an option: `main.pdf` prints `47ba4a0bd9ba` and the tag `submitted-2`
  in its computational audit, and a rewrite changes that hash.
- `program/CLAUDE.md` is development history and sits inside `program/`, which
  is the hand-in directory. `program/README.md` now says it is not part of the
  submission, but a careless copy of the directory still ships it.

## Recent sessions

One line each. `git log` has the full message for every one of them.

- **2026-09-03.** A full-repository consistency review: six defects in the PDF,
  none mathematical. `sec:incidence-convention` was a bare `\label` mid-paragraph
  resolving to section 1.3 with a figure-caption anchor, and is now subsection
  1.3.1; the `m=6, n=6, r=3` hypergraph cell was described three ways in one
  subsection and now reads the same in caption, legend and table; one badged
  theorem had an unbadged proof heading; ten name compounds took en dashes. Then
  the stale internal notes were cleared, `research_notes/scripts/` having moved
  to `program/scripts/` when the hand-in was reduced.
- **2026-09-02, second session.** An external code audit: six defects, all
  reproduced, two of its claims narrower than stated. One `_require_integer`
  primitive now guards every integer input, after finding two laundering paths
  the audit missed (a simple graph's `min(mu + 1.9, 1)` hands `_assign` a clean
  integer, and `frozenset([0, 1, True])` silently drops a member). The machine
  cache became render vs rebuild. `record_revision.sh` stopped calling an
  untracked tree clean and stopped moving tags. A from-scratch rebuild of all
  529 values changed no exact value and moved one plotted point, upward. Fixed
  the multi-below-simple inversion in the m=6 hypergraph grid. Tests 135 -> 157.
- **2026-09-02.** The incidence convention adopted in every model, `K_m(n)` and
  `K_m^dir(n)` became problems of their own, and the hand-in was reduced to
  `main.pdf` plus `program/`.
- **2026-09-01.** An appendix review: five local errors, and two inductions that
  were being proved twice collapsed into `sec:two-step-budget`. Then an external
  review's seven findings, five actioned in the body.
- **2026-08-31.** Four appendix proof replacements checked line by line, each
  trading a cited heavyweight for a self-contained argument.
- **2026-08-29.** Stijn's front-matter review, and `thm:sorensen-thomassen`
  restated in two ranges so it has no exceptions. Then the author curated the
  badges.
- **2026-08-26 to 08-28.** The fourth model (twelve variants -> sixteen), the
  variant grids and their value table, the tone pass, the move of constructions
  into the appendix, and the AI medal.

## Revision policy agreed on 7 September 2026 (supersedes older status notes)

Unchecked AI arguments are labelled `Conjecture` with `with proof` and `[AI]` in the heading. Their arguments are `Proposed proof`. Checked deductions relying on unresolved conjectures are labelled likewise with `[conditional]` and `Conditional proof`. Preserve the author's existing verification distinctions. General directed multigraph and hypergraph bounds are not established just because their proposed proofs are included. Match this status in summaries, tables, plots and program results.

Hypergraph discovery is random greedy growth with shuffled restarts. The user requested accurate documentation of this implementation, not a tabu implementation. Chapter 3 explains every model family's edge and vertex status in detail. The full Mader proof stays in the appendix.

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
path the thesis prints is relative to the repository root, so it begins with
`program/`, unless a base directory is named where the path is given (the
equal-budget records are the only case).

## Current build state (2026-09-07, after the corrective pass)

- `main.pdf`: 126 pages. `latexmk -pdf -g main.tex` exits 0 with 0 overfull, 0
  underfull, 0 undefined refs, 0 LaTeX warnings and 0 occurrences of `??`.
  The underfull hbox of badness 1168 that this block used to record went away
  with the `BercziEtAl24` bibliography entry, which only `offcuts.tex` cites
  now, so `unsrt` no longer prints it in `main.bbl`. Do NOT read that as proof
  that a clean count is safe to assume: an earlier version of this block claimed
  0 underfull and 0 LaTeX warnings while the log held 4 and 1, because a bare
  grep silently matched nothing. See the locale gotcha below, recount with
  `LC_ALL=C grep -a` before ever restating these numbers, and prove the grep
  read the file with a pattern you know is present (`Output written` works).
- Recorded revision: the tags run to `submitted-11`, printed in the
  computational audit. `record_revision.sh` will not move an existing tag, so
  each recorded build takes the next free name. An earlier version of this line
  still named `submitted-3` after three further builds had been recorded, so
  read the tag off `git tag` rather than off this file.
- **`./check_consistency.sh` is the pre-hand-in gate.** Run it before any
  recorded build. It catches the three defects `latexmk` exits 0 on: an
  `\aimedal` edited on a Chapter 1 statement but not its appendix proof (or the
  reverse), `??` in the built PDF, and a lowercase `\crefname` (see the badge
  and cleveref entries below).
- `program/`: one file, `erdos915_unified.py`. Core needs numpy and scipy only;
  pulp, networkx and matplotlib are optional and guarded. `geng` optional.
- Tests: `cd program && ../.venv/bin/python3 -m unittest discover -s tests`,
  currently 207 tests with 1 expected skip.
- **The hand-in is built, never copied: `./build_handin.sh`** wraps the
  `git archive` bundle so the local `.DS_Store`, `__pycache__`,
  `_erdos_fast.so` and the fourteen uncited scratch logs in `program/logs/`
  cannot ride along. Its shape matches the audit's instructions, the venv going
  at the bundle root so `../.venv/bin/python3` resolves from `program/`. It runs
  publish.sh's working-notes guard over the finished bundle and refuses on a
  dirty tree, and `handin/` is gitignored, so it is a build product with no
  independent existence. **Rebuild it after every recorded build**, or its
  `main.pdf` silently lags `HEAD`.
- **`.gitattributes` is what keeps `program/CLAUDE.md` out of both
  distributions.** `git archive` honours `export-ignore`, and both the hand-in
  and `publish.sh` go through `git archive`, so one line covers both. Before
  2026-09-07 only publish.sh stripped it, by an explicit `rm -f`, and the
  hand-in path did not: 392 lines of program working notes shipped to the
  examiners in a bundle whose own manifest did not list them. That `rm -f` and
  the guard stay as a second line of defence.
- Standard of done: run `./check_consistency.sh`, rebuild the PDF clean, run the
  suite, run the program's `_run_checks` self-test, and re-verify any numeric
  claim against a second implementation (`program/scripts/` holds the
  independent ones).

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
  appendix". All three say the badge sits on BOTH the Chapter 1 statement
  and the Appendix A proof, so editing one end alone makes the thesis vouch
  for a result in one place and disclaim it in the other. This happened to
  five results and was caught only by a full review; `./check_consistency.sh`
  now gates it. On 2026-09-03 the author cleared `thm:dir-arc-m2-exact`,
  `thm:dir-vertex-m2-exact`, `prop:hyper-edge`, `thm:hyper-vertex-m2` and
  `thm:hyper-vertex-m3`, so those five are unbadged at both ends. 41 badges.
- **Cleveref names are capitalised in BOTH slots** for the theorem family, as
  they already were for figure, table, section, chapter and part. Every
  reference goes through `\Cref`, and a mixed-type group such as
  `\Cref{prop:a,thm:b}` capitalises only its FIRST group, taking the lowercase
  `\crefname` for the rest. With lowercase names that printed "Proposition A.37
  and theorem 1.11" at five sites, one of them in the Contribution Statement.
  Do not restore lowercase forms without first adding a `\cref` use that needs
  them, and there is none.
- **Two remotes, and main is the private one.** `main` tracks EVERYTHING: the
  LaTeX sources, the figures, the research notes and the working notes including
  this file. It pushes to `backup`, the private repository
  `louisvandenbruwaene/thesis-private`. `git config remote.pushDefault` is set
  to `backup`, so a bare `git push` can never reach the public repository.
  The public repository `louisvandenbruwaene/thesis` is a GENERATED SNAPSHOT
  carrying `main.pdf`, `program/` and `README.md` only, refreshed by
  `./publish.sh` and by nothing else. Privacy lives in that script, not in
  `.gitignore`: a file is public because publish.sh copies it. Whole directories
  are copied, so anything private inside one (`program/CLAUDE.md` was the first
  case, and it did leak once) must be named for removal in the script, which
  also refuses to push if a working-notes file reaches the snapshot. After a
  recorded build, run `./publish.sh` to put the new PDF on the public link.
  Everything remains in the public repository's OLD history from before the
  reduction, and rewriting that is ruled out because `main.pdf` prints commit
  hashes.
- **Commit and push at the end of each session.**
- **Re-verify any numeric or bibliographic claim inherited from an older note.**
  Several "settled" facts turned out to rest on a convention mismatch that
  flipped a value by one or by a sign. `git log --grep=convention`.

## Gotchas that each cost a session

- **Use `.venv/bin/python3`, never bare `python3`.** The system interpreter has
  no matplotlib, and the import guard sets every plotting name to None together,
  so a figure call runs most of its length and fails late inside legend
  construction with a hundred-line traceback that looks like a code defect.
- **`main.log` is not valid UTF-8, so grep over it can silently match nothing.**
  It carries an invalid continuation byte `0xf3` around offset 57167. On a
  matching pattern a bare `grep` returned zero hits for `Warning`, `Underfull`
  and every other pattern in one shell, while `LC_ALL=C grep -a` returned the
  true counts 1 and 4 in the same shell on the same file. There is no error and
  no `Binary file ... matches` line, only an empty result that reads exactly
  like a clean build. Whether a bare grep fails depends on the active locale, so
  do not depend on one: **always `LC_ALL=C grep -a` on any `.log` in this repo**,
  and treat an empty result as unproven until rerun that way. A previous version
  of this entry blamed `grep -c` and prescribed `grep ... | wc -l`; that is the
  wrong cause and the workaround does not help, because the pipe cannot recover
  matches grep never made. This trap has now produced a false "0 warnings"
  claim in a review.
- **`??` is the real build gate, not the log.** Cleveref's fallback prints `??`
  with no warning and `latexmk` exits 0. Check
  `pdftotext main.pdf - | LC_ALL=C grep -a '??' | wc -l`. `pdftotext` output has
  been clean UTF-8 so far, so this one has not misfired, but use the same
  invocation everywhere rather than keeping two habits.
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

- Commits up to and including `0152e21` are stamped `chief@mba.local`, because
  neither `user.name` nor `user.email` was set and git fell back to
  username@hostname. Both are set as of 2026-09-03, so `b4547a7` onward carry
  `Louis Vandenbruwaene <louis@vandenbruwaene.eu>`. Rewriting the past is not an
  option: `main.pdf` prints a commit hash and a tag in its computational audit,
  and a rewrite changes that hash.

## Recent sessions

One line each. `git log` has the full message for every one of them.

- **2026-09-07 (third pass).** Structural checks rather than greps, and the two
  that paid. `thm:dir-multi-m2` was headed "with proof" but had NO proof block:
  its argument sat inside the statement body, so the promised block never
  existed. `check_consistency.sh` only compared headings that were present, so
  it passed. It now also requires that a "with proof" conjecture HAVE a proof,
  named-target or inline, with the right status word, verified by deleting the
  block again and watching the gate fail. **`offcuts.tex` had stopped building
  entirely** (exit 12), unnoticed because its last log predated the overhaul:
  three transcript `\lstinputlisting` paths still said `figures/` after the logs
  moved to `program/logs/`, and two `\includegraphics` pointed at the combined
  twelve-variant PNGs that the `_graphs`/`_hypergraphs` split superseded when
  the fourth model took the count to sixteen. Those two image slots now carry a
  note instead of being repointed at a sixteen-variant replacement, since the
  archived captions say twelve. It builds again, 136 pages. Its 66 `??` over 17
  labels are EXPECTED and now documented in its header: `xr` reads `main.aux`,
  so a surviving label resolves and a label whose material was itself cut cannot.
  **Do not chase `??` in offcuts.pdf the way you must in main.pdf.**
  Verified clean by script: 41 conjectures, 33 `[AI]` and 8 `[conditional]`,
  none both, every conditional leaning on an unchecked result directly or
  transitively; no unmarked result's proof cites a conjecture; bibliography
  prints in appearance order under `unsrt` with no missing or dangling keys;
  every referenced file path exists; no duplicate labels and no dangling refs in
  the thesis; British spelling consistent once TikZ `color=`/`anchor=center`
  keys are excluded. The equal-budget numbers reproduce from `report.json` to
  the digit (74/128, 54 short, 68 all-seeds, 57657.7 s selected vs 58690.8 s
  including discards, 110 in all three seeds at n=12 m=6 against 180).
  Also `program/README.md`'s layout block was missing `requirements*.txt` and
  understated `data/`, and "programme of conjectures" collided with the thesis's
  own word for the code.

- **2026-09-07 (second pass).** A consistency sweep of the conjecture-status
  overhaul, hunting prose that the demotion missed. Nine sites where running
  text still asserted a conjectural result: `ch2` had `cor:mstar-integral`
  "proves" the integrality that carries `L_m^dir(n) = (m-1)M^*(n)`, with the
  paragraph deriving the identity unconditionally, and the appendix had "the
  upper-bound side closes completely" at hypergraph `m=3`,
  `thm:dir-arc-linear-error` "now proves" the bipartite pattern,
  `prop:hyper-edge` "bounds every simple hypergraph", "the true maximum is one
  below the bound of 12", "the count `lem:reach-skeleton` proves", "the rank
  bound now yields `thm:hyper-vertex-m3`", and a "proves" inside the
  `prop:dir-hyper-first` statement. `make_figures.py`'s bouquet docstring
  carried the SAME defect the 09-07 review fixed in the prose: it said the
  thickened tree "is optimal" at `m <= 4`, where only `m <= 2` is settled, plus
  two proof-verbs on `thm:multi-vertex-blocks` and `thm:clique-chain-vertex`.
  The **popularising summary** was the worst of it: untouched since 09-06, so it
  still sold five conjectures as achievements, including "settles the exact
  answer completely" and "proves the count outright" for the directed multigraph.
  Rewritten to name the status convention in lay terms and to credit Huang and
  Lyu for the asymptotic that does not depend on an unchecked proof. Faculty cap
  is 3,500 characters, now at 3,449, still one page. Also removed ten prose
  semicolons the overhaul introduced, nine of them in `ch3`'s new status table.
  **Two invariants verified by script and clean:** no unmarked result's proof,
  named-target or inline, cites a conjecture, so the dependency closure the
  Contribution Statement promises actually holds; and `make_figures.py`'s
  `conjectural` predicate agrees with `ch3`'s new subsections variant by
  variant. Build 124 -> 126 pages, 0 warnings, 0 `??`, tests green.

- **2026-09-07.** A full independent review of the built PDF, then a corrective
  pass on what it found. No new proof gap: the mathematics was re-derived end to
  end and every load-bearing computation reproduced from scratch, with a
  separate max-flow and `geng` and no import of `program/`. Reproduced exactly:
  all 43 cells of `tab:multi-vertex-blocks`, `g_6(9) = 54` attained by graph6
  `H??EDz}` at 14 edges over 191826 candidates, no 2-connected block on nine or
  fewer vertices beating the rate `m/2` for any `m <= 8`, the 2-connected counts
  468 / 7123 / 194066, and the four equal-budget totals (128 cases, 74 / 68 / 8,
  57657.7 s and 58690.8 s) to the digit. Four defects fixed. The PACKAGING one
  is the one that mattered: see the `.gitattributes` entry above. The
  MATHEMATICAL one was a wording defect at two sites, ch1 and `app_proofs`
  around `cor:multi-vertex-m3`, both saying the multigraph vertex problem
  "parts company with its edge counterpart at `m = 5`", which asserts
  `K_4(n) = L_4(n)` at every `n` while `tab:summary` and `tab:open-problems`
  both list that variant open from `m >= 4`. The evidence is only
  `g_4(b) = 3(b-1)` for `b <= 8`, and the easy bound is far too weak to close
  it: every edge of a 2-connected block has `kappa >= 2`, so `W_4(B) <= 2|E|`,
  a factor 4/3 above `3(b-1)`. Both now read "the first threshold at which the
  two values are known to differ is `m = 5`" and say `m = 4` is open. Also:
  three prose semicolons removed; ch2's blanket "every file path is relative to
  the repository" qualified, since the equal-budget records name their own base
  directory; `const:clique-core`'s `r = n-m` renamed to `p`, `r` being reserved
  thesis-wide for hyperedge size; `H_{m,n}` (undirected hub-and-spokes GRAPH,
  `floor(m(n-1)/2)` edges) disambiguated from `H_m(n)` (directed hub ARC COUNT,
  `m(n-1)`) where both are in play, and `thm:clique-chain-vertex` now says its
  `r` is a clique order. Left alone as deliberate: `lem:near-regular`'s generic
  `r`, and a handful of banned-list phrases the author may still want out.

- **2026-09-04.** A full read-through of all four chapter sources with every
  numeric claim re-derived. Four defects, one of them a bound the thesis
  understated against its own table. `cor:dir-multi-incidence` said
  `M(n) = floor(n^2/4)` for `n >= 4`, false at 4, 5 and 6, since the branches
  only tie at 7. Three places still described the m=2 directed proof as the
  vertex-deletion induction it no longer is: `ch2_machine.tex` said
  `thm:dir-vertex-m2-exact` "depends on finite checks through n=7", against the
  appendix's own "no result in this thesis rests on a machine run"; the Short
  Summary said "a long induction"; and `directed_arc_m2`'s docstring said
  "induction on n". Fourth, `theta_bouquet_lower_bound` built the `K_m(n)`
  curve from theta blocks alone, which the theta family caps at `b <= m+1`, so
  the grid and `tab:variant-values` printed `K_6(8) >= 45` where the swept
  `g_6(8) = 47` is attained by a block on eight vertices that is not a theta
  (graph6 `G?AFvw`). It is now `block_bouquet_lower_bound`, reading the
  swept `g_m(b)` for `b <= 8` and falling back to the theta and thickened
  `K_{s,t}` families beyond, and the pinning test's literal was recording that
  truncation rather than the sweep it named. Independent re-verification, no
  import of the program: the whole of `tab:multi-vertex-blocks` (43 cells, own
  max-flow plus a geng sweep), the 125970-candidate `m=6, n=6, r=3` hypergraph
  enumeration, `K_5(4)=14` and `K_5(5)=19` by direct multigraph exhaustion, and
  `ell_3^dir` and `k_3^dir` at n=3,4. Checking the appendix prose against
  `logs/multi_vertex_blocks_log.txt` then found two more: the maximiser is
  NOT unique at m=8, b=7 (six of them, as the log says), and the m=6, b=7
  cell HAS a complete bipartite tie (`K_{2,5}`, again as the log says),
  against prose claiming uniqueness across four cells and none across six.
  Both were contradicted by the very log the passage tells the reader to
  consult. Also re-verified: geng -C 9 gives 194066, `h_4(b) = 2(b-1)` with
  the hub-and-spokes the unique optimum at every b from 4 to 8, and the rate
  m/2 attained and never exceeded for m <= 8.
  A third pass, prompted by the author, found three more and one
  non-finding. `fig:gomory-hu-dist` carried two wrong tree-distance
  comments (a-c is a TREE edge, distance 1 not 2; e-c is 2 not 3), source
  only, the drawn tree itself verified a genuine Gomory-Hu tree. The audit
  said the render command "never starts a search", true of
  `machine_values.json` but false of the command. A FIRST ATTEMPT AT THIS FIX
  WAS ALSO WRONG and an external review caught it, so get the mechanism right:
  the two enumeration caches are EXHAUSTIVE and currently HIT, so they are
  neither timed nor recomputed. Only `surface_cache.json` both misses (it
  carries `d58345...` against the program's `cbcb38...`) and is filled by timed
  `solve(exhaustive=False, max_seconds=20)` calls. The gallery and the
  annealing-against-tabu comparison are not fingerprint-governed at all and rerun
  under wall-clock budgets EVERY invocation. All of it feeds offcut-only outputs,
  so nothing printed moved. A plain run did rewrite committed surface values
  downward (`multi_directed_vertex/9/5`: 64 -> 50), observed in session but not
  preserved in any git object; the earlier note blamed CPU contention, which was
  never tested and is only one candidate, the stale cache predating a program
  change being another.
  **CORRECTED 2026-09-07: a bare `make_figures.py` is safe.** The render/rebuild
  split made `main()` draw from the frozen record and never start a search, which
  is what both the thesis audit instructions and the public README tell a reader
  to run. `--grids-only` and `--tables-only` are narrower reruns, and only
  `--rebuild` computes. The old warning here predated that split. The symbols table
  listed `h_m(b)` but not `g_m(b)` or `W_m(G_0)`; adding them took the thesis
  from 111 to 112 pages, the symbols list now owning a page of its own.
  `g_6(9) = 54` is now IN `_BLOCK_SWEEP`, so the m=6 curve reads 54 at n=9 and
  101 at n=16. The rows of that table are deliberately ragged: the appendix
  prints the b<=8 square, and this one extra cell has its own script
  (`scripts/multi_vertex_blocks_b9.py`) and transcript, cited where it is
  stated. The curve is still short from n=10 on, since g_6(10) is unknown. An
  exhaustive
  9-vertex search settles `g_6(9) = 54` EXACTLY, attained by graph6 `H??EDz}`
  (14 edges, kappa^max 5), so `K_6(9) = 54` against the curve's 52. Exhaustive
  over all 191826 two-connected graphs on 9 vertices with at least 14 edges,
  which is no restriction: kappa >= 2 on every edge of a 2-connected graph caps
  `W_6` at `4|E|`, so 13 edges cannot reach 53. `tab:multi-vertex-blocks`
  already warns the table does not extrapolate, and the curve is labelled a
  lower bound, so both stay honest. Extending the sweep to b=9 would tighten
  it. `program/CLAUDE.md` riding into the hand-in was flagged here and is fixed
  as of 2026-09-07 by `.gitattributes`.

- **2026-09-03 (second pass).** A pre-hand-in review, six defects, none
  mathematical. The AI badge had come off five Chapter 1 statements but not
  their appendix proofs; the audit printed a revision nine commits stale; the
  popularising summary predated the incidence row and its PDF predated its own
  tex; `cor:dir-multi-n7` printed as "Corollary A.41 ( [AI])"; five mixed-type
  `\Cref` groups printed lowercase names; the working notes were being served
  publicly. All fixed, `check_consistency.sh` added as the gate, `handin/` added
  as a git-archive bundle. Independent brute force (own Edmonds-Karp, no import
  of the program) reconfirmed `thm:dir-arc-m2-exact` to n=5,
  `thm:dir-vertex-m2-exact` to n=5, `thm:dir-multi-full` to (4,4), and
  K_5(4)=14 against L_5(4)=12.

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

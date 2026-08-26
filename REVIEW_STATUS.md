# Review status, checked against `3b353ea` on 2026-08-26

Two external review batches were actioned. This file records what is verified
closed, what is still open, and the one thing I deliberately did not do.

Context: the repo moved a long way between the reviews and this check. The
chapters were rewritten, a fourth model was promoted so the thesis now runs on
**sixteen** variants rather than twelve, and `claude.md` was condensed from a
3770-line session log to a 219-line summary. Every fix below survived that,
sometimes reworded, and two were extended by the rewrite rather than merely kept.

## Batch 1 — all closed

| # | Finding | State at `3b353ea` |
|---|---|---|
| 1 | MILP missing the cut-side constraints | Closed. `ch2_machine.tex:463` carries `x^{st}_s = 1, x^{st}_t = 0`, and the two-step `min` linearisation is written out. |
| 2 | Hypergraph gadget drew the wrong bottleneck | Closed, and **extended**: the split gate `e^- → e^+` is drawn, and its capacity is now `μ` rather than `1`, because the fourth model makes multi-hypergraphs a first-class variant. |
| 3 | Summary table's directed simple vertex cell | Closed. |
| 4 | Augmented-bipartite case split | Closed. |
| 5 | "The extremisers are doubled trees" overclaim | Closed. |
| 6 | `solve` code card did not match the dispatch | Closed. |
| — | `c_m` and `h_m(b)` in the symbols table, SPQR `Q` component, Metropolis / Kirkpatrick-Gelatt-Vecchi / Glover / Hanifehnezhad-Dolati citations, `ChekuriXu17` and `DewarPikeProos18` now behind real claims, appendix grouped into four signposted parts | All present. |
| — | `record_revision.sh`, `program/requirements-lock.txt`, PDF metadata | All present. |

## Batch 2 — all closed

| # | Finding | State at `3b353ea` |
|---|---|---|
| 1 | `solve()` optimised multiplicity for the multigraph **vertex** variants | Closed and re-verified by running it: at `n=3, m=3` it now returns 3 undirected and 6 directed, in both exhaustive and discovery mode, was 6 and 12. `MultigraphVertexObjective` (6 tests) is in `tests/test_solve.py`. |
| 2 | The `m=6` grid plotted a hypergraph witness that cannot exist | Closed. `attained_hyper_edge` / `attained_hyper_vertex` gate the witness by proved attainment, and the rewrite extended the same pattern to the new fourth model. Both grids were regenerated in `2829e47`. |
| 3 | Short summary misreported what the search rediscovered | Closed. |
| 4 | `k_5(n)` exceptions dropped in prominent summaries | Closed. `ch1_basecases.tex:457` states `k_5(7) = 15` and `k_5(12) = 27`; `ch4_synthesis.tex:116` and the summary table carry `n ≠ 7, 12`. |
| 5 | "All computational claims rerun from one program" | Closed. Both standalone block sweeps are named where their numbers are used and in the audit section. Both READMEs corrected. |
| 6 | `Hypergraph` did not enforce `r`-uniformity | Closed. `r` is an optional constructor argument, enforced on every add when given, and the thesis says uniformity is a generator property rather than a container one. |
| 7 | False reason for equal search-node counts | Closed. The caption now says the counts coincide as a computed fact. |
| 8 | Stale PuLP skip on a branch that no longer needs it | Closed. The only remaining skip is `test_n5_known_count`, gated behind `RUN_SLOW_ENUM=1`, which is a deliberate slow-test gate. |

## Still open

**1. The hypergraph "proved" curve means two different things at adjacent points.**
Not a wrong value, but a presentational inconsistency worth one pass.

`prop:hyper-edge` gives a proved *upper bound* for every `r`-uniform hypergraph.
`_reconcile_panel` invariant 1 then caps every `proved=` curve down to any
machine-exact value at that `n`. So where exhaustion finished inside its budget
the plotted line is the true maximum, and where it did not the line is the looser
bound. At `m = 6, r = 3` that gives a kink: at `n = 5` the curve is clamped to the
true 8, at `n = 6` it stays at 12 while the true maximum is 11 (verified two ways:
all 125970 twelve-hyperedge simple 3-uniform hypergraphs on six vertices are
infeasible, and the program's own branch and bound returns 11 exactly).

Both readings are correct *as an upper bound*, so nothing published is false. But
one line carrying two meanings is the kind of thing this thesis otherwise refuses
to do. Fixing it properly means letting a panel carry an upper-bound curve that is
exempt from the exact-value clamp, which touches every panel in
`gather_variant_grid`, so it was recorded rather than rushed.

Files: `program/make_figures.py`, `_reconcile_panel` and the two hypergraph panels.

**2. The sixteen-variant rewrite has not been audited.**
Commits `2829e47` and `3b353ea` promoted the multi-hypergraph to a first-class
variant, rewrote the chapters, and relaxed Mader's hypothesis. That work postdates
both review batches and neither review saw it. The build is clean (0 overfull,
0 undefined, 102 pages) and the suite is green, but neither of those would catch
the class of problem both batches actually found: prose that drifts from what the
code does. Worth pointing a fresh reviewer at specifically:

- the count itself, since `ch1`'s old "three models, two directions, two
  separations" explanation was written to justify **twelve** and the arithmetic
  has changed;
- the multi-hypergraph rows of `tab:summary`, which are new;
- the `cap μ` gate, which generalises a construction whose correctness argument
  in `thm:menger-hyper` was written for `cap 1`.

**3. `claude.md` no longer records the two review batches.**
The condensation in `09ef22e` was deliberate and the file is much better for it,
but the reasoning behind several current choices now lives only in the git log.
The two entries worth restoring in one or two lines each are why the multigraph
vertex variants reduce to the simple problem, and why the hypergraph witness is
gated by attainment rather than clamped downstream.

## Not done, by choice

Promoting one or two proofs out of the appendix into a body chapter. That reverses
a deliberate decision (`c1c5390`, "Move every proof to the appendix"), so it stays
the author's call. The compatible half was done instead: the appendix is grouped
into four signposted parts that appear in the contents, with a reading guide that
names the flagship arguments.

The `ErdosProblems` bib entry still lists Pál Erdős as the author of a website he
cannot have written (erdosproblems.com is Thomas F. Bloom's). Flagged in the first
batch, left alone because it could not be verified from here and neither review
raised it.

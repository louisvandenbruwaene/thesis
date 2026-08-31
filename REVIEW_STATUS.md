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
| — | `c_m` and `h_m(b)` in the symbols table, Metropolis / Kirkpatrick-Gelatt-Vecchi / Glover citations, `ChekuriXu17` and `DewarPikeProos18` now behind real claims, appendix grouped into four signposted parts | All present. |
| — | SPQR `Q` component in the symbols table, Hanifehnezhad-Dolati citation | Both retired on 2026-08-31, when the triconnected decomposition and the hypergraph Gomory-Hu theorem left the appendix. |
| — | `record_revision.sh`, `program/requirements-lock.txt`, PDF metadata | All present. |

## Batch 2 — all closed

| # | Finding | State at `3b353ea` |
|---|---|---|
| 1 | `solve()` optimised multiplicity for the multigraph **vertex** variants | Closed and re-verified by running it: at `n=3, m=3` it now returns 3 undirected and 6 directed, in both exhaustive and discovery mode, was 6 and 12. `MultigraphVertexObjective` (6 tests) is in `tests/test_solve.py`. |
| 2 | The `m=6` grid plotted a hypergraph witness that cannot exist | Closed. `attained_hyper_edge` / `attained_hyper_vertex` gate the witness by proved attainment, and the rewrite extended the same pattern to the new fourth model. Both grids were regenerated in `2829e47`. |
| 3 | Short summary misreported what the search rediscovered | Closed. |
| 4 | `k_5(n)` exceptions dropped in prominent summaries | Closed. `ch1_basecases.tex:457` states `k_5(7) = 15` and `k_5(12) = 27`; `ch3_synthesis.tex:116` and the summary table carry `n ≠ 7, 12`. |
| 5 | "All computational claims rerun from one program" | Closed. Both standalone block sweeps are named where their numbers are used and in the audit section. Both READMEs corrected. |
| 6 | `Hypergraph` did not enforce `r`-uniformity | Closed. `r` is an optional constructor argument, enforced on every add when given, and the thesis says uniformity is a generator property rather than a container one. |
| 7 | False reason for equal search-node counts | Closed. The caption now says the counts coincide as a computed fact. |
| 8 | Stale PuLP skip on a branch that no longer needs it | Closed. The only remaining skip is `test_n5_known_count`, gated behind `RUN_SLOW_ENUM=1`, which is a deliberate slow-test gate. |

## Still open

**1. CLOSED 2026-08-26. The hypergraph "proved" curve meant two different
things at adjacent points.**

`prop:hyper-edge` gives a proved *upper bound*. `_reconcile_panel` invariant 1
capped every `proved=` curve down to any machine-exact value at that `n`, which
is right for a curve carrying a closed-form *value* (Mader's floor overshoots at
`n < m`, where the complete graph is the answer) and wrong for one carrying a
bound. The line then meant the true maximum wherever exhaustion happened to
finish inside its four-second budget and the looser bound wherever it did not,
so the switch point was set by the budget rather than by any mathematics.

Measured before fixing, the clamp fired at **one plotted point in the whole
thesis**: `m = 6`, `r = 3`, simple hypergraph, undirected edge, `n = 5`, pulled
from the bound's 10 down to the exact 8. At `m = 3` the bound is tight wherever
exhaustion reached, so nothing was capped, and at `m = 6` the two vertex panels
take the `open` branch (`hyper_vert_proved = (m <= 3)`) and carry no `proved=`
curve at all. This note previously estimated the fix as touching every panel in
`gather_variant_grid`. That was wrong: twelve panels keep the clamp untouched.

Fixed by a per-panel `clamp_formula=False`, set on the four hypergraph panels
(`make_figures.py`, panels 9, 10, 13, 14) and honoured in `_reconcile_panel`.
The search circles are still clamped, since a witness really cannot beat a
proved optimum. Un-clamping only ever raises a curve, and an exact value can
never exceed a proved bound for the model being enumerated, so no square can
rise above its curve as a result. Verified by sweeping all sixteen panels at
both `m`: no exact square above any curve, no search circle above any exact
value.

The panel now reads as one claim. The line is the bound, the markers are what
has been reached, and the gaps are visible: at `m = 6` the exact square at
`n = 5` is 8 against the curve's 10, and at `n = 6` the curve reads 12 where the
true maximum is 11. `plot_variant_grid` labels the blue curve "proved upper
bound" in a grid whose every blue curve is one, decided per figure rather than
per panel, so no panel carries a mark its neighbours lack. Both hypergraph
captions in `ch2_machine.tex` say the same in words, and both sideways pages
were re-rendered to confirm the longer captions still fit.

**2. AUDITED 2026-08-27. The sixteen-variant rewrite.**

All three things this note asked a fresh reviewer to look at were checked.

*The count.* Clean. `ch1` reads "three toggles create a lattice of eight models"
and separation is applied afterwards, so eight times two is sixteen with no
leftover twelve-era arithmetic anywhere.

*The multi-hypergraph rows of `tab:summary`.* One defect. The vertex cell claimed
repeats close "cases the simple model misses at `m=3`". True, and verified
numerically at eight parameter points, but no theorem in the thesis stated it:
`thm:hyper-vertex-m3` and `prop:hyper-vertex-lower` both give attainment by a
*simple* hypergraph when `m-1 <= C(n-2, r-2)`, and nothing covered the multi
lower bound. Fixed by adding `prop:hyper-vertex-lower-multi`: the star hypertree
at multiplicity `m-1` has `kappa^max = m-1` exactly and attains
`(m-1)(n-1)/(r-1)` whenever `(r-1) | (n-1)`, which at `m=3` meets the upper bound.
Stated in `ch1` beside the theorem and cited from the table's notes.

*The `cap mu` gate.* One defect, in the opposite direction to the one predicted
here. This note worried the `cap mu` gate generalised a construction proved for
`cap 1`. In fact `thm:menger-hyper` and the program agreed at capacity one
(`cap[gate_in, gate_out] = 1`, one gate per *copy*), and it was the two gadget
figures and the `ch2` prose that described a capacity-`mu` gate nothing built.
Resolved on the author's call by moving the code to the text rather than the
text to the code: `_hyper_capacity_matrix` now gives each *distinct* hyperedge
one gate of capacity `mu`, and `thm:menger-hyper` is restated and reproved for
multiplicities.

Merging cannot change a measured value: `q` copies at capacity one are `q`
parallel arcs between the same two nodes, and replacing parallel arcs by one arc
of their summed capacity leaves every cut alone, hence the min cut and the max
flow. Checked rather than asserted, over 149532 pairwise measurements with 1670
instances carrying real duplicates and both directed storage spellings, 0
mismatches, and pinned permanently by `MergedGateMatchesPerCopy` in
`tests/test_hypergraph.py`, which keeps the old per-copy construction as the
reference. Benchmarked at 1.006 times the old cost, which is noise.

**3. CLOSED 2026-08-27. `claude.md` no longer recorded the two review batches.**

Both entries this note asked for are restored as standing conventions, each with
the reasoning rather than just the conclusion: why the multigraph vertex variants
reduce to the simple problem (parallel copies never raise kappa, so counted with
multiplicity the question has no finite answer, and why the multihypergraph cells
do NOT collapse the same way), and why the hypergraph witness is gated at the
source by proved attainment rather than clamped downstream (the downstream clamp
can only fire where exhaustion finished, which at `m = 6, n = 6, r = 3` it does
not). A dated entry for this session's work is appended to the same file.

One thing fixed while in there: the standing rule to run
`program/sync_code_appendix.py` after editing the program was dead, since
Appendix C was removed in the 2026-08-24 shortening pass, and a later session
note said so while the rule itself still instructed the opposite. The rule is now
corrected rather than contradicted.

## Subsequently closed

**1. CLOSED 2026-08-28. The machine-value cache is the record, and it is
machine-dependent.**

The `exact` entries are exhaustions under a wall-clock budget and the `search`
entries are timed heuristics, so what a given machine reaches is part of the
answer. `MachineValues._reconcile` makes a refresh unable to degrade the record.
The computational-audit section now states the exact distinction: `--refresh`
recomputes every entry but confirms or improves the stored record, while deleting
the cache is the stronger operation that starts again without that record.

**2. CLOSED 2026-08-28. Second independent proof and reference pass.**

The multihypergraph Menger proof's overview incorrectly called the translated
flow paths arc-disjoint even when several paths use a helper arc of capacity
`mu(e) > 1`; the detailed paragraph below already used the correct capacity
argument. The overview now says that the Berge paths give a feasible integral
flow. The computational-audit paragraph also no longer calls an unrecorded
working build an immutable submission snapshot. Finally, the verified DOIs for
Gomory--Hu, Chekuri--Xu, and Ford--Fulkerson were added to the bibliography.

## Not done, by choice

Promoting one or two proofs out of the appendix into a body chapter. That reverses
a deliberate decision (`c1c5390`, "Move every proof to the appendix"), so it stays
the author's call. The compatible half was done instead: the appendix is grouped
into four signposted parts that appear in the contents, with a reading guide that
names the flagship arguments.

## Subsequent correction

On 28 August 2026 the `ErdosProblems` entry was corrected to follow the website's
recommended citation and credit Thomas F. Bloom. The same pass corrected the
Bártfai source for the $m=3$ vertex result and the thesis-repository metadata.

## 2026-09-02 (Opus, second session) -- a code audit: 24 findings verified, 2 retracted, all fixed

A review of `erdos915_unified.py` produced 27 claimed defects. Every one was
re-checked against the file before anything was changed, which is how two of them
turned out to be wrong, and the check itself found a stale figure cache nobody
had asked about.

**THE ONE THAT WAS SHIPPING WRONG FIGURES.** `_all_objects_of_variant` took
`simple` and `max_mult` and ignored both on its hypergraph branch, sweeping
presence only (`product((0,1), ...)`). So the four multihypergraph panels of every
4x4 grid were byte-identical to the four simple hypergraph ones under a
multihypergraph label. Proved before fixing:
`_all_objects_of_variant(4, simple=True, max_mult=1)` and the same call with
`simple=False, max_mult=2` returned the same 16 objects, while the matrix branch
correctly gave 8 against 27. The config's own comment said row 4 "does NOT
collapse onto the simple rows", so the intent was documented and unimplemented.
Fixed to mirror `_brute_force_hypergraph`: each candidate hyperedge runs over
`{0..cap}` and is emitted `q` times. 16 -> 81 objects at n=4, and the regenerated
`edges_dist.png` multihypergraph row now reaches 8 edges where it used to stop at
4. `sample_random_hypergraph` had the same hole (it did not even take `simple`,
which `_sample_variant` was passing it) and now carries the hurdle-geometric tail
`sample_random_multigraph` uses.

**A STALE CACHE FOUND WHILE MIGRATING, NOT REPORTED BY THE REVIEW.**
`figures/surface_cache.json` was written 2026-08-25, before the incidence
convention landed on 2026-09-02, and its two multigraph VERTEX rows still held
values from the collapsing convention: `K_3(3)` cached as 3 where the current
proved value is 4, and so on for 14 exact cells. Checking all 206 exact cells
against `_surface_known_value` is what surfaced it. Both keys dropped so they
recompute. The other 178 exact cells verified with 0 mismatches and were kept.
**Re-stamping a migrated cache is only safe if you verify the values first.**

**THE j >= 7 SOUNDNESS NOTE WAS STALE, AND THE CODE WAS ALREADY RIGHT.**
`directed_multigraph_arc` said "Proved, all n and m" while
`enumerate_extremal_directed_multigraphs` carried a long warning that its j >= 7
pruning used the CONJECTURED floor(j^2/4) and "cannot certify completeness for
n >= 7". Both cannot hold. `thm:dir-multi-full` proves the value at every n
(`app_proofs.tex:940`), and the arithmetic already agreed:
`max(_PROVEN_MSTAR.get(j,0), j^2/4)` equals `max(2(j-1), j^2/4)` at every j from 2
to 13, the two branches tying exactly at j=7. So nothing computational changed and
only the claim did. The five-entry `_PROVEN_MSTAR` table is replaced by `_mstar(k)`
(`max(2(k-1), floor(k^2/4))`), defined once beside `directed_multigraph_arc`, which
is now `(m-1) * _mstar(n)`. Both warnings deleted. The generation twin's prefix
prune read the same table and so pruned nothing at all above j=6, and it now prunes at
every prefix size.

**A CRASH THAT HAS NOT FIRED AND NOW CANNOT.** `_propose_removal` weights removals
by `exp(-sigma/T)`, which underflows to exactly 0.0 once `sigma/T > 745`, so
`rng.choices` raises "Total of weights must be greater than zero" below T=0.00134
whenever no present edge is slack. The default schedule stops at T=0.0074, but
`plot_sa_vs_tabu_convergence` passes `steps=10**7` under an 8s deadline and this
machine runs 5400 to 6100 steps, crossing the cliff at step 5139. It survives only
because the minimum sigma was 0 in 446 of 446 low-T removals, and a sweep over 96
(variant, n, m, separation, seed) combinations found no all-load-bearing state.
Fixed by shifting by the minimum sigma before exponentiating and flooring at
1e-300. `rng.choices` normalises, so the freest edge is pinned at weight 1.0
instead of collapsing to zero with everything else.

**THE OTHER NINETEEN.** Tabu ranked candidate moves on energy first, so an
ordinary move with lower energy could displace a held aspiration move and drop the
global improvement it carried (energy is `-|E| + 6*excess`, so a dense infeasible
trial can undercut a feasible one). Now strictly lexicographic, aspiration first.
Tabu also evaluated every trial's max-flow BEFORE testing the tabu list, and the
resulting arc count alone rules most tabu moves out, so the test moved above the
flow. `ProofResult.value_for` raised `ValueError: cannot convert float NaN` on any
non-OPTIMAL solve and returns `None`. `plot_sa_vs_tabu_convergence` hardcoded
`L_3` in a label on a parameterised `m`. `_graph6_edges` silently misparsed the
n >= 63 multi-byte header and now refuses it. `plot_conn_threshold_3d` sized its
bars by the smallest gap between x positions, which is 0 once `min(1.0, r*p_star)`
clamps twice, making every bar in the panel invisible (fires at n <= 10 with m=3,
not at the default n=30). `_brute_force_hypergraph` ran an all-pairs Berge flow
before checking whether the candidate could beat the incumbent at all, which at
n=4, r=3 is 75% of candidates wasted. Reordered, values identical, 1.0x to 4.0x
faster on the cases timed. `sample_random_multigraph` looped forever at
`alpha=1.0`. `solve` never passed `kind`, so the "general" orientation model was
unreachable through the public driver even though the self-check shows it doubling
forward's value at n=r=4, m=4. Now threaded, and the label names it when it is not
the default. `SearchResult.feasible_found` was a stored field that both engines set
to True and never anything else, so it carried no information. It is now a property
meaning "bettered the empty graph". `_VARIANT_SAMPLE_CONFIGS` was 12 dead entries
that `_variant_panel_grid`'s docstring advertised as a drop-in for a 16-panel grid,
now deleted. The module docstring opened with "Twelve concrete variants" against
sixteen everywhere else, and `plot_variant_3d_surfaces` claimed sixteen while
drawing twelve. Both corrected, with the twelve-variant subsets named as such.
`_UNBOUNDED` was 10**9 against an int32 cast, leaving two saturated arcs at 2e9
inside 7% of a silent wraparound. Now 10**6, still enormous against real
capacities. The endpoint gate uncapping in three flow builders is a genuine no-op
(the flow starts past one gate and ends before the other, confirmed by rebuilding
with both set to 0 and re-measuring every pair of 200 random multigraphs, 0
mismatches) and now says so instead of reading as load-bearing. Five near-duplicate
pair generators collapsed onto `_matrix_cells`, moved up so it precedes all of
them. `_failures` never reset, so a second `_run_checks` in one process
double-counted. Plus the small ones: the double `warnings` import, `Callable` and
`Iterator` moved to `collections.abc` beside `Iterable`, three conditional
expressions used as statements, `prob += 0` for an empty objective, a hardcoded 2s
enumeration budget that ignored `time_per_case`, and a self-check slack written
`1e-3 * 5 * 5` where the tie-breaker maxes at `1e-3 * n(n-1)`.

**THE CACHES ARE JSON NOW, AND A DOCSTRING NO LONGER COSTS HOURS.**
`enumeration_cache` and `pair_enumeration_cache` were pickles: unreadable in a repo
a reader is meant to inspect, and `pickle.load` on a committed file is arbitrary
code execution. Both are JSON, nested `{"_meta": ..., "data": ...}` like the
surface cache, which itself spliced its fingerprint into the payload's own
namespace and now does not. The twelve unaffected keys were migrated rather than
recomputed. Separately, `_cache_metadata` hashed the whole 300KB source, so fixing
a typo in a docstring threw away hours of enumeration. `_source_fingerprint` now
round-trips through `ast` with docstrings stripped, so comment and prose edits keep
the cache and real code edits still invalidate it. Verified in both directions: a
docstring-and-comment-only edit leaves the fingerprint unchanged while the raw-byte
hash moves, and changing `_UNBOUNDED` still invalidates. Same trade `MachineValues`
already makes.

**TWO REVIEW FINDINGS RETRACTED.** The claim that the docstrings cite tests that
are not shipped is false: `program/tests/` holds 13 files and all three cited tests
exist (`test_search.py:89 test_fast_path_matches_exact`, `test_solve.py:361`'s
blind product sweep, `test_solve.py:139`'s geng equality). The claim that
`_canonical_form`'s C and Python paths may disagree is also false: differentially
tested over 300 random graphs at n=5, 0 mismatches. Only a documentation nit
survived, that "lexicographically smallest" is over the int32 byte encoding and
coincides with integer order while multiplicities stay under 256, which
feasibility guarantees.

**THE SEARCH CHANGES MOVE NO PUBLISHED VALUE, AND THIS WAS MEASURED.** The tabu
aspiration fix and the annealer weight fix both touch trajectories, and the four
`variant_bounds_*` grids the thesis actually prints read `machine_values.json`,
which is search-derived. So the old and new modules were loaded side by side and
run against each other on 16 fixed-step cases (both engines, both separations,
four variants, same seeds): 0 differences. `machine_values.json` therefore needs
no refresh and the printed figures are unaffected. Worth knowing for the next
person who changes a search engine: load the two modules with
`importlib.util.spec_from_file_location` and diff them directly, and use FIXED
STEP COUNTS rather than deadlines, so the comparison is deterministic and CPU
contention cannot skew it.

**WHICH FIGURES THIS TOUCHED, AND WHICH THE THESIS PRINTS.** The multihypergraph
enumeration bug corrupted `edges_dist`, `scatter_lambda_edges`, `pair_conn_dist`
and `conn_dist_m6`, and `main.tex` includes NONE of them: the thesis prints seven
figures and those four are not among them. The bug was real and the on-disk PNGs
were wrong, but the submitted PDF never showed them. Checked by extracting every
`includegraphics` path from the chapters rather than by assuming.

VERIFY: 132 tests OK with 1 expected skip, matching the pre-change baseline
exactly. Self-check ALL CHECKS PASSED. Every fix re-tested individually.
`enumeration_cache.json` and `pair_enumeration_cache.json` regenerated at 16 keys
each, `surface_cache.json` rebuilt after its two stale rows were dropped, and
`scatter_lambda_edges`, `pair_conn_dist`, `edges_dist`, `conn_dist_m6`,
`sa_vs_tabu_convergence`, `threshold_3d` and `variant_surface_3d` redrawn. The
multihypergraph row of `edges_dist.png` was cropped and inspected directly to
confirm it now carries its own data rather than the simple hypergraph's.


## 2026-09-02 (Opus) -- one convention for vertex separation, and the two multigraph problems it restores

The thesis now poses vertex separation once, in the incidence graph I(H): routes
are internally vertex-disjoint paths of I(H), so q parallel edges are q routes,
exactly as q copies of a hyperedge are. That is the convention the hypergraph
theorems already use, and the multigraph vertex question is its r = 2 case, so
the two are now the same question and the program says so.

**THIS SUPERSEDES BUG 1 OF 2026-08-25 (lines below).** That entry is kept for the
record and its diagnosis of the symptom was right: the driver was reporting a
number that could exceed the adjacencies available, and under the convention in
force then, where a parallel copy never raises kappa, counting multiplicity did
make the maximum infinite. The fix chosen, routing the multigraph vertex case
through the simple variant on the underlying graph, is now gone. Under the
incidence convention the cap that makes the question finite is the same one the
edge separation already uses, m - 1 per adjacency, because m parallel copies are
m disjoint routes in either sense. So the objective counts multiplicity, the
witness is a genuine multigraph, and the value is K_m(n) or K_m^dir(n).

WHAT CHANGED IN THE PROGRAM.
- `_split_capacity_matrix` gives each adjacency arc capacity mu(u, v) instead of
  1. The unit gate on the vertex copies is untouched: it is what makes the
  separation a vertex separation, and at r = 2 this is literally the hypergraph
  network.
- `solve()` lost the reduction branch entirely, along with `parallel_routes`
  everywhere it appeared (`exceeds_bound`, the split matrix) and the labels that
  named the old behaviour ("reduced", "= simple", "other convention"). There is
  no switch: one convention, one code path. `_brute_force_matrix` already
  enumerated multiplicities up to m - 1 under both separations, so exhaustion
  needed nothing; discovery already defaulted to the same cap.
- `max_multigraph_vertex_standard` is now `max_multigraph_vertex`, kept as an
  independent enumerator so the self-check can cross-examine the driver.
- `_surface_known_value` returns (m-1)(n-1) for m <= 3 (thm:hyper-vertex-m2/m3 at
  r = 2) and drops `_SURFACE_ALIASED_VERTEX`, the table that mirrored the
  multigraph vertex surface onto the simple one.
- `make_figures.py` panels (6) and (8) are their own rows now, exhaustive to
  n = 6 and n = 5 at a 120s budget, with the thickened tree 2(n-1) as the proved
  curve at m <= 3 and points only above.

NUMBERS THIS PRODUCES. K_3(n) = 2(n-1) is proved and matched by exhaustion at
n <= 6. K_6(n) = 5, 12, 19, 26 for n = 2..5, against L_6(n) = 5, 10, 15, 20: the
two separations genuinely part company on multigraphs, and K_5(4) = 14 > 12 =
L_5(4) is the smallest witness of it, now pinned in both the self-check and the
suite. Directed: K_2^dir(n) = M(n), K_3^dir(n) = 12 at n = 4, and K_6^dir(3) = 24
which is ABOVE (m-1)M(3) = 20, so the arc extremiser read through kappa <= lambda
is a lower bound for the incidence problem and not its value.

CACHE. `--refresh` was not enough on its own: it recomputes everything and then
reconciles against the published record, which is the wrong instrument for a
redefinition. `MachineValues.key` now appends `convention=incidence-1` to exactly
the keys whose meaning depends on the convention (vertex separation, not simple,
not hypergraph). It orphaned zero of the 506 entries then present, because the
old code never called the driver for those cells at all, which is precisely why
the bug survived a year of figures. It will retire them the moment anything about
the convention moves again.

TESTS. The three `MultigraphVertexObjective` tests asserted the reduction and are
replaced by nine in `MultigraphVertexIncidenceConvention`: two parallel edges are
two routes, one added copy raises the local value by exactly one and kappa^max by
at most one, K_2(n) = n - 1 and K_3(n) = 2(n-1) by exhaustion with a doubled-edge
witness, K_5(4) = 14 against the edge value 12, discovery reaching the thickened
tree, the directed values at m = 2 and 3, and the one that carries the
convention: the graph checker and the hypergraph checker agree on random
multigraphs, pair by pair and on kappa^max, when the multigraph is presented as a
2-uniform multihypergraph with one hyperedge per copy. 132 tests, one skip.

A FOURTH INVARIANT, near enough, in `_reconcile_panel`. Invariant 2 justifies its
running maximum by the isolated vertex, but it only ever clamped the search
circles DOWN to an exact value, so a search that underperformed could report less
at n+1 than was already proved at n. The m = 6 incidence row printed an exact 26
at n = 5 and >= 25 at n = 6. Exact values are now folded into the series before
the running maximum, on the ground that a maximum is attained and is therefore
itself a witness. Only those four rows moved.

VERIFY: full suite green, self-check green, all four grids and
`variant_table_all.tex` regenerated. Chapters not yet touched.

## 2026-08-25 (Opus) -- second review batch: two computational bugs, six overclaims

A second external review of `ea07b51`. All eight findings were reproduced before
anything was changed, and the two flagged as computational were the real ones.

**BUG 1: solve() optimised the wrong objective for both multigraph VERTEX
variants.** `sec:parallel-convention` poses those two with the objective counting
ADJACENCIES, and it has to: a parallel copy never raises kappa, so it never breaks
feasibility either, and counted with multiplicity the maximum would be infinite
and the question empty. The driver nevertheless maximised `Graph.edge_count()`,
which counts multiplicity. Reproduced at n=3, m=3: undirected reported 6 where
only 3 pairs exist, directed 12 where only 6 ordered pairs exist, in BOTH the
exhaustive and the discovery path. The reported number was not merely scaled, it
exceeded the number of adjacencies available.
  It hid because the figures never call the public driver for those two cells:
`gather_variant_grid` panels (6) and (8) reuse the simple-variant results
(`ex2/se2`, `ex4/se4`) directly. So every published figure was right and only a
direct caller of `solve()` was wrong, which is the worst place for it, since that
is the entry point the thesis documents.
  FIXED at the dispatch, the way the thesis says the question reduces: the
multigraph vertex case now routes through the simple variant on the underlying
graph, so it returns an adjacency count with a simple witness, and both the
`variant` string and the `note` say the reduction happened. As a side effect the
directed case now gets the pruned branch and bound instead of blind brute force.
Six regression tests pin it: value, simplicity of the witness, agreement with the
count read off that witness, agreement with the simple driver at six (n, m) cells,
and an invariant the old code violated at every m >= 3, that an adjacency count
cannot exceed the number of pairs.
  MY FIRST TEST WAS WRONG, recorded because the mistake is instructive. I asserted
the value does not move with m, on the theory that the underlying graph is fixed.
It is not: k_3(4)=4 but k_4(4)=6, since at m >= n the complete graph is itself
feasible. The pairs-available invariant is the right pin and the m-invariance was
never true.

**BUG 2: the m=6 grid plotted a hypergraph witness that provably does not exist.**
`make_figures.lb_hyper_edge` fed the universal upper bound of `prop:hyper-edge`
into `_extend_lower_bounds`, which promotes it to an open-circle WITNESS. The
panels enumerate SIMPLE hypergraphs, and `thm:simple-hyper-edge` attains that
bound only when `m-1 <= C(n-2, r-2)`. At r=3, m=6, n=6 the condition fails (5 > 4)
and the circle claimed 12. It cannot be met: I enumerated all C(20,12) = 125970
twelve-hyperedge simple 3-uniform hypergraphs on six vertices and none is
feasible, and the program's own branch and bound independently returns 11 as the
exact maximum. At m=3 the same fault put 2 at n=3, where only one 3-set exists.
  The gate for this, `_hyper_edge_simple_proved`, was already written, and
`hypergraph_edge`'s docstring already said in as many words that figures should
read the gated version. The comment at the vertex panel shows what happened: the
author knew about the corner and relied on `_reconcile_panel`'s exact-value clamp
to fix it. That clamp can only fire where exhaustion FINISHED, and `exact_budget`
is 4 seconds while n=6 at m=6 takes minutes, so at exactly the cell that needed it
the safety net was not there. A safety net downstream of a wrong value is not the
same as not producing the wrong value.
  FIXED by gating at the source: new `attained_hyper_edge` / `attained_hyper_vertex`
return 0 outside the proved-attainment range, so the honest search value stands.
The ungated formula is kept for the proved CURVE, where it belongs, since it is a
genuine upper-bound theorem. Both grids regenerated. `ch2` now states the gap
plainly instead of claiming the search reaches every available upper bound: on the
two undirected hypergraph rows the blue curve is an upper bound whose attainment by
a simple hypergraph is unproved below the threshold, so the circles sit below it,
and the m=6, n=6 cell is named with its enumerated count.
  NOT CHANGED, and worth a future look: the same closed form is capped down to
machine-exact values by `_reconcile_panel` invariant 1, so where exhaustion happens
to finish the plotted "proved" curve is the true value and where it does not the
curve is the looser bound. At m=6 that produces a kink between n=5 (true 8, curve
clamped) and n=6 (true 11, curve 12). Correct as an upper bound either way, but the
plotted line means two different things at two adjacent points. Fixing it properly
means teaching the panel to carry upper-bound curves that are not clamped, which
touches every panel, so it is recorded rather than done.

**SIX OVERCLAIMS.** (3) The Short Summary credited the search with "the double
star (undirected multigraphs at m=2)", wrong on all three counts against
`tab:rediscovery`, which records a multiplicity star for undirected multigraphs at
m=3 and the double star for DIRECTED multigraphs at m=3. It also claimed the search
rediscovered the one-directional bipartite digraph and the augmented-bipartite
construction, which `ch2` itself contradicts two sections later (the n=8 search
stalls at 14, and the augmented family is supplied and checked). Rewritten to
match, and ch1's "the thirty-arc counterexample was found the same way [by
exhaustive search]" corrected too, since ten vertices put a blind sweep far out of
reach and it was constructed and then checked.
  (4) `thm:sorensen-thomassen` correctly excludes n=7 and n=12, with k_5(7)=15 and
k_5(12)=27, but the unconditional formula was printed in the Short Summary, the ch3
discussion, `tab:summary`, the ch1 lineage paragraph, the divergence caption and
the plot legend. At n=12 it gives 28 against the true 27, which contradicts the
adjacent claim that edge and vertex agree through n=13. Exceptions added in all six.
  (5) "All computational claims rerun from erdos915_unified.py" is not true: the
194066-block sweep behind c_m and the multigraph block sweep run from standalone
scripts in `research_notes/`, which the root README described as work NOT in the
thesis. Both are now named where their numbers are used and in the audit section,
and the framing is honest: they were deliberately written apart so they corroborate
the main program rather than share its code. `program/README.md` also advertised
`rediscovery_table.tex` as generated by `make_figures.py`; nothing generates it, it
is hand-kept from `solve()` runs at fixed seeds, and both README rows say so now.
  (6) `Hypergraph` does not enforce r-uniformity: it asks only for two vertices per
edge, has no r field, and will hold edges of sizes 2, 3 and 4 side by side. The
generators are all uniform, so no reported search is affected. Took both options
the review offered: `r` is now an optional constructor argument, enforced on every
add when supplied, and ch2 says uniformity is a property of the generators rather
than of the store.
  (7) The base-case table said the arc and vertex runs visit identical node counts
"because the prunes do not depend on the separation". They do: the feasibility
prune picks `_arc_flow_at_least` or `_vertex_flow_at_least` by separation. The
counts coincide empirically, and the caption now says so.
  (8) `test_directed_multigraph_is_proved` was skipped unless pulp was installed,
on the grounds that solve() proves it through the MILP. It has not for some time:
that branch returns the closed form of `thm:dir-multi-full` and checks it against a
named witness. Skip removed, the method string asserted, and the now-unused
`PULP_AVAILABLE` import dropped. That was the last "expected skip" in the minimal
environment for a reason that no longer existed.

OUT OF SCOPE, checked and left alone: `_VARIANT_ENUM_CONFIGS` and
`_VARIANT_SAMPLE_CONFIGS` do carry multigraph vertex cells that count multiplicity,
but they drive distribution figures over a whole enumerated population rather than
an extremal objective, and those figures are offcuts, not in the live thesis.
[2026-09-02: moot. Counting multiplicity there is what the incidence convention
asks for.]

VERIFY: 115 pp, 0 overfull, 4 underfull, 0 undefined, 0 warnings. Full suite green
with the stale skip gone. Both grids regenerated from the gated code.

## 2026-09-02 (Opus, second session) — input validation, and the cache split into render vs rebuild

An external audit listed six defects. All six reproduced against the code before
anything was changed, and two of its claims were narrower than stated: SciPy
already rejects equal endpoints in EDGE mode (only the split matrix returned 1
for a self-pair), and an out-of-range hypergraph endpoint is only silently
accepted while the index lands inside the gate block, since a larger one falls
off the network and raises. Neither weakens the fix, because validation that
depends on where a bad index happens to land is not validation.

VALIDATION. One primitive, `_require_integer(name, value, minimum, maximum,
range_error)`, is now the only place an integer is checked, because the part that
gets forgotten is the first line: `bool` is a subclass of `int`, so `True` passes
every naive test and means vertex 1 or multiplicity 1. It is wired into both
`__init__`s, `_require_vertex`, `_assign`, `add_edge`/`remove_edge`, the new
`Hypergraph._vertex_set`, both connectivity endpoint guards, and `solve`'s domain
(n >= 1, m >= 2, 2 <= r <= n; n = 1 is admitted because 0 is its true answer).

**TWO LAUNDERING PATHS, BOTH FOUND BY WRITING THE FIX AND NOT BY READING THE
AUDIT.** A guard on `_assign` alone does NOT catch `add_edge(0, 1, 1.9)` on a
simple graph: the saturation `min(mu + 1.9, 1)` returns a clean integer 1 and the
bad input is gone before the assignment sees it. And `frozenset([0, 1, True])` is
`{0, 1}`, because `True == 1`, so a bad member does not survive to be rejected,
it disappears and leaves a hyperedge one vertex short. A declared uniformity
catches that by accident, as a size error; `r=None` does not catch it at all.
Both fixes are therefore ordered: check before the normalising step, never after.

CACHE, REBUILT AS RENDER VS REBUILD. The old `--refresh` reconciled a rerun
against the published record and kept the better value, which meant a "successful"
refresh could stamp the new program's hash onto values the old program computed.
Fixing that by hand ran into the deeper problem: the fingerprint answers "did any
byte change", never "did any answer change", so a fail-closed check fires on a
validation edit that provably changes nothing. Rendering now never computes (a
missing key is an error), `--rebuild` recomputes everything from scratch into
`data/machine_values.candidate.json` and draws nothing, `--compare` lists every
departure, and `--promote` is the only act that writes the record. Provenance
(program hash, source commit, python, platform, date) is recorded and never
enforced. `_reconcile`, `--accept-stale` and the compatibility-list idea are all
gone, and about eighty lines with them.

MEASURED, NOT ESTIMATED. A full rebuild is about an hour: 46.5 min for the 129
exact entries plus 10 min of timed searches. Two entries are 46 percent of it
(directed simple n=6 m=3, 930s vertex and 357s edge). The 1800s budgets are pure
headroom, never spent, and larger m is CHEAPER, not dearer, because a weaker
constraint lets the incumbent climb and the search prune. All 129 exact values
recomputed identically under the new code, which is the evidence that the
validation edits changed no answer. The same two entries were recorded at 1423s
and 544s earlier, 1.5x slower on the same machine, which is exactly the
machine-dependence the render/rebuild split exists to contain.

RECORD_REVISION. `git diff` ignored untracked files, so an untracked figure the
PDF was built from read as clean; now `git status --porcelain`. `git tag -f` could
move a tag already printed inside a handed-in PDF; now it refuses, and options are
parsed rather than read as a tag name.

VERIFY: full suite green, self-check ALL CHECKS PASSED, both variant grids
gathered from the record with nothing computed and no candidate written.

# Equal-budget benchmark protocol

This protocol was chosen before the long experiment started. It is a new
experiment and does not relabel or overwrite the historical thesis data.

## Allocation

All 16 combinations of direction, multiplicity, graph or hypergraph model
and route separation are included. Orders are 6, 8, 10 and 12. Thresholds are
3 and 6. Hypergraphs are 3-uniform and directed hypergraphs use the forward
orientation. The multigraph vertex convention counts parallel direct edges
as separate routes through the incidence graph.

Each variant receives a total allocation of 3600 seconds of search. Its eight
parameter cases each have three runs with initial seeds 0, 1000000 and
2000000. Each run has a 150-second stopping target. There are 384 runs in all,
requiring approximately 16 hours plus setup and witness validation.

The matrix engine is tabu search. The hypergraph engine is randomised greedy
growth. Both start empty and receive no construction, target optimum or
incumbent from another run. Matrix restarts increment the initial seed.
Hypergraph restarts continue a single seeded random stream.

## Execution and records

Runs are serial. The order of variants rotates between parameter cases.
Numerical-library thread limits are set to one. This does not isolate the
computer from other programs, thermal changes or operating-system scheduling.
The full regression suite is completed before starting the long experiment.

The runner freezes its own code, the solver, the C source and the available C
binary. Their hashes are recorded. Each trial stores a witness and its
rechecked connectivity, objective value, wall time, CPU time and validation
time. Validation uses the main checker and is not claimed to be an independent
proof of that checker's correctness.

The search deadlines are cooperative. A check in progress can overrun its
target. Completed trials are checkpointed atomically and retained on resume.
An interrupted trial without a checkpoint is restarted. Its lost elapsed time
is marked unknown, so resumed experiments may have consumed more time than
their nominal allocation. A lock prevents two runners from sharing the output.

## Reporting

The separate reporting script freezes the supplied construction baseline and
shows minimum, median and maximum search values over the three runs. All
individual witnesses remain available. A supplied construction is a lower
bound and is not labelled optimal unless separately proved elsewhere.

An incomplete experiment is labelled partial. Missing trials are not assigned
zero and a row with fewer than three completed seeds has not received its full
allocation. Reports do not update the historical grids or manuscript
automatically. Integration into the thesis follows review of the completed
data and any interruptions.

## Preflight checks

A short smoke experiment exercised all 384 trial slots at the actual selected
orders. Its allocation was only 0.12 seconds per variant and its outcomes are
not performance evidence. Every returned witness passed validation. Resuming
the completed smoke experiment reused all checkpoints. The separate reporter
rendered all 128 parameter rows with construction counts in a distinct column.

Unit tests check equal allocation, unique trial identifiers, preservation of
checkpoints on failed writes and rejection of invalid budgets.

## Further audit corrections

The nine-vertex block sweep now checks its generator's exit status before
asserting an upper bound. Its pruning threshold is not printed as an attained
value unless a witness has actually been found. The retained witness
`H??EDz}` was checked to have 14 support edges and multigraph score 54 at m=6,
with maximum incidence connectivity 5. A fresh generator count matched the
historical 191826 candidates. This checks the transcript's coverage count and
witness, not the entire historical optimisation calculation.

The manuscript now states the integer hypotheses in both degree-balancing
lemmas. It explains why sharing vertices fits more clique blocks without
incorrectly claiming that bridges create vertices. The bipartite construction
proof distinguishes the exhibited two-step paths from longer paths that may
also exist. The block proof handles a chain of blocks rather than assuming
that any two blocks share a vertex. The joint asymptotic discussion no longer
presupposes that its bounded ratio converges.

A separate regression check tested the incidence-rank inequality on every
eligible partition of connected simple graphs through six vertices in the
NetworkX graph atlas. The multigraph induction still requires its mathematical
proof. No claim of complete independent certification of every retained
theorem is made.

## Review while the experiment is running

On resuming at 208 saved trials, the timing review found one anomaly in
`v05_n6_m3_seed0`. Its outer monotonic duration was 90.302 seconds, its CPU
time was 90.042 seconds and the solver reported 792.301 seconds on its
calendar clock. The UTC timestamps agree with the longer calendar interval.
Sleep or a clock adjustment could account for the discrepancy. The saved
record does not establish which occurred.

The original frozen solver uses calendar-clock deadlines. Its code and trial
files have not been changed. The reporter now flags discrepancies over one
second and durations more than one second short of the requested target.
Such trials remain available as raw feasible witnesses but are excluded from
timing-qualified statistics. An experiment with these flags cannot be reported
as a completed equal-budget comparison without review and replacement runs.
Replacement runs should occur after the serial experiment ends, preserve the
original files and record their own source version. No replacement has yet
been run.

The working solver has been changed to use monotonic duration budgets in
`solve()`. Direct callers passing absolute calendar deadlines to older helper
functions remain supported. Tests exercise all 16 variants in discovery and
exhaustive mode while making calendar-clock access raise an exception.
Monotonic duration and calendar time are distinct measurements, especially
around system suspension. New runner snapshots record both explicitly.

The preflight full suite completed 185 tests in 235.283 seconds with one
expected skip. Subsequent targeted regression checks cover the timing fix,
the incidence-rank check and the new construction below. Short test and
document-build jobs have run during the live benchmark. The experiment is
serial at the search-runner level but is not a machine-isolated CPU benchmark.

## A cell settled by the new search

`v12_n6_m6_seed0` found 12 hyperedge copies in the undirected multihypergraph
edge problem. The duration was 150.002 seconds and the clock checks pass.
The saved witness has degrees 5, 11, 5, 5, 5 and 5. Thus every vertex pair
includes an endpoint of degree five, giving a cut of at most five copies.
Its 12 copies meet the upper bound floor(5*5/2)=12.

The thesis now gives a cleaner explicit construction as
`const:multihyper-six`. On a hub and five leaves, include all ten triples
through the hub, repeat the triple using the last two leaves and add the
triple consisting of the first three leaves. Every leaf then has degree five.
This construction was checked by the flow helper and by enumerating all 62
nontrivial vertex cuts independently. It settles the edge value but only
supplies a lower bound for vertex separation.

Historical search observations remain unchanged. The construction series
and the current thesis table now include 12. The running benchmark's
comparison_baseline.json intentionally retains the earlier supplied value
11, as frozen before this result was found. It is a historical comparison
baseline, not a claim to contain the latest known constructions.

The current construction series also includes the bounded-outdegree forward
hypergraph family in `const:bounded-outdegree-hyper`. Each vertex receives at
most m-1 outgoing hyperedge copies. Those copies form a cut separating that
source from every other vertex. The simple count is
n*min(m-1, binomial(n-1,r-1)) and the multi count is n*(m-1). These are compared
with the two-layer construction, not substituted for search results. This
improves the supplied small-order bounds, including the previous zero simple
construction entry at n=m=6, where this family gives 30. The frozen benchmark
baseline is unchanged.

After the duration-clock changes, targeted runs passed 10 audit regression
tests, 32 solver tests, 10 search tests, 9 construction tests and 18 table
tests. The construction checks include both route separations for the new
forward family. These are targeted checks of the revised working code, not
a rerun of the entire preflight suite or of the frozen benchmark.
The 21 hypergraph tests and 26 model tests also passed. The rebuilt thesis
has 118 pages and passes the reference-consistency gate. There are no
unresolved-reference or overfull-box warnings. The existing bibliography
underfull-box warning remains. Both new construction passages were visually
checked in the PDF.

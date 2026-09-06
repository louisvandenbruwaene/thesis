# erdos915: the unified program

One main Python file, `erdos915_unified.py`, models every variant of Erdős
Problem 915, measures connectivity exactly, certifies upper bounds for small
sizes, and searches for extremal objects with model-specific heuristics. It is
written to be read top to bottom: clear names, docstrings everywhere, and a
strict separation between what is *measured*, what is *proved*, and what is
merely *discovered*. An optional C helper accelerates small hot paths, but the
Python implementation is the correctness path.

There is one solver. Whatever the question, you call `solve(...)`: it picks the
right method for the case (a proved closed form, brute-force enumeration, a
matrix search, or randomised greedy hypergraph search) and labels its answer
honestly as exact, an upper bound, or a lower bound. You never run a different
program for a different case.

## Layout

```
program/
  erdos915_unified.py   the whole program: the model, the connectivity checker,
                        Gomory-Hu, the cut-counting solver check, sensitivity, the
                        tabu and annealing searches, solve(), the random-model sampling,
                        the figure routines, and a self-check in __main__
  _erdos_fast.c         optional C hot-path helpers for small max-flow and
                        canonical-form calls
  build_fast.sh         builds the optional _erdos_fast.so accelerator
  make_figures.py       regenerates every thesis figure into ../figures/
  tests/                an extensive unittest suite covering the whole program
  scripts/              independent mathematical checks, block sweeps and
                        experiment drivers that call the main solver
  data/                 machine_values.json, the recorded result of every solve
                        call behind the four variant grids
  logs/                 run transcripts the computational audit cites
  README.md             this file
```

The thesis hands a reader two things, `main.pdf` and this directory, so
everything the text points at is inside it.

## Requirements

Install with `pip install -r requirements.txt`. The core needs only `numpy` and
`scipy`: the model, the connectivity checker, the search, the enumeration, the
random-model sampling, and the self-check all run on those two alone, because connectivity is measured by integer max-flow on a capacity matrix (Menger).
Small capped checks can use the optional C helper; capacities too large for
safe int32 arithmetic use the Python-integer fallback.
One more library backs the solver check and two are optional:

- `pulp` backs the MILP solver checks (`prove_directed_multigraph` and
  `prove_integral_arc_bound`): one solver-agnostic cut-counting model that runs on
  CBC (bundled with `pulp`) by default and on Gurobi by passing `use_gurobi=True`.
  These routines raise a clear message if called without `pulp`.
- `matplotlib` is needed only to render the figures (`make_figures.py` and the
  `plot_*` routines). Without it everything else still runs.
- `networkx` is needed only for the Gomory-Hu tree, a single figure/analysis
  helper. `gomory_hu_tree` raises a clear message if it is called without it.

The program runs without a build step. `bash build_fast.sh` optionally compiles
`_erdos_fast.so` to accelerate small hot-path searches.

One optional extra: `enumerate_extremal_directed_multigraphs_via_generation` (the
sound, generation-based directed-multigraph enumerator that follows J. Goedgebeur's
`geng` suggestion) shells out to nauty's `geng`. It decorates the supports in
parallel across processor cores (each support is independent), which is what makes
the open `n = 7` classification practical on a multi-core machine. Pass
`parallel=False` for a single-process run. Everything else, including the
self-test, the figures, and the test suite, runs without `geng`. Every test that
needs an optional dependency skips itself cleanly when that dependency is absent,
`geng` for the generation pipeline, `pulp` for the MILP certifier and `networkx`
for the Gomory-Hu view, so a minimal `numpy` plus `scipy` install runs the suite
green rather than reporting failures for tools it was never asked to have.

## How to run

From this `program/` directory:

```bash
../.venv/bin/python3 erdos915_unified.py            # run the built-in invariant self-check
../.venv/bin/python3 -m unittest discover -s tests  # run the full suite
../.venv/bin/python3 make_figures.py                 # regenerate every figure
../.venv/bin/python3 make_figures.py --grids-only    # regenerate the four bound grids
../.venv/bin/python3 make_figures.py --tables-only   # regenerate the sixteen-variant value table
../.venv/bin/python3 make_figures.py --rebuild       # recompute every machine value from scratch
../.venv/bin/python3 make_figures.py --compare       # show how the rebuild departs from the record
../.venv/bin/python3 make_figures.py --promote       # publish the reviewed rebuild
```

### Search results are not construction values

The grids retain raw unaided search outcomes as circles and show supplied
constructions separately as plus signs. Neither exact values nor a stronger
result at another order or in another model overwrite the search.
A contradiction with a proved upper bound raises an error rather than
silently clamping a number.

The companion tables give separate search/construction rows.
`data/search_evidence.json` gives both values for all plotted orders, the
historical per-case limit, and the source cache key. Most historical searches
used 0.4 seconds; the more expensive selected open cases used 4 seconds.
These are not equal-time or one-hour benchmark results. Deadline checks are
cooperative: an in-progress feasibility check can overrun the target.
A fixed seed does not make timed outcomes hardware-independent.

### Equal-budget benchmark

`scripts/equal_budget_benchmark.py` runs the 16 variants serially. The default
allocation is 3600 seconds of search per variant, split equally over orders
6, 8, 10 and 12, thresholds 3 and 6 and three initial seeds. Thus each of the
384 trials has a 150-second cooperative stopping target. Hypergraphs are
3-uniform and directed hypergraphs use the forward orientation. Matrix models
use tabu search and hypergraph models use randomised greedy search. No
construction or optimum is passed to either method.

```bash
../.venv/bin/python3 scripts/equal_budget_benchmark.py --output data/equal_budget_2026-09-06
../.venv/bin/python3 scripts/benchmark_report.py data/equal_budget_2026-09-06
```

The output directory must be new. It contains a frozen copy of the solver,
the runner and the optional C accelerator, together with source hashes and
the full schedule. Each completed trial saves its witness, checked
connectivity, actual search time, CPU time and validation time. The process
limits numerical-library threads to one but does not control other programs
on the computer. Wall time depends on system load and sleep.

Use the printed frozen `--resume` command after an interruption. Completed
trials are reused. An unfinished trial is restarted and recorded as an
interruption with unknown previous elapsed time. Such restarts mean the total
time spent can exceed the nominal allocation. A lock prevents simultaneous
runners from writing to the same experiment.

The separate report shows all seed outcomes and supplied construction counts.
It labels unfinished experiments as partial and does not count missing trials
as zero. Neither script replaces historical data or updates the thesis figures.
The full default experiment needs about 16 hours plus setup and validation.

The first long experiment uses its frozen, older solver with calendar-clock
deadlines. One saved trial showed a large discrepancy between calendar time
and the outer monotonic duration clock. The reporter flags such trials and
excludes them from timing-qualified statistics without deleting their values.
A flagged run must be reviewed or rerun before claiming the full equal-budget
comparison. A one-second tolerance is used for clock disagreement and short
durations. Cooperative overruns remain visible in the elapsed-time fields.

The working solver now uses monotonic duration budgets in `solve()`. Direct
calls to older helpers still accept absolute calendar deadlines for backwards
compatibility. The running experiment's frozen source has not been modified.
New experiments additionally record calendar elapsed time alongside monotonic
duration and CPU time.

### The machine-value record

The four sixteen-variant bound grids are built from several hundred `solve`
calls, exhaustive enumerations run to a timeout and timed searches, and that is
almost all the wall clock in `make_figures.py`. Their results are kept in
`data/machine_values.json`, one readable entry per
`(kind, n, m, budget, variant)`, holding the value that run produced or `null`
where an exhaustion did not finish inside its budget. With the file present the
grids redraw in about three seconds.

Those numbers are an experiment and the file is its result, so **rendering and
recomputing are separate acts**:

| command | what it does |
| --- | --- |
| no flag | renders only the figures and tables used by the current thesis, from formulas and the frozen record. It never starts a search. A missing recorded value is an error. |
| `--rebuild` | recomputes every value from scratch, consulting nothing, into `data/machine_values.candidate.json`. Draws nothing. Resumable: an interrupted run picks up where it stopped. |
| `--compare` | lists every way the candidate departs from the record, and calls out two completed exhaustions that disagree. |
| `--promote` | replaces the record with the reviewed candidate. |

The separation is what makes the figures reproducible. A search given four
seconds finds what four seconds of one particular machine reaches, so a render
that quietly recomputed would redraw the thesis differently on a busier laptop.
A rebuild is therefore a deliberate act with a review step, and the record is
what the published figures are drawn from.

Provenance sits beside the values: the program fingerprint, the source commit,
the interpreter version, the platform and the date. It is recorded, not
enforced. A fingerprint answers "did any byte change", never "did any answer
change", so nothing refuses to draw because it moved; `--rebuild` followed by
`--compare` settles that question with the numbers themselves. The fingerprint
now covers the complete main program, C source and figure/experiment driver.
The earlier chapter-four cutoff missed flow helpers defined later in the file.
New runs also record dependency versions, the loaded C binary hash, method,
requested and elapsed seconds, completion status and the witness. Historical
records without those fields remain explicitly incomplete; they are not backfilled.

A recorded value is only meaningful while its key still means the same
question, so the key of a multigraph *incidence* entry carries a convention
stamp (`VERTEX_CONVENTION` in `make_figures.py`). Bumping the stamp retires
exactly the entries whose meaning moved and leaves the rest alone.

The test suite needs no third-party test runner: it uses the standard library
`unittest`. If you do have `pytest` installed, `pytest tests` discovers the same
tests.

To solve a specific case, import `solve` and call it, for example:

```python
from erdos915_unified import solve
solve(6, 3, directed=True, simple=False, exhaustive=True)  # directed multigraph value
solve(16, 3, directed=True, exhaustive=False) # discover a dense example (lower bound)
solve(7, 2, hypergraph=True, r=3)             # the hypergraph model
solve(5, 3, simple=False, separation="vertex") # K_3(5), the multigraph incidence value
```

The two separations are `separation="edge"` and `separation="vertex"`, and on a
multigraph they are different questions, not two names for one. Under the
incidence convention of `sec:incidence-convention` a route is a path of the
incidence graph, so `q` parallel edges are `q` internally disjoint routes just as
they are `q` edge-disjoint ones, and the multigraph incidence maxima `K_m(n)` and
`K_m^dir(n)` are problems in their own right rather than the value of the
underlying simple graph. They can separate: `K_5(4) = 14` against `L_5(4) = 12`.

## The honesty contract

| Computational route | What it gives you |
|-----------------------|-------------------|
| connectivity checker  | **exact** local connectivity (Menger / max-flow) |
| cut-counting solver check | a finite solver result and primal witness, with no independently replayable certificate emitted |
| tabu search (and the annealing cross-check) | a **discovered** construction, hence only a **lower** bound, never a proof of optimality |
| random-model sampling | an **estimate** over random samples, never a proof |

The search proposes. The certifier and the hand proofs dispose.

## Which output feeds which figure

The thesis is three chapters: (1) The Problem and Its Variants, (2) Certifying
and Discovering Bounds by Machine, and (3) Synthesis, Results, and Open Problems.
`make_figures.py` renders the current thesis assets, including the rediscovery
table from `data/rediscovery.json`. The latter contains seven fresh unaided
runs, each with a two-second target, initial seed zero, measured elapsed time
and a saved witness. To perform a new experiment without replacing that record:

```bash
../.venv/bin/python3 scripts/rediscovery.py --seconds 2 --output data/rediscovery.new.json
```

These are small validation cases, not an equal-time sixteen-variant benchmark.
The remaining separately generated table,
`figures/generating_benchmark_table.tex` is written by
`scripts/generating_search_benchmark.py`. Each header records how its rows
were produced; rerun those calls to check them.

| Figure | Thesis chapter |
|--------|----------------|
| `figures/edge_vertex_divergence.png` | the m=5 divergence (Ch.1) |
| `figures/edge_vertex_sampling.png` | edge vs vertex disjointness in G(n,p) (offcut only) |
| `figures/complexity_growth.png` | the enumeration explosion in n, m, direction (Ch.2) |
| `figures/temperature_trace.png` | a cooling run (offcut only) |
| `figures/sensitivity_mixed.png` | load-bearing edges by sensitivity (offcut only) |
| `figures/rediscovery_table.tex` | validation-by-rediscovery table (Ch.2), rendered from `data/rediscovery.json` |
| `figures/generating_benchmark_table.tex` | blind / pruned / generated timings (Ch.2), from `scripts/generating_search_benchmark.py` |
| `figures/variant_table_all.tex` | the sixteen-variant value table (Appendix audit) |
| `figures/variant_bounds_m3_graphs.png` | theorem / enumeration / raw search / construction, the eight graph-model variants at m = 3 (Appendix audit) |
| `figures/variant_bounds_m3_hypergraphs.png` | the eight hypergraph-model variants at m = 3 (Appendix audit) |
| `figures/variant_bounds_m6_graphs.png` | the same graph-model half at m = 6 (Appendix audit) |
| `figures/variant_bounds_m6_hypergraphs.png` | the same hypergraph-model half at m = 6 (Appendix audit) |
| `program/data/machine_values.json` | the cached `solve` results those four grids plot (not a figure) |
| `figures/directed_crossover.png` | hub/bipartite crossover (Ch.3) |
| `figures/scatter_lambda_edges.png` | the extremal envelope over all graphs (offcut only) |
| `figures/variant_surface_3d.png` | the bound surface over the (n, m) grid (offcut only) |
| `figures/extremal_graphs_gallery.png` | the named extremal families (offcut only) |
| `figures/pair_conn_dist.png` | pooled per-pair connectivity distributions (offcut only) |
| `figures/edges_dist.png` | edge-count distributions (offcut only) |
| `figures/conn_dist_m6.png` | per-graph connectivity distributions at m = 6 (offcut only) |
| `figures/threshold_3d.png` | the threshold across densities, three variants (offcut only) |
| `figures/trace_*.png` | per-variant search traces (offcut only, all five) |
| `figures/sa_vs_tabu_convergence.pdf` | SA against tabu, wall-clock timed (offcut only) |

**Offcut only** means the figure is no longer referenced from `main.tex`. It is
preserved for `offcuts.tex`, the record of removed material. Normal figure
rendering no longer reruns these archived experiments or refreshes their assets.

The solver records (`logs/certificate_log.txt`, `logs/basecase_search_log.txt`,
`logs/basecase_search_vertex_log.txt`) were produced by the named finite
routines on the directed cases; the appendix now tabulates them rather than
printing them verbatim. Randomised searches use fixed seeds. The SA-versus-tabu
timings are the documented exception, because their stopping rule is wall-clock.

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
                        temperature search, solve(), the random-model sampling,
                        the figure routines, and a self-check in __main__
  _erdos_fast.c         optional C hot-path helpers for small max-flow and
                        canonical-form calls
  build_fast.sh         builds the optional _erdos_fast.so accelerator
  make_figures.py       regenerates every thesis figure into ../figures/
  tests/                an extensive unittest suite covering the whole program
  README.md             this file
```

## Requirements

Install with `pip install -r requirements.txt`. The core needs only `numpy` and
`scipy`: the model, the connectivity checker, the search, the enumeration, the
random-model sampling, and the self-check all run on those two alone, because every
connectivity measure is one scipy integer max-flow on a capacity matrix (Menger).
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
python erdos915_unified.py            # run the built-in invariant self-check
python -m unittest discover -s tests  # run the full suite (no third-party test runner)
python make_figures.py                # regenerate the figures in ../figures/
python make_figures.py --grids-only   # just the four sixteen-variant bound grids
python make_figures.py --refresh      # ignore the cached machine values, recompute
```

### The machine-value cache

The four sixteen-variant bound grids are built from several hundred `solve`
calls, exhaustive enumerations run to a timeout and timed searches, and that is
almost all the wall clock in `make_figures.py`. Their results are kept in
`../figures/machine_values.json`, one readable entry per
`(kind, n, m, budget, variant)`, holding the value that run produced or `null`
where an exhaustion did not finish inside its budget. With the file present the
grids redraw in about three seconds instead of half an hour.

Caching a *timed* search is not only a speed-up. A search given four seconds
finds what four seconds of one particular machine reaches, so recomputing it
elsewhere can legitimately return a different (still honest) lower bound and
move a plotted circle. Recording the value pins the published figure to the run
that produced it.

Delete the file, or pass `--refresh`, to recompute every entry from scratch;
that is the check that the file is still telling the truth. The fingerprint
stored beside the values covers the program above its chapter 4 banner, which is
everything `solve` runs, so editing the plotting code below does not raise a
false alarm. A mismatch is reported and the values are reused, since whether it
matters is a judgement about what changed.

The test suite needs no third-party test runner: it uses the standard library
`unittest`. If you do have `pytest` installed, `pytest tests` discovers the same
tests.

To solve a specific case, import `solve` and call it, for example:

```python
from erdos915_unified import solve
solve(6, 3, directed=True, simple=False, exhaustive=True)  # directed multigraph value
solve(16, 3, directed=True, exhaustive=False) # discover a dense example (lower bound)
solve(7, 2, hypergraph=True, r=3)             # the hypergraph model
```

## The honesty contract

| Computational route | What it gives you |
|-----------------------|-------------------|
| connectivity checker  | **exact** local connectivity (Menger / max-flow) |
| cut-counting solver check | a finite solver result and primal witness, with no independently replayable certificate emitted |
| temperature search | a **discovered** construction, hence only a **lower** bound, never a proof of optimality |
| random-model sampling | an **estimate** over random samples, never a proof |

The search proposes. The certifier and the hand proofs dispose.

## Which output feeds which figure

The thesis is three chapters: (1) The Problem and Its Base Cases, (2) Certifying
and Discovering Bounds by Machine, and (3) Synthesis, Results, and Open Problems.
`make_figures.py` writes every figure below except
`figures/rediscovery_table.tex`, which is a small hand-kept LaTeX table of
`solve(...)` discovery runs at fixed seeds. Its header records how each row
was produced; rerun those calls to check it.

| Figure | Thesis chapter |
|--------|----------------|
| `figures/edge_vertex_divergence.png` | the m=5 divergence (Ch.1) |
| `figures/edge_vertex_sampling.png` | edge vs vertex disjointness in G(n,p) (offcut only) |
| `figures/complexity_growth.png` | the enumeration explosion in n, m, direction (Ch.2) |
| `figures/temperature_trace.png` | a cooling run (Ch.2) |
| `figures/sensitivity_mixed.png` | load-bearing edges by sensitivity (Ch.2) |
| `figures/rediscovery_table.tex` | validation-by-rediscovery table (Ch.2), hand-kept, not generated |
| `figures/variant_bounds_m3_graphs.png` | proved / conjectured / guessed, the eight graph-model variants at m = 3 (Ch.2) |
| `figures/variant_bounds_m3_hypergraphs.png` | the eight hypergraph-model variants at m = 3 (Ch.2) |
| `figures/variant_bounds_m6_graphs.png` | the same graph-model half at m = 6 (Ch.2) |
| `figures/variant_bounds_m6_hypergraphs.png` | the same hypergraph-model half at m = 6 (Ch.2) |
| `figures/machine_values.json` | the cached `solve` results those four grids plot (not a figure) |
| `figures/directed_crossover.png` | hub/bipartite crossover (Ch.2) |
| `figures/scatter_lambda_edges.png` | the extremal envelope over all graphs (Ch.2) |
| `figures/variant_surface_3d.png` | the bound surface over the (n, m) grid (offcut only) |
| `figures/extremal_graphs_gallery.png` | the named extremal families (offcut only) |
| `figures/pair_conn_dist.png` | pooled per-pair connectivity distributions (offcut only) |
| `figures/edges_dist.png` | edge-count distributions (offcut only) |
| `figures/conn_dist_m6.png` | per-graph connectivity distributions at m = 6 (offcut only) |
| `figures/threshold_3d.png` | the threshold across densities, three variants (offcut only) |
| `figures/trace_*.png` | per-variant search traces (offcut only, all five) |
| `figures/sa_vs_tabu_convergence.pdf` | SA against tabu, wall-clock timed (offcut only) |

**Offcut only** means the figure is no longer referenced from `main.tex`. It is
still generated, still checked, and still rendered, but by `offcuts.tex` (the
record of what the shortening pass removed) rather than by the thesis. None of
these files may be deleted while that document exists.

The solver records (`figures/certificate_log.txt`, `figures/basecase_search_log.txt`,
`figures/basecase_search_vertex_log.txt`) were produced by the named finite
routines on the directed cases; the appendix now tabulates them rather than
printing them verbatim. Randomised searches use fixed seeds. The SA-versus-tabu
timings are the documented exception, because their stopping rule is wall-clock.

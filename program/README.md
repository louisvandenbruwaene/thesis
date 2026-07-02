# erdos915: the unified program

One main Python file, `erdos915_unified.py`, models every variant of Erdős
Problem 915, measures connectivity exactly, certifies upper bounds for small
sizes, and searches for extremal graphs with a temperature-guided walk. It is
written to be read top to bottom: clear names, docstrings everywhere, and a
strict separation between what is *measured*, what is *proved*, and what is
merely *discovered*. An optional C helper accelerates small hot paths, but the
Python implementation is the correctness path.

There is one solver. Whatever the question, you call `solve(...)`: it picks the
right method for the case (brute-force enumeration, the pruned exhaustive search,
the cut-counting certifier, or the temperature search) and labels its answer
honestly as exact, an upper bound, or a lower bound. You never run a different
program for a different case.

## Layout

```
program/
  erdos915_unified.py   the whole program: the model, the connectivity checker,
                        Gomory-Hu, the cut-counting certifier, sensitivity, the
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
One more library backs the certifier and two are optional:

- `pulp` backs the MILP certifier (`prove_directed_multigraph` and
  `prove_integral_arc_bound`): one solver-agnostic cut-counting model that runs on
  CBC (bundled with `pulp`) by default and on Gurobi by passing `use_gurobi=True`.
  The certifier raises a clear message if it is called without `pulp`.
- `matplotlib` is needed only to render the figures (`make_figures.py` and the
  `plot_*` routines). Without it everything else still runs.
- `networkx` is needed only for the Gomory-Hu tree, a single figure/analysis
  helper. `gomory_hu_tree` raises a clear message if it is called without it.

The program runs without a build step; `bash build_fast.sh` optionally compiles
`_erdos_fast.so` to accelerate small hot-path searches.

One optional extra: `enumerate_extremal_directed_multigraphs_via_generation` (the
sound, generation-based directed-multigraph enumerator that follows J. Goedgebeur's
`geng` suggestion) shells out to nauty's `geng`. It decorates the supports in
parallel across processor cores (each support is independent), which is what makes
the open `n = 7` classification practical on a multi-core machine; pass
`parallel=False` for a single-process run. Everything else, including the
self-test, the figures, and the test suite, runs without `geng`; the one unit test
that exercises it skips automatically when `geng` is not on `PATH`.

## How to run

From this `program/` directory:

```bash
python erdos915_unified.py            # run the built-in invariant self-check
python -m unittest discover -s tests  # run the full test suite (88 tests, stdlib only)
python make_figures.py                # regenerate the figures in ../figures/
```

The test suite needs no third-party test runner: it uses the standard library
`unittest`. If you do have `pytest` installed, `pytest tests` discovers the same
tests.

To solve a specific case, import `solve` and call it, for example:

```python
from erdos915_unified import solve
solve(6, 3, directed=True, exhaustive=True)   # prove the directed multigraph value
solve(16, 3, directed=True, exhaustive=False) # discover a dense example (lower bound)
solve(7, 2, hypergraph=True, r=3)             # the hypergraph model
```

## The honesty contract

| Method inside `solve` | What it gives you |
|-----------------------|-------------------|
| connectivity checker  | **exact** local connectivity (Menger / max-flow) |
| cut-counting certifier | a **proved** upper bound for a fixed `n` when it reports OPTIMAL with zero gap |
| temperature search | a **discovered** construction, hence only a **lower** bound, never a proof of optimality |
| random-model sampling | an **estimate** over random samples, never a proof |

The search proposes; the certifier and the hand proofs dispose.

## Which output feeds which figure

The thesis is four chapters: (1) The Problem and Its Base Cases, (2) Certifying
Bounds by Machine, (3) Discovering Bounds by Search, (4) Synthesis, Results, and
Open Problems. `make_figures.py` writes every figure below.

| Figure | Thesis chapter |
|--------|----------------|
| `figures/edge_vertex_divergence.png` | the m=5 divergence (Ch.1) |
| `figures/edge_vertex_sampling.png` | edge vs vertex disjointness in G(n,p) (Ch.1) |
| `figures/complexity_growth.png` | the enumeration explosion in n, m, direction (Ch.3) |
| `figures/temperature_trace.png` | a cooling run (Ch.3) |
| `figures/sensitivity_mixed.png` | load-bearing edges by sensitivity (Ch.3) |
| `figures/rediscovery_table.tex` | validation-by-rediscovery table (Ch.3) |
| `figures/variant_bounds_m3.png`, `..._m6.png` | proved / conjectured / guessed, all twelve variants (Ch.3) |
| `figures/directed_crossover.png` | hub/bipartite crossover (Ch.4) |
| `figures/scatter_lambda_edges.png` | the extremal envelope over all graphs (Ch.4) |
| `figures/pair_conn_dist.png` | pooled per-pair connectivity distributions, all variants, mid-range split (Ch.4) |
| `figures/edges_dist.png` | edge-count distributions, all variants, mid-range split (Ch.4) |
| `figures/variant_surface_3d.png` | the bound surface over the (n, m) grid (Ch.4) |
| `figures/conn_dist_m6.png` | per-graph connectivity distributions, all variants (App. B) |
| `figures/threshold_3d.png` | the threshold across densities, three variants (App. B) |
| `figures/trace_*.png` | per-variant search traces (App. B) |

The solver transcripts in the appendix (`figures/certificate_log.txt`,
`figures/basecase_search_log.txt`) were produced by `solve(...)` on the directed
cases. All randomised searches use fixed seeds, so every figure is reproducible.

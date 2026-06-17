# Erdős Problem 915 across twelve variants

Master's thesis of **Louis Vandenbruwaene** (KU Leuven), supervised by **Stijn Cambie**.

The thesis studies an extremal question of Erdős — *how many edges (or arcs) can a
graph on `n` vertices hold if no pair of vertices is joined by `m` independent
routes?* — and follows it across **twelve variants**: three models (simple graphs,
multigraphs, `r`-uniform hypergraphs) × two directions (undirected / directed) × two
separations (edge-disjoint / internally vertex-disjoint). It pairs hand proofs with a
single unified program that measures connectivity exactly, certifies small-case upper
bounds, and discovers dense constructions.

The built paper is **[`main.pdf`](main.pdf)**.

## What's here

```
chapters/             the thesis text (ch1 base cases, ch2 certify, ch3 discover,
                      ch4 synthesis, app_proofs appendix)
main.tex, preamble.tex, ref.bib, kulakreport.cls, *.pdf/*.png   LaTeX sources + logos
figures/              all figures: matplotlib PNGs + their data caches
program/
  erdos915_unified.py one file: the model, exact max-flow checker, cut-counting
                      certifier, simulated-annealing search, and the proof-support
                      solvers. ALL runnable code lives here (project rule).
  make_figures.py     regenerates every figure from the program (fixed seeds)
  tests/              unit tests
popularising_summary/ lay summary
CLAUDE.md, TASKS.md   operating notes and the prioritized open-problem queue
main.pdf              the compiled thesis
```

## Build

LaTeX (needs a TeX Live with `latexmk`):

```bash
latexmk -pdf main.tex
```

Figures (needs Python 3 with numpy, scipy, networkx, matplotlib):

```bash
cd program && python3 make_figures.py     # writes into ../figures/
```

Every randomized search uses a fixed seed, so figures are reproducible.

## The honesty contract

The search **proves nothing** — it only exhibits concrete graphs, hence *lower
bounds*. A value is called settled only when a hand proof or the cut-counting
certifier supplies the matching *upper bound*. Every general statement in the thesis
rests on a hand proof or a cited theorem; computations are supporting evidence.

## Where to continue

The open problems are stated precisely in **ch4 (`chapters/ch4_synthesis.tex`,
"Open problems")** and tracked in **`TASKS.md`**. The headline targets:

- **The backward-arc lemma** — proving an extremal non-hub digraph has no arc from `B`
  to `A` would turn the directed-arc conjecture into a theorem for all `m ≥ 3`.
- **The hypergraph vertex problem at `m ≥ 4`** — needs a 4-connectivity analogue of the
  triconnected (Tutte/SPQR) decomposition used for `m = 3`.
- **Two finite `n = 7` facts** that close the directed-multigraph problem at `m = 3`:
  `L₃ᵈⁱʳ(7) = 24`, and the classification of its 24-arc extremisers. The enumerator
  now streams canonical forms (RAM bounded by isomorphism-class count); the remaining
  bottleneck is DFS time — see `TASKS.md` for the memory-capped run command and the
  Jan Goedgebeur `geng`+`directg`/`watercluster2` generation-pipeline follow-up.

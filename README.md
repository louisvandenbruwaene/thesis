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
  erdos915_unified.py one Python driver: the model, exact max-flow checker,
                      cut-counting certifier, simulated-annealing search, and
                      the proof-support solvers.
  _erdos_fast.c       optional C hot-path helper, built as _erdos_fast.so
                      by build_fast.sh; correctness does not depend on it.
  make_figures.py     regenerates every figure from the program (fixed seeds)
  tests/              unit tests
popularising_summary/ lay summary
research_notes/       conjectures and supposed proofs NOT in the thesis: too
                      specific or unfinished for the text, kept for future work
                      (AI or human). Self-contained, with reproducible scripts.
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

- **The extremal decomposition** — proving an extremal non-hub digraph splits as `A ∪ B`
  with `A → B` complete, no arc inside `A`, and no arc from `B` back to `A` would turn
  the directed-arc conjecture into a theorem for all `m ≥ 3`. The backward-arc clause is
  the hardest quarter of it, not the whole. Unconditionally the leading constant is
  already settled: `ℓₘᵈⁱʳ(n) = n²/4 + O(n^{3/2})`.
- **The directed *vertex* problem at `m ≥ 3`** — a separate question, not a corollary of
  the arc one. Whitney's `κ ≤ λ` makes the vertex-feasible family the larger of the two,
  so an arc upper bound does not restrict it. Proved equal at `m = 2` only by re-running
  the induction and its base cases under the vertex test.
- **The hypergraph vertex problem at `m ≥ 4`** — needs a 4-connectivity analogue of the
  triconnected (Tutte/SPQR) decomposition used for `m = 3`.
- **One finite `n = 7` fact** that closes the directed-multigraph problem at `m = 3`:
  the value `L₃ᵈⁱʳ(7) = 24` (fact (a)). Its companion, the classification of the
  24-arc extremisers (fact (b)), is already proved by the sound `geng`-based
  generation enumerator (~7 h on 10 cores; exactly `2B(3,4)`, `2B(4,3)`, and the
  doubled path `P₇`). Fact (a) needs either the same enumerator uncapped at
  target 25 (long run, command in `TASKS.md`) or the Gurobi MILP route.

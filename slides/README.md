# Slides

Two Beamer decks for *Erdős Problem 915, from Proof to Search*. Both reuse the
thesis house style (`../shared/colors.tex` and `../shared/tikz-styles.tex`) so
the colours and the graph vocabulary match the document.

| File | Length | Frames | Character |
|---|---|---|---|
| `talk_10.tex` | 10 minutes | 10 | figure-led, one frame per minute |
| `talk_60.tex` | 1 hour | 48 | figure-led, seven parts plus backup |

## Build

```bash
cd slides
latexmk -pdf talk_10.tex     # the ten-minute version
latexmk -pdf talk_60.tex     # the hour version
```

## The one rule

**Every picture and every formula is one the thesis main text carries today.**
A deck never invents a figure and never quotes a result the body does not
state. Concretely there are two sources:

1. **Rendered files in `../figures/`.** Only the ten a chapter actually
   `\includegraphics` or `\input`s: `edge_vertex_divergence.png`,
   `directed_crossover.png`, `complexity_growth.png`, the four
   `variant_bounds_m{3,6}_{graphs,hypergraphs}.png` grids,
   `rediscovery_table.tex`, `generating_benchmark_table.tex` and
   `variant_table_all.tex`. The many other files in `../figures/` are leftovers
   from earlier drafts and are deliberately **not** used.
2. **TikZ pictures in `thesis-figures.tex`.** Nine drawings copied from the
   chapters, each with a header comment naming its source file and `\label`:
   `fig:menger`, `fig:edge-vs-vertex`, `fig:simple-digraph-m2`,
   `fig:hyper-star` (ch1), `fig:spine`, `fig:vertex-split`,
   `fig:rediscovery-gallery` (ch2), `fig:augmented-wall`,
   `fig:variant-tree-status` (ch3). That file also carries the thesis's
   canonical graph vocabulary (`gvertex`, `gdir`, `grA`, the `vt*` variant-tree
   styles, the four `regime*` tints), copied from `preamble.tex`, because the
   decks load only the two `shared/` files.

**These copies are the drift risk.** If a chapter changes or drops one of those
nine figures, or if a chapter stops including one of the ten files above, the
matching frame has to be updated by hand. The two checks are one line each:

```bash
# every rendered asset a deck pulls in is still in the main text
grep -ohE "\{[a-z_0-9]+\.png\}|\.\./figures/[a-z_0-9]+\.tex" talk_*.tex \
  | tr -d '{}' | sed 's|\.\./figures/||' | sort -u \
  | while read f; do grep -qF "$f" ../chapters/ch{1_basecases,2_machine,3_synthesis}.tex \
      || echo "GONE FROM MAIN TEXT: $f"; done

# every copied TikZ figure still has its label in the main text
grep -oE "fig:[a-z0-9-]+" thesis-figures.tex | sort -u \
  | while read l; do grep -q "label{$l}" ../chapters/ch*.tex || echo "GONE: $l"; done
```

## Theme and frame builders

`thesis-beamer.tex` holds the Beamer theme, the notation shorthands, three
tables lifted from the thesis, and the frame builders. Editing a deck usually
means adding one builder line.

| Builder | Use |
|---|---|
| `\figframe{title}{file}{line}` | a rendered figure, height-capped |
| `\figframetall{title}{file}{line}` | the near-square multi-panel grids |
| `\figframewide{title}{file}{line}` | a panel of ratio above 2 |
| `\tikzframe{title}{\figmacro}{line}` | a TikZ picture, scaled to the text width and capped in height |
| `\tikzframescaled{title}{\figmacro}{line}{frac}` | the same at a chosen width fraction, for a small picture |
| `\sectionframe{part}{title}` | a plain divider |
| `\titleframe{subtitle}` | the shared title frame |

## Tables

The three tables that live in `thesis-beamer.tex` are thesis tables with their
cross references replaced by short words:

- `\sixteentable` is `tab:summary` (`ch3_synthesis.tex`). Its status chips are
  the four regimes of `fig:variant-tree-status`: **PROVED** (a closed form for
  every *n* and *m*), **RANGE** (proved for a range of *m*, open beyond it),
  **CONJ** (a conjectured formula with a proved lower bound and the small cases
  exhausted), and **LEADING TERM** (the *n²* term is a theorem, the exact value
  is not). **Keep it in step with `tab:summary` by hand.**
- `\notationtable` is `tab:notation` (`ch1_basecases.tex`).
- `\openproblemstable` is `tab:open-problems` (`ch3_synthesis.tex`).

`rediscovery_table.tex`, `generating_benchmark_table.tex` and
`variant_table_all.tex` are `\input` straight from `../figures/`, so those three
need no maintenance at all.

## The two decks

The ten-minute version is the spine on its own:

1. Title
2. The question, and Mader's bound
3. `fig:variant-tree-status`, four models, two directions, two separations
4. `edge_vertex_divergence.png`, edge and vertex part company at *m* = 5
5. `directed_crossover.png`, one-way traffic buys a quadratic
6. `complexity_growth.png`, why a machine is needed
7. `rediscovery_table.tex`, what the machine is allowed to claim
8. `variant_bounds_m3_graphs.png`, the eight graph-model variants at *m* = 3
9. What is new here
10. What is left

The hour version expands the same spine into seven parts (the question, the
sixteen variants, the hand proofs, the directed turn, why a machine, discovery,
the landscape and the results), then closes with backup frames for the question
round: the sixteen variants as numbers, the orientation conventions for a
directed hyperedge, and the stated limits of the program.

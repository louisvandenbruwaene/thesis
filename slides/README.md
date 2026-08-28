# Slides

Two Beamer decks for *Erdős Problem 915, from Proof to Search*. Both
reuse the thesis house style (`../shared/colors.tex` and
`../shared/tikz-styles.tex`) so the colours and the graph vocabulary match the
document.

| File | Length | Frames | Character |
|---|---|---|---|
| `talk_10.tex` | 10 minutes | 10 | figure-led, one frame per minute |
| `talk_60.tex` | 1 hour | 42 | figure-led, seven parts plus backup |

## Build

```bash
cd slides
latexmk -pdf talk_10.tex     # the ten-minute version
latexmk -pdf talk_60.tex     # the hour version
```

## The two figure-led decks

`talk_10.tex` and `talk_60.tex` share one theme file, `thesis-beamer.tex`, which
holds the Beamer theme, the notation shorthands, the twelve-variant table, and
four frame builders (`\figframe`, `\figframetall`, `\figframewide`,
`\sectionframe`). Editing a deck usually means adding one `\figframe` line.

Both decks obey one rule: **every picture is a figure the thesis already
produced**, taken from `../figures/`. Neither deck draws a figure of its own,
and neither needs `make_figures.py` to be re-run. Text is deliberately thin, one
title and one reading line per figure.

The hour version uses all 21 figure files plus `rediscovery_table.tex`. The
ten-minute version uses five of them, chosen to carry the argument on their own:

1. Title
2. The question, and Mader's theorem
3. `edge_vertex_divergence.png` — the edge and vertex problems part at *m* = 5
4. `directed_crossover.png` — one-way traffic buys a quadratic
5. `complexity_growth.png` — why a machine is needed
6. `temperature_trace.png` — what the machine does
7. `variant_bounds_m3.png` — all twelve variants at once
8. The twelve-variant status table
9. What is new here
10. What is left

The hour version expands the same spine into seven parts (the question, the
twelve variants, the hand proofs, the directed turn, why a machine, discovery,
the landscape and the results), then closes with backup frames for the question
round: the connectivity distribution at *m* = 6, the three remaining search
traces, the orientation-model table, and the multigraph vertex table.

## Tables

The tables in the two figure-led decks are the thesis tables with their cross
references replaced by short words, so they read on a slide. They are
`tab:summary` (twelve variants), `tab:sa-vs-tabu`, `tab:orientation`,
`tab:multi-vertex`, and the rediscovery table, which is `\input` straight from
`../figures/rediscovery_table.tex`.

`\twelvetable` lives in `thesis-beamer.tex`, not in either deck, so it must be
kept in step with `tab:summary` in `chapters/ch3_synthesis.tex` by hand. Its
status chips distinguish PROVED, CITED, BOUND, CONJ, and LEADING TERM. BOUND
marks a proved upper bound whose stated construction does not attain it for
every parameter; LEADING TERM marks the amber case where the `n^2` term is a
theorem but the exact value is not.

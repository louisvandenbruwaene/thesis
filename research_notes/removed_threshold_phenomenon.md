# Removed from the thesis: the threshold-universality phenomenon (old Figure 4.2)

Removed from `chapters/ch3_synthesis.tex` on 2026-06-20 at the author's request
("not a fan of the whole story behind Figure 4.2"). This note preserves the
prose, the figure caption, and the recipe to restore it, in case it should go
back in.

What was removed:

- The third of the "three principal phenomena" (the threshold-universality
  story). The section is now "Two principal phenomena".
- The 2-D figure `fig:threshold` (`figures/degree_threshold.png`), the old
  Figure 4.2.
- A transient 12-panel variant grid `fig:threshold-variant-grid`
  (`figures/threshold_variant_grid.png`) that briefly replaced the
  random-sampling distribution grid; rejected and not intended to return.

What was KEPT:

- The 3-D threshold histogram `fig:threshold-3d`
  (`figures/threshold_3d.png`) stays as a standalone appendix figure
  (`app_gallery.tex`, section `app:m6`), decoupled from the removed Figure 4.2
  and now referencing `thm:gnp-threshold` directly.
- `thm:gnp-threshold` in Chapter 1 (the proved appearance threshold for simple
  `G(n,p)`) is untouched.
- The generators in `program/erdos915_unified.py`:
  `plot_degree_threshold`, the unified random sampler (`sample_random_graph`,
  `sample_random_multigraph`, `sample_random_hypergraph`, `_sample_variant`,
  `_p_for_target_degree`, `_mean_binding_degree`, `_measure_variant`,
  `_VARIANT_SAMPLE_CONFIGS`). `plot_sampled_variant_grid` and
  `plot_threshold_variant_grid` were deleted; both are recoverable from git
  history if ever wanted.

## Restore recipe

1. In `program/make_figures.py`, re-add the import of `plot_degree_threshold`
   and a call:

   ```python
   plot_degree_threshold(
       FIGURES / "degree_threshold.png", n=12, m=4, alpha=0.5, trials=70, seed=7)
   ```

2. Re-insert the prose and figure into `chapters/ch3_synthesis.tex`, restore the
   section title to "Three principal phenomena" and the two "two"->"three"
   wordings (chapter intro "genuine surprises" and the phenomena lead-in).

## Removed prose (verbatim)

> The third is the universality of the threshold $p^* = m/n$, with one honest
> asterisk. \Cref{ch:basecases} proves the appearance threshold $p^* = m/n$ for
> simple $G(n, p)$ (\Cref{thm:gnp-threshold}), and its mechanism is a degree
> count: below threshold the maximum degree stays under $m$, so the degree bound
> caps every local connectivity, and above it Mader's bound forces a high pair
> into existence. That mechanism does not care which model it runs on, so the
> natural general statement is that the forbidden configuration appears once the
> \emph{expected degree} crosses $m$, of which $p^* = m/n$ is merely the
> simple-graph face, since there $\mathbb E[\deg] = p(n-1)$. To put this to all
> twelve variants at once we extend $G(n,p)$ by a single rule: every cell (a
> pair, an ordered pair, or an $r$-set) carries an independent weight,
> Bernoulli$(p)$ for simple graphs and hypergraphs, and for multigraphs a
> \emph{hurdle-geometric} weight that is empty with probability $1-p$ and
> otherwise $1 + \mathrm{Geometric}(\alpha)$ parallel copies, so the multiplicity
> decays geometrically (we use $\alpha = \tfrac{1}{2}$ throughout) and
> $\alpha = 0$ recovers $G(n,p)$ exactly. For multigraph panels, multiplicities
> are capped at $m-1$ so that a single fat edge cannot trivially breach the
> connectivity ceiling. For simple-graph and hypergraph panels no cap is needed,
> since those models already admit at most one copy per cell or hyperedge.
>
> \Cref{fig:threshold} samples all six generative shapes and plots, against the
> measured mean degree in units of $m$, the chance that a sample already holds a
> pair of binding connectivity at least $m$. The universality is real but
> \emph{asymptotic}. The degree argument is model-free only in the regime
> $m/\ln n \to \infty$. At the fixed small $m$ a computation can reach, the
> curves are visibly \emph{ordered} rather than coincident. The ordering, from
> cheapest to most expensive in mean degree required to force a high pair, is:
> directed multigraph, directed simple, undirected simple, undirected
> multigraph, undirected hypergraph, directed hypergraph. The directed
> multigraph crosses first because parallel edges concentrate connectivity into a
> few pairs without spreading degree evenly. The undirected multigraph lands
> further right than the simple cases because a lower inclusion probability
> (needed to keep mean degree fixed) leaves many pairs absent, making the
> minimum-degree bound harder to satisfy. The directed hypergraph needs the most
> degree because each hyperedge serves only one Berge route at a time. The
> vertical line is the asymptotic threshold, degree $= m$, and the spread of
> crossings around it is exactly the finite-$m$ gap \Cref{thm:gnp-threshold}
> already disclaims. The collapse onto one density is a statement about the
> limit, not about any size we can sample.

## Removed figure caption (fig:threshold, degree_threshold.png)

> The appearance threshold across all six generative models, read against
> expected degree ($n = 12$, $m = 4$, multigraph panels use the hurdle-geometric
> model with $\alpha = \tfrac{1}{2}$, multiplicities capped at $m-1$). Each curve
> samples one model (simple, multigraph, or $3$-uniform hypergraph, each
> undirected and directed) and plots the probability that a sample already
> contains a pair of binding connectivity at least $m$ against its \emph{measured}
> mean binding degree, in units of $m$. The vertical line is the asymptotic
> threshold degree $= m$ of \Cref{thm:gnp-threshold}. At this finite $m$ the
> curves form a strict six-way ordering, not a coincident band: multigraph
> directed crosses first (parallel edges concentrate connectivity into a few
> pairs), then simple directed, then simple undirected, then multigraph
> undirected (lower inclusion probability offsets the per-pair multiplicity
> gain), then $3$-uniform hypergraph undirected, and finally $3$-uniform
> hypergraph directed last (each Berge route consumes an entire hyperedge, so
> connectivity is hardest to force). The model-free collapse onto one threshold
> is the $m/\ln n \to \infty$ limit. The spread here is the finite-$m$ gap.

The rendered PNGs `degree_threshold.png` and `threshold_variant_grid.png` are
preserved alongside this note in `removed_threshold_figures/`.

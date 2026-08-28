
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

VERIFY: 115 pp, 0 overfull, 4 underfull, 0 undefined, 0 warnings. Full suite green
with the stale skip gone. Both grids regenerated from the gated code.

# Research notes: conjectures and supposed proofs (NOT part of the thesis)

This folder is a working archive for results, conjectures, and proof attempts
that grew out of the thesis but are **deliberately not in it** -- they are too
specific, too long, or too unfinished to belong in the main text, yet they are
worth keeping for whoever (AI or human) continues the work.

## Ground rules

- **Nothing here is claimed in the thesis.** The thesis's honesty contract still
  holds: a statement enters the thesis text only after a proof-check. Items here
  are flagged PROVED / VERIFIED / CONJECTURE / OPEN explicitly.
- Every computational claim is backed by a script in `scripts/`. The PROOF
  scripts are self-contained (standard-library Python + a hand-rolled
  unit-capacity max-flow). The two CROSS-CHECK scripts (`nauty_pipeline.py`,
  `tabu_vs_sa.py`) are the exception by design: they import the thesis program
  and/or call nauty, because their whole job is to check the program and the
  tools against each other. Run any of them with
  `python3 research_notes/scripts/<name>.py`.
- Keep the formal statement and its status at the top of each entry; put the
  reasoning and the open residue below.

## Contents

### Directed simple-digraph arc problem at `m = 3` (`conj:dir-arc`)
A line of attack on the thesis's flagship open problem -- proving the quadratic
branch of `conj:dir-arc` for `m >= 3`. It reduced the whole `m = 3` quadratic
upper bound to one hypothesis (H) about sources. **As of 2026-06-30, (H) is
FALSE** (an explicit infinite family of extremisers refutes it), so the reduction
does not close the problem. The VALUE conjecture is unharmed; the characterisation
is wrong. Details and what survives are in section 0 of the reduction note.

- [`directed_arc_m3_reduction.md`](directed_arc_m3_reduction.md) -- the
  min-degree-deletion reduction and the conditional structure theorem. Section 0
  now records that **(H) is FALSE**; the rest is kept for the record.
- [`directed_arc_m3_extremisers.md`](directed_arc_m3_extremisers.md) -- the
  augmented-bipartite family and the attachment refutation, both SUPERSEDED: the
  family is not the complete extremal set and the refutation rested on (H).

Scripts: `h_counterexample.py` (the (H) refutation: the `n=9` witness and the
infinite family, self-contained + cross-checked against the program),
`h_violation_search.py` (the fixed-arc-count search that maximised max R-in-degree
and found the `n=9` violation), `attach_check.py`, `attach_check_all_perms.py`
(now historical, the attachment refutation), `characterisation_checks.py` (arc
partition, the source lemma, the conditional bound, family feasibility),
`odd_extremiser_search.py` (a search probe; weak), `lemma_check.py` (the
self-similarity lemma, still true), `probe_overshoot.py` (the recursion
overshoots Q(n)), `coupling_inequality.py` (the summed-coupling inequality and the
counting-is-insufficient result). The 2026-06-30 scripts are self-contained.

### Fact (a) by the delta-split route (IN PROGRESS 2026-07-04)
The last open statement of the m=3 directed multigraph problem, L_3^dir(7)=24,
reduced to two finite 6-vertex classifications (all feasible multigraphs with
exactly 19 and exactly 18 arcs) plus an attachment check. The route is proved
correct in both directions (a survivor would BE a counterexample), the
classifications are running, and the attachment half is implemented and
control-tested.

- [`fact_a_delta_split.md`](fact_a_delta_split.md) -- the delta-split lemma,
  the mixed-pair filter lemma, the conditional theorem, and the verification
  ladder.

Scripts: `fact_a_attachment_check.py` (self-contained capped Edmonds-Karp,
`--selftest` controls, `--crosscheck` against the thesis checker).

### Closing the m=4 odd-uniqueness hole (PROVED here, 2026-07-04)
The counting hole of rem:odd-step-roadmap is closed for m=4 at every level
n=2k+1, k>=5: a new deficiency-1 attachment corollary (exact structure of a
vertex attached to (m-1)B_{p,q} one arc below the attachment-lemma cap) plus
a tight-pair-deletion analysis force a vertex of degree exactly 3k, so
value+uniqueness propagate at m=4 like at m=3, down to finite bases at
n=7..10. The same corollary kills the m=5 value escape (j=1), so thm:odd-step
extends to m=5 in value. m=5 uniqueness still leaks (excess outgrows the
min-degree count), documented precisely.

- [`m4_odd_uniqueness_closed.md`](m4_odd_uniqueness_closed.md) -- Lemma E
  (even value free), Corollary D1 (deficiency-1 attachment), Lemma T (tight
  pairs), Theorem U4, the m=4 chain consequence, the m=5 value result and its
  honest residue.

Scripts: `deficiency_attachment_check.py` (exhaustive corollary check at five
(m;p,q) sets, all contradiction structures infeasible, counting identities).

### Directed multigraph linear branch: the saturated attachment lemma
A PROVED lemma (2026-07-02): attaching one vertex to any everywhere-saturated
multigraph (in particular to any doubled bidirected tree at multiplicity m-1)
caps the new degree at 2(m-1), with equality exactly when the attachment grows
the tree by one full-multiplicity leaf. It is the linear-branch analogue of the
thesis's lem:attachment (bipartite base), shortens the n=8 seam argument and
the degree-4 case of fact (b), and reduces the d(v)=5 case of fact (a) to the
uncapped n=6 classification.

- [`saturated_attachment_lemma.md`](saturated_attachment_lemma.md) -- statement,
  full proof, consequences, and what still blocks fact (a) along this route.

Scripts: `saturated_attachment_check.py` (exhaustive verification on all nine
doubled trees with 5 and 6 vertices at m=3; imports the thesis program for the
capped feasibility predicate).

### Jan Goedgebeur's follow-up: the nauty pipeline and tabu search
Cross-checks (not new mathematics) of the two P2 items from Jan's email, run
once nauty became available locally. The geng+directg/watercluster2 pipeline
reproduces the program's digraph counts (= OEIS A000273) and its simple-directed
extremal values; watercluster2 is ~15x faster than directg; and a
support-from-nauty multigraph hybrid reproduces the directed-multigraph
enumeration ~17x faster than the thesis DFS at n=5. Tabu search ties the thesis
annealer on the easy cases and clearly beats it on the harder directed ones
(reaching the L_3^dir(7)=24 extremiser where annealing stalls).

- [`jan_followup_nauty_and_tabu.md`](jan_followup_nauty_and_tabu.md) -- results,
  tables, caveats, and the concrete next step for an ENUM (b) n=7 cross-check.

Scripts: `nauty_pipeline.py` (counts / extremal / timing / multigraph hybrid),
`tabu_vs_sa.py` (tabu vs simulated annealing benchmark). Both import the thesis
program; the pipeline also needs nauty on PATH.

### Case 2 of thm:dir-arc-linear-error is already tight (PROVED negative result, 2026-07-30)
The remark after `thm:dir-arc-linear-error` suggests that Case 2's constant
`4(m-1)` might be cuttable towards the conjectured `(m-2)/2` by exploiting that
the conjectured extremiser has `min(d+,d-)=0` on a whole side. This note proves
that specific idea does not work: Case 2's bound is the exact maximum
extractable from the one inequality it uses (the aggregate two-step-route
budget plus the per-vertex degree floor), via a concentration/exchange
argument. Closing the gap needs a genuinely new inequality, not a sharper use
of the existing one; a candidate direction (interference among the `O(m)`
near-balanced vertices themselves) is named but not attempted.

- [`case2_tightness.md`](case2_tightness.md) -- the reformulation, the
  concentration lemma, the exact asymptotic match to `4(m-1)(n-1)`, and what
  it rules out.

Scripts: `case2_tightness_check.py` (closed-form bang-bang value vs. an
independent nonlinear solver; self-contained, numpy + scipy only).

### conj:multi-vertex REFUTED for all m >= 5 (PROVED, 2026-07-31)
The thesis's own conjecture (added hours earlier the same day) that a
thickened tree becomes optimal for the multigraph vertex problem under the
alternate convention once `n >= m+2` is false for every `m >= 5`. Chaining
thickened `K_r` cliques (optimal block size `r ~ m/2`) through single bridge
vertices beats the tree by a margin that grows LINEARLY in `n`, and the true
growth rate in `m` is `Theta(m^2)`, not `Theta(m)`. Proved by hand (a clean
cut-vertex feasibility argument, not just search) and cross-checked two
independent ways. Folded into the thesis as `thm:clique-chain-vertex`
(app_proofs.tex), replacing the withdrawn `conj:multi-vertex`.

- [`multi_vertex_clique_chains.md`](multi_vertex_clique_chains.md) -- the
  construction, the exact multiplicity formula, the feasibility proof, the
  exact-optimal-r table, and what is still open (the exact value, since the
  construction is known not to be optimal).

Scripts: `multi_vertex_clique_check.py` (builds the chain, checks feasibility
via the thesis program's `exceeds_bound` AND a from-scratch networkx max-flow,
confirms the exact gain formula; self-contained modulo importing the program).

### The hypergraph vertex problem at m = 4 (2026-07-31)
Two findings. **PROVED:** the general formula
`k_m^(r)(n) = floor((m-1)(n-1)/(r-1))` cannot hold for all `m` and `r`, because
at `r = 2` this problem *is* the multigraph vertex problem of
`sec:multi-vertex-standard` (the measures coincide, proved), so
`thm:clique-chain-vertex` breaks it there for every `m >= 5` and `n >= 3`.
The live question is only whether `r >= 3` postpones the failure past `m = 4`.
**VERIFIED (no counterexample):** at `m = 4` the formula survives exhaustive
checking at eleven `(n,r)` pairs, both halves, far beyond the single
previously-known cell `k_4^(3)(5) = 6`.

- [`hyper_vertex_m4.md`](hyper_vertex_m4.md) -- the `r = 2` identification and
  its proof, the exact rank/hyperedge-count equivalence that makes the search
  a direct test of the missing bound, the `m = 4` table, and what is open.

Scripts: `hyper_vertex_m4_search.py` (self-contained, standard library only;
no-argument run does the `m = 4` sweep, `... 2` does the `r = 2` cross-check
which re-derives the clique-chain witness from a different search space).

### The two-step budget, and three results it unlocks (2026-08-12)
**PROVED, all three now in the thesis.** Isolating what
`thm:dir-arc-linear-error` actually uses (one cap on one family of routes, then
only degree counting) turns it into a lemma about any digraph obeying that cap
(`lem:two-step-budget`), and three different arguments supply the cap.
(1) The route family is internally vertex-disjoint as well as arc-disjoint, so
the **directed vertex** problem gets `k_m^dir(n) = n^2/4 + Theta_m(n)`
unconditionally, a row the thesis had listed as untouched by the arc case.
(2) The **directed hypergraph** constant is settled,
`(1+o(1))(m-1)n^2/(4(r-1))` under both separations, closing
`conj:dir-hyper-constant`: the named obstacle is paid rather than removed, at a
factor `r-1` that lands in the linear error term while a second, unrelated
factor `r-1` divides the leading one. (3) The **multigraph vertex** problem
gets its first upper bound, `K_m^multi(n) <= (m-1)k_m(n) < 2(m-1)^2 n`, via
Mader's density theorem, which turns the section's unearned claim that the
bouquet has "the right order" into a theorem, `Theta(m^2 n)` as `m -> infinity`
with `n/m -> infinity` (not uniformly for fixed small `n`).

- [`two_step_budget.md`](two_step_budget.md) -- the three derivations, why the
  vertex transfer is legitimate when Whitney runs the wrong way, why the two
  factors of `r-1` are different factors, and the questions that note originally
  left open. The general-orientation question was subsequently closed below.

Scripts: `two_step_budget_check.py` (self-contained, standard library only;
checks all three route families against `kappa` rather than `lambda`, and
reproves `k_3(4)=4`, `k_3(5)=6`, `k_4(5)=8` from scratch).

The general-orientation gap that note left open is now closed too, see the next
entry, and the multigraph constant it reports as 16 apart is now 11.66 apart,
see the one after.

### The general orientation model shares the constant (PROVED, 2026-08-14)
`thm:dir-hyper-constant` covers the forward model (one tail, many heads) and, by
reversal, the backward one, but its proof uses the single tail **twice**, once
for the hyperedges routes enter through and once for the ones they leave
through. With several tails both uses fail at once: two midpoints may leave
through one shared hyperedge, and from `r >= 4` a mixed hyperedge may be one
target's entrance and another's exit. The fix is not a second matching and not
the greedy independent set the earlier note guessed at. Take a **maximum** family
of two-step routes and ask what stopped it: every target it leaves unserved must
be blocked by a hyperedge already spent, and a hyperedge has only `r` vertices to
block with, counting tails and heads together. In the thesis as
`thm:dir-hyper-general-constant`; the orientation axis now collapses
asymptotically rather than only on the evidence.

- recorded inside [`two_step_budget.md`](two_step_budget.md), section 2, since
  it is the same argument's missing case rather than a separate topic.

Scripts: `general_orientation_check.py` (self-contained, standard library only;
checks the budget against exact `kappa`, the mechanism against a brute-force
MAXIMUM family rather than a greedy one, the assembled bound on grown feasible
instances, and deliberately adversarial worst cases).

### The multigraph vertex problem is a block problem (PROVED, 2026-08-14)
Recovering the `-sum(pi)` correction that `prop:multi-vertex-upper` discards
turns the objective into an exact closed form,
`sum over edges of (m - kappa_{G0}(u,v))` over the underlying simple graph. That
is a sum of **local** terms, and no route between adjacent vertices leaves their
block, so it is additive over blocks and the value is a knapsack over the best
`2`-connected block of each size. Consequences: exact values for all `n <= 8`,
`m <= 8` (in particular `K_5^multi(7) = 29`, against the bouquet's 27 and an
unfinished search's 28); from `m = 5` on, a single `2`-connected block beats
every split, so the bouquet is not the shape of the answer; and the winning
blocks are unbalanced bipartite rather than complete, which gives a better
construction and cuts the gap to the upper bound from 16 to `6+4sqrt2 ~ 11.66`.

- [`multi_vertex_blocks.md`](multi_vertex_blocks.md) -- the closed form, the
  block reduction, the exact table, the thickened `K_{s,t}` optimisation, and the
  open residue (the remaining constant, and that `g_m(b)/(b-1)` is still rising
  at `b=8`, so the table does not extrapolate).

Scripts: `multi_vertex_blocks.py` (needs nauty's `geng` and networkx; sweeps all
`2`-connected blocks, solves the knapsack, and cross-checks every cell the thesis
program can prove exhaustively).

### Extremal uniqueness on the quadratic branch (PROVED for n >= 2m, 2026-08-14)
`thm:dir-multi-full` settles the directed multigraph VALUE for every `n` and `m`,
and ch3 recorded the uniqueness question as untouched by it, since the
reachability-skeleton proof "never needs to know which digraph it is peeling
apart". That is true of the proof read forwards. Read BACKWARDS from equality the
same construction is rigid: the skeleton count is uniquely maximised at one value
of the component number, forcing the extremiser to be ACYCLIC, and the
triangle-freeness used only to apply Mantel's bound becomes Mantel's EQUALITY
case, pinning the skeleton to a balanced complete bipartite graph. A new
observation, that inclusion-minimality also makes the skeleton SHALLOW (no
directed path of three arcs), closes it: for `n >= max(8, 2m)` the extremiser is
unique, the balanced one-directional complete bipartite digraph at multiplicity
`m-1`.

- [`quadratic_branch_uniqueness.md`](quadratic_branch_uniqueness.md) -- the
  reframing, the shallowness lemma, the proof chain, the exact regularity that
  equality also forces, and the open range `n < 2m`.

Scripts: `quadratic_branch_uniqueness.py` (self-contained, standard library only;
enumerates extremisers outright using acyclicity plus exact regularity plus the
monotone-feasibility prune).

### The 1974 problem as a block problem (2026-08-14)
`k_m(n)`, the undirected vertex problem open since 1974, has the same block
structure as the multigraph variant: `k_m(n)` is a knapsack over the best
2-connected block of each size, so `c_m = lim k_m(n)/(n-1) = sup_b h_m(b)/(b-1)`.
That reproves `m <= 4` in two lines and identifies the (disproved)
Bollobas-Erdos conjecture as exactly the claim that `K_m` is the best block.
Exhaustive computation shows no block on `<= 9` vertices beats it, for every
`m <= 8`.

The reason that is not evidence for the conjecture is the useful part. The
Sorensen-Thomassen witness glues copies of `K_m - e` **in a cycle**, so it has no
cut vertex at all: it is a single 2-connected block, invisible to a block
decomposition, and the refinement needed is the triconnected (SPQR) one along
2-cuts, which this thesis already uses elsewhere. Its smallest member beating
the conjecture has 26 vertices at `m=5`, against the 9 exhaustion reaches. Also
records a degeneracy question that would halve the only known upper bound.

- [`simple_vertex_blocks.md`](simple_vertex_blocks.md) -- the state of the art
  read off the primary source, the reduction, the block table, the verified
  Sorensen-Thomassen recursion, and the degeneracy question.

Scripts: `simple_vertex_blocks.py` (block table via geng), `st_construction.py`
(rebuilds the Sorensen-Thomassen witness and checks counts, 2-connectivity and
feasibility), `vertex_min_degree.py` (the degeneracy search).

### Two external drafts on the directed problem (UNVERIFIED, arrived 2026-09-02)

Three files in [`external/`](external/), drafted with GPT and passed on by Stijn.
They are recorded as received. Neither has been proof-checked here, and the
second one is missing the program its proof depends on.

**1. The two-path bound (folded into the thesis as a citation).** A digraph with
`lambda^max <= m-1`, or with `kappa^max <= m-1`, has at most `m-1` directed
two-step routes between any ordered pair, so it contains no `P_{m,2}`, `m` such
routes with common endpoints. The Turan number for that family is a published
theorem of Huang and Lyu (Discrete Appl. Math. **388** (2026) 1-10,
doi:10.1016/j.dam.2026.02.043), and it turns the error term of
`thm:dir-arc-linear-error` and `thm:dir-vertex-linear-error` from
`4(m-1)(n-1)` into `(m-1)n + O_m(1)`, at the price of a threshold
`n >= N(m-1)` that is cubic in `m` (121 at `m=3`, 390 at `m=6`). The thesis
bound stays the uniform one, holds from `n = 2`, and is the one that carries
over to hypergraphs, which this does not. ch1 cites the paper in one sentence
where the linear coefficient is discussed. The formula `g(n,t)` and the journal
metadata were checked against the arXiv abstract (2406.16101) and Crossref. The
threshold `N(t)` was NOT checked, and neither was whether Huang and Lyu allow
digons: if their digraphs forbid opposite arcs, their class is smaller than the
thesis's and the bound does not transfer. Check both before this becomes
anything more than a citation.
  Files: `directed_connectivity_two_path_improvement.tex` (with the sandwich
  against the conjectured `(m-2)/2`), `directed_connectivity_huang_lyu_short.tex`
  (the same result, shorter).

**2. `conj:dir-arc` at m = 3, claimed in full (NOT in the thesis).**
`m3_simple_digraph_proof.tex` claims `ell_3^dir(n) = max(3(n-1), floor((n+1)^2/4))`
for every `n >= 3`, by induction on `n` from a machine-checked base range
`n <= 10`. The machinery is a safe arc-splitting operation, a counting lemma for
posets whose intervals hold at most three elements, and a nine-row case table.
Nothing in it contradicts the thesis: the exhaustive values at `n <= 6` and the
searched values at `n = 7, 8` all sit on the claimed formula.
  It is out of the thesis for two reasons. The proof is long and its base cases
are a computer run, which makes it read as confirmation that the conjecture
looks right rather than as a clean argument, and `verify_m3_bases.py`, the Z3
script that runs those base cases, was never handed over. Without that script
the finite half of the proof cannot be replayed at all, so it could not enter
the thesis under the honesty contract even if the human half checked out.
Ask for the script first, then check the case table.

## How to add an entry

One topic per file (or a small folder if it grows). Lead with the formal
statements and their status, then proofs, then the open residue and concrete next
steps. Add a reproducible script in `scripts/` for any numeric claim and name it
in the entry. Link related entries.

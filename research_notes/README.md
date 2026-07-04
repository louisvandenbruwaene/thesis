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

## How to add an entry

One topic per file (or a small folder if it grows). Lead with the formal
statements and their status, then proofs, then the open residue and concrete next
steps. Add a reproducible script in `scripts/` for any numeric claim and name it
in the entry. Link related entries.

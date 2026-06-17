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
branch of `conj:dir-arc` for `m >= 3`. It reframes the problem away from the
stuck "no backward arc" exchange and reduces the whole `m = 3` quadratic upper
bound to a single concrete hypothesis about sources.

- [`directed_arc_m3_reduction.md`](directed_arc_m3_reduction.md) -- the
  min-degree-deletion reduction (the `m=2` engine applied to `m=3`) and the
  conditional structure theorem. **Reduces the upper bound to one hypothesis (H).**
- [`directed_arc_m3_extremisers.md`](directed_arc_m3_extremisers.md) -- the full
  extremiser family (not unique) and the attachment refutation that kills the
  residual `+1` case once (H) is known.

Scripts: `attach_check.py` (arithmetic + single-cycle attachment),
`attach_check_all_perms.py` (attachment over all extremiser types),
`characterisation_checks.py` (arc partition, the source lemma, the conditional
bound, family feasibility), `odd_extremiser_search.py` (a search probe; weak,
see its note).

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

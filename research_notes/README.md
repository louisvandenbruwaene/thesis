# Research notes: conjectures and supposed proofs (NOT part of the thesis)

This folder is a working archive for results, conjectures, and proof attempts
that grew out of the thesis but are **deliberately not in it** -- they are too
specific, too long, or too unfinished to belong in the main text, yet they are
worth keeping for whoever (AI or human) continues the work.

## Ground rules

- **Nothing here is claimed in the thesis.** The thesis's honesty contract still
  holds: a statement enters the thesis text only after a proof-check. Items here
  are flagged PROVED / VERIFIED / CONJECTURE / OPEN explicitly.
- Every computational claim is backed by a self-contained script in `scripts/`
  (no external dependencies; standard-library Python + a hand-rolled unit-capacity
  max-flow). Run any of them with `python3 research_notes/scripts/<name>.py`.
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

## How to add an entry

One topic per file (or a small folder if it grows). Lead with the formal
statements and their status, then proofs, then the open residue and concrete next
steps. Add a reproducible script in `scripts/` for any numeric claim and name it
in the entry. Link related entries.

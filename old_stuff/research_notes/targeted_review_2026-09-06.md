# Targeted manuscript review

This pass preserves the existing exposition except where a specific claim or
explanation needed correction.

## Corrections

- The contribution table now restricts the additive linear-order estimate for
  simple digraphs to fixed m at least 3. The m=2 case has a different correction.
- The directed hypergraph summary specifies rank at least 3 when covering both
  simple and repeated-edge models with the same leading coefficient.
- Both synthesis tables now state the joint regime for the quadratic-in-m
  multigraph incidence estimate. The discussion no longer treats its asymptotic
  lower constant as an exact bound for each finite m or assumes convergence.
- Open problems no longer presume a linear coefficient exists or a hypergraph
  counterexample must occur. An unsupported structural prediction was removed.
- The program summary distinguishes matrix tabu search from hypergraph greedy
  search and describes directed hyperedges by tail and head sets.
- Reproducibility wording now distinguishes rerunning a workflow from reproducing
  historical timed outcomes. It acknowledges missing historical witnesses and
  runtimes and does not call every experiment driver an independent checker.
- The general-orientation proof introduction now says maximal rather than
  maximum and explains the difference, matching the existing greedy argument.
- The badge policy explicitly covers constructions with unverified proofs.
  The synthesis summary retains the author's verification caveat rather than
  silently upgrading badged results.

## Scope and ongoing work

The frozen benchmark source, manifest and trial checkpoints were not changed.
Its derived report was refreshed at 300 saved trials out of 384. The experiment
is still partial. Timing qualification remains separate from witness feasibility.

This is a targeted consistency pass, not independent certification of every
proof. No new solver changes or new mathematical results were introduced.

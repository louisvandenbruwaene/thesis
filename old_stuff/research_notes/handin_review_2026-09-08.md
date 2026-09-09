# Submission review — 8 September 2026

Reviewed the current repository, starting at `c12d896`. The recent author-verification commits (`93bce9a` and `c12d896`) and the theorem/proof environments are the source of truth for status. Older Downloads copies and dated working notes are not current evidence.

## Assessment

The current thesis is substantially closer to submission than the older copy. The principal defect was that the recent proof promotions had not propagated through the abstract, status index, lay summary and computational discussion. Those inconsistencies are corrected. Open problems do not need to be solved to submit a thesis. The 13 author-unchecked arguments remain explicitly conjectural, with proposed proofs, rather than being silently promoted.

This was a submission-consistency review with proof spot-checks, not independent peer review of every argument or a guarantee of mathematical correctness. The checked/unverified distinction continues to record the author's verification status. In particular, the standalone multigraph incidence m=3 proposed proof retains its badge even though the checked hypergraph upper and attainment statements already imply that value at r=2.

## Changes

- Updated the abstract, contribution table, synthesis, appendix introductions and companion documentation to match the already checked directed multigraph arc, hypergraph vertex and directed hypergraph results.
- Distinguished the m=3 hypergraph upper bound from equality on the stated attainment ranges.
- Corrected the hypergraph figure generator: established upper bounds are blue, retain their upper-bound semantics, and are not labelled conjectural merely because attainment is unknown elsewhere. Updated the existing construction/status regression assertion and regenerated the two affected plots and value table from the frozen record.
- The twelve-copy (n,m,r)=(6,6,3) multihypergraph edge construction now correctly meets a proved upper bound of 12. Its vertex value remains a lower bound only.
- Preserved all 13 conjecture statements and their proposed proofs. No numerical search result or machine-value record was changed.
- Updated the one-page popularising summary and supplied a plain-text version (3,174 characters excluding its final newline).

## Verification

- Full companion suite: 208 tests, one deliberate slow-enumeration skip, passed.
- Built-in companion self-check: all checks passed.
- Document-tool suite: 13 tests passed.
- After the figure-status change, all 27 construction/value-table tests passed.
- The consistency gate passed. The rebuilt thesis has 125 pages, zero unresolved references, zero LaTeX warnings, and zero overfull or underfull boxes. The scientific summary now fits one page.
- Rendered the short summary, synthesis status table, hypergraph grid and finite-values table for visual inspection.
- Figure regeneration only read the recorded data. It did not rerun timed experiments or alter `program/data/machine_values.json`.

## Final author checks

1. Confirm the cover's academic year, currently **2026–2027**. No year was guessed or changed.
2. Confirm the enrolled programme's language requirements. The current summaries are English. Faculty guidance requires Dutch and English scientific summaries for a Dutch programme, and English for an English programme. It also specifies a popularising summary of at most one A4 page and 3,500 characters. The plain-text English lay summary is supplied for portal entry. See [Faculty of Science thesis guidance](https://wet.kuleuven.be/english/mastersthesis/copy_of_mastersthesisconceptnote) and [submission workflow](https://wet.kuleuven.be/english/mastersthesis/workflow).
3. Ensure that the final contribution/AI-use declaration accurately describes your work and matches any separate declaration required by your programme. No institutional acceptance or supervisor approval has been inferred.

## Retained author-unchecked proposed proofs

- `thm:simple-vertex-blocks` — The vertex problem is a knapsack over blocks
- `lem:equality-forces` — What equality forces
- `lem:skeleton-shallow` — A minimal bipartite skeleton has no long path
- `thm:dir-multi-uniqueness` — Extremal classification on the quadratic branch
- `cor:multi-vertex-m3` — The multigraph incidence value at $m = 3$
- `thm:clique-chain-vertex` — A bouquet of thickened cliques, and how it beats the thickened tree
- `prop:multi-vertex-upper` — An upper bound of the same order
- `lem:multi-vertex-objective` — The objective in closed form
- `thm:multi-vertex-blocks` — The multigraph incidence problem is a knapsack over blocks
- `thm:multi-vertex-bipartite` — Thickened complete bipartite blocks
- `lem:multi-vertex-split-dir` — Splitting the directed vertex measure
- `cor:dir-multi-incidence` — The directed multigraph incidence value
- `prop:dir-multi-vertex-blocks` — The directed incidence value is a block problem too

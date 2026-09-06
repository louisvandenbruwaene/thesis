# Proof audit, 6 September 2026

## Scope and verdict

All 62 explicit proof environments in the live appendix were read in this
pass. Their uses were checked against the main theorem statements. The inline
directed constructions, clique-core cuts, elementary deletion lemmas, asymptotic
calculations and checker-bookkeeping argument were also reviewed.

No unresolved logical gap was found in the central original proofs under the
thesis's stated incidence convention. This is a reasoning audit by an AI
assistant, not a formal proof-assistant certificate or an independent human
referee report. It does not change which proofs Louis has personally checked.
The existing author-verification badges therefore remain.

Published results are dependencies, not new proofs verified here from first
principles. Source checking has limits, recorded below. Historical claims based
only on exhaustive computation are also distinct from the 62 written proofs.
This pass did not rerun every historical enumeration.

## Proof-by-proof record

“Checked” means the argument was followed and its dependency and boundary cases
were examined. It does not mean a finite experiment proved its conclusion.

| Proof label | Review of the argument |
|---|---|
| `lem:degree-bound` | Checked. Distinct routes use distinct incident edge copies at each endpoint. |
| `prop:monotone` | Checked. Discard the at most one route using the new copy. The incidence convention is essential for the vertex case. |
| `lem:dist-1-count` | Checked. Simplicity permits at most one graph edge for each of the n-1 tree adjacencies. |
| `lem:sum-dist` | Checked. Separate distance-one edges from edges with tree distance at least two. |
| `lem:double-count` | Checked. Each graph edge crosses exactly the tree cuts on its endpoint path. Requires the fundamental-cut property of Gomory-Hu trees. |
| `thm:mader` | Checked. Combine the two distance inequalities and round the integer edge count down. |
| `thm:multigraph-edge` | Checked. Every copy crosses a tree cut. Thickened trees meet the resulting sum bound. |
| `lem:near-regular` | Checked. Check both parities. In the odd case the added matching is disjoint and its cyclic distance is absent from the starting graph. |
| `thm:extremal-existence` | Checked. The spoke degree cap controls every pair because there is only one hub. |
| `thm:extremal-char` | Checked. The three nonnegative integer slacks sum to the parity remainder, either zero or one. |
| `thm:simple-vertex-blocks` | Checked. Block weights and vertex costs add. Gluing preserves feasibility. Corrected the indexing in the Fekete step. |
| `lem:reach-skeleton` | Checked. Two arborescences per SCC preserve reachability. The reduced condensation is triangle-free. Discrete convexity bounds the count by its endpoints. |
| `lem:two-hop-arc` | Checked. The direct arc and m-1 distinct two-hop detours contradict the cap. |
| `thm:directed-upper` | Checked. Sum internal indegrees and the two possible hub arc classes. |
| `thm:dir-vertex-m2-exact` | Checked. An omitted skeleton arc would coexist with a longer path whose interior is disjoint from that direct arc. |
| `thm:dir-arc-m2-exact` | Checked. The vertex upper bound applies to the smaller arc-feasible family and both constructions attain the maximum. |
| `lem:augmented-feasible` | Checked. The displayed short routes give a lower bound and reachable final arcs give the matching cut. Clarified that longer routes can exist. |
| `lem:feasible-budgeted` | Checked. The direct route and routes through distinct midpoints are disjoint under both separations. |
| `lem:budget-degree-sum` | Checked. Diagonal two-walks contribute twice the digon count, which is absorbed by the arc term. |
| `lem:small-side` | Checked. The larger of the two degrees is at least half their sum. |
| `lem:floor-identity` | Checked. Both parities give the claimed floor identity. |
| `lem:smaller-half-deletion` | Checked. Mark incoming arcs at source-like vertices and outgoing arcs at sink-like vertices. Double marking only reduces the deletion count. |
| `lem:two-step-budget` | Checked. Low-degree deletion preserves the budget. Otherwise the minimum total degree converts the product sum to the required linear bound. |
| `thm:dir-arc-linear-error` | Checked. Apply the budget lemma and expand the augmented construction. Positive linear lower error requires m at least 3. |
| `thm:dir-vertex-linear-error` | Checked. The same short-route family meets the stronger disjointness requirement. This is not an invalid transfer of an arc upper bound. |
| `prop:dir-arc-stability` | Checked. Cauchy-Schwarz bounds the marked-arc count. No claim of a balanced or complete surviving bipartition is needed. |
| `lem:thickening` | Checked. Every cut capacity scales by the same positive integer. |
| `lem:reach-delete` | Checked. A path inside the removed copies augments any surviving arc-disjoint family by one. |
| `thm:dir-multi-full` | Checked. Induct on the integer cap, including zero. Every peel costs at most M(n) and reduces the cap. |
| `cor:dir-multi-n7` | Checked. Substitute M(7)=12 and multiplicity two. |
| `cor:mstar-integral` | Checked. The feasible weight set is a finite union of rational polytopes. Clear a rational optimum's denominator and apply the integer theorem. |
| `lem:equality-forces` | Checked. All peels must attain the bound. Strict endpoint dominance forces singleton SCCs, followed by equality in Mantel. Added m at least 2 explicitly. |
| `lem:skeleton-shallow` | Checked. A three-arc path in the complete bipartite skeleton forces either a cycle or a redundant arc. |
| `thm:dir-multi-uniqueness` | Checked. A two-arc path would force at least floor(n/2) disjoint routes. The n at least 2m restriction then forces one-way orientation and saturated multiplicities. |
| `thm:menger-hyper` | Checked. Gate flows and Berge paths translate in both directions. Partial deletion of identical copies cannot change reachability. |
| `lem:hyper-cut-induction` | Checked. Trace copies inherit the route cap. Each crossing copy contributes exactly one beyond its two traces. |
| `prop:hyper-edge` | Checked. Specialise the trace sum to uniform rank. Check the divisible star construction and the simple attainment condition. |
| `thm:simple-hyper-edge` | Checked. Degree smoothing on the non-hub vertices gives distinct sets. Every pair contains a non-hub endpoint with a small incident cut. |
| `const:multihyper-six` | Checked. The five non-hub degrees are all five. Twelve copies match the edge upper bound, not a vertex upper bound. |
| `lem:sparse-hypergraph` | Checked. An exchange reduces the sum of squared degrees unless the degrees differ by at most one. The ceiling of their mean is at most the integer cap. |
| `thm:hyper-vertex-m2` | Checked. Incidence cycles are exactly the obstruction to the cap one condition. Forest counting and the star forest attain the floor. |
| `prop:hyper-vertex-lower` | Checked. The simple edge-feasible construction is also vertex-feasible under the fixed incidence convention. |
| `prop:hyper-vertex-lower-multi` | Checked. Copies within a block give direct routes. Routes between different blocks must use the shared hub. |
| `lem:incidence-rank` | Checked. Checked base cases, block summation, both degree-two reductions and all three separating-pair torso cases. See the expanded notes below. |
| `thm:hyper-vertex-m3` | Checked. Apply the rank inequality componentwise. The component count contributes a nonpositive correction. The stated simple attainment range meets the degree condition. |
| `lem:multi-vertex-split` | Checked. Direct copies contribute independently. Longer internally disjoint paths project injectively to the simple support. |
| `thm:multi-vertex-m2` | Checked. Any support cycle creates a detour beside an edge. Thus the support is a forest with unit multiplicities. |
| `cor:multi-vertex-m3` | Checked. The hypergraph upper bound at rank two matches a doubled tree. |
| `thm:clique-chain-vertex` | Checked. Each clique has detour count r-2. Attachment vertices prevent extra routes between blocks. The gain formula follows by subtraction. |
| `prop:multi-vertex-upper` | Checked. The simple support is feasible and every multiplicity is capped. Apply the cited average-degree theorem to the support. |
| `lem:multi-vertex-objective` | Checked. Each edge's optimal multiplicity is m minus its simple-support connectivity and remains at least one. |
| `thm:multi-vertex-blocks` | Checked. The local edge objective is block-additive. Every admissible multiset of blocks can be glued at one vertex. |
| `thm:multi-vertex-bipartite` | Checked. Same-side pairs have the opposite side as a separator. Adjacent-pair detours number s-1. Optimisation of the rate gives the stated asymptotic constant. |
| `lem:multi-vertex-split-dir` | Checked. The copy-plus-detour argument preserves orientation and the reverse arc cannot belong to a simple path with the given endpoints. |
| `cor:dir-multi-incidence` | Checked. At cap one repeats vanish. In general use the arc construction below and the directed hypergraph upper bound at rank two above. |
| `prop:dir-multi-vertex-blocks` | Checked. Directed paths stay within their underlying undirected block. Complete directed blocks have b-2 detours per ordered adjacent pair. |
| `prop:dir-hyper-first` | Checked. Count one-step tail-head incidences. The cyclic-word construction has distinct vertices per edge and degree at most the cap. |
| `const:bounded-outdegree-hyper` | Checked. Deleting a tail's outgoing copies cuts every route starting there. Different tails give different forward hyperedge types. |
| `lem:dir-hyper-duality` | Checked. Reversal is an involution preserving edge copies and interior intersections while exchanging endpoints. |
| `prop:dir-hyper-general` | Checked. Each copy occupies at least r-1 ordered pairs and each pair is occupied at most m-1 times. |
| `thm:dir-hyper-constant` | Checked. A maximal entrance matching covers the target set through its used hyperedges. Distinct tails keep exits separate from all entrances. |
| `thm:dir-hyper-general-constant` | Checked. A maximal route family obstructs each unused target through a used hyperedge. Count at most r vertices per used copy and at most two copies per route. |

## Incidence-rank induction

The block step needs the block-cut tree, not an assumption that every two blocks
share a vertex. Summing repeated X-vertices cancels all block costs except one
and leaves a nonpositive contribution from Z cut vertices.

Suppressing a degree-two Z-vertex preserves cycle rank and connectivity among
surviving vertices. Deleting a degree-two X-vertex reduces both cycle rank and
the available X bound by one. The remaining graph is simple because parallel
X edges would have a third route through the rest of a 2-connected graph.

In the separating-pair step, an existing separator edge forces exactly one
separator endpoint to lie in X. Otherwise the edge and the two side paths give
three routes between X endpoints. A missing separator edge is represented by
one edge when at least one endpoint is in X and by a fresh degree-two X-vertex
when both endpoints lie in Z. Any violating family among old X-vertices lifts
through the opposite side. A family involving the fresh vertex is capped by
its degree. The rank identities and X counts give the claimed bound in all
three cases.

Strict decrease of vertex-plus-edge count also holds. A side cannot be a single
vertex in the remaining simple minimum-degree-three graph, while replacing a
side adds at most one vertex and two edges. Thus there is no circular induction.

## Source checks and their limits

- [Huang and Lyu, Theorem 2](https://arxiv.org/html/2406.16101v2) uses strict
  digraphs, so reverse arcs are permitted but loops and parallel arcs are not.
  Taking t=m-1 gives the upper bound used in the thesis for fixed m at least 3
  and sufficiently large n. Its expression is n squared over four plus tn and
  a bounded term for fixed t. No finite-n conclusion was imported outside the
  theorem's size restriction.
- [Carmesin's paper](https://arxiv.org/abs/2003.00942) explicitly records the
  Mader consequence used here, average degree at least 4k forcing a
  (k+1)-connected subgraph. The thesis need not weaken that to k-connectivity.
  The remark claiming its bound was the only general upper bound known was
  removed. This pass does not claim the thesis uses the sharpest modern bound.
- [The publisher abstract for Sørensen and Thomassen](https://www.sciencedirect.com/science/article/pii/0095895674900823)
  specifically describes the 3-connected result for 5-rails. The thesis's
  unrestricted all-m attribution was removed from the prose and bibliography.
  The full original article could not be retrieved through the available web
  routes in this pass. Its detailed Theorem 4 transcription and recursive
  construction remain cited literature dependencies, not newly source-certified
  results. Their arithmetic and applications in the thesis were checked.
- Menger, Gomory-Hu, Mantel and Fekete are used in their stated standard forms.
  Their original published proofs were not reproduced or newly audited line
  by line. The crucial fundamental-cut property of the Gomory-Hu tree is
  explicitly included.

## Corrections made

The augmented bipartite proof now distinguishes its exhibited short routes
from all possible routes. The Fekete step explicitly defines its shifted
sequence. The equality-forces lemma explicitly assumes m at least 2. The
hypergraph Menger theorem specifies distinct endpoints and hypergraph edge
statements use maximum local connectivity explicitly. The order-one convention
for maximum local connectivity is now stated.

The fractional optimum discussion says an integral optimum can be chosen,
not that every optimum must be integral. The checker argument now restricts
identical search outcomes to fixed-step comparisons. Under a time limit,
faster checking can change the number of steps and the returned witness.

## Finite checks in this pass

- Nonuniform cut induction: 400 seeded random instances, no violation.
- Degree smoothing: every family size for each rank through order 8, with one
  seeded starting family per size, no failure.
- Cyclic word: head-side sizes through 11 and degree caps through 11, no failure.
- Incidence rank: 318 eligible labelled multigraph/partition instances through
  order 4 with multiplicities at most 3, all encountered recursive cases passed.
  The minimum-degree-three core branch was not exercised.
- Two new regression tests passed. One checks the torso hypotheses and
  bookkeeping in all four combinations of separator membership and retained
  edge. These fixtures exercise the torso operation, not eligible
  minimum-degree-three cores. The other ensures generator failure raises an
  error instead of being reported as an empty enumeration.

The helper now reports actual branch coverage, uses compatible integer labels
for fresh torso vertices and checks the external generator's exit status.
None of these finite checks replaces the written induction.

## Benchmark status during the audit

At 302 saved trials, eight had timing discrepancies and remain excluded from
timing-qualified statistics. Original witnesses and trial files were preserved.
Replacement search for eight 150-second trials would take about 20 minutes.
No replacements were run concurrently with the continuing serial benchmark.
The frozen benchmark source was not changed.

Small audit checks and LaTeX builds ran on the same computer. The benchmark is
not an isolated-machine CPU comparison.


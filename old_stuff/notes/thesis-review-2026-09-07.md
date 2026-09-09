Submission-readiness review, 7 September 2026

**Verdict: not yet submission-ready under your standard of correct, understandable, compact and clean.** The build and computational checks are strong. The remaining concerns are the treatment of proof verification, precise definitions, contradictory descriptions of the search, and avoidable presentation problems. I did not find a counterexample to a principal extremal formula in this review. That is not a certification of every theorem.

Reviewed the 124-page `main.pdf`, the main LaTeX sources, substantial portions of the proof appendix, computational documentation and saved evidence. Inspected contact sheets of every PDF page for layout. Mathematical checking concentrated on the Gomory–Hu count, reachability skeleton and deletion argument, incidence-rank induction, two-step budget, and directed hypergraph shadow arguments. This was not an independent line-by-line verification of every proof, an exhaustive literature search for novelty, or a check of faculty submission regulations.

Locations below refer to the current sources. Printed page numbers differ from physical PDF page numbers by the front matter.

1. **Resolve the verification status of the main results and their dependencies.**

   [Contribution Statement, main.tex:50](/Users/chief/Documents/Projects/thesis/main.tex:50) instructs the reader to treat badged results as conjectures with likely-correct proofs. But the Short Summary says the directed multigraph problem “closes completely” and the directed hypergraph leading term is “settled” ([main.tex:108](/Users/chief/Documents/Projects/thesis/main.tex:108)). These are central conclusions, not incidental claims.

   More concretely, the unbadged hypergraph vertex theorem at m=3 relies directly on the badged incidence-rank lemma: compare [the lemma, app_proofs.tex:1473](/Users/chief/Documents/Projects/thesis/chapters/app_proofs.tex:1473) with [the theorem's proof, app_proofs.tex:1631](/Users/chief/Documents/Projects/thesis/chapters/app_proofs.tex:1631). The unbadged directed m=2 results likewise rely on the badged reachability-skeleton lemma at line 466. Checking a deduction from an unchecked lemma does not establish the lemma itself.

   The global caveat in Chapter 3 acknowledges the issue but does not resolve it. Either the necessary proofs and dependencies need verification by someone taking responsibility for them, or conclusions depending on unresolved results need a consistent qualified status throughout. Do not merely remove the badges. This finding concerns what the manuscript warrants, not a claim that AI assistance makes a proof false.

2. **The heuristic description contradicts the implemented hypergraph method.**

   [Chapter 2, lines 555–577](/Users/chief/Documents/Projects/thesis/chapters/ch2_machine.tex:555) applies the penalised energy and tabu walk to edges, arcs and hyperedges, then says the reported discovery bounds use tabu search. However, the experiment protocol correctly says hypergraphs use random greedy growth. The implementation explicitly rejects tabu and simulated annealing for hypergraph discovery ([erdos915_unified.py:2812](/Users/chief/Documents/Projects/thesis/program/erdos915_unified.py:2812)).

   Restrict the energy/tabu explanation to matrix models and describe the random greedy hypergraph procedure separately where the algorithms are introduced. Readers should not need the later experimental section to correct their understanding of the method.

3. **The universal incidence convention needs an explicit directed definition.**

   [Chapter 1, lines 420–425](/Users/chief/Documents/Projects/thesis/chapters/ch1_basecases.tex:420) says every model uses the same incidence graph, then defines undirected incidences and ordinary paths. Read literally, that allows traversal against an arc or from one head of a hyperedge to another. A single arc u→v would incorrectly give a reverse route.

   State that directed models use a directed incidence graph: arcs go from each tail to its edge-copy node and from that node to each head, and routes are directed paths. The later flow-network description already respects these directions. This is a gap in the introductory definition, not evidence that the checker ignores orientation.

4. **A Gomory–Hu tree is not necessarily a spanning subgraph of G.**

   [Chapter 1, line 122](/Users/chief/Documents/Projects/thesis/chapters/ch1_basecases.tex:122) says every graph has a “weighted spanning tree” encoding its local connectivities. In standard graph terminology, a spanning tree uses edges of the original graph. The correct statement is a weighted tree **on the same vertex set**. The appendix states it correctly.

   A concrete obstruction is K₂,₃. The two vertices in its part of size two have local edge-connectivity three, while every adjacent pair has local edge-connectivity two. Any tree restricted to original edges would therefore have every weight two and could not encode the value three. Replace the introductory wording with the appendix's formulation. The current wording is also literally impossible for disconnected graphs.

5. **The explanation of the identical m=2 enumeration counts is incorrect.**

   [Appendix A.13, app_proofs.tex:2776](/Users/chief/Documents/Projects/thesis/chapters/app_proofs.tex:2776) and the following table caption call the identical pruning/node counts a coincidence.

   At this threshold the two feasible families are identical: λmax≤1 if and only if κmax≤1. For the nontrivial direction, take two arc-disjoint directed u–v paths. Follow one from u to its first subsequent intersection with the other. Their two prefixes are internally vertex-disjoint, so some ordered pair has κ≥2. The reverse direction follows from κ≤λ.

   Thus the same partial graph fails either feasibility test at exactly the same point. With the stated identical branching, incumbent and pruning rules, matching search-tree counts are expected mathematically. The different flow networks can still take different amounts of time. Replace the coincidence explanation with this equivalence.

6. **Repair the front-matter page breaks.**

   Printed page VI (physical PDF page 8) has only the “Abbreviations and Symbols” heading and two abbreviation entries. The symbols table moves wholesale to page VII. This leaves most of page VI empty and detaches the table from its heading. The cause is the unbreakable second `tabular` beginning at [main.tex:121](/Users/chief/Documents/Projects/thesis/main.tex:121).

   Use a table that can break across pages or split the entries deliberately with repeated headings. Do not solve this by making the type substantially smaller. The contribution table also starts on the next page after its introductory sentence, and the Short Summary spills a short final paragraph onto a second page. Those are additional worthwhile front-matter adjustments. I did not see comparable widespread clipping or overlap in the body-page contact sheets.

7. **Shorten repeated explanation and research history.**

   The main text occupies 31 numbered pages, while the proof-and-audit appendix occupies pages 32–108. That allocation alone is not a defect, but much of the appendix repeats a result before its statement, in its proof, and again after the proof.

   Specific shortening candidates:

   - The arithmetic identity and elementary small-side estimate around [app_proofs.tex:775](/Users/chief/Documents/Projects/thesis/chapters/app_proofs.tex:775) can be brief observations inside the counting argument rather than separate named lemmas with full commentary.
   - The reversal lemma at [app_proofs.tex:2157](/Users/chief/Documents/Projects/thesis/chapters/app_proofs.tex:2157) states reversal invariance, explains it again in words, and then proves it in detail. A short proof is sufficient.
   - The discussion around [app_proofs.tex:974](/Users/chief/Documents/Projects/thesis/chapters/app_proofs.tex:974) repeatedly explains how a hand proof replaced an unfinished computation. Retain the mathematical argument and one audit statement documenting the unfinished run.
   - The forcing-versus-avoiding convention discussion around line 291 spends substantial space recounting mistakes in earlier drafts. Keep the convention and a worked example; move draft history to working notes.

   Preserve the full Mader proof and the technical details that justify the difficult steps. The shortening target is repeated explanation. In Chapter 1, subdividing the long “Proven bounds” section by graph family would also make the progression easier to follow without moving proofs into the body.

8. **Distinguish an original proof from a consequence of existing literature.**

   The contribution table presents the simple directed n²/4+Θm(n) results as original results. The thesis also cites Huang–Lyu's stronger eventual upper bound. Their Theorem 2, with t=m−1, implies an upper bound n²/4+(m−1)n+O_m(1) for both of your simple directed feasible families, since both exclude m internally disjoint two-step paths with common endpoints. Combined with your displayed lower construction, this already implies the asserted order of the error term. This is an inference from [Huang and Lyu, Theorem 2](https://arxiv.org/html/2406.16101v2).

   Describe the contribution precisely as the self-contained elementary proof, the explicit bound valid at every n, and the extensions that are established here. The existing citation is good, but it should also inform the novelty wording in the contribution statement. This observation does not settle the originality of the hypergraph results or assert that the proofs were copied.

**Checks completed.** A fresh out-of-tree LaTeX build succeeds and produces the same extracted PDF text as `main.pdf`: zero LaTeX warnings, zero natbib warnings, zero overfull boxes, zero unresolved `??` markers, and one minor underfull bibliography box. The consistency gate passes. The program suite runs 207 tests successfully with one skip; the separate bundle suite passes all five tests; the program self-check passes. All 403 saved original and replacement benchmark witnesses pass the supplied independent per-copy NetworkX validator, invoked without rewriting the audit files. `main.pdf` and `handin/main.pdf` have identical SHA-256 hashes. The tests used the existing environment; I did not test a fresh dependency installation or rerun the hours-long benchmark searches. Thesis files and tracked repository state were left unchanged.

**One administrative item to verify:** the cover hard-codes academic year 2026–2027 at [preamble.tex:546](/Users/chief/Documents/Projects/thesis/preamble.tex:546). I cannot determine your submission cohort from the repository. Check it against the academic year of the examination session; this is not a confirmed error.

The most important next step is to resolve the proof-status dependencies. The remaining concrete corrections and a focused shortening/layout pass would then make the document substantially closer to the standard you described.

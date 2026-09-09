# Submission proofreading — 9 September 2026

Reviewed the current thesis (front matter, all three chapters, proof appendix,
captions, tables and printed bibliography), the seminar deck including its
backup slides, the popularising summary in TeX/PDF/plain text, and the root,
slides and program READMEs. The root README identifies these as the current
deliverables; archived material under `old_stuff/` was excluded.

This is a proofreading and internal-consistency review. No program, tests,
searches, solvers, figure generators or LaTeX builds were run. PDF-reading
utilities were used to extract text and inspect selected existing pages.
The cover, summary and one dense backup slide were visually inspected;
this was not an every-page visual layout audit or a formal verification of
every proof. Publication metadata was not independently checked online.

The submission files have not been edited. Suggested changes are below,
with more consequential wording issues first. Line numbers refer to the
sources as reviewed. Slide numbers refer to the printed footer; PDF page
numbers are one higher.

## Corrections that affect meaning

1. **The explanation of the incidence convention contains a false equivalence.**
   `chapters/ch1_basecases.tex:436` says an edge lies on a route “exactly when
   both of its endpoints do.” A path can contain both endpoints without using
   their edge: in a triangle, the path u–w–v contains u and v but does not use
   uv. The conclusion about simple graphs is correct, but this justification
   should be replaced with:

   > For a simple graph this gives the usual definition: distinct internally
   > vertex-disjoint paths cannot share an edge. The direct edge between the
   > endpoints supplies at most one path.

2. **The Whitney discussion confuses a local gap with a gap between feasible
   families.** `chapters/app_proofs.tex:611` infers that “there really are
   digraphs in the difference of the two families” merely from paths sharing
   an interior vertex. A local example does not establish the required
   maximum-over-all-pairs condition. In particular, the later lemma explicitly
   proves that the feasible families coincide at m=2. Replace this explanation
   with:

   > Local arc and vertex connectivities can differ. This alone does not show
   > that the feasible families differ at a given threshold; at m=2 they
   > coincide, as Lemma `lem:directed-m2-families` shows.

   Also replace “the larger of the two” with “a family containing the
   arc-feasible family” where strict containment has not been established.

3. **The popularising summary overstates the scope of the exact directed
   result.** `popularising_summary/popularising_summary.tex:35`, also paragraph
   5 of the `.txt`, says repeated one-way links have an exact maximum at every
   size and route limit. This is established for arc separation; the directed
   incidence problem is still open in general. Suggested first sentence:

   > For one-way networks whose links may be repeated, the thesis proves the
   > exact maximum when separate routes may not share a link copy.

   Keep the following skeleton explanation. Update both the TeX and plain-text
   versions together when applying this correction.

4. **Some prose drops the explicitly conjectural status.** After the proposed
   bipartite-block proof, `chapters/app_proofs.tex:1963` says “The answer is
   therefore a block optimisation problem” and then states the asymptotic
   inequalities without qualification. Those arguments are still labelled
   conjectures. Suggested opening:

   > Under the proposed block reduction, the answer becomes a block
   > optimisation problem. If the proposed lower and upper bounds are
   > verified, then in the regime …

   Preserve the existing proof-status labels; this is a correction to the
   surrounding prose, not a recommendation to promote any result.

5. **The equality discussion overlooks the odd case in its introductory
   sentence.** `chapters/app_proofs.tex:263` says equality forces both
   inequalities to be tight. The theorem immediately following correctly
   permits one unit of slack when m(n−1) is odd. Replace the final sentence
   with:

   > Equality forces zero total slack when m(n−1) is even and exactly one
   > unit of slack when it is odd.

6. **The seminar's search diagram omits an implemented method.**
   `slides/seminarie/seminarie.tex:997`, slide 12, sends “matrix or list” to
   “SEARCH / tabu.” Hyperedge lists use random greedy growth, as the thesis
   and later slides correctly explain. Label the box “tabu / random greedy,”
   or distinguish the two representations in the diagram.

7. **The vertex-splitting slide needs to specify how endpoints are handled.**
   `slides/seminarie/seminarie.tex:888`, slide 10, shows only “cap 1” at v.
   This is valid for an intermediate vertex. To make the slide self-contained,
   label v as intermediate, or state that the flow runs from s-out to t-in,
   bypassing the endpoint gates. This is a clarification to the current
   simplified slide, not a request to restore its previous layout.

8. **“No counterexample” has no stated target.**
   `slides/seminarie/seminarie.tex:1293`, slide 26, says “No counterexample at
   m=4 across eleven (n,r) cells; the r=2 case fails at m=5.” The slide does
   not identify the tested assertion. State the exact inequality or conjecture
   being tested and identify whether the check used simple hypergraphs or
   multihypergraphs. The r=2 distinction matters: the thesis's simple-graph
   example is k₅(14)=33>ℓ₅(14)=32, whereas its multigraph example is
   K₅(4)=14>L₅(4)=12. These are different comparisons. Do not retain this
   sentence without identifying its intended one.

## Thesis wording and consistency

9. **Use “order” or “vertex count” for n.** Chapter 1 defines size as |E|,
   but Chapter 2 uses “given size” and “fixed size” for n at lines 22, 289
   and 559. Rename the section “Checking every graph of a fixed order.”
   Replace line 22 with:

   > The enumeration considers graphs of a fixed order and maximises their
   > edge count subject to the connectivity constraint.

10. **Remove stale candidate language.** `chapters/ch2_machine.tex:504,509`
    calls M(n) a “candidate,” although the theorem now establishes it.
    Use “established value M(n).” At line 511, “What would generalise is
    integrality” should become “The general statement is integrality.”
    At line 322, replace “even where a conjecture predicts their leading
    term” with “even where their leading term is established.”

11. **Remove dangling references to earlier arguments.**
    `chapters/ch1_basecases.tex:716` mentions “the parity obstruction that
    stopped the vertex-deletion induction,” and
    `chapters/app_proofs.tex:944` mentions “the fractional remainder above.”
    Neither passage supplies the corresponding abandoned argument. Delete
    these clauses or explain the obstruction explicitly. The present skeleton
    proof reads more directly without them.

12. **Correct the direction of a prose cross-reference.**
    `chapters/app_proofs.tex:1791`: “the next proposed upper bound” should be
    “the preceding proposed upper bound,” preferably an explicit reference to
    `prop:multi-vertex-upper`.

13. **Complete the symbol-list entry.** `main.tex:166` ends with “vertex set V
    and edge or arc set.” Use “vertex set V and edge multiset E or arc
    multiset A,” which also accommodates the multigraph models.

14. **Do not say hypergraphs have no matrix tools.**
    `chapters/ch2_machine.tex:24` says “there are no matrix tools for them,”
    and line 294 says “A hypergraph is not a matrix at all.” Both are too
    broad; the thesis itself uses incidence representations. Suggested text:

    > The program represents hypergraphs by lists of hyperedges rather than
    > adjacency matrices.

15. **Clarify the hyperedge-gate wiring.**
    `chapters/ch2_machine.tex:55`: “Every member … flows into the entry and
    out of the exit” makes vertices sound like the flowing objects. Use:

    > Add an unlimited-capacity arc from each member vertex to the entry
    > node and from the exit node to each member vertex.

16. **A skeleton does not discard every copy of every arc.**
    `chapters/app_proofs.tex:469`: replace “every parallel copy of every arc”
    with “all but one copy of each retained arc.”

17. **Fix the incomplete comparison.**
    `chapters/app_proofs.tex:1399`: “A multihypergraph does not, because it
    may repeat one hyperedge instead” lacks a clear verb phrase. Use:

    > A multihypergraph does not require distinct sets, because it may repeat
    > a hyperedge instead.

18. **The directed-incidence introduction describes the wrong dependency.**
    `chapters/app_proofs.tex:1972` says the splitting statement carries the arc
    results across “without any asymptotic argument.” The checked corollary
    now obtains its general upper bound from the shadow theorem at r=2;
    its exact conclusion is restricted to m=2. Suggested replacement:

    > The proposed splitting identity also has a directed version. The
    > checked corollary below separately gives the exact value at m=2 and
    > the leading term for every fixed m.

19. **Carry the separation notation into the audit.**
    `chapters/app_proofs.tex:2485` onward describes all shortcut bookkeeping
    using λmax, although it later claims coverage of both separations.
    Introduce cmax=λmax or κmax, as Chapter 2 already does, or add “The same
    discussion applies with κmax under vertex separation.”

20. **Small language corrections.**
    - `chapters/ch1_basecases.tex:134`: “use Berge paths, which aligns” →
      “use Berge paths, consistent with the path definition above.”
    - `chapters/ch2_machine.tex:22`: “connectivity restraint” →
      “connectivity constraint.”
    - `chapters/ch1_basecases.tex:4`: “results that can be proven using
      logical arguments” → “results established by mathematical proofs.”
    - `chapters/ch2_machine.tex:5`: “those statements are naive” →
      “these conjectures are supported only by small instances.”
    - `chapters/app_proofs.tex:2602`: “the Edmonds and Karp algorithm” →
      “the Edmonds–Karp algorithm.”
    - `preamble.tex:540`: “fulfillment” → “fulfilment” to match the document's
      predominantly British spelling. Treat prescribed faculty wording as
      fixed if this sentence is required verbatim.

## Summary and seminar presentation

21. **Correct the summary's grammatical subject.** Paragraph 3 says
    “Ordinary links use a short memory.” The search uses memory, not the
    links. Use “For ordinary links, the search keeps a short memory of recent
    moves …” Also change “This problem was posed by …, listed today as …”
    in paragraph 2 to “Posed by …, this is now listed as Erdős Problem 915.”

22. **Describe rediscovery as recovery of families.** Paragraph 3 of the
    summary says the program rediscovers “the very networks” singled out by
    earlier proofs. Chapter 2 explicitly distinguishes an extremal family
    from a unique graph. Use “examples from the known extremal families.”
    Similarly, slide 14 draws a path, whereas the recorded simple-graph
    witness is a star. Add “illustrative examples of the families” to the
    slide or its caption; the thesis already makes this distinction.

23. **Define PROPOSED in the delivered deck.** The current deck uses PROPOSED
    badges, but the explanation of their precise meaning is only in source
    comments/the README, not in its visible text. A short legend is sufficient:

    > PROPOSED: conjecture with a proposed proof not yet checked line by line
    > by the author.

    This does not require reinstating the removed AI discussion slide.

24. **Qualify construction badges and asymptotic ranges.**
    - Slide 23 calls the thickened bidirected tree EXTREMAL without naming
      its range. Add “linear branch, n≤7”; the bipartite construction wins
      for n≥8.
    - Slide 28 calls the repeated star EXTREMAL without the m=3 and
      (r−1)|(n−1) qualifications associated with the stated attainment.
    - Slide 30 should explicitly retain r≥3 and fixed m,r as n→∞; the
      simple r=2 leading coefficient is different for m≥3.
    - On slides 18 and 22, NEAR-EXTREMAL for a block family has no stated
      quantitative meaning. “Feasible construction” is safer, with the
      proposed asymptotic bound stated separately. The directed bipartite
      families have an established asymptotic justification; distinguish
      them from the conjectural block bounds.

25. **The status legend is too restrictive.** Slide 15 says “exact value
    open, asymptotic bounds only.” Some amber variants have exact small cases
    and explicit finite bounds. Match the thesis's wording: “exact value
    open, asymptotic bounds discussed below,” or simply “general exact value
    open.”

## Companion documentation and final presentation

26. **Scope the README's formula-return description.**
    `program/README.md:22` says `solve(exhaustive=True)` returns a construction
    as a lower bound without stating the branch. Add “For directed
    multigraphs under arc separation,” as Chapter 2 does. Otherwise a reader
    could think all exhaustive calls behave this way.

27. **Fix the timing explanation in the program README.** Its final sentence
    calls SA-versus-tabu timings an exception “because their stopping rule
    is wall-clock.” The same README correctly says the other historical
    searches are timed too. Use:

    > Fixed seeds do not make timed search outcomes reproducible across
    > machines or system loads; this also applies to the SA-versus-tabu
    > comparison.

28. **Make environment setup consistent.** The root README and appendix
    direct readers to the lock file, but `program/README.md:67` leads with
    unpinned requirements and its run commands assume a `.venv` that this
    README has not created. Refer to the root setup instructions, or include
    the same environment-creation and lock-file commands. This is a
    documentation consistency point, not a request to install or run anything.

29. **Consider shortening bibliography annotations.** The printed references
    include substantial research notes such as “The m≤4 equality is from
    Leonard's 1972 paper, not this one.” This is not a citation error, but
    reads like internal audit commentary. Move explanatory discussion into
    the thesis and keep bibliographic notes to necessary qualifications.
    In the Huang–Lyu note, correct “Turan” to “Turán” and typeset t+1 in math
    mode. Unused entries in `ref.bib` do not appear in the PDF and need not be
    deleted for submission.

## Checks that were satisfactory

- The current PDFs have 125 thesis pages, 33 seminar pages and one summary
  page. These are physical PDF page counts, not the displayed page numbers.
- The summary plain-text file has 3,175 characters including whitespace.
  The PDF's extracted text, including its heading, author, subtitle and page
  furniture, has approximately 3,354 characters. Both are below the
  3,500-character limit stated in the source. This checks the document against
  its stated limit, not the university's current administrative rules.
- The summary's plain-text and TeX bodies agree on the reviewed wording.
- Eleven conjecture environments remain, matching the Short Summary.
- The equal-allocation summary table agrees with the reported totals: best
  run reaches or exceeds C in 74/128 cases, all seeds in 68, and 54 cases
  fall short. These are checks of the printed numbers, not fresh experiments.
- The cover and title slide consistently show the same thesis title, author,
  promotor and academic year 2026–2027. Verify that the academic year is the
  one required for this particular submission; internal agreement alone
  cannot establish that.
- No literal unresolved-reference “??” or obvious TODO/TBD placeholder was
  found in the extracted thesis or slide text. PDF extraction is not a full
  LaTeX reference audit.
- The inspected cover and summary pages have no obvious clipping or overlap.
  The dense backup slide inspected is readable, though its last line sits
  close to the footer.

The most useful final pass would address items 1–8 first, then the stale
status language and dangling references. Most remaining issues are concise
wording changes rather than changes to the mathematics.

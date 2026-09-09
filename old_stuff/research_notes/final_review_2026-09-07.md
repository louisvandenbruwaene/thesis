# Final review scope and remaining limits

## Mathematics

The proof-by-proof record in proof_audit_2026-09-06.md covers all 62 explicit
proof environments. It records a logical review of the arguments, not merely
agreement with experiments. No unresolved gap was found in those original
arguments under the stated incidence convention. In particular, the
incidence-rank separating-pair step was checked logically. Its eligible
minimum-degree-three core remains outside the finite branch coverage.

This is an AI reasoning audit, not a formal certificate or independent human
referee report. Published theorems remain dependencies. The existing author
badges must not be changed by treating this review as Louis's personal
verification.

CLOSED 2026-09-07. The 1974 paper of Sørensen and Thomassen is in the
repository as `sorensen.pdf`, a scan with no text layer, and was read in a
later pass. Every claim the thesis attributes to it, the Theorem 4 statement
and its two exceptional values, the small-range formula, the Corollary 2(a)
rate, the recursive construction with its vertex and edge counts, the
3-connected treatment at m=5 and the attributions of the disproof, matches the
original. See sorensen_thomassen_source_check_2026-09-07.md. Leonard's
57-vertex counterexample is still carried from a secondary source.

The follow-up makes the fixed m at least three regime explicit in two
asymptotic conclusions. It also corrects the incidence-rank proof's sentence
about inheritance of hypotheses: non-bridge blocks inherit them, whereas a
bridge with a Z endpoint need not satisfy the degree condition and is handled
directly in the next sentence. This clarifies an already valid separate case.

The clique-core script again verified 135 parameter cases and all 4094
nontrivial cuts of the n=12, m=5 example. The recursive construction script
again verified all 12 displayed instances, for thresholds 5, 6 and 7 and
depths zero through three. These checks do not replace proofs for arbitrary
parameters.

## Code and evidence

The recursive construction checker previously could print a failed invariant
and exit successfully. It now raises on a wrong order, edge count, connectivity
or block condition. A regression test supplies a bad witness and requires that
failure. Its five-test block-audit suite passes.

The full suite completed with 206 tests in 427.517 seconds and no failures.
One optional slow enumeration was skipped. The new bad-construction regression
was added after that suite was loaded and passed separately in the five-test
block-audit run. The current tree therefore discovers 207 tests, not 206.
The 15 benchmark regression tests and the final manuscript consistency gate
also pass. The build has no overfull boxes or undefined references. The one
existing bibliography underfull warning remains.

The equal-budget review is complete as documented in
benchmark_review_2026-09-07.md. Timing qualification covers all 384 selected
trials and independent witness validation covers all 403 saved attempts.
Historical data have not all been regenerated. Timed search results are not
hardware-independent and test coverage is not a proof of correctness for every
input or execution path.

## Text and release

Existing sound text is retained. The conclusion now says that recorded
successful solver checks reach n=6, rather than implying that this is a hard
limit of the encoding. The completed benchmark's interpretation separates
unaided search from supplied constructions and reports actual search time.

The manuscript is reviewed and improved, not asserted to be uniquely optimal
prose. Source recording requires a clean committed snapshot. Public publication
is a separate external action for which approval has been requested.

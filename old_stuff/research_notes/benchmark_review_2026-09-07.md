# Completed benchmark review

The review began at commit 68da0bf with a clean worktree. That commit already
contained the completed replacements and fixes for forced rebuilding and
non-UTF-8 LaTeX logs. Those changes were preserved.

All 19 replacement trials completed at 21:39:56 UTC on 6 September 2026.
There are 384 timing-qualified selected trials across 128 parameter cases.
All 403 saved witnesses, including discarded originals, passed the independent
NetworkX audit again during this review. The renderer verified the selected
checkpoint hashes and rejected no construction or search count against the
recorded upper bounds. Original checkpoints and frozen search sources were
not changed.

The best run reaches the supplied construction count in 74 cases and falls
short in 54. Here reaching includes exceeding, which occurs in eight cases.
All three seeds reach the comparison count in 68 cases. These counts compare
against supplied constructions, not asserted optima. At n=12 and m=6, for
example, every directed multigraph arc trial returns 110 against a construction
with 180 arcs. Chapter 2 now explains both the successes and this limitation.

Selected monotonic search time is 57657.7 seconds against 57600 allocated.
All saved search attempts together used 58690.8 seconds. These are not calendar
durations and exclude validation and reporting. No original or replacement
interruption was recorded.

The five rendered tables were visually inspected at PDF pages 33 and 106
through 109. The columns, group labels and captions are legible and contained
within the page. Search counts and construction counts remain separate.
The completed tables are now required manuscript inputs. Missing table files
therefore fail the build instead of silently selecting a pending-results text.

The finalization command now includes its own regression tests. A new test
requires a forced LaTeX build, accepts a non-UTF-8 log without an overfull box
and rejects such a log when it contains an overfull warning. All 15 benchmark
regression tests pass. The rebuilt PDF passes the reference consistency gate
and has no overfull boxes. The existing bibliography underfull warning remains.

This finishes the benchmark review, not a formal certification of the entire
thesis. The proof audit and its source-access limits remain recorded in
proof_audit_2026-09-06.md. No commit, push, publication or author-verification
badge change was performed in this review.

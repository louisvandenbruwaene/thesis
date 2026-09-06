# Benchmark completion check

The original serial run finished at 20:15:42 UTC on 6 September 2026,
which is 22:15 Brussels time. All 384 trial checkpoints are present.
The regenerated report classifies 365 as timing-qualified and flags 19.
Completion of the runner is therefore not completion of the equal-budget audit.

All frozen source hashes still match the original manifest. No checkpoint,
manifest or frozen source file was changed. Flagged witnesses remain lower
bound evidence but their values are excluded from timing-qualified statistics.
Replacing 19 runs at 150 seconds each requires 2850 seconds of search, plus
setup and validation. No replacement runs were started in this check.

The current solver's exhaustive hypergraph loop now checks the deadline every
256 candidates that are skipped by the cheap size comparison. It also checks
before each potentially expensive candidate construction and connectivity
calculation. This change does not alter the frozen unaided benchmark, which
used random greedy search for hypergraphs rather than exhaustive enumeration.

Two regression tests cover checking before expensive work and batching clock
reads across cheap skips. The 12 audit regression tests pass. No quantitative
speedup is claimed without a separate performance measurement.

The repository was already at commit 02156f5 when this check began. No commit,
push or publication was performed during this check.

## Replacement follow-up

The separate replacement run started at 20:52:23 UTC on 6 September. Its
manifest selects all 19 timing-flagged trials in the original schedule order,
without looking at their objectives. The runner uses the original frozen
solver and compiled helper, verified against their original hashes. Only the
solver's module-local clock binding changes from calendar to monotonic time.
Original records are never overwritten and a replacement takes its slot even
when its edge count is lower. The current exhaustive-loop fix is not imported
into this frozen random-greedy experiment.

The independent witness audit reconstructs separate flow networks in NetworkX
without importing the thesis checker. Every parallel hyperedge copy receives
its own unit gate. Direct route enumeration and resource-set packing agree
with this validator on 192 seeded small instances across all sixteen models.
These finite checks support implementation agreement, not search optimality.
At six completed replacements, all 390 saved witnesses passed the audit.
The audit will be regenerated after all replacements finish.

The renderer requires the declared 384-trial protocol, complete timing
coverage and an independent audit covering every selected checkpoint hash.
It rejects values above supplied upper bounds. Search minima, medians and
maxima remain separate from construction counts. The updated construction
snapshot is stored in manuscript_baseline.json without changing the older
comparison_baseline.json or the historical machine-value cache.

The manuscript now explains the one-hour allocation per variant, timing
replacement rule and lack of machine isolation. Its result tables remain
conditional until the final audit passes. A background finalization command
is waiting for the replacement run. It will audit, render, run the benchmark
tests and rebuild the working PDF without committing or publishing. Its status
and log live in the experiment directory. Visual review remains a separate step.

The 12 targeted benchmark tests passed after the reporting changes. The
working manuscript built successfully and its reference consistency gate
passed. A filename overflow introduced by the new documentation was corrected.

The full suite then finished in 431.095 seconds with 201 tests and no failures.
One optional slow enumeration was skipped. Tests added after that process
started passed separately, including the direct route-packing reference,
invalid-clock rejection and two finalization failure guards. At 21:12 UTC,
eight of the nineteen replacements had completed. The expected finish was
still about 21:40 UTC, followed by the automatic audit and manuscript build.

## Completion, and two defects in the finalization command

All nineteen replacements finished at 21:39:56 UTC. The finalization command
then ran its five stages in sequence. The independent witness audit passed all
403 saved witnesses, the renderer wrote five audited tables from the full
384-trial protocol, the 12 benchmark tests passed, and the reference
consistency gate reported clean. The command then failed at its sixth stage,
the layout warning check, with a UnicodeDecodeError on byte 0xf3 at offset
56920 of `main.log`. That is the non-UTF-8 log recorded in the working notes,
reached this time by a strict Python decode rather than by a locale-sensitive
grep. The check now decodes with `errors="replace"`.

The second defect was silent and mattered more. The `latexmk` stage reported
"Nothing to do for main.tex" three seconds after the tables were written.
Both `main.fls` and `main.fdb_latexmk` held no reference to any
`equal_budget` file. The preceding build had run while those files did not
exist, so each `\IfFileExists` recorded a lookup that failed rather than a
dependency to watch, and the newly written tables could not invalidate
anything. The stage now passes `-g`, which is the same cure the working notes
already prescribe for `record_revision.sh` and `\InputIfFileExists`. Without
it the command would have reported a successful build of a manuscript still
printing the placeholder text that says the audit is in progress.

After the forced rebuild the manuscript is 124 pages, up from 112, carrying
the summary table in Chapter 2 and the four detailed tables in Appendix A.
The gates read 0 overfull, 0 undefined references, 0 LaTeX warnings and 0
occurrences of `??`, counted with `LC_ALL=C grep -a`. The one underfull hbox
is the badness 1168 bibliography line that was already there. The rerun of
the corrected command completed every stage and recorded PDF SHA-256
`e9f1b858...`. The 14 benchmark tests pass, now including the two
finalization guards.

Three runner lock files are excluded from tracking, since `program/` reaches
the hand-in through `git archive`. The frozen `_erdos_fast.so` under
`source/` stays tracked, because the manifest records its hash and the runner
verifies against it.

Not done: the visual review of the five tables, the recorded revision, and
the public snapshot.

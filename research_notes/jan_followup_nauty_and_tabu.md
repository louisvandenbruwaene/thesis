# Jan Goedgebeur's follow-up: the nauty pipeline and tabu search

Status: **VERIFIED / MEASURED cross-checks. Nothing here changes a thesis claim.**
These are the two P2 items from Jan's 2026-06-15 email (see `../TASKS.md`),
executed on 2026-06-18 in an environment where nauty (geng, directg,
watercluster2, multig, ...) is installed, so both became runnable for the first
time. Scripts: [`scripts/nauty_pipeline.py`](scripts/nauty_pipeline.py),
[`scripts/tabu_vs_sa.py`](scripts/tabu_vs_sa.py). Unlike the proof scripts in
this folder, these two intentionally import the thesis program and call nauty:
their whole purpose is to cross-check the program and the tools against each
other, so they are not standalone.

## 1. geng + directg / watercluster2 as a generation pipeline (VERIFIED)

`geng n | directg` orients every edge of each undirected graph in one of three
ways (forward, backward, both) with isomorph rejection, so over geng's output it
emits exactly the non-isomorphic SIMPLE DIGRAPHS on n vertices -- the thesis's
simple-directed object space (two-cycles included). `watercluster2` is the same
generator by a different method.

**Result A (counts agree).** The pipeline's non-iso digraph count equals OEIS
A000273 AND the thesis program's own count (its labelled enumeration
deduplicated by `_canonical_form`). Two independent isomorphism engines, same
numbers:

|  n |  nauty | program | A000273 |
|---:|-------:|--------:|--------:|
|  2 |      3 |       3 |       3 |
|  3 |     16 |      16 |      16 |
|  4 |    218 |     218 |     218 |
|  5 |   9608 |    --   |    9608 |
|  6 | 1540944|    --   | 1540944 |

**Result B (simple-directed extremal value agrees).** Feeding the pipeline's
digraphs through the program's exact max-flow checker reproduces the
simple-directed arc bound L_3^dir(n) the program's own exhaustive `solve`
reports: n = 2,3,4,5 -> 2, 6, 9, 12. (These small-n values sit ABOVE the
asymptotic quadratic `conj:dir-arc` value floor((n+m-2)^2/4): at small n the
near-complete digraph is still feasible because lambda^max is capped by the
out-degree. That is correct, not a contradiction -- the conjecture is the
large-n branch.)

**Result C (watercluster2 is faster -- Jan was right).** Counting all non-iso
simple digraphs:

|  n |   count   | directg | watercluster2 |
|---:|----------:|--------:|--------------:|
|  5 |      9608 |   0.01s |         0.00s |
|  6 |   1540944 |   1.22s |         0.08s |

watercluster2 is ~15x faster at n = 6, matching Jan's "usually faster" remark.
(n = 7 is 882_033_440 digraphs -- generating all of them is out of reach; this
is why a connectivity/arc-count prefilter, not raw generation, is the route for
the simple-directed n = 7 question.)

**Result D (the multigraph hybrid -- the ENUM (b) cross-check Jan flagged as
non-trivial).** A directed multigraph with multiplicities in {0..m-1} has a
simple-digraph SUPPORT. Let nauty do the hard isomorphism reduction on the
support (`geng | directg`), then layer multiplicities {1..m-1} onto its arcs and
deduplicate the finished multigraphs with the program's canonical form. This
reproduces the program's own DFS enumerator at the proved base cases, and is
much faster at n = 5:

|  n | arcs | hybrid classes | DFS classes | hybrid time | DFS time |
|---:|-----:|---------------:|------------:|------------:|---------:|
|  4 |   12 |              2 |           2 |       0.0s  |    0.4s  |
|  5 |   16 |              3 |           3 |      26.3s  |  456.0s  |

The classes match (n=4: doubled star + doubled path; n=5: star, broom, path) and
the hybrid is **~17x faster than the thesis DFS at n = 5**. This is direct
evidence for Jan's central point: the DFS *time* is the bottleneck (his "dedup
only fixed RAM" warning), and pushing the isomorphism reduction into nauty's
generator attacks exactly that.

**Open residue / next step for ENUM (b) at n = 7.** The hybrid as written
deduplicates whole multigraphs with the program's n!-canonical form, which is
fine at n <= 5 but the support-layer dedup does not yet exploit each support's
automorphism group, so it does redundant work and the n = 6 support set (1.5M)
is heavy. To reach the real target -- 24-arc, max-degree-8 multigraphs at n = 7
-- the principled version is: generate supports with `directg -G` (it reports
each support's group size), enumerate multiplicity assignments up to that group,
and prefilter supports by arc-count range and the degree cap. That keeps the
work proportional to non-iso multigraphs, not labelled ones. The pieces are all
present here; only the per-support automorphism dedup is missing.

## 2. Tabu search vs simulated annealing (MEASURED)

Jan suggested tabu search as an alternative discoverer to the thesis's simulated
annealing (`search_for_dense_graph` / `best_of_searches`), "expecting similar
performance but worth quantifying." Both optimise the same energy
`-|E| + penalty * max(0, lambda^max - (m-1))` over the same add/remove
neighbourhood; the annealer is the thesis's own function, the tabu searcher is
in `scripts/tabu_vs_sa.py`. Equal 6s wall-clock budget per method per case
(SA restarted from fresh seeds = `best_of_searches`; tabu restarted on stalls):

| variant            | n | opt | SA best | tabu best | verdict        |
|--------------------|--:|----:|--------:|----------:|----------------|
| simple undirected  | 7 |   9 |       9 |         9 | tie (both opt) |
| multi undirected   | 6 |  10 |      10 |        10 | tie (both opt) |
| simple directed    | 6 |  15 |      15 |        15 | tie (both opt) |
| multi directed     | 5 |  16 |      15 |        16 | TABU +1 (=opt) |
| multi directed     | 7 |  24 |      20 |        24 | TABU +4 (=opt) |
| simple directed    | 7 |  18 |      16 |        18 | TABU +2 (=opt) |

**Finding (sharper than Jan expected).** Tabu *ties* simulated annealing on the
undirected and small directed cases, but **clearly beats it on the harder
directed cases**: tabu reaches each construction optimum -- including the 24-arc
2B(3,4) extremiser that is exactly the L_3^dir(7) = 24 lower bound of ENUM (b) --
while the annealer stalls below it in equal time. The gap is largest precisely
on the directed multigraph variant, the densest and most-parallel model, where
the annealer's random walk struggles to assemble the structured bipartite
optimiser and tabu's best-improvement step climbs to it.

**Caveats.** (a) "SA" here is the thesis annealer with default parameters
started from the empty graph (which is exactly what `best_of_searches` does --
no bipartite seeding; the bipartite/noisy-bipartite starts in the log were for
the separate *fractional* search). A bipartite-seeded annealer would likely also
reach these optima. (b) The tabu searcher evaluates the full neighbourhood each
step, so it does more work per step; the comparison is at equal wall-clock, which
is the fair end-user metric. (c) Quality only -- neither is a proof; the values
are construction lower bounds, reached or not.

**Suggested use.** If the discovery chapter ever wants a stronger default
engine for the directed (especially multigraph) cases, tabu search is the better
choice here and is a small addition. Not pursued into the thesis text: the
discovery results there are already at the proved/constructed optima, so this is
an engineering note, not a new result.

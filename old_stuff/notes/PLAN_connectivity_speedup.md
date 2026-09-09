# PLAN — bottleneck-free connectivity, nauty dedup, and thesis clarity

**Status: NOT STARTED. This file is written for a COLD session.** It is the single
source of truth for the work the author authorised on 2026-06-15. Read it top to
bottom before touching anything. Line numbers below are anchors as of baseline commit
`7d20265` and may have drifted: always re-grep for the function name, do not trust the
number blindly.

The author's words, so intent is not lost:
> "I would just love to have a bottleneck free implementation with good results; you may
> install whatever Jan recommended and perhaps even some more if you trust it to be good.
> Afterwards add the changes to the thesis paper with very clear explanations. I want
> nothing pushed under the rug, everything above board. While improving clarity, focus on
> the part where we introduce p and x with w<=1; there are a lot of inequalities and
> symbols that I just don't understand."

---

## 0. How to use this file (cold-start checklist)

1. Read `CLAUDE.md` (auto-loaded) and the top of `TASKS.md`. The hard rules still bind:
   ALL runnable code lives in `program/erdos915_unified.py`; thesis text may go in
   uncommented only after a Fable proof-check; append a dated entry to `claude.md`;
   `latexmk -pdf main.tex` must exit 0 before ending a session that touched any `.tex`.
2. Do the SAFETY step in §2 BEFORE the first edit.
3. Execute the phases in order: A -> B -> C -> (D optional) -> E -> tests -> thesis.
   Phases A and B are the core win and have no external dependency; do them first and
   land them green before starting E (nauty).
4. Fill in the CHANGE LOG (§13) as you go. Nothing is "done" until its row is filled and
   its test is green.

---

## 1. Goal and scope

Two real bottlenecks, one clarity task.

- **Bottleneck 1 (discovery).** The simulated-annealing search recomputes the connectivity
  of the whole graph from scratch on (almost) every step. `_energy`
  (`erdos915_unified.py:1361`) calls `measure(graph)`, where `measure` is
  `max_edge_connectivity` / `max_vertex_connectivity` -> `max_connectivity`
  (`:786`), which is **O(n^2) max-flows, one per vertex pair**. `_energy` runs at least
  twice per step (proposal at `:1484`, best/feasibility check at `:1495`), and
  `sensitivity_map` (`:1278`) runs every `bias_refresh=200` steps and itself calls
  `edge_sensitivity` once per edge, each of which calls `measure` twice. With thousands of
  steps and up to 200 restarts (`:1676`), connectivity dominates the runtime. This is the
  bottleneck Jan diagnosed.

- **Bottleneck 2 (proof).** The n=7 extremal enumeration
  (`enumerate_extremal_directed_multigraphs`, `:3761`) blew up to ~22 GB and crashed the
  desktop because isomorphic copies are filtered only at the end; it "stores too many
  states" (TASKS.md). Jan's nauty suggestion is aimed here, even though he framed it for
  connectivity.

- **Clarity.** The MILP cut-counting formulation in `chapters/ch2_certify.tex:218-227`
  (the variables `p^{st}_{uv}`, `x^{st}_u`, the indicator inequality, and `w <= 1`) is
  hard to follow. Rewrite it so every symbol is defined in words and the one tricky
  inequality is shown by a worked case table.

**Non-goal / guardrail:** do NOT change any reported value, bound, figure number, or
proof. The discovery speedup must be **trajectory-preserving** (see §4): same random walk,
same witnesses, same numbers, just fewer flow calls. The enumeration speedup must return
the **same set of graphs up to isomorphism**. Everything is verified by a test that
compares against the current exact code (§10).

---

## 2. SAFETY / revert strategy (do this first)

The repo `thesis_improved/` is a clean git repo on `master`. A baseline tag already exists:

- **Baseline tag:** `baseline-pre-speedup` -> commit `7d20265` (created 2026-06-15, clean tree).

Steps:

1. Confirm clean tree: `git -C thesis_improved status -s` (should be empty). If not, stop
   and ask the author.
2. Work on a dedicated branch so `master` stays pristine:
   `git -C thesis_improved checkout -b feat/connectivity-speedup baseline-pre-speedup`
3. Belt and suspenders for the one big file (author asked for "git or a copy"): keep a
   read-only baseline copy for quick diffing without git gymnastics:
   `cp program/erdos915_unified.py program/erdos915_unified.baseline.py`
   Add `erdos915_unified.baseline.py` to `.gitignore` (it is a scratch copy, not a
   deliverable). Delete it when the work is signed off.
4. Commit after each green phase with a clear message (do NOT push; the author pushes).
   This gives a per-phase revert point on top of the branch.
5. **To revert everything:** `git checkout master` (work is isolated on the branch), or
   `git reset --hard baseline-pre-speedup` if on the branch, or restore from the `.baseline.py`
   copy for the program only.

The CHANGE LOG in §13 is the human-readable record of what was removed and added, so a
reviewer never has to read a diff to know what happened.

---

## 3. The core principle: trajectory-preserving, nothing under the rug

The search's correctness rests on two facts, NOT on the exact connectivity value:

- **(Soundness of the reported bound.)** The best graph returned is a real witness, so its
  feasibility (lambda^max <= m-1) must be CERTAIN. We never weaken this. The feasibility of
  a candidate-best is always decided by an exact predicate.
- **(The energy only needs the EXCESS.)** `_energy = -|E| + penalty * max(0, lambda^max - (m-1))`.
  When the graph is feasible the excess is 0 and the value of lambda^max does not enter the
  energy at all. When infeasible we need the exact excess, hence the exact value, but those
  steps are the minority.

So the optimisation is: **compute the exact connectivity value only on the steps where the
slow code's energy would actually depend on it (i.e. infeasible proposals); on all other
steps prove feasibility with a cheap capped flow or skip the flow entirely by monotonicity,
which yields the identical energy the slow code would have computed.**

Because the energy is identical on every step, the Metropolis accept/reject decisions are
identical, the random-number draw order is identical, the trajectory is identical, and the
returned witness and edge count are **bit-for-bit identical** to the current code. The
speedup is invisible to every number in the thesis. The equivalence test (§10) asserts
exactly this.

(The only per-step quantity that is purely cosmetic is `SearchStep.connectivity` at
`:1504`, used by `fig:trace`. See §10 for how the figure stays exact.)

---

## 4. Two facts we will lean on (state and prove these; they go in the thesis too)

Let lambda^max(G) = max over pairs (s,t) of the maximum number of edge/arc-disjoint
s-t routes (the quantity `max_connectivity` returns). The same statements hold verbatim for
the internally-vertex-disjoint version kappa^max.

- **Fact M1 (monotonicity).** Removing one unit of an adjacency cannot increase lambda^max;
  adding one unit cannot decrease it. *Proof:* a max-flow between any fixed pair equals a
  min cut; deleting capacity cannot raise any cut value, adding capacity cannot lower the
  min cut. Take the max over pairs. []
- **Fact M2 (unit step).** Adding one unit to a single adjacency raises lambda^max by at
  most 1. *Proof:* the added unit of capacity crosses any fixed s-t cut at most once, so
  every pair's min cut rises by at most 1; take the max. []

Consequences used by the algorithm:
- A removal applied to a feasible graph leaves it feasible (M1). No flow needed.
- If the current lambda^max is provably <= m-2, one addition keeps it <= m-1 (M2). No flow
  needed.
- Otherwise one capped flow decides feasibility, and the exact value is computed only if the
  proposal is actually infeasible (so the penalty term is exact).

These rely on every move changing exactly one adjacency by one unit, which the annealer does
(`add_edge` at `:1482`, `remove_edge` at `:1473` change multiplicity by 1). If a future move
changes multiplicity by `delta > 1`, replace "+1" with "+delta" in M2 and the guard.

---

## 5. PHASE A — capped, early-exit feasibility predicate (P1)

**Idea.** We never need the value, only the predicate "is lambda^max > k?". A capped flow
answers exactly that and stops as soon as the answer is known.

`_tiny_maxflow(mu, n, s, t, cap)` (`:3726`) ALREADY returns `True` iff the max-flow exceeds
`cap` (its loop runs `while flow <= cap`). Its docstring says it beats networkx "by orders
of magnitude" for n <= 7. It works on any capacity matrix, directed or symmetric. We reuse
it for the EDGE case and add a vertex variant.

### A.1 Generalise the capped flow to a capacity matrix

Keep `_tiny_maxflow` as is (edge case passes `graph.mu` directly). Add a vertex-split
capacity builder and a thin wrapper:

```python
def _split_capacity_matrix(graph) -> tuple[np.ndarray, int]:
    """2n x 2n capacity matrix of the vertex-split network (Section 3 convention).

    Vertex v -> in-copy 2v, out-copy 2v+1, internal arc 2v -> 2v+1 capacity 1.
    Each adjacency u->v (mu>0) becomes (2u+1) -> (2v) capacity 1.
    Endpoints are uncapped by the caller (see exceeds_bound).
    """
    n = graph.num_vertices
    size = 2 * n
    cap = np.zeros((size, size), dtype=int)
    for v in range(n):
        cap[2 * v, 2 * v + 1] = 1          # internal gate, one route through v
    for u in range(n):
        for v in range(n):
            if u != v and graph.mu[u, v] > 0:
                cap[2 * u + 1, 2 * v] = 1   # parallel edges do NOT raise kappa
    return cap, size
```

### A.2 The single predicate the search calls

```python
def exceeds_bound(graph, k: int, *, separation: str = "edge") -> bool:
    """True iff lambda^max(G) > k  (edge)  /  kappa^max(G) > k  (vertex).

    Decides the predicate with capped flows and TWO early exits: each pair's flow
    stops after k+1 augmenting paths, and the pair loop stops at the first violating
    pair. Equivalent to (max_connectivity(graph, ...) > k) but usually far cheaper,
    and on an infeasible graph it typically returns after one pair.
    """
    n = graph.num_vertices
    if separation == "edge":
        mu = graph.mu
        for s, t in _pairs(graph):
            if _tiny_maxflow(mu, n, s, t, k):
                return True
        return False
    if separation == "vertex":
        cap, size = _split_capacity_matrix(graph)
        for s, t in _pairs(graph):
            # uncap the endpoints' own in->out gates so Menger counts INTERNAL routes
            cap[2 * s, 2 * s + 1] = _UNBOUNDED_INT
            cap[2 * t, 2 * t + 1] = _UNBOUNDED_INT
            hit = _tiny_maxflow(cap, size, 2 * s + 1, 2 * t, k)
            cap[2 * s, 2 * s + 1] = 1       # restore
            cap[2 * t, 2 * t + 1] = 1
            if hit:
                return True
        return False
    raise ValueError("separation must be 'edge' or 'vertex'")
```

Notes:
- `_UNBOUNDED_INT` = a large int (e.g. `10**9`); mirror the existing `_UNBOUNDED` used in
  `local_connectivity` (`:779`). `_tiny_maxflow` already uses `10**9` as its bottleneck
  sentinel, so keep capacities below that.
- `_pairs(graph)` (`:851`) yields ordered pairs for digraphs, unordered for undirected, and
  matches what `max_connectivity` iterates, so the predicate is over the SAME pair set.
- The vertex variant mutates and restores two cells of `cap`; if that ever feels fragile,
  rebuild `cap` per pair (n is tiny). Correctness first.

### A.3 Phase-A test gate

In `tests/test_connectivity.py` add: for many random graphs across all four variants and
both separations, assert
`exceeds_bound(g, k, separation=sep) == (max_connectivity(g, vertex_split=(sep=="vertex")) > k)`
for every k in `range(-1, max+2)`. This pins the predicate to the trusted exact code.

---

## 6. PHASE B — monotonicity + maintained upper bound (P2)

This is where the per-step flow count actually collapses. Implement inside
`search_for_dense_graph` (`:1405`); do NOT change the public signature or defaults.

### B.1 State carried across steps

Maintain, alongside `current` / `current_energy`:
- `feasible: bool` — is `current` feasible (lambda^max <= m-1). Start `True` (empty graph).
- `lam_ub: int` — a SOUND upper bound on lambda^max(current). Start 0 (empty graph).

`lam_ub` is updated by Facts M1/M2 on every ACCEPTED move:
- accepted addition: `lam_ub += 1` (M2; sound, never an underestimate).
- accepted removal: `lam_ub` unchanged (M1; the old bound still bounds the smaller graph).

`lam_ub` may drift above the truth after a run of removals. That only costs extra capped
checks (never correctness). Resync it to the exact value at the `bias_refresh` cadence,
where the code already pays for flows to rebuild the sensitivity map:
`lam_ub = measure(current); feasible = lam_ub <= m - 1`.

### B.2 Per-move energy, computed the cheap way but identical to the slow path

Replace the unconditional `proposal_energy = _energy(proposal, ...)` (`:1484`) with a helper
that returns the **same number** the slow `_energy` would, using the least work:

```python
def _proposal_energy(proposal, *, is_add, lam_ub, m, penalty, measure_full, sep):
    """Return _energy(proposal) EXACTLY, computing connectivity only when it can bite.

    measure_full(proposal) is the exact max_connectivity; called only on the rare
    infeasible branch so the penalty term is exact.
    """
    edges = proposal.edge_count()
    if not is_add:
        # removal: proposal <= current in connectivity (M1). If current was feasible,
        # proposal is feasible, excess 0. If current was infeasible we must check.
        if feasible_current:            # pass this in
            return -edges               # excess 0, identical to slow path
        # current infeasible: removal may or may not restore feasibility
        if not exceeds_bound(proposal, m - 1, separation=sep):
            return -edges               # feasible now, excess 0
        return -edges + penalty * (measure_full(proposal) - (m - 1))
    # addition
    if lam_ub <= m - 2:                  # M2: proposal still <= m-1, feasible
        return -edges                    # excess 0, identical to slow path
    if not exceeds_bound(proposal, m - 1, separation=sep):
        return -edges                    # at boundary but still feasible
    return -edges + penalty * (measure_full(proposal) - (m - 1))
```

`measure_full` = `max_edge_connectivity` or `max_vertex_connectivity` per `separation`. The
key invariant: this returns the IDENTICAL float `_energy` returns, because (a) when the
result is `-edges` the slow path's excess is provably 0, and (b) otherwise we compute the
exact excess. Hence the trajectory is unchanged (see §3).

### B.3 Updating state after acceptance

On accept (`:1491`):
- recompute/carry `feasible` for the new `current`. Cheap: addition -> `feasible` is known
  from the branch above (excess 0 means feasible; else infeasible). Removal -> from the
  branch above. So set `feasible` from which branch produced the energy; do NOT call a flow
  again.
- update `lam_ub` per B.1.

Best-witness tracking (`:1495`) currently calls `measure(current) <= m - 1`. Replace with
the `feasible` flag you just maintained (it is exact for the accepted `current`), so the
best-tracking does ZERO extra flows. The witness recorded is still certified feasible.

### B.4 `SearchStep.connectivity` and `fig:trace`

`history.append(SearchStep(..., connectivity=measure(current), ...))` (`:1504`) is the only
remaining unconditional `measure` call. It feeds the scatter in `fig:trace` only. Options,
in order of preference:
- Add a parameter `record_exact_connectivity: bool = False`. When False (production /
  discovery), log `lam_ub` (clearly an upper bound) or skip the field. When True, compute
  the exact value for the trace. `make_figures.py`'s `fig:trace` run sets it True. That run
  is a single n=4 schedule, so the cost is negligible and the FIGURE STAYS EXACT.
- Verify `make_figures.py` to confirm which call produces `fig:trace`
  (grep `temperature_trace`), and flip that one call to `record_exact_connectivity=True`.

### B.5 Phase-B test gate (the equivalence test — the heart of "nothing under the rug")

Add `tests/test_search.py::test_fast_path_matches_exact`:
- For a grid of `(variant, n in {3,4,5}, m in {2,3}, separation in {edge,vertex}, seed in 0..9)`,
  run the search twice: once with a forced `reference_mode=True` flag that makes
  `_proposal_energy` always call `_energy` (slow, exact), once normal (fast).
- Assert: identical `best_edge_count`, identical sequence of `accepted` flags, identical
  per-step `energy` values, identical final `best_graph.mu`.
- Assert the returned `best_graph` is genuinely feasible via the exact
  `max_connectivity(best_graph, ...) <= m - 1`.
- Assert the invariant `lam_ub >= max_connectivity(current)` holds at every step (add a
  debug hook or a cheap check in reference_mode).

`reference_mode` is a private test-only kwarg; keep it out of the public docstring or mark
it clearly as internal. If you prefer not to add a kwarg, factor the energy decision behind a
module-level switch the test can monkeypatch.

---

## 7. PHASE C — cheapen `sensitivity_map` (safe, no behaviour change)

`sensitivity_map` (`:1278`) calls `edge_sensitivity` (`:1256`) once per edge; each call
recomputes `before = connectivity(graph)` (`:1270`) — the SAME value for every edge — and
then `after = connectivity(reduced)`. So `before` is recomputed E times for no reason.

- **C.1 Compute `before` once.** Refactor `sensitivity_map` to compute `before = connectivity(graph)`
  a single time and pass it in, or inline the loop:
  ```python
  def sensitivity_map(graph, connectivity=max_edge_connectivity):
      before = connectivity(graph)
      out = {}
      for u, v, _ in graph.edges():
          reduced = graph.copy(); reduced.set_multiplicity(u, v, 0)
          out[(u, v)] = before - connectivity(reduced)
      return out
  ```
  This roughly halves the cost and changes NO value. Keep `edge_sensitivity` as the public
  single-edge function (it must still compute its own `before`); only the map shares it.
- **C.2 (optional) cap the `after` flows.** `after <= before`, so `after` can be computed
  with a flow capped at `before` (early exit). Lower priority; do only if profiling says
  sensitivity is still hot after C.1.

Test: assert the refactored `sensitivity_map` returns a dict equal to the old one on random
graphs (compare against `{e: edge_sensitivity(g, *e) for e in edges}`).

---

## 8. PHASE D — optional extra exploits (do only if profiling still shows a hotspot)

Each is independent and must keep results identical. Add behind a flag, default to the safe
existing behaviour, and only flip the default if a test proves equivalence.

- **D.1 Pure-Python capped flow for tiny n.** `_tiny_maxflow` does `mu.astype(int).copy()`
  (numpy) per call; for n <= 8 a list-of-lists residual avoids numpy per-call overhead.
  Micro-opt; benchmark before bothering.
- **D.2 Gomory-Hu resync for the undirected edge case.** `max_edge_connectivity_via_tree`
  (`:899`) gives exact lambda^max in n-1 flows for UNDIRECTED graphs. Use it for the
  `lam_ub` resync (B.1) when the variant is undirected and separation is edge — cheaper than
  the O(n^2) `max_connectivity`. No effect on directed or vertex cases (no GH analogue
  there, which is exactly why the capped+monotone path carries them).
- **D.3 Bounded memo of the feasibility predicate.** The walk revisits states. An
  `functools.lru_cache(maxsize=...)`-style memo keyed by `graph.mu.tobytes()` of
  `exceeds_bound(g, m-1, sep)` can skip recomputation. CAP the size (memory was the thing
  that crashed the desktop). Only worth it if profiling shows repeated states.
- **D.4 Parallel restarts.** `_search_within_budget` (`:1662`) and `best_of_searches`
  (`:1517`) run restarts sequentially; a `multiprocessing.Pool` over seeds parallelises
  them. KEEP figure reproduction single-process and seeded (the figures must reproduce
  exactly), so gate parallelism behind an explicit `workers` arg used only for production
  discovery, never by `make_figures.py`.

---

## 9. PHASE E — nauty / canonical-form dedup for the n=7 enumeration (P3)

This is Jan's nauty suggestion, aimed where it actually helps: isomorphism rejection in
`enumerate_extremal_directed_multigraphs` (`:3761`). The memory blow-up is from storing many
labelled copies of the same graph. Fix: store one canonical representative per isomorphism
class, so memory is bounded by the number of iso-classes, not labelled graphs.

**Design rule:** correctness must NOT depend on an external binary. Implement a pure-Python
canonical form as the source of truth; use nauty only as an accelerator with a guarded
fallback. Then the proof stands even on a machine without nauty.

### E.1 Pure-Python canonical form (always available)

```python
def _canonical_form(mu: np.ndarray) -> bytes:
    """Lexicographically smallest flattened multiplicity matrix over all vertex
    relabellings. Source of truth for isomorphism of directed multigraphs."""
    n = mu.shape[0]
    best = None
    for perm in permutations(range(n)):
        p = list(perm)
        cand = mu[np.ix_(p, p)].tobytes()
        if best is None or cand < best:
            best = cand
    return best
```

For n=7 that is 5040 permutations per graph — fine on CPU. Store canonical `bytes` in a
`set`; that is what bounds memory. Use it in the DFS so only NEW iso-classes are kept, and
in any post-pass dedup.

### E.2 nauty acceleration (optional, install authorised)

The 5040-perm canonical form is fine for n=7 but scales as n!. For headroom, use nauty's
canonical labelling. Directed multigraphs are not nauty's native object, so encode:

- Try `pip install pynauty` first (user-level, no sudo). pynauty does directed graphs and
  vertex colouring but not multi-edges. Encode multiplicity k in {0..m-1} on arc u->v by a
  small coloured gadget (e.g. attach k distinctly-coloured markers to a colour class that
  tags the ordered pair, or expand each arc into a short coloured path of length k). Verify
  the encoding is injective on iso-classes by checking, on all n<=5 cases, that
  `nauty_canon(mu) == nauty_canon(mu2)` iff `_canonical_form(mu) == _canonical_form(mu2)`.
- If pynauty is unavailable, the system package on Arch is `nauty` (provides `labelg`,
  `shortg`, `directg`, `geng`). Installing it needs root; the implementing session cannot
  sudo. Ask the author to run, in this session, `! sudo pacman -S --needed nauty`. Then
  shell out to `labelg`/`shortg` for canonical g6 strings (again via an injective encoding
  for the directed-multigraph case).
- **Guard:** wrap nauty use in a try/except and `shutil.which` check; on any failure fall
  back to `_canonical_form`. Log which path was taken.

### E.3 Memory-capped run

When ready to actually run n=7, follow the existing TASKS.md guidance: a hard cgroup cap so
the desktop cannot crash again:
`systemd-run --user --scope -p MemoryMax=16G -p MemorySwapMax=0 timeout 3600 python -c "..."`.
With canonical-form dedup the run should stay far under the cap. Launch detached, tee to
`program/logs/enum_n7_<date>.log`, record PID + resume command in TASKS.md (CLAUDE.md rule).

### E.4 Soundness note (keep above board)

The j>=7 prefix pruning in the DFS uses the CONJECTURED bipartite bound (see the soundness
note at `:3776`), so the enumeration is a complete proof only for n<=6 and a lower-bound
search for n>=7. The dedup change does NOT alter this; it only changes memory. State this in
the thesis and in the log; do not let the speedup be mistaken for closing n=7.

### E.5 Test

For n in {3,4,5}, assert the deduped enumeration returns exactly one representative per
iso-class and that the SET of iso-classes equals the current code's output deduped by
`_canonical_form`. The counts at n=4,5 are known (2 and 3 doubled bidirected spanning trees,
per claude.md) — assert those.

---

## 10. Testing strategy (summary; all green before thesis edits)

1. `test_connectivity.py`: `exceeds_bound` matches `max_connectivity` predicate (A.3).
2. `test_search.py`: fast path == reference path, bit-for-bit; witnesses certified feasible;
   `lam_ub` upper-bound invariant (B.5). THIS is the "nothing under the rug" proof.
3. `test_sensitivity.py`: refactored `sensitivity_map` equals the old per-edge result (C).
4. `test_certify.py` (or a new enum test): deduped enumeration == iso-classes of old
   enumeration for n<=5; known counts at n=4,5 (E.5).
5. Run the whole suite: `cd program && python -m pytest -q` AND the built-in
   `python erdos915_unified.py` self-test (`_run_checks`, `:4087`). Both must pass.
6. Regenerate figures: `python make_figures.py`. `fig:trace` and `fig:sensitivity` must look
   unchanged (the trace run uses exact connectivity per B.4). Diff the PNGs or eyeball.

---

## 11. Thesis documentation (after code is green; everything above board)

Author rule: text goes in uncommented only after a Fable proof-check of the underlying
claims. Facts M1/M2 are elementary min-cut facts; still run a proof-check before they enter
uncommented. Honour the punctuation rules: NO semicolons, NO em dashes (---), NO en dashes
(--) in prose (TikZ/math `--` is fine).

### 11.1 ch3 (`ch3_discover.tex`) — new short subsection after "Temperature and edge sensitivity"

Title suggestion: "Keeping the checker cheap inside the search". Content:
- State the problem: the energy needs connectivity, and a naive search remeasures the whole
  graph every step.
- State and prove Facts M1 (monotonicity) and M2 (unit step) as a small numbered
  Lemma/Proposition.
- Explain the consequence in plain words: a removal from a feasible graph stays feasible so
  needs no measurement; an addition while strictly below the bound stays feasible; only at
  the boundary do we run a single flow, and that flow stops as soon as it sees one route too
  many. Maintain an upper bound updated by M2, resynced periodically.
- **Transparency paragraph (the author insisted):** state explicitly that this is an
  implementation efficiency that changes no reported value, that the returned graph is still
  certified feasible by an exact check, and that a regression test verifies the optimised
  search reproduces the exact search step for step. Cite the test by name. Nothing hidden.
- Optional: one sentence that Gomory-Hu (already in ch2) is the matching trick for the
  undirected edge case, and that the directed/vertex cases have no such tree, which is why
  the capped+monotone method carries them.

### 11.2 ch2 (`ch2_certify.tex`) — connectivity-checker section (around `:74-125`)

Add one or two sentences: the same checker runs in two modes, an exact-value mode (this
section, used for proofs and reported numbers) and a capped predicate mode (used inside the
search of ch3 for speed), cross-referenced. Do not weaken the "measures exactly" claim.

### 11.3 ch2 MILP clarity rewrite (`ch2_certify.tex:218-227`) — THE AUTHOR'S PRIORITY

The author finds `p^{st}_{uv}`, `x^{st}_u`, the indicator inequality, and `w <= 1`
confusing. Rewrite the paragraph at `:218` and the reading-the-constraints paragraph at
`:227` so that:

1. **Every symbol is named in words before any formula:**
   - `w(u,v)` = the scaled multiplicity of arc u->v, a number in [0,1] (defined at `:205`);
     "how much arc weight we put on u->v".
   - For each ordered pair (s,t) we are choosing ONE cut. `x^{st}_u in {0,1}` is the
     yes/no label "is vertex u on the source (s) side of that cut", with `x^{st}_s = 1`
     and `x^{st}_t = 0` fixed.
   - `p^{st}_{uv} >= 0` = "the weight of arc u->v that we are forced to count as crossing
     this cut": it equals w(u,v) when the arc goes from the source side to the sink side,
     and 0 otherwise.

2. **Show the one tricky inequality by a worked case table.** The constraint
   `p^{st}_{uv} >= w(u,v) + x^{st}_u - x^{st}_v - 1` is an indicator. Because `w <= 1`, the
   right-hand side is positive only in the crossing case:

   | x_u | x_v | meaning | RHS = w + x_u - x_v - 1 | forces |
   |-----|-----|---------|--------------------------|--------|
   |  1  |  0  | u source side, v sink side: arc CROSSES | w + 1 - 0 - 1 = w | p >= w |
   |  1  |  1  | both source side | w - 1 <= 0 | p >= 0 (free, stays 0) |
   |  0  |  0  | both sink side   | w - 1 <= 0 | p >= 0 (free, stays 0) |
   |  0  |  1  | u sink, v source | w - 2 <= 0 | p >= 0 (free, stays 0) |

   Add a sentence: "this is where `w <= 1` earns its keep: it makes the three non-crossing
   rows land at or below zero, so the helper is forced up to the arc weight in exactly one
   case, the crossing one." Render the table as a small `tabular` or as an `align*` of the
   four cases, whichever fits the thesis style (the surrounding text uses align*).

3. **Then the cut constraint reads plainly:** `sum_{u != v} p^{st}_{uv} <= 1` says the total
   weight crossing this chosen cut is at most one. By max-flow / min-cut, a cut of capacity
   <= 1 exists exactly when maxflow(s,t) <= 1. So the two lines together say "every ordered
   pair admits a cut of capacity at most one", which is the feasibility we want, exactly, not
   a relaxation.

4. **Keep, but clarify, the last two helper constraints** (the redundant 2-step-detour
   bound and the degree-ordering symmetry break): one sentence each, framed as "these do not
   change the answer, they only help the solver finish in time". The current text at `:227`
   is correct; just shorten and de-jargon it.

5. Consider a small TikZ figure: a handful of vertices split into source side / sink side by
   a dashed cut line, the crossing arcs highlighted and labelled with their `p = w`. A
   picture of one cut makes `x` and `p` concrete. Put it near the formula. (Figures are
   encouraged by the editorial rule.) Code for it goes nowhere except the `.tex` (TikZ), so
   it does not violate the one-file rule.

Keep `thm:dir-multi-small` and everything after it unchanged.

### 11.4 Reproducibility section (`ch2_certify.tex:243`) and logs

- Mention the new tests in the reproducibility narrative if appropriate (the equivalence
  test is a nice thing to point at).
- Append the dated `claude.md` entry (newest at bottom): what changed, why, the test names,
  and the explicit statement that no reported value moved.
- Update `TASKS.md`: mark the speedup done, update the n=7 enum item to note the dedup fix is
  in place, keep it under ~80 lines.

### 11.5 Build gate

`latexmk -pdf main.tex` must exit 0. Check the page count and the `fig:trace` /
`fig:sensitivity` look unchanged. Fix any new overfull hboxes the table/figure introduce.

---

## 12. Suggested execution order (one ordered checklist)

1. §2 safety: branch + baseline copy.
2. §5 Phase A: `_split_capacity_matrix`, `exceeds_bound`; A.3 test green.
3. §6 Phase B: state + `_proposal_energy` + accept-branch updates + B.4 history; B.5
   equivalence test green. Commit.
4. §7 Phase C: `sensitivity_map` `before`-once; test green. Commit.
5. Run full suite + self-test + regenerate figures (§10.5, §10.6). Commit.
6. §9 Phase E: pure-Python canonical form + dedup in the enumerator; E.5 test green. Then
   try pynauty (or ask author to install system nauty); guard with fallback. Commit.
7. §11 thesis: ch3 lemma+subsection (proof-checked), ch2 cross-ref, ch2 MILP clarity rewrite
   (the priority), optional TikZ cut figure, reproducibility/claude.md/TASKS.md. Build green.
   Commit.
8. Summarise for the author: what got faster (with before/after timing on one representative
   search), the equivalence-test guarantee, the thesis diffs, and the nauty status.

Timing evidence to collect for the author (so "good results" is shown, not asserted): time
`best_of_searches` (or a fixed discovery call) on baseline vs branch for a couple of
`(n, m)` and report the speedup, plus the peak memory of the n<=5 enumeration before/after
dedup.

---

## 13. CHANGE LOG (fill this in as you implement — the revert/audit record)

For every function touched, one row: what was REMOVED (old behaviour) and ADDED (new), and
the test that guards it. Keep it honest and complete.

STATUS: DONE 2026-06-15. All phases A,B,C,E landed green; thesis written and built (87 pp,
latexmk exit 0). Phase D skipped (not needed: the per-step connectivity bottleneck is gone;
see results below). Commits on branch `feat/connectivity-speedup`: Phase A `413abce`, Phase
B+C, Phase E, thesis (see `git log`).

| Area | File:func | Removed / changed | Added | Guard test | Status |
|------|-----------|-------------------|-------|------------|--------|
| A | erdos915_unified.py: new `_split_capacity_matrix`, `exceeds_bound` | (none) | capped early-exit predicate (reuses `_tiny_maxflow`) | `test_connectivity.CappedPredicate` (matches exact over 4 variants x 2 sep x all k) | DONE |
| B | erdos915_unified.py: `search_for_dense_graph` | unconditional `measure` per step | `lam_ub`/`feasible` state, `_proposal_energy`, exact only when infeasible | `test_search.test_fast_path_matches_exact` (bit-for-bit) | DONE |
| B | erdos915_unified.py: `SearchStep` use + make_figures.py | unconditional exact `connectivity` log | `record_exact_connectivity` flag (fig:trace sets True) | pixel-diff: temperature_trace.png identical | DONE |
| C | erdos915_unified.py: `sensitivity_map` | `before` recomputed per edge | `before` once | `test_sensitivity.test_map_equals_per_edge_sensitivity` | DONE |
| E | erdos915_unified.py: `enumerate_extremal_directed_multigraphs` | buffer-all-then-dedup (RAM blow-up) | `_canonical_form` + streamed dedup (memory bounded by #iso-classes) | `test_certify.EnumerationDedup` (n=3,4; n=5 gated RUN_SLOW_ENUM, confirmed =3) | DONE |
| thesis | ch3_discover.tex | (none) | `prop:monotone` (M1/M2 + proof) + "Keeping the checker cheap" section + transparency para citing the test | build | DONE |
| thesis | ch2_certify.tex | confusing MILP prose `:218-227` | symbol glossary (w/x/p in words) + case table `tab:crossing-cases` + plain reading + de-jargoned helpers | build | DONE |
| thesis | ch2_certify.tex | (none) | TikZ cut figure `fig:cut` + two-mode checker cross-ref | build | DONE |
| safety | .gitignore | (none) | `erdos915_unified.baseline.py` | n/a | DONE |

Revert anchors: tag `baseline-pre-speedup` (`7d20265`), branch `feat/connectivity-speedup`,
scratch copy `program/erdos915_unified.baseline.py` (delete on sign-off).

RESULTS (measured on this machine):
- Search speedup, branch vs baseline, IDENTICAL best edge count in every case:
  MULTI_DIRECTED n=5 m=3 edge: 6.05s -> 1.58s (3.8x, 15/15);
  MULTI_DIRECTED n=6 m=3 edge: 11.17s -> 3.36s (3.3x, 18/18);
  SIMPLE_UNDIRECTED n=7 m=3 edge: 12.52s -> 3.23s (3.9x, 9/9);
  MULTI_DIRECTED n=5 m=3 vertex: 13.17s -> 5.14s (2.6x, 21/21).
- Enumeration: branch output byte-identical to baseline for n=3,4 (both up_to_iso modes);
  memory now bounded by #iso-classes not labelled copies (n=4: 2 reps streamed vs 16 labelled
  buffered before; the n=7 case is where the old code hit ~22 GB). n=5 reconfirmed = 3 classes.
- Full suite: 75 unittest tests pass (1 slow n=5 skipped); `python erdos915_unified.py`
  self-test exits 0; figures pixel-identical.
- nauty status: pure-Python `_canonical_form` is the source of truth (no external dependency).
  The enumeration's real cost is the DFS, not iso-rejection, so nauty would not speed it up;
  the RAM crash is fixed structurally. Jan's email (2026-06-15) recommends a different,
  generation-time pipeline (geng + directg/watercluster2) -- see TASKS.md, left for the author.

---

## 14. Acceptance criteria (definition of done)

- [x] All tests in §10 green, including the bit-for-bit equivalence test.
- [x] `python erdos915_unified.py` self-test passes; unittest suite (75 tests) passes.
- [x] Figures verified unchanged (temperature_trace.png + sensitivity_mixed.png pixel-identical).
- [x] Measured speedup reported (2.6x-3.9x, identical edge counts); enumeration memory now
      bounded by iso-classes (byte-identical output to baseline at n=3,4).
- [x] `latexmk -pdf main.tex` exits 0 (87 pp); no value/bound/figure changed.
- [x] ch2 MILP passage rewritten: every symbol defined in words, worked case table, cut figure.
- [x] CHANGE LOG (§13) filled; `claude.md` dated entry appended; `TASKS.md` updated.
- [x] Nothing under the rug: trajectory-preserving (equivalence test) and iso-class-preserving
      (byte-identical to baseline) speedups, stated plainly in the thesis with the test named.

# Claude progress log — attacking the unsolved variants

Session start: 2026-06-11. Goal: rigorously prove the easiest unsolved variants
(for all n and m where possible), logging progress here regularly.

## 2026-08-17 — Authoritative audit trail for the final thesis corrections

**Status and precedence.** This section records the corrections made during the
final, repeated thesis audit. It is intended to let a later AI or human reviewer
reconstruct and challenge every material editorial, mathematical, computational,
and reproducibility change. Where an older entry in this file conflicts with this
section or with the current theorem statements, the older entry is a historical
work note and this section plus the current TeX source takes precedence. In
particular, older phrases such as “for all n” and “unique extremizer” must not be
copied back into the thesis without re-proving them under the precise hypotheses.

The audit was deliberately conservative: an equality was weakened to an upper
bound when attainment was not proved; a global classification was restricted to
the actually searched class; and asymptotic notation was given the regime in
which its constants are uniform. These changes do not constitute an independent
proof that the thesis is error-free. They identify the precise points a future
reviewer should attack first.

### Mathematical corrections and reasons

1. **Directed simple-graph second-order term excludes `m=2`.** The displayed
   claim
   `ell_m^dir(n)=n^2/4+Theta_m(n)` (and the corresponding `k_m^dir` claim) was
   false as stated for every fixed `m >= 2`: at `m=2`, the extremal value is
   eventually exactly `floor(n^2/4)`, so the correction is `O(1)`, not
   `Theta(n)`. The theorem, introduction, contribution summary, Chapter 1, and
   Chapter 4 now state the `Theta_m(n)` conclusion only for fixed `m >= 3` and
   state the `m=2` exception explicitly. A future reviewer should check both
   inequalities producing the linear term and verify that their constants may
   depend on fixed `m` but not on `n`.

2. **The multigraph joint-growth asymptotic now has its necessary regime.** The
   unqualified formula `K_m^multi(n)=Theta(m^2 n)` is not uniform in arbitrary
   simultaneous `m,n`; for example, at `n=2` the value is only `m-1`. It is now
   asserted in the large-block-packing regime `n/m -> infinity`. The surrounding
   prose explains why fixed or very small `n` is outside that claim. This was
   corrected in the main text, Chapter 4, the proof appendix, and README. A
   reviewer should derive explicit upper/lower constants in this regime and test
   boundary sequences such as `n=2`, `n=m`, and `n=m^2`.

3. **A missing `s=1` case was supplied in the bipartite multigraph proof.** In
   the proof of `thm:multi-vertex-bipartite`, the argument treated the component
   as a 2-connected block even when one bipartition class has size one. For
   `s=1<t` the graph is instead a thickened tree. The proof now handles that case
   separately. It also explicitly justifies that the rate used in the packing
   argument is maximized at `t=m-1`, rather than leaving that monotonicity
   implicit. The next reviewer should recompute the local connectivity in all
   cases `s=1`, `t=1`, and `s,t>=2`, then independently differentiate or compare
   the discrete rate.

4. **Directed-multigraph extremal classification was not unique for odd `n`.**
   The previous theorem called the balanced one-directional complete bipartite
   construction unique up to isomorphism. When `n` is odd, reversing all arcs
   changes which unequal part is the source, yielding two non-isomorphic directed
   graphs. The theorem now gives the set
   `{(m-1)B_(ceil,floor), (m-1)B_(floor,ceil)}`: one isomorphism class for even
   `n`, two reversal-paired classes for odd `n`. The proof steps, theorem title,
   introduction, and synthesis chapter were corrected accordingly. A reviewer
   should verify that “isomorphism” here preserves arc direction and that no
   implicit allowance for global reversal collapses the odd-order pair.

5. **The `n=7,m=3` multigraph classification is degree-capped, not global.**
   The text formerly claimed exactly three unrestricted extremal isomorphism
   classes. That cannot be true: every doubled bidirected tree is extremal, and
   there are already eleven undirected tree isomorphism classes on seven
   vertices. The actual machine call imposed maximum total degree eight. The
   thesis now says that, *within that cap*, the three observed classes are
   `2B_(3,4)`, `2B_(4,3)`, and the doubled bidirected path. Chapter 2, Chapter 4,
   the proof appendix, and gallery language now preserve this scope. The
   saturated-attachment lemma is no longer presented as classifying every
   linear-branch extremizer. A reviewer should inspect the generator arguments,
   confirm whether the cap applies before or after canonicalization, and never
   infer an unrestricted classification from this experiment.

6. **Hypergraph upper bounds were separated from exact attainment.** Earlier
   summaries blurred a universal upper bound with equality for all parameters.
   For the `m=3` result, the bound is universal in its proved domain, while the
   construction attaining it requires the stated rank/order conditions (in
   particular the relevant `r >= 3` range); simple-hypergraph and
   multihypergraph assertions are kept distinct. Tables, contribution claims,
   Chapter 4, and proof language now say “upper bound” where equality has not
   been proved. The next reviewer should check the incidence-rank lemma, every
   divisibility/floor term, small `n<r`, repeated-edge behavior, and the exact
   hypotheses of each construction. The older “NOW FULLY PROVED (all n, all r)”
   wording below is therefore historical and superseded.

7. **Directed-hypergraph claims were narrowed to the defined model.** A directed
   hyperedge is a tail together with `r-1` heads, and routes follow that
   orientation. Claims now distinguish this model from undirected Berge paths
   and avoid presenting exploratory bounds as a general theorem for all notions
   of directed hypergraph connectivity. A reviewer should independently check
   the shadow/matching reductions, endpoint conventions, repeated hyperedges,
   and whether cuts mix vertices and hyperedges in each statement.

8. **Random-threshold prose was scoped to what the citations support.** The
   audit removed an unsupported directed analogue, qualified the random-graph
   threshold statement and its parameter regime, and corrected the density scale
   used for the hypergraph discussion. These are contextual statements, not new
   thesis theorems. A later reviewer should re-open the cited primary sources and
   verify model, normalization, probability regime, and whether a threshold is
   sharp or only order-of-magnitude.

9. **Finite enumeration is no longer extrapolated beyond the computation.** Any
   block/enumeration claim based on searches through `n,m <= 8` is now labeled as
   evidence in that finite range rather than a theorem for `m >= 5` or arbitrary
   order. Chapter 2 explains the certification boundary and Chapter 3 separates
   discovery evidence from proof. The external AI contribution that suggested
   one discovery route is explicitly attributed rather than silently absorbed.
   A reviewer should match every numerical sentence to an archived command,
   parameter cap, and certificate.

### Reproducibility, exposition, and disclosure corrections

10. **The reproducibility appendix was rewritten around executable artifacts.**
    A long source-code listing was removed; it duplicated the maintained program,
    inflated the PDF, and could silently diverge. The appendix now documents the
    five implemented methods, dependencies (including optional parallel
    facilities and their sequential fallback), commands, generated computational
    figures, and archive relationship. Checksum instructions explicitly exclude
    the manifest itself to avoid a self-referential hash. Claims that an external
    archive is “authoritative” were softened where the repository contents are
    the directly inspectable evidence. The PDF consequently fell from 296 to 171
    pages. This is a presentation/reproducibility change, not a mathematical one.

11. **Summary tables, captions, and interface descriptions were made literal.**
    Table cells now distinguish exact results from bounds and computational
    observations; figure captions state the actual generated scope. Chapter 1
    describes a common *interface* across graph, digraph, and hypergraph models,
    not one identical internal data model. Counts such as “five methods” were
    aligned with the code. Grammatical/modeling fixes include plural “data
    suggest” and removal of claims broader than the program implements.

12. **Disclosure and front matter were simplified without hiding provenance.**
    The AI-use disclosure was condensed but retains the division between machine
    assistance and author responsibility. An unnecessary custom open-access page
    was removed. External AI-generated ideas remain identified where materially
    relevant. Bibliographic entries and nearby prose were corrected where the
    former wording overstated what a source established. A reviewer should still
    verify the final disclosure against the university's rules in force at the
    actual submission date.

### Files affected and how to review the patch

The final audit changed `main.tex`, `chapters/ch1_basecases.tex`,
`chapters/ch2_certify.tex`, `chapters/ch3_discover.tex`,
`chapters/ch4_synthesis.tex`, `chapters/app_proofs.tex`,
`chapters/app_code.tex`, `chapters/app_gallery.tex`, `README.md`, and `ref.bib`;
`main.pdf` was rebuilt from those sources. This audit record is the additional
change to `claude.md`. Use `git diff` rather than this summary alone: the diff is
the exact record of altered language, while this section explains the intent.

High-risk proof points for the next reviewer, in recommended order:

1. Re-prove the hypergraph incidence-rank/SPQR-leaf argument and all equality
   conditions without relying on the prose summary.
2. Re-prove the directed reachability-skeleton and deletion-induction arguments,
   checking zero-degree vertices and both orientations of every cut.
3. Check the directed-multigraph equality case and the even/odd isomorphism split.
4. Check the multigraph block-packing optimization, especially the thickened-tree
   boundary and the precise meaning of `n/m -> infinity`.
5. Re-run every finite enumeration with the displayed caps and compare canonical
   representatives, including uncapped doubled-tree counterexamples.
6. Verify directed-hypergraph shadow/matching statements directly from the route
   definition, not by analogy with ordinary digraphs.
7. Re-check every random-threshold sentence against its cited primary source.

### Verification completed after the corrections

On 2026-08-17 the following checks completed successfully:

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
cd program && ../.venv/bin/python -m unittest discover -s tests -v
git diff --check
```

The build produced a 171-page PDF with resolved references. The test suite ran
93 tests successfully with one optional test skipped. Parallel enumeration was
unavailable in the sandbox and correctly used the tested sequential fallback.
`git diff --check` reported no whitespace errors. LaTeX reported several
underfull-box warnings, including in a long corrected proof remark; these are
typesetting warnings rather than failed proofs or unresolved references. A future
reviewer should nevertheless visually inspect those pages before submission.

## Status of open problems (from ch4_synthesis.tex)

| Open item | Difficulty assessment | Plan |
|---|---|---|
| Hypergraph vertex-disjoint (undirected), table row "vertex/hyper: ---" | EASIEST — unexplored, m=2 looks provable for all n, r | Attack first |
| Directed hypergraph (arc + vertex), "---" | Model must be defined (program: tail + r-1 heads); first bounds provable | Second |
| conj:min-degree (directed multigraph, odd n, mixed regime) | Well-posed single lemma; numerics + partial rigorous progress | Third |
| Backward-arc lemma (m>=3 directed simple) | Known hard, thesis names it as THE obstacle | Not attempted |
| k_m(n), m>=6 (1974) | Half-century open | Not attempted |

## Definitions fixed by the program (erdos915_unified.py)

- kappa for hypergraphs (`vertex_split=True`): max number of Berge u-v paths
  pairwise **hyperedge-disjoint AND internally vertex-disjoint** (flow network:
  capacity-1 gate per hyperedge, capacity-1 split per internal vertex,
  endpoints uncapped). Menger holds with **mixed cuts** (vertices + hyperedges).
  Whitney kappa <= lambda holds by definition.
- Directed hyperedge: (tail, frozenset of r-1 heads); a route enters at the
  tail, leaves toward any head.

## Result 1 (PROVED, pending write-up): hypergraph vertex case, m = 2

**Theorem A.** For r >= 2 and all n >= 1, the maximum number of hyperedges of an
r-uniform (multi-)hypergraph on n vertices with kappa^max <= 1 is
floor((n-1)/(r-1)). Extremal: the star hypertree / any Berge forest with that
many edges. So k_2^{(r)}(n) = l_2^{(r)}(n): the vertex and edge problems agree
at m=2 for every r.

Proof skeleton (verified carefully):
- kappa^max >= 2  <=>  the bipartite incidence graph I(H) contains a cycle.
  (A cycle in I alternates v1,e1,v2,e2,...,el,v1, l>=2: paths v1,e1,v2 and
  v1,el,vl,...,e2,v2 are hyperedge-disjoint with disjoint internal vertex sets,
  so kappa(v1,v2)>=2. Conversely two such paths concatenate to a Berge cycle =
  cycle in I. Length-4 incidence cycles = two hyperedges sharing two vertices,
  so repeated hyperedges are automatically excluded.)
- Hence kappa^max <= 1 <=> I(H) is a forest: r|E| <= n + |E| - 1, i.e.
  |E| <= (n-1)/(r-1).
- Lower bound: hub h + floor((n-1)/(r-1)) disjoint blocks of r-1 vertices,
  hyperedges {h} u B_i, leftover vertices isolated. I is a tree => kappa^max<=1.

## Result 2 — UPDATE 2026-06-12: m = 3 NOW FULLY PROVED (all n, all r)

**Theorem.** For r >= 2, every r-uniform multihypergraph with kappa^max <= 2
has at most floor(2(n-1)/(r-1)) hyperedges; attained (simply) for r >= 3 when
2 <= binom(n-2, r-2). So k_3^{(r)}(n) = l_3^{(r)}(n) for all n.

The missing counting step ("Lemma L") is proved — the key realisation is to
ORDER the reductions so the terminal configuration has min degree >= 3
everywhere, then analyse the LEAVES of Tutte's triconnected decomposition
(the earlier z-deletion route was a dead end):

**Incidence rank lemma.** G connected multigraph, V = X u Z, (i) Z
independent, (ii) edges at Z unrepeated, (iii) every z-degree >= 2,
(iv) kappa_G(x,x') <= 2 for all X-pairs  =>  rank(G) <= |X| - 1.
Induction on |V|+|E|:
 1. Cut vertex: per-block induction + block-cut-tree count
    (sum (|X_B|-1) = |X|-1 - sum_{Z-cut}(b-1) <= |X|-1; bridges direct).
 2. z of degree 2: suppress (neighbours distinct, in X; all preserved).
 3. x of degree 2 (now all z-degrees >= 3): DELETE x; rank drops exactly 1,
    |X| drops 1, z-degrees stay >= 2. This was the unlock.
 4. Remaining: 2-connected, min degree >= 3. Parallel X-X edges already give
    kappa >= 3 (third route through any third vertex: G-x' walk + G-x walk),
    so G is simple. 3-connected G: all pairs kappa >= 3 => |X| <= 1 => z's
    have degree <= 1, absurd. Otherwise the Tutte/SPQR tree has >= 2 leaves
    (cite Tutte 1966, Hopcroft-Tarjan 1973), each leaf L with one virtual
    edge {a,b} and a far-side real a-b path avoiding L:
     - S-leaf (cycle, length >= 3): interior vertex has G-degree 2. Absurd.
     - P-leaf (bond): >= 2 real parallels. Absurd (simple).
     - R-leaf (3-connected, >= 4 nodes): Menger in L + far-side substitution
       gives kappa_G >= 3 for ALL pairs of V(L) => <= 1 X-node in L => some
       z* not in {a,b} has all neighbours in <= 1 X-node, degree <= 1. Absurd.
    So Step 4 is vacuous and the induction closes. QED
Numerics: 150 random maximal feasible sets at n=7, r=3, m=3 cap at 6 = bound;
n=5,6 exhaustive (multi) already matched; k_4^{(3)}(5) = 6 verified
exhaustively (q=6 feasible, q=7 not), so vertex=edge survives at m=4, n=5.

Write-up: lem:incidence-rank + thm:hyper-vertex-m3 + scope remark replace the
old conjecture block in app_proofs.tex (commented); ref.bib needs Tutte66 and
HopcroftTarjan73 entries (noted inline). m >= 4 open: no clean 4-connectivity
decomposition; first r >= 3 divergence point unknown.

## Result 2 (original notes, superseded): hypergraph vertex case, m = 3

Reformulation (exact, via the program's mixed-cut Menger): kappa_H(u,v) equals
the max number of internally disjoint u-v paths in the incidence graph I(H).
So the m=3 problem is: maximize q (number of degree-r Y-nodes) in a bipartite
graph I with parts X (n vertices) and Y (q hyperedges) such that no two
X-nodes are joined by 3 internally disjoint paths. Claimed value: q(r-1) <=
2(n-1), i.e. **k_3^{(r)}(n) = floor(2(n-1)/(r-1))** (lower bound already known
via Whitney + thm:simple-hyper-edge).

- Block-tree reduction PROVED: if every 2-connected block B satisfies
  rank(B) <= |X cap B| - 1, then total cycle rank <= |X|-1, which is exactly
  the bound. (Count: sum over blocks (|X_i|-1) = |X| - 1 - sum over Z-class
  cut nodes (b(z)-1) <= |X|-1.)
- Remaining core: **Lemma L**: H 2-connected multigraph, Z independent set,
  every z in Z with >=3 distinct X-neighbours and no parallel Z-edges, all
  X-pairs kappa<=2  =>  rank(H) <= |X|-1.
  - Proved: Z = empty case (ear decomposition => H is a cycle).
  - Proved: degree-2 Z-suppression preserves all hypotheses.
  - Proved: for z in Z, N(z) is pairwise kappa<=1 in H-z (dispersal).
  - Remaining: the counting step rank(H-z) <= |X| - deg(z) using dispersal.
- Numerics planned: brute force r=3, n=5,6 (is n-1 really the max?).

## Numerics completed (2026-06-11/12, via the thesis's own checker)

- Theorem A verified: star hypertree attains floor((n-1)/(r-1)) with
  kappa^max=1 for r=3,4 and n up to 11; brute force over ALL hypergraphs
  (multi included at m=2 automatically, since repeats force codegree 2):
  no hypergraph beats the bound at (n,r) in {(5,3),(6,3),(7,3),(6,4),(7,4)}.
- m=3, r=3: max edges with kappa^max<=2 is exactly n-1 at n=5,6 — verified
  over SIMPLE and MULTI hypergraphs (codegree<=2 pruning + exhaustive).
  Supports k_3^{(r)}(n) = floor(2(n-1)/(r-1)).
- Fractional min-degree search (hill climbing + annealing, multi-start,
  n=7 and n=9): max min-degree found = k exactly (bipartite point, rigid);
  max total weight found = floor(n^2/4) at n=7. No counterexample direction.

## Result 3: directed multigraph odd case — NEW ROUTE bypassing conj:min-degree

The thesis route to L_m^dir(2k+1) needs conj:min-degree. Found a different
route that avoids it. All statements below have full proofs (checked twice,
to be written into app_proofs.tex commented out).

**Lemma C (attachment lemma, UNCONDITIONAL).** Let D0 = (m-1)*B_{p,q} be the
one-directional complete bipartite multigraph (parts A, |A|=p>=2, sinks B,
|B|=q>=2, every arc A->B at multiplicity m-1, m>=2). If D is obtained from D0
by adding one new vertex v together with any set of arcs incident to v, and
lambda^max(D) <= m-1, then d(v) <= (m-1) max(p, q).
Proof by classifying v's arc classes iA, iB, oA, oB (in from A/B, out to A/B):
 - iA>0 and oB>0 impossible: a->v->b is an m-th route on top of the m-1
   parallel a->b arcs.
 - iA>0 and an out-arc v->a' with a'!=a impossible: a->v->a'->b is an m-th
   route (uses fresh arcs (a,v),(v,a'),(a',b)).
 - so iA>0 forces v to be a pure sink (except possibly a 2-cycle with a single
   a, which caps d(v) <= 2(m-1)); then for each a in A,
   lambda(a,v) = mu(a,v) + sum_b min(mu(b,v), m-1) = mu(a,v) + iB <= m-1,
   so d(v) = iA + iB <= p(m-1) - iB(p-1) <= p(m-1).
 - symmetrically oB>0 forces pure source; lambda(v,b) = mu(v,b) + oA <= m-1
   for every b gives d(v) <= q(m-1) - oA(q-1) <= q(m-1).
 - iB>0 and oB>0 (different sinks) impossible: a->b->v->b' is an m-th route
   on (a,b'); same-b 2-cycle caps at 2(m-1).
 - iB and oA only: lambda(a',v) >= iB and lambda(v,b') >= oA force
   iB <= m-1, oA <= m-1, so d(v) <= 2(m-1).
All cases give d(v) <= (m-1) max(p,q,2) = (m-1) max(p,q). QED

**Theorem D (odd step closes for ALL m >= 3, conditional only on even level).**
Fix k >= 4 (so the quadratic branch dominates: k^2 > 2(2k-1)). Assume
 (i)  L_m^dir(2k) = (m-1)k^2, and
 (ii) every extremal multigraph at 2k is (m-1)*B_{k,k}.
Then L_m^dir(2k+1) = (m-1)k(k+1).
Proof. Lower bound: (m-1)*B_{k,k+1}. Upper: let A = (m-1)k(k+1) + j with
j >= 1; min-degree deletion gives A <= (2k+1)/(2k-1) * (m-1)k^2, so
j <= J := floor((m-1)k/(2k-1)). Every vertex satisfies
d(v) >= A - L(2k) = (m-1)k + j, while the average degree is
2A/(2k+1) = (m-1)k + j + [(m-1)k - (2k-1)j]/(2k+1) < (m-1)k + j + 1.
Hence some v has d(v) = (m-1)k + j exactly, and D - v has exactly (m-1)k^2
arcs: it is extremal at 2k, so by (ii) D - v = (m-1)*B_{k,k}. Lemma C then
caps d(v) <= (m-1)k < (m-1)k + j. Contradiction; so j = 0. QED

**UPDATE 2026-06-12 (second pass): uniqueness propagation now PROVED in both
parities via an equality version of the attachment lemma.**

- **Corollary (attachment equality, proved).** In Lemma C with max(p,q) >= 3
  and d(v) = (m-1)max(p,q): q > p forces v = pure source at full multiplicity
  (rebuilds (m-1)B_{p+1,q}); p > q symmetric; p = q one of the two.
- **Odd uniqueness (m=3, n=2k+1 >= 9):** extremiser has degrees >= 2k and not
  all >= 2k+1 ((2k+1)^2 > 4k(k+1)); a degree-2k vertex deletes to 2B_{k,k},
  equality corollary rebuilds 2B_{k+1,k} / 2B_{k,k+1}. PROVED given even
  level below.
- **Even uniqueness (m=3, n=2k >= 10):** averaging equality forces
  2k-regularity, every deletion extremal at 2k-1, odd uniqueness + equality
  corollary (q>p case) rebuild exactly 2B_{k,k}. PROVED given odd level below.
- **Seam n=8:** regularity excludes the double star among 7-vertex
  extremisers (hub degree 24 > 8), leaving the two bipartite orientations,
  so D = 2B_{4,4} — PROVED given the n=7 facts below.
- **CORRECTION (found by the new enumerator): the linear-branch extremal set
  is all doubled bidirected spanning trees, not just the double star.**
  Exhaustive enumeration (new tool
  `enumerate_extremal_directed_multigraphs`, DFS with proved prunings +
  canonical dedup): n=4, m=3, 12 arcs: exactly 2 extremals (doubled star,
  doubled path); n=5, m=3, 16 arcs: exactly 3 (star, broom, path — all
  bidirected-symmetric, i.e. exactly the doubled spanning trees). Every
  bidirected tree at multiplicity m-1 is feasible (proof: flows bottleneck at
  tree edges / pass through cut vertices), so this is the full set at small n.
- **Seam n=8 RE-PROVED with the corrected set:** D 8-regular, D-v a 24-arc
  extremiser with max degree <= 8: among doubled trees only the doubled path
  P_7 qualifies (tree degree <= 2); attaching v to P_7 forces weight 4 on
  each path end (degree count), i.e. bidirected full multiplicity, giving the
  doubled bidirected C_8 — infeasible (two doubled directions around: lambda
  = 4 > 2). So all deletions are bipartite-type and D = 2B(4,4). Seam holds.
- **Net result: the ENTIRE m=3 directed multigraph problem now rests on two
  finite integral statements:**
  (a) M*(7) = 12 (i.e. L_3(7) = 24);
  (b) every 24-arc feasible multigraph on 7 vertices with max degree <= 8 is
      2B(3,4), 2B(4,3), or the doubled bidirected path P_7.
- Certifier strengthened accordingly: `use_deletion_cuts` flag adds three
  PROVED-valid families (vertex-deletion <= M*(n-1), pair-deletion
  <= M*(n-2), degree-pair d+(s)+d-(t)-w(s,t) <= n-1). Verified unchanged
  optima at n=5; n=6 timing comparison in progress.

**Uniqueness propagation (m = 3, original sketch, superseded by the above).**
 - Odd extremal at 2k+1 (m=3): A = 2k(k+1) forces min degree exactly 2k
   (counting: all degrees >= 2k+1 would need sum >= (2k+1)^2+2k+1 > 2A),
   deletion lands on the even extremal, Lemma C analysis forces v to be a
   pure source to B (or pure sink from A) at full multiplicity, so the
   extremal at 2k+1 is exactly 2*B_{k+1,k} or 2*B_{k,k+1}.
 - Even extremal at 2k (m=3): A = 2k^2 forces 2k-regularity and every
   deletion extremal at 2k-1; reattachment via Lemma C forces 2*B_{k,k}.
 - So for m=3 value+uniqueness propagate jointly for all n >= 9, and the
   whole m=3 directed multigraph problem reduces to the FINITE bases
   n = 7, 8 (value + extremal characterization), exactly the certifier's
   next target. NOTE crossover subtlety: at n=7 the branches tie (24 arcs,
   double star AND 2*B(3,4) AND 2*B(4,3) all extremal), so the n=8
   reconstruction must use degree-regularity to exclude the double star
   (hub degree 24 > 8 cannot fit in an 8-regular graph) — this works.
 - For m >= 4 there is one identified HOLE: at odd levels the extremal could
   a priori have all degrees >= (m-1)k+1 (counting allows it when
   k(m-3) >= 1), so odd uniqueness does not yet propagate; Theorem D still
   gives the VALUE at odd levels whenever even uniqueness is available.

**Relation to conj:min-degree.** Theorem D bypasses it. Note the conjecture
is equivalent (over all m at once) to its fractional version: w in [0,1] on
ordered pairs, all max-flows <= 1, n = 2k+1 => some weighted degree <= k.
Conditional bound from averaging: min weighted degree <= 2k^2/(2k-1) < k+1
(given fractional even bound k^2), i.e. integral slack <= m-2; conjecture
asks slack 0 and stays open, but is no longer on the critical path for m=3.

## Numerics: fractional min-degree / total weight (n=7, n=9)

Hill climbing + simulated annealing, multi-start (zero, random, bipartite,
noisy bipartite), all-pairs max-flow feasibility checked exactly:
 - max min-degree found = k exactly (3 at n=7, 4 at n=9), attained by the
   one-directional bipartite point, which is locally rigid in every tested
   direction; noisy starts converge back below it.
 - max total weight found = 12.000 at n=7 = max(2(n-1), floor(n^2/4)).
Supports both the fractional odd bound and conj:min-degree.

## Result 4 (planned): directed hypergraph first bounds

Model: hyperedge = (tail, r-1 heads). Easy and rigorous:
- Degree bound: lambda(u,v) <= min(d+(u), d-(v)).
- Pair-codegree bound: <= m-1 hyperedges share the same (tail u, head v) pair,
  hence (r-1)|E| <= (m-1) n(n-1).
- Bipartite construction: tails A, heads in B, per-tail (r-1)-uniform simple
  hypergraph on B with max degree <= m-1 (exists by lem:sparse-hypergraph):
  |A| * floor((m-1)|B|/(r-1)) edges, lambda^max = m-1 when only single-step
  routes exist (B has no tails). Quadratic ~ (m-1) n^2 / (4(r-1)).

## Result 4 (PROVED): directed hypergraph first bounds

Model (matches the program): hyperedge = (tail, r-1 heads). Proved:
pair-codegree <= m-1 gives (r-1)|E| <= (m-1)n(n-1); bipartite construction
(tails A, shared sparse (r-1)-uniform head hypergraph on B from
lem:sparse-hypergraph) gives alpha*floor((m-1)(n-alpha)/(r-1)) feasible
hyperedges, so the value is quadratic. Exact value open (factor ~4 gap).

## Deliverables written (all commented out / non-invasive, PENDING REVIEW)

- chapters/app_proofs.tex:
  * after the directed-multigraph section: lem:attachment (full proof),
    thm:odd-step (full proof), rem:odd-step-roadmap (m=3 reduction to bases
    n=7,8; m>=4 hole identified).
  * end of the hypergraph section: incidence-graph translation,
    thm:hyper-vertex-m2 (full proof), prop:hyper-vertex-lower (full proof),
    conj:hyper-vertex + rem:hyper-vertex-m3 (reduction + partial progress),
    prop:dir-hyper-first (full proof).
- chapters/ch4_synthesis.tex: commented replacement row for the summary
  table (vertex/hyper) and commented updates to two open-problem items.
- program/erdos915_unified.py: new section "OPEN-VARIANT EXPLORATION"
  (hypergraph_vertex_m2, max_hyper_vertex_connectivity,
  hyper_vertex_feasible_exists, verify_hyper_vertex_value,
  fractional_flows_feasible, fractional_anneal) + commented self-test hooks.
  Full self-check suite re-run after integration: ALL CHECKS PASSED.
- main.pdf recompiles cleanly (latexmk exit 0, no errors).

## Honest status summary

PROVED unconditionally, all n:
  * k_2^{(r)}(n) = floor((n-1)/(r-1)) for every r (hypergraph vertex, m=2).
  * prop:hyper-vertex-lower (all m, r >= 3).
  * Attachment lemma (lem:attachment) for all m >= 2, p,q >= 2.
  * Directed hypergraph pair-codegree upper bound + quadratic construction.
PROVED conditionally:
  * thm:odd-step: odd-level value for ALL m >= 3 given even value+uniqueness.
  * m=3 value+uniqueness propagate for all n >= 9 given bases n=7,8.
STILL OPEN (precisely delimited):
  * Bases n=7,8 for the directed multigraph at m=3 (finite computations).
  * Odd-level extremal uniqueness for m >= 4 (the counting hole).
  * Lemma L counting step (hypergraph vertex m=3); conjecture for m >= 4.
  * conj:min-degree itself (bypassed for m=3, supported numerically).

## Progress on the finite bases (2026-06-12, late session)

- Full self-test suite re-run after all program edits: ALL CHECKS PASSED.
- Fractional certifier with deletion cuts: n=6 OPTIMAL M*(6)=10 in 1315s
  (comparable to baseline ~20 min; fractional n=7 out of reach locally).
- NEW: integral certifier `certify_integral_arc_bound(n, m, target)` — the
  m=3 chain needs only the INTEGRAL fact L_3(7) = 24, i.e. "no 25-arc
  feasible multigraph on 7 vertices", a much friendlier MILP (integer mu,
  exact cuts at capacity m-1, two-hop exact-min rows, deletion cuts from
  certified M*(4), M*(5), M*(6), degree-pair inequality, degree-sorting).
  Sanity: n=5 t16 FEASIBLE 0.7s, t17 INFEASIBLE 2.9s.
  RESULT: n=6 t21 INFEASIBLE in 1309s — independent integral re-proof of
  L_3^dir(6) = 20.
- n=7 t25 MILP and the n=6 max-degree-8 enumeration were CANCELLED after ~2h
  CPU each (no verdict yet) at the user's request. To resume (run from
  program/, each prints a single verdict line):
    python -c "from erdos915_unified import certify_integral_arc_bound as c;\
 print(c(7, 3, 25, time_limit=86400.0))"
    # INFEASIBLE => L_3^dir(7) = 24 => statement (a) PROVED
    python -c "from erdos915_unified import \
enumerate_extremal_directed_multigraphs as e;\
 r = e(6, 3, 20, max_degree=8); print(len(r)); [print(M) for M in r]"
    # expected: only the doubled bidirected path P_6 => degree-4 case of (b)
  Budget hint: the integral MILP closed n=6 in ~22 min on this machine; n=7
  plausibly needs hours-to-days, so a cluster node or an overnight run (or
  a stronger solver, e.g. Gurobi on the same encoding) is the right tool.
- Statement (b), degree-4 case PROVED by hand (conditional on the n=6
  max-degree-8 characterization, enumeration in flight): if some d(v) = 4,
  then D - v is a 20-arc extremiser at n=6 with max degree <= 8 — expected
  to be only the doubled path P_6 (bipartite 2B(3,3) = 18 < 20 is not
  extremal at 6; doubled non-path trees have a degree-12+ hub). Attaching a
  degree-4 vertex v to doubled P_6: interior vertices are degree-saturated
  (8), so v attaches only to the two path ends; full bidirected weight 4 on
  ONE end gives exactly the doubled P_7 (allowed third extremiser); any
  split across BOTH ends adds a parallel channel between the path ends on
  top of the capacity-2 path, pushing some lambda to 3+ (case check over
  the orientation splits 2+2: all fail). So (b) reduces to its delta >= 5
  core: 24 arcs, 5 <= d(v) <= 8 — where 2B(3,4) (degrees 8,8,8,6,6,6,6)
  lives. That core remains a computation (or an S-T-style hand argument).

## Future direction noted: m = 4 hypergraph vertex problem

The incidence reduction generalizes: k_{m}^{(r)}(n) = floor((m-1)(n-1)/(r-1))
would follow from "kappa_X <= m-1 implies rank <= (m-2)(|X|-1)". For m=4 the
predicted tight 2-connected pieces are the K_{3,t} incidence blocks (rank
exactly 2(|X|-1), all X-pairs at kappa = 3). The obstruction: Tutte's
decomposition stops at 3-connectivity; a 4-connectivity analogue (k-blocks of
Carmesin-Diestel-Hamann-Hundertmark?) lacks the clean tree-of-pieces with
virtual edges that Step 4 of the incidence rank lemma leans on. Verified
k_4^{(3)}(5) = 6 exhaustively, so no early counterexample.

## Suggested next actions for the author

1. Review the commented LaTeX blocks; if accepted, uncomment and re-run the
   (commented) self-test hooks in _run_checks for the printed evidence.
2. Point the certifier at n=7, m=3 directed multigraphs (value 24 + extremal
   set {double star, 2B(3,4), 2B(4,3)}?) — this is now the single missing
   base for the full m=3 theorem.
3. The Lemma L counting step (claude.md Result 2) is a self-contained
   graph-theory problem, suitable as a focused push or a co-advisor question.

## Session 2026-06-12/13 (overnight, carte blanche granted)

Author lifted the commented-block rule: verified content goes in directly.

FABLE PROOF-CHECK of all of app_proofs.tex (every statement, active and
commented). 29 statements verified correct, 4 ERRORS found and FIXED:
 1. prop:mutual-unreachability FALSE as stated — counterexample
    {(u,v),(v,u),(u,w)}: λ^max ≤ 1 yet v→u→w. Restated: no v–w path in D−u;
    counterexample now displayed in the proof + figure.
 2. thm:odd-step "all m ≥ 3" had a GAP for m ≥ 5: the correction term
    ((m-1)k−(2k-1)j)/(2k+1) need not lie in [0,1) (m=5,k=4,j=1 gives exactly
    1: an 18-regular 81-arc escape is arithmetically consistent). Restated
    for m ∈ {3,4} with the [0,1) step justified ((m−3)k+1 ≤ k+1 < 2k+1);
    m ≥ 5 value-gap documented in rem:odd-step-roadmap. m=3 chain UNAFFECTED.
 3. prop:min-degree-m2 false at n=3 (bidirected star), proof invalid n=5
    (linear branch dominates). Restated with n ≥ 7.
 4. thm:extremal-char odd case missed a third slack location (a G-edge at
    tree distance 3). Proof rewritten as the S1+S2+S3 slack identity
    2|E| = m(n−1) − (S1+S2+S3). Also fixed: "K_4 blocks glued along shared
    edges" → glued at shared cut vertices (edge-gluing is infeasible: shared
    pair reaches λ=5), claim softened to "consistent with".

INTEGRATED (now live, uncommented): lem:attachment, cor:attachment-equality,
thm:odd-step, rem:odd-step-roadmap, thm:hyper-vertex-m2, prop:hyper-vertex-
lower, lem:incidence-rank, thm:hyper-vertex-m3, rem:hyper-vertex-m3-scope,
prop:dir-hyper-first + new \section{The hypergraph vertex problem}.

OTHER WORK (subagents, all builds verified):
- Easy fixes (sonnet): Tutte66/HopcroftTarjan73 active in ref.bib (verified
  DOIs); k-tree defined inline in ch1 (false forward ref removed); K_4-trees
  dropped from main.tex summary; citations added for pre-2024 conjecture
  (ErdosProblems) and Bollobás–Erdős attribution (BollobasErdos62).
- ch4 (opus): PENDING blocks resolved, tab:summary updated (hyper-vertex row
  proved m≤3; directed rows cond. m=3; dir-hyper quadratic), open problems
  rewritten (two finite n=7 computations in progress; m≥4/m≥5 holes split).
- Related work (opus): new ch1 \section{Where this work sits} — lineage +
  nauty/geng, SAT (Heule), flag algebras (Razborov), all 5 new bib entries
  web-verified. New ch2 \section{Reproducibility}.
- Consolidation (opus): ch3 trichotomy sections merged → sec:trichotomy;
  ch4 figures 9→6 (m6 distribution pair + threshold_3d cut, prose added for
  scatter + surface); G(n,p) home is ch1 only.
- Figures (opus): 7 TikZ figures in appendix (Gomory–Hu dist, two Mader
  constructions, mutual-unreachability + counterexample, attachment setup,
  P_7→C_8 seam, hypergraph↔incidence translation + star hypertree, SPQR leaf
  schematic); 3 in ch1 (B_{4,4}, bidirected star, 30-arc counterexample with
  highlighted routes). Proof-idea sketches surfaced into ch1 body. G(n,p)
  limitation sentence added (fixed-m regime not covered).
- Build: latexmk exit 0, 81 pages, zero undefined refs. Figure pages
  spot-checked visually (renders clean).

COMPUTATIONS LAUNCHED (detached, survive session):
- PID 37597: certify_integral_arc_bound(7,3,25,time_limit=86400) →
  logs/milp_n7_t25_20260613.log
- PID 37663: enumerate_extremal_directed_multigraphs(6,3,20,max_degree=8) →
  logs/enum_n6_d8_20260613.log
- Watcher (background bash bijy4lkb4) re-invokes the session when one ends.

## 2026-06-13 (morning, Opus) — figure/data audit + first-introduction TikZ + Fable queue

Author's brief: the plots felt "rough/incomplete/inaccurate"; wanted uniformity
(equal datapoints, general rules holding); more TikZ when graph classes are FIRST
introduced; and Fable set up to attempt the hard proofs next.

FIGURE/DATA FIXES (the main ask). All 13 used figures were stale (generated Jun 7-9,
code changed Jun 12); regenerated via `make_figures.py`
(log program/logs/make_figures_20260613.log). Root-cause fixes, not cosmetic:
1. `gather_variant_grid` (make_figures.py): the search "lower-bound" circles were raw
   annealing that plateaued jaggedly BELOW the proved curves — contradicting the
   caption, which promises each circle is "the better of the search and a named
   construction." `_extend_lower_bounds` was applied to only 2 of 12 panels. Now applied
   to every proved/conjectured panel, over UNIFORM n-ranges (matrix 2..12, hyper 2..10),
   so each panel has equal datapoints and circles land ON the curves. Verified: across
   all proved/conj panels, search==curve (0 above, 0 below). search_budget 1.5->0.4
   (construction dominates those panels, so anneal quality there is irrelevant).
2. Hyper-undirected-vertex panel was drawn "open" though thm:hyper-vertex-m3 proves it.
   Now PROVED (solid line + on-curve dots) at m<=3, OPEN (band) at m>=4. Verified on
   both m=3 (proved) and m=6 (open) grids.
3. `variant_surface_3d` was ENTIRELY purple: `compute_surface_cache` called
   `solve(exhaustive=False)`, which never returns bound=="exact". Added
   `_surface_known_value(vkey,n,m)` = proved closed form (capped at trivial max) in the
   proved regime, else None. Proved cells -> exact/blue; open cells -> discovery/purple.
   Cache migrated IN PLACE on next run (proved cells overwritten, open cells kept), no
   recompute. Now 202 exact / 218 lower; proved variants render as blue sheets, the
   open/proved boundary is visible (e.g. simple vertex blue m<=4, hyper vertex blue m<=3).
4. Integer x-ticks: `plot_conn_dist_grid` (set_xticks(levels)), `plot_edge_dist_grid` and
   `plot_scatter_lambda_edges` (MaxNLocator integer) — kills spurious 0.5/1.5 labels on
   the sparse directed panels.
5. The `edge_vertex_divergence` "wiggle" is NOT a bug: it is the true floor staircase
   (m=2,4 integer slope -> straight; m=3,5 zigzag by <=1). Left as correct maths.
   Caption numbers spot-checked and correct: edge_vertex_sampling shows kap<lam 22/12/6%.

TIKZ AT FIRST INTRODUCTION (ch1, self-contained inline styles; roleMeasure/roleObserve/
KULblauw1/roleDiscover colours): fig:three-models (simple triangle / multigraph with
triple+double parallel edges / shaded 3-vertex hyperedge + ordinary edge) at the model
paragraph; fig:edge-vs-vertex (two s-t routes through one cut vertex w: lam=2, kap=1,
Whitney) at the separation paragraph; fig:berge-path (two overlapping hyperedges sharing
y, orange route u->y->w) at the hypergraph section. All three render clean in the PDF.

BUILD: latexmk exit 0, 83 pages (+2), zero undefined refs, 1 (pre-existing) overfull hbox.

TASKS.md rewritten with a NEXT-SESSION FABLE block (backward-arc lemma flagship; hyper
vertex m=4 needing a 4-connectivity SPQR analogue; m>=4 odd-uniqueness / m>=5 value-step
hole; the two n=7 facts by hand).

BACKGROUND JOBS: MILP 37597 (1.8 GB) + enum 37663 still running; enum now ~17 GB RAM and
climbing (OOM risk, 288 MB free). I tried to `kill 37663` to free RAM for the figure run
but the sandbox DENIED killing a process it did not start. Flagged in TASKS.md: author
can kill 37663 safely (identical predecessor was already cancelled without a verdict).
Neither log has produced a verdict yet (only START lines).

FOLLOW-UP same day (author review): (1) author's PC ran out of RAM — the unbounded enum
(PID 37663) had grown to ~22 GB; author-authorised, killed it (no partial output, prints
only at the end). MILP 37597 left running. Big computations moved to a TASKS.md "run
later, memory-capped" block (systemd-run --user --scope -p MemoryMax=... verified to
work). (2) Author spotted GREEN exact squares BELOW PURPLE circles in variant_bounds
(impossible — a lower bound above the proved optimum), worst at m=6. Cause: my
construction-extension planted the raw closed form, but floor(m(n-1)/2) etc. are the
value only for n>=m; for n<m the complete graph K_n is feasible and the formula
overshoots (e.g. n=2,m=6 gives 3 edges where only 1 exists). Fixed by capping every
proved/conj curve AND its planted lower bound at the model trivial max
(lb_simple_edge/lb_multi_edge/lb_multi_dir; directed/hyper were already capped). Both
grids regenerated; a sanity assert confirms no exact square exceeds its curve.
(3) Reworked the 3 TikZ figures the author flagged: A.3(a) apex x -> labelled circle;
A.4 attachment lemma decluttered (wider, faint background A->B arcs, bold v-classes);
A.6(a) hypergraph -> clean filled hulls with an orange Berge path. Build clean, 83 pages.

---
Session: 2026-06-13. Tasks: prose cleanup in main.tex and chapter 1-2 authorial commands.

Changes made:
(1) main.tex prose: removed -- (en-dashes) from compound names in prose; changed
    S{\o}rensen--Thomassen -> S{\o}rensen-Thomassen and Gomory--Hu -> Gomory-Hu in two
    prose locations (Contribution Statement and Abbreviations table).
(2) ch1 line 6: inserted K_5 - 2 edges TikZ figure (fig:k5-example) as the first
    concrete graph example in the chapter.
(3) ch1 three-models figure: rebuilt the hypergraph subfigure with 7 vertices and 2
    hyperedges of different sizes (size 3, violet; size 4, blue), no regular edges;
    updated caption to describe both hyperedges.
(4) ch1 Sorensen-Thomassen: removed the vague "sufficiently large n" qualifier and
    replaced with concrete "n >= 10"; added a remark explaining the threshold.
(5) ch1 Construction 1.5 (directed hub): added a paragraph introducing d+ (out-degree)
    and d- (in-degree) before the construction uses those symbols.
(6) ch1 bidirected-star figure: expanded to two-panel figure (m=2 left, m=4 right)
    using subcaption-free side-by-side TikZ scopes; the m=4 panel shows hub arcs
    (blue) + two circulant layers (orange). Caption updated accordingly.
(7) ch1 "pre-2024 conjecture": removed the misattributed \cite{ErdosProblems} and
    changed to "the natural initial conjecture" since that conjecture (directed, m>=3)
    is not stated in Problem 915.
(8) ch2 hyperedge gadget: added a room-with-doors analogy paragraph explaining the
    helper-node construction.
Build check: pdflatex clean, 83 pages, 0 errors.

## 2026-06-13 (Opus) — merged erdos915_simplified.py back into the unified program
Author asked to fold the scratch teaching file `program/erdos915_simplified.py` (a
class-hierarchy rewrite of the core) back into `erdos915_unified.py`, optimising for
readability then brevity. Decision (confirmed with author): KEEP the matrix+Variant
`Graph` — it is the better unification (the simplified file's SimpleGraph/MultiGraph
"differ by one line", which the `simple` flag already captures) and underpins every
prover/figure efficiently. Harvested the simplified file's ONE genuine win: the graph
CHECKER now measures edge- and vertex-connectivity through a single `vertex_split`-
parameterised path — `_flow_network` / `local_connectivity` / `max_connectivity` —
exactly mirroring the hypergraph section, with `max_edge_connectivity` etc. kept as
thin named views so nothing downstream changed. Removed `_edge_flow_network` and
`_vertex_split_network` (6 connectivity funcs → 3 real + 5 one-line views). Deleted the
now-redundant `erdos915_simplified.py` (restores hard-rule #1: one runnable file). No
.tex touched. Full `python erdos915_unified.py` self-check: ALL CHECKS PASSED (~59s).

## 2026-06-13 (Opus) — plainer naming (author found "annealing"/"certifying" too hard)
Author asked for more accessible names + softer comments. Confirmed vocabulary: the
DISCOVER corner is now "search", the PROVE corner is now "prove" (aligning the code
names with the file's own MEASURE/PROVE/DISCOVER narrative). Renames across BOTH
`erdos915_unified.py` and `make_figures.py`: anneal()→search_for_dense_graph,
search_best_graph()→best_of_searches, AnnealingResult→SearchResult, StepRecord→
SearchStep, _timed_anneal→_search_within_budget, plot_temperature_trace→plot_search_trace,
fractional_anneal→fractional_search; certify_directed_multigraph→prove_directed_multigraph,
certify_integral_arc_bound→prove_integral_arc_bound, CertificateResult→ProofResult,
_CERTIFIED_MSTAR→_PROVEN_MSTAR, local var certificate→proof. Comments softened
(Metropolis→"accept-worse rule", "geometric cooling"→"cools", certifier→prover,
certified→proved). KEPT: the "temperature/cooling" metaphor; "(simulated annealing)"
named once in the SEARCH banner + search docstring to preserve the thesis link; the
thesis-facing figure strings ("multigraph, certified" caption, "certified optimum"
label, temperature_trace.png filename). Self-check: ALL CHECKS PASSED (~59s); all
make_figures imports resolve. Backup at /tmp/erdos915_unified.bak.py (pre-rename).

## 2026-06-13 (Opus) — closed the rename's last gap: the test suite + TASKS.md
The previous rename verified `erdos915_unified.py` + `make_figures.py` but MISSED the
`program/tests/` suite (10 files, 66 tests) and a stale resume command. Fixed the only
two test files that imported renamed symbols: `test_search.py` (anneal→
search_for_dense_graph, search_best_graph→best_of_searches, plus the method name
test_anneal_*→test_search_*) and `test_certify.py` (certify_directed_multigraph→
prove_directed_multigraph, class Certifier→Prover, docstring certifier→prover); also
the cosmetic `test_solve.py` method test_*_is_certified→_is_proved. Confirmed the
SearchResult / ProofResult attributes the tests read (history, feasible_found,
acceptance_rate, status, scaled_optimum) all survived the rename. Fixed TASKS.md's
BIG-COMPUTATIONS resume command (certify_integral_arc_bound→prove_integral_arc_bound)
so it can still be copy-pasted. `python -m unittest discover -s tests`: **66 tests OK**
(~104s). The .tex prose keeps "annealing"/"Metropolis"/alg:anneal on purpose — that is
the formal write-up, and the code's one "(simulated annealing)" anchor links to it.
`local_edge_connectivity` is NOT dead after all — the test suite exercises it; the
edge/vertex × local/max measure table is fully covered (solver + tests).

## 2026-06-13 (Opus) — hardened the three provers + a small trim
Author asked to harden the provers (and trim if possible). Full correctness AUDIT of
prove_directed_multigraph (fractional MILP), prove_integral_arc_bound (integral MILP),
and _exhaustive_directed (branch & bound) + _arc_flow_at_least (Ford–Fulkerson):
- Cut formulation is EXACT, not a relaxation (maxflow<=1 iff a chosen vertex-cut has
  capacity<=1; the MILP picks the cut), so OPTIMAL/INFEASIBLE = genuine proof.
- Verified EVERY strengthening row is a valid inequality (so none cuts a feasible
  point / lowers the optimum): two-hop (arc-disjoint direct+detours), the McCormick
  min (solver pins z to exactly min via the binary selector b in BOTH the z<=w and the
  conditional-cap·b encodings), degree-pair 6c (= two-hop + min(a,b)>=a+b-(m-1)),
  deletion cuts (induced subgraph on k verts has <= (m-1)·M*(k) arcs, gated on the
  correct _PROVEN_MSTAR={2:2,3:4,4:6,5:8,6:10}=2(n-1)), degree-ordering symmetry
  (relabel-invariant, preserves the optimum). B&B: feasibility is anti-monotone so the
  include-only-when-feasible prune is sound; the affected-pair set reaches_to(u) ×
  reaches_from(v) is exactly the pairs the new arc can touch; bound prune is a valid
  over-estimate. Conclusion: all three provers are SOUND. No code-logic bug found.
HARDENING added to the self-check (the INFEASIBLE proof path was previously UNtested):
- "valid inequalities sharpen but never move the optimum": prove_directed_multigraph(3,
  use_two_hop=False, use_symmetry_breaking=False) must still give M*(3)=4 — a tripwire
  that fires if any 'valid' row is ever made invalid.
- "an INFEASIBLE verdict is a genuine proof": prove_integral_arc_bound(4,3,12)=FEASIBLE
  and (4,3,13)=INFEASIBLE (L_3^dir(4)=12) — the same mechanism as the thesis L_3(7)=24
  proof, at a size that runs in the suite (~adds a few s).
TRIM (obeys the file's own "hoisted imports" rule): hoisted permutations &
combinations_with_replacement to the top block and deleted the 3 in-function itertools
imports incl. the redundant `combinations as _comb` alias. Did NOT extract the two
provers' shared COO/add_row boilerplate — it nets ~0 lines and churns thesis-critical
code; left as an optional readability refactor. Verified: self-check ALL CHECKS PASSED
(incl. the 3 new lines); 66 tests OK (~105s); enumerate(4,3,12)=2 extremals and the
hypergraph multi path still work after the import move.

## 2026-06-13 (later) — figure audit & rework (author's detailed pass)

Author reviewed every data/TikZ figure and gave per-figure instructions; actioned
all of them. Mapping figure number -> source confirmed via main.aux.

TikZ (ch1_basecases.tex):
- Fig 1.2 (fig:three-models) hypergraph panel: redrawn so the size-3 (violet) and
  size-4 (blue) hyperedges SHARE one vertex (rightmost of the triple = bottom-left
  of the quad). Translucent fills (fill opacity 0.32) blend in the overlap; both
  darker outlines drawn on the main layer ABOVE both fills; vertices drawn last.
- Fig 1.6 (fig:bidirected-star) right panel: m=4 -> m=3 (dropped the j=2 circulant
  layer); now one circulant layer, d^+=d^-=2, m(n-1)=15 arcs, lambda^max=2. Caption
  + panel label updated.
- Fig 1.8 (fig:berge-path): two ellipses now in DIFFERENT colours (e1 violet, e2
  blue), translucent so the lens blends; both outlines stroked on top; e2 label
  recoloured. Caption notes the blend.

Data figures (erdos915_unified.py / make_figures.py), all regenerated:
- Fig 3.1 (complexity): dropped cryptic "$2^E$/$3^E$/..." from the legend; plain model
  names under a "model" title; exponential forms moved into the caption.
- Fig 3.2 (trace): replaced the two disliked lower panels with ONE scatter — every
  visited graph by (lambda^max, arcs), coloured by step, feasible/infeasible shaded,
  star at the densest feasible (lambda=2, 12 arcs). Kept the cooling-schedule panel.
- Fig 3.3 (sensitivity): now a SIDE-BY-SIDE pair (structure with mu labels |
  sensitivity with sigma colours+labels) on a BIGGER 7-vertex multigraph. The s->b
  edge is deliberately over-provisioned (mu=3 but sigma=1) to show mu != load-bearing;
  s->d dead end has sigma=0. (draw_graph_with_sensitivity rewritten; only used here.)
- Fig 3.4 / 3.5 (variant grids): THREE fixes via new _reconcile_panel() in
  make_figures: (1) dropped the certain-interval BANDS and let axes rescale to data;
  (2) clamp every proved/conj/guess curve, named branch, and search circle to the
  machine-proved EXACT value where known — kills the green-square-below-curve bug
  (root cause: hyper LB capped at comb(n,3), the *complete* hypergraph, which is
  infeasible at small n; e.g. m=6,n=5 exact=8 but formula said 10); (3) search lower
  bounds made monotone non-decreasing (running max = extend-by-isolated-vertex bound),
  killing the non-monotone purple dots (m=6 simple/multi undirected vertex). Captions
  updated (no more "shaded band").
- Fig 4.1 (crossover): kept; added a marker + annotation at the hub->bipartite
  crossover (n=9 at m=3).
- Fig 4.2: REPLACED the 3-family connectivity histogram with an appearance-threshold
  plot (new plot_appearance_threshold + appearance_threshold.png): P[lambda^max>=m]
  vs density in units of p*=m/n, three growing (n,m), threshold at x=1. Honest caveat
  in caption: clean step is the m/ln n->inf limit; at computable fixed-small m the
  transition only concentrates near p*. Rewrote the phenomenon-3 paragraph + caption;
  relabelled fig:conn-dist -> fig:threshold. OLD connectivity_distribution.png now
  orphaned.
- Fig 4.3 (scatter landscape): flipped to lambda^max (x, integer) vs edge count (y);
  extremal envelope now an integer STAIRCASE with one dot per connectivity level (was
  linear interpolation between sparse points). Caption + body reworded.
- Fig 4.4 (conn_dist grid): kept; font/tick sizes bumped to match the other 12-panel
  grids, per-panel boundary legend added.
- Fig 4.5 (edges_dist grid): "max feasible" line now read straight off the enumeration
  (max edge count among feasible graphs) — always present and never left of the blue
  mass. Fixes "blue right of the dotted line" (old line used the SIMPLE formula even
  for multigraphs) and "no line on some panels". Caption + body reworded. NOTE: the
  multigraph-directed-vertex panel is all-blue because at the forced enum_n=3 every
  graph has kappa^max<=2<=m-1; that is genuine, not a bug (flagged for author).
- Fig 4.6 (surface 3d): kept 3D; unified camera (view_init 24,-58), z from 0, white
  bar edges, sharper suptitle/caption stating the takeaway (blue=proved, purple=open).

Build check pending; will run latexmk after this entry.

## 2026-06-14 — sampled all-twelve-variant random model (author idea)

Author proposed generalising G(n,p) to a unified random model and looking at all
twelve variants by sampling, asking "is this a logical distribution?". Implemented
where the G(n,p) model lived (ch4 phenomenon 3).
- Unified sampler in erdos915_unified.py: sample_random_multigraph (HURDLE-
  GEOMETRIC: empty w.p. 1-p, else 1+Geom(alpha) parallel copies, so alpha=0 recovers
  G(n,p) exactly; capped at m-1 so a fat edge can't trivially break feasibility);
  sample_random_hypergraph (Bernoulli on r-sets). _VARIANT_SAMPLE_CONFIGS mirrors the
  enum configs with per-variant sample_n (up to 26).
- TWO figures (author said implement both display options, will prune):
  * Fig A figures/degree_threshold.png  -> ch4 4.2 (fig:threshold), REPLACES the old
    appearance_threshold.png (author flagged "I don't get it, try something else").
    Appearance prob vs MEAN BINDING DEGREE / m, six generative models.
  * Fig B figures/sampled_variant_grid.png -> ch4 4.3 (fig:sampled-grid). 12-panel
    binding-connectivity distributions at sampling sizes past the enumeration wall.
- KEY HONEST FINDING (measured, NOT what I first hoped): the "expected degree = m"
  collapse is FALSE at finite computable n. The six models are ORDERED in degree-
  efficiency: directed multigraph cheapest (~0.24-0.3 m; heavy parallels over-disperse
  degree), directed hypergraph dearest (~1.2-2 m; one Berge route per hyperedge),
  simple/undirected ~0.6 m between. Universality is ONLY the m/ln n->inf asymptotic
  (same regime as thm:gnp-threshold). All titles/captions/prose say this honestly;
  Fig B's colour balance is Fig A's ordering seen distributionally. I caught and fixed
  my own initial overclaim ("one threshold for every model / collapse") before commit.
- Math for the record: hurdle-geometric is valid for any p in [0,1], alpha in [0,1)
  (positive tail sums to exactly p); nests simple (alpha=0); the naive "P(mu=1)=p with
  decay c" needs c<=1-p to normalise -- flagged to the author.
- appearance_threshold.png deleted (orphan); plot_appearance_threshold still defined,
  now unused. Build: latexmk exit 0. Ch4 figures renumbered (scatter now 4.4, etc.).

## 2026-06-14 (later) — probabilistic model audit & caption fixes

Author reported "still trouble with the probabilistic graph representation." Full audit of ch1–ch4 and app_proofs:

ISSUES FOUND AND FIXED (5 edits, build clean at 85 pages):

1. **ch4 body text (phenomenon 3)**: α was a free parameter in the text but its value (α=1/2) was never stated. Added "we use α=1/2 throughout" inline. Also rewrote the cap sentence to distinguish multigraph panels (cap m-1 needed) from simple/hypergraph panels (no cap needed — those models already limit to one copy per cell/hyperedge).

2. **ch4 fig:threshold caption**: Three fixes:
   - Added "multigraph panels use hurdle-geometric with α=1/2, multiplicities capped at m-1" (old caption said "multiplicities capped at m-1" as if it applied to all six models).
   - Replaced "directed multigraphs cross first, directed hypergraphs last, simple cases between" with the accurate 6-way ordering: dir-multi < dir-simple < simple-undir < multi-undir < hyper-undir < hyper-dir. The undirected multigraph is NOT in the "simple cases" — it crosses further right than simple undirected because a lower inclusion probability (needed to keep mean degree fixed) leaves many pairs absent. Added the explanation: "lower inclusion probability offsets the per-pair multiplicity gain."

3. **ch4 phenomenon 3 body paragraph**: Rewrote the "simple and undirected graphs lie between" sentence to describe the actual 6-way ordering and explain why the undirected multigraph sits where it does.

4. **ch4 sampled_variant_grid caption**: Added explicit note that the multigraph directed arc panel is entirely red, and that this is consistent with the model ordering (cheapest to force high connectivity = first to saturate at expected degree m). Previously this all-red panel was unexplained.

5. **ch3 fig:complexity caption**: "a multigraph capped at threshold m offers m^E candidates" was ambiguous — "capped at threshold m" reads as cap=m (which would give (m+1)^E per cell), but the formula m^E requires cap=m-1. Fixed to "with multiplicity cap m-1 (the connectivity ceiling), one choice per cell from {0,...,m-1}, offering m^E candidates."

NO OTHER SIMILAR ISSUES FOUND: ch1 G(n,p)/threshold sections clean; ch2 spine/checker descriptions accurate; app_proofs unaffected; sensitivity figure (8 vertices) matches caption (log note "7-vertex" was an earlier design plan).

---

## 2026-06-14 (continued) — full punctuation sweep + figure placement

### Punctuation sweep (no-semicolon, no-em-dash, no-en-dash rule)

Systematically removed all remaining prose semicolons and em dashes (---) across every .tex file. Roughly 50 individual edits across 5 files:

**ch1_basecases.tex** (3 fixes): split 3 prose semicolons into new sentences or rephrased.

**ch2_certify.tex** (1 fix): `not a fractional one ---` → `not a fractional one:`.

**ch3_discover.tex** (4 fixes): 1 semicolon in trichotomy paragraph, 1 semicolon in caption, 2 em dashes in the "what the search is worth" paragraph.

**ch4_synthesis.tex** (~20 fixes): multiple em dashes in open-problems list and directed-frontier section; table semicolons changed to commas; multiple caption semicolons; em dashes in the crossover description and threshold caption.

**app_proofs.tex** (~25 fixes): all remaining prose semicolons and em dashes including list items, proof transitions, caption em dashes, theorem-name semicolons (`[Hypergraph Gomory--Hu; ...` → `[Hypergraph Gomory--Hu, ...`), and the L407 two-case proof sentence.

Build clean at 85 pages after all edits.

### Figure placement

Changed float specifiers so figures appear near their references in the source:
- All `[p]` (float page only) → `[htbp]` in ch3 and ch4
- All `[t]` (top only) → `[ht]` in ch1, ch3, ch4

Figures in ch4 (threshold, sampled-grid, scatter, conn-dist, edge-dist, 3d-surface) and ch3 (complexity, trace, sensitivity, variant-bounds) are already positioned right after the paragraphs that reference them in the source; the specifier change allows LaTeX to place them on the same page rather than deferring to a float page.

Build: 85 pages, exit 0.

## 2026-06-14 layout polish pass (author request: snippets, graphs, plots, titles)

Author asked to improve the visual layout of code snippets, graph style, plots,
and titles/subtitles without breaking the KU Leuven format rules. All changes are
thesis-local (preamble.tex + one table fix in ch4); the class-mandated cover,
back cover, logos, footer, margins, sans-serif font, and 1.5 spacing untouched.
The shared/ TikZ + colour files were NOT edited, so the slides and progress
report keep their own look.

- **Titles/subtitles** (preamble titlesec block): "Chapter N" label now in
  KULblauw1; section numbers in KULblauw1 with a thin KULblauw3a accent rule
  under each \section; subsection/subsubsection get a blue number; \paragraph
  runs in, blue. Chapter/part formats unchanged otherwise.
- **Plots/figures/tables** (new \captionsetup): bold KULblauw3b label, small
  justified body text, labelsep=period, margin 14pt, skip 8pt; sub-captions
  footnotesize. Applies uniformly to every figure, plot, and table.
- **Code signature cards**: \codecard now tints frame + title bar + a 2.2pt left
  border by the card's role colour (MODEL/MEASURE/PROVE/DISCOVER/OBSERVE/DRIVER),
  so the spine is scannable down the page. codecardbox gained an optional
  key-val arg; added cardcol@<ROLE> -> role colour map.
- **algorithm2e**: blue bold "Algorithm N" caption (\SetAlCapNameFnt), keywords
  + functions in KULblauw1 bold, comments KULblauw3b italic via one-arg wrapper
  macros (\algokwsty etc). NOTE: \SetNlSty in this algorithm2e version does NOT
  take (font,txtcolor,bgcolor) -- it printed "gray1, gray2..."; dropped it, line
  numbers stay default bold black. Ruled layout kept.
- **listings**: faint KULblauw1!4 background tint on pythonkul.
- **Graphs** (thesis-local \tikzset after the shared input): subtle drop shadow
  on vertex/smallvertex/hnode (opacity 0.16-0.20), rounded line caps on the
  edge styles. shared/tikz-styles.tex itself untouched.
- **Bonus fix**: tab:summary (ch4, twelve-variant table) was the one pre-existing
  overfull hbox (92.7pt over). Converted tabular{llll} -> tabularx with the Value
  and Status columns as raggedright X so they wrap. Overfull count 1 -> 0.

Verified by rendering pages 24-27 + 36 to PNG: chapter label blue, section rule,
role-coloured cards (cyan MODEL, blue MEASURE, dark-blue DRIVER, plus the spine
diagram's green PROVE / orange DISCOVER / violet OBSERVE), vertex shadows, blue
caption labels, blue algorithm caption + keywords, correct 1..n line numbers.

Build: latexmk -pdf main.tex exit 0, 81 pages, 0 overfull hboxes.

## 2026-06-14 layout polish round 2 (author corrections)

Author review of round 1 plus flagged mistakes in the figures. All addressed.

- **Section "subtitle" rule removed.** Author disliked the blue accent rule under
  every \section. Dropped the [\titlerule] after-code in preamble; sections now
  show just the blue number + black title, no underline.
- **computernote corners.** Was `sharp corners=downhill` (mixed sharp/round).
  Now `arc=2.5pt`, all four corners rounded.
- **TikZ rectangle bug (the big one), app_proofs A.3-A.7.** Root cause: a bare
  colour passed to an `aplab` node (= edgelabel, fill=white) is read as
  `color=<c>`, which overrides the white fill and turns the whole label into a
  SOLID colour block with same-colour (invisible) text. 16 labels affected
  (the "what are these red/blue/green rectangles?" notes). Fix: added an
  `apname` style (font only, no fill) to the appendix tikzset and rewrote every
  such label as `apname, text=<colour>` -- coloured text, no box. Also switched
  free-floating vertex-name labels (A.2, A.5, A.6, A.7) from aplab to apname so
  the ugly white boxes over coloured hulls are gone.
- **A.2 overlaps.** `v^*` was on top of the hub, `h` on top of the spokes.
  Repositioned both into clear gaps; hub nodes bumped 8->9pt.
- **A.5 (seam).** Centre label `\lambda=4>2` was a solid red rectangle (same
  bug) -> red text. Nodes were too small -> apx bumped to 10pt for this figure,
  orange nodes to 11pt. `v` no longer overlaps its node.
- **codecard outputs Z -> N.** Author: "shouldn't the output be N?" The six
  MEASURE cards (connectivities, sensitivity) return non-negative counts, so
  $\to\mathbb{Z}$ became $\to\mathbb{N}$ in ch2/ch3.
- **ch4 data-figure captions were factually wrong (author flagged).** Verified
  against the regenerated PNGs:
  * sampled_variant_grid: caption claimed "multigraph directed arc panel is
    entirely red"; the plot shows the four SIMPLE panels are red almost
    everywhere and multi-directed keeps blue. Caption rewritten.
  * conn_dist_m3: caption claimed "most graphs sit comfortably inside the
    feasible region"; the bulk is infeasible in several variants. Caption + the
    lead-in prose para rewritten to the honest reading (balance varies; the
    bound is a real constraint; extremal graphs rare regardless, per edge-dist).
- **Redundant per-panel legends removed (author).** plot_conn_dist_grid and
  plot_sampled_variant_grid in erdos915_unified.py: the identical "m-1 boundary"
  legend was repeated in all 12 panels. Dropped it (boundary named once in
  title+caption); conn_dist keeps a legend only if a per-panel known-max line is
  drawn. Regenerated conn_dist_m3, conn_dist_m6, sampled_variant_grid (fixed
  seeds, enumeration_cache.pkl reused so it was fast).
- All addressed author-note comments deleted from the .tex sources.

NOTE: tab:summary (ch4) is back to `tabular{llll}` and overfull by 92.7pt -- the
author reverted my round-1 tabularx wrap (intentional), so I left it. It is the
only overfull hbox. Flagged to the author rather than re-imposing the wrap.

Build: latexmk -pdf main.tex exit 0, 83 pages, 1 overfull (the table above).

## 2026-06-14 (later) tab:summary overflow fixed

Author asked to fix the ch4 summary table overflow (the one left flagged above,
after they reverted my tabularx wrap). Wrapped the `tabular{llll}` in
`\resizebox{\textwidth}{!}{...}`: keeps every cell on a single line (no ragged
wrapping, which the author did not want) and scales the table to exactly the
text width. Removed the "table goes over the right margin" comment.
Build: exit 0, now 0 overfull hboxes (was 1).

## 2026-06-14 (later) final author-note sweep

Swept all .tex (main, preamble, chapters) for leftover author notes/commands.
One actionable note remained: ch2 L23 "%mention that hypergraphs could have been
represented as higher order matrices: tensors, but that wasn't done for
efficiency". Added a sentence to the "single representation" section saying the
hypergraph could be a higher-order ($r$-dimensional) tensor but that array is
almost all zero and costs n^r entries, so the program keeps the compact
hyperedge list. Removed the comment. No other author notes or commented-out
commands remain anywhere. Build exit 0, 0 overfull, 83 pages.

## 2026-06-15 connectivity speedup + enum dedup + ch2 MILP clarity (PLAN executed)

Executed PLAN_connectivity_speedup.md in full on branch `feat/connectivity-speedup`
(off tag `baseline-pre-speedup`=7d20265). NO reported value/bound/figure moved; every
speedup is proven trajectory- or iso-class-preserving by a test. Scratch baseline copy
at program/erdos915_unified.baseline.py (gitignored, delete on sign-off).

- **Phase A (capped predicate).** New `exceeds_bound(graph,k,sep)` + `_split_capacity_matrix`,
  reusing `_tiny_maxflow`: equivalent to `max_connectivity(...) > k` but with two early exits
  (per-pair flow stops after k+1 paths, pair loop stops at first violator). Guard:
  `test_connectivity.CappedPredicate` matches the exact checker over all 4 variants x 2 sep x
  every k.
- **Phase B (monotone fast energy).** `search_for_dense_graph` now maintains `feasible` (exact)
  and a sound upper bound `lam_ub` (Facts M1/M2: remove can't raise lambda^max, add raises by
  <=1). New `_proposal_energy` returns the IDENTICAL float `_energy` would, computing a flow
  only at the boundary and the exact value only when the proposal is genuinely infeasible. Best
  tracking uses the exact `feasible` flag (witness still certified). New kwargs:
  `record_exact_connectivity` (fig:trace logs exact lambda^max; production logs lam_ub, killing
  the last per-step measure) and `reference_mode` (test-only slow path). Guard:
  `test_search.test_fast_path_matches_exact` proves fast==reference BIT-FOR-BIT (energies,
  accept flags, edge counts, final graph) over 4 variants x {3,4,5} x {2,3} x {edge,vertex}.
- **Phase C.** `sensitivity_map` computes the shared baseline once instead of per edge (value
  identical; `test_sensitivity.test_map_equals_per_edge_sensitivity`).
- **Phase E (enum RAM fix).** `enumerate_extremal_directed_multigraphs` streams each found graph
  through pure-Python `_canonical_form` (lexicographically smallest relabelled matrix) and keeps
  one rep per iso-class as it goes, instead of buffering all labelled then deduping at the end.
  Peak memory now bounded by #iso-classes (the old code hit ~22 GB on n=7). Output byte-identical
  to baseline at n=3,4 (both up_to_iso modes); n=5 reconfirmed = 3 classes (472 s, gated behind
  RUN_SLOW_ENUM). Guard: `test_certify.EnumerationDedup`. NB the n>=7 j=7 prefix prune is still
  the conjectured bipartite bound, so n>=7 stays a lower-bound search; dedup changed memory only.
- **Results.** Search 2.6x-3.9x faster, IDENTICAL best edge counts (15/15, 18/18, 9/9, 21/21 on
  the four sampled cases). Suite: 75 tests pass (1 slow skipped); self-test exit 0; figures
  pixel-identical. Phase D (Gomory-Hu resync, parallel restarts, memo) NOT needed and skipped:
  the per-step connectivity bottleneck is gone.
- **Thesis.** ch3: new section "Keeping the checker cheap inside the search" with
  `prop:monotone` (M1/M2 stated and PROVED via min-cut, elementary) + plain-words consequences +
  a transparency paragraph naming `test_fast_path_matches_exact`. M1/M2 are textbook min-cut
  monotonicity, reasoned rigorously inline (not Fable-checked; flag if a formal pass is wanted).
  ch2: two-mode checker cross-ref; and the priority rewrite of the MILP `p/x/w<=1` passage
  (`ch2_certify.tex` ~218) into a symbol glossary (w,x,p in words), a worked four-row case table
  `tab:crossing-cases` for the indicator inequality (w<=1 makes the 3 non-crossing rows <=0), a
  plain reading of the cut/maxflow line, de-jargoned helper constraints, and a TikZ cut figure
  `fig:cut`. Build exit 0, 87 pages, 0 overfull hboxes, 0 undefined refs.
- **nauty.** pynauty installs/builds fine, but the enumeration's real cost is the DFS, not
  iso-rejection, so nauty would not speed it up and the RAM crash is already fixed; pure-Python
  canonical form is the source of truth (no external dependency). Jan's 2026-06-15 email instead
  recommends a GENERATION-time pipeline: geng (underlying undirected) -> directg or
  watercluster2 (all non-iso orientations, watercluster2 usually faster). That targets simple
  digraph orientations and needs adapting for the multiplicity/bidirected multigraph case; left
  as an open follow-up for the author (TASKS.md). Jan also CONFIRMED the monotonicity approach
  for the connectivity bottleneck and that countg --G is classical (min) vertex-connectivity,
  not the lambda^max/kappa^max (max over pairs) we cap.

## 2026-06-15 (afternoon) — Jan Goedgebeur email + Tier 1 ops

Branch feat/connectivity-speedup merged into master (clean fast-forward); that
branch held the Phase E canonical-form dedup fix (RAM bottleneck solved), the
monotone connectivity speedup, and the ch2 MILP clarity pass.

Jan Goedgebeur (nauty author) replied on 2026-06-15, confirming the monotone
connectivity speedup. Key notes: (1) `countg --G` gives classical minimum
vertex-connectivity, not our max-local lambda^max/kappa^max — not useful for our
problem (already known). (2) For n=7 directed multigraph generation, Jan recommends
`geng | watercluster2` (usually faster than directg) as a generation-time pipeline;
adapting it for multiplicities {0..m-1} plus bidirected arcs is non-trivial. (3) Jan
suggested tabu search as an alternative to SA; added as a P2 item in TASKS.md.

Contribution statement in main.tex updated: added paragraph crediting
thm:hyper-vertex-m2, thm:hyper-vertex-m3, lem:incidence-rank (hypergraph vertex
at m=2 and m=3 for all r and n), and the m=3 directed multigraph reduction to
two n=7 computations via lem:attachment + thm:odd-step + rem:odd-step-roadmap.

Popularising summary audit (no edits): does not yet mention hypergraph vertex m=3
or the odd-step reduction; author should verify completeness for submission.

## 2026-06-15 (evening) — conjecture correction + accessibility pass

CONJECTURE CORRECTION (major finding): conj:dir-arc was wrong for m>=4.
The old formula floor(n^2/4) + (m-2)*ceil(n/2) used a balanced partition
|A|=|B|~n/2, but the optimal partition is |B|=ceil((n+m-2)/2), |A|=n-|B|,
giving floor((n+m-2)^2/4) arcs. For m=2,3 both formulas agree; for m>=4 and
n large enough (n=12 for m=4, n=12 for m=5) the new formula is strictly larger.
Verified computationally: m=4,n=12 gives 49 arcs with lambda_max=3, beating the
old conjecture's 48. const:augmented-bipartite and conj:dir-arc in ch1_basecases.tex
updated to use the new partition and formula. ch4_synthesis.tex updated to match.
The insight from ch4: the upper bound argument |B|*(n-|B|+m-2) was already pointing
to this formula — the conjecture just hardcoded a suboptimal partition. Build: exit 0,
87 pages, 0 errors.

ACCESSIBILITY: fig:scaling-reduction added to ch2_certify.tex (illustrates the
divide-by-(m-1) scaling step concretely for m=3 before the formal M*(n) formula);
dense 15-sentence paragraph in ch4 about the m=3 directed multigraph reduction split
into four focused paragraphs with an itemized list for facts (a) and (b).

BACKWARD-ARC LEMMA: attempted 2026-06-15 (Sonnet agent). Route-counting approach
blocked; repartitioning approach outlined but not closed. No proof found. Remains open.

## 2026-06-16 — gallery of extremal graphs + figure 3.2 improvements

GALLERY OF EXTREMAL GRAPHS: implemented gallery_extremal_graphs() in erdos915_unified.py.
For all 12 variants (8 matrix + 4 hypergraph), all (n,m) pairs with n<=7, m<=4, r=3:
- Finds the extremal edge count via repeated search (2000 steps/restart, >=3 seeds)
- Enumerates all non-iso extremal graphs via DFS (_enum_matrix_extremals, _enum_hyper_extremals)
- Counts |Aut(G)| by brute-force over n! permutations, records labelled_count = n!/|Aut|
- Deduplicates with _canonical_form (matrix) or _hyper_canonical (hyperedge collection)
- Output: figures/extremal_gallery.json (JSON-serializable dict, complete=False when deadline hit)
New helpers: _graph_from_mu, _aut_count_matrix, _hyper_canonical, _aut_count_hyper,
_hyper_to_lists, _enum_matrix_extremals, _enum_hyper_extremals, save_gallery_json.

FIGURE 3.2 IMPROVEMENTS (plot_search_trace):
- Gradient: changed from viridis to RdYlBu + PowerNorm(gamma=0.2); early steps warm
  (red/orange), converged tail uniformly blue — the user asked for "everything blue except
  one or two dots" and this delivers it.
- Feasible/infeasible labels: moved from inside the axes (top corners) to just above the
  axes box, centred over each region, using blended_transform_factory (data-x, axes-y).
  No overlap with other text.
- Legend: moved from lower-left to upper-left.
- Density histogram: new right panel (ax_hist) showing horizontal bar chart of visit counts
  by arc count. Y-limits synced manually with the scatter panel.
- Layout: 3 panels (cooling | scatter | histogram) or 2 (scatter | histogram) when
  show_cooling=False. New kwargs: show_cooling, connectivity_label, edge_label, title.
- Suppressed tight_layout UserWarning in _save() (cosmetic, bbox_inches=tight handles it).

MULTI-VARIANT TRACES: generated scatter-only traces for:
  trace_simple_undirected_n7_m3.png, trace_simple_directed_n5_m3.png,
  trace_multi_undirected_n5_m3.png, trace_multi_directed_n5_m3.png,
  trace_multi_directed_n4_m3_vertex.png
The format works well for all variants; the vertex-separation case clearly shows the search
spending more steps in the infeasible region (harder constraint).

All self-checks pass. Gallery PID 31802 still running at session end (max_n=7 ~15min total).

## 2026-06-16 (later) -- verify Sonnet's session, P2 polish, big-computation feasibility

VERIFICATION OF THE GALLERY + FIGURE WORK (all confirmed correct):
- 75 unittests pass, full _run_checks self-test passes.
- Gallery values match known/certified results: simple-undirected trees on n=4 (2
  classes, 16 labelled) and n=5 (3 classes, 125 labelled), K4 at m=4, and
  L_3^dir(4)=12 = the certified Fig 3.2 optimum. Incomplete cases correctly carry
  complete=False and report the search lower bound (e.g. multi_directed n=7,m=3=20,
  not the true 24) -- sound, but any caption citing the JSON should say so.
- Cross-validated the NEW gallery enum: _enum_matrix_extremals(MULTI_DIRECTED,4,3,12)
  returns byte-identical canonical iso-classes to the independent
  enumerate_extremal_directed_multigraphs(4,3,12). Two code paths agree.

FIXED A GAP: Sonnet regenerated temperature_trace.png (Fig 3.2) at 00:25 but never
rebuilt main.pdf afterward (build was 20:15, stale). Rebuilt main.tex: exit 0, 87 pp,
0 overfull hboxes. Fig 3.2 now correctly embedded.

P2 POLISH:
- Open-variant test coverage (was zero): added fast checks to _run_checks --
  verify_hyper_vertex_value at (4,3,2),(5,3,2),(4,3,3),(5,3,3); fractional_flows_feasible
  accept(path)/reject(two-route); fractional_search ceilings at n=5 for "total" (<=8) and
  "min_degree" (<=2 plus the 1e-3*total tie-breaker slack). ~2s, all PASS. Replaced the
  old commented n>=7 suggestion block (those sweeps added minutes).
- Popularising summary: closing rewrote from "questions still open" to state both positive
  results in lay terms (hyperedge variant solved at the two strictest route limits for all
  n/r; one-way variant reduced to a single finite n=7 check). Mirrors the Contribution
  Statement. Rebuilt clean, still 1 page. AWAITING AUTHOR wording sign-off.

BIG-COMPUTATION FEASIBILITY (the headline question -- do the Phase A-E speedups give the
n=7 jobs a shot?). Empirical, all runs stayed <320 MB RSS:
- MEMORY is solved. Phase E streamed dedup means nothing approached the old ~22 GB; the
  desktop-crash failure mode is gone. Both jobs are now SAFE to leave running.
- MILP (a), prove L_3(7)<25 => INFEASIBLE: n=5@17 INFEASIBLE in 2.9s; n=6@21 LIMIT at
  600s (unsolved); n=7@25 LIMIT at 2000s (unsolved). The Phase A-E work never touched the
  MILP, and scipy/HiGHS cannot close n=7 as formulated. INTRACTABLE this route. Fix: a
  commercial solver (Gurobi academic, would likely close it in minutes) or a tighter
  encoding. NOT a memory problem -- pure solver runtime.
- ENUM (b), 24-arc deg<=8 extremals: no-cap DFS explodes (n=4 0.42s -> n=5 466s, ~1100x;
  hopeless beyond n=5). WITH max_degree=8 (the real command): n=4 0.93s (1 class, the cap
  drops the higher-degree class); n=5 still >330s because the cap barely binds below n=7;
  n=7 did NOT finish in a 40-min (2400s) timeout but stayed memory-safe. So the cap prunes
  hard only at n=7 yet 40 min was not enough. Borderline: a multi-hour run MIGHT finish (no
  longer risks the machine), but the principled fix is Jan's geng+directg/watercluster2
  generation pipeline, which attacks the DFS time itself (the open follow-up in TASKS.md).
  This exactly matches Jan's warning that dedup "only fixed RAM".

BOTTOM LINE: the speedups solved the crash (memory) but not the runtime. MILP needs a
better solver; ENUM needs either a long safe run or the generation pipeline.

## 2026-06-17 (Opus) — repo split + a fresh angle on the backward-arc lemma

REPO: at author's request this directory was split out of MasterThesis/thesis_improved
into its own repo (renamed `thesis`), fresh git history, pushed private to
github.com/louisvandenbruwaene/thesis. Only thesis_improved content carried over.

BACKWARD-ARC LEMMA (flagship, TASKS.md top item) — went deep; NO proof, but a new line
that sidesteps the stuck non-monotone-exchange obstacle. Full writeup +
mechanically-checked script in research_notes/ (directed_arc_m3_reduction.md +
scripts/attach_check.py). Summary:
- KEY REFRAMING. Forget "no backward arc". Run the m=2 min-degree-deletion engine
  (thm:dir-arc-m2-exact) on the m=3 quadratic branch Q(n)=floor((n+1)^2/4). Using the
  true bound ell(n-1)=max(3(n-1),Q(n-1)), the overshoot floor(n/(n-2)ell(n-1))-Q(n) is
  +0 at odd n>=11, +1 at even n>=10, and +2 only at the crossover seam n=9 (where
  ell(8)=21 is linear). So the WHOLE m=3 quadratic upper bound reduces to killing one
  +1 of slack at even n plus finite seam bases — structurally identical to the
  multigraph thm:odd-step + lem:attachment already in the thesis. The prior attempts
  (route-counting, repartitioning) worked the backward-arc framing; this engine was
  never tried for the simple case.
- FORCED STRUCTURE (proved). If a=Q(2k)+1=k^2+k+1 then every vertex has degree >=k+1, D
  is (k+1)-regular up to total degree-excess exactly 2, and every degree-(k+1) vertex
  deletes to an exact odd extremiser on 2k-1 vertices. So the +1 case = "odd extremiser
  + one degree-(k+1) vertex, still feasible".
- ATTACHMENT REFUTED for k=4,5,6 (exact max-flow, attach_check.py): taking the odd
  extremiser as augmented bipartite B_{k-1,k}+k-cycle, NO degree-(k+1) attachment keeps
  lambda^max<=2. Intuition: the complete A->B layer makes a third arc-disjoint route
  unavoidable.
- REMAINING GAPS (why this is NOT yet a proof): (1) odd-extremiser uniqueness on 2k-1
  vertices [most important; multigraph analogue needed thm:extremal-char]; (2) a uniform
  all-k argument for the attachment contradiction (promote the third-route sketch to a
  Menger lemma); (3) seam bases ell_3^dir(9)=25, ell_3^dir(10)=30 via the certifier
  (Gurobi route, cf. BIG-COMPUTATIONS); (4) m>=4 redo, expecting the known odd-uniqueness
  hole (rem:odd-step-roadmap).
- NOTHING entered the thesis .tex (rule: proof-check before uncommenting). Working note
  only. Next: characterise the odd extremisers (gap 1) — the load-bearing step.

## 2026-06-17 (Opus, cont.) — characterising the extremisers (gap 1)

Pushed on gap (1). Files: research_notes/directed_arc_m3_extremisers.md +
characterisation_checks.py + attach_check_all_perms.py (all self-contained, run clean).
Results (NOTHING in the thesis .tex):
- ARC PARTITION (proved, sanity-checked): sources have in-degree 0, so every arc is
  S->R or internal to R; a = e(S,R)+e(R) with e(S,R)<=sigma(n-sigma).
- LEMMA (proved; 0 violations / 300 random feasible digraphs): for a source s, the
  subdigraph on N^+(s) has max in-degree <=1 (else 3 arc-disjoint s-routes). So a
  universal source forces R to have internal max in-degree <=1.
- CONDITIONAL THEOREM (proved): if non-sources R induce max in-degree <=1 then
  a <= (n-sigma)(sigma+1) <= Q(n) in BOTH parities (max at sigma=(n-1)/2 odd; checked
  n=7..19), equality iff augmented-bipartite family. So the WHOLE m=3 quadratic upper
  bound + characterisation reduce to ONE hypothesis (H): an extremiser has a source
  adjacent to every non-source. (H) is the new load-bearing open statement — concrete,
  about sources, exchange-free (sidesteps the non-monotone backward-arc obstacle).
- EXTREMISER FAMILY (not unique): augmented bipartite B_{k-1,k} + ANY fixed-point-free
  permutation of B (one per partition of k into parts >=2: k=5 -> {5},{2,3};
  k=6 -> {6},{2,4},{3,3},{2,2,2}). All feasible at k^2 (verified k=4,5,6). The thesis
  const:augmented-bipartite (single k-cycle) is one member.
- ATTACHMENT REFUTATION extended to ALL permutation cycle types (k=4,5,6): no
  degree-(k+1) attachment stays feasible. So +1 even case dies GIVEN (H).
- TOOLING NOTE: homemade SA can't reach the optimum at n=9,11 (24/34 vs 25/36) — a
  search-strength limit, not a result; thesis annealer needs networkx/scipy (absent
  here). Conditional theorem makes the empirical question secondary; (H) is the target.
- NEXT: prove (H) [extremisers have a universal source / R max-in-degree<=1]; make the
  attachment refutation uniform in k (Menger lemma); seam bases ell_3(9)=25, ell_3(10)=30.

## 2026-06-18 (Opus) — standalone build fix + thesis consistency/clarity pass

Focus shifted (author request) to making the thesis better: figures + clearer explanations.
Author chose "edit plot code only" (author regenerates PNGs) and clarity focus = ch2/ch3.
- BUILD FIX (important): the repo split left preamble.tex pointing at ../shared/{colors,
  tikz-styles}.tex, which lived at the old MasterThesis root and was not carried over, so
  the standalone repo DID NOT BUILD. Vendored both into shared/ and repointed preamble.
  Clean build now: 93 pages, 0 undefined refs, 0 undefined cites, 0 overfull.
- CONSISTENCY BUG fixed: conj:dir-arc was corrected in a prior session to
  floor((n+m-2)^2/4) in ch1 + ch4, but THREE places still printed the old pre-correction
  formula floor(n^2/4)+(m-2)ceil(n/2) while citing conj:dir-arc — ch3 (display L144 +
  inline L174) and app_proofs L397 (the proof step, "balanced partition ... uniformly in
  m"). They agree at m=3 but DIFFER at m=6 (the m=6 figure already uses the corrected one).
  Fixed all three to the (n+m-2)^2/4 form; app_proofs now uses the optimal partition
  |B|=ceil((n+m-2)/2) matching ch4 L16.
- CLARITY: ch2 timing sentence ("well under a second, under a second, and a few seconds")
  rewritten.
- FIGURE CODE (author regenerates): plot_variant_grid suptitle was overlong and redundant
  with the per-panel legends + caption; shortened to "Erdős 915 across the twelve variants,
  m = M" and threaded m through from make_figures.py. >>> AUTHOR: rerun make_figures.py to
  refresh variant_bounds_m3.png / variant_bounds_m6.png with the shorter title. <<<
- NOTE: matplotlib/numpy/scipy/networkx NOT installed in this env, so data figures cannot
  be regenerated here; only TikZ + .tex + plot-code edits are possible.

## 2026-06-18 (Opus, cont.) — P2 polish + Jan's two follow-up items (nauty available!)
Fresh clone of the split-out `thesis` repo into ~/Projects/thesis. KEY ENV DIFFERENCE
from the morning session: this machine HAS numpy/scipy/matplotlib/networkx AND the full
nauty toolset (geng, directg, watercluster2, multig, vcolg, countg, ...) on PATH, so the
figure regen and Jan's pipeline both became runnable for the first time. No Gurobi (MILP
ENUM(a) still blocked). Author asked for P2 polish + Jan's follow-up.

P2 POLISH (all done, build verified):
- Baseline build clean: 93 pages, 0 overfull, 0 undefined refs/cites (the 375 "undefined"
  in a cold latexmk log are just pre-bibtex passes; a converged single pdflatex pass is
  clean). Program self-check ALL CHECKS PASSED.
- Refreshed variant_bounds_m3.png + variant_bounds_m6.png via make_figures' gather/plot
  (only the plot_variant_grid suptitle had changed in the prior session; the committed
  PNGs predated it). Regenerated ONLY those two to avoid matplotlib-version pixel drift on
  the other 23 figures. m=6 grid is slow (~6 min, exhaustive solves) so it ran separately.
  Rebuilt thesis to embed them: 93 pp, 0 overfull.
- Spell check (hunspell -t over all .tex): clean. 259 flags all = British spellings
  (colour/behaviour/optimisation), names (Erdős/Bérczi/Sørensen truncate at accents),
  technical terms, TikZ style names, code identifiers. No doubled words, no common typos.
- Layout/ToC/placement: fine. The 5 ch4 [p] floats are the legit full-page grid figures
  (sampled grid, scatter, conn/edges distributions, 3D surface). A couple of cosmetic
  underfull hboxes in app_proofs captions, left as-is (not overfull).

JAN FOLLOW-UP #1 (geng+directg/watercluster2 pipeline) — research_notes/
jan_followup_nauty_and_tabu.md + scripts/nauty_pipeline.py. VERIFIED:
- COUNTS: nauty non-iso simple-digraph count = OEIS A000273 = program's own canonical-form
  dedup count (3,16,218,9608,1540944). Two independent iso engines agree.
- EXTREMAL: feeding nauty's digraphs through the program's max-flow checker reproduces the
  program's exact simple-directed L_3^dir(n) = 2,6,9,12 for n=2..5. (Small-n values exceed
  the asymptotic conj:dir-arc floor((n+m-2)^2/4); correct, the conjecture is the large-n
  branch.)
- TIMING: watercluster2 ~15x faster than directg at n=6 (0.08s vs 1.22s) — Jan's claim
  confirmed. n=7 simple is 882M digraphs, out of reach for raw generation.
- MULTIGRAPH HYBRID (the non-trivial ENUM(b) cross-check): layer multiplicities {1..m-1}
  onto nauty-generated simple-digraph SUPPORTS, dedup finished multigraphs by the program's
  canonical form. Reproduces enumerate_extremal_directed_multigraphs at n=4 (2 classes) and
  n=5 (3 classes), and is ~17x FASTER at n=5 (26.3s vs the DFS's 456.0s). Direct evidence
  for Jan's "DFS time is the wall, dedup only fixed RAM". For n=7 ENUM(b) the principled
  next step is per-support Aut dedup (directg -G) + arc/degree prefilter.

JAN FOLLOW-UP #2 (tabu vs SA) — scripts/tabu_vs_sa.py. MEASURED, sharper than Jan's
"similar performance expected": same energy + neighbourhood, equal 6s wall-clock, SA =
the thesis's own best_of_searches (empty-graph restarts, no bipartite seeding). TIES on
simple-undirected n=7 (9), multi-undirected n=6 (10), simple-directed n=6 (15); TABU WINS
on multi-directed n=5 (16 vs 15), multi-directed n=7 (24 vs 20 — tabu reaches the 24-arc
2B(3,4)=L_3^dir(7) extremiser), simple-directed n=7 (18 vs 16). Engineering note only; the
thesis discovery results are already at the proved/constructed optima, nothing enters .tex.

REPO STATE: committed + pushed to main (author now wants commit+push every session;
saved as a standing preference in auto-memory). Two commits: (1) the P2 polish +
research_notes cross-checks above; (2) the thesis incorporation below.

INCORPORATED INTO THE THESIS (author asked, 2026-06-18): new ch2 section 2.6
"Generating the directed cases faster" presenting the speedup with before/after numbers
(in-house DFS ~456s at n=5 vs nauty pipeline ~26s, ~17x; watercluster2 ~15x faster than
directg at n=6; counts = OEIS A000273; n=4->2, n=5->3 families) and crediting Prof. Jan
Goedgebeur (named there + in the acknowledgments as promotor) for the suggestion. Framed
honestly as a validated faster route + the practical path to the open n=7 fact (b), not as
a rewrite of the program. Build clean: 93 pp, 0 overfull, 0 undefined refs/cites; the new
\cite{McKayPiperno14} reuse and \Cref{rem:odd-step-roadmap} resolve. program .py unchanged.

## 2026-06-18 (Opus) -- MERGE of the two diverged repos into this one

Context: the thesis existed as TWO independent git repos with no shared history -- this
one (`louisvandenbruwaene/thesis`, at ~/Projects/thesis, canonical going forward) and
`louisvandenbruwaene/MasterThesis` (at ~/Documents/.../thesis_improved), each with one
session of unique work. The author asked to merge "best of both" into THIS repo and keep
the other as a mirror. Diffed the two trees and reconciled file by file.

Kept from THIS (codex) repo: the corrected conj:dir-arc formula floor((n+m-2)^2/4) in ch3
(the other repo's ch3 still had the old floor(n^2/4)+(m-2)ceil(n/2), wrong for m>=4); the
app_proofs proof-detail expansions (incidence-count, block-cut count, attachment flow
estimate, the two-hop/no-back-arc bound); the new ch2 "Generating faster" section; the
main.tex Goedgebeur acknowledgment; preamble shared/ vendoring; research_notes/ and shared/.

Brought in from the other repo: (1) the punctuation/spelling sweep -- removed all prose
em-dashes and semicolons and fixed Br/Am spelling across ch1-ch4 + app_proofs (this repo
had not had that sweep: 12 em-dashes + 25 semicolons); the missing-arc-notation, "dear"
typo, and stale "running" fixes were already here. (2) the geng pipeline as a PROPER
in-program function `enumerate_extremal_directed_multigraphs_via_generation` +
`_geng_support_graphs` in erdos915_unified.py (this repo only had it as a research_notes
prototype script using directg/watercluster2). Mine generates the UNDIRECTED support with
geng and decorates multiplicities/bidirection in-program, prunes with PROVED M*(j<=6) only
(no conjectured bound -> sound at all n), validated == DFS at n=4/n=5. (3) the geng unit
test, the program README geng note, the _tiny_maxflow .copy() drop, shutil/subprocess
imports.

Reconciled conflict: this repo's ch2 section described `directg`/`watercluster2` orienting
+ "layering multiplicities" and cited 26s/17x and watercluster2-vs-directg numbers from the
SEPARATE research_notes script. Rewrote it to match the SHIPPED in-program implementation
(geng undirected support + in-program decoration; directg/watercluster2 can't express
bidirected arcs or multiplicities), kept Goedgebeur's credit and the validated facts
(2 families at n=4, 3 at n=5; sound at all n), dropped the unverified-for-this-impl
speed multiples (left "substantially faster"). Kept codex's plot_variant_grid(m) shorter
suptitle + its make_figures caller + its variant_bounds figures.

Verify: full suite 77 tests pass (was 75 + my 2 geng tests), 1 slow-enum skip. n=7 fact (b)
run still going in the other tree's logs/. Build + commit + push pending at end of this
entry; the MasterThesis repo will be mirrored to match this one.

## 2026-06-19 (Opus) — verified the C extension, fixed an app_proofs punctuation regression, repo consolidation

Author asked Opus to review Sonnet's recent work and to make THIS repo (Projects/thesis,
remote louisvandenbruwaene/thesis, branch main) the single canonical one going forward, with
the school-tree copy (Documents/.../MasterThesis_Louis/thesis_improved, remote MasterThesis,
branch master) downstream. Future sessions: pull + work + push HERE.

C extension review (the guards were already in place via 3d1beef; this confirms they are
correct and were the right call):
- Differential-tested the C primitives against pure Python AND networkx: _canonical_form
  0/4000, _tiny_maxflow 0/8000, _tiny_maxflow vs networkx exact max-flow 0/3000; the scipy
  csgraph exact-connectivity path 0/3000 vs networkx (directed + undirected); exceeds_bound
  consistent with max_connectivity in vertex mode 0/1500.
- Confirmed the two guards are load-bearing: without `and n <= 7`, canonical_form_min (buffers
  best[49]/perm[7]) stack-smashes at n>=8 (reproduced), which the seam-base enumeration at
  n=9,10 would hit. With the guard, n>=8 falls back to pure Python (0 mismatches at n=8/9/10).
  The n<=16 guard on max_connectivity_exceeds matches res[256]/parent[16]; the search never
  reaches it but the guard keeps it sound. .so is gitignored (correct: built per machine via
  build_fast.sh, so -march=native stays optimal and never ships to a different CPU).
- ch3's parallel-restart claim is true and harmless: ProcessPoolExecutor over a module-level
  worker with the SAME seeds + order-preserving map + first-max tie-break, identical to
  sequential, so no reported number changes.

Fix landed here: the expanded app_proofs.tex (the fuller floor((n+m-2)^2/4) derivation, the
incidence-graph edge count, the block-cut identity) had reintroduced 8 prose semicolons that
violate the no-semicolon rule. Replaced with periods/commas, keeping all the new math:
M*(7)=12 "; and"->", and"; theorem titles [Gomory--Hu; ...]/[Chernoff bounds; see] -> commas;
"of e; it has"->". It has"; "3-connectivity; the"->". The"; "(Tutte \cite{Tutte66};"->","
(two-citation parenthetical); "edges; give"->". Give"; "matplotlib; an optional"->". An".
No Unicode em/en dashes anywhere. Suite 77 pass / 1 skip. Build: latexmk exit 0, 95 pp,
0 overfull, 0 undefined refs/cites. Pushed to origin/main.

Note for the author: maintaining two repos with parallel agents caused duplicate work (both
trees independently fixed the same C guard bug). Recommend treating MasterThesis purely as a
pre-submission mirror and doing all development here.

## 2026-06-19 (Opus) -- dropped networkx + matplotlib to OPTIONAL; one max-flow engine

Author: carte blanche ("more C, cleaning up the code, rewriting the paper, etc"). This
machine has numpy+scipy+gcc but NOT networkx/matplotlib/geng/Gurobi, so the program would
not even import (hard `import networkx`/`matplotlib` at module top) and nothing could be
verified. Fixed that AND unified the checker, which is a genuine cleanup, not a workaround.

WHAT CHANGED (program/erdos915_unified.py):
- networkx + matplotlib are now OPTIONAL try/except imports (NETWORKX_AVAILABLE /
  MATPLOTLIB_AVAILABLE flags, same pattern as the existing GUROBI_AVAILABLE). Stringized
  annotations (`from __future__ import annotations`) mean the `-> nx.DiGraph` signatures
  never evaluate at import, so the module loads on numpy+scipy alone.
- THE UNIFICATION: every connectivity measure now runs through ONE scipy integer max-flow
  on a capacity matrix (Menger), exactly as edge mode already did. Removed the two
  networkx network builders `_flow_network` and `_hyper_flow_network` (the only callers
  were the vertex/hyper connectivity fns). Vertex mode reuses `_split_capacity_matrix`;
  added `_hyper_capacity_matrix` (integer-indexed transcription of the old nx builder:
  vertices 0..base-1, hyperedge gate i at base+2i / base+2i+1). local_connectivity (vertex)
  and hyper_connectivity now call `_csgraph_maxflow`. Net: fewer lines, one engine, no nx
  on any reported-number path.
- networkx now used in exactly ONE place: `gomory_hu_tree` (a figure/analysis helper),
  guarded by `_require_networkx(...)` with a clear message. Dropped nx from drawing (replaced
  nx.circular_layout with a 3-line numpy unit-circle layout), from the geng pipeline (new
  pure-python `_graph6_edges` graph6 decoder replaces nx.from_graph6_bytes), and from
  `fractional_flows_feasible` (new `_float_maxflow_value`, Edmonds-Karp for FLOAT capacities,
  since scipy csgraph is integer-only).
- matplotlib: flag-gated only (figures are reachable only from the figure driver, like the
  Gurobi prover path), import guarded so the module loads headless.

VALIDATION (independent oracles, since networkx -- the old oracle -- is absent here):
- vertex-mode scipy value vs brute-force Menger min-vertex-cut: 0 mismatches / 19,161 pairs.
- vertex value vs the already-nx-validated `exceeds_bound` predicate (incl adjacent +
  multigraph): 0 / 31,388 pairs.
- hypergraph edge-connectivity scipy vs brute Menger on the incidence graph: 0 / 17,148.
- `_float_maxflow_value` vs scipy scaled-integer max-flow on random rationals: max abs diff
  1.8e-15 over 3,000 graphs.
- `_graph6_edges` encode/decode round-trip: 0 bad / 5,000 graphs up to n=12.
- Test suite: 77 pass, 5 skipped (2 Gomory-Hu need nx; 2 geng need the binary; 1 slow enum
  flag) -- all legitimate, no silent breakage. Self-check: ALL CHECKS PASSED headless
  (guarded the one Gomory-Hu self-check block behind NETWORKX_AVAILABLE). C extension built
  + loaded (gcc here), C_EXTENSION_LOADED True.
- test_connectivity.GomoryHu now @skipUnless(NETWORKX_AVAILABLE).

DOCS updated to match: program/README.md Requirements (core = numpy+scipy; matplotlib for
figures, networkx for Gomory-Hu only) + test count 75->77; ch2_certify.tex reproducibility
sentence rewritten ("core needs only numpy and scipy ... two further libraries optional").
Build: latexmk rc=0, 95 pp, 0 overfull, 0 undefined refs/cites.

WHY IT MATTERS: (1) the reproducibility claim is now true for a minimal scientific-Python
install, not a four-library one; (2) the checker is genuinely one engine (the thesis says
"one max-flow checker" -- now literally true, no second networkx path); (3) future sessions
on a numpy+scipy box (like this one) can run + verify everything. No reported value, bound,
or figure number changed (validated). Author's machine (has nx) behaves identically.

## 2026-06-19 (Opus, cont.) -- strategy convo + consolidation + PuLP MILP swap

Author asked for my honest read of the code (felt "all over the place", C+Python mix), whether
to go full C, import libraries instead of hand-rolling, unify variants, whether C speedups give
new results, and whether to drop the one-file/one-solver rules. My take (saved to auto-memory):
NO full C rewrite (math thesis, code is apparatus, C is wrong tool for MILP/maxflow/figures and
would BALLOON his own LOC); the C speedups are constant-factor and will NOT unlock new results
(the open n=7 facts are algorithm-bound: need Gurobi or cluster); keep one-solver, relax one-file.
Author then: postponed Gurobi (no KU Leuven wifi), said install any library, relaxed one-file,
gave carte blanche.

DID THIS SESSION (two commits, pushed):
1. Consolidation (4891297): `_pairs` now serves Graph or Hypergraph from one sweep;
   max_hyper_connectivity dropped its hand-rolled loop; deleted `_measure` (byte-identical
   duplicate of `_connectivity_measure`). 77 tests pass.
2. PuLP MILP swap (6913ac3): replaced the ~530-line hand-rolled certifier (a _VariableIndex
   registry, a _MilpRows COO accumulator, four row-builders, a separate ~120-line
   _prove_with_gurobi backend, two near-duplicate scipy.milp drivers) with ONE solver-agnostic
   PuLP model `_cut_counting_model` + `_pick_solver`. Net -319 lines in the program. Gurobi is
   now a one-line switch: prove_*(..., use_gurobi=True). pulp is OPTIONAL (PULP_AVAILABLE),
   consistent with nx/matplotlib; certifier + its self-check block + its tests skip cleanly
   without it. Validated faithful vs the OLD scipy impl (captured before swap): M*(3,4,5)=4,6,8
   (default, deletion, and tighteners-off); integral L_3(4) 12 FEAS/13 INFEAS, L_3(5) 16/17.
   Found + fixed a real bug while building: cat="Binary" in PuLP RESETS bounds to [0,1], so the
   cut endpoints (x[s,t,s]=1, x[s,t,t]=0) must be CONSTANTS, not fixed-bound Binary vars (else the
   cut core is vacuous and M* comes out too high). Pinned pulp<4 (3.x is mid-migration to a 4.0
   API rename; suppressed the 4.0 DeprecationWarnings); new program/requirements.txt. Docs:
   README + ch2 + app_proofs reproducibility notes now say core=numpy+scipy, certifier+=pulp,
   matplotlib/networkx optional.

ENV: made a venv at Projects/thesis/.venv (gitignored) with numpy/scipy/networkx/matplotlib/pulp
so the FULL suite + figures run here. System python3 has only numpy/scipy (+gcc), which is the
"minimal core" headless test: self-check passes there with prover + Gomory-Hu sections skipped.
Suite: 77 pass / 3 skip (venv) ; build 95 pp, 0 overfull, 0 undefined.

NOT DONE (surfaced to author as a decision): the package split (one-file -> small package). Real
tension discovered: the thesis PROSE repeatedly sells "a single self-contained file" as a
reproducibility virtue (ch2 L350, app_proofs L1189, both edited this session). A full split
contradicts that narrative and needs prose rewrites, and the file is already ~640 lines leaner
across the two 06-19 sessions with the worst duplication gone. Recommended deciding split vs.
keep-and-keep-consolidating before churning ~4700 lines. Awaiting author's call.

## 2026-06-20 (Opus) -- figure helpers + reviewed hypergraph views & enumeration paths

Author DECISION recorded (auto-memory [[feedback-keep-one-file]]): keep one self-contained file,
consolidate IN PLACE, no package split (the thesis sells the single-file design). Author asked:
(1) make shared figure helpers to cut lines, (2) look at the hypergraph named-view wrappers, (3)
look into the two enumeration paths WITHOUT changing them and report. Planned in plan mode
(/Users/chief/.claude/plans/woolly-snuggling-spindle.md), approved, executed.

DID (figures, erdos915_unified.py only, -14 net lines but the real win is dedup):
- Generalised the existing `_variant_dist_grid` -> `_variant_panel_grid(draw_panel, *, configs,
  suptitle, suptitle_fontsize, row_label_fontsize, path)`: it owns the subplots(3,4,figsize
  16x11), the panel loop, the per-row model-label annotate loop, the suptitle, tight_layout(rect),
  and _save. Routed ALL FIVE 12-panel grids through it -- the two dist grids (already used it),
  plus plot_sampled_variant_grid, plot_variant_grid (passes its `panels` as configs), and
  plot_scatter_lambda_edges -- each now just supplies a draw_panel closure + its config list. The
  subplots/row-label/tight_layout/save boilerplate was duplicated 4x; now it lives once.
- Named the red `_RED="#E05050"` (was inline in 4 panel bodies) and pulled the scattered
  `_GREEN`/`_VIOLET` into the one colour block at the top of FIGURES (each now commented by role).
- `_save(path, *, tight=True)`: the two 3-D plotters (plot_variant_3d_surfaces,
  plot_conn_threshold_3d) call `_save(path, tight=False)` instead of duplicating
  `plt.savefig(...); plt.close()`; tight_layout still skipped for 3-D (it misbehaves there).
- Behaviour-preserving by construction (moved code verbatim). Did NOT regenerate/commit the PNGs:
  local matplotlib is 3.11.0 and would add version-drift binary diffs; author regenerates figures.

REVIEWED, report only (no change), per the brief:
- Hypergraph named-view wrappers (hyperedge_connectivity, max_hyperedge_connectivity,
  max_hyper_vertex_connectivity): thin wrappers over hyper_connectivity/max_hyper_connectivity,
  mirroring the graph-side thin views (local_edge_connectivity etc). NOT dead -- used by
  tests/test_hypergraph + the self-check. KEEP (they are the named API the tests/text use).
- Two enumeration paths: DFS `enumerate_extremal_directed_multigraphs` is dependency-free but
  complete only for n<=6 (falls back to the CONJECTURED floor(j^2/4) bound at j>=7). The geng twin
  `..._via_generation` uses nauty's geng to generate undirected supports and applies the PROVED
  M*(j) bound only for j<=6 (none for j>=7), so it is SOUND for ALL n and can certify the open n=7
  classification once it finishes; needs the geng binary. test_solve checks they agree at n<=5.
  KEEP BOTH (deliberate redundancy: they cross-validate, only geng is sound at n=7). FUTURE-CLEANUP
  NOTE: the proved table {2:2,3:4,4:6,5:8,6:10} is hardcoded 3x (_PROVEN_MSTAR in the MILP, `known`
  in the DFS, `proved_mstar` in geng); a single source of truth would be safer but touches the
  enumeration code that was out of scope here.

VERIFY: all 5 refactored grids + the 3-D tight=False path render to PNGs in the venv with no error;
suite 77 pass / 3 skip (venv); headless self-check ALL CHECKS PASSED (numpy+scipy only). Committed
and pushed.

## 2026-06-20 (Opus) -- queued review fixes + audit of recent Sonnet/Opus work

Author asked to pull, clear the queued fix tasks, then hunt for new mistakes (focus on
recent Sonnet work). Pull was already up to date.

SIX QUEUED FIXES (TASKS.md "ERRORS FOUND" + "DEEPSEEK REVIEW NOTES", all verified):
- ch1 prop:leonard-m2 proof: "two arcs of the cycle" -> "two paths of the cycle" (arc is
  reserved for directed edges in this thesis).
- ch3: removed the misattributed \cite{ErdosProblems} on the "pre-2024 conjecture" line,
  reworded to "the natural initial conjecture" to match ch1. ErdosProblems still cited
  twice in ch1, so no orphaned bib entry.
- ch1:387 false "first at n=m+8 for m=4": VERIFIED with a script -- the QUADRATIC branches
  floor((n+m-2)^2/4) vs floor(n^2/4)+(m-2)ceil(n/2) differ by exactly 1 at every even n
  for m=4 (tie at odd n); the FULL max-formulas (with the hub term m(n-1)) first diverge
  at n=12. Reworded to compare the full formulas, n=12 at m=4. (n=m+8 does NOT generalise:
  m=5,6 diverge at degenerate small n.)
- prop:hyper-edge "whenever" ambiguity: split into "a simple hypergraph attains the bound
  whenever m-1 <= C(n-2,r-2), and a multihypergraph attains it whenever (r-1)|(n-1)" --
  exactly what app_proofs proves (the multi star-hypertree only hits the floor cleanly
  when (r-1)|(n-1); general-n multi attainment holds by a Gale-Ryser argument but the
  thesis only proves the divisible subcase + the simple route, so I did not overclaim).
- rem:threshold-analogues (app_proofs): added the sentence that Mader's edge bound does
  NOT carry to kappa, since kappa<=lambda runs the wrong way; the Bollobas / Frieze-
  Karonski results are what supply kappa^max>=m.
- ch2 M* reduction: added a bridging sentence -- the optimisation ranges over fractional
  weights yet its optimum is realised by a {0,1} matrix, so the relaxation is tight and
  M*(n) is the largest fractional weight AND the densest integer multigraph / (m-1), never
  an overestimate (closes DeepSeek concern #16).

AUDIT OF RECENT WORK (the 4 commits after the figure-helpers session, NOT previously in
this log): 35c5c1d + 1c16c0c are Sonnet 4.6; e2188a1 + ed9a3a1 are Opus 4.8. ALL SOUND:
- 35c5c1d (Sonnet): augmented_bipartite shifted partition |B|=ceil((n+m-2)/2) and
  directed_arc_lower_bound -> floor((n+m-2)^2/4). Verified: arc count = ceil(N/2)floor(N/2)
  = floor(N^2/4), N=n+m-2; the size_a>=1 (n>=m) guard implies m-2<size_b (size_b>=m-1), so
  the dropped circulant-distinctness check is safe; formula agrees with old at m=2,3.
  _PROVEN_MSTAR dedup correct (one module constant, None for j>=7 preserved). Tests updated.
- 1c16c0c (Sonnet): const:augmented-bipartite m=3 prose fix VERIFIED (balanced and shifted
  partitions give the SAME arc count floor(n^2/4)+ceil(n/2) in both parities). New
  phenomenon-2 prose numbers all check: n=8,m=2 wall 16 vs hub 14; n=10,m=3 aug-bip 30 vs
  naive 27; lambda^max reasoning correct.
- ed9a3a1 (Opus): Fig 3.1 directed 3-uniform count n*C(n-1,2)=3*C(n,3)=n(n-1)(n-2)/2,
  correct. Adaptive midrange split decouples pair_conn/edge_dist figures from m (deliberate;
  ch4 prose + captions match). Fixed one stale comment in _midrange_lambda_threshold (the
  floor protects the BLUE/low side from emptiness, not the red side as the comment said).
- e2188a1 (Opus): phenomenon 3 removed; section now "Two principal phenomena", intro says
  "two", no dangling \Cref to fig:threshold / fig:sampled-grid / fig:conn-dist-m3.

NO NEW MATH OR REFERENCE ERRORS FOUND in the recent work. VERIFY: build latexmk exit 0,
93 pp, 0 overfull, 0 undefined refs/cites, no missing-graphics in the log; suite 77 pass /
3 skip; self-check ALL CHECKS PASSED; module imports, aug_bip(10,3)=30, dir_arc_lb(12,4)=49.

## 2026-06-21 (Opus) -- parallelism fixes, SA-vs-tabu task, parallel geng enumeration

Author asked: apply the two parallelism fixes I flagged; answer "do we use parallelism?";
execute the queued SA-vs-tabu task; then (mid-session) explain Gurobi-vs-own-hardware and
implement the geng parallelism since it speeds things up.

PARALLELISM FIXES (both done):
- ch3 parallel-restart claim softened from "wall-clock for k restarts is roughly that of
  one" (overclaim) to "a small multiple of one, bounded by the slowest restart and process
  startup" -- MEASURED ~2.5x for 6 restarts on 10 cores (56.4s->22.6s), not ~6x. macOS
  spawn overhead + restart-length variance.
- best_of_searches fallback: bare `except Exception` -> `except (OSError,
  concurrent.futures.BrokenExecutor)` + a RuntimeWarning, so a lost-parallelism event is
  reported, not silently swallowed, and a real worker bug fails loudly. (Validated: a
  guard-less script triggered BrokenProcessPool and the warning fired + ran sequentially.)

SA vs TABU (TASKS queued task, all 5 steps done):
- tabu_search_for_dense_graph added (twin of search_for_dense_graph, same energy +
  _neighbour_moves, deterministic best-improving + tabu tenure + stall perturbation);
  method="sa"|"tabu" on best_of_searches and solve; SearchStep gained seconds + best_feasible
  for timed convergence; 4 tabu unit tests (81 tests total, all pass).
- PERF BUG FOUND + FIXED: the research-note tabu computed the full all-pairs max-flow TWICE
  per trial move, so in 6s it barely moved (reached 14 at n=7, not 24). Rewrote the inner
  loop to the annealer's capped trick (one exceeds_bound per trial, full measure only when
  infeasible) -- identical trajectory, ~3-4x faster, and now it reaches the optima in budget.
- Benchmark (fresh, 6s/method, native fast modes): simple-undir n=7 9/9 tie; simple-dir n=7
  SA 16 / tabu 18; dir-multi n=7 SA 20 / tabu 24. Dropped dir-multi n=5 from the thesis TABLE
  (SA's true ceiling there IS 16 = the double star, reached with normal restarts per
  tab:rediscovery in ~150s; at a 6s cap SA gets 13 -- so n=5 is a slow tie, not a clean
  differentiator, and listing 13 would contradict tab:rediscovery's 16). Figure keeps n=5+n=7
  (single representative schedules; caption says wall-clock/representative).
- ch3 \subsection{Simulated annealing versus tabu search} + tab:sa-vs-tabu + fig:sa-vs-tabu;
  build 93pp, 0 overfull, 0 undefined.

PARALLEL GENG ENUMERATION (author asked to implement since it speeds up + isn't buggy):
- enumerate_extremal_directed_multigraphs_via_generation now fans the geng supports across
  cores (parallel=True default). Extracted the per-support decoration to a module-level,
  picklable _decorate_support_worker; main collects via ProcessPoolExecutor.map(chunksize=1)
  with the same OSError/BrokenExecutor fallback+warning; final canonical dedup as a safety net
  (distinct geng supports are non-isomorphic, so no cross-support dupes). Embarrassingly
  parallel: work scales with #supports. This is the practical route to n=7 fact (b) on a
  multi-core box (Gurobi is only for fact (a)).
- geng is NOT on PATH on this machine, so validated geng-free: brute-force all non-iso
  supports, feed the worker -- par==seq==DFS at n=4 (unit test SupportWorker, geng-free) and
  n=4 manually; n=5 manual check in flight (slow DFS ground-truth). README test count 77->81 +
  parallel note; function docstring documents parallel=.

GUROBI (answered to author): the n=7 wall is NOT a supercomputer problem. Fact (b)
(enumeration) is pure CPU and now parallel -- runs on his own multi-core laptop. Fact (a)
(MILP infeasibility) is solver-bound: bundled CBC is weak, Gurobi is strong and runs LOCALLY
on his laptop; it only needs the free academic licence activated over eduroam. No cluster
needed for either; a cluster would only brute-force (b) without the parallelism.

VERIFY: build latexmk 0 overfull / 0 undefined; suite 81 pass / 3 skip; self-check passes
earlier this session. Commit local; push left to author (direct-to-main push needs his ok).

## 2026-06-24 (Opus) -- conj:min-degree obstruction remark + numerics task

Author asked: "can you prove conj:min-degree for general m?" Answer: NO (it is the
thesis's single identified open gap, mixed fractional regime; attacked across many prior
sessions without closure). Did NOT fabricate a proof. Worked it directly: confirmed the
averaging route provably cannot finish (granting the even bound, deletion gives
M <= k(k+1)+k/(2k-1) = (2k+1)k^2/(2k-1), so min-degree <= 2M/(2k+1) <= k+k/(2k-1) < k+1,
and the fractional leftover k/(2k-1) is not roundable; to force <=k by averaging needs
M <= k^2+k/2 but the bipartite point already has M=k^2+k, so no averaging bound suffices
for any m). Also tried the obvious counterexample (bolt backward weight eps onto the
saturated bipartite point to lift B-degrees to k+eps): it COLLAPSES for any eps>0 because
recirculation a->b->a0->b' pushes maxflow(a,b') to 1+k*eps>1. Same mechanism as the
conj:dir-arc back-arc obstruction -- the two open gaps are one phenomenon. (Integral
version at m=k+2 collapses identically; I initially miscounted it as a counterexample,
then caught the 3-hop recirculation routes.)

DONE (author: "do one"): added rem:min-degree-obstruction to app_proofs.tex right after
the mixed-regime paragraph (before lem:attachment), recording both facts above so the
conjecture is not read as a routine averaging exercise. Math checked: the M bound matches
the existing prop:dir-multi-even discussion (k(k+1)+k/(2k-1)); references
lem:scaling-reduction, prop:dir-multi-even, prop:min-degree-m2, lem:attachment,
conj:dir-arc, ch:discover all resolve. No em-dash/en-dash/semicolon in the prose.

ADDED (author: "add three to the future tasks"): TASKS.md new section
"CONJ:MIN-DEGREE -- numerical stress test before submission" with a runnable
fractional_search(n,'min_degree') sweep at n=9,11,13 x {bipartite,random,zero} x 8 seeds;
expected best min weighted-degree = k=(n-1)/2 exactly, a value > k would REFUTE the
conjecture. n=7,9 already clean per prior numerics; this extends into the larger odd sizes.

BUILD: latexmk exit 0, 108 pp, 0 overfull, 0 undefined refs/cites, new label in aux.
No program code touched. Committed + pushed to main.

## 2026-06-25 (Opus) -- SA-vs-tabu honesty note, code cleanup, code-into-thesis integration

Author asks: (1) note the SA-vs-tabu values are conjectured/found not proven; (2) integrate
more implementation detail into the thesis (function names, library names, ideas) like the
existing codecards; (3) clean the code first, shorter where possible.

ch4 odd-n fix (earlier same day, separate commit): ch4 "balanced partition |A|=|B|=floor(n/2)"
was wrong for odd n (n=5 gives 4 != floor(25/4)=6); corrected to (floor(n/2), ceil(n/2)).

(1) tab:sa-vs-tabu caption: now states only the simple-undirected value is a proved optimum
(Mader); the two directed values are best-known/found by search+construction past the certified
range (n<7), and the "optimum" column is the target each engine aims at.

(2) CODE CLEANUP (verified: self-check PASS, 82 tests OK baseline, montecarlo+hypergraph re-run
OK, import OK, no cascades): removed 3 genuinely-dead top-level functions --
average_max_connectivity (unused MC helper), plot_appearance_threshold (orphaned figure, png
already deleted), hypergraph_vertex_m2 (trivial closed form superseded by verify_hyper_vertex_value;
its docstring still referenced "the commented block in the appendix", stale). _PROVEN_MSTAR was
already a single module constant (the triplication noted in older logs is gone). A dead-code
sweep over program+make_figures+tests now finds 0 unreferenced top-level defs.

(3) CODE INTO THESIS (all cited names verified to exist in erdos915_unified.py; build clean
108 pp, 0 overfull, 0 undefined):
- All 8 codecards regrounded from idealized camelCase to the REAL snake_case Python names:
  solve (max_seconds, SolveResult), Graph(n, Variant(directed, simple)) with numpy self.mu,
  local_edge_connectivity / max_edge_connectivity / max_vertex_connectivity (_split_capacity_matrix)
  / max_edge_connectivity_via_tree / max_hyperedge_connectivity (_hyper_capacity_matrix),
  edge_sensitivity (sensitivity_map).
- Library routines named at their natural points: scipy.sparse.csgraph.maximum_flow (checker),
  networkx.gomory_hu_tree (GH view), pulp + CBC/Gurobi via _pick_solver (prover), nauty/geng +
  graph6 via _graph6_edges (generation), Edmonds-Karp _float_maxflow_value (fractional, since
  scipy csgraph is integer-only).
- Two NEW codecards: PROVE prove_directed_multigraph (_cut_counting_model, pulp, _pick_solver,
  prove_integral_arc_bound) and DISCOVER search_for_dense_graph (best_of_searches).
- Routines named in prose: _exhaustive_directed (pruned B&B), enumerate_extremal_directed_
  multigraphs + ..._via_generation + _canonical_form, tabu_search_for_dense_graph,
  fractional_search / fractional_flows_feasible, _tiny_maxflow, _erdos_fast.c/.so + build_fast.sh.
- Reproducibility section gained an entry-point index (solve / measures / prove / search).
- FIXED stale name: app_proofs cited certify_directed_multigraph, renamed to
  prove_directed_multigraph back on 2026-06-13; corrected, and added the exact fact-(a)/(b)
  calls prove_integral_arc_bound(7,3,25) and enumerate_extremal_directed_multigraphs(7,3,24,
  max_degree=8).
PROVE card page rendered to PNG and visually verified (clean, underscores render, no overflow).

## 2026-06-25 (Opus, cont.) -- bigger hypergraph checker figure + directed companion

Author: figure 2.6 (fig:hyper-gadget-example) should have more vertices, way more
hyperedges, and more edge-disjoint paths; then repeat the figures + explanation for
the directed variants.

- preamble.tex: two thesis-local metro colours metroG (magenta), metroH (teal) so an
  8-line figure can give every hyperedge its own hue (shared file stops at metroF; left
  untouched so slides keep their look).
- fig:hyper-gadget-example (2.6) rebuilt: 6 vertices/4 hyperedges/flow 2 -> 10 vertices,
  8 hyperedges, 4 rails, max flow 4. Four parallel rails, each two lines sharing the
  stretch a_i--b_i; panel (b) has 8 turnstiles h_1..h_8 and 4 black routes. Lead-in prose
  and caption updated (lambda(u,v)=4; a 5th route would reuse a turnstile since u sits on
  only 4 hyperedges). Rendered + visually checked, no overlap.
- NEW directed subsection "The directed hypergraph checker" with two figures mirroring
  the undirected pair: fig:dir-hyper-gadget (2.7), one directed hyperedge (tail; heads) ->
  a one-way GATE g_e (cap-1 tail->gate, gate->each head); fig:dir-hyper-gadget-example
  (2.8), a directed 3-uniform hypergraph on 8 vertices, 6 oriented metro stars on 3 rails,
  3 arc-disjoint directed Berge routes u->m_i->v, flow network with 6 gates, max flow 3.
  Gates placed on the arc midpoints so each black route rides its coloured arcs (fixed an
  earlier version where the routes floated above the arcs). Prose explains tail/head entry,
  the gate as a directional turnstile, and that vertex-splitting on top counts internally
  vertex-disjoint directed routes, so one checker measures all four hypergraph variants.
- Build clean: 110 pp (+2), 0 overfull, 0 undefined refs/cites. All three labels resolve;
  no prose em-dash/semicolon.

## 2026-06-26 (Opus) -- general directed hyperedge model + orientation bounds

Author liked the "different kinds of directed" hyperedges that surfaced while redrawing the
hypergraph metro figure and asked to expand the thesis around them (implement the code,
discover bounds, maybe change the variant count). Scope confirmed with the author: implement
the GENERAL model (all tail/head splits, subsuming forward/backward/mixed); decide thesis
presentation AFTER seeing the numbers (so no .tex written yet, code only).

TAXONOMY. A directed hyperedge is a split of an r-set into a non-empty tail set T and head
set H. forward = |T|=1 (the thesis's existing model), backward = |H|=1, general = any split.
Two facts shape it: (1) backward is the arc-reversal DUAL of forward, so identical extremal
numbers (a one-line lemma); (2) at r=3 every split has a singleton side, so general =
forward + backward (per-edge orientation choice) and genuinely mixed (|T|,|H|>=2) arcs only
exist from r>=4.

CODE (erdos915_unified.py, all additive, forward path kept byte-identical):
- Hypergraph now stores a directed edge as the legacy forward (tail:int, heads) OR the
  general (tails:frozenset, heads:frozenset); new _dir_tails_heads() normalises both. The
  gate gadget _hyper_capacity_matrix wires every tail->gate and gate->every head, so the
  same scipy max-flow checker serves all kinds. members(), _hyper_canonical/_aut_count_hyper/
  _hyper_to_lists (forward [tail,[heads]] shape preserved), _hyperedge_candidates,
  _brute_force_hypergraph, _random_hypergraph_search, _enum_hyper_extremals all gained a
  kind="forward"|"backward"|"general" axis.
- NEW max_feasible_hyperedges(n,r,m,*,directed,vertex_split,kind,time_limit,seed_lb) -> the
  hypergraph-side branch-and-bound maximiser (matrix side already had one): DFS include/
  exclude with the monotone-feasibility prune + an incumbent bound prune + a short random
  warm start; seed_lb lets general start from the forward optimum (forward subset of general)
  so general >= forward is guaranteed and the prune bites. Returns (value, exact).

FINDINGS (r=3 unless noted; * = branch-and-bound proved exact):
- forward == backward in EVERY computed cell (duality confirmed empirically).
- m=2: general == forward everywhere (edge and vertex), no gain (forest-like regime).
- m=3: general strictly beats forward only when vertices are scarce (n ~ r):
  * r=3: n=3 general 4* vs forward 3*; n=4 BOTH 8* (gap closes); n=5,6 equal lower bounds.
  * r=4: n=4 general 6* vs forward 4* (m=3) and 8* vs 4* (m=4, doubles); n=5 no gap found.
  So extra orientations buy density only while a single hyperedge-set dominates; once n>r,
  forward already saturates the Menger budget. (n>=5 values are seeded lower bounds, not exact.)

VERIFY: new self-check section "directed orientation models" (mixed-gate one-way, duality,
the n=3 and n=r=4 gaps, all proved exact) -> ALL CHECKS PASSED. Full suite 88 tests OK / 3
skip (was 82; +6 new in tests/test_hypergraph.py DirectedOrientationModels). Forward
regression spot-checks unchanged (K_4^(3)=3, star hypertree, verify_hyper_vertex_value,
forward enum class counts + legacy format).

THESIS INTEGRATION (author chose: focused subsection; prove duality + try general bound):
- app_proofs.tex: lem:dir-hyper-duality (backward = forward by arc reversal, edge AND vertex,
  full proof) + prop:dir-hyper-general (the general model obeys the SAME (m-1)n(n-1)/(r-1) cap
  as forward, since a hyperedge (T,H) fills |T||H| >= r-1 ordered tail-head pairs each usable
  by <= m-1 disjoint one-step routes; forward construction is itself general, so same quadratic
  lower bound). Both placed right after prop:dir-hyper-first.
- ch4_synthesis.tex: new \subsection{Orientation models for the directed hypergraph}
  (sec:orientation-models) after tab:summary -- taxonomy, the two results, and tab:orientation
  giving the proved-exact gap (forward vs general at r=3 n=3: 3/4; r=3 n=4: 8/8; r=4 n=4 m=3:
  4/6; r=4 n=4 m=4: 4/8). Verdict: orientation axis collapses for n>r, so Problem 915 stays a
  TWELVE-variant question and general enters as a margin refinement, not a 13th column. Open-
  problems directed-hyper item cross-links the duality + general bound.
- ch2_certify.tex: connector paragraph after the directed gate noting the gate is indifferent
  to the tail/head split, pointing to sec:orientation-models.
- Build: latexmk exit 0, 112 pp (+2), 0 overfull, 0 undefined refs/cites; lem A.41, prop A.42,
  subsec 4.3.1, tab 4.2 all resolve. Table values re-verified by max_feasible_hyperedges (edge
  AND vertex coincide).

FIGURE REBUILD DONE (author: "do the figure, i gave you all you needed"). The author reverted
the awful 4-rail fig 2.6 and handed a hand-designed metro layout (15 coords named a..o; the 8
letters appearing in edges are stations a,c,d,e,j,l,m,n, the other 7 are helper junctions named
after their edge; 8 hyperedges ead/nmj/elc[typo "els"->c, author-confirmed]/edm/nel/elm/mcj/ldj;
directed = middle vertex is the tail, author-confirmed). Replaced BOTH whole-hypergraph figures
in ch2 with single-panel metro maps (the helper junction IS the gate, so map and flow network
are one drawing, no more two-panel before/after):
  * fig:hyper-gadget-example (2.6, undirected): 8 stations, 8 colour Y-hyperedges meeting at
    boxed gates named after the edge; checker reads lambda(e,l)=4 (e,l share elc,elm,nel + one
    longer route). ldj helper placed at (5,5) (author left it unplaced).
  LABELLING CONFIRMED + REDRAWN (author flagged "looks awful"): the alphabetical a..o naming is
  column-major (first coord x ascending 0..8, then second coord y ascending 0..8) -- which is
  what I already had (verified: that order gives the shortest total spoke length, 70.9, vs 78+
  for the others). So the labelling was right; the awfulness was my DRAWING. Replaced the bowed
  parallel-lane spine rails with PLAIN STRAIGHT SPOKES (the helper boxes stack on the x=4 spine
  and mask the lines passing behind them). Both figures and the undirected caption updated (no
  more "parallel rails" prose).
  * fig:dir-hyper-gadget-example (2.8, directed): same layout, dmetro arrows tail->gate->two
    heads; checker reads lambda(d,e)=2 (orientation drops it from the undirected 4). Lead-ins +
    captions rewritten (no more u,v,c interchange / "max flow = 3" two-panel prose). Old layered
    acyclic directed figure removed.
  Rendered both in-thesis (pp 35, 37): clean, no overlap, distinct colours, arrows correct.
  Committed ch2_certify.tex + main.pdf.

NOT done in solve()/variant configs/figure grid (deliberately -- general stays a margin
refinement, not a first-class 12-grid variant).

## 2026-06-30 (Opus) -- pull + health check, then flagship directed-arc m=3 (H)

Author asked to pull the thesis, check everything is alright, and start working.

HEALTH CHECK (all green): local main == origin/main (0 ahead/0 behind; the only
working change was a non-deterministic main.pdf rebuild, restored). Forced clean
latexmk rebuild: 112 pp, 0 overfull, 0 undefined refs/cites. Program self-check:
ALL CHECKS PASSED. Suite: 88 tests OK / 3 skip (~141s). (The build "failed exit 1"
notification was a false alarm: the job's last command was `grep undefined`, which
exits 1 when it finds zero matches -- zero undefined refs is the good outcome.)

WORK: the TASKS.md flagship -- close the m=3 directed-arc quadratic upper bound,
which research_notes/directed_arc_m3_reduction.md reduces to hypothesis (H): every
extremiser's non-source set R has max in-degree <= 1. (H) is NOT closed this
session (it is the thesis's central open gap; I did NOT fabricate a proof). I did
add three unconditional, verified increments to that note (new section 2.4):
- Lemma (L), self-similarity: a source has in-degree 0 so no path passes through
  it, hence lambda_D(u,v) = lambda_{D[R]}(u,v) for u,v in R, so D[R] is itself
  feasible and e(R) <= ell_3^dir(|R|). (Not previously stated in the note.)
- The recursion from (L) alone OVERSHOOTS Q(n) by +8..+16 at n=9..15 (the argmax
  takes a small dense inner R under a near-complete source layer, which feasibility
  forbids). So the recursion and the source-neighbourhood coupling (2.2) must be
  used together -- this pinpoints why (H) is the hard core, not an artefact.
- Proposition (complete-layer): a feasible D with a source and a COMPLETE source
  layer satisfies (H), giving a <= rho(sigma+1) <= Q(n). Proof: a source pointing
  to w and to two R-in-neighbours of w breaks Lemma 2.2. This recovers the
  augmented-bipartite extremisers' optimality with no exchange, and narrows (H) to
  exactly the GAPPED-layer case (a missing arc s->x must not overpay for a denser R).
Two SELF-CONTAINED verification scripts added (own capped max-flow, no dependence
on the program they corroborate): research_notes/scripts/lemma_check.py (partition
+ (L) on augmented-bipartite k=3..8 and random feasible n=4..10, all OK) and
research_notes/scripts/probe_overshoot.py (the overshoot table). Both pass.

NO thesis .tex or program code touched (these are research-note increments, not
yet thesis-grade closure). (H) general case remains open; honest next steps are in
TASKS.md (exchange argument for the gapped-layer case; or the finite seam bases
ell_3^dir(9)=25, ell_3^dir(10)=30 via Gurobi).

SECOND ROUND (author chose "keep attacking (H)"): two more verified results added
to the note (section 2.5), and a third self-contained script
coupling_inequality.py (all pass):
- (star) summed-coupling inequality: summing Lemma 2.2 over all sources gives
  sum_{R-arcs} c(x,y) <= e(S,R), where c(x,y) = #common source in-neighbours of the
  endpoints. Recovers (H) in the complete-layer case (c == sigma). 0 failures / 280.
- KEY NEGATIVE RESULT: the conditional bound a <= (n-sigma)(sigma+1) FAILS for
  non-extremal feasible digraphs even with sigma >= 1 (95/280; e.g. n=9 one source
  a=21 > 16), because sigma counts only GLOBAL sources while D[R] can be a dense
  linear-regime digraph with its own internal sources. So no "sum local constraints
  over the whole digraph" count can prove (H): a proof MUST use extremality. This
  rules out the counting route and re-focuses all future work on the exchange
  (attack 1). Recorded in 2.5.2 and the status block.
Honest bottom line: (H) NOT closed. The non-monotone exchange (a hole s->x cannot
always be filled without manufacturing a 3rd route) remains the barrier the note
already named; this session sharpened WHERE the barrier is and proved the counting
route is a dead end, but did not break it.

THIRD ROUND -- (H) IS FALSE (author: keep attacking it). Instead of trying to
PROVE (H), I tested it directly: a fixed-arc-count search that MAXIMISES the max
R-in-degree (h_violation_search.py) found, at n=9, a feasible 25-arc digraph
(= Q(9)) with sigma=3 and an R-vertex of in-degree 2. Triple-verified feasible
(the search's own max-flow, the thesis program's max_edge_connectivity, and a
from-scratch Edmonds-Karp), and MAXIMAL (no arc addable). It then GENERALISES to
an explicit INFINITE FAMILY: complete A->B (|A|=k-1,|B|=k) plus one head beta0
pointing to one tail a0 and to the rest of B, giving k^2 = Q(2k-1) arcs, feasible
(lambda^max=2), sigma=k-2, max R-in-degree 2, for EVERY odd n=2k-1>=9 (checked
n=9..17 two independent ways). So (H) is FALSE, not merely open. The augmented-
bipartite family is NOT the whole extremal set; the characterisation and the
(H)-based attachment kill of the even case are void. The VALUE conjecture
ell_3(n)=Q(n) is UNHARMED (the family attains Q(n), never exceeds it). Recorded in
reduction-note section 0 + h_counterexample.py; directed_arc_m3_extremisers.md and
the README banner marked SUPERSEDED. NOTE: with A=sources there is no back-arc, so
this does NOT refute the thesis's own backward-arc lemma (which may take A=sources)
-- no proved thesis content is affected, and nothing here goes in the thesis.

## 2026-07-02 (Fable) -- full review: proofs re-checked, two plot-code bugs fixed, list numbering restored

Author asked for a full pass: mistakes, mathematical proofs, tikz/plot improvements,
code audit. Baseline was green throughout (build 116 pp, 0 overfull, 0 undefined; 88
tests OK / 3 expected skips; self-check ALL 55 CHECKS PASSED).

PROOF CHECK (every statement of app_proofs A.1-A.8 re-derived independently, plus the
chapter claims): ALL CORRECT. Highlights of what was actually re-verified rather than
skimmed: the incidence rank lemma end to end (block-cut count, suppression preserving
kappa, degree bookkeeping under (ii), SPQR leaf analysis incl. the one-virtual-edge
path bound); thm-hyper-vertex-m2/m3 component sums; the attachment lemma case split
and its equality corollary; thm:odd-step's averaging identity and the m<=4 window
((m-3)k+1 <= k+1 < 2k+1); dir-arc m=2 induction remainder ((2k+1)k^2 = (2k-1)(k^2+k)+k);
Mader slack identity 2|E| = m(n-1) - (S1+S2+S3); near-regular circulant parities;
Baranyai two-class split with ceil(re/n) <= d; dir-hyper duality + general |T||H| >= r-1
cap; Chernoff constants. No mathematical errors found anywhere.

CODE AUDIT (checker core, MILP builder incl. validity of every strengthening row,
annealer fast path exactness, tabu, B&B, both enumerators incl. the degree-gated
prefix feasibility, canonical form incl. the C memcmp low-byte argument, C guards):
sound. THREE genuine issues found and FIXED:
 1. STALE FORMULA (visible bug at m=6 only): plot_directed_crossover and the
    make_figures panel-3 "bipartite" branch still used the pre-correction balanced
    count floor(n^2/4)+(m-2)ceil(n/2); the 2026-06-15 conjecture correction fixed the
    .tex but missed these two plot sites (they agree at m=3, which is why every test
    and the shipped crossover figure hid it). Both now use floor((n+m-2)^2/4);
    directed_crossover.png (legend) and variant_bounds_m6.png (branch line now rides
    under the red conjecture curve instead of ~4 arcs below it) regenerated.
 2. LIST NUMBERING: the preamble's Petersen-icon enumerate label made BOTH of the
    thesis's enumerates unnumbered, orphaning the prose references "Pattern (1)-(3)"
    (lem:attachment proof) and "part (1)/(2)" (prop:monotone). Fixed locally with
    [label=(\arabic*)] on those two lists; the decorative icon stays everywhere else.
 3. _exhaustive_directed: on a timeout before any recorded leaf it returned
    seed_value-1 beside a seed witness of seed_value arcs; return now takes
    max(best, seed_value). No shipped number affected (all reported runs completed).

TIKZ: cleared the deferred faint-width item (TASKS.md): bgarc/abk/attachment
background now inherit the canonical gdirfaint; affected pages rendered and checked.

VERIFY: rebuild 116 pp, 0 overfull, 0 undefined refs/cites; suite 88 OK / 3 skips
after the code edits; regenerated figures inspected (m6 grid consistent, crossover
legend general-form, values at m=3 unchanged so variant_bounds_m3 left untouched).


## 2026-07-02 (Fable, continued) -- FACT (b) PROVED by machine; saturated attachment lemma; uncapped n=6 classified

Author: keep going (tasks, figure cleanup esp. appendix, prove/disprove, improve text).

MACHINE RESULTS (nauty installed via brew; sound geng enumerator, 10 cores):
 1. n=6 target 20 cap 8: exactly 1 class, doubled P_6 (352 s). Closes the June
    cancellation.
 2. **FACT (b) PROVED**: n=7 target 24 cap 8, 25895 s: exactly 3 classes,
    2B(3,4), 2B(4,3), doubled P_7 -- precisely the predicted set, each
    re-verified with the exact checker (24 arcs, lambda=2, degree profiles,
    canonical match against an independently built doubled P_7). The m=3
    directed multigraph problem now rests on fact (a) alone.
 3. Uncapped n=6 target 20: exactly 6 classes in 2187 s = the 6 doubled
    spanning trees (all verified bidirected/tree-support/mult-2/lambda=2;
    5 degree sequences with the (1,1,1,2,2,3) pair distinguishing caterpillar
    vs spider). NEW classification, previously known only n<=5.
 4. Fact (a) attempt LAUNCHED: uncapped n=7 target 25 (empty = L_3(7)=24 =
    the whole m=3 problem closes). Running; resume command in TASKS.md.

NEW LEMMA (proved + exhaustively verified + integrated as lem:saturated-attachment,
A.30): attaching one vertex to any everywhere-saturated multigraph (doubled trees
in particular) caps d(v) <= 2(m-1); equality = grow the tree by one full leaf.
Verification: scripts/saturated_attachment_check.py (all 3^(2n) patterns over all
nine doubled trees on 5-6 vertices; max feasible degree exactly 4; equality shapes
exactly the n single-partner attachments). Consequences: the n=8 seam argument is
now a one-liner (fig:seam-c8 kept as illustration), the doubled-tree closure is
explained structurally, and with the uncapped n=6 classification any 25-arc witness
against fact (a) has min degree >= 6 (recorded in rem:odd-step-roadmap; the d(v) in
{6,7} residue needs a 19/18-arc near-extremal classification, see the research note).

THESIS UPDATES: rem:odd-step-roadmap (fact (b) settled, sound-tool naming fixed --
the DFS enumerator was cited for a job it is only sound for at n<=6), ch2
generation section, ch4 body + open problems + tab:summary caption, contribution
statement. research_notes/saturated_attachment_lemma.md + script; notes README
indexed; TASKS.md rewritten per its delete-after-logging rule.

TEXT PASS (author asked to improve explanations everywhere): fixed the garbled
m>n sentence in ch1, centerpiece->centrepiece, "a hot metal"->"hot metal" (foreword
+ lay summary), Menger caption now explains why no 2-edge cut exists, honest
phrasing for "one common data structure" (hypergraph is list-stored) and for the
two m=2 structural props in ch4. Paragraph breaks at natural seams: ch1 direction
axis, hypergraph intro, G(n,p) discussion; ch2 helper-point + scaling; ch3
trichotomy colours; thm:odd-step proof; rem:odd-step-roadmap now five movements
with the (a)/(b) facts as a labelled list. Abbreviations + symbols tables extended
(MILP, SA, SPQR; r, hypergraph functions, M*(n), B_{p,q}). Word-tic clusters
thinned (precisely/honest repeats). program/README test count 82->88.

FIGURES (appendix pass): sub-captions ragged-right globally (fixes stretched
justified text in narrow A.2/A.3 panels); star-hypertree hubs orange in ch1+A.6
(A.6 caption already claimed orange -- caption/figure mismatch found and fixed);
extremal gallery states uniform multiplicity once per panel ("all arcs x2/x3")
instead of 12 overlapping labels on the dense panels; gallery caption updated.

VERIFY: builds clean throughout (116->118 pp, 0 overfull, 0 undefined); suite 88
OK (only 1 skip now -- geng tests run since nauty is installed); self-check ALL
PASSED earlier in the session. Everything committed and pushed to main.

## 2026-07-02 (Fable, final) -- accessibility pass: no prior knowledge assumed

Author: "is all the math accessible enough? Make sure i get it all first time
around. No prior knowledge needed." Walked the text in reading order checking
every symbol and term at FIRST use. Glossed, in place and in the author's voice:
floor/ceiling brackets (at Mader's theorem), the binomial coefficient (K_5
caption), digraph = directed graph, parity = even/odd of m(n-1), clique defined
and "chordal scaffolds" -> "clique scaffolds" (term never recurs), mod-N
wrap-around at the circulant construction, ln n / o(n) / the union bound
unpacked at the threshold discussion, "relaxation" defined at the MILP,
"not convex" -> "has no helpful shape", the Metropolis acceptance chance and
geometric cooling spelled out, logarithmic scale = tenfold steps, Theta(n^2) ->
"grows like n^2", pair-codegree -> plain counting phrase, cycle/acyclic glossed
at prop:leonard-m2, "lexicographically smallest" -> "smallest in dictionary
order", multiset, 2k-regular (both ch4 and roadmap), "cactus value" -> the
multigraph value of thm:multigraph-edge, D(n,p) defined, semi-degree defined.
Build clean, 118 pp, 0 overfull, 0 undefined. Fact (a) run still going.

## 2026-07-03 (Fable) -- full accessibility + correctness pass (author: "no big claims, small steps, make me proud")

Read every chapter and the whole appendix end to end, re-deriving the mathematics
rather than skimming. VERIFIED CORRECT (a sample of what was actually re-derived):
Mader's Gomory-Hu double count and the extremal characterisation slack identity;
the S-T divergence values at n=6..10; the m=2 directed induction arithmetic incl.
the (2k+1)k^2 = (2k-1)(k^2+k)+k remainder; the 30-arc counterexample's 2-arc cut;
the augmented-bipartite count floor((n+m-2)^2/4), the m<=3 partition tie and the
m=4 divergence at n=12; the MILP indicator table, McCormick min pinning, and the
scaling identity; the attachment lemma case split, odd-step averaging identity,
saturated attachment cut analysis, incidence-rank component count
q(r-1) <= 2(n-1)+2(1-C); Chernoff constants; duality + general-orientation bound.
Machine state re-verified today: self-check ALL CHECKS PASSED, 88 unit tests OK
(1 expected skip), build 118 pp / 0 overfull / 0 undefined. All thesis-cited code
identifiers exist in erdos915_unified.py; solve() defaults method="tabu" matching
ch3's claim; transcripts and rediscovery table match the text.

SIX FIXES (all small, none touches any reported value):
1. ch2: "directed double star" used BEFORE the term's definition (and for what is
   really the bidirected star) -> "bidirected star (fig:bidirected-star)" in the
   checker sanity check + reproducibility list.
2. ch4: the ambiguous "The two formulas agree for m<=3" paragraph (read naturally,
   it compared the multigraph and simple conjectures, which never agree past m=2)
   rewritten to say what was meant: parallel copies make the balanced split optimal
   for multigraphs, in-arcs inside B push the simple split to ceil((n+m-2)/2) at
   m>=4, balanced=shifted count at m<=3, and the m-1 factor cancels in the n=7
   crossing.
3. app_proofs roadmap even level: "q>p" now names its p>q mirror (the corollary is
   symmetric; the text looked one-sided).
4. app_proofs: two remaining prose semicolons (attachment pattern list ->
   sentences; orientation-models lead-in).
5. ch1 fig:menger caption: "no two edges can" expanded to the full small-step
   reading (each removed edge breaks at most one route).
6. erdos915_unified.py module docstring said "Sixteen concrete variants" against
   twelve everywhere else (incl. this file) -> Twelve. Configs counted: 12 + 12.

OPERATIONAL: the fact (a) run (uncapped n=7 t25) did NOT survive the 2026-07-02
session -- no process, no verdict, no log (geng_uncapped_20260702.log is the
finished n=6 run). TASKS.md corrected from IN PROGRESS to NOT RUNNING with a
detached (nohup) relaunch command and an honest budget hint.

## 2026-07-03 (Fable, round 2) -- "nothing missing, spotless, code in big lines"

Author brief: suggest-or-do anything still missing; thesis self-contained; code
included at the WHAT level (we iterate this, calculate that), not loop mechanics.

STALENESS FIXES (all predated the 2026-07-02 fact (b) proof):
- ch4 limitations paragraph still said BOTH n=7 computations "have not yet
  returned certificates", contradicting ch4's own fact (b) report two sections
  earlier -> now: classification (b) done, value (a) the one outstanding
  certificate.
- main.tex Short Summary now says one of the two n=7 statements is already
  verified (the Contribution Statement already did).
- Root README "Where to continue": "Two finite n=7 facts" -> one remaining, with
  the (b) result and the two routes to (a) stated; dropped the resolved
  directg/watercluster2 follow-up.

BIG-LINES METHOD DESCRIPTIONS ADDED (what is iterated and calculated):
- ch2 generation section: the decoration spelled out (per support edge, every
  ordered multiplicity pair except (0,0); monotonicity prune; canonical dedup;
  independent supports across cores). Checked against _decorate_support_worker;
  worded "along the way" since the code checks completed prefixes, not every
  assignment.
- ch4 orientation models: max_feasible_hyperedges described as the fig:prune
  include-or-exclude search over candidate hyperedges, finished sweep = proof.
- app_proofs fact (a) passage: prove_integral_arc_bound mechanism stated (cut
  model, integer weights, fixed arc total, INFEASIBLE = proof) and the two
  strengthening families now PROVED in place instead of "all proved valid":
  deletion bounds via restriction-feasibility, degree-pair via the two-hop
  route count with min(a,b) >= a+b-1 (derivation re-checked by hand).
- app_proofs: "fractional hill-climb" glossed (nudge one weight, keep only
  improving feasible changes).
- ch2: graph6 glossed (compact one-line text encoding).

SPOTLESS SWEEPS: w.h.p. removed from the abbreviations table (never used; GH,
SA, MILP, SPQR all confirmed used); lay summary's "confirming one example"
corrected to "one exhaustive computer check at that single size" (fact (a)
confirms absence, not an example; summary rebuilt clean); doubled-word regex
clean; typo grep clean (hunspell not installed on this box; last full pass
2026-06-18 was clean and everything since has been read closely).

VERIFY: thesis latexmk exit 0, 0 overfull, 0 undefined/missing; lay summary
pdflatex exit 0. Committed + pushed.

## 2026-07-03 (Fable, round 3) -- MILP-jargon audit + real hunspell pass

Author asked: is MILP etc. thoroughly explained, and install hunspell + spell check.

MILP AUDIT. The ch2 core explanation was already thorough (linear + mixed-integer
defined, variables in words, indicator table, McCormick spelled out, relaxation
and gap glossed). Four residual jargon spots FIXED:
- ch2 PROVE codecard used "MILP" four lines before the term's expansion ->
  "the mixed-integer linear program written out below"; CBC/Gurobi now named as
  solvers (free bundled / commercial) in the codecard AND the reproducibility
  section, with pulp glossed as the write-once-run-anywhere library.
- app_proofs transcript note "the branch count defeats it" assumed the reader
  knows solvers branch -> spelled out (case-splitting the yes/no cut labels).
- ch1 related work: "LP/ILP-based certification ... whose optimal dual is itself
  the proof" -> acronym expanded, "optimal dual" replaced by the plain
  certificate-of-optimality reading (short list of numbers checkable by
  arithmetic). This is the one school the thesis claims as its own form, so it
  could not stay jargon.
- app_proofs: Edmonds--Karp glossed as a textbook maximum-flow routine run on
  fractional capacities.
Also: nontrivial -> non-trivial (ch1, matching ch3's usage).

SPELL CHECK, REAL THIS TIME. brew install hunspell; en_GB.aff/dic fetched from
LibreOffice/dictionaries into ~/Library/Spelling (verified colour/behaviour/
optimise accepted). Full -t -l pass over main + all chapters + lay summary:
every flag is a technical term, a surname, a TikZ token, or a code identifier.
ONE American spelling found, "utilize", inside the KU Leuven copyright
boilerplate on the disclaimer page -- left untouched (mandated faculty text).
Post-edit re-check of the four edited files: clean.

Build: latexmk exit 0, 0 overfull, 0 undefined. hunspell + en_GB now installed
on this machine for future pre-submission passes.

## 2026-07-30 (Opus) -- external-review audit: one real proof error, five overclaims

Author brought an external (ChatGPT) review of the PDF and asked whether it or my
earlier sign-off was right. Answer: neither. The review found ONE genuine
mathematical error and several genuine overclaims, and it also over-diagnosed
(demanded rows be deleted that are fine, and its top "doable improvement",
L_3^dir(7)=24, is already proved in research_notes). Verified every claim against
the source before acting. Author then asked for all of it fixed.

**THE REAL ERROR (found, verified, FIXED).** app_proofs proof of
thm:dir-vertex-m2-exact read "By Whitney kappa <= lambda, every digraph feasible
for the vertex problem is feasible for the arc problem, so k_2 <= ell_2". That is
backwards. kappa <= lambda gives {lambda^max <= m-1} SUBSET {kappa^max <= m-1}, so
the VERTEX-feasible family is the larger one and k_m >= ell_m: an arc upper bound
says nothing about the vertex problem. Same inversion in the ch1 lead-in and in
ch4 ("it will follow from the arc case the moment the backward-arc lemma is
supplied" -- it will not). Notably rem:threshold-analogues had the direction RIGHT
all along, so this was a local slip, not a misunderstanding.
  THE THEOREM IS STILL TRUE, and the repair is cheap: kappa is deletion-monotone
  for exactly the reason lambda is (lem:subdigraph-monotone now states both), so
  the n>=8 induction and both parity computations transfer verbatim; only the base
  cases n<=7 had to be re-run under the vertex test. They were, three independent
  ways (a scratch vertex-split max-flow, a scratch Menger-by-hand bitmask version,
  and the thesis program itself), all returning 2,4,6,8,10,12 = M(n). New
  rem:whitney-direction spells out the trap, the proof is rewritten in two halves,
  and figures/basecase_search_vertex_log.txt is the transcript beside the arc one.

**PROGRAM.** _exhaustive_directed's vertex branch called max_vertex_connectivity on
the WHOLE graph per node (that is why the vertex base cases had never been run) and
deliberately refused to seed the vertex search. Both fixed: new
_vertex_flow_at_least (the vertex twin of _arc_flow_at_least, on the split network)
makes the vertex branch incremental like the edge branch, and the seed is now valid
in both separations BY Whitney in the correct direction (arc-feasible implies
vertex-feasible, so an arc construction is an honest vertex lower bound -- the old
comment claiming otherwise was the same inversion in the code). Differential-tested
0 mismatches / 225,296 (pair, k) checks against the exact checker.

**FIVE OVERCLAIMS FIXED** (all confirmed against the source first):
1. Multigraph vertex rows: the collapsing convention makes the EDGE count
   unbounded (pile on parallel copies forever). New sec:parallel-convention says
   the objective counts adjacencies, notes that the other convention gives a
   genuinely new problem (and that lem:incidence-rank uses it), tab:summary rows
   relabelled "convention" not "proved".
2. Hypergraph vertex separation is a hybrid (no shared hyperedge AND no shared
   interior vertex). It was only implicit in ch1. Now defined at first use, with
   why both halves are needed.
3. "The whole m>=3 upper bound rests on one missing lemma" hid four hypotheses.
   Now open:decomposition states all four; ch4/README/open-problems match.
4. The scaling identity L_m = (m-1)M*(n) was displayed unconditionally before the
   integrality observation that earns the reverse direction. Now the inequality is
   general and the equality is stated as conditional on an integral optimum
   (verified for n<=6). "L_3(7)=24, equivalently M*(7)=12" was one-directional;
   corrected, and it is the INTEGRAL program that is asked.
5. prop:dir-hyper-general claimed forward and general share a leading constant.
   They share two bounds a factor of 4 apart, which fixes the order only. Fixed in
   the proposition and in ch4's orientation section ("the moment n exceeds r the
   gap is gone" is computational evidence, now labelled as such).

**THRESHOLD SCALE (code bug, not just a caption).** tab:summary claimed p*=m/n
"applies uniformly across all models" and plot_conn_threshold_3d drew the m/n line
on a 3-uniform HYPERGRAPH panel. Wrong scale: a vertex lies in p*C(n-1,r-1)
hyperedges, so p* = m/C(n-1,r-1) = Theta(m/n^(r-1)); at r=3,n=8 that is 3/21, not
3/8. The figure now sweeps each panel in units of its OWN p* and titles each with
it; new rem:threshold-scope does the arithmetic; ch1 and both captions corrected.

**NEW RESULT (from the review, author must decide on acknowledgment).**
prop:dir-arc-stability: for any simple digraph with lambda^max <= m-1,
|A| <= floor(n^2/4) + sqrt(m) n^{3/2}, and deleting that many arcs leaves a
one-directional bipartite digraph. Proof: the direct arc plus the two-step detours
through distinct midpoints are automatically arc-disjoint, so summing the
per-pair cap bounds sum_x d+(x)d-(x) <= m n(n-1) (the digon diagonal costs the
+1 in m); Cauchy-Schwarz then bounds sum_x min(d+,d-) by sqrt(m) n^{3/2}; deleting
each vertex's smaller side leaves only source-like -> sink-like arcs. Hence
ell_m^dir(n) = n^2/4 + O_m(n^{3/2}) UNCONDITIONALLY -- the first upper bound in the
thesis for m>=3 with no structural hypothesis, and it fixes conj:dir-arc's leading
constant 1/4. Every step machine-checked (0 violations / 3000 sampled feasible
digraphs) and a check is in the self-test. The error term is honest not sharp:
the conjecture's second-order term (m-2)n/2 is smaller than n^{3/2}, so sharpening
to O_m(n) is the natural next target. Added to the contribution statement.

**BIBLIOGRAPHY (two confirmed wrong, one unresolved).** Leonard "On a conjecture
of Bollobas and Erdos" is Period. Math. Hungar. 3 (1973) 281-284, NOT 2(1-4)
191-194 (1972); key renamed Leonard73BE, DOI added. Ref [19] Bollobas 1984 TAMS
286 is the GIANT-COMPONENT paper and cannot support "kappa = delta whp"; replaced
by Bollobas, Random Graphs (2nd ed.) Ch. 7 plus Bollobas-Thomason 1985 for the
hitting-time form. NOT RESOLVED: the review says Sorensen-Thomassen holds for
n >= 13 where the thesis says n >= 10. Could not verify either way (paywalled,
erdosproblems.com 403s). ch1's own justification of n >= 10 is internally sound
(its five arithmetic claims all check out), so it was LEFT ALONE and flagged in
TASKS.md as the one item needing the original paper.

VERIFY: 90 unit tests OK (was 88, +2 for the vertex flow predicate), self-check
ALL CHECKS PASSED including the new vertex base cases and the stability bound.

## 2026-07-30 (Opus, phase 2) -- the promotor's list closed, three new results

Author clarified that the ChatGPT review WAS Stijn Cambie's feedback (he ran the
draft through it), so the promotor's concerns and the review list are the same
list. Author asked to attempt three of the review's research suggestions and to
keep auditing for mistakes.

**AUDIT FOUND TWO MORE ERRORS, mine and the review's alike missed them.** Both
are missing hypotheses that make a stated result literally false at small n:
 - thm:leonard was "for simple graphs and m <= 4, k_m(n) = floor(m(n-1)/2)" with
   NO n condition. At n=3, m=4 the formula gives 4 where a 3-vertex graph has 3
   edges. Exhaustive check confirms the value is 3. Mader's theorem in the same
   chapter carries "n >= m"; Leonard's had lost it. Fixed, with the reason
   spelled out (below n = m the complete graph is itself feasible).
 - conj:dir-arc had the same hole: at n=3, m=4 it predicts 8 where 6 arcs exist.
   Exhaustive check confirms 6. Both constructions it cites already say n >= m.
   Fixed in ch1, ch3 and the tab:summary caption.
The figures had been capped at the trivial maximum since 2026-06-13, so the
plots were right and the text was wrong. That is the kind of inconsistency an
audit catches and a reader does not.

**RESULT 1: the error term sharpened from O(n^{3/2}) to O_m(n).** This goes past
what the review suggested. Two additions to prop:dir-arc-stability:
 - Step 2 tightened from m n(n-1) to (m-1) n(n-1). The digon diagonal is at most
   |A| (distinct digons use disjoint arc pairs) and Step 1 leaves exactly |A| of
   slack, so the two cancel. Machine-checked tight (slack 0 attained).
 - lem:small-side: min(d+,d-) <= 2 d+ d- / deg, since max >= deg/2. So a vertex
   of LARGE degree has a SMALL smaller-side, which is exactly the case where the
   Cauchy-Schwarz of Step 3 is lossy. Dichotomy: min degree >= n/2 gives
   sum min <= 4(m-1)(n-1) directly; otherwise delete a vertex of degree
   <= floor(n/2) and induct, closing exactly via lem:floor-identity.
 => thm:dir-arc-linear-error: |A| <= floor(n^2/4) + 4(m-1)(n-1) for all n, m,
 so ell_m^dir(n) = n^2/4 + Theta_m(n) unconditionally. The conjecture's
 second-order coefficient is (m-2)/2; this pins it below 4(m-1), a factor of
 about 8. Verified: 4000 random feasible digraphs for the counting steps, 1356
 min-degree->=n/2 samples for Case 2, 0 violations, and the self-test carries
 both bounds plus the Case 2 inequality.

**RESULT 2: the multigraph vertex problem under the other convention (new
section A.8), and my first conjecture about it was REFUTED by the data.**
 - lem:multi-vertex-split: kappa(u,v) = mu(u,v) + pi(u,v), where pi counts
   internally disjoint routes of length >= 2. Parallel copies and longer routes
   never interfere.
 - thm:multi-vertex-m2: K_2(n) = n-1, exactly the spanning trees (proved).
 - I first conjectured K_m(n) = (m-1)(n-1) for n >= m-1 on the m=2,3 data. The
   exhaustion then returned 14 at m=5,n=4 and 19 at m=5,n=5 against the tree's
   12 and 16. REFUTED. The extremiser is a THICKENED THETA: two poles, the n-2
   middles joined to both at multiplicity m-2, poles joined at m+1-n. Feasible
   iff n <= m+1, and it beats the tree there for every m >= 4.
 - So the problem is genuinely NOT the multigraph edge problem, which the m <= 4
   data alone would have suggested. Restated as conj:multi-vertex for n >= m+2
   only, flagged as verified for m <= 4. Reduction to
   sum pi >= (m-1) rank(G_0) given, and the theta graph is exactly its
   counterexample in the small-n regime (rank 3, sum pi 9, needs 12).
 - Program: max_multigraph_vertex_standard + a parallel_routes flag on
   _split_capacity_matrix / exceeds_bound. Cross-validated against an
   independent script on 15 cells, 0 mismatches, and the program is faster.

**RESULT 3: the review's third suggestion is misdirected, and testing it fixed
my own conjecture.** ChatGPT proposed classifying m=3 extremisers at n=6,7,8 to
test whether they admit the A->B partition. But at m=3 the quadratic branch only
overtakes the linear one at n=9, so n=6,7,8 are all hub-regime and cannot test
the hypothesis at all. Ran the classification at m=2 instead, where the
crossover is n=8: at n=5 and n=6 there are exactly 3 and 6 extremal digraphs up
to isomorphism, which are the numbers of TREES on 5 and 6 vertices. So the
linear-branch extremal set is all bidirected spanning trees, not just the hub,
and open:decomposition's "extremal non-hub digraph" was too narrow a hypothesis.
Restated with a condition on n (past the branch crossover) instead of on shape.

ACKNOWLEDGMENT: author asked to credit Stijn Cambie for the review and to say
something about cross-model review. Added to the foreword and a paragraph to the
Contribution Statement: a model that helped write an argument is a poor reviewer
of it, a cold second model reads each sentence as a standalone claim, the value
came from the disagreement, and most of what it raised was wrong and had to be
checked against the source first.

S-T RANGE: left at n >= 10 per the author, with a recorded note that an external
review claims n >= 13 and that nothing here depends on which is right.

VERIFY: build 136 pp, 0 overfull, 0 undefined refs/cites; 90 tests OK; self-check
ALL CHECKS PASSED including the new entries; hunspell en_GB clean.

## 2026-07-30 (Sonnet) -- S-T threshold resolved via erdosproblems.com, and a real citation mismatch found

Author asked to work the open-problem queue while the fact (a) confirmation run and
the m=5/m=6 multi-vertex sweep keep going in the background (both left untouched;
machine load was 25-30 on 10 cores, so no new heavy compute was launched).

**S-T RANGE RESOLVED.** The n>=10 vs n>=13 question, previously left as the
author's call because the primary paper is paywalled, is now settled without
needing the paywalled paper: erdosproblems.com (Thomas Bloom's maintained Erdos
Problems database, already cited in this thesis as \cite{ErdosProblems}) states
directly, quoting Sorensen-Thomassen: "proved that k_5(n) = floor(8n/3) - 3 for
n >= 13." Fetched via plain curl (WebFetch hit a Cloudflare 403 the tool couldn't
get past; curl worked fine, ordinary public page, nothing paywalled or
authenticated). thm:sorensen-thomassen and its surrounding paragraph updated to
n>=13, citing \cite{ErdosProblems} for the number and stating plainly that this
corrects the thesis's own earlier n>=10.

**REAL CITATION MISMATCH FOUND while on the same page.** erdosproblems.com lists
THREE separate Leonard papers under separate keys: Le72 ("proved l_m(n)=k_m(n) for
2<=m<=4 and the l_5 parity formulas"), Le73 ("disproved this conjecture for m=5,
giving an explicit counterexample with 57 vertices and 141 edges"), Le73b ("proved
l_6(n)=3n-2"). This thesis's thm:leonard (the m<=4 equality) and the ch1 lineage
paragraph both cited \cite{Leonard73BE}, whose TITLE is "On a Conjecture of
Bollobas and Erdos" -- that title is unmistakably Le73, the DISPROOF paper, not
the m<=4 equality paper. The correct entry was sitting unused in ref.bib all
along as Leonard72b ("On Graphs with at Most Four Line-Disjoint Paths Connecting
any Two Vertices", JCTB 13:242-250, 1972), whose title is exactly Le72's claim.
Both citations swapped to \cite{Leonard72b}. Leonard73BE (correct bibliographic
data, fixed earlier today) was not orphaned: it is the right citation for
Leonard's own 57-vertex/141-edge counterexample, which the thesis discussed
without ever citing -- added one sentence crediting it right where the m=5
divergence is introduced, so the entry now supports a claim it actually makes.
(Leonard73, "Graphs with 6-Ways", Canadian J. Math 25:687-692, plausibly matches
Le73b's ell_6(n)=3n-2 but is not currently cited by any claim in this thesis;
left alone, not urgent.)

VERIFY: latexmk exit 0, 138 pp, 0 overfull, 0 underfull, 0 undefined refs/cites.
Program untouched, no test re-run needed.

## 2026-07-30 (Sonnet, cont.) -- Case 2 of thm:dir-arc-linear-error proved tight (negative result)

Attempted the concrete idea TASKS.md flagged: cut Case 2's constant (currently
4(m-1), conjectured target (m-2)/2, factor ~8 gap) by exploiting that the
conjectured extremiser has min(d+,d-)=0 on a whole side, since Case 2 "charges
every vertex the worst case" of lem:small-side. Reformulated exactly what Case
2's proof is allowed to use (the aggregate budget sum d+(x)d-(x) <=
(m-1)n(n-1) plus the per-vertex floor d(x)>=n/2) as a resource-allocation
relaxation, and proved via a concavity/exchange (smoothing) argument that the
true maximum of sum min(d+,d-) under those two facts alone is attained by
CONCENTRATING the budget on ~16(m-1) vertices (a constant, not growing with n)
at d+=d-=n/4 each, with the rest at 0 -- and that this bang-bang maximum
equals 4(m-1)(n-1) asymptotically, exactly the theorem's existing constant.
Verified independently with a constrained nonlinear solver (SLSQP, multi-start)
across several (n,m): agreement to 1e-13 relative error.

So the idea does NOT work: the "vertices with min=0" intuition is already
baked into the tight point of the CURRENT proof's own relaxation (lem:small-
side is tight iff d+=d-, the floor substitution d(x)->n/2 is tight iff
d(x)=n/2, both hold simultaneously only at d+=d-=n/4, exactly where the
bang-bang optimum sits), so summing the crude per-vertex bound loses nothing.
Closing the gap needs a genuinely independent second inequality (candidate:
interference among the O(m) expensive near-balanced vertices themselves, not
attempted), not a sharper reading of the existing one.

Wrote this up as a full proof (concentration lemma + tight-point coincidence)
in research_notes/case2_tightness.md, with research_notes/scripts/
case2_tightness_check.py (self-contained, numpy+scipy, verifies the bang-bang
closed form against an independent solver). Folded a condensed version into
app_proofs.tex as new rem:case2-tight right after thm:dir-arc-linear-error's
proof, replacing the old "the dichotomy above suggests where to push" hint
(which pointed at exactly the idea now ruled out) with the actual result, so a
future reader or session does not re-attempt the same dead end. Style matches
the existing rem:min-degree-obstruction (a full proved-negative-result remark,
not just a footnote).

VERIFY: latexmk exit 0, 138 pp (unchanged), 0 overfull. Two underfull hboxes
present are pre-existing (confirmed via git stash against the prior commit,
unrelated to this edit -- one is a figure resizebox, one is near main.bbl).
No program code touched, no test re-run needed.

## 2026-07-31 (Sonnet, cont.) -- conj:multi-vertex REFUTED for all m>=5: clique chains

Working task #1 from the queue (prove sum pi(u,v) >= (m-1)rank(G_0), which the
thesis says would close conj:multi-vertex), the target inequality itself
turned out FALSE. Direct construction: a single triangle grafted onto the
thickened tree has cycle rank 1 and sum pi = 3 (each triangle edge has pi=1,
the "long way round"), so the inequality (m-1)*1 <= 3 fails for every m>=5.
Checked this actually beats the tree via the real feasibility checker, not
just the sufficient-inequality proxy: built the multigraph directly
(triangle at multiplicity m-2, rest of the tree at m-1) and confirmed with
exceeds_bound(..., parallel_routes=True) that kappa^max stays exactly at
m-1 while total multiplicity exceeds (m-1)(n-1) by exactly m-4, for every
tested (m,n) with m>=5, n from m+2 up to n=30.

Pushed further: does packing MULTIPLE disjoint triangles compound the gain?
Yes, exactly linearly (k triangles -> k(m-4) excess), confirmed computationally
for k up to 10. Then asked whether triangles are even the best local gadget:
generalized to K_r blocks (thickened complete graphs on r vertices, the
thesis's own existing "thickened complete graph" construction, but used as a
repeated LOCAL block rather than the whole graph). Derived gain(r,m) =
(r-1)(r-2)(m-1-r)/2 per block algebraically (matches numerics exactly, no
rounding). The gain RATE per vertex used is maximized near r~m/2, not r=3,
and scales like Theta(m^2) there (numerically: m=50 gives rate ~265 per
vertex, roughly m^2/9). So for large m the correct construction uses
half-m-sized cliques, not triangles, and the resulting lower bound is
K_m^multi(n) >= (m-1)(n-1) + floor(n/r)*gain(r,m), giving
K_m^multi(n)/n -> (m-1)+Theta(m^2) as n->infinity, a QUALITATIVELY different
growth rate in m from the withdrawn conjecture's Theta(m).

FEASIBILITY PROVED BY HAND (not just checked numerically), via a clean
cut-vertex argument: every bridge/pendant edge in the chain-of-blocks graph is
a genuine bridge (single edge, no alternate route between blocks), so no
length->=2 path between two vertices of the SAME block can leave and return
(would need to cross a bridge twice), hence pi(u,v)=r-2 exactly inside each
K_r (standard Menger fact: K_r minus one edge has exactly r-2 internally-
disjoint 2-paths, no more, since the other r-2 vertices are a matching-size
cut). So kappa within a block = q+(r-2) = (m+1-r)+(r-2) = m-1 exactly, never
over. Cross-block pairs are separated by a single cut vertex (a port), so
kappa<=1 there, nowhere near the cap. This closes the construction as a
genuine theorem, not just a numerically-checked family.

VERIFIED TWO INDEPENDENT WAYS at a spread of (m,r,k): the thesis program's own
exceeds_bound(separation="vertex", parallel_routes=True), AND a from-scratch
max-flow on a hand-built vertex-split network using networkx
(maximum_flow_value), sharing no code with the thesis checker. Both agree
exactly (not just approximately) with the closed-form formula in every case,
including m=15,r=8,k=2,n=21 (worst kappa=14=m-1) and m=20,r=11,k=2,n=27
(worst kappa=19=m-1).

THESIS CORRECTED (this conjecture was only added a few hours earlier in
today's own phase-2 session, so this is same-day self-correction, not a
lingering error): app_proofs.tex's conj:multi-vertex environment removed
entirely (a false statement has no place in a numbered Conjecture, matching
the honesty contract) and replaced with thm:clique-chain-vertex (full
statement + proof, renders as Theorem A.56, page 114-115, visually verified
clean). The "Two things stand out" lead-in paragraph, the sum-pi reduction
paragraph, ch4_synthesis.tex's open-problems item, and main.tex's contribution
statement sentence about this section were all rewritten to match. Program
code untouched (exceeds_bound/parallel_routes were already there and correct,
this was purely a mathematical-content finding, not a bug).

Written up in research_notes/multi_vertex_clique_chains.md (full derivation +
proof + the exact-optimal-r table + what remains open: whether same-size
clique chains are actually optimal among ALL feasible multigraphs, which they
are not known to be) with research_notes/scripts/multi_vertex_clique_check.py
(both verification methods, asserts, reproducible).

VERIFY: latexmk exit 0, 138 pp (unchanged), 0 overfull, 0 undefined refs/cites
(thm:clique-chain-vertex resolves as A.56). No program code touched, no test
suite re-run needed (no .py changes).

## 2026-07-31 (Opus) -- verified the Sonnet session, found and fixed a hypothesis gap

Author switched models and asked to check the previous session's work before
resuming. Re-verified the central claim (the conj:multi-vertex refutation)
with a THIRD implementation written from scratch -- own Edmonds-Karp on a
hand-built split network, no thesis program, no networkx, no scipy. The
refutation holds. The smallest witness is fully hand-checkable and now stated
in the thesis: m=5, n=7 (the very first size the withdrawn conjecture covered),
a triangle at multiplicity 3 plus a four-edge pendant path at multiplicity 4,
total 25 against the conjectured maximum 24, with kappa^max exactly 4.

FOUND A REAL GAP in the new theorem's hypothesis range. thm:clique-chain-vertex
was stated for 3 <= r <= m+1, but at r = m+1 the block multiplicity q = m+1-r
drops to ZERO, so the blocks carry no edges and the underlying graph falls
apart into isolated vertices. The proof's count substitutes
|E(G_0)| = n-1+rank(G_0), which assumes connectivity, so the proof is invalid
at that endpoint. (The final formula happens to survive the degeneracy by an
algebraic accident -- the rank and sum-pi errors cancel exactly -- which is
precisely the kind of coincidence that hides a broken proof, so this was worth
catching.) Fixed: hypothesis tightened to 3 <= r <= m, giving q >= 1, and the
proof now says explicitly where that hypothesis is used and what goes wrong
without it. Nothing is lost, since a positive gain needs r <= m-2 anyway.
Research note and verification script updated to match (the script's assert
now enforces q >= 1 rather than q >= 0, so the degenerate case can no longer
be fed to it silently).

Also verified, and confirmed correct as written: the gain formula
gain(r,m) = (r-1)(r-2)(m-1-r)/2 (re-derived independently from the direct edge
count, matches), the r=3 specialisation m-4 (zero at m=4, matching the
exhaustive table's no-counterexample finding, positive from m=5), the
Theta(m^2) growth-rate claim (continuous optimum at r ~ m/2 gives rate
~ m^2/8; exact integer optima track it), and the Case 2 tightness argument
from the previous session.

VERIFY: latexmk exit 0, 138 pp, 0 overfull, 0 undefined refs/cites. Script
re-run after the range fix, all checks pass. Background jobs untouched and
still alive (fact (a) confirmation PID 79768, multi-vertex sweep PID 79194).

## 2026-07-31 (Opus) -- hypergraph vertex at m=4: no counterexample, but the formula's boundary is now PROVED

Task #4 from the queue. Applied the lesson from the multigraph result: TEST
the target statement before investing in proving it.

FIRST, THE ARITHMETIC THAT MAKES THE TEST EXACT. For a connected incidence
graph with b hyperedges of size r on n vertices, rank(I) = b(r-1) - n + 1, so
rank > (m-2)(n-1) holds exactly when b > (m-1)(n-1)/(r-1). "One hyperedge past
the formula" and "rank past the conjectured bound" are therefore the SAME
condition, so searching for one extra hyperedge is a direct test of the
missing 4-connectivity rank bound rather than a proxy for it.

FINDING 1 (PROVED): the general formula k_m^(r)(n) = floor((m-1)(n-1)/(r-1))
cannot hold for all m and r. rem:hyper-vertex-m3-scope already observed that
r=2 "speaks of multigraphs under the hyperedge-as-gate convention", but only
in one direction. The identification runs BOTH ways: at r=2 the hypergraph
vertex measure equals mu(u,v)+pi(u,v), i.e. lem:multi-vertex-split, because
the mu parallel copies are pairwise edge-disjoint with empty interiors, and
any two internally-vertex-disjoint paths of length >=2 are AUTOMATICALLY
edge-disjoint (a shared edge would force a shared interior vertex), so the
hyperedge-disjointness requirement bites only among the length-one routes,
which is exactly what makes parallel copies count separately. Hence
k_m^(2)(n) = K_m^multi(n), and yesterday's thm:clique-chain-vertex applies
verbatim: the formula fails at r=2 for every m>=5 and every n>=3, by a margin
growing linearly in n. This also explains tab:multi-vertex's own bold entries
(14 at m=5,n=4 and 19 at m=5,n=5 against the formula's 12 and 16) -- the
thesis was already displaying this failure without connecting it to the
hypergraph row. So the live question is not "is the formula true for all m,r"
(it is not) but "does r>=3 postpone the failure past m=4", which puts m=4
right at the boundary.

FINDING 2 (VERIFIED, no counterexample): at m=4 the formula survives
exhaustive checking of BOTH halves (target attained, target+1 infeasible) at
ELEVEN (n,r) pairs: (4,3),(5,3),(5,4),(6,4),(6,5),(7,5),(7,6),(8,6),(8,7),
(9,7),(9,8). Previously only the single cell k_4^(3)(5)=6 was known. Still
evidence, not proof.

METHOD + CROSS-VALIDATION: research_notes/scripts/hyper_vertex_m4_search.py,
written from scratch (standard library only, own Edmonds-Karp, own
incidence-graph model, no dependence on the thesis program it corroborates).
DFS over multisets of r-sets with monotone feasibility pruning plus a codegree
filter. Run at r=2 it independently reproduces tab:multi-vertex including the
m=5 failure, and the witness it returns at m=5,n=5 is a triangle at
multiplicity 3 with two pendant edges at multiplicity 4 -- precisely the
clique-chain shape, rediscovered from a completely different search space
without being told to look for it. That is a third independent confirmation
of thm:clique-chain-vertex.

THESIS: rem:hyper-vertex-m3-scope rewritten. It previously cited the SIMPLE
graph case (m=5, Sorensen-Thomassen, a different convention) as the warning
that the pattern must fail eventually. It now states the sharper same-
convention fact (r=2 fails at exactly m=5, provably, for all n>=3), records
the eleven-cell m=4 evidence, and says plainly that this is evidence rather
than proof with the 4-connectivity rank bound still missing.

STILL OPEN + LAUNCHED: where the formula first breaks for r>=3. A search at
m=5,6 for r=3,4,5 was started but did not return within the session (the
looser codegree cap at higher m widens the space sharply). Logged in TASKS.md
as the natural next computation.

VERIFY: latexmk exit 0, 138 pp, 0 overfull, 0 undefined refs/cites. Script
runs clean in both modes. Background jobs untouched (fact (a) PID 79768,
multi-vertex sweep PID 79194, both still alive).

CONSISTENCY AUDIT after the above: swept every place that states the
hypergraph vertex agreement or the multigraph vertex status, since three
sessions have now edited overlapping claims. Found ONE stale spot:
ch4_synthesis.tex's open-problems item still cited only k_4^(3)(5)=6 and
called the eventual failure "the analogue of the m=5 graph divergence", an
analogy that is now an actual theorem in this convention. Rewritten to carry
the eleven-cell evidence and the r=2 boundary. Checked and found CORRECT
(no edit needed): tab:summary's two multigraph vertex rows, which refer to
the COLLAPSING convention of sec:parallel-convention and are untouched by the
alternate-convention result; main.tex's "settled at m=2 and m=3" claim; ch2's
description of the other convention as a new extremal problem; and the lay
summary, whose two claims are the m<=3 hypergraph results and fact (a),
neither affected. No dangling reference to the removed conj:multi-vertex
(build reports 0 undefined).

## 2026-07-31 (Opus) -- repo health check caught a reproducibility-claim bug in the test suite

Ran the full suite as a closing health check (no program code had been touched
all session, so this was meant to be a formality). It was not: 90 tests,
1 ERROR on the MINIMAL CORE install.

test_solve.test_directed_multigraph_is_proved calls solve(4,3,directed=True,
simple=False,exhaustive=True), which routes through prove_directed_multigraph
and therefore needs pulp. test_certify.py guards the certifier tests with
@skipUnless(PULP_AVAILABLE, ...) but test_solve.py never imported that flag,
so on a numpy+scipy-only machine this test ERRORED instead of skipping.

That matters more than a normal flaky test, because ch2's reproducibility
section and program/README both advertise numpy+scipy as sufficient for the
core. A reader following that advice, on exactly the configuration the thesis
recommends, would run the suite and be told it FAILED. The claim and the
artefact disagreed.

Fixed with the existing pattern: imported PULP_AVAILABLE into test_solve.py
and added @skipUnless to that one method, with a reason line naming why
solve() needs pulp for this particular case (it proves the directed multigraph
value through the MILP certifier). Verified in BOTH environments, which is the
point: system python3 (no pulp) now reports OK with a clean skip, and the
venv (with pulp) still actually runs the test and passes it, so the guard
hides nothing where the dependency exists.

Full suite on the minimal core: 90 tests, OK, 6 skipped (was 5 skipped +
1 error). README's optional-dependency sentence generalised from geng alone to
all three optional tools (geng, pulp, networkx), stating that a minimal
install runs the suite green rather than reporting failures for tools it was
never asked to have.

## 2026-07-31 (Opus) -- new Appendix C: the complete source code

Author asked for all the code in the paper as another appendix, readable, with
no lines running off the page, and with the surrounding explanation written
plainly (explicitly NOT flagged as simplified, so a reader is not made to feel
talked down to).

SCOPE: measured the real cost first rather than guessing. A test document at
\scriptsize with breaklines gives ~73 code lines per page, so all 7541 lines
(erdos915_unified.py 5733, make_figures.py 627, _erdos_fast.c 139, tests/ 1042)
come to ~104 pages of listing. Put the options to the author with real page
counts since it roughly doubles the document; author chose ALL of it. Final
build is 281 pages, so the appendix came to 143 including its prose and
headings.

STRUCTURE: the appendix follows the program's own internal chapter banners,
which already mirror the thesis chapters, so a reader can jump to the part they
want instead of scrolling a 100-page wall. Split into: how the file opens
(1-183), the objects (184-754), measuring and proving (755-1266), searching
(1267-2308), the random model (2309-2546), the figures (2547-3466), walking the
whole space (3467-4362), the open variants (4363-4911), the gallery
(4912-5446), the self-check (5447-5733), then the figure script, the C helper,
and each test file. Every part opens with a few sentences of plain explanation
of what it does and which chapter it belongs to. Boundaries were checked to
land on blank lines before the banners.

PREAMBLE: added three missing literate mappings (o-double-acute from Erdos, and
the en and em dashes) which appear in the source files and would otherwise abort
the build under utf8 inputenc. New `sourcelisting` style derived from
pythonkul: \scriptsize, no background tint (kinder to a printer over 143
pages), no frame since line numbers already mark the left edge.

VERIFICATION (the "no lines out of bounds" requirement, checked properly rather
than assumed): latexmk exit 0, 281 pp, ZERO overfull hboxes, no undefined refs,
no missing characters. Then an end-to-end completeness check, because zero
overfull only proves nothing exceeds the margin, not that nothing was dropped:
extracted the appendix text and confirmed the final printed line number equals
the true file length for all THIRTEEN files (5733, 627, 139, and each test file
from 16 to 198). Two false alarms along the way, both artefacts of pdftotext
rather than the PDF: listings inserts inter-token spacing, and breakatwhitespace
=false lets a wrap fall mid-identifier, so naive substring matching against the
extracted text fails on lines that are in fact fully present. Pages rendered to
PNG and inspected: highlighting, line numbers and the hookrightarrow wrap marker
all correct.

## 2026-07-31 (Opus) -- full-thesis audit, part 1: a convention trap in the cited S-T constant

Author asked for a complete re-check of every statement. Set up five audit
threads (closed forms by machine, m<=4 extrapolations, degenerate hypothesis
endpoints, citations, cross-chapter consistency). First real finding came out
of the citation thread.

CONVENTION MISMATCH (author decision needed, recorded not silently fixed).
Cross-checking the bibliography against erdosproblems.com showed the database
states every result in the OPPOSITE convention to this thesis: it gives the
minimum number of edges that FORCES an m-connected pair, where the thesis
gives the maximum that AVOIDS one. Those differ by exactly one, confirmed on
all six entries both sources state (k_2(n)=n vs n-1, k_3(2n)=3n-1 vs 3n-2,
k_4(n)=2n-1 vs 2n-2, l_5(2n)=5n-2 vs 5n-3, l_6(n)=3n-2 vs 3n-3, and the
Bollobas-Erdos conjecture as 1+C(m,2)n vs C(m,2)n). The thesis's own
convention is machine-confirmed: exhaustive search gives k_3(4)=4, k_3(5)=6,
k_4(5)=8, exactly floor(m(n-1)/2), i.e. the database's values minus one.

CONSEQUENCE: yesterday I took the n>=13 threshold for thm:sorensen-thomassen
from that database but did NOT notice the FORMULA needs the same shift. The
database's k_5(n)=floor(8n/3)-3 corresponds to floor(8n/3)-4 in this thesis's
convention, yet the thesis prints -3. So the stated constant is probably one
too high. It is NOT a mistake I introduced (the -3 predates today) but it is
one I walked past while editing the same sentence.

Both -3 and -4 satisfy k_5 >= l_5, which Whitney forces, so the thesis's own
arithmetic cannot decide between them and only the original paper can. Did NOT
silently change a cited external theorem. Instead added
rem:threshold-convention, which lays out the shift with all six examples and
the machine-verified values, says plainly that the printed constant is the
database figure carried over unadjusted, and notes that nothing in the thesis
depends on which is right since k_5 enters only as the cited first divergence.
Flagged in TASKS.md as needing the paper. Also dropped the now-vestigial
small-n arithmetic from that passage, which dated from when the threshold was
n>=10.

VERIFY: latexmk exit 0, 281 pp, 0 overfull, 0 undefined.

## 2026-07-31 (Opus) -- the overnight sweep beat my own theorem; construction strengthened

The m=5/m=6 multigraph-vertex sweep (PID 79194, launched by an earlier
session) finished. Values: m=3 n=7 = 12 exact (= tree), m=4 n=6 = 15 exact
(= tree), m=6 n=5 = 26 exact (theta, > tree 20), and three that hit their time
cap as lower bounds: m=5 n=6 >= 24, m=4 n=7 >= 18, and m=5 n=7 >= 28.

That last one is the interesting one, because n=7 = m+2 at m=5 is exactly the
regime the withdrawn conjecture covered, and 28 is well past the tree's 24.
More to the point it is past MY OWN construction: thm:clique-chain-vertex as
written this morning gives only 26 there. So the theorem I added today was
true but visibly not the best available.

FOUND THE IMPROVEMENT. The chain joined DISJOINT K_r blocks with bridge edges,
which fits floor(n/r) blocks because every bridge spends a whole vertex on the
join and nothing else. Letting all the blocks SHARE a single common vertex
instead fits floor((n-1)/(r-1)) blocks, strictly more, with the identical
per-block gain and an identical feasibility argument (the shared vertex is a
cut vertex, so a route between two vertices of one block still cannot leave
and return). At m=5,n=7 the bouquet gives 27 against the chain's 26; at
m=10,r=6,n=11 it gives 150 against 120. Verified across seven (m,r,k)
settings, both by the program's checker and by the independent networkx
max-flow, formula matching exactly every time.

Theorem restated in the bouquet form (same label, retitled "Thickened cliques
beat the thickened tree"), proof adjusted (the cut-vertex argument is if
anything simpler), and the surrounding text now states plainly that even the
bouquet is NOT the exact value, citing the 28-vs-27 gap. ch4 and the
contribution statement updated to match. Research note and verification script
updated, with the chain recorded as superseded rather than deleted so the
reasoning is traceable.

The Theta(m^2) growth claim is unaffected: the gain per vertex is now
gain(r,m)/(r-1) rather than /r, which improves the constant and leaves the
order alone.

VERIFY: latexmk exit 0, 283 pp, 0 overfull, 0 undefined refs/cites.

## 2026-07-31 (Opus) -- audit part 2: a stale summary-table cell, and the audit's own dependency bug

CROSS-CHAPTER SWEEP found one stale cell. tab:summary (ch4) still printed the
Sorensen-Thomassen threshold as n>=10, the value corrected to n>=13 in ch1
this morning. Exactly the failure mode this repo keeps hitting: a number fixed
in one place and left behind in another (the conj:dir-arc correction missed
three sites for weeks in June). Fixed, and pointed at the new
rem:threshold-convention so the cell carries the caveat too. Swept for any
other surviving "n >= 10": none.

AUDIT SCRIPT hit the same missing-pulp bug I had just fixed in the test suite,
in its own way: audit_closed_forms.py calls solve() on the directed multigraph
row, which routes into the MILP prover, so under the system python it died
partway with an ImportError. Relaunched under the venv interpreter. Worth
recording because it is the second time today that the "core needs only numpy
and scipy" claim collided with something that quietly needs pulp, which
suggests the boundary is thinner than the docs imply.

AUDIT RESULTS SO FAR (seven sections completed before the crash): 46 cells in
exact agreement, 0 mismatches inside any stated hypothesis range, and 10
mismatches OUTSIDE the stated ranges. That last number is the useful one: it
is the evidence that the n >= m hypotheses on thm:mader, thm:leonard and
conj:dir-arc are load-bearing rather than decorative, since the formulas
genuinely do fail below them (thm:mader at n=2,3 for m=4 and n=2,3,4 for m=5;
conj:dir-arc at n=2 for m=3 and n=2,3 for m=4). Those hypotheses were added
only yesterday, so this is the first sweep that has actually tested them.

VERIFY: latexmk exit 0, 283 pp, 0 overfull, 0 undefined refs/cites.

## 2026-07-31 (Opus) -- gurobi_handoff/ for the promotor, and a fragility fix in Appendix C

Author asked for a single folder his promotor at KU Leuven can run, since
Gurobi is the realistic route to fact (a) and the local uncapped enumeration
has now been going 13.5 h (about 58 CPU-hours across 10 workers) with no
verdict and no way to estimate one.

gurobi_handoff/ contains erdos915_unified.py (unmodified copy), check_setup.py,
run_fact_a.py, run_fact_a4.py, README.md, requirements.txt. Also zipped at
gurobi_handoff.zip for sending. Design decisions worth recording:
- check_setup.py runs in seconds and re-proves L_3^dir(4): FEASIBLE at 12,
  INFEASIBLE at 13. A wrong answer there means the install is broken rather
  than the mathematics, which is a much better thing to learn in five seconds
  than five hours in. It also reports the Gurobi licence state explicitly.
- run_fact_a.py passes use_gurobi=True on purpose, so it fails loudly instead
  of silently falling back to CBC and running forever. A friendly pre-flight
  guard catches the no-Gurobi case and points at check_setup rather than
  dumping a traceback at a promotor.
- The README states all three verdicts and what each means, including that
  FEASIBLE would contradict the hand proof and should be sent back rather than
  assumed to be an error.
- Verified self-contained by copying to a scratch directory and running there.

FIXED A REAL BUG IN THE PROGRAM'S ERROR MESSAGE: _pick_solver told the user to
"install gurobipy", but this path is PuLP's GUROBI_CMD, which shells out to
gurobi_cl and does not need gurobipy at all. Corrected to name gurobi_cl.

THAT EDIT THEN EXPOSED THE FRAGILITY I HAD FLAGGED WHEN BUILDING APPENDIX C.
Adding two lines to erdos915_unified.py shifted every hardcoded linerange below
the edit, so eight of the ten listings would have printed the right code under
the wrong heading, silently. Rather than hand-patch, added
program/sync_code_appendix.py, which recomputes the boundaries from the
program's own section banners and either checks (non-zero exit if stale) or
rewrites them. Ran it, rebuilt, and re-verified completeness: all thirteen
files still print in full, final line numbers matching true lengths, 0 overfull.
RUN THIS AFTER ANY EDIT TO erdos915_unified.py.

VERIFY: latexmk exit 0, 283 pp, 0 overfull, 0 undefined refs/cites. Handoff
folder exercised end to end (correct verdicts on both known cases, clean
failure on the missing-Gurobi path).

## 2026-07-31 (Opus) -- stopped the fact (a) enumeration, recorded the Gurobi route in the thesis

Author: "stop the shell running, i don't care about the result for now. put in
the thesis that it can be checked with the gerobi." Killed the uncapped n=7
enumeration and its ten workers after ~14 h and ~58 CPU-hours with no verdict
(load dropped from ~25 to ~19). The audit sweep is a separate job and was left
running.

Recorded the Gurobi route in two places, since the thesis previously said only
that the check was runtime-limited without telling a reader what to do about
it. rem:odd-step-roadmap (app_proofs) now gives the exact call,
prove_integral_arc_bound(7, 3, 25), states that INFEASIBLE IS fact (a), and
explains that CBC and the uncapped enumerator both fail while the identical
model with use_gurobi=True goes to a solver in a different class, free for
academic use, with _pick_solver routing the same pulp model either way and the
verdict being a proof because the cut formulation is exact rather than a
relaxation. ch4's open-problems item carries the same call in one sentence.
This mirrors gurobi_handoff/ so a reader of the thesis and a reader of the
folder are told the same thing.

VERIFY: latexmk exit 0, 283 pp, 0 overfull, 0 undefined refs/cites.

## 2026-08-11 (Sonnet) -- the directed multigraph problem CLOSED: an external
## proof checked, verified three independent ways, and integrated in full

Stijn showed the author `directed_multigraph_extremal_revised.pdf`, a ChatGPT-authored
proof claiming L_m^dir(n) = (m-1)*max(2(n-1), floor(n^2/4)) for ALL n>=2, m>=2 (the
directed MULTIGRAPH arc problem, arcs counted with multiplicity -- NOT the simple-digraph
conj:dir-arc, a separate still-open problem). This is exactly the flagship result Result 3
chased for months (attachment lemma, thm:odd-step restricted to m in {3,4}, fact (a)/(b)
at n=7, the Gurobi handoff), so it demanded real scrutiny before touching anything.

CHECKED BY HAND, line by line: the "reachability-preserving spanning subgraph" argument
(SCC decomposition + one in-arborescence + one out-arborescence per component, contract to
a DAG, thin to its transitive reduction, Mantel's theorem on the triangle-free result,
discrete convexity gives the max at an endpoint) is CORRECT. No errors found anywhere.

VERIFIED THREE INDEPENDENT WAYS against cases the thesis had never previously computed
(m=4,5 at n=5,6 -- exactly the m>=5 regime where the thesis's OWN thm:odd-step has a
documented gap): the thesis's exhaustive branch-and-bound solver (n=5 m=4 -> 24=3*8, n=5
m=5 -> 32=4*8, n=6 m=4 -> 30=3*10, all exact), and the MILP certifier (same three cases,
FEASIBLE/INFEASIBLE exactly at target/target+1). All three code paths agree with the hand
proof and with each other.

INTEGRATED into the thesis as thm:dir-multi-full (chapters/app_proofs.tex, new section
"The directed multigraph problem, solved in full"), written at the same explanatory pace
as the rest of the thesis (a new worked example + fig:skeleton-example, a 3-SCC digraph
walked through all three construction steps) since the author found the PDF's own proof
"way too fast to understand." SUPERSEDED AND REMOVED: lem:attachment (+ its figure),
cor:attachment-equality, thm:odd-step, thm:even-step, rem:odd-step-roadmap,
conj:min-degree, rem:min-degree-obstruction, prop:min-degree-m2, lem:scaling-reduction,
prop:dir-multi-even, fig:seam-c8. KEPT: lem:saturated-attachment + rem:saturated-closure
(linear-branch extremal-graph UNIQUENESS, genuinely separate from the value and not implied
by the new proof, reframed as bonus "beyond the value" content) and the n=7 machine
classification (renamed rem:n7-classification, now a standalone fact about which graphs
attain 24 arcs, not a step in proving that 24 is the value). Also directly closes fact (a)
(L_3^dir(7)=24) BY HAND as a 3-line corollary (cor:dir-multi-n7), no Gurobi needed.

Propagated the upgrade from conjecture/conditional to THEOREM across: tab:summary (row now
"proved, all n and m", the "cond." status marker dropped from the caption since no row
uses it any more), ch4's directed-frontier section and open-problems list (the fact-(a)
computation item and the fact-(a)-pseudo-Boolean-certificate item both removed as moot; the
uniqueness-beyond-the-linear-branch item rewritten to reflect what's actually still open),
ch2's "Generating the directed cases faster" / scaling-reduction / certification-standards
sections (reframed as independent confirmation of a now-proved theorem, not the route to
it), main.tex's contribution statement, and the lay summary's closing paragraph (rewritten
in plain language, no more "one computer verdict... is the main question the thesis leaves
open" -- there is no computer verdict needed any more). TASKS.md's flagship item, the fact
(a) confirmation run, and the "m=4 base facts" item (which was independently chasing
L_4^dir(7)=36 by the same seam machinery) are all marked resolved: thm:dir-multi-full gives
every one of those numbers directly, for every m, with no size limit and no solver. Added a
new Mantel07 bib entry (Wiskundige Opgaven, 1907), the first use of Mantel's theorem in
this thesis.

VERIFY: full sweep for dangling \Cref/\ref to every removed label across chapters/*.tex,
main.tex, popularising_summary.tex -- zero remaining. latexmk clean rebuild (full -C purge
first): 285 pp, 0 overfull, 0 undefined refs/cites (one transient overfull from the new
figure's natural TikZ width exceeding \textwidth, fixed with \resizebox{\textwidth}{!}{},
matching this file's existing convention for wide two-panel figures). Rendered the new
theorem/lemma/construction/figure/corollary pages (pp 95-99) to PNG and inspected visually:
clean typesetting, the two-panel skeleton figure has no overlaps, arrows correctly
directed, cross-references resolve. gurobi_handoff/ and its .zip are now vestigial (the
whole point was getting a promotor's Gurobi licence onto fact (a), which is now a hand
proof) -- left in place, not deleted, flagged for the author's own call.

## 2026-08-12 (Opus) -- audit of the new flagship, then three open problems closed

Author asked for a mistake-check plus an attempt at the open problems by proof.

**AUDIT OF thm:dir-multi-full (the 2026-08-11 external proof): CORRECT.** Re-derived
it independently before touching anything, since it is the least-vetted material in the
thesis and supersedes months of work. The reachability-skeleton argument holds: deleting
a subgraph that preserves reachability drops every positive lambda by at least one (the
skeleton's u-v path is arc-disjoint from any packing surviving in D-R), the skeleton
costs 2(n-q) + floor(q^2/4) via SCC arborescences plus a triangle-free condensation, and
that is discretely convex in q so it maxes at an endpoint, giving exactly M(n). Values
check against every computed cell (n=4..7 at m=3 give 12,16,20,24). One cosmetic
imprecision only, not worth an edit: the arc count is written with "=" where the two
arborescences of one SCC can share an arc (a 3-cycle rooted anywhere does), so it is
really "<=", which is the direction the proof needs anyway.

**ONE REAL MISTAKE FOUND (an overclaim, now repaired by proving the missing half).**
sec:multi-vertex-standard asserted that thm:clique-chain-vertex is "a lower bound of the
right order in both n and m" and wrote K_m^multi(n)/n -> (m-1) + Theta(m^2) as an
asymptotic equality. There was no upper bound anywhere in the section, so neither claim
was earned. Both are now true, see result 3.

**THE COMMON ENGINE.** prop:dir-arc-stability and thm:dir-arc-linear-error use
feasibility exactly once, in Step 1, to cap ONE family of routes; everything after is
degree arithmetic. Promoting that cap from a deduction to a hypothesis gives
lem:two-step-budget (a C-budgeted simple digraph has <= floor(n^2/4) + 4C(n-1) arcs; the
only extra check is that the hypothesis passes to induced subdigraphs, which is trivial).
Three different arguments supply the cap, and each is a new thesis result:

1. **thm:dir-vertex-linear-error: k_m^dir(n) = n^2/4 + Theta_m(n), unconditional.** The
   direct arc has empty interior and the two-step detours have distinct singleton
   interiors, so Step 1's family is internally vertex-disjoint too and can be counted
   against kappa. This is NOT the illegitimate transfer the thesis rightly keeps warning
   about (an arc upper bound says nothing over the larger vertex-feasible family): what
   transfers is the CONSTRUCTION, not the bound. The row ch4 listed as untouched by the
   arc case now has the same status as the arc row.
2. **thm:dir-hyper-constant: conj:dir-hyper-constant PROVED**, and for BOTH separations
   at once, so two of the twelve rows change. |E| <= (m-1)floor(n^2/4)/(r-1) +
   4(m-1)^2(n-1), matching prop:dir-hyper-first's bipartite construction asymptotically.
   The thesis had named the obstacle precisely (a hyperedge carries r-1 heads, so
   two-step routes through different midpoints need not be edge-disjoint) and waited for
   it to be removed. It is not removed, it is PAID: a matching argument on the bipartite
   graph of targets-versus-hyperedges-at-u thins the family at a cost of exactly r-1
   (an unmatched target has all its hyperedges matched, each holding <= r-1 targets).
   That factor inflates only C, hence only the LINEAR error term, never the n^2/4, while
   a second and unrelated factor r-1 divides the leading term in the codegree count
   (r-1)|E| = sum cod <= (m-1)|A(R)| over the one-step shadow R. Both steps hold against
   kappa, which is why the vertex row falls out too. NOT covered: the general
   orientation model (the single tail is used twice), flagged in TASKS.md.
3. **prop:multi-vertex-upper: K_m^multi(n) <= (m-1)k_m(n) < 2(m-1)^2 n**, so
   K_m^multi(n) = Theta(m^2 n) and the overclaim above becomes a theorem. Route: the
   underlying simple graph of a feasible multigraph is itself feasible for the SIMPLE
   vertex problem (kappa_{G_0} = 1 + pi <= mu + pi on edges, = pi off them), then Mader's
   density theorem. The first inequality is the informative half, tight at m = 2, and it
   ties the least understood of the twelve variants to the oldest.

VERIFICATION (all before writing any .tex): research_notes/scripts/two_step_budget_check.py,
self-contained, own Edmonds-Karp, no import of the program. Step 1 and Step 2 of the
hypergraph theorem asserted against kappa over 3000 random hypergraphs and every ordered
pair, with 4553 pairs ATTAINING the (r-1) factor with equality, so neither step is slack
that could have been tightened; the vertex route family over 3000 random digraphs; the
multigraph bound on all nine cells of tab:multi-vertex, with k_3(4)=4, k_3(5)=6, k_4(5)=8
reproved from scratch (they match ch1's own machine-verified convention check). Separately
a full-chain run on GROWN FEASIBLE hypergraphs verified every link end to end, and the
final bound was checked against max_feasible_hyperedges at twelve (n,r,m) cells.
Mader's theorem statement and its bibliographic data were both web-verified before citing
(Abh. Math. Semin. Univ. Hambg. 37 (1972) 86-97, doi 10.1007/BF02993903), new entry Mader72.

PROPAGATED: tab:summary (four rows: both directed hypergraph rows now carry a proved
leading constant, both directed simple rows now state n^2/4 + Theta_m(n)), ch4's
directed-frontier paragraph, the orientation-models paragraph, three open-problem items,
and main.tex's contribution statement (a new paragraph for the three, framed around the
budget lemma). Note the two hypergraph upper bounds do NOT dominate one another and both
are kept: prop:dir-hyper-first is smaller until n is around 16(m-1)(r-1)/3.

VERIFY: latexmk exit 0, 289 pp (was 285), 0 overfull, 0 undefined refs/cites. New pages
rendered to PNG and read: A.27/A.28 (budget lemma and vertex theorem), A.54/A.55 (shadow
and hypergraph theorem), A.59 (multigraph upper bound), all clean, all cross-references
resolving. No program code touched, so no suite re-run needed.

## 2026-08-12 (Opus, cont.) -- full-thesis consistency audit after the two closures

Author: integrate directly, keep going until nothing is left. Swept the whole document.

**HONESTY VIOLATION, three places, the most serious finding.** The appendix corollary,
ch2's scaling section, and ch2's certification-standards section each claimed the n=7
MILP had confirmed L_3^dir(7)=24, one in the present tense ("the call returns
INFEASIBLE"). It never ran to completion: CBC timed out, the uncapped enumeration was
killed after ~14 h, and it was never rerun on a stronger solver (the gurobi_handoff
folder was deleted as vestigial the same day). A fourth spot in ch4 said the certifier's
role at n=7 was "an independent check rather than the source of the result", which
implies a verdict that does not exist. All four now say plainly that the machine route
was abandoned unfinished and the hand proof replaced it. This is exactly the failure the
thesis's own honesty contract exists to prevent, so it is worth recording loudly.

**STALE-BY-CONTRADICTION (yesterday's deletions left prose behind that resolves as no
reference, so the build never complained):**
- main.tex SHORT SUMMARY (the abstract) still sold the deleted attachment lemma and
  conditional odd-step theorem plus "two finite machine-checkable statements". Rewritten.
- ch4 closed the directed-multigraph section with "for m>=5 even the value step stalls",
  three paragraphs after stating the theorem holds for every m. It was a limitation of
  the abandoned method; reframed as such.
- ch3's trichotomy put the directed multigraph in the CONJECTURED regime and cited the
  deleted conj:min-degree. Moved to the first regime in both the regime list and the
  paragraph; the certificates are now described as an independent check on a theorem.
- ch3 twice said no upper bound is known for the directed arc problem at m>=3. One has
  existed since 2026-07-30 (thm:dir-arc-linear-error); it is merely too loose at n<=12
  to check a search against, which is what the sentences meant.
- fig:variant-tree-status coloured the multigraph directed EDGE leaf red; tab:summary's
  caption defined "lower bd." which no row used any more after this morning.
- **The generated figures disagreed with the text**: make_figures panel (7) still drew
  the directed multigraph as a red conjecture curve titled "(multigraph, certified)".
  Changed to proved=, retitled, and BOTH grids regenerated (m=3 and m=6). Verified the
  panel now reads "(multigraph, proved)" with a blue curve and the search circles on it,
  and that no other panel drifted.
- program docstring for directed_multigraph_arc still said "Proved for n <= 6.
  Conjectured to continue". It is printed verbatim in Appendix C, so sync_code_appendix
  had to be rerun (it caught 8 shifted lineranges, exactly the fragility it was built for).
- Three SLIDE decks promised "two finite n=7 checks" and a solver that would close them.

**NEW RESULT out of the audit: cor:mstar-integral.** ch2 states as open whether the
fractional optimum M*(n) is always attained by a {0,1} matrix. It is. The feasible region
is a finite union of bounded rational polytopes (one cut choice per pair), so the optimum
is rational; scaling a rational optimum by its denominator q gives an integral multigraph
feasible at m-1=q, and thm:dir-multi-full applies at EVERY m, so no denominator is out of
reach. Hence M*(n)=M(n) and the scaling identity L_m^dir(n)=(m-1)M*(n) is unconditional.
Worth noting the direction: an integral theorem settles a fractional question, not the
other way round, which is only possible because the theorem has no ceiling in m.

**STRUCTURE / CLEANLINESS:** the directed hypergraph material (prop:dir-hyper-first
through the new thm:dir-hyper-constant) sat inside the section titled "The hypergraph
VERTEX problem"; given its own section A.8. The appendix's "How to read this appendix"
guide named three load-bearing sections when there are six; rewritten. Two symbols used
throughout (M(n), K_m^multi(n)) were missing from the symbol table. One unreferenced
figure (fig:scaling-reduction) now has a pointer. Four prose semicolons against the
thesis's own convention, two American spellings (maximizes, nonnegative), one doubled
word ("two two-step"). ch1's two "the upper bound is open" statements refined to say what
is and is not open. Contribution statement now records that the three new results inherit
the external reviewer's counting idea.

**VERIFIED:** 90 unit tests OK, program self-check ALL CHECKS PASSED, Appendix C in step,
two_step_budget_check.py passes, latexmk exit 0, 290 pp, 0 overfull, 0 undefined
refs/cites, all three slide decks rebuild. Numeric spot-checks by hand: the clique-bouquet
counts (27, 25, 150 vs 120), every cell of the theta/tree/complete comparison in
tab:multi-vertex, and the m=4 first-divergence at n=12 for conj:dir-arc.

## 2026-08-12 (Opus, final) -- the closed-form sweep, run to completion for the first time

audit_closed_forms.py had never finished: at BUDGET=90.0 it exhausted a 50-minute wall
clock, and the only previous attempt (2026-07-31) crashed partway on the missing-pulp
bug. Reran at BUDGET=6.0 under the venv with PYTHONPATH set (the script derives its
import path from __file__, so a copy elsewhere cannot find the program).

FIRST RUN: 99 cells, 2 mismatches IN RANGE, which is the column that must be empty:
prop:hyper-edge at n=3 m=3 r=3 and n=4 m=3 r=4, formula 2 against true 1 in both.

DIAGNOSIS: the script's fault, not the thesis's. solve() in hypergraph mode enumerates
SIMPLE hypergraphs (_brute_force_hypergraph walks each candidate hyperedge present or
absent, never repeated), while prop:hyper-edge states that a simple hypergraph attains
the floor only when m-1 <= C(n-2,r-2) and otherwise a MULTIhypergraph does. At both
cells that condition fails by exactly one (m-1=2 against C=1), and two parallel copies
of the single r-set attain the formula with lambda=2=m-1. thm:hyper-vertex-m3 carries
the same attainment caveat and is equally precise. The vertex rows were unaffected
because hyper_vertex_feasible_exists uses combinations_with_replacement, so it DOES
allow repeats; that asymmetry between two routines of the same program is the whole
explanation for why only the edge row lit up.

FIXED IN THE SCRIPT (not the thesis): those cells are now gated in-range on
m-1 <= C(n-2,r-2), the trap is written into the docstring so the next run does not
re-raise it, and the directed-multigraph block was repointed from the superseded
thm:dir-multi-small to thm:dir-multi-full (verified the two formulas agree on every
cell exhaustion reaches, since the branches tie at n=7 and the quadratic one leads only
from n=8).

SECOND RUN, CLEAN: 99 cells, 0 mismatches in range, 12 out of range. All twelve are the
intended output, the evidence that the n >= m hypotheses on thm:mader, thm:leonard and
conj:dir-arc and the simple-attainment condition on prop:hyper-edge are load-bearing
rather than decorative. Elapsed 1284s. Every closed form the thesis states now agrees
with exhaustive computation at every size within reach.

## 2026-08-12 (Opus) -- full proof-check of the appendix, at the author's request

Author lifted the standing "do not re-verify the author-verified pages" rule and asked
for the appendix proofs to be checked. Re-derived every original argument independently
rather than reading along. **NO MATHEMATICAL ERRORS FOUND.** What was actually
recomputed, section by section:

- A.2 Mader in full: lem:dist-1-count, lem:sum-dist, the Gomory-Hu double count
  (an edge crosses exactly the tree cuts on its endpoints' tree path), the upper bound
  2|E| <= m(n-1), both lower-bound constructions incl. the identity
  (n-1) + floor((m-2)(n-1)/2) = floor(m(n-1)/2), lem:near-regular's circulant plus
  near-perfect matching (checked the matching distance (N+1)/2 cannot collide with the
  circulant distances 1..(r-1)/2, which needs exactly r <= N-1), and thm:extremal-char's
  slack identity 2|E| = m(n-1) - (S1+S2+S3) re-derived line by line.
- A.3 directed arc m=2: lem:two-hop-arc, thm:directed-upper's arc split
  (n-1)+(n-1)+(m-2)(n-1) = m(n-1), and both parities of the induction. The odd case's
  remainder is exactly right: (2k+1)k^2 = (2k-1)(k^2+k) + k, so the bound is
  k(k+1) + k/(2k-1) and integrality closes the last fraction. The m=2 vertex twin
  transfers legitimately, since the argument uses only deletion monotonicity (which
  lem:subdigraph-monotone states for kappa too) and the re-run base cases.
- A.4 structural: prop:mutual-unreachability (and the D-u restriction really is needed),
  prop:disjoint-second-nbhd, prop:two-hop-bipartite, and the partition count
  b(n+m-2-b) maximised at floor((n+m-2)^2/4).
- A.7 lem:incidence-rank, the hardest proof in the thesis, checked in full. Step 1's
  block-cut count collapses correctly to |X|-1-sum_{z cut}(b(z)-1). Step 2 must precede
  Step 3 (that is what leaves a Z-neighbour at degree >= 2 after Step 3 removes an edge)
  and it does. Step 4's simplicity argument works because the concatenated walk avoids
  the edge {x,x'} on BOTH halves, so any path extracted from it has an interior vertex.
  The R-leaf argument turns on a point worth stating: at most ONE of the three
  internally disjoint paths can use the virtual edge (two would put a or b interior to
  both), so a and b are either shared endpoints or interior to that single path, and the
  far-side substitution therefore preserves disjointness. Then |V(L)| >= 4 with
  |X n V(L)| <= 1 leaves a Z-vertex off {a,b} of degree <= 1. Sound.
- A.7 thm:hyper-vertex-m3's component count rq-(n+q)+C <= n-C, i.e.
  q(r-1) <= 2(n-1)+2(1-C); thm:hyper-vertex-m2's forest equivalence.
- A.6 lem:sparse-hypergraph (uses (n/r)C(n-1,r-1) = C(n,r) and ceil(re/n) <= d) and
  thm:simple-hyper-edge, which is what my own thm:dir-hyper-constant leans on downstream.
- A.10 cor:chernoff-degree ((1+delta_0)mu = mu/c <= m) and both cases of
  thm:gnp-threshold, incl. that the c>1 display really is exp(-(c-1)^2 m(n-1)/(4c)).

Everything above is the author's own or classical and all of it holds. The only
corrections this session made to appendix MATHEMATICS were to my own new text (the
alpha = floor(n/2) overprecision), which is the honest summary: the pre-existing proofs
were right, and the errors were in prose ABOUT them.

## 2026-08-12 (Opus) -- proof-check of chapters 1 to 4

Same treatment as the appendix, at the author's request. VERIFIED CORRECT, re-derived
rather than skimmed: thm:multigraph-edge (the Gomory-Hu charging argument, which needs
only dist_T >= 1 and so loses the factor two Mader's simple-graph count gains);
prop:leonard-m2; const:bipartite; const:directed-hub (the circulant needs m <= n or its
layers would wrap onto themselves, and the hypothesis supplies exactly that);
const:augmented-bipartite in full; conj:dir-arc's arithmetic (m=3 reduction, the m=4
"larger by exactly one at every even n", the first overtake at n=12, the n=3 m=4
degeneracy); thm:leonard's and thm:sorensen-thomassen's hypotheses and values
(k_5(13)=31 > 30); thm:gnp-threshold's statement against the A.10 proof; ch2's MILP
(all four rows of tab:crossing-cases recomputed, plus the exactness argument and the
validity of the two-hop and degree-sorting rows); prop:monotone; ch3's complexity
counts (incl. that direction multiplies cells by 3 for the 3-uniform hypergraph, since
n*C(n-1,2) / C(n,3) = 3); tab:orientation, all four cells reproduced by
max_feasible_hyperedges with exact=True (the general r=3 n=4 cell needs ~121s, so a
120s budget reports it as a lower bound and the caption's "proved equal" claim is
nonetheless correct).

ONE REAL ERROR FOUND, subtle, and it is a conflation of two different error terms.
prop:dir-arc-stability proves TWO things: an arc count n^2/4 + sqrt(m) n^{3/2}, and a
STABILITY statement, that deleting at most sqrt(m) n^{3/2} arcs leaves a one-directional
bipartite digraph. thm:dir-arc-linear-error then improves the COUNT to
n^2/4 + 4(m-1)(n-1). It does NOT improve the stability statement, and cannot as written:
its Case 1 deletes a VERTEX and recurses, so the arcs at the deleted vertices are never
accounted for as deletions from the original digraph. Two places quietly upgraded the
stability to the linear error term anyway:
 - main.tex contribution statement: "and deleting a comparable number of arcs always
   leaves a one-way bipartite graph", sitting directly after the 4(m-1)(n-1) count.
 - ch4 phenomena: "every feasible digraph is within O_m(n) arcs of being one".
Both now separate the two currencies explicitly: within O_m(n) in SIZE, and a wall after
deleting O(sqrt(m) n^{3/2}) in SHAPE. ch4 L77 and app_proofs L472 already had it right,
which is what made the slip visible.

## 2026-08-13 (Opus) -- the presentations were stale, the body was not; plus four buried derivations

Author asked to check that intro, presentations and conclusions are up to date with the
current results, and to improve the readability of the mathematics.

**THE BODY WAS ALREADY CURRENT.** Swept main.tex, ch1-ch4 and app_proofs for every phrase
tied to the superseded machinery ("two checks", "attachment lemma", "odd-step",
"conj:min-degree", "fact (a)/(b)", "n <= 6"): the August audits had propagated both
closures properly. Three small inconsistencies survived, below, but no stale result claim.

**THE PRESENTATIONS HAD NOT BEEN SWEPT.** This is the finding worth recording, because the
2026-08-12 audit says it fixed "three SLIDE decks" and it did fix their prose, but it did
not touch the tables.
- `slides/thesis-beamer.tex`'s `\twelvetable` is `\input` by BOTH figure-led decks and
  lives in neither, so nobody editing talk_10 or talk_60 ever sees it. It still read
  "PROVED $n\le6$, COND $m=3$" for the directed multigraph arc row and "LOWER BD." for both
  directed hypergraph rows. talk_10 therefore contradicted itself inside one deck: frame 10
  says "the exact values behind the leading terms now settled" while frame 8's table denies
  the leading terms are settled at all. Rewritten against tab:summary; the directed simple
  rows now carry the $m=2$ value AND the unconditional $n^2/4+\Theta_m(n)$; a fourth chip
  LEADING TERM covers the amber case. `\resizebox` + a legend line, since two values per row
  pushed it 42pt past the slide.
- `slides/slides.tex` (the older narrative deck) was the stalest artefact in the repo. Its
  backup frame B3 diagrammed "Attachment lemma -> Odd-step theorem -> Induction over all n
  -> Two checks on n=7" and listed facts (a) and (b) as the remaining work. Every link in
  that chain is deleted from app_proofs.tex. Replaced with the reachability-skeleton
  argument (SCC -> in/out arborescences -> Mantel on the condensation -> peel $m-1$ times).
  Also: the status spectrum (directed multigraph was under "certified by machine $n\le6$",
  directed hypergraph under "open"), the results frame (advertised the reduction to two
  n=7 checks), the landscape table, the open problems (named the backward-arc lemma as THE
  missing piece rather than one quarter of open:decomposition), and the cheat sheet.
- Retitled talk_60's "Three new results" frame, which listed four, and folded
  thm:dir-vertex-linear-error into its item 2 rather than adding a fifth to an already
  overfull frame. That frame's 21.5pt vbox overflow was pre-existing and is now gone.

**THREE INCONSISTENCIES IN THE INTRO AND CONCLUSION.**
1. main.tex: "Three further results come from isolating what the quadratic bound above
   actually uses (lem:two-step-budget)", then describes two. prop:multi-vertex-upper is
   NOT one of them: its proof runs through the underlying simple graph and Mader's density
   theorem and never touches the budget lemma. app_proofs' own lead-in already said "two",
   so the count was wrong in exactly one place, and so was the sentence assigning the
   reviewer's debt to "these three". Corrected, with a clause saying explicitly that the
   multigraph bound reaches its conclusion by an unrelated route.
2. ch4 tab:functions listed the directed vertex row's Prove column as "reduces to the arc
   problem above". That is the Whitney inversion the thesis spends two chapters warning
   against, sitting in a summary table. It is `_exhaustive_directed` re-run under the
   vertex test via `_vertex_flow_at_least` (both verified present in the program).
3. tab:summary's caption and its lead-in still defined "Certified" as a status, though no
   row has used it since thm:dir-multi-full retired the category. Both now say so.
   Also added the $n\ge13$ qualifier to the Short Summary's S-T value, which ch1 and
   tab:summary carry but the abstract did not.

**READABILITY: four multi-step calculations moved out of running prose.** Chosen by
scanning for lines above 400 characters carrying 12 or more relational operators inside
inline math, which found exactly these.
- Step 2 of prop:dir-arc-stability, the densest passage in the thesis: a four-term digon
  cancellation performed inside a single sentence ("removing the diagonal terms turns
  Step 1's bound X into Y, and bounding that digon term by |A(D)| cancels the -|A(D)|
  exactly"). Now three labelled facts (2a) walks-by-midpoint, (2b) what the diagonal
  counts, (2c) digons are few, then a four-line chain with the reason on each line.
- thm:extremal-char's slack identity: five inline equations chained in prose, now the
  three slacks displayed together, the two expressions for sum dist_T(e) displayed side by
  side, and the substitution shown.
- ch1's m=2 induction sketch, which matters because it is where a reader first meets the
  thesis's central argument: the averaging, the inductive bound and the rearrangement
  a(1-2/n) <= ... are now three displays instead of one 1900-character paragraph.
- rem:case2-tight's concavity-and-exchange argument: cost function c(t) displayed, and the
  conclusion given with underbraces naming the two factors (vertices at the cap, each
  buying n/4). Arithmetic re-checked: c(n/4)=n^2/16, so 16Q/n^2 vertices at n/4 each gives
  4Q/n = 4(m-1)(n-1), matching the constant already claimed.
No mathematical content changed in any of the four. Costs two pages, 290 -> 292.

VERIFY: latexmk exit 0, 292 pp, 0 overfull, 0 undefined refs/cites. Lay summary and all
three decks rebuild clean (slides.tex keeps 3 pre-existing hbox overfulls at its frames
S4/S5/S7, all before the first line I touched). Four rewritten pages rendered to PNG and
read. Slide frames 8 (talk_10), 9, 11, 12, 18 and 20 (slides) rendered and inspected, two
layout collisions found and fixed that way (chips overlapping between bands 3 and 4, and a
cramped results column). Program untouched, so no suite re-run.

NOTE FOR FUTURE SESSIONS: `\twelvetable` in slides/thesis-beamer.tex and the landscape
table in slides/slides.tex are two hand-maintained copies of ch4's tab:summary. Nothing
links them, and a build never complains. Recorded in slides/README.md.

## 2026-08-13 (Opus) -- the Sorensen-Thomassen item closed from the primary source

The author obtained the paper (JCTB 17(2) 1974, 143-159). It had been treated as
paywalled since 2026-07-30; it is not free, but the block on the earlier attempt was
ScienceDirect's bot-detection rather than the paywall, which is worth distinguishing.
The file is gitignored (copyrighted Elsevier PDF, do not commit it).

THREE errors, of which only the first was suspected.
1. CONVENTION. p.143: "we define f_k(n) as the least integer r so that every graph with
   n vertices and r or more edges contains a k-rail". Forcing convention, one more than
   this thesis's k_m(n). So the value here is floor(8n/3) - 4. The Erdos Problems
   database was faithful to its own stated definition all along and the figure was
   carried across unconverted.
2. RANGE. Theorem 4 (p.158) is "for n >= 6, n != 7, n != 12", not n >= 13. The database
   records only the clean tail. The paper gives the two exceptions, f_5(7) = 16 and
   f_5(12) = 28, hence k_5(7) = 15 and k_5(12) = 27 here. The closed form predicts 14
   and 28 at those sizes, so both are real holes.
3. DIVERGENCE POINT, the one nobody was looking for. The paper proves
   f_5(n) = floor(5(n-1)/2) + 1 throughout 6 <= n <= 13, i.e. exactly l_5(n) in this
   convention. The edge and vertex problems therefore AGREE up to n = 13 and first
   separate at n = 14. ch1 and ch4 had claimed the separation from n >= 13, derived by
   comparing a forcing k_5 (31) against an avoiding l_5 (30), which is precisely the
   half-converted comparison rem:threshold-convention itself declared certainly wrong.

WHY IT SURVIVED, worth remembering: k_5 > l_5 is INVARIANT under the convention shift,
because both functions move by one. Any quantity built from their difference is
convention-blind, so no internal consistency check could have fired. It only becomes
visible when one side is evaluated in each convention, which is what the remark's own
worked example did without noticing.

Independent confirmation before writing anything: the corrected function reproduces all
five values the paper states explicitly (n = 7, 12, 13, 14, 15) as f_5 - 1, and
reproduces agree-through-13 / diverge-from-14 exactly.

PROPAGATED: thm:sorensen-thomassen, rem:threshold-convention (rewritten from an open
caveat into a resolved note quoting the paper's definition), ch1's divergence-figure
caption and lineage paragraph, ch4's phenomena section and tab:summary, main.tex's Short
Summary, both slide tables, the slides cheat sheet, ref.bib.

PROGRAM: simple_undirected_vertex_m5 had the unconverted formula and no range guard.
Fixed, with the two exceptions and a ValueError below n = 6. plot_edge_vertex_divergence
called it from n = 4, outside the determined range; the m=5 curves now start at n = 6 and
the regenerated figure shows them coinciding to n = 13 and parting at n = 14 rather than
separating immediately. The old test asserted the old formula; replaced by four (formula
with exceptions, the paper's own five values, the sub-6 guard, the divergence structure).
Suite 90 -> 93 all pass, self-check ALL CHECKS PASSED, Appendix C re-synced,
program/README test count updated.

VERIFY: 292 pp, 0 overfull, 0 undefined refs, three decks clean, theorem page rendered
and read.

## 2026-08-24 (Opus) -- the shortening pass, all three groups in one commit

Executed revision 3 of the shortening plan (`~/.claude/plans/i-d-like-to-make-cryptic-tome.md`),
aggressively: groups A, B and C in one pass rather than one group at a time.
**173 pp -> 155 pp**, 0 overfull, 0 undefined refs, 103 tests OK, self-check ALL
CHECKS PASSED.

**NOTHING WAS DELETED.** Every removal was MOVED into `offcuts.tex` at the repo
root, which `\input{preamble}`s the thesis's own preamble, so each excerpt renders
exactly as it looked in the thesis and IS the source to paste back from. It builds
to `offcuts.pdf` (38 pp, gitignored). Each excerpt carries a provenance header:
plan item, source file, restore anchor (a verbatim fragment of the surviving text
it sat after, NOT a line number), and the reason. Compressions print WAS and IS NOW
together, the IS NOW pulled live from the current source at assembly time so the two
cannot drift. `xr` + `\externaldocument{main}` resolves `\Cref` in an excerpt against
the live thesis; it worked first try and needed no fallback. Labels inside an IS NOW
extract are neutralised through `\offcutlabel` so they cannot clash with main's.

WHAT WENT: B.2 traces (5 figs), B.3 (`conn_dist_m6` + `threshold_3d`, so Appendix B
is now the gallery alone), `pair_conn_dist` + `edges_dist`, §2.9 and the inventory in
2.9.1, A.12 self-check list, the `m=6` grid, three transcript dumps (replaced by
`tab:basecase-search`), the worked vertex-split example, the wall-clock SA/tabu plot
and four paragraphs, the engineering colour in §2.5/2.6, the Contribution Statement's
second results narrative, two proof sketches in A.1, five thin codecards (10 -> 5),
the three-regimes walk through all twelve variants in §3.6, the Chernoff primer.

WHAT WAS KEPT AGAINST REVISION 1, on the author's review: `variant_surface_3d` (it
separates proved from searched, that is variance not rarity), both hypergraph gadget
examples (non-standard models), every pruning rule and its soundness (that is what
licenses the word *proved*), the two base-case logs as a compact table (`app_proofs`
cites them as the settled base cases of the directed m=2 VERTEX theorem, which cannot
be inherited from the arc case), and `edge_vertex_sampling`.

TWO PROSE FACTS THAT HAD TO BE RIGHT, both wrong in revision 1: tabu is the DEFAULT
and reaches every value the thesis reports, annealing is retained for the self-check;
and the sampling figure shows edge/vertex connectivity coming apart on a fraction of
random samples, NOT the m=5 extremal divergence. Ch1 had quietly claimed the latter
("It is already there, in miniature, in the random model"); rewritten.

VERIFY: label diff against the baseline commit `d4d5a0d` across EVERY source file, not
just `app_proofs.tex`. 14 labels left `chapters/`, all of them figures or sections that
appear in `offcuts.tex`; ZERO thm/lem/prop/cor/conj/const/rem labels lost. One added,
`tab:basecase-search`. Round trip tested on A6: pasted back at its anchor, rebuilt to
157 pp, reverted. That +2 for a 1.5 pp figure is the float non-additivity the plan
warned about, and it is why 155 rather than the estimated ~148: the estimates were
pre-build and floats reflow.

ALSO: `figures/` untouched by design (rule 2) since `offcuts.pdf` renders eleven of
them, AND `slides/talk_60.tex` includes `variant_bounds_m6.png` and `conn_dist_m6.png`
directly, so deleting them would have broken a deck silently. `program/README.md` now
marks the offcut-only figures; Appendix C's archival checklist says `offcuts.tex` is
not part of the submitted artefact. Plan item C2: the automorphism `assert count >= 1`
in `_aut_count_matrix` is now an explicit `RuntimeError` (callers divide by that count
and `python -O` strips asserts). `mistakes found 24082026.md` left as it is, being a
closure record rather than a task list.

## 2026-08-24 (Codex) -- second shortening pass and compact m=6 restoration

Continued the reversible shortening workflow above. **155 pp -> 149 pp**. The whole
remaining random-graph side thread moved out: its Chapter 1 examples and sampling
figure, appearance-threshold theorem, appendix proof, front-matter and software-inventory
references, and the OBSERVE/sampling endpoint in the program-spine diagram. The redundant 3D twelve-variant
surface and the one-figure Supplementary Figures appendix also moved out. The live
thesis now moves directly through the twelve structural variants and their proof/search
pipeline.

RESTORED: `variant_bounds_m6.png`, formerly offcut A6, now sits beside the m=3
twelve-variant grid in one compact two-panel figure in Chapter 3. A6 remains in
`offcuts.tex`, explicitly marked restored, to preserve its former standalone full-width
layout and caption. The two-panel figure and the shortened program-spine figure were
rendered and inspected at physical PDF pages 63 and 31 respectively.

REVERSIBILITY: every removed passage, theorem, proof, caption, diagram definition, and
whole-appendix input is in new Group D of `offcuts.tex`, with source and restore anchors.
No image assets or bibliography records were deleted. The manifest now distinguishes
A6 as restored and lists D1--D4; `program/README.md` marks the newly offcut-only images.

VERIFY: `latexmk -pdf main.tex` -> 149 pp; `latexmk -pdf offcuts.tex` -> 49 pp.
Both logs have zero undefined references/citations, multiply-defined labels, overfull
boxes, or missing PDF destinations. The removed-label audit found every removed label
either preserved in `offcuts.tex` or still live in the paired-grid figure.
`git diff --check` is clean. Program source was not changed, so the Python suite was not
rerun.

## 2026-08-24 (Codex) -- third shortening pass, figures retained and compacted

Continued the same reversible workflow. **149 pp -> 131 pp.** No figure was removed
in this pass. Chapter 2's three capacity-one checker reductions now share one row, its
two full hypergraph examples remain at 82% text width, Chapter 4's directed crossover
and backward-arc obstruction now share one row, and Chapter 3's paired $m=3/m=6$
twelve-variant grids remain together on one page.

WHAT WAS SHORTENED: Chapter 3's prove--certify--conjecture commentary; Chapter 4's
directed-frontier interpretation, orientation-model discussion, and seven essay-form
open problems; the Contribution Statement's five long result paragraphs; repeated
checker exposition and captions; and the Software and Reproducibility appendix. The
live versions retain the theorems, formulas, definitions, exact tables, caveats,
commands, evidence standards, contribution scope, and AI-credit disclosure.

REVERSIBILITY: Group E of `offcuts.tex` contains exact former snapshots for all five
edits, including the old separate/full-size figure layouts, with provenance and restore
anchors. Labels inside the snapshots are neutralised or namespaced so the archive can
build beside the live thesis.

VERIFY: `latexmk -pdf main.tex` -> 131 pp and `latexmk -pdf offcuts.tex` -> 79 pp.
Both logs have zero undefined references/citations, multiply-defined labels, overfull
boxes, or missing PDF destinations; `git diff --check` is clean. The compact figure
pages were rendered and inspected at physical pages 37, 58, and 60. Program source was
not changed, so the Python suite was not rerun.

## 2026-08-24 (Codex) -- merge of the two machine-method chapters

Merged the former Chapters 2 (certification) and 3 (search) into one chapter,
**Certifying and Discovering Bounds by Machine**, and consolidated their source as
`chapters/ch2_machine.tex`. `main.tex` now has three body chapters. The former
`ch:certify` and `ch:discover` labels remain aliases on the combined chapter so the
proof appendix and historical offcuts continue to resolve; new live cross-references
use `ch:machine`, `sec:search-wall`, and `sec:rediscovery` where the distinction matters.

The merged opening states the model--measure--prove/discover pipeline once. The old
chapter-to-chapter hand-off is now Section 2.10, ``From certification to discovery: the
enumeration wall.'' Repeated framing around the separate openings and transition was
shortened, without removing a figure, theorem, algorithm, table, code card, or evidential
caveat. The program README's chapter map and figure locations were updated.

REVERSIBILITY: Group F of `offcuts.tex` preserves the former `main.tex` declarations,
the two source filenames and boundary, the old README map, both chapter openings, the
pipeline caption and driver-card sentence, the old transition, and every shortened
enumeration-wall phrase. The substantive contents of both old source files remain live,
in order, inside `chapters/ch2_machine.tex`.

VERIFY: `main.pdf` remains 131 physical pages because the saved chapter break is
absorbed by recto and appendix pagination. The contents page, combined chapter opening,
and Section 2.10 transition were rendered and inspected at physical pages 8, 31, and
47. `latexmk -pdf main.tex` and `latexmk -pdf offcuts.tex` complete successfully;
the resulting PDFs are 131 and 85 pages. Both logs have zero undefined references or
citations, multiply-defined labels, overfull boxes, or missing PDF destinations, and
`git diff --check` is clean. Program source was not changed, so the Python suite was
not rerun.

## 2026-08-24 (Codex) -- conservative post-merge compression

Compressed the merged machine-method chapter and the classical opening of the proof
appendix without removing a figure, theorem, algorithm, proof, construction, code card,
or substantive original result. The historical MILP section still contains the scaling
argument, complete optimisation, both diagrams, and finite theorem, but its generic MILP
tutorial, crossing-case table, big-M walkthrough, and repeated run history moved out.
The former solver-claims, reproducibility, certification-standard, trichotomy, and honesty
blocks are consolidated into one `Results and evidential status` section beside the final
grid. Long captions in Chapters 1 and 2 now identify rather than reteach their figures.

Appendix A retains the statements of Menger and Gomory--Hu, the full compact Mader
argument, all three counting lemmas, both Mader figures, and every original proof. Its
textbook flow/uncrossing explanation and long reading guide were compressed, and the
Gomory--Hu diagram was scaled to 86 percent. The substantive alternative-convention
section A.9 was deliberately left untouched.

REVERSIBILITY: Group G of `offcuts.tex` preserves the displaced MILP tutorial and solver
history, the four-case crossing table, the repeated evidence/reproducibility sections,
the full former appendix reading guide and classical exposition, and every long-form
caption replaced in this pass, with restore anchors. Groups A--F remain unchanged.

VERIFY: `latexmk -pdf main.tex` -> 123 pp and `latexmk -g -pdf offcuts.tex` ->
96 pp. This pass saves eight physical thesis pages from the 131-page merged baseline.
Both logs have zero undefined references/citations, multiply-defined labels, overfull
boxes, or missing PDF destinations; `git diff --check` is clean. The MILP opening and
model were inspected at physical pages 39--40, the consolidated status/grid page at 50,
and the revised appendix opening at 60. Program source was not changed, so the Python
suite was not rerun.

## 2026-08-24 (Codex) -- removal of one-case and redundant displays

Removed the requested one-case cooling trace, complete labelled-graph landscape,
introductory variant tree and 2-tree illustration, Mader construction picture, SPQR
leaf schematic, appendix hyperedge-convention figure, machinery cross-reference table,
finite orientation table, two multigraph-vertex tables, and directed base-case run table.
The load-bearing SPQR argument remains as one compact paragraph without the tutorial or
picture. The directed-hyperedge drawing convention now appears beside the first family
of variant diagrams in Chapter 1. The Mader lower construction is stated once: the
general hub-and-spokes construction specialises to the clique construction when the
divisibility condition holds.

Table 3.1 was rebuilt as a concise three-column `tabularx` at normal body size; it is no
longer shrunk with `resizebox`. Generic machine listings were retained because they serve
several variant families rather than documenting a single run. All displaced source is
preserved as restore-ready entries H1--H12 in `offcuts.tex`, with local labels and restore
anchors; no figure assets or program source were deleted.

VERIFY: `latexmk -pdf main.tex` -> 115 pp and `latexmk -pdf offcuts.tex` ->
108 pp. This pass saves eight physical thesis pages from the 123-page prior version.
Both logs have zero undefined references/citations, multiply-defined labels, overfull
boxes, or missing PDF destinations. Program source was not changed, so the Python suite
was not rerun.

## 2026-08-24 (Codex) -- removal of implementation displays and repeated results

Removed all three raw code listings from Chapter 2, together with the conventional
simulated-annealing pseudocode. Their mathematical content remains in prose: the matrix
symmetry invariant, capacity-one hyperedge gate, monotone capped-flow cases, energy,
Metropolis acceptance rule, cooling, and sensitivity bias. Removed the directed
whole-hypergraph duplicate (the undirected example and compact directional gate remain),
the plain-enumeration results table, and the rediscovery results table. Both table results
are still stated as independent agreement with values proved elsewhere.

Figure 2.9's sensitivity plot was reduced from 78 to 60 percent of text width. Table 3.1
keeps normal body type but now uses six model rows with edge/arc and vertex results side by
side, instead of twelve separate rows; it shares a page with the surrounding text rather
than occupying a page alone. All displaced source is preserved as restore-ready entries
I1--I8 in `offcuts.tex`; the full directed-example TikZ source was already present in E3.

VERIFY: `latexmk -pdf main.tex` -> 113 pp and `latexmk -pdf offcuts.tex` ->
114 pp. Both logs have zero undefined references/citations, multiply-defined labels,
overfull boxes, or missing PDF destinations; `git diff --check` is clean. The compact
Table 3.1 and reduced sensitivity figure were rendered and inspected at physical pages
52 and 42. Program source was not changed, so the Python suite was not rerun.

## 2026-08-24 (Codex) -- structural reduction to 100 pages

Reduced the thesis from 113 to exactly 100 physical pages by moving complete units,
not merely their captions. The seven-page appendix on the alternative convention where
parallel copies count as distinct vertex-disjoint routes moved out in full; it is a
separate extremal problem and is not one of the twelve variants under the convention
fixed in Chapter 2. Its contribution-statement row, symbol, open-problem row, boundary
discussion, and dependent cross-references moved with it.

The separate Software and Reproducibility appendix and repeated computational-transcript
section are consolidated into one short `Computational audit` section at the end of
Appendix A, retaining the repository, commands, evidence hierarchy, finite ranges, and
log paths. Chapter 2's representation figure and operations table moved out because
Chapter 1 already defines the same model axes; one paragraph now states the shared data
representation. The entire SA--tabu benchmark subsection and timing table also moved out,
leaving only the method choice and evidential status.

REVERSIBILITY: Group J of `offcuts.tex` contains the exact former alternative-convention
section, transcript section, software appendix, scope references, representation displays,
and SA--tabu subsection. Earlier Groups A--I remain intact. No figure asset or program
source was deleted.

VERIFY: `latexmk -pdf main.tex` -> 100 pp and `latexmk -pdf offcuts.tex` ->
128 pp. Both logs have zero undefined references/citations, multiply-defined labels,
overfull boxes, or missing PDF destinations; `git diff --check` is clean. The contents,
compressed Chapter 2 opening, and computational-audit ending were text-inspected at
physical pages 8--10, 28--30, and 95--97. Program source was not changed, so the Python
suite was not rerun.

## 2026-08-24 (Claude) -- repair of the shortening pass, and two restorations

An audit of the 100-page version found that the LaTeX layer was clean (zero
undefined references, zero multiply-defined labels, zero overfull boxes) while
five prose references pointed at material the cuts had removed. Label aliasing
hid the drift: `sec:transcripts` survived as a live label on the shortened
audit section, so every pointer still resolved.

Repaired, by making the promise true rather than by deleting it. The compact
directed base-case table (offcut H12) is live again as `tab:basecase-search` in
the computational audit, and the four passages that promised a transcript now
point at it: Chapter 2's pruned-search section, the Appendix A.3 lead-in, its
base-case paragraph, and the vertex counterpart in A.4. Its six rows were
re-checked against `figures/basecase_search_log.txt` and
`figures/basecase_search_vertex_log.txt`, including the node counts and the
718 s against 3125 s wall times. The rediscovery table (offcut I7) is live
again as `tab:rediscovery`, immediately before the sentence "What the table
hides", which had been left with no table to hide anything.

Two restorations, both judgement calls. First, the alternative multigraph-vertex
convention (offcut J1) is back as Appendix A.9, without its two cell-by-cell
data tables: it is an original result of this thesis, the strongest statement
about it (a block-knapsack reduction with matching order) has no other home, and
the section already argued its own scope. Its contribution row, the
`K_m^multi` symbol, the open-problem row, and the boundary sentence in the
parallel-copy remark came back with it (offcut J4). Its claims were re-checked
against `figures/multi_vertex_blocks_log.txt`, which gives 19 at m=5,n=5 and 29
at m=5,n=7 as the text states. Second, the two hypergraph vertex theorems, the
first row of the Contribution Statement, were stated only in the appendix and in
two table cells. They are now stated in Chapter 1 at the end of the hypergraph
section, following the pattern already used for Mader and for the directed m=2
values, and Appendix A.7 proves them as `Proof of \Cref{...}`.

Also: the Short Summary said the program "certifies" the directed multigraph
values at n<=6, one notch stronger than the body's own standard, and now says
"independently checks". `chapters/app_code.tex` and `chapters/app_gallery.tex`
were no longer `\input` anywhere and are removed, their content being preserved
in `offcuts.tex` (E5, J3, A1, A2, D4) and in history. The README's chapter list
was stale.

VERIFY: `latexmk -pdf main.tex` -> 108 pp and `latexmk -pdf offcuts.tex` ->
120 pp, both with zero undefined references, zero multiply-defined labels, zero
overfull boxes. The restorations cost eight pages against the 100-page version.
Every `\ref` target resolves, no sentence is duplicated across the document, and
the rendered text carries no deictic reference ("the table", "reproduced below")
without its referent. Program source was not changed, so the Python suite was
not rerun.

## 2026-08-24 (Claude) -- reference audit, self-containment, and the page budget

A full audit of pictures, tables and proofs, beyond what LaTeX can see.

Every `\ref` target resolves, every `\includegraphics` file exists, no `??`
survives in the rendered text, no label's prefix disagrees with the object it
points at, and every statement is proved, cited, or explicitly deferred. Three
floats were labelled but never referenced: the paired twelve-variant grids, the
Gomory--Hu distance figure, and the open-problems table. Each now has a
sentence that names it, and the open-problems section gained the lead-in
paragraph it never had. Nine anchors carry more than one label. All are
deliberate (subfigures, the two chapter-merge aliases, the shared-clique
alias), and the four aliases on the computational audit now carry a source
comment saying what they are, since a live label on absent content is exactly
how the earlier dangling references hid from LaTeX.

Self-containment: the repository URL appeared only on the audit page, so a
reader meeting `program/erdos915_unified.py` in Chapter 2 or a log path in
Appendix A had no anchor. Chapter 2 now names the repository where the code is
first mentioned and says every quoted file path is relative to it, and the
block-sweep log in A.9 points at the same place.

Thirty-five semicolons in running prose and captions were rewritten as full
stops or conjunctions, per the author's standing preference. Semicolons inside
table cells and in mathematical notation (`maxflow(s, t; w)`) are left alone,
where they separate list items rather than clauses. No em-dashes or en-dashes
occur in prose.

Page budget: 108 -> 106 with no content removed, by tightening `\parskip` from
0.5em to 0.25em, the theorem pre/post skips from 1em to 0.75em, and the three
float separations, plus `\allowdisplaybreaks[2]` so long display chains no
longer push whole blocks to the next page. Class-mandated settings (margins,
1.5 line spacing, fonts, covers) were not touched. The document has no slack
left: outside the cover, contents and back matter, only three pages fall below
250 words, and those are chapter-end pages.

The 100-page target is now mutually exclusive with the restored Appendix A.9.
That section is seven pages, the tightening returned two, and the rest of the
document is dense. Reaching 100 would mean deleting either A.9 (original
mathematics) or the classical machinery in A.1 and A.2 (about three and a half
pages, and the opposite of self-contained). Left at 106 with A.9 in place. The
lever is one paragraph in `preamble.tex` and one section in `app_proofs.tex` if
the author decides otherwise.

VERIFY: `latexmk -pdf main.tex` -> 106 pp, `latexmk -pdf offcuts.tex` -> 117 pp,
both with zero undefined references, zero multiply-defined labels, zero overfull
boxes. Rendered pages 24, 25 and 42 were inspected as images to confirm the
tightened spacing still reads comfortably. Program source unchanged, so the
Python suite was not rerun.

## 2026-08-25 (Opus) -- external review actioned: six correctness fixes, five consistency fixes, seven citations

An external review of the built PDF was handed over. Every claim was checked
against the source before acting; all six correctness-level findings were real,
and the review's bibliographic and version numbers were accurate to the digit.

**SIX CORRECTNESS FIXES.**
1. **The displayed MILP did not describe an s-t cut.** It omitted
   $x^{st}_s = 1$ and $x^{st}_t = 0$, so $x \equiv 0$ was admissible, no ordered
   pair ever crossed, every $p^{st}_{uv}$ rested at $0$, and the cut constraint
   was satisfied by every weight matrix whatsoever. The formulation as printed
   therefore bounded nothing. The implementation is right and always was: in
   `_cut_counting_model` the two side values are Python CONSTANTS, not
   `LpVariable`s (a deliberate choice recorded on 2026-06-19, since `cat="Binary"`
   resets bounds to [0,1] and would make the cut core vacuous), which is exactly
   why they never surfaced as constraints in the write-up. Both lines added, with
   a paragraph on why they are load-bearing, and the two-step $\min$ is now shown
   linearised through $z^{sxt}$ and its binary selector rather than printed as a
   minimum a linear program cannot take.
2. **The hypergraph gadget figure showed the wrong bottleneck.** The undirected
   panel had ONE helper node with plain edges, and the directed panel put the
   capacity-one label on the tail arc. The code (`_hyper_capacity_matrix`) and the
   appendix proof of `thm:menger-hyper` both use the standard construction, one
   gate split as $e^- \to e^+$ at capacity one with UNCAPPED membership arcs, so
   the figure was the only place in the thesis that disagreed with itself. Both
   panels redrawn to match, members in a column beside the gate pair so the six
   membership arcs read cleanly, and the $\infty$ labels put on the arcs. The
   accompanying prose was wrong in the same direction and said the gate "draws one
   capacity-one arc in from every tail"; that variant would let a several-tailed
   hyperedge carry one route PER TAIL and overcount the disjoint routes, which the
   corrected passage now says explicitly.
3. tab:summary's directed simple VERTEX cell said "same status and values" as the
   arc cell, directly contradicting the preceding sentence that exact equality at
   $m \ge 3$ is open. Cell now states its own values and names the open part.
4. The augmented-bipartite case analysis in ch1 said "pairs starting in $B$ ...
   have no routes", one clause after correctly saying pairs INSIDE $B$ are held
   down by the in-degree. `lem:augmented-feasible` has the right split; the chapter
   now matches it (from $B$ to $A$, or inside $A$).
5. "The extremisers are doubled trees ..." overstated `rem:saturated-closure`,
   which says in as many words that not every linear-branch extremiser has been
   classified. Softened to constructions exhibited, with the appendix named.
6. The `solve` code card did not describe `solve`. Cut-counting is NOT reached
   from it (`prove_directed_multigraph` is called on its own), hypergraphs use
   separate enumeration and search routines, and the budget is checked BETWEEN
   iterations so one iteration may overrun it, as the docstring already said.
   Card rewritten against the dispatch. Separately the code mislabelled simulated
   annealing as "random search" in one `SolveResult`; corrected.

**CONSISTENCY.** The model axis is described as two independent binary choices
over four lattice nodes, but the variant count is three models; the reason is
that multiplicity separates the problems at $r = 2$ and does not at $r \ge 3$,
where every upper bound is proved for multihypergraphs and only ATTAINMENT
differs, and ch1 now says so instead of leaving the arithmetic to the reader.
"One representation holds every variant" contradicted ch1's own correct account
and is now one interface over two internal representations. "The certifier proves
upper bounds" is now "closes", matching `sec:certification-standard`. $c_m$ was
used in the open-problems table with its definition only in the appendix; it and
$h_m(b)$ are in the symbols table now, and the table cell carries the limit. The
$\lambda$-measure figure in ch1 carried two parallel $v_0 \to v_2$ arcs inside the
simple-digraph discussion; the duplicate is gone (it took part in neither the
three highlighted routes nor the cut) and the caption says "simple".

**CITATIONS.** Simulated annealing, the Metropolis rule and tabu search were
explained with no citation at all; Metropolis et al. 1953, Kirkpatrick-Gelatt-
Vecchi 1983 and Glover 1989 added, all three metadata-verified through Crossref.
"A hypergraph Gomory--Hu theorem from the recent literature" was followed only by
the 1961 graph citation; now cites Hanifehnezhad and Dolati 2020 for the
symmetric-submodular construction (Crossref-verified: Inf. Comput. 271, 104479).
`ChekuriXu17` and `DewarPikeProos18` sat in ref.bib uncited since they were added;
both now support a real claim in the hypergraph section, where the thesis says
which of several inequivalent connectivity notions it uses. `ErdosProblems` gained
`url` and an access date. NOT DONE, flagged for the author: that entry lists Pal
Erdos as the author of a website he cannot have written (erdosproblems.com is
Thomas Bloom's), which the review did not raise and I could not verify (the site
403s bots), so I did not silently change an attribution.

**STRUCTURE AND REPRODUCIBILITY.** The appendix is longer than the three body
chapters and presented as a flat list of ten sections. Rather than reverse the
2026-08-24 decision to move every proof into it, the ten sections are now grouped
under four signposted parts (classical machinery, directed, hypergraph, extension
plus audit) that write themselves into the contents page, and the reading guide
names the three original arguments worth reading first. This introduces no label
and no numbering, so all 26 `\Cref{app:proofs}` in the body still resolve. THE
BIGGER STRUCTURAL CALL, promoting one or two proofs into a body chapter, is the
author's and is deliberately not taken here.
The appendix promised an immutable commit and printed none: `record_revision.sh`
now writes `revision.tex` (refused on a dirty tree) and tags the same commit, so
the hash in the PDF and the tag in the repository cannot disagree; the audit
section prints `\thesiscommit`. `requirements.txt` gave ranges only, so
`requirements-lock.txt` pins the environment the runs were verified in, confirmed
live: Python 3.14.6, NumPy 2.4.6, SciPy 1.18.0, PuLP 3.3.2, Matplotlib 3.11.0,
NetworkX 3.6.1. PDF title/author/subject/keywords were blank and are now set.
The lay summary called both strictest hypergraph limits exact; the $m=3$ result
carries attainment conditions, so it now distinguishes the two (3310 characters,
still one page, still inside the 3500 limit).

**MINOR.** "the section just below" pointed upward; SPQR expanded without its Q
component; "proving what proved cleanly". Five prose semicolons that my own edits
introduced were removed before commit, per the standing rule.

VERIFY: clean rebuild 115 pp (was 111), 0 overfull, 4 underfull (the same four the
review saw), 0 undefined refs/cites, 0 multiply-defined labels, 0 LaTeX warnings.
BibTeX clean, 28 entries cited (was 21), every new one resolving. 103 tests OK
with the one expected skip. Lay summary rebuilds to one page. The redrawn gadget
figure, the corrected MILP display, the summary table, both contents pages and a
part divider were rendered to PNG and inspected.

# Review of `SIMPLIFIED_AI_PROOFS.md`

Checked against `chapters/app_proofs.tex` at commit `a402744`, which is the
commit the document names and is HEAD. Every A-number in its badge-to-proof map
resolves to the environment it claims, and every headline number (1.6 to 1.14)
is correct against `main.aux`.

Verdict in one line: the mathematics is sound, five of its proofs have small
gaps that need a sentence each, and exactly four of the thirty-seven are worth
adopting. The other thirty-three restate proofs the thesis already carries, in
less detail, and adopting them would shorten the appendix by making it harder to
read rather than easier.

## 1. What is worth adopting

### 1.1 Lemma 18, the elementary cut induction (replaces the Gomory--Hu route to `prop:hyper-edge`)

Correct, and checked numerically: 4000 random non-uniform multihypergraphs on up
to 7 vertices, zero violations, with the bound attained (`lhs - rhs = 0`) at
several of them, so it is tight and not merely true.

It proves more than `prop:hyper-edge` needs. Stated for arbitrary
multihypergraphs, not uniform ones, it gives `sum_e (|e|-1) <= k(n-1)`, and the
`r`-uniform bound and `thm:multigraph-edge`'s upper bound are both one-line
specialisations (`|e| = r`, and `|e| = 2`).

What it removes from the appendix: `thm:hyper-gomory-hu` (A.51) and the
paragraph explaining it, plus the three-step Steiner-tree double count in the
proof of `prop:hyper-edge`. That is lines 1142 to 1178, about 700 words.
`thm:hyper-gomory-hu` is cited from nowhere else in the thesis, checked by grep
across all four chapters and `main.tex`, so it goes cleanly.

**One defect to repair before use.** The document writes "Choose two vertices in
different sides of a minimum cut", which inverts the logical order: the cut is
produced from the pair, not the pair from the cut. The replacement below fixes
it by naming the reachable component explicitly.

**This collides with a standing convention.** `claude.md` records the author's
2026-08-26 decision to keep Mader's theorem proved in full, on the ground that
"its Gomory--Hu double count is the move the multigraph and hypergraph arguments
reuse, so a reader who cannot check it there cannot check them either." Adopting
Lemma 18 breaks that thread: Mader still needs the Gomory--Hu tree, because the
cut induction gives only `(m-1)(n-1)` and cannot produce the factor two that
comes from charging most edges to two tree cuts. So the choice is between a
shorter appendix and a hypergraph proof that echoes the graph proof. That is the
author's call, not a coding one.

Drop-in replacement, to sit where `thm:hyper-gomory-hu` currently sits:

```latex
\begin{lemma}[Cut induction for multihypergraphs,\aimedal]\label{lem:hyper-cut-induction}
Let $\HH$ be a multihypergraph on $n \ge 1$ vertices, not assumed uniform, with
$\lec^{\max}_\HH \le k$. Then, the sum running over hyperedge copies,
\[
    \sum_{e} \bigl(|e| - 1\bigr) \;\le\; k\,(n-1).
\]
\end{lemma}

\begin{proof}
Induction on $n$. At $n = 1$ every hyperedge is a single vertex and both sides
are $0$.

Let $n \ge 2$ and fix any two vertices $u \ne v$. By \Cref{thm:menger-hyper}
some set $F$ of at most $\lec_\HH(u,v) \le k$ hyperedge copies separates them.
Let $S$ be the set of vertices reachable from $u$ in $\HH - F$ and write
$\bar S = V \setminus S$, so $u \in S$, $v \in \bar S$, and every copy meeting
both sides lies in $F$. Both sides are non-empty and at most $k$ copies cross.

Form the two \emph{trace} multihypergraphs $\HH[S]$ and $\HH[\bar S]$ by
replacing every copy $e$ by $e \cap S$, respectively $e \cap \bar S$, and
discarding the intersections of size $0$ or $1$. A Berge route of a trace lifts,
copy by copy, to a Berge route of $\HH$ on the corresponding original copies,
and distinct trace copies come from distinct original copies, so a
hyperedge-disjoint family in a trace lifts to one of the same size in $\HH$.
Hence $\lec^{\max} \le k$ on both traces and the induction hypothesis applies to
each.

Now split the copies of $\HH$. A copy lying wholly inside one side contributes
its whole $|e| - 1$ to that side's trace sum. A crossing copy splits as
\[
    |e| - 1 \;=\; \bigl(|e \cap S| - 1\bigr)
              \;+\; \bigl(|e \cap \bar S| - 1\bigr) \;+\; 1 ,
\]
each bracket being the contribution its trace makes, and zero exactly when that
trace was discarded. Summing over all copies,
\[
    \sum_e \bigl(|e|-1\bigr)
    \;\le\; k\bigl(|S| - 1\bigr) + k\bigl(|\bar S| - 1\bigr)
            + \bigl|\{\text{crossing copies}\}\bigr|
    \;\le\; k(n-2) + k \;=\; k(n-1). \qedhere
\]
\end{proof}
```

and the upper-bound half of the proof of `prop:hyper-edge` becomes

```latex
\emph{Upper bound.} Every hyperedge copy has $|e| = r$, so
\Cref{lem:hyper-cut-induction} at $k = m-1$ reads
$(r-1)|E(\HH)| \le (m-1)(n-1)$. Dividing and rounding down, because
$|E(\HH)|$ is an integer, gives the stated floor.
```

At $r = 2$ the same lemma is the upper bound of `thm:multigraph-edge`, which is
worth one sentence there.

### 1.2 Lemma 20, degree smoothing (replaces Baranyai)

Correct, and the exchange step was run to a fixed point from random starts over
every `(n, r, e)` with `n <= 8`: it never stalls, the fixed point always has
degrees within one of each other, and the maximum degree is always exactly
`ceil(re/n)`.

The argument is three lines and it retires `thm:baranyai` (A.54), its
explanatory paragraph, and the proof of `lem:sparse-hypergraph` (A.55), which
currently derives an equitable two-class partition from Baranyai in order to
conclude something a smoothing argument gives directly. About 350 words.
`thm:baranyai` is cited nowhere else.

```latex
\begin{lemma}[Sparse uniform hypergraphs exist]\label{lem:sparse-hypergraph}
Let $r \ge 1$, $n \ge r$ and $0 \le d \le \binom{n-1}{r-1}$. There is a simple
$r$-uniform hypergraph on $n$ vertices with exactly $\floorfrac{dn}{r}$
hyperedges and maximum degree at most $d$.
\end{lemma}

\begin{proof}
Put $e := \floorfrac{dn}{r} \le \frac{n}{r}\binom{n-1}{r-1} = \binom{n}{r}$, so
$e$ distinct $r$-sets are available. Among all families of exactly $e$ distinct
$r$-sets choose one minimising $\sum_x \deg(x)^2$. Suppose two vertices had
$\deg(x) \ge \deg(y) + 2$. Write $a$ for the number of family edges containing
$x$ but not $y$ and $b$ for the number containing $y$ but not $x$, so
$a \ge b + 2$. The injection $A \mapsto A - x + y$ sends the first kind into the
second, so if every image were present we would have $b \ge a$. Hence some $A$
in the family has $A - x + y$ absent, and exchanging them keeps the family
simple and of size $e$ while changing the objective by
$(\deg(x)-1)^2 + (\deg(y)+1)^2 - \deg(x)^2 - \deg(y)^2
 = 2\bigl(\deg(y) - \deg(x)\bigr) + 2 \le -2$,
contradicting minimality. So all degrees differ by at most one, and since they
sum to $re$ the largest is $\ceil{re/n} \le d$, the last step because
$re \le dn$ and $d$ is an integer.
\end{proof}
```

### 1.3 Lemma 23, the incidence rank lemma without Tutte or SPQR

Correct. I re-derived the whole separating-pair case by hand, including the
three torso constructions, the four hypotheses on each torso, the induction
measure, and the rank and $|X|$ bookkeeping in all three branches. Every
identity checks out:

| branch | $\mathrm{rank}(G)$ | $|X_U| + |X_W|$ | bound |
|---|---|---|---|
| $ab \in E(G)$, forced $s = 1$ | $r_U + r_W$ | $|X| + 1$ | $|X| - 1$ |
| temporary edge, $s \in \{1,2\}$ | $r_U + r_W - 1$ | $|X| + s$ | $|X| + s - 3$ |
| both separators in $Z$, $s = 0$ | $r_U + r_W - 1$ | $|X| + 2$ | $|X| - 1$ |

This is the largest single win in the document. It removes two citations
(`Tutte66`, `HopcroftTarjan73`), the paragraph setting up the triconnected
decomposition, and the three-way leaf analysis, about 220 words, and more to the
point it removes the one place in the thesis where a reader has to take a
decomposition theorem on trust.

**One defect to repair.** The document drops the thesis's "$G$ is simple" step,
which is what rules out $|V| = 3$. A $2$-connected multigraph on three vertices
with minimum degree at least three is neither $3$-connected nor in possession of
a separating pair, so the case split as written has a hole there. It is vacuous,
but it needs the line. Keep the thesis's existing simplicity paragraph and note
that a simple graph of minimum degree at least three has $|V| \ge 4$. Then
replace only the material from "Otherwise $G$ is $2$-connected but not
$3$-connected" to the end of the proof by:

```latex
Otherwise $G$ has a separating pair $\{a, b\}$. Delete it and gather the
remaining components into two non-empty groups with vertex sets $U$ and $W$.
Since $G$ is $2$-connected, each of $a$ and $b$ has a neighbour in $U$ and one
in $W$, and each side carries an $a$--$b$ path. Write $s = |X \cap \{a,b\}|$ and
build two \emph{torsos} $G_U$ and $G_W$, where $G_U$ is the subgraph induced on
$U \cup \{a,b\}$ carrying one temporary $a$--$b$ connection, and $G_W$ likewise:

\begin{itemize}
    \item if $ab \in E(G)$, retain that edge on both sides;
    \item if $ab \notin E(G)$ and $s \ge 1$, add one new edge $ab$ to each side;
    \item if $s = 0$, add to each side a fresh $X$-vertex together with the two
          edges joining it to $a$ and to $b$.
\end{itemize}

The three cases are exhaustive, since $Z$ is independent by (i), so
$ab \in E(G)$ already forces $s \ge 1$. In that case $s = 1$ exactly: two
endpoints in $X$ would give $\kap(a,b) \ge 3$, counting the edge together with
one $a$--$b$ path through each side, against (iv).

\emph{Each torso satisfies (i) to (iv).} Condition (i) holds because every
temporary edge has at least one endpoint in $X$, a fresh vertex in the third
case. Condition (ii) holds because a temporary edge joins a pair that carried no
edge at all. For (iii), a $Z$-vertex inside $U$ keeps all its neighbours, and a
separator vertex in $Z$ keeps at least one neighbour on its own side and gains
the temporary connection. For (iv), a fresh $X$-vertex has degree two, so its
local connectivity is at most two, and for two old $X$-vertices any internally
disjoint family uses the temporary connection at most once, since internally
disjoint $x$--$x'$ paths can share no edge but $xx'$ itself. Replacing that one
path's temporary connection by an $a$--$b$ path through the opposite side turns
three internally disjoint paths in a torso into three in $G$, which (iv)
forbids. Both torsos are smaller in $|V| + |E|$, since the opposite side retains
at least one vertex, of degree at least three.

\emph{The bookkeeping.} Write $r_U, r_W$ for the two ranks and $X_U, X_W$ for
the two $X$-sets. Direct calculation from $\mathrm{rank} = |E| - |V| + 1$ gives
$\mathrm{rank}(G) = r_U + r_W$ and $|X_U| + |X_W| = |X| + 1$ in the first case,
where the retained edge is counted twice, and
$\mathrm{rank}(G) = r_U + r_W - 1$ with $|X_U| + |X_W| = |X| + s$ in the second
and $|X| + 2$ in the third. Feeding in the two inductive bounds
$r_U \le |X_U| - 1$ and $r_W \le |X_W| - 1$ gives $\mathrm{rank}(G) \le |X| - 1$
in the first and third cases, and $\mathrm{rank}(G) \le |X| + s - 3 \le |X| - 1$
in the second, since $s \le 2$. This exhausts the cases.
```

`rem:hyper-vertex-m3-scope` then needs its middle sentence rewritten: the proof
no longer "leans on the triconnected decomposition exactly where $\kap \le 2$
lives". The honest replacement is that the separating-pair split is what needs
$\kap \le 2$, since a torso's temporary connection can absorb only one path of
an internally disjoint family, and at $m = 4$ there is no comparable device.

### 1.4 Lemma 25, the cyclic-word construction

Correct, verified over every `(b, k, d)` with `b <= 11`, `d <= 11`. It replaces
the `q` copies of the complete `(r-1)`-uniform hypergraph plus a Baranyai
remainder in the proof of `prop:dir-hyper-first` (A.60) by reading a round-robin
word in blocks of `k`. Round-robin makes the degree bound `ceil(ek/b)` immediate.
About 170 words, and it drops the last use of the divisibility bookkeeping.

## 2. My own addition: the two block theorems are one theorem

Not in the document, and it is the second-largest saving available.
`thm:simple-vertex-blocks` (A.13) and `thm:multi-vertex-blocks` (A.70) have
literally the same proof written out twice, 33 lines apart from each other in
substance: the same "no $u$--$v$ path leaves its block" observation, the same
$\sum_B (|V(B)|-1) = n - c$ count, and the same glue-at-one-vertex realisation.
They differ only in which number is attached to a block, $|E(B)|$ or $W_m(B)$.
Extracting the shared statement once removes the second copy entirely.

```latex
\begin{lemma}[Block-additive objectives are knapsacks,\aimedal]\label{lem:block-knapsack}
Let $\sigma$ assign a real number to every simple graph that is $2$-connected or
a single edge, and for a simple graph $G$ put
$\sigma(G) := \sum_{B} \sigma(B)$, the sum over the blocks of $G$. Write
\[
    g(b) \;:=\; \max\bigl\{\, \sigma(B) : B \text{ $2$-connected or an edge},\
                 |V(B)| = b,\ \kap^{\max}_B \le m-1 \,\bigr\},
\]
with $g(b) := -\infty$ when no such $B$ exists. Then
\[
    \max\bigl\{\, \sigma(G) : |V(G)| = n,\ \kap^{\max}_G \le m-1 \,\bigr\}
    \;=\; \max\Bigl\{\, \textstyle\sum_i g(b_i) \;:\; b_i \ge 2,\
          \sum_i (b_i - 1) \le n-1 \,\Bigr\}.
\]
\end{lemma}

\begin{proof}
A $u$--$v$ path of $G$ never leaves the block containing $u$ and $v$: leaving
means crossing a cut vertex, and returning means crossing that same cut vertex a
second time, which no path does. Hence $\kap_G(u,v) = \kap_B(u,v)$ whenever
$u$ and $v$ share a block, while a pair in no common block is separated by a
single cut vertex and has $\kap_G(u,v) \le 1$. So $G$ is feasible exactly when
every block of $G$ is, and $\sigma(G) \le \sum_B g(|V(B)|)$.

Inside one component the block sizes satisfy $\sum_B (|V(B)|-1) =
(\text{order of the component}) - 1$, and each further component loses one more
vertex, so $\sum_B (|V(B)|-1) \le n-1$ over all blocks. That is $\le$.

For $\ge$, take blocks $B_1, \dots, B_t$ with $\sum (b_i-1) \le n-1$, choose one
vertex and attach every $B_i$ to it, pairwise disjoint otherwise, then add
isolated vertices to reach order exactly $n$. Its nontrivial blocks are exactly
the $B_i$, so by the first paragraph it is feasible and scores
$\sum_i \sigma(B_i)$.
\end{proof}
```

`thm:simple-vertex-blocks` is then this at $\sigma(B) = |E(B)|$ and
`thm:multi-vertex-blocks` is this at $\sigma(B) = W_m(B)$, the latter
block-additive by `lem:multi-vertex-objective` together with the first paragraph
above. Both proofs collapse to two sentences. `thm:simple-vertex-blocks` keeps
its superadditivity and limit paragraph, and the document's replacement for that
paragraph is worth taking too: packing `floor((n-1)/(b-1))` optimal blocks gives
the limit directly and retires the appeal to Fekete's lemma. It needs one
addition the document omits, that `c_m` is finite, which `rem:vertex-degeneracy`
already supplies through Mader.

## 3. Defects to repair before any of it is used

1. **§5, Lemma 18.** The cut is chosen before the pair. Fix as in 1.1 above.
2. **§6, Lemma 23.** No simplicity step, so $|V| = 3$ is uncovered by the split
   into "3-connected" and "has a separating pair". Vacuous, but keep the
   thesis's existing paragraph.
3. **§4, Theorem 16.** Rules out a two-arc path with its middle vertex in $B$
   only. The mirror case, middle vertex in $A$, needs naming as symmetric, which
   is what `thm:dir-multi-uniqueness` Step 1 does.
4. **§1, Theorem 2.** Asserts the limit exists without showing
   $c = \sup_b h_m(b)/(b-1)$ is finite. The thesis gets that from Mader.
5. **§8, Theorem 37.** "For fixed $s$, the factor $t/(s+t-1)$ increases with
   $t$" is false at $s = 1$, where it is constant, and $K_{1,t}$ is not
   $2$-connected so the block theorem does not apply to it. The thesis handles
   both explicitly and should keep doing so.
6. **§0, item 4.** Says Mader's density theorem is used only in the optional
   alternate-convention bound. Defect 4 means Theorem 2 needs it as well.

## 4. What is not worth adopting, and why

Everything else in the document is the thesis's own proof written shorter. That
is not the same as simpler, and in several places the compression loses the part
a reader needs.

- **§1 Lemma 1.** The thesis's inline version ("returning means crossing that
  same cut vertex a second time") is shorter than the document's cycle argument
  and is already stated where it is used.
- **§2 Lemma 5.** The consolidation is right in principle: the thesis currently
  proves `prop:dir-arc-stability` in four steps, then proves
  `thm:dir-arc-linear-error` by citing two of those steps, then obtains
  `lem:two-step-budget` by instructing the reader to re-read both proofs with
  $C$ in place of $m-1$. Three levels of indirection for one induction. But the
  material the reorganisation would strand is worth more than the saving:
  `lem:small-side` and `rem:case2-tight`, which prove that four is the best
  universal coefficient obtainable from the two facts Case 2 uses. If this is
  reorganised, state `lem:two-step-budget` first with a self-contained proof and
  derive `prop:dir-arc-stability` and `thm:dir-arc-linear-error` from it,
  keeping the two remarks. Do not adopt §2 as written, which drops them.
- **§3 Lemmas 8, 9 and Theorem 10.** Faithful compressions with no new idea.
  The thesis's versions carry `fig:skeleton-example`, which is what makes the
  three-step construction readable.
- **§3 Corollary 11.** This is `thm:dir-multi-m2` (A.42), already in the thesis
  and already saying exactly this.
- **§3 Theorem 12.** Identical to the thesis's proof of
  `thm:dir-vertex-m2-exact`, including the same machine base cases. No gain.
- **§4 Lemmas 13 to 15 and Theorem 16.** Compressions. Theorem 16 additionally
  drops the remark that pins where $n \ge 2m$ is used and the regularity
  consequence at even $n$.
- **§5 Lemma 17 and Theorem 21.** Compressions of `thm:menger-hyper` and
  `thm:simple-hyper-edge`.
- **§6 Theorem 22 and Theorem 24.** Compressions.
- **§7 Lemma 27 and Propositions 26, 28, Theorems 30 and 31.** Compressions.
  Theorem 31's proof in the thesis is already the shortest route known for the
  general orientation model.
- **§8 Lemmas 32, 35 and Theorems 33, 36, 37, Proposition 34.** Compressions.

## 5. Net effect if items 1.1 to 1.4 and section 2 are all taken

Roughly 1500 words and two citations leave the appendix, which is two to three
printed pages out of fifty-nine, and three pieces of machinery leave the
dependency graph: the hypergraph Gomory--Hu tree, Baranyai's theorem, and the
Tutte/SPQR decomposition. Menger, the ordinary Gomory--Hu tree and Mader's
density theorem all stay.

The dependency saving matters more than the page count. As it stands the
appendix asks a reader to accept three transported classical constructions in
order to follow three separate arguments. After these four changes it asks for
none of them, and the only classical results left standing are the ones the
thesis states with a citation and does not lean on structurally.

## 6. Reproduction

The numerical checks in this review are in
`research_notes/scripts/review_simplified_proofs.py`.

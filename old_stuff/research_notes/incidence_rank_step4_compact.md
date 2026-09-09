# The incidence rank lemma, Step 4, written out compactly

For `lem:incidence-rank` in `chapters/app_proofs.tex`. Statement, idea,
complete argument, one example. Every justification of the original is kept.
One presentational gap in the published Step 4 is filled and flagged.

## Statement

Let $G$ be a connected loopless multigraph with $V(G) = X \cup Z$ (disjoint):

- (i) $Z$ is independent,
- (ii) no edge incident to $Z$ is parallel to another edge,
- (iii) every $z \in Z$ has degree at least 2,
- (iv) $\kappa_G(x, x') \le 2$ for all distinct $x, x' \in X$.

Then $\mathrm{rank}(G) := |E| - |V| + 1 \le |X| - 1$.

Steps 1 to 3 of the induction on $|V| + |E|$ dispose of a cut vertex, a
degree-two $Z$-vertex and a degree-two $X$-vertex. **Step 4 is the case where
$G$ is 2-connected, $|V| \ge 3$, and every vertex has degree at least 3.**

## The idea in three sentences

Hypothesis (iv) caps how richly two $X$-vertices may be joined. That cap kills
parallel edges, because two copies are already two disjoint routes and
2-connectivity always finds a third, and it kills 3-connectivity outright,
because a 3-connected graph joins every pair by three disjoint paths. What is
left has a separating pair, and cutting there gives two smaller graphs whose
ranks and $X$-counts add up, with the cap surviving the cut because at most one
of three disjoint paths can use a single temporary connection and the other
side always has a genuine path to swap in.

## The argument

### (a) $G$ is simple

By (ii) any parallel class lies inside $X$. Suppose $\mu(x, x') \ge 2$. The two
copies are internally disjoint $x$-$x'$ paths, each with empty interior, so a
third path with at least one interior vertex would give $\kappa(x, x') \ge 3$.

Pick $w \notin \{x, x'\}$, available since $|V| \ge 3$. $G$ is 2-connected, so
$G - x'$ and $G - x$ are both connected. Take a walk from $x$ to $w$ in
$G - x'$ and **truncate it at the last occurrence of $x$**; take a walk from $w$
to $x'$ in $G - x$ and **truncate it at the first occurrence of $x'$**.
Concatenating gives an $x$-$x'$ walk whose interior avoids both $x$ and $x'$
and which passes through $w$, hence has length at least two. Any path extracted
from it begins with that walk's second vertex, which is neither $x$ nor $x'$,
so the path has an interior vertex. That is the third route, against (iv).

> The two truncations are the one thing the published proof leaves implicit
> when it says the concatenation "visits $x$ only first and $x'$ only last".
> Without them a walk may revisit an endpoint and the extracted path can
> collapse to the single edge $xx'$, which carries no interior vertex and
> proves nothing. The claim is true, and one sentence repairs it.

$G$ is therefore simple, and minimum degree three then forces $|V| \ge 4$.

### (b) $G$ is not 3-connected

$|V| \ge 4 = 3 + 1$, so were $G$ 3-connected, the global form of Menger's
theorem would give three internally disjoint paths between **every** pair,
adjacent pairs included. Two $X$-vertices would then break (iv), forcing
$|X| \le 1$. But any $z \in Z$ sends all its edges into $X$ by (i) with no two
parallel by (ii), hence has degree at most $|X| \le 1$, against degree three;
and $Z = \emptyset$ would give $|V| = |X| \le 1$, against $|V| \ge 4$. So $G$
has a separating pair $\{a, b\}$.

### (c) The cut

$G - \{a, b\}$ is disconnected. Gather its components into two non-empty
groups with vertex sets $U$ and $W$. Three facts follow, each used later:

1. **Each of $a$ and $b$ has a neighbour in $U$ and one in $W$.** If $a$ had
   none in $U$, then $U$'s only outside neighbour would be $b$, so $b$ alone
   would be a cut vertex.
2. **Each of $U$ and $W$ carries an $a$-$b$ path.** Every single component of
   $G - \{a,b\}$ has a neighbour in each of $a$ and $b$, by the same argument,
   so any non-empty group of components does.
3. **Neither side is a single vertex.** In a simple graph such a vertex could
   only be adjacent to $a$ and $b$, giving degree two. So $|U|, |W| \ge 2$.

### (d) The torsos

Write $s = |X \cap \{a, b\}|$. Build $G_U$ from the subgraph induced on
$U \cup \{a, b\}$ plus one temporary $a$-$b$ connection, and $G_W$ likewise:

1. $ab \in E(G)$: keep that edge on both sides.
2. $ab \notin E(G)$ and $s \ge 1$: add one new edge $ab$ to each side.
3. $s = 0$: add to each side a fresh $X$-vertex $t$ joined to $a$ and to $b$.

The three are exhaustive because (i) makes $ab \in E(G)$ force $s \ge 1$. In
case 1, $s = 1$ exactly: $s = 2$ would give $\kappa(a,b) \ge 3$ from the edge
together with one $a$-$b$ path through each side (fact 2), against (iv).

### (e) Each torso satisfies (i) to (iv)

**(i).** Every temporary connection has an endpoint in $X$: in cases 1 and 2
because $s \ge 1$, in case 3 because $t \in X$.

**(ii).** Case 1 adds nothing. Cases 2 and 3 add edges at pairs that carried no
edge at all ($ab \notin E(G)$; $t$ is fresh), so no parallel pair is created.

**(iii).** A $Z$-vertex inside $U$ keeps every neighbour, since $U$'s
components touch nothing outside $U \cup \{a, b\}$. A separator vertex in $Z$
keeps at least one neighbour on its own side by fact 1 and gains the temporary
connection, so it has degree at least two.

**(iv).** If one of the pair is the fresh $t$, its degree is two and a local
connectivity never exceeds a degree. For two old $X$-vertices $x_1, x_2$,
suppose $G_U$ carried three internally disjoint $x_1$-$x_2$ paths.

*At most one uses the temporary connection.* In case 3, $t$ would be an
interior vertex of any path using it, and internally disjoint paths share no
interior vertex. In cases 1 and 2 the connection is a single edge $ab$, and two
internally disjoint $x_1$-$x_2$ paths share no edge except $x_1x_2$ itself, of
which the torso holds exactly one copy.

*Swap it out.* Replace that one path's temporary connection by an $a$-$b$ path
through the opposite side, which fact 2 supplies. Its interior lies in the
opposite side, so it meets no vertex of $U \cup \{a, b\}$, while $a$ and $b$
already lie on the path being rebuilt. The rebuilt object is still a path, and
the three are still internally disjoint. They now live in $G$, contradicting
(iv) there.

This is the step the whole cut turns on: (iv) is not inherited, it is
**transported back**, and the transport works only because the temporary
connection can be used at most once.

### (f) Both torsos are strictly smaller

Forming $G_U$ deletes $W$, at least two vertices by fact 3, together with every
edge meeting $W$. Each $w \in W$ has degree at least three, so at least
$\lceil 3|W|/2 \rceil \ge 3$ edges go. It adds at most one vertex and two edges
(case 3; cases 1 and 2 add no vertex and at most one edge). So $|V| + |E|$
drops by at least two, and the induction hypothesis applies. Each torso is
connected, since every component of its side meets both $a$ and $b$ and the
temporary connection joins $a$ to $b$.

### (g) The count

Let $E_U$ and $E_W$ be the edges of $G$ inside $U \cup \{a,b\}$ and
$W \cup \{a,b\}$, excluding any $ab$ edge, so $|V| = |U| + |W| + 2$ and
$|E| = |E_U| + |E_W| + [\,ab \in E(G)\,]$. Write $r_U, r_W$ for the torso ranks
and $X_U, X_W$ for the torso $X$-sets. In all three cases $r_U = |E_U| - |U|$
and $r_W = |E_W| - |W|$, which is where the fresh vertex of case 3 pays for its
two edges:

| | $\mathrm{rank}(G)$ | $\|X_U\| + \|X_W\|$ | induction gives |
|---|---|---|---|
| 1 | $r_U + r_W$ | $\|X\| + s = \|X\| + 1$ | $\le \|X\| - 1$ |
| 2 | $r_U + r_W - 1$ | $\|X\| + s$ | $\le \|X\| + s - 3 \le \|X\| - 1$ |
| 3 | $r_U + r_W - 1$ | $\|X\| + 2$ | $\le \|X\| - 1$ |

Case 2 uses $s \le 2$ and is tight exactly at $s = 2$. Case 1's retained edge
is counted on both sides, which is why no $-1$ appears there.

## The example

Take $a, b$, $U = \{u_1, u_2\}$ and $W = \{w_1, w_2\}$, with each of
$G[U \cup \{a,b\}]$ and $G[W \cup \{a,b\}]$ a $K_4$ minus the edge $ab$. Then
$|V| = 6$, $|E| = 10$, $\mathrm{rank} = 5$, minimum degree 3, 2-connected, and
$\{a, b\}$ is a separating pair. All three cases of (d) run on it, and the
identities of (g) hold to the digit (checked by script):

- **Case 2**, $X = \{a, b, u_2, w_2\}$, $s = 2$. Each torso is a $K_4$ with
  $r = 3$ and $|X_T| = 3$. Then $r_U + r_W - 1 = 5 = \mathrm{rank}(G)$, and
  $|X_U| + |X_W| = 6 = |X| + s$.
- **Case 1**, after adding the edge $ab$, with $Z = \{b\}$ so $s = 1$. Each
  torso is again a $K_4$, $r = 3$, $|X_T| = 3$. Then $r_U + r_W = 6 =
  \mathrm{rank}(G)$ and $|X_U| + |X_W| = 6 = |X| + 1$.
- **Case 3**, $Z = \{a, b\}$ so $s = 0$. Each torso has five vertices and seven
  edges, $r = 3$, $|X_T| = 3$ counting the fresh $t$. Then
  $r_U + r_W - 1 = 5 = \mathrm{rank}(G)$ and $|X_U| + |X_W| = 6 = |X| + 2$.

This graph satisfies (i), (ii) and (iii) but **not** (iv): case 2 has
$\kappa(a,b) = 4$, case 3 has $\kappa(u_1,u_2) = 3$. That is the point of using
it. The bookkeeping of (g) is pure arithmetic and holds regardless, and the
conclusion fails here ($\mathrm{rank} = 5 > 3 = |X| - 1$) for exactly one
reason: hypothesis (iv) is false, so the inductive bounds $r_U \le |X_U| - 1$
are unavailable. It shows what (iv) is carrying.

## Step 4 may never fire

Searching for a graph in Step 4's own hypothesis set, simple, 2-connected, not
3-connected, minimum degree at least three, carrying a partition
$V = X \cup Z$ that satisfies (i) to (iv):

| $n$ | connected, min degree 3 | 2-connected, not 3-connected | admitting a valid partition |
|---|---|---|---|
| 5 | 3 | 0 | 0 |
| 6 | 19 | 2 | 0 |
| 7 | 150 | 13 | 0 |
| 8 | 2589 | 193 | 0 |
| 9 | 84242 | 3261 | 0 |

Exhaustive over `geng -c -d3`, every independent set $Z$ tried, local
connectivity by max flow on the split graph with unit arcs. The 3-connected
graphs need no search: part (b) rules them out by proof. The $Z = \emptyset$
case needs none either, since minimum degree three gives
$|E| \ge \lceil 3n/2 \rceil$ while (iv) on every pair caps $|E|$ at Mader's
$k_3(n) = \lfloor 3(n-1)/2 \rfloor$, which is strictly smaller.

So through $n = 9$ the separating-pair machinery is never reached: Steps 1 to 3
always finish first. $n = 10$ was started and abandoned: 5203110 graphs at that
order, and the sweep had not cleared its first 200000 after six minutes, so it
would have run for hours in this form. Nothing here rests on it. This does **not** shorten the proof, since Step 4 still has
to be discharged at every $n$, but it says where to look. If the core is
provably empty then Step 4 collapses to parts (a) and (b), and the lemma loses
its only case that reasons about how routes recombine, which is also its only
case that the branch coverage in `final_review_2026-09-07.md` does not reach.

Scripts: `program/scripts/incidence_rank_step4_core.py` (the sweep) and
`program/scripts/incidence_rank_step4_torso.py` (the three-case bookkeeping).

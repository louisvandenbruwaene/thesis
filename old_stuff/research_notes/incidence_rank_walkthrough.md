# The incidence rank lemma, written out, 8 September 2026

`lem:incidence-rank` (A.53) is the longest single proof in the thesis and the
last thing standing between `thm:hyper-vertex-m3` and `prop:hyper-vertex-lower-multi`
and their proved status. The author asked for it in a checkable form.

Step 4 already has its own note, `incidence_rank_step4_compact.md`, written on
7 September, with the statement, the argument, one worked example and one
sentence of repair. This note covers everything else: what the statement is
for, why the induction is set up as it is, and Steps 1 to 3 in full. Read this
first and that one second.

## The statement

Let $G$ be a connected loopless multigraph with $V(G) = X \dot\cup Z$ such that

- **(i)** $Z$ is independent, no edge joins two $Z$-vertices;
- **(ii)** no edge incident to $Z$ is parallel to another edge;
- **(iii)** every $z \in Z$ has degree at least $2$;
- **(iv)** $\kappa_G(x, x') \le 2$ for all distinct $x, x' \in X$.

Then $\mathrm{rank}(G) \le |X| - 1$.

Here $\mathrm{rank}(G) = |E| - |V| + 1$ for a connected graph, the number of
independent cycles, also called the cycle rank or first Betti number.

## What it is for

$G$ is the incidence graph $I(\mathcal{H})$ of a hypergraph: $X$ is the vertex
class, $Z$ is the hyperedge class, and an edge of $G$ is one incidence. Then
the four hypotheses read:

- (i) no hyperedge-node is adjacent to another hyperedge-node, which is what an
  incidence graph is;
- (ii) no hyperedge repeats a vertex;
- (iii) no hyperedge dangles as a leaf, it has at least two members;
- (iv) the hypergraph is feasible at $m = 3$, since $\kappa_I(u,v) = \kappa_{\mathcal{H}}(u,v)$
  for vertex pairs under the incidence convention.

The conclusion turns into the hyperedge count in four lines, which is worth
seeing first because it shows why rank is the right quantity to bound. With
$n$ vertices, $q$ hyperedges, $r$-uniform, and $C$ components of $I(\mathcal{H})$:

- $I(\mathcal{H})$ has $rq$ edges and $n + q$ nodes, so $\sum_c \mathrm{rank} = rq - (n+q) + C$;
- the lemma summed over components gives $\sum_c (|X_c| - 1) = n - C$;
- so $rq - (n + q) + C \le n - C$, that is $q(r-1) \le 2(n-1) + 2(1 - C)$;
- and $C \ge 1$ gives $q(r-1) \le 2(n-1)$.

Everything the $m = 3$ hypergraph vertex bound needs is in that arithmetic. The
lemma is the whole difficulty.

## Why the induction is set up as it is

The induction is on $|V| + |E|$, which must drop strictly at every step. The
plan is to keep peeling structure off until the graph is forced into a shape
where a genuine argument is possible:

1. **Step 1** disposes of graphs with a cut vertex, by splitting into blocks.
   After it, $G$ is $2$-connected.
2. **Step 2** disposes of a $Z$-vertex of degree exactly $2$, by suppressing it.
   After it, every $Z$-vertex has degree at least $3$.
3. **Step 3** disposes of an $X$-vertex of degree exactly $2$, by deleting it.
   After it, minimum degree is at least $3$.
4. **Step 4** faces what is left: $2$-connected, not $3$-connected once the
   $3$-connected case is excluded by proof, minimum degree at least three. It
   splits at a separating pair and inducts on two torsos.

The ordering matters and is not cosmetic. Step 3 deletes a vertex, which drops
its neighbours' degrees by one. A $Z$-neighbour of degree $2$ would fall to
degree $1$ and break (iii). Step 3 is safe only because Step 2 has already been
used up and every $Z$-vertex has degree at least $3$. If you read the steps out
of order this looks like a gap, and it is not one.

## Base case, $|V| \le 2$

*One vertex.* It has degree $0$. Hypothesis (iii) puts a floor of $2$ on the
degree of a $Z$-vertex, so this vertex cannot be in $Z$, hence lies in $X$, and
$\mathrm{rank} = 0 \le 0 = |X| - 1$.

*Two vertices.* Suppose one of them, say $z$, were in $Z$. Its only possible
neighbour is the other vertex, and (ii) forbids the edge from being parallel to
another, so $z$ would have degree at most $1$, against (iii). So both vertices
lie in $X$ and $|X| = 2$.

Now the multiplicity between them. Parallel edges between two vertices are
internally disjoint paths, because each has empty interior and so no two can
share an interior vertex. Hypothesis (iv) caps that at $2$, so there are at most
two edges, $\mathrm{rank} \le 2 - 2 + 1 = 1 = |X| - 1$.

## Step 1: a cut vertex

Suppose $G$ has a cut vertex. Break it into blocks $B_1, \dots, B_c$ with
$c \ge 2$. A block is a maximal piece with no cut vertex of its own, so a bridge
edge, a two-vertex parallel bundle, or a maximal $2$-connected subgraph. Two
blocks meet in at most one vertex, and a shared vertex is a cut vertex of $G$.

*Rank adds over blocks.* No cycle passes through two different blocks. An
excursion out of a block must come back through the same cut vertex, by the
block-cut tree, and a cycle cannot repeat a vertex. So
$\mathrm{rank}(G) = \sum_i \mathrm{rank}(B_i)$, and it is enough to bound each
block and add.

*Each block satisfies the hypotheses, or is trivial.*

- A bridge block is a single edge, so $\mathrm{rank} = 0$, and by (i) at least
  one of its two endpoints is in $X$, giving $0 \le |X \cap B| - 1$.
- Every other block has minimum degree at least $2$, including a two-vertex
  parallel bundle. Hypotheses (i) to (iv) restrict to it, and it is strictly
  smaller since $c \ge 2$, so induction gives
  $\mathrm{rank}(B_i) \le |X \cap B_i| - 1$.

*Adding them up, which is the only fiddly part.* A cut vertex sits in several
blocks and would be counted several times. Write $b(v)$ for the number of
blocks containing $v$, so $b(v) = 1$ unless $v$ is a cut vertex. Counting each
$X$-vertex once per block containing it,

$$\sum_i |X \cap B_i| = |X| + \sum_{x \in X \text{ cut}} (b(x) - 1).$$

The block-cut tree identity is

$$c = 1 + \sum_{v \text{ cut}} (b(v) - 1),$$

which comes from counting that tree's edges twice. The tree has $c$ block-nodes
plus one node per cut vertex, so being a tree it has
$c + \#\{\text{cut vertices}\} - 1$ edges. It also has exactly $b(v)$ edges at
each cut vertex $v$, so $\sum_{v \text{ cut}} b(v)$ edges. Equate and solve for $c$.

Subtract the second display from the first and split the cut vertices into
their $X$-part and $Z$-part:

$$\mathrm{rank}(G) \le \sum_i (|X \cap B_i| - 1)
= |X| - 1 - \sum_{z \in Z \text{ cut}} (b(z) - 1) \le |X| - 1,$$

the last step because every $b(z) - 1 \ge 0$. The $X$-cut terms cancel exactly
against the block-count identity, and the $Z$-cut terms only help.

Worth noticing: a $Z$ cut vertex makes the bound *stronger*, and that slack is
never needed. The step is tight when no cut vertex lies in $Z$.

## Step 2: a $Z$-vertex of degree two

$G$ is now $2$-connected. Suppose $z_0 \in Z$ has degree exactly $2$.

Its two neighbours are in $X$ by (i), and they are distinct: two edges to the
same vertex would be parallel edges at a $Z$-vertex, which (ii) forbids.

**Suppress $z_0$**: delete it and join its neighbours $x, x'$ by one new edge.

- *Rank is unchanged.* Two edges go, one comes, one vertex goes. So $|E|$ and
  $|V|$ each drop by one, and $\mathrm{rank} = |E| - |V| + 1$ is unchanged.
- *$|X|$ is unchanged*, since the new edge runs $X$ to $X$ and only a
  $Z$-vertex was removed. So the target $|X| - 1$ is unchanged too.
- *(i), (ii), (iii) survive* for the remaining $Z$-vertices: the new edge
  touches no $Z$-vertex, and no other degree changed.
- *(iv) survives.* Replacing the path $x, z_0, x'$ by a direct edge changes no
  route among the surviving vertices, so every $\kappa(x_1, x_2)$ is preserved
  exactly, not merely bounded.
- *The measure drops.* $|V| + |E|$ falls by $2$.

Induction on the smaller graph returns the bound for $G$ unchanged, because both
sides of the inequality are unchanged.

## Step 3: an $X$-vertex of degree two

$G$ is $2$-connected and, Step 2 being used up, every $Z$-vertex has degree at
least $3$. Suppose $x_0 \in X$ has degree $2$. Delete it.

- *Connectivity.* Deleting one vertex from a $2$-connected graph leaves it
  connected, so the induction hypothesis is applicable.
- *Rank drops by exactly one.* Two edges and one vertex go.
- *$|X|$ drops by exactly one.*
- *(iii) survives.* Each neighbour loses one edge. A neighbour in $Z$ falls
  from degree at least $3$ to degree at least $2$, which is still enough. This
  is the place where Step 2 has to have come first.
- *(iv) survives.* Deleting a vertex cannot raise a connectivity.
- *(i) and (ii) survive*, since removing a vertex only removes edges.

One side condition: $|X| \ge 2$ to begin with, so that $|X| - 1 \ge 1$ on the
smaller graph. If $|X| \le 1$, then by (i) every $z \in Z$ sends all its edges
to that one $X$-vertex, and (ii) forbids repeats, so $z$ would have degree at
most $1$, against (iii).

Induction gives $\mathrm{rank}(G) - 1 \le (|X| - 1) - 1$, that is
$\mathrm{rank}(G) \le |X| - 1$.

## Step 4

See `incidence_rank_step4_compact.md`. In outline it shows the surviving graph
is simple, excludes a $3$-connected core by proof, then splits at a separating
pair and applies the induction hypothesis to two smaller torsos, transporting
hypothesis (iv) back rather than inheriting it.

Two things recorded there that are worth knowing before you start:

- **One sentence needs repair, and the claim stands.** Part (a) concatenates a
  walk from $x$ to a third vertex inside $G - x'$ with a walk from that vertex
  to $x'$ inside $G - x$, and says the concatenation visits $x$ only first and
  $x'$ only last. Truncating the first walk at the *last* occurrence of $x$ and
  the second at the *first* occurrence of $x'$ makes that true as written. It is
  recorded rather than edited into the thesis because the badge is yours.
- **Step 4 may never fire.** An exhaustive search over `geng -c -d3` found no
  graph at all in Step 4's own hypothesis set through $n = 9$: simple,
  $2$-connected, not $3$-connected, minimum degree at least three, with a
  partition satisfying (i) to (iv). The $3$-connected case needs no search,
  part (b) excludes it, and $Z$ empty needs none either, since minimum degree
  three forces $|E| \ge \lceil 3n/2 \rceil$ while (iv) on every pair caps $|E|$
  at Mader's $\lfloor 3(n-1)/2 \rfloor$, which is smaller. This does not shorten
  the proof, which still has to discharge Step 4 at every $n$, but it means you
  will not find a small instance to test your reading against.

## What to focus on while reading

Steps 1 to 3 are bookkeeping and they are checkable in a sitting. The three
things actually worth pausing on are the block-cut tree identity in Step 1, the
fact that suppression in Step 2 preserves $\kappa$ exactly rather than
approximately, and the ordering dependency of Step 3 on Step 2.

Step 4 is the only part that reasons about how routes recombine, and it is the
part the 7 September review recorded as sitting outside the finite branch
coverage.

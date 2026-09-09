# The directed hypergraph chain, written out, 8 September 2026

Six results carry the directed hypergraph leading constant. The author asked
for each one in a form he can check rather than in the compressed form the
appendix prints. Nothing here changes the thesis. Numbers quoted as computed
come from `program/scripts/dir_hyper_chain_examples.py`, which shares no code
with the thesis program for the parts it checks.

The six, in the order they are marked to read:

| | | Result | Own proof |
|---|---|---|---|
| 1 | A.68 | `prop:dir-hyper-first` | 306 words |
| 2 | A.69 | `const:bounded-outdegree-hyper` | 81 |
| 3 | A.70 | `lem:dir-hyper-duality` | 50 |
| 4 | A.71 | `prop:dir-hyper-general` | 175 |
| 5 | A.73 | `thm:dir-hyper-general-constant` | 698 |
| 6 | 1.14 | `thm:dir-hyper-constant` | 767 |

## The shape of the whole thing, before any detail

There is one target: for fixed $r$ and $m$, the largest directed $r$-uniform
multihypergraph with every ordered pair carrying at most $m-1$ disjoint routes
has

$$|E| = (1+o(1))\,\frac{(m-1)n^2}{4(r-1)}.$$

Two halves. The lower half is one construction, and result 1 supplies it. The
upper half is where the work is, and it is done twice, once for the forward
model (result 6) and once for the general model (result 5), by the same
three-step skeleton.

**The three steps, in words.**

1. **Shadow.** Forget the hypergraph and keep only the simple digraph $R$ that
   records which ordered pairs are joined in one step. Count hyperedges against
   arcs of $R$.
2. **Budget.** Show $R$ cannot be arbitrary: for every ordered pair $(u,v)$,
   the number of one-step and two-step routes from $u$ to $v$ in $R$ is bounded
   by a constant depending only on $r$ and $m$.
3. **Assemble.** Feed that budget into `lem:two-step-budget`, which you have
   already verified, to get $|A(R)| \le \lfloor n^2/4\rfloor + O(n)$, and
   substitute back into step 1.

Result 1's upper bound is the same step 1 stopped early, using the trivial
$|A(R)| \le n(n-1)$ instead of step 3. That is the entire difference between
the crude bound and the sharp one, and it is exactly a factor of four, since
$n(n-1)$ is about $n^2$ and $\lfloor n^2/4\rfloor$ is about $n^2/4$. Computed
at $r = m = 3$:

```
     n  construction     sharp     crude  crude/constr
    20           100       404       380          3.80
    50           625      1409      2450          3.92
   200         10000     13184     39800          3.98
  1000        250000    265984    999000          4.00
```

So results 5 and 6 exist to buy that factor of four, and they buy it entirely
in their step 2. If you accept `lem:two-step-budget`, which you have, then the
only new mathematics in either of them is one paragraph.

---

## 1. A.68, `prop:dir-hyper-first`. Two crude bounds

Forward model: a hyperedge is one tail $u$ and $r-1$ heads. A route enters at
the tail and leaves at a head.

### The upper bound, $(r-1)|E| \le (m-1)n(n-1)$

Say a hyperedge with tail $u$ **serves** the ordered pair $(u,h)$ for each of
its $r-1$ heads $h$.

*Each ordered pair is served at most $m-1$ times.* Suppose $m$ distinct
hyperedges all served $(u,v)$. Each gives a one-step route $u \to v$. They use
different hyperedges, so they are hyperedge-disjoint. A one-step route has no
interior vertex, so they are internally vertex-disjoint too. That is $m$
disjoint routes, against feasibility.

*Now count the pairs (hyperedge, ordered pair it serves) two ways.* Each
hyperedge serves exactly $r-1$ pairs, so the count is $(r-1)|E|$. Each of the
$n(n-1)$ ordered pairs is served at most $m-1$ times, so the count is at most
$(m-1)n(n-1)$. Hence $(r-1)|E| \le (m-1)n(n-1)$.

That is the whole upper bound. It is one double count and one sentence about
one-step routes.

### The lower bound, the bipartite family

Split $V$ into tails $A$ with $|A| = \alpha$ and heads $B$ with
$|B| = b = n - \alpha \ge r - 1$. Write $k = r-1$ and $d = m-1$.

*First build a $k$-uniform multihypergraph $\mathcal{G}^*$ on $B$ with
$e = \lfloor db/k \rfloor$ edges and every degree at most $d$.* Label $B$ as
$0, 1, \dots, b-1$, write the infinite word $0,1,\dots,b-1,0,1,\dots$, and cut
it into blocks of $k$ consecutive letters. Take the first $e$ blocks.

- Each block has $k$ distinct letters, because $k \le b$ and the word never
  repeats a letter inside any window of $b$ consecutive positions.
- The $e$ blocks occupy $ek$ consecutive positions of a word that cycles with
  period $b$, so each letter occurs $\lfloor ek/b \rfloor$ or
  $\lceil ek/b \rceil$ times.
- $e = \lfloor db/k \rfloor$ gives $ek \le db$, so $ek/b \le d$, so
  $\lceil ek/b \rceil \le d$. Every degree is at most $d = m-1$.

Worked instance, $r = 3$ so $k = 2$, $m = 3$ so $d = 2$, $b = 5$:
$e = \lfloor 10/2 \rfloor = 5$, the word is $0,1,2,3,4,0,1,2,3,4$, and the
blocks are $\{0,1\}, \{2,3\}, \{4,0\}, \{1,2\}, \{3,4\}$. Every letter appears
exactly twice, which is the cap.

*Then hang every tail off it.* For each $a \in A$ and each $H \in
\mathcal{G}^*$, include the hyperedge $(a, H)$, with the same multiplicity. The
count is $\alpha e = \alpha \lfloor (m-1)(n-\alpha)/(r-1) \rfloor$, which is
the printed formula.

*Why it is feasible.* No vertex of $B$ is a tail of anything, so once a route
has taken one step it is stuck. Every route is therefore a single step. Routes
from $a \in A$ to $v \in B$ are exactly the hyperedges $(a, H)$ with $v \in H$,
of which there are $\deg_{\mathcal{G}^*}(v) \le m-1$. Pairs inside $A$ and
pairs starting in $B$ have no routes at all. So
$\lambda^{\max} \le m-1$.

Checked by brute force, enumerating every simple Berge route and searching for
a largest disjoint family, with no import of the thesis program:

```
n=6 m=3 r=3 alpha=2:  8 hyperedges, lambda^max = 2, cap 2
n=6 m=2 r=3 alpha=3:  3 hyperedges, lambda^max = 1, cap 1
n=5 m=3 r=2 alpha=2: 12 hyperedges, lambda^max = 2, cap 2
n=7 m=3 r=3 alpha=3: 12 hyperedges, lambda^max = 2, cap 2
```

The printed count was also checked against the construction actually built, for
every $r \le 4$, $m \le 4$, $n \le 10$ and every admissible $\alpha$.

*Simplicity.* If $d \le \binom{b-1}{k-1}$ there are enough distinct $k$-sets
containing any fixed vertex, so `lem:sparse-hypergraph` supplies a simple
$\mathcal{G}^*$ instead of the cyclic one, and the whole family is simple.

*The $n^2$.* Maximising $\alpha (m-1)(n-\alpha)/(r-1)$ over real $\alpha$ gives
$\alpha = n/2$ and the value $(m-1)n^2/(4(r-1))$.

**One thing the proof does not claim, and it is worth knowing before you read
it.** $\alpha = \lfloor n/2 \rfloor$ is not always the integer maximiser. At
$r = 4$, $m = 2$, $n = 20$ it gives $30$ while $\alpha = 11$ gives $33$. The
appendix says only that the balanced split already reaches
$(m-1)n^2/(4(r-1)) - O_{m,r}(n)$, and it flags this in its own parenthetical
about the floor favouring an off-balance split by a unit or two. Checked over
$r \le 4$, $m \le 6$, $n \le 2000$: the gap from $\lfloor n/2 \rfloor$ to the
true integer maximum never exceeds $0.334\,n$, so it cannot touch the $n^2$
term.

---

## 2. A.69, `const:bounded-outdegree-hyper`. A cut you get for free

One observation: **every route out of $u$ must begin with a hyperedge whose
tail is $u$.** So the set of out-hyperedges of $u$ is a cut separating $u$ from
everything else. If $u$ has $d$ of them then $\lambda(u,v) \le d$ for every
$v$.

Give every vertex $d = \min\{m-1, \binom{n-1}{r-1}\}$ distinct out-hyperedges,
with any distinct $(r-1)$-subsets as head sets. That gives a simple directed
hypergraph with $nd$ hyperedges and $\lambda^{\max} \le m-1$. The vertex
measure is no larger, since vertex-disjoint routes are in particular
hyperedge-disjoint.

The multi version replaces the $d$ distinct hyperedges by $m-1$ copies of one,
giving $n(m-1)$ copies.

This family is linear in $n$, so it never competes with the bipartite one
asymptotically. It is here because it is the family that works at every $n$
including small ones, and because the one-line cut argument is reused later.

---

## 3. A.70, `lem:dir-hyper-duality`. Reversal

Send every hyperedge $(T, H)$ to $(H, T)$. In the forward model $T$ is a
single vertex, so the image has a single head, which is the backward model.
The map is an involution and preserves the number of hyperedges.

Take a directed Berge route from $u$ to $v$: vertices
$u = v_0, v_1, \dots, v_l = v$ and a hyperedge $e_i$ for each step with
$v_{i-1}$ a tail and $v_i$ a head. Reverse the vertex sequence and reverse each
$e_i$. In $\mathcal{H}^R$ the reversed $e_i$ has $v_i$ as a tail and $v_{i-1}$
as a head, so the reversed sequence is a Berge route from $v$ to $u$. It uses
the same edge copies and the same interior vertices.

Two routes are hyperedge-disjoint before if and only if after, since the edge
copies are the same. Same for internal vertices. So
$\lambda_{\mathcal{H}}(u,v) = \lambda_{\mathcal{H}^R}(v,u)$ and likewise for
$\kappa$. Taking a maximum over ordered pairs, and noting reversal just permutes
the ordered pairs, $\lambda^{\max}$ and $\kappa^{\max}$ are unchanged. A
bijection preserving both the edge count and feasibility carries the extremal
number across.

Nothing else is going on. The only thing to check while reading is that a
reversed Berge route really is a Berge route, which is the display above.

---

## 4. A.71, `prop:dir-hyper-general`. The same crude bound, one new inequality

Now a hyperedge is any split $(T, H)$ with both parts non-empty and
$|T| + |H| = r$.

*Per-pair cap.* A hyperedge with $u \in T$ and $v \in H$ carries the one-step
route $u \to v$. Distinct such hyperedges give routes sharing no edge copy and
no interior vertex, so if $k$ hyperedges have $u$ in the tail and $v$ in the
head then $\lambda(u,v) \ge k$ and $\kappa(u,v) \ge k$, forcing $k \le m-1$.
Identical to result 1.

*Double count.* A hyperedge $(T,H)$ fills exactly $|T|\,|H|$ ordered pairs, so

$$\sum_{(T,H)} |T|\,|H| \;\le\; (m-1)\,n(n-1).$$

*The one new inequality.* $|T|\,|H| \ge r-1$. Both parts are at least one and
they sum to $r$, so the product is $j(r-j)$ for some $1 \le j \le r-1$, and
$j(r-j)$ is smallest at the ends, where it equals $r-1$. Hence

$$(r-1)|E| \;\le\; \sum_{(T,H)} |T|\,|H| \;\le\; (m-1)n(n-1).$$

The forward family of result 1 is a set of general hyperedges, so it is still
available as a lower bound, and the general value is $\Theta_{r,m}(n^2)$ too.

That is the whole result: result 1's bound plus the observation that splitting
a hyperedge more evenly only makes it fill more pairs, never fewer than $r-1$.

---

## 5 and 6. The sharp constant, A.73 and 1.14

These two are the same three-step argument. Read 6 first if you want the
cleaner one, then 5 as a variation, or read them in the marked order which
follows the page order. Below they are done together, with the differences
called out.

Throughout, $R$ is the **one-step shadow**: the simple digraph with an arc
$(u,v)$ whenever some hyperedge has $u$ in its tail and $v$ among its heads.
`cod(u,v)` counts the hyperedges realising that arc. $R$ has no loops, since a
hyperedge's tail set and head set are disjoint.

### Step 1, in both. Hyperedges against shadow arcs

Exactly the double count of results 1 and 4, but stopped at $|A(R)|$ instead of
throwing it away as $n(n-1)$:

$$(r-1)\,|E(\mathcal{H})| \;\le\; \sum_{(u,v) \in A(R)} \mathrm{cod}(u,v)
\;\le\; (m-1)\,|A(R)|.$$

The per-arc cap $\mathrm{cod}(u,v) \le m-1$ is the same one-step-route argument
as before. In the general model the left side uses $|T||H| \ge r-1$ from
result 4.

### Step 2, the one paragraph that differs

The aim is the hypothesis of `lem:two-step-budget`: for every ordered pair
$(u,v)$,

$$\mathbf{1}_{(u,v) \in A(R)} + p_2(u,v) \;\le\; C,$$

where $p_2(u,v)$ counts midpoints $x$ with $(u,x)$ and $(x,v)$ both in $R$.
Call the set counted on the left the **targets** of $(u,v)$: $v$ itself when
the arc is there, plus every midpoint.

**Forward model (1.14): a maximal matching, $C = (r-1)(m-1)$.**

Every target $t$ is a head of at least one hyperedge whose tail is $u$, by the
definition of $R$. Form the bipartite graph joining each target to each such
hyperedge, and take a **maximal** matching $M$, meaning one that cannot be
extended. Not a maximum matching. Greedily adding any addable edge produces one.

*Claim: $|T| \le (r-1)|M|$.* Let $t$ be an unmatched target. Every hyperedge
joined to $t$ must already be matched, or $M$ could be extended by that pair.
So every target, matched or not, lies in a hyperedge used by $M$. A forward
hyperedge has $r-1$ heads, so it can hold at most $r-1$ targets. Counting
targets by the hyperedge of $M$ that holds them gives $|T| \le (r-1)|M|$.

*Claim: $|M| \le \kappa(u,v)$.* Read each matched pair as a route. A matched
pair $(v, e)$ gives the one-step route $u \to v$ through $e$. A matched pair
$(x, e)$ with $x$ a midpoint gives $u \to x \to v$, entering through $e$ and
leaving through any hyperedge with tail $x$ and $v$ as a head, one of which
exists because $(x,v) \in A(R)$. These routes are pairwise disjoint:

- entering hyperedges are distinct, because $M$ is a matching;
- leaving hyperedges have pairwise distinct tails, namely the distinct
  midpoints, so they are distinct from one another;
- no leaving hyperedge is an entering one, because entering ones have tail $u$
  and leaving ones have tail a midpoint, which is not $u$;
- interiors are the empty set and distinct singletons, so the routes are
  internally vertex-disjoint as well.

So they form a disjoint family of size $|M|$, and $|M| \le \kappa(u,v) \le m-1$.

Together, $|T| \le (r-1)(m-1)$, which is the budget.

Checked directly on random forward hypergraphs, computing $\kappa(u,v)$ exactly
by enumerating every simple Berge route and searching for a largest disjoint
family: over 3345 ordered pairs carrying at least one target, the inequality
$|T| \le (r-1)\kappa(u,v)$ never failed, and the largest ratio
$|T|/\kappa(u,v)$ observed was exactly $2 = r-1$ at $r = 3$, so the factor is
tight and not slack.

**General model (A.73): a greedy route family, $C = (2r+1)(m-1)$.**

The matching argument does not survive, because a general hyperedge can hold
targets in its tail set as well as its head set. The replacement is cruder and
costs a worse constant.

Call a hyperedge an **entrance** for a target $t$ if $u$ is a tail and $t$ a
head, and an **exit** for a midpoint $t$ if $t$ is a tail and $v$ a head. Every
target has an entrance and every midpoint has an exit. No hyperedge is both an
entrance and an exit for the *same* $t$, since that would put $t$ in its tail
set and its head set at once, and those are disjoint.

Build a family $\mathcal{F}$ of routes greedily: distinct targets, pairwise
distinct hyperedges, adding any addable route until none is addable. Say it has
size $M$ and serves target set $S$, using hyperedge set $U$ with $|U| \le 2M$,
since each route uses one or two hyperedges. As before the routes are pairwise
hyperedge-disjoint by construction and internally vertex-disjoint because their
interiors are empty or distinct singletons, so $M \le \kappa(u,v) \le m-1$.

Now take an unserved target $t \notin S$. If it had an unused entrance, and for
a midpoint an unused exit too, the route through them could be added, against
maximality. So either every entrance of $t$ is in $U$, or $t$ is a midpoint all
of whose exits are in $U$. An entrance has $t$ as a head and an exit has $t$ as
a tail, so either way $t$ lies in $T_e \cup H_e$ for some $e \in U$. Hence

$$|T| \;\le\; M + \sum_{e \in U} (|T_e| + |H_e|) \;=\; M + r\,|U| \;\le\; (2r+1)M
\;\le\; (2r+1)(m-1).$$

The middle equality is the point of writing it this way: $|T_e| + |H_e| = r$
exactly, so the constant is $r$ and not $2(r-1)$.

### Step 3, in both. Assemble

`lem:two-step-budget` says a $C$-budgeted simple digraph on $n$ vertices has
$|A(D)| \le \lfloor n^2/4 \rfloor + 4C(n-1)$. Apply it to $R$ and substitute
into step 1.

Forward, $C = (r-1)(m-1)$:

$$|E| \;\le\; \frac{m-1}{r-1}\Bigl[\Bigl\lfloor \frac{n^2}{4}\Bigr\rfloor
+ 4(r-1)(m-1)(n-1)\Bigr]
\;=\; \frac{m-1}{r-1}\Bigl\lfloor \frac{n^2}{4}\Bigr\rfloor + 4(m-1)^2(n-1),$$

where the $(r-1)$ cancels in the second term. That is the printed statement.

General, $C = (2r+1)(m-1)$, gives the printed
$\frac{m-1}{r-1}\lfloor n^2/4 \rfloor + \frac{4(2r+1)(m-1)^2}{r-1}(n-1)$, worse
only in the linear term.

The hypothesis $\lambda^{\max} \le m-1$ implies $\kappa^{\max} \le m-1$ by
Whitney, so the bound stated under $\kappa$ covers the $\lambda$ case too.

The lower bound is result 1's family, feasible under both separations at once
since it is $\lambda$-feasible and $\kappa \le \lambda$. Its count matches the
$n^2$ term, so the constant is settled.

### The $r = 2$ and simplicity remarks

For fixed $r \ge 3$ the simplicity condition of result 1 holds once $n$ is
large, so the leading term is attained by simple hypergraphs. At $r = 2$ the
model is the simple digraph problem, with leading term $n^2/4$, and repeats are
needed to reach the constant for $m \ge 3$.

---

## What to focus on while reading

Results 2, 3 and 4 are one idea each: a cut you get for free, an involution,
and $j(r-j) \ge r-1$.

Result 1 is a double count plus a construction whose only trick is the cyclic
word.

Results 5 and 6 are the same three-step argument, and steps 1 and 3 are already
yours. What is left to check is the single step-2 paragraph in each, and the
two are independent of one another. That is the maximal matching for the
forward model and the greedy route family for the general one.

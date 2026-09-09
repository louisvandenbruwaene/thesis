# Sørensen-Thomassen checked against the original paper, 7 September 2026

`final_review_2026-09-07.md` recorded that the full 1974 paper had not been
retrieved, so the transcription and the recursive construction could not be
called checked against the original. The paper is in the repository as
`sorensen.pdf`, a 17-page scan with no text layer, which is why greps over it
came back empty. It was read page by page in this pass.

B. Aagaard Sørensen and C. Thomassen, "On k-Rails in Graphs", *Journal of
Combinatorial Theory (B)* **17** (1974), 143-159. Received 25 July 1973.

## The convention

Section 1 defines a *k-rail* as the union of $k$ paths each pair of which has
exactly the endvertices in common, so a $k$-rail is $k$ internally disjoint
paths and the paper's problem is the vertex one. It defines $f_k(n)$ as the
least integer $r$ such that every graph on $n$ vertices with $r$ or more edges
contains a $k$-rail. That is a forcing count, one more than the maximum this
thesis writes. `rem:threshold-convention` states exactly this.

## Every claim the thesis attributes to the paper

- **Theorem 4, page 158.** "For $n \ge 6$, $n \ne 7$, $n \ne 12$,
  $f_5(n) = \lfloor 8n/3 \rfloor - 3$." The thesis quotes it verbatim in
  `rem:threshold-convention`, including the two exceptions.
- **The exceptional values.** The paragraph after Theorem 4 gives $f_5(7) = 16$
  and states without proof that $f_5(12) = 28$. The thesis quotes both.
- **The small range.** The same paragraph closes with
  $f_5(n) = \lfloor 5(n-1)/2 \rfloor + 1$ for $6 \le n \le 13$. The thesis
  quotes it and builds `thm:sorensen-thomassen` from it.
- **Arithmetic of the two-range restatement.** Subtracting one throughout gives
  $k_5(n) = \lfloor 5(n-1)/2 \rfloor$ for $6 \le n \le 13$ and
  $k_5(n) = \lfloor 8n/3 \rfloor - 4$ for $n \ge 14$. Checked at the joins:
  $f_5(6) = 13$ is stated on page 155 and the first formula gives 13;
  $f_5(13) = 31$ is stated on page 158 and both formulas give 31;
  $f_5(14) = 34$ is stated on page 158 and the second gives 34. Leonard's edge
  value $\ell_5(n) = \lfloor 5(n-1)/2 \rfloor$ reads 30 at $n = 13$ against
  $k_5(13) = 30$ and 32 at $n = 14$ against $k_5(14) = 33$, so the divergence
  point is $n = 14$ as the thesis states.
- **The two exceptions read the way `ch1_basecases.tex` says.** At $n = 7$ the
  second formula gives 14 against the true 15, one too few. At $n = 12$ it gives
  28 against the true 27, one too many.
- **Corollary 2(a), page 156.** "For each $k \ge 5$,
  $f_k(n) > \frac{k(k-1)-2}{2k-3}(n-k)$ for infinitely many $n$." This is the
  rate the thesis quotes as $c_m \ge \frac{m(m-1)-2}{2m-3}$.
- **The recursive construction, proof of Corollary 2(a), page 156.** $G^0$ is
  $K_k$ with an edge deleted. $G^m$ is built from $G_1 = G_2 = G^0$ and
  $G_3 = G^{m-1}$ by the three-way identification of Lemma 5 (page 155), whose
  Figure 1 draws the three graphs glued in a cycle. The paper's counts are
  $n(G^m) = k + (2k-3)m$ and $e(G^m) = (k(k-1)-2)(m + \tfrac12)$, so each step
  adds $2k-3$ vertices and $k(k-1)-2$ edges. The thesis says exactly this with
  its own $m$ in place of the paper's $k$.
- **The threshold at which the recursion beats $m/2$.** Comparing
  $e(G^j)$ with $\tfrac{m}{2}(n-1)$ gives a difference of
  $j(m-4)/2 - 1$, positive exactly when $j > 2/(m-4)$. That gives the smallest
  members at 26, 24 and 18 vertices for $m = 5, 6, 7$, which is what the thesis
  prints.
- **The 3-connected case at $m = 5$.** Section 4 is headed "The number of edges
  required to guarantee the existence of 5-rails in 3-connected graphs" and
  proves Theorem 3 there.
- **The attributions of the disproof.** Page 143: Leonard [6] disproved the
  Bollobás-Erdős conjecture for $k = 5$, and Mader [9] showed
  $f_k(n) > \tfrac12 kn + m$ for some $n$ whenever $k > 5$. Page 144 states the
  disproof for all $k \ge 5$. The thesis credits Leonard first at $m = 5$ and
  Mader for $m \ge 6$.

## What this paper does not settle

Leonard's counterexample is cited in the thesis as an explicit graph on 57
vertices, from `Leonard73BE`. Sørensen and Thomassen cite the paper but do not
reproduce the graph, so that number is still carried from the secondary source.

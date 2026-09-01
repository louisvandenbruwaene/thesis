# Two unused m = 2 propositions cut from the appendix (2026-09-01)

Cut from `chapters/app_proofs.tex` in the appendix shortening pass:
`prop:mutual-unreachability` (mutually unreachable out-neighbourhoods),
its two-panel figure `fig:mutual-unreach`, and
`prop:disjoint-second-nbhd` (disjoint second out-neighbourhoods).

Both are one-line consequences of feasibility at `lambda^max <= 1`, so they
apply only at m = 2. Neither was cited by any later proof: the only reference
to either label anywhere in the thesis was the figure caption inside the first
one's own proof. They were written as structural context for
`open:decomposition` but the load-bearing proposition in that section is
`prop:two-hop-bipartite`, which stays in the appendix and drives the quadratic
branch count.

Kept verbatim so they can be reinstated without retyping.

```latex
\begin{proposition}[Mutually unreachable out-neighbourhoods]\label{prop:mutual-unreachability}
Let $D$ be a simple digraph with $\lec^{\max}_D \le 1$. For any vertex $u$ and distinct out-neighbours $v, w$ of $u$, there is no directed path from $v$ to $w$ in $D - u$.
\end{proposition}

\begin{proof}
If $P$ were a directed $v$--$w$ path avoiding $u$, then $u \to w$ and $u \to v \xrightarrow{P} w$ would be two arc-disjoint $u$-to-$w$ routes: the first uses only the arc $(u,w)$, the second starts with $(u,v)$ and continues along $P$, none of whose arcs touch $u$. This contradicts $\lec_D(u, w) \le 1$. The restriction to $D - u$ is not cosmetic, and \Cref{fig:mutual-unreach} draws both the argument and the reason for the restriction: in the digraph with arcs $(u,v)$, $(v,u)$, $(u,w)$ every local connectivity is $1$, yet $v \to u \to w$ reaches $w$ from $v$ through $u$.
\end{proof}

\begin{figure}[htbp]
\centering
\begin{subfigure}[b]{0.55\textwidth}
\centering
\begin{tikzpicture}[scale=1.0]
\node[apxlab] (u) at (0,0) {u};
\node[apxlab] (v) at (-1.7,1.3) {v};
\node[apxlab] (w) at (1.7,1.3) {w};
% out-arcs of u
\draw[aparc] (u)--(v);
\draw[aparc] (u)--(w);
% a forbidden v->w path through D-u (apex x as a full labelled node, like u,v,w)
\node[apxlab] (x) at (0,2.5) {x};
\draw[apredarc] (v)--(x);
\draw[apredarc] (x)--(w);
% label the two routes
\node[apname, text=KULblauw1!85] at (1.25,0.45) {$u\!\to\! w$};
\node[apname, text=vertexred, align=center] at (-2.35,2.55)
  {forbidden\\$v\rightsquigarrow w$};
\end{tikzpicture}
\caption{If a directed $v\rightsquigarrow w$ path (red) existed in $D-u$,
then $u\!\to\! w$ and $u\!\to\! v\rightsquigarrow w$ would be two
arc-disjoint $u$--$w$ routes, against $\lec(u,w)\le1$.}
\label{fig:mutual-unreach-main}
\end{subfigure}\hfill
\begin{subfigure}[b]{0.40\textwidth}
\centering
\begin{tikzpicture}[scale=1.0]
\node[apxlab] (u) at (0,0) {u};
\node[apxlab] (v) at (-1.4,1.4) {v};
\node[apxlab] (w) at (1.4,1.4) {w};
\draw[aparc] (u) to[bend left=14] (v);
\draw[aparc] (v) to[bend left=14] (u);
\draw[aparc] (u)--(w);
\node[apname, text=vertexred] at (0.05,1.65) {$v\!\to\! u\!\to\! w$};
\end{tikzpicture}
\caption{The counterexample $\{(u,v),(v,u),(u,w)\}$: $\lec^{\max}=1$,
yet $w$ \emph{is} reachable from $v$ only \emph{through} $u$.}
\label{fig:mutual-unreach-counter}
\end{subfigure}
\caption[Mutually unreachable out-neighbourhoods]{Why
\Cref{prop:mutual-unreachability} must exclude paths through $u$.
\textbf{(a)} For out-neighbours $v,w$ of $u$ in a digraph with
$\lec^{\max}\le1$, no $v\rightsquigarrow w$ path can avoid $u$: such a path
would combine with the lone arc $u\!\to\! w$ into two arc-disjoint routes.
\textbf{(b)} The restriction to $D-u$ is essential. In the three-vertex
digraph $\{(u,v),(v,u),(u,w)\}$ we have $\lec^{\max}=1$, yet $v$
reaches $w$ via $v\!\to\! u\!\to\! w$, a route that reuses the vertex $u$,
which the proposition allows.}
\label{fig:mutual-unreach}
\end{figure}

\begin{proposition}[Disjoint second out-neighbourhoods]\label{prop:disjoint-second-nbhd}
Let $D$ be a simple digraph with $\lec^{\max}_D \le 1$, let $u \in V$, and let $v_1 \ne v_2$ be out-neighbours of $u$. Then $(N^+(v_1) \setminus \{u\}) \cap (N^+(v_2) \setminus \{u\}) = \emptyset$.
\end{proposition}

\begin{proof}
A common out-neighbour $w \ne u$ would give the two arc-disjoint routes $u \to v_1 \to w$ and $u \to v_2 \to w$, contradicting $\lec_D(u, w) \le 1$.
\end{proof}

```

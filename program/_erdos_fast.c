/*
 * _erdos_fast.c  –  hot-path C helpers for erdos915_unified.py
 *
 * Compile:  gcc -O3 -march=native -shared -fPIC -o _erdos_fast.so _erdos_fast.c
 *
 * All functions take a flat row-major int32 array `mu` of size n*n.
 * Access:  mu[u*n + v]  is the capacity (multiplicity) of arc u->v.
 */

#include <stdint.h>
#include <string.h>
#include <stdlib.h>

/* ------------------------------------------------------------------ */
/* tiny_maxflow                                                         */
/* DFS Ford-Fulkerson; returns 1 iff max-flow(s,t) > cap.             */
/* Stops as soon as it finds cap+1 augmenting paths (early exit).     */
/* n <= 7 in practice; residual lives on the stack.                   */
/* ------------------------------------------------------------------ */
int tiny_maxflow(const int *mu, int n, int s, int t, int cap)
{
    /* local mutable residual; sized for n up to 16 (vertex-split at n=8) */
    int res[256];
    memcpy(res, mu, (size_t)(n * n) * sizeof(int));

    int flow = 0;
    while (flow <= cap) {
        /* DFS to find an augmenting path */
        int parent[16];
        for (int i = 0; i < n; i++) parent[i] = -1;
        parent[s] = s;

        /* stack-based DFS (max depth = n vertices) */
        int stack[16];
        int sp = 0;
        stack[sp++] = s;

        while (sp > 0 && parent[t] == -1) {
            int u = stack[--sp];
            for (int v = 0; v < n; v++) {
                if (parent[v] == -1 && res[u * n + v] > 0) {
                    parent[v] = u;
                    stack[sp++] = v;
                }
            }
        }

        if (parent[t] == -1)
            return 0;   /* max-flow <= cap */

        /* find bottleneck */
        int bottleneck = 1 << 30;
        for (int v = t; v != s; ) {
            int u = parent[v];
            int cap_uv = res[u * n + v];
            if (cap_uv < bottleneck) bottleneck = cap_uv;
            v = u;
        }

        /* augment */
        for (int v = t; v != s; ) {
            int u = parent[v];
            res[u * n + v] -= bottleneck;
            res[v * n + u] += bottleneck;
            v = u;
        }

        flow += bottleneck;
    }
    return 1;   /* max-flow > cap */
}

/* ------------------------------------------------------------------ */
/* max_connectivity_exceeds                                             */
/* Sweeps all pairs; returns 1 iff any pair has flow > k.             */
/* directed=1: all ordered pairs; directed=0: unordered pairs.        */
/* ------------------------------------------------------------------ */
int max_connectivity_exceeds(const int *mu, int n, int k, int directed)
{
    for (int s = 0; s < n; s++) {
        int start = directed ? 0 : s + 1;
        for (int t = start; t < n; t++) {
            if (s == t) continue;
            if (tiny_maxflow(mu, n, s, t, k))
                return 1;
        }
    }
    return 0;
}

/* ------------------------------------------------------------------ */
/* canonical_form_min                                                   */
/* Writes the lex-min row-major permutation of the n×n matrix into    */
/* out (n*n int32 values).  Uses Heap's algorithm to enumerate n!     */
/* permutations.  At n=7: 5040 iterations × 49 ints each.            */
/* ------------------------------------------------------------------ */
void canonical_form_min(const int *mu, int n, int *out)
{
    int perm[7], best[49], cand[49];
    int c[7];    /* Heap's algorithm counters */
    int nn = n * n;

    for (int i = 0; i < n; i++) { perm[i] = i; c[i] = 0; }

    /* identity permutation is the first candidate */
    for (int r = 0; r < n; r++)
        for (int col = 0; col < n; col++)
            best[r * n + col] = mu[perm[r] * n + perm[col]];

    /* Heap's algorithm */
    int i = 1;
    while (i < n) {
        if (c[i] < i) {
            /* swap */
            if (i % 2 == 0) {
                int tmp = perm[0]; perm[0] = perm[i]; perm[i] = tmp;
            } else {
                int tmp = perm[c[i]]; perm[c[i]] = perm[i]; perm[i] = tmp;
            }

            /* build candidate permuted matrix */
            for (int r = 0; r < n; r++)
                for (int col = 0; col < n; col++)
                    cand[r * n + col] = mu[perm[r] * n + perm[col]];

            /* update best if cand is lex-smaller */
            if (memcmp(cand, best, (size_t)nn * sizeof(int)) < 0)
                memcpy(best, cand, (size_t)nn * sizeof(int));

            c[i]++;
            i = 1;
        } else {
            c[i] = 0;
            i++;
        }
    }

    memcpy(out, best, (size_t)nn * sizeof(int));
}

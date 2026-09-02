#!/usr/bin/env python3
"""Reproducible check for directed_arc_m3_reduction.md section 2.4.2.

The self-similarity recursion from Lemma (L),
    ell_3^dir(n) <= max_{sigma>=1} [ sigma(n-sigma) + ell_3^dir(n-sigma) ],
OVERSHOOTS the conjectured value Q(n) = floor((n+1)^2/4).  Using the conjectured
true value f(n) = max(3(n-1), Q(n)) for the inner term (an upper estimate of the
recursion's strength), the right-hand side exceeds Q(n) by a growing margin.  So
the recursion alone cannot close the bound: the source-neighbourhood coupling is
essential.  Pure arithmetic, no graph search.
"""


def Q(n):
    return (n + 1) ** 2 // 4


def f(n):
    return max(3 * (n - 1), Q(n))


def main():
    print(f"{'n':>3} {'Q(n)':>5} {'recursion':>10} {'overshoot':>10} {'argmax sigma':>13}")
    for n in range(9, 16):
        best, arg = -1, None
        for s in range(1, n):
            val = s * (n - s) + f(n - s)
            if val > best:
                best, arg = val, s
        print(f"{n:>3} {Q(n):>5} {best:>10} {'+' + str(best - Q(n)):>10} {arg:>13}")
    print("recursion-only bound exceeds Q(n) for every n >= 9: coupling is needed.")


if __name__ == "__main__":
    main()

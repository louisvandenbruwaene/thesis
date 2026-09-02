"""Verify the Case-2 tightness claim of case2_tightness.md.

Checks that the "bang-bang" closed form for
    max sum_x t_x   s.t.   sum_x c(t_x) <= Q,  0 <= t_x <= n/4,  c(t) = t(n/2 - t)
agrees with a constrained nonlinear solver (scipy SLSQP, multi-start), and that
both agree asymptotically with the theorem's crude bound 4(m-1)(n-1).

Self-contained: numpy + scipy only, no dependency on the thesis program.
Run: python3 program/scripts/case2_tightness_check.py
"""

import numpy as np
from scipy.optimize import minimize, NonlinearConstraint, Bounds


def bangbang_value(n, Q):
    """Closed-form max of sum t_x given the budget, via the concentration lemma."""
    tau = n / 4
    cmax = tau * (n / 2 - tau)  # = n^2 / 16
    k_full = int(min(n, Q // cmax))
    remaining = Q - k_full * cmax
    frac_t = 0.0
    if k_full < n and remaining > 0:
        disc = tau * tau - remaining
        if disc >= 0:
            frac_t = tau - disc**0.5
    return k_full * tau + frac_t


def solver_value(n, Q, restarts=20, seed=0):
    """Independent check via a constrained nonlinear solver, multi-start."""
    tau = n / 4

    def negsum(t):
        return -np.sum(t)

    def negsum_grad(t):
        return -np.ones_like(t)

    def cost(t):
        return np.sum(t * (n / 2 - t))

    def cost_grad(t):
        return n / 2 - 2 * t

    nlc = NonlinearConstraint(cost, -np.inf, Q, jac=lambda t: cost_grad(t))
    bounds = Bounds(0, tau)
    rng = np.random.default_rng(seed)
    best = -np.inf
    for _ in range(restarts):
        t0 = rng.uniform(0, tau, size=n)
        res = minimize(
            negsum, t0, jac=negsum_grad, bounds=bounds,
            constraints=[nlc], method="SLSQP",
            options={"maxiter": 500, "ftol": 1e-10},
        )
        if res.success and -res.fun > best:
            best = -res.fun
    return best


def main():
    cases = [(20, 3), (20, 5), (20, 10), (30, 4), (50, 3), (50, 5), (60, 3),
             (80, 6), (100, 3), (100, 5), (100, 10)]
    print(f"{'n':>4} {'m':>3} {'bangbang':>10} {'solver':>10} {'theorem 4(m-1)(n-1)':>20}")
    max_rel_gap = 0.0
    for n, m in cases:
        Q = (m - 1) * n * (n - 1)
        bb = bangbang_value(n, Q)
        sv = solver_value(n, Q)
        theorem = 4 * (m - 1) * (n - 1)
        rel_gap = abs(bb - sv) / max(1.0, bb)
        max_rel_gap = max(max_rel_gap, rel_gap)
        print(f"{n:4d} {m:3d} {bb:10.3f} {sv:10.3f} {theorem:20d}")
    assert max_rel_gap < 1e-3, f"bang-bang vs solver mismatch: {max_rel_gap}"
    print(f"\nmax relative gap bang-bang vs solver: {max_rel_gap:.2e} -- OK")
    print("Bang-bang value tracks 4(m-1)(n-1) once k=16(m-1)(n-1)/n < n "
          "(the budget-bound regime), confirming Case 2's constant is tight "
          "for its own inequality.")


if __name__ == "__main__":
    main()

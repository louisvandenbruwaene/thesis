"""OPTIONAL SECOND RUN: the same question one route-limit higher, m = 4.

    python3 run_fact_a4.py

Only worth starting once run_fact_a.py has returned INFEASIBLE. The thesis
closes the m = 4 chain the same way it closes m = 3, and the base fact it needs
is L_4^dir(7) = 36, i.e. no 37-arc example on 7 vertices.

This one is strictly harder than fact (a): multiplicities now range over
{0,1,2,3} instead of {0,1,2}, so the search space per pair is 16 states rather
than 9. Treat a LIMIT verdict as normal rather than as a failure.
"""

import sys
import time
import platform

from erdos915_unified import prove_integral_arc_bound

N, M, TARGET = 7, 4, 37
TIME_LIMIT = 60 * 60 * 48          # 48 hours


def main():
    import pulp
    if not pulp.GUROBI_CMD(msg=0).available():
        print("Gurobi is not usable on this machine, so this run would not\n"
              "finish. Please run `python3 check_setup.py` first, which says\n"
              "exactly what is missing. Nothing has been started.")
        return 1

    header = (
        f"Fact (a4):  is there a 37-arc feasible directed multigraph on 7 vertices?\n"
        f"  n = {N}, m = {M}, target = {TARGET}, cap = {M-1} routes per pair\n"
        f"  time limit {TIME_LIMIT/3600:.0f} h,  machine {platform.node()}\n"
        f"  started {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(header, flush=True)
    print("-" * 70 + "\nSolver log follows.\n", flush=True)

    t0 = time.time()
    verdict = prove_integral_arc_bound(
        N, M, TARGET, time_limit=TIME_LIMIT,
        use_gurobi=True, show_solver_log=True,
    )
    elapsed = time.time() - t0

    meaning = {
        "INFEASIBLE": ("The result we wanted: L_4^dir(7) = 36, which is the base\n"
                       "  fact the m = 4 chain needs."),
        "FEASIBLE": ("Unexpected. A 37-arc example exists and the m = 4 picture\n"
                     "  needs rethinking. Please send this output back."),
        "LIMIT": ("Undecided within the time limit. Nothing proved either way.\n"
                  "  This is the likely outcome and is not a failure."),
    }[verdict]

    report = (f"\n{'=' * 70}\nVERDICT: {verdict}      ({elapsed/60:.1f} minutes)\n"
              f"{'=' * 70}\n  {meaning}\n")
    print(report, flush=True)
    with open("fact_a4_result.txt", "w") as fh:
        fh.write(header + "\n" + report)
    print("Written to fact_a4_result.txt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""THE MAIN RUN: settle L_3^dir(7) = 24, the last open step of the m = 3 chain.

    python3 run_fact_a.py

Asks a mixed-integer program whether any directed multigraph on 7 vertices,
with multiplicities in {0,1,2} and no pair of vertices joined by 3 arc-disjoint
routes, can carry 25 arcs. INFEASIBLE is the answer we expect and the one that
settles it, because 24 arcs are already known to be achievable.

The verdict is printed and also written to fact_a_result.txt. Expect minutes to
a few hours with Gurobi. Run check_setup.py first.
"""

import sys
import time
import platform

from erdos915_unified import prove_integral_arc_bound

N, M, TARGET = 7, 3, 25
TIME_LIMIT = 60 * 60 * 24          # 24 hours; raise if it returns LIMIT


def main():
    import pulp
    if not pulp.GUROBI_CMD(msg=0).available():
        print("Gurobi is not usable on this machine, so this run would not\n"
              "finish. Please run `python3 check_setup.py` first, which says\n"
              "exactly what is missing. Nothing has been started.")
        return 1

    header = (
        f"Fact (a):  is there a 25-arc feasible directed multigraph on 7 vertices?\n"
        f"  n = {N}, m = {M}, target = {TARGET}, cap = {M-1} routes per pair\n"
        f"  time limit {TIME_LIMIT/3600:.0f} h,  machine {platform.node()},"
        f" python {sys.version.split()[0]}\n"
        f"  started {time.strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(header, flush=True)
    print("-" * 70, flush=True)
    print("Solver log follows. No news is normal: it prints when it finishes.\n",
          flush=True)

    t0 = time.time()
    verdict = prove_integral_arc_bound(
        N, M, TARGET,
        time_limit=TIME_LIMIT,
        use_gurobi=True,            # fail loudly rather than fall back to CBC
        show_solver_log=True,
    )
    elapsed = time.time() - t0

    if verdict == "INFEASIBLE":
        meaning = (
            "INFEASIBLE is the result we wanted.\n"
            "  No 25-arc example exists, so L_3^dir(7) = 24.\n"
            "  That closes the m = 3 directed multigraph problem for EVERY n,\n"
            "  because the thesis reduces all larger n to exactly this fact."
        )
    elif verdict == "FEASIBLE":
        meaning = (
            "FEASIBLE would be a genuine surprise.\n"
            "  It would mean a 25-arc example exists, contradicting the hand\n"
            "  proof, and the conjecture would need revisiting. Please send\n"
            "  this output back rather than assuming it is a mistake."
        )
    else:
        meaning = (
            "LIMIT means the solver ran out of time without deciding.\n"
            "  Nothing is proved or disproved. Raise TIME_LIMIT at the top of\n"
            "  this file, or run it on a bigger machine, and try again."
        )

    report = (
        f"\n{'=' * 70}\nVERDICT: {verdict}      ({elapsed/60:.1f} minutes)\n"
        f"{'=' * 70}\n  {meaning}\n"
    )
    print(report, flush=True)

    with open("fact_a_result.txt", "w") as fh:
        fh.write(header + "\n" + report + f"\nfinished {time.strftime('%c')}\n")
    print("Written to fact_a_result.txt. Please send that file back.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

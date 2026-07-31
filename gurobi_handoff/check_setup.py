"""Check the machine is ready BEFORE starting the long run.

Runs in a few seconds. It verifies that Python, the libraries, and Gurobi are
all usable, and it re-proves two small facts whose answers are already known,
so that a wrong answer here means the setup is broken rather than the
mathematics being wrong.

    python3 check_setup.py
"""

import sys


def main():
    print("=" * 68)
    print("SETUP CHECK")
    print("=" * 68)

    print(f"\nPython {sys.version.split()[0]}")
    if sys.version_info < (3, 10):
        print("  !! Python 3.10 or newer is needed (the code uses `X | None` types).")
        return 1

    try:
        import numpy, scipy                                   # noqa: F401
        print(f"numpy {numpy.__version__}, scipy {scipy.__version__}  OK")
    except ImportError as exc:
        print(f"  !! missing: {exc}.   Fix:  pip install numpy scipy")
        return 1

    try:
        import pulp
        print(f"pulp {pulp.__version__}  OK")
    except ImportError:
        print("  !! missing pulp.   Fix:  pip install 'pulp<4'")
        return 1

    print("\nLooking for Gurobi...")
    solver = pulp.GUROBI_CMD(msg=0)
    if solver.available():
        print("  Gurobi FOUND and licensed. This is the one that matters.")
        gurobi_ok = True
    else:
        print("  !! Gurobi NOT found, or its licence is not active.")
        print("     The run will still work but will use CBC, which is far too")
        print("     weak to finish this problem. Check that `gurobi_cl --version`")
        print("     runs, and that the academic licence is activated while on")
        print("     the university network.")
        gurobi_ok = False

    print("\nRe-proving two facts whose answers are already known...")
    from erdos915_unified import prove_integral_arc_bound

    # L_3^dir(4) = 12: 12 arcs are achievable, 13 are not.
    a = prove_integral_arc_bound(4, 3, 12, time_limit=120)
    b = prove_integral_arc_bound(4, 3, 13, time_limit=120)
    print(f"  n=4, m=3, target 12 -> {a:11s} (expected FEASIBLE)")
    print(f"  n=4, m=3, target 13 -> {b:11s} (expected INFEASIBLE)")

    if (a, b) != ("FEASIBLE", "INFEASIBLE"):
        print("\n  !! WRONG ANSWER on a known case. Do not trust a long run on")
        print("     this machine until that is understood.")
        return 1

    print("\n" + "=" * 68)
    if gurobi_ok:
        print("READY.  Next:  python3 run_fact_a.py")
    else:
        print("Software is fine, but Gurobi is not usable yet, and without it")
        print("the main run will not finish. Sort the licence out first.")
    print("=" * 68)
    return 0 if gurobi_ok else 1


if __name__ == "__main__":
    sys.exit(main())

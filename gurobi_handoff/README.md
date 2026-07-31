# One Gurobi run to close the m = 3 directed multigraph problem

**What is being asked:** whether a directed multigraph on 7 vertices, with
multiplicities in `{0,1,2}` and `lambda^max <= 2` (no pair of vertices joined by
3 arc-disjoint routes), can carry **25** arcs.

**The answer we expect is INFEASIBLE**, which gives `L_3^dir(7) = 24`, since 24
arcs are already known to be achievable.

**Why it matters:** the thesis reduces the whole infinite family, every `n`, to
exactly this one finite fact. An attachment lemma and a conditional odd-step
theorem propagate the value and the extremal characterisation upwards from
`n = 7`, so INFEASIBLE here turns a conjecture into a theorem for every `n` at
once. It is the last open step of that chain.

**Why it needs you:** the encoding is a mixed-integer program. The free CBC
solver bundled with `pulp` cannot close it (measured, 2026-06-16), and neither
can the exhaustive combinatorial search running locally, which has been going
over 13 hours without a verdict. Gurobi solves this class of problem far
better, and it is free on an academic licence from a university network.

---

## Instructions

Everything needed is in this folder. Nothing outside it is used.

```bash
# 1. dependencies (a virtual environment is fine, not required)
pip install numpy scipy 'pulp<4'

# 2. verify the machine is ready. Takes seconds.
python3 check_setup.py

# 3. the real run.
python3 run_fact_a.py
```

`check_setup.py` confirms Python, the libraries and Gurobi are usable, and
re-proves two small facts whose answers are already known, so a wrong answer
there means the setup is broken rather than the mathematics being wrong. Please
do not skip it: it is far better to find a licence problem in five seconds than
five hours in.

`run_fact_a.py` prints the verdict and writes `fact_a_result.txt`. **Please send
that file back.** The solver log is left on so there is something to watch;
long silences are normal.

Expect minutes to a few hours. The time limit is set to 24 hours, and a `LIMIT`
verdict just means it needs longer or a bigger machine, not that anything is
wrong.

`run_fact_a4.py` is an optional second, harder run at `m = 4`, worth starting
only if the first returns INFEASIBLE. A `LIMIT` there is the likely outcome and
is not a failure.

## The three possible verdicts

| Verdict | Meaning |
|---|---|
| `INFEASIBLE` | **The expected result.** No 25-arc example exists, so `L_3^dir(7) = 24` and the m = 3 problem closes for every `n`. |
| `FEASIBLE` | A genuine surprise: it would contradict a hand proof that has been checked twice. Please send the output back rather than assuming a mistake. |
| `LIMIT` | Ran out of time without deciding. Nothing is proved either way. Raise `TIME_LIMIT` at the top of the script or use a larger machine. |

## Notes

- Requires Python 3.10 or newer.
- `pulp` is pinned below 4.0 because 4.x is mid-way through an API rename.
- Gurobi is reached through `pulp`'s `GUROBI_CMD`, which calls the `gurobi_cl`
  command line, so a normal Gurobi install with an active licence is enough and
  `gurobipy` is not required. If `gurobi_cl --version` runs, this will work.
- `run_fact_a.py` passes `use_gurobi=True` deliberately, so it fails loudly if
  Gurobi is missing rather than silently falling back to CBC and running
  forever.
- `erdos915_unified.py` is the thesis program, unmodified. Only its MILP prover
  is exercised here. The optional C accelerator is not needed and its absence
  changes no answer.
- Nothing here writes outside this folder or needs network access.

## What is being solved, in one paragraph

For every ordered pair `(s,t)` the program *chooses* a cut, using binary
indicators for which side each vertex falls on, and a helper variable picks up
the weight of each arc that crosses that cut. Constraining the crossing total to
at most `m-1` says exactly that `maxflow(s,t) <= m-1`, which by Menger's theorem
says the pair has at most `m-1` arc-disjoint routes. Adding the requirement that
the multiplicities total at least 25 asks for a feasible 25-arc example, so
INFEASIBLE is a genuine proof that none exists rather than a failure to find
one. Several extra constraint families are switched on (two-hop bounds, deletion
bounds from smaller proved values, a degree-pair inequality, and a
degree-ordering symmetry break); each is proved valid in the thesis appendix, so
they speed the solver up without moving the answer.

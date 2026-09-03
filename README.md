# Erdős Problem 915

Master's thesis of Louis Vandenbruwaene, KU Leuven, supervised by Stijn Cambie.

This repository holds the two things the thesis hands a reader:

- `main.pdf` — the thesis.
- `program/` — the companion program, its tests, the standalone scripts, the
  recorded machine values and the run transcripts the computational audit cites.

Every file path printed in the thesis is relative to this repository and begins
with `program/`. `program/README.md` documents the program itself.

## Running the program

Create the environment with Python 3.14.6, the interpreter used for the recorded
runs, and install the pinned versions:

```bash
python3 -m venv .venv
.venv/bin/python3 -m pip install -r program/requirements-lock.txt
```

Then, from `program/`:

```bash
../.venv/bin/python3 erdos915_unified.py            # built-in self-check
../.venv/bin/python3 -m unittest discover -s tests  # test suite
../.venv/bin/python3 make_figures.py                # redraw the figures
```

The core needs only NumPy and SciPy. PuLP backs the solver checks; Matplotlib
and NetworkX are optional and guarded. The two block sweeps additionally need
nauty's `geng` on `PATH`.

Appendix A.13 of the thesis gives the full audit instructions.

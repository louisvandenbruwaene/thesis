"""Test suite for the unified Erdos-915 program.

The tests import ``erdos915_unified`` from the parent directory, so we put that
directory on the path here, once, for every test module. The whole suite runs
with the standard library alone:

    cd program
    python -m unittest discover -s tests

(no pytest required, though pytest will also discover and run these if present).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

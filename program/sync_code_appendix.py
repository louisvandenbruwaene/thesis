"""Keep Appendix C's line ranges in step with the program.

The code appendix splits erdos915_unified.py at its own section banners, using
explicit line numbers in \\lstinputlisting. Those numbers are correct only for
one version of the file: editing the program by even one line silently shifts
every range below the edit, so the appendix would print the right code under
the wrong headings.

This script recomputes the boundaries from the banners themselves and rewrites
the numbers in chapters/app_code.tex.

    python3 sync_code_appendix.py           # check only, non-zero exit if stale
    python3 sync_code_appendix.py --write   # rewrite the ranges

Run it after any edit to erdos915_unified.py.
"""

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "erdos915_unified.py"
APPENDIX = HERE.parent / "chapters" / "app_code.tex"

# Each split point is identified by a line that STARTS with this text. The
# order here is the order the appendix prints them.
MARKERS = [
    "######################################################################",  # ch1
    "######################################################################",  # ch2
    "######################################################################",  # ch3
    "######################################################################",  # ch4
    "# --- FIGURES:",
    "# --- ENUMERATION LANDSCAPES:",
    "# --- OPEN-VARIANT EXPLORATION:",
    "# --- GALLERY:",
    "def _run_checks()",
]


def boundaries():
    """Return the first line of each appendix part, then the file length."""
    lines = SOURCE.read_text().splitlines()
    total = len(lines)
    starts, search_from = [], 0
    banner_seen = 0
    for marker in MARKERS:
        for i in range(search_from, total):
            if not lines[i].startswith(marker):
                continue
            # The four identical banner rules come in pairs (open and close of
            # the comment box); we want the opening one of each pair, so skip
            # any hit that is the closing rule of the banner just taken.
            if marker.startswith("#####"):
                banner_seen += 1
                if banner_seen % 2 == 0:      # this is a closing rule
                    continue
            starts.append(i + 1)              # 1-indexed
            search_from = i + 1
            break
        else:
            raise SystemExit(f"marker not found in the program: {marker!r}")
    return starts, total


def expected_ranges():
    starts, total = boundaries()
    edges = [1] + starts + [total + 1]
    return [(edges[i], edges[i + 1] - 1) for i in range(len(edges) - 1)]


def main():
    write = "--write" in sys.argv
    want = expected_ranges()
    text = APPENDIX.read_text()

    pattern = re.compile(
        r"(firstnumber=)(\d+)(,\s*\n\s*linerange=\{)(\d+)-(\d+)(\})")
    found = list(pattern.finditer(text))

    if len(found) != len(want):
        raise SystemExit(
            f"appendix has {len(found)} ranged listings but the program splits "
            f"into {len(want)} parts. Fix chapters/app_code.tex by hand.")

    stale = []
    for match, (lo, hi) in zip(found, want):
        if (int(match.group(2)), int(match.group(4)), int(match.group(5))) != (lo, lo, hi):
            stale.append((match.group(0).split(",")[0], f"{lo}-{hi}"))

    if not stale:
        print(f"Appendix C is in step with the program "
              f"({len(want)} parts, {want[-1][1]} lines).")
        return 0

    print(f"{len(stale)} of {len(want)} listing ranges are stale:")
    for was, now in stale:
        print(f"   {was}  ->  should be {now}")

    if not write:
        print("\nRe-run with --write to fix.")
        return 1

    def repl(match, _it=iter(want)):
        lo, hi = next(_it)
        return f"{match.group(1)}{lo}{match.group(3)}{lo}-{hi}{match.group(6)}"

    APPENDIX.write_text(pattern.sub(repl, text))
    print("\nRewritten. Rebuild the thesis to pick the change up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

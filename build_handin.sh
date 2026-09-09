#!/bin/sh
# Build the hand-in bundle: main.pdf plus program/, and nothing else.
#
#     ./build_handin.sh
#
# The bundle is BUILT, never copied. `git archive` is what keeps the local
# .DS_Store, __pycache__, the untracked program/_erdos_fast.so and uncited scratch logs in
# program/logs/ out of it, and .gitattributes is what keeps program/CLAUDE.md,
# the program's development history, out of it. handin/ is gitignored, so it is
# a build product. An existing bundle is retained when a replacement is built.
# The tracked accelerator inside the frozen benchmark remains part of the bundle.
#
# The venv sits at the bundle root, matching the audit's instructions, so that
# `../.venv/bin/python3` resolves from program/. It is machine-specific and is
# not built here.
set -e
cd "$(dirname "$0")"

if [ -n "$(git status --porcelain)" ]; then
    echo "build_handin.sh: commit your work first, so the bundle has a source." >&2
    git status --short >&2
    exit 1
fi

stage=$(mktemp -d .handin-build.XXXXXX)
trap 'rm -rf "$stage"' 0
mkdir "$stage/bundle"
# Separate commands expose an archive failure instead of losing its exit status
# behind a successful tar invocation in a pipeline.
git archive --format=tar HEAD program > "$stage/program.tar"
tar -xf "$stage/program.tar" -C "$stage/bundle"
git show HEAD:main.pdf > "$stage/bundle/main.pdf"

# Last line of defence, the same one publish.sh runs: refuse to hand in a
# bundle carrying a working-notes file, whatever the path.
if find "$stage/bundle" -iname 'CLAUDE.md' -o -iname 'TASKS.md' -o -iname 'REVIEW*' \
        -o -iname 'SIMPLIFIED_AI_PROOFS*' -o -iname 'PLAN_*' -o -iname 'mistakes found*' \
        | grep -q .; then
    echo "build_handin.sh: refusing to build, a working-notes file reached the bundle:" >&2
    find "$stage/bundle" -iname 'CLAUDE.md' -o -iname 'TASKS.md' -o -iname 'REVIEW*' \
        -o -iname 'SIMPLIFIED_AI_PROOFS*' -o -iname 'PLAN_*' -o -iname 'mistakes found*' >&2
    exit 1
fi

if [ -e handin ] || [ -L handin ]; then
    mkdir -p old_stuff/builds
    previous=$(mktemp -d old_stuff/builds/handin.previous.XXXXXX)
    mv handin "$previous/handin"
    echo "Previous bundle retained in $previous/handin"
fi
mv "$stage/bundle" handin

echo "handin/ built from $(git rev-parse --short=12 HEAD):"
find handin -maxdepth 2 -mindepth 1 -not -path '*/__pycache__*' | sort | sed 's/^/  /'

#!/bin/sh
# Refresh the public repository, github.com/louisvandenbruwaene/thesis.
#
#     ./publish.sh
#
# main is the working branch. It tracks EVERYTHING and is pushed to the private
# `backup` remote only. The public repository is a generated snapshot carrying
# just what the thesis hands a reader: main.pdf, program/, README.md, the
# seminar deck in slides/ and the one-page popularising_summary/. Nothing
# is kept private by .gitignore any more; it is kept private by not being copied
# here. So if you ever want a file public, add it to the archive line below.
#
# Whole directories are copied, so only tracked files travel. slides/ and
# popularising_summary/ hold their sources and their built PDFs and nothing
# else: their LaTeX intermediates are gitignored, so no .aux or .log reaches
# the snapshot. Check that again if either directory gains a tracked file.
#
# The hand-in bundle is deliberately narrower. build_handin.sh still carries
# main.pdf and program/ alone, because the deck and the summary are separate
# faculty deliverables rather than part of the thesis submission.
#
# A plain `git push` goes to `backup`, never to origin: this script is the only
# thing that writes to the public repository.
set -e
cd "$(dirname "$0")"

if [ -n "$(git status --porcelain)" ]; then
    echo "publish.sh: commit your work first, so the snapshot has a source." >&2
    git status --short >&2
    exit 1
fi

src=$(git rev-parse --short=12 HEAD)
wt=.public-snapshot
stage=$(mktemp -d "$PWD/.publish-build.XXXXXX")
trap 'rm -rf "$stage"' 0
# Check archive creation before replacing anything in the public worktree.
git archive --format=tar HEAD main.pdf program README.md slides popularising_summary \
    > "$stage/snapshot.tar"

git fetch -q origin
git worktree remove --force "$wt" 2>/dev/null || true
git worktree add -q -B public "$wt" origin/main

# Replace the snapshot wholesale, so a file deleted on main disappears here too.
find "$wt" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
tar -xf "$stage/snapshot.tar" -C "$wt"

# Whole directories are copied above, so anything private living INSIDE one has
# to be named here. program/CLAUDE.md is the program's development history and
# is not part of the submission.
rm -f "$wt/program/CLAUDE.md"

# kulakbeamer.cls and its three page images are KU Leuven's corporate identity
# template, handed to members through the university's own templates page. The
# deck needs them to compile and they are tracked here so it always does, but
# they are KU Leuven's to distribute, not this repository's. slides/README.md
# tells a reader where to get them.
rm -f "$wt/slides/seminarie/kulakbeamer.cls" \
      "$wt/slides/seminarie/kuleuvenBackground.pdf" \
      "$wt/slides/seminarie/kuleuvenOutline.pdf" \
      "$wt/slides/seminarie/kuleuvenTitlepage.pdf" \
      "$wt/slides/seminarie/kuleuvenLogo.pdf"

# cheatsheet.tex/.pdf are Louis's own speaker notes for presenting the seminar
# deck, not a deliverable a reader should see.
rm -f "$wt/slides/seminarie/cheatsheet.tex" \
      "$wt/slides/seminarie/cheatsheet.pdf"

# Last line of defence: refuse to publish a snapshot carrying a working-notes
# file, whatever the path, rather than push and discover it afterwards.
if find "$wt" -iname 'CLAUDE.md' -o -iname 'TASKS.md' -o -iname 'REVIEW_*.md' \
        -o -iname 'SIMPLIFIED_AI_PROOFS*' -o -iname 'PLAN_*' -o -iname 'mistakes found*' \
        | grep -q .; then
    echo "publish.sh: refusing to publish, a working-notes file reached the snapshot:" >&2
    find "$wt" -iname 'CLAUDE.md' -o -iname 'TASKS.md' -o -iname 'REVIEW_*.md' \
        -o -iname 'SIMPLIFIED_AI_PROOFS*' -o -iname 'PLAN_*' -o -iname 'mistakes found*' >&2
    exit 1
fi

cd "$wt"
git add -A
if git diff --cached --quiet; then
    echo "publish.sh: public snapshot already matches $src, nothing to do."
else
    git commit -q -m "Published snapshot of $src"
    git push -q origin public:main
    echo "publish.sh: pushed public snapshot of $src"
fi
cd ..
git worktree remove --force "$wt"

echo "public tree is now:"
git ls-tree -r --name-only public | sed 's/^/  /' | grep -v '^  program/.' | head
echo "  program/  ($(git ls-tree -r --name-only public | grep -c '^program/') files)"

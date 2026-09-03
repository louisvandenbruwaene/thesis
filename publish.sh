#!/bin/sh
# Refresh the public repository, github.com/louisvandenbruwaene/thesis.
#
#     ./publish.sh
#
# main is the working branch. It tracks EVERYTHING and is pushed to the private
# `backup` remote only. The public repository is a generated snapshot carrying
# just what the thesis hands a reader: main.pdf, program/ and README.md. Nothing
# is kept private by .gitignore any more; it is kept private by not being copied
# here. So if you ever want a file public, add it to the archive line below.
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

git fetch -q origin
git worktree remove --force "$wt" 2>/dev/null || true
git worktree add -q -B public "$wt" origin/main

# Replace the snapshot wholesale, so a file deleted on main disappears here too.
find "$wt" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
git archive HEAD main.pdf program README.md | tar -x -C "$wt"

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

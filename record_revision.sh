#!/bin/sh
# Record the clean source snapshot used for a PDF build.  The generated
# revision.tex is read by preamble.tex and printed in the computational audit;
# the tag names the same source commit.  The built PDF is an output of that
# source commit, so this records the source revision rather than claiming the
# necessarily later artifact commit has the same hash.
#
# Run this AFTER the last content change and BEFORE the final build:
#
#     ./record_revision.sh && latexmk -pdf main.tex
#
# The build then carries the hash of the source commit it was built from. Pass a
# tag name to override the default.
#
# A tag that is already in the repository is never moved. It may be printed
# inside a PDF that has already been handed in, and a recorded revision that can
# silently come to mean a different commit records nothing at all. Record a new
# build under a new name.
set -e
cd "$(dirname "$0")"

case "$1" in
    -*)
        echo "record_revision.sh: unknown option '$1'." >&2
        echo "Usage: ./record_revision.sh [tag-name]" >&2
        exit 2
        ;;
esac

tag=${1:-submitted}

# --porcelain, not `git diff`: an untracked .tex or figure is invisible to a
# diff, and the PDF being recorded may well have been built from it. Anything
# git would not carry to another machine makes this snapshot unreproducible.
if [ -n "$(git status --porcelain)" ]; then
    echo "record_revision.sh: the working tree is not clean." >&2
    echo "Commit or remove the following, so the recorded hash matches what was built:" >&2
    git status --short >&2
    exit 1
fi

if git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
    echo "record_revision.sh: the tag '$tag' already exists and will not be moved." >&2
    echo "Record this build under a new name, e.g. ./record_revision.sh ${tag}-2." >&2
    exit 1
fi

commit=$(git rev-parse HEAD)
short=$(git rev-parse --short=12 HEAD)
date=$(git log -1 --format=%cs HEAD)

cat > revision.tex <<TEX
% Written by record_revision.sh. Do not edit by hand.
\\renewcommand{\\thesistag}{$tag}
\\renewcommand{\\thesiscommit}{\\texttt{$short} (tag \\texttt{$tag}, $date)}
TEX

git tag "$tag" "$commit"

echo "revision.tex written: $short (tag $tag, $date)"
echo "Now rebuild:  latexmk -pdf main.tex"
echo "Then push the tag:  git push origin $tag"

#!/bin/sh
# Record the submitted snapshot: write the current commit into revision.tex, which
# main.tex prints in the computational audit, and tag the same commit so the hash
# in the PDF and the tag in the repository can never disagree.
#
# Run this AFTER the last content change and BEFORE the final build:
#
#     ./record_revision.sh && latexmk -pdf main.tex
#
# The build then carries the hash of the commit it was built from. Pass a tag name
# to override the default.
set -e
cd "$(dirname "$0")"

tag=${1:-submitted}

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "record_revision.sh: the working tree is dirty." >&2
    echo "Commit or stash first, so the recorded hash matches what was built." >&2
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

git tag -f "$tag" "$commit"

echo "revision.tex written: $short (tag $tag, $date)"
echo "Now rebuild:  latexmk -pdf main.tex"
echo "Then push the tag:  git push --force origin $tag"

#!/bin/sh
# Pre-hand-in consistency gate for the thesis sources.  Run it before any
# recorded build; latexmk exits 0 on every defect it checks for.
#
#     ./check_consistency.sh
#
# 1. Proof status. Unchecked AI statements and dependent deductions must be
#    conjectures with proofs, and their appendix headings must retain that status.
# 2. Dangling references.  Cleveref prints ?? with no warning and latexmk still
#    exits 0, so the log is not the gate, the PDF text is.
# 3. Cleveref naming.  Every reference here goes through \Cref, and a mixed-type
#    group such as \Cref{prop:a,thm:b} capitalises only its FIRST group, taking
#    the lowercase \crefname for the rest.  The lowercase slot therefore holds
#    the capitalised name; if that is ever reverted, mixed groups start printing
#    "Proposition A.37 and theorem 1.11".
# 4. Floats.  Every figure and table must carry a label and a caption, every
#    file it pulls in must exist, and something must \Cref it.  A float on a
#    [p] page that nothing references is reachable only by where LaTeX floated
#    it, and latexmk reports nothing.
set -e
cd "$(dirname "$0")"
PY=.venv/bin/python3
status=0

"$PY" - <<'PYEOF' || status=1
import re, sys, glob
ch1 = open('chapters/ch1_basecases.tex', encoding='utf-8').read()
app = open('chapters/app_proofs.tex', encoding='utf-8').read()
bad = 0

from check_proof_status import check_proof_status
errors = check_proof_status({
    'chapters/ch1_basecases.tex': ch1,
    'chapters/app_proofs.tex': app,
})
for error in errors:
    print(error)
bad = bool(errors)

pre = open('preamble.tex', encoding='utf-8').read()
for m in re.finditer(r'\\crefname\{([a-z]+)\}\{([^}]*)\}\{([^}]*)\}', pre):
    kind, sg, pl = m.groups()
    if sg[:1].islower() or pl[:1].islower():
        print("LOWERCASE \\crefname: %s -> {%s}{%s}; a mixed \\Cref group will "
              "print it uncapitalised" % (kind, sg, pl)); bad = 1
for m in re.finditer(r'\\cref\{', ''.join(
        open(f, encoding='utf-8').read() for f in ['main.tex'] + sorted(glob.glob('chapters/*.tex')))):
    print("LOWERCASE \\cref USED: the capitalised \\crefname slots would misprint it"); bad = 1

import os
sources = {f: open(f, encoding='utf-8').read()
           for f in ['main.tex'] + sorted(glob.glob('chapters/*.tex'))}
everything = '\n'.join(sources.values())
for name, text in sources.items():
    for env in ('figure', 'sidewaysfigure', 'table'):
        for m in re.finditer(r'\\begin\{' + env + r'\*?\}(.*?)\\end\{' + env + r'\*?\}', text, re.S):
            body = m.group(1)
            label = re.search(r'\\label\{([^}]+)\}', body)
            if not label:
                print("UNLABELLED FLOAT: %s: %s" % (name, env)); bad = 1; continue
            label = label.group(1)
            if not re.search(r'\\caption', body):
                print("FLOAT WITHOUT CAPTION: %s" % label); bad = 1
            for target in re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', body):
                if not os.path.exists(target):
                    print("FLOAT MISSING FILE: %s wants %s" % (label, target)); bad = 1
            for target in re.findall(r'\\input\{([^}]+)\}', body):
                if not (os.path.exists(target) or os.path.exists(target + '.tex')):
                    print("FLOAT MISSING FILE: %s wants %s" % (label, target)); bad = 1
            if not re.search(r'\\Cref\{[^}]*\b' + re.escape(label) + r'\b', everything):
                print("FLOAT NEVER \\Cref-ED: %s" % label); bad = 1
sys.exit(bad)
PYEOF

if [ -f main.pdf ]; then
    n=$(pdftotext main.pdf - | LC_ALL=C grep -a -c '??' || true)
    [ "$n" = "0" ] || { echo "DANGLING REFS: $n occurrences of ?? in main.pdf"; status=1; }
fi

[ "$status" = "0" ] && echo "check_consistency: clean"
exit $status

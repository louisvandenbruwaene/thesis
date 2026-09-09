# Seminar slides

The deck is `seminarie/seminarie.tex`, with `seminarie/seminarie.pdf` built
from it. It draws its diagrams in TikZ and uses the thesis logo from the
repository root, so build it from its own directory:

```sh
cd slides/seminarie
latexmk -pdf seminarie.tex
```

The committed PDF is rebuilt whenever the source changes, so the two always
match. Rebuild it again after editing the deck.

The deck states the same bounds, statuses and computed values as the thesis,
and marks each one PROVED, PROPOSED or OPEN on the same basis: PROPOSED means
a conjecture whose proposed proof the author has not verified line by line,
exactly as the thesis's Contribution Statement defines it. When a claim moves
in the thesis, it has to move here too.

Earlier decks and their shared styles are kept outside this directory as
historical drafts. They are not maintained, and their claims and relative
paths may be outdated.

# Seminar slides

The deck is `seminarie/seminarie.tex`, with `seminarie/seminarie.pdf` built
from it.

## Building it

The deck uses KU Leuven's own corporate beamer template, `kulakbeamer.cls`
with its `kul` option, so it needs five files beside the source:

    kulakbeamer.cls
    kuleuvenBackground.pdf
    kuleuvenOutline.pdf
    kuleuvenTitlepage.pdf
    kuleuvenLogo.pdf

Those are KU Leuven's to distribute rather than this repository's, so the
public snapshot does not carry them. KU Leuven members get them from the
university's presentation templates page, linked from the header of the class
file itself. With the five in `seminarie/`:

```sh
cd slides/seminarie
latexmk -pdf seminarie.tex
```

The committed PDF is rebuilt whenever the source changes, so the two always
match. Rebuild it again after editing the deck.

## What the deck has to keep in step with

It states the same bounds, statuses and computed values as the thesis, and
marks each one PROVED, PROPOSED or OPEN on the same basis: PROPOSED means a
conjecture whose proposed proof the author has not verified line by line,
exactly as the thesis's Contribution Statement defines it. When a claim moves
in the thesis, it has to move here too.

Earlier decks and their shared styles are kept outside this directory as
historical drafts. They are not maintained, and their claims and relative
paths may be outdated.

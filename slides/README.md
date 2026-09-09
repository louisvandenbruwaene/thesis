# Seminar slides

The active deck is `seminarie/seminarie.tex`. It draws its diagrams in TikZ
and uses the thesis logo from the repository root.

To build it when document execution is wanted:

```sh
cd slides/seminarie
latexmk -pdf seminarie.tex
```

`seminarie/seminarie.pdf` was rebuilt with the 9 September 2026 source-review
corrections in commit `8e901ce`. Rebuild it again after editing the deck source.

Earlier decks (`talk_10`, `talk_60`, `final_presentation`, and
`seminarie/main.tex`) and their shared styles are in `../old_stuff/slides/`.
They are historical drafts; their claims and relative paths may be outdated.
See `../REVIEW_2026-09-09.md` for the current corrections and remaining decisions.

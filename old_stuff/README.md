# Historical material

This is the single archive created during the 9 September 2026 review.
The active thesis starts at `../main.tex`; the active slides are
`../slides/seminarie/seminarie.tex`. Archived claims are historical, not an
alternative statement of the current thesis.

| Location | Previous location / contents |
| --- | --- |
| `offcuts.tex` | Root document containing removed passages |
| `figures/` | Unused root `figures/` assets and their old caches |
| `research_notes/` | Former root research notes, including external draft proofs |
| `notes/` | Old root plans, reviews, tasks and development history |
| `notes/program/CLAUDE.md` | Former program development history |
| `notes/thesis-review-2026-09-07.md` | Loose thesis review recovered from the parent directory |
| `slides/` | Earlier decks, preserving their former structure within `slides/` |
| `references/` | Local third-party/reference PDFs formerly at the root |
| `builds/` | Old hand-in bundles, LaTeX intermediates, scratch run logs and local working files |

The old hand-in bundles retain their complete contents. The former current
`handin/` is also here because its PDF predates the source fixes. A future
`build_handin.sh` invocation will create a fresh root `handin/` and store its
predecessor under `old_stuff/builds/`.

`builds/` and `references/` remain local and ignored by Git. Other moved files
remain available for tracking in the private source repository. Public
snapshot creation includes only `main.pdf`, `program/` and the root README.

Archived LaTeX files retain their original relative paths; they are not
standalone build targets in this layout. Restore the original layout from
Git in a separate checkout if an old document needs rebuilding. Bibliography
entries used only by offcuts are retained in the active `ref.bib` for that purpose.

Recorded machine data, frozen benchmark source snapshots, cited transcripts,
and the NPZ enumeration evidence remain in the active `program/` tree.
Only disposable Python caches, macOS metadata and empty scratch directories
were deleted outright.

# The content matrix

`var/html/index.html` is **generated**. Edit the words here, never the HTML.

    TILLANDSIAS_CLONE=/path/to/a/tillandsias/checkout/at/the/pinned/tag \
      python3 scripts/build-matrix.py

Without `TILLANDSIAS_CLONE` the page still builds; with it, every footnote target is
checked — the file must exist and the line range must be inside it — and the build
prints anything that does not resolve. Do a checked build before publishing: a
footnote that 404s is worse than no footnote.

One file per explanation level. Each is a single merged narrative — what the thing
is and how it works, woven together, because splitting them read as two disconnected
essays. The reader knows nothing about the project.

## The dialect

Small on purpose. Anything not listed here is not supported.

| Syntax | Renders as |
|---|---|
| `## Heading` / `### Sub` | section headings |
| `- item` / `1. item` | bullets / numbered list |
| `**bold**` `*italic*` `` `code` `` | inline emphasis |
| `> GREEN: …` | 🟢 something verified and working |
| `> RED: …` | 🔴 something incomplete, pending, wrong or overclaimed |
| `> PATH: …` | → the recorded path to green for the RED above it |
| `> NOTE: …` | a neutral aside |
| `$x$` and `$$x$$` | inline / display maths, rendered by KaTeX |
| `@fig:name` | a diagram from `scripts/figures.py` |
| `[^3]` … `[^3]: Label \| path#L10-L20` | a footnote linking into the source repo |

A callout continues across lines that begin with `>`; a bare `>` starts a new
paragraph inside the same callout.

## Rules that are not style preferences

- **Every `> RED:` is followed by a `> PATH:`.** If the repo records no remedy, the
  PATH line says exactly `No path to green is recorded in the repo.` — after looking.
- **No internal identifiers in prose.** A reader does not know what `755-qcxh` is.
  State the substance in a sentence they could repeat out loud; the identifier lives
  in the footnote target and nowhere else.
- **Footnote targets are repo-relative paths** with optional `#L10-L20` anchors, or
  full external URLs. They are resolved against the tag pinned in `build-matrix.py`,
  not against `main`, so a reader clicking a line number lands on the line we quoted.
  When you bump that tag, re-verify the line ranges — they drift.
- **Implementation trivia is not substance.** File counts, test counts, crate and
  function names earn their place only when the claim collapses without them.

## Figures

`layers`, `loop`, `staircase`, `lln`, `lattice`, `crdt`, `gate`, `ephemeral` — defined
as inline SVG in `scripts/figures.py`, drawn with the page's own CSS variables so they
carry one idea each and need no second palette.

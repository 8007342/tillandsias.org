# The content matrix

`var/html/index.html` is **generated**. Edit the words here, never the HTML.

    TILLANDSIAS_CLONE_DIR=/dir/of/checkouts/named/by/tag \
      python3 scripts/build-matrix.py

`TILLANDSIAS_CLONE_DIR` holds one checkout per release tag the levels pin to
(`/dir/v56.9.5.1`, …); `TILLANDSIAS_CLONE=/one/checkout` still works for a single
tag, read from `git describe`. Without either the page still builds; with them, every
footnote of a level whose checkout is present is checked — the file must exist, the
line range must be inside it, and the quote must appear verbatim inside that range —
and the build prints anything that does not resolve and exits non-zero. Do a checked
build before publishing: a footnote that 404s is worse than no footnote, and a quote
that drifted from its source is worse than a 404.

Each level pins its own release in the `LEVELS` table of `scripts/build-matrix.py`.
The newest pin is shown in the page header as the release the site was last checked
against. Levels move independently so that a page whose owner accepts only tiny
deltas is not dragged forward when the others are re-verified.

One file per explanation level. Each is a single merged narrative — what the thing
is and how it works, woven together, because splitting them read as two disconnected
essays. The reader knows nothing about the project.

## The dialect

Small on purpose. Anything not listed here is not supported.

| Syntax | Renders as |
|---|---|
| `# Title` | the level's own title, once, at the top |
| `## Heading` / `### Sub` | section headings |
| `- item` / `1. item` | bullets / numbered list |
| `**bold**` `*italic*` `` `code` `` | inline emphasis |
| `> GREEN: …` | ● *verified* — something checked against the source and working |
| `> RED: …` | ● *shortcoming* — something incomplete, pending, wrong or overclaimed |
| `> PATH: …` | → the recorded path to green for the RED above it |
| `> PROVEN: …` | ✓ *shown* — an argument we can point at the code or a test for |
| `> PLAUSIBLE: …` | ∼ *plausible* — an argument that sounds right and is not yet demonstrated |
| `> REFUTED: …` | ✗ *does not hold* — an argument we tried, and it failed |
| `> NOTE: …` | a neutral aside |
| `$x$` and `$$x$$` | inline / display maths, rendered by KaTeX |
| `@fig:name` | a diagram from `scripts/figures.py` |
| `[^3]` … `[^3]: Label \| path#L10-L20` | a footnote linking into the source repo |
| `    > quoted lines` (under a footnote) | the verbatim quote shown in the tooltip and the list |

A callout continues across lines that begin with `>`; a bare `>` starts a new
paragraph inside the same callout.

GREEN and RED say what the *thing* does. PROVEN, PLAUSIBLE and REFUTED say how good
*our argument* for a claim is — use them where the page reasons rather than reports,
and use them sparingly: a page that is all flags has stopped being prose.

A footnote number in the text opens its source in a new tab; hovering it shows the
label, the quote, and the target. The list at the foot of the level stays for
completeness and for readers without a pointer.

## Rules that are not style preferences

- **Every `> RED:` is followed by a `> PATH:`.** If the repo records no remedy, the
  PATH line says exactly `No path to green is recorded in the repo.` — after looking.
- **No internal identifiers in prose.** A reader does not know what `755-qcxh` is.
  State the substance in a sentence they could repeat out loud; the identifier lives
  in the footnote target and nowhere else.
- **Footnote targets are repo-relative paths** with optional `#L10-L20` anchors, or
  full external URLs. They are resolved against the tag the level pins in
  `build-matrix.py`, not against `main`, so a reader clicking a line number lands on
  the line we quoted. When you bump a level's tag, re-verify its line ranges — they
  drift — and rebuild with the checkout present so the quotes are re-checked too.
- **Quotes are verbatim and contiguous.** Copy the characters from the cited range;
  no paraphrase, no ellipsis, at most a few sentences. The checked build searches for
  the quote inside the cited lines after collapsing whitespace, and fails if it is
  not there. A footnote with no quote is allowed (external references, long ranges).
- **Implementation trivia is not substance.** File counts, test counts, crate and
  function names earn their place only when the claim collapses without them.
- **Level 5 moves only in tiny, individually justified deltas.** Its pin is bumped
  separately from the others, and every change to its text is proposed in an OpenSpec
  change under `openspec/changes/` before it lands.

## Figures

`layers`, `loop`, `staircase`, `lln`, `lattice`, `crdt`, `gate`, `ephemeral`,
`fixpoint`, `galois`, `hasse` — defined as inline SVG in `scripts/figures.py`, drawn
with the page's own CSS variables so they carry one idea each and need no second
palette.

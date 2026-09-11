## Why

The site tells the Tillandsias story in five written levels, but there is no way
to *present* it: no deck, no walk-through, nothing to stand in front of a room
with. A live talk needs a fourth page — **Slides** — reachable from the same
menu, carrying a short deck that tells the project's story in a handful of
slides: a **containerized workflow**, **Linux security**, a **portable cloud
region**, and a methodology that keeps the state of that region **conflict-free
through replicated data types**.

This change is deliberately the framework first and the content later. The
deliverable is the page, the deck mechanism (slide N → slide N+1 and back), the
three-slide skeleton with the most important placeholders, and the honesty
machinery that keeps a presentation from becoming the one surface on the site
that can say anything uncited. The pretty content inside each slide — figures,
animations, transitions — is a later change; it must not be needed for the deck
to show and move.

## What Changes

- A fourth page, `view-slides`, behind the existing hamburger menu, listed after
  **Live progress**, built by the same generator that builds the other three
  pages and never edited in the rendered output.
- A declarative slide source, `scripts/slides.py`, holding the deck as data:
  each slide a small dict (label, title, blocks, a drawing-on line), rendered
  into the page by `scripts/build-matrix.py`. Editing the deck means editing
  the source and rebuilding — the same contract the levels obey.
- A deck mechanism inside the page: exactly one slide visible at a time; a
  counter ("2 / 3"); prev/next controls; arrow and home/end keys; a progress
  rail; and a deep link (`#slides`, `#slides-2`) so a slide is addressable and
  a talk can be started on any slide.
- Three slides carrying the story's most important placeholders:
  1. **The thesis** — what Tillandsias is (the site's established one-liner).
  2. **The pillars** — containerized workflow, Linux security, portable cloud
     region.
  3. **The mechanism** — the methodology, and conflict-free replicated data sets
     (CRDTs).
- Content honesty for the deck: a slide states only what a level page already
  establishes, and every slide carries a visible "drawing on" line naming the
  level it restates; a placeholder says it is a placeholder.
- The navigation spec loses its "three pages" to a "four pages" requirement,
  the uncited-claim rule is widened to cover Slides, and the home page's links
  onward gain Slides.

## Capabilities

### New Capabilities

- `site/slides`: the presentation page — the fourth menu entry, the deck
  mechanism, the counter and deep links, the ship-inline rule, and the honesty
  contract (no uncited claims, placeholders labelled, every slide naming the
  level it draws on). It does not restate the levels' content; it points at it.

### Modified Capabilities

- `site/navigation`: the menu now carries four pages in the order Home, What is
  it?, Live progress, Slides; the uncited-claim and sentence-shape rules now
  cover Slides; Home's onward links gain Slides.

## Impact

- New change directory `openspec/changes/slides-presentation/` with a delta
  spec under `specs/site/slides/` and a delta to `specs/site/navigation/`.
- New file `scripts/slides.py` (deck source, a fact-file sibling of
  `scripts/facts.py`).
- Changes to `scripts/build-matrix.py` (a `slides_view()` renderer, a
  `__SLIDES__` placeholder, the menu entry, deck CSS and deck JS) and, through
  the build, to `var/html/index.html` (the committed page).
- The deck is not a level page: it carries no footnote lists. Its honesty
  mechanism is the "drawing on" line, which links into the level page rather
  than repeating that level's footnote machinery.
- The five explanation levels MUST NOT be promoted into the menu; Slides is a
  page, not a level, and this change does not blur that line.
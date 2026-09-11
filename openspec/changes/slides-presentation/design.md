# Design: slides-presentation

## Overview

Slides is a fourth `view` inside the same generated single-page document, built
the same way the other three are: the generator (`scripts/build-matrix.py`)
emits markup into the `TEMPLATE`, the menu's `[data-go]` buttons and
`.view`/`.is-active` switching are already generic, and the deck lives inside
the page with no external assets. Nothing new is fetched; nothing new blocks.

```
scripts/
├── slides.py          NEW  — the deck, as plain data (a facts.py sibling)
└── build-matrix.py    EDITED — slides_view(), __SLIDES__ placeholder,
                               menu entry, deck CSS, deck JS

var/html/index.html    REGENERATED (the committed page)
```

## The deck source

`scripts/slides.py` exports `SLIDES`, a list of slide dicts. Each slide:

- `label` — short title for the progress rail and aria (`"thesis"`).
- `title` — the slide's headline.
- `eyebrow` — the small kicker above the title (page furniture, e.g. "Slide 1 of
  the deck").
- `blocks` — a list of `(kind, text)` pairs the renderer turns into elements.
  Kinds for the skeleton: `"p"` (paragraph) and `"pillars"` (rendered as three
  cards, each card a `(name, sentence)` tuple). Kinds can grow as the deck does;
  the renderer is a plain `if kind:` dispatch.
- `draws_on` — optional; the level the slide restates, stored as its tab slug
  and shown as a linked "drawing on the … level" line. `None` for furniture-only
  slides. Stored at build time via the same `LEVELS` table `build-matrix.py`
  already carries.

Placeholder regions are part of the data, not magic: a slide whose content is
not yet written lists its blocks and the renderer or a small `PLACEHOLDER`
helper marks un-written blocks with the site's labelled "content to come" chip,
the way Home labels its artwork. The placeholders make no claims.

## The mechanism

Within `view-slides`:

- One `.deck` container holding `.deck-frame` (the visible slide) and
  `.deck-nav` (prev control, counter, next control, plus an sr progress
  rail). Only one slide has `.is-on` at a time; the rest are `display:none`.
  CSS-only: no scripting needed to see the first slide, because the first
  slide is the one marked `.is-on` in the markup.
- Slides carry `data-slide="N"` and `aria-hidden` toggles; the counter reads
  `N / count`; the rail fills as the reader advances.
- One new IIFE, `deck()`, mirrors the existing tab code:
  - `go(n)`: hides all slides, shows slide N, updates the counter and rail,
    and `history.replaceState` to `#slides` (N=1) or `#slides-N`.
  - Buttons wire to `go(N±1)`; at either end the control is disabled (the spec
    forbids wrapping).
  - `keydown`: ArrowRight / Space → next, ArrowLeft → prev, Home → 1, End →
    last, but only while `view-slides` is active, the drawer is closed, and
    the focus is not in an input.
  - `fromHash()` addition: `#slides` → `view-slides`; `#slides-N` → the view
    plus slide N (clamped, URL corrected). `hashchange` re-runs it so the back
    button undoes a slide change.

Fragments never collide: level fragments are `#level-3-power`, the deck's are
`#slides-N`.

## The page, menu and navigation spec

- The drawer gains a fourth `<button class="nav" data-go="view-slides">`
  (glyph `▶` via `&#9654;`), after Live progress. The existing `go()` and
  `fromHash()` need only a `slides` case added.
- `slides_view()` emits the `<section class="view" id="view-slides" …>`, the
  deck markup, and the deck's header (eyebrow + heading, so it is not a bare
  frame). `build()` inserts it via a `__SLIDES__` placeholder in the `TEMPLATE`.
- The `site/navigation` delta changes three pages → four, adds Slides to the
  uncited-claim and sentence-shape rules, and adds Slides to Home's onward
  links; the `site/slides` delta declares the deck page's own contract. Both are
  in this change; `site/slides` is archived with it, `site/navigation` is
  synced as a modification.

## Content honesty

The deck's three skeleton slides use only the site's already-fixed, already
checked wording: the byline "An idempotent, ephemeral cloud region, folded
through your hypervisor" is the page's own `<title>` and `<h1>`; "Local
hardware. Free software. Nothing rented, nothing metered, nothing left behind."
is the lede and Home's positioning line. Every substantive region beyond that is
a labelled placeholder. `draws_on` wires the pillar cards and the mechanism
slide to the levels they will restate (power user / security / mathwiz), so when
the content lands it must land no stronger than the named level, and the link
lets a reader follow it. The spec's scenarios in `site/slides` and the widened
`site/navigation` wording enforce that this is the only way the deck speaks.

## No output change beyond the deck

The deck is added, so the page necessarily changes; but the property the build
already promises holds: rebuild the same sources and the deck bytes are
identical. A `sha256sum` of `var/html/index.html` before and after a no-op
rebuild is recorded in `tasks.md` 5.2.
## Why

The site's five explanation pages (`docs/matrix/level-1..5-*.md`, rendered into
the single `var/html/index.html`) are the project's front door, and each is a
long-lived contract of its own: a distinct audience, a distinct honesty frame
(GREEN/RED/PATH), and a set of claims that must stay true against the pinned
release tag. Today nothing declares what a given page *is for* or what a change
to it must preserve, so edits can silently break the level's promise (e.g. a RED
flag that no longer matches the code, or a claim that drifts from its footnote).

We need an OpenSpec document per page — one delta spec per level — so each page
has a stable identity, an owner, and a change trail. This change initializes all
five page specs in one step; the 2026-09-04 audit annotations
(`docs/matrix/*.audit.md`) are referenced from the specs so the next editor can
see what was checked.

## What Changes

- One new OpenSpec delta spec per explanation level:
  - `site/level-1`: "Like I'm 5" — simplest-true framing, app-vocabulary promise.
  - `site/level-2`: "I barely understand my phone" — privacy/cost/what-breaks.
  - `site/level-3`: "I'm a power user" — anatomy, survivorship, sharp edges.
  - `site/level-4`: "I'm a Cyber Security expert" — boundaries, egress, provenance.
  - `site/level-5`: "I'm a PhD / MathWiz / Hacker" — formal math content.
- Each spec states the page's purpose, its audience, its sourcing rule (footnotes
  resolve against the pinned tag, never `main`), and its ownership. Level 5's spec
  records that its explanation is owned outside this audit.
- The audit annotation files (`docs/matrix/level-1..4-*.audit.md`) are declared as
  companion artifacts; the level-5 page has no audit file (out of scope).

## Capabilities

### New Capabilities

- `site/level-1`: The "Like I'm 5" explanation page's purpose and content contract.
- `site/level-2`: The "I barely understand my phone" page's purpose and content contract.
- `site/level-3`: The "I'm a power user" page's purpose and content contract.
- `site/level-4`: The "I'm a Cyber Security expert" page's purpose and content contract.
- `site/level-5`: The "I'm a PhD / MathWiz / Hacker" page's purpose and content contract.

### Modified Capabilities

None.

## Impact

- New change directory `openspec/changes/add-level-page-specs/` with five delta
  specs under `specs/site/level-<n>/`.
- No change to rendered output: `var/html/index.html` rebuilds byte-identical.
- After archive/sync, the main specs tree gains `openspec/specs/site/level-<n>/spec.md`.
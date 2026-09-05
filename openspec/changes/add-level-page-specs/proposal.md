## Why

The site's five explanation pages (`docs/matrix/level-1..5-*.md`, rendered into
the single `var/html/index.html`) are the project's front door, and each is a
long-lived contract of its own: a distinct audience, a distinct honesty frame
(GREEN/RED/PATH), and a set of claims that must stay true against the release
tag the level pins. Today nothing declares what a given page *is for* or what a
change to it must preserve, so edits can silently break the level's promise: a
RED that no longer matches the code, a claim that drifts from its footnote, a
pin that lags the stable channel with no record of why.

We need an OpenSpec document per page — one delta spec per level, plus one
shared spec for the rules every level obeys — so each page has a stable
identity, an owner, and a change trail. Requirements state durable properties of
the pages. The dated findings of any one audit run are work items in `tasks.md`
and notes in the dated audit files; they are never requirement text, because a
finding that is true at one pin is false at the next.

## What Changes

- One shared delta spec, `site/level-common`: each level pins its own release;
  the pin equals the stable channel's tag or the dated audit record names the
  lag and why; the checked build with verbatim quotes passes before publish; the
  RED lifecycle at a pin bump; where audit records live and what the
  `*.audit.md` files are; the argument markers, used sparingly.
- One delta spec per explanation level:
  - `site/level-1`: "Like I'm 5" — simplest-true framing, app-vocabulary promise.
  - `site/level-2`: "I barely understand my phone" — privacy/cost/what-breaks.
  - `site/level-3`: "I'm a power user" — anatomy, survivorship, sharp edges.
  - `site/level-4`: "I'm a Cyber Security expert" — boundaries, egress, provenance.
  - `site/level-5`: "I'm a MathWiz / Hacker" — the formal content, under the
    delta discipline: its own pin, every change through an OpenSpec change,
    verdicts re-derived at each pin bump.
- Each per-level spec states the page's purpose, its audience, and the
  properties an edit must preserve, expressed as properties that hold at the
  level's pin rather than as verdicts on particular flags. Level 5's spec is the
  delta-discipline contract that `docs/matrix/README.md` already imposes; its
  owner is this repository's operator.
- The audit annotation files (`docs/matrix/level-1..4-*.audit.md`) are dated
  inputs to the work items in `tasks.md`, valid for the pin named in their
  header and superseded by the next record under `docs/audit/`.

## Capabilities

### New Capabilities

- `site/level-common`: The rules every level page obeys — per-level pin, pin
  equals stable or the lag is recorded, checked build with verbatim quotes, RED
  lifecycle at a pin bump, audit records, argument markers.
- `site/level-1`: The "Like I'm 5" explanation page's purpose and content contract.
- `site/level-2`: The "I barely understand my phone" page's purpose and content contract.
- `site/level-3`: The "I'm a power user" page's purpose and content contract.
- `site/level-4`: The "I'm a Cyber Security expert" page's purpose and content contract.
- `site/level-5`: The "I'm a MathWiz / Hacker" page's purpose, claim form and
  delta discipline.

### Modified Capabilities

None.

## Impact

- New change directory `openspec/changes/add-level-page-specs/` with six delta
  specs under `specs/site/`.
- No change to rendered output: the specs and the audit files are not inputs to
  `scripts/build-matrix.py`. The rebuild check and its result are recorded in
  `tasks.md` 3.2.
- After archive/sync, the main specs tree gains
  `openspec/specs/site/level-common/spec.md` and
  `openspec/specs/site/level-<n>/spec.md`.

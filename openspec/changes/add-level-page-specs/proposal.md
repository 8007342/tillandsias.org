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
- One delta spec for the site as a whole, `site/navigation`: the hamburger
  control and the left collapsing menu with its three entries — Home, "What is
  it?", Live progress — landing on "What is it?"; the home page's labelled
  placeholder, its `Tillandsias` wordmark and `by Tlatoāni` byline, and the one
  fun fact drawn per visit from a pool that ships with the page; the Live
  progress board, where every finding in `issues.d/` sits in exactly one of
  three columns, the columns are folded from the ledger's own monotone ladder
  rather than maintained by hand, and each finding's dependencies, chronology
  and upstream filing state are visible; and the measurement requirements,
  which permit the intention to grade components and to plot convergence on a
  logarithmic time axis while forbidding the page to present a pass rate as a
  CentiColon score, or to draw monotone progress across a change of denominator.
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
- `site/navigation`: The site as a whole — the three pages behind the collapsing
  menu and which one a reader lands on, the home placeholder and its single
  fun fact, the three-column progress board derived from the findings ledger,
  and the rule that a measurement the project cannot yet compute is never shown
  as measured.

### Modified Capabilities

None.

## Impact

- New change directory `openspec/changes/add-level-page-specs/` with seven delta
  specs under `specs/site/`.
- No change to rendered output: the specs and the audit files are not inputs to
  `scripts/build-matrix.py`. The rebuild check and its result are recorded in
  `tasks.md` 3.2.
- After archive/sync, the main specs tree gains
  `openspec/specs/site/level-common/spec.md`,
  `openspec/specs/site/level-<n>/spec.md` and
  `openspec/specs/site/navigation/spec.md`.
- `site/navigation` describes the three-page site the operator is building
  separately; this change writes the contract only and implements none of it.

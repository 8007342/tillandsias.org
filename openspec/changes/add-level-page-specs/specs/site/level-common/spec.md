## Purpose

The rules every explanation page obeys, stated once so the per-level specs can
say only what is particular to their page. They restate as requirements what
`docs/matrix/README.md` and `skills/update-website/SKILL.md` already impose: a
page is a set of claims footnoted into the Tillandsias source at a release the
page pins, and it stays true by being re-verified against that release — never
by being frozen.

## ADDED Requirements

### Requirement: Each level pins its own release
Each level MUST pin its own release tag in the `LEVELS` table of
`scripts/build-matrix.py`, and every footnote of that level MUST resolve against
that tag, never `main`. Levels move independently. A footnote MAY point past its
level's pin only with an explicit `@vTAG` suffix, and only on a PATH line that
acknowledges a fix present in a build newer than the pin.

#### Scenario: Footnote resolves at the pin
- **WHEN** a reader follows a footnote of a level
- **THEN** they land on the cited path and line range at that level's pinned tag

#### Scenario: Footnote past the pin
- **WHEN** a PATH line cites a fix that exists only in a build newer than the pin
- **THEN** that footnote carries the newer build's tag as an `@vTAG` suffix, and
  no other footnote of the level points past the pin

### Requirement: The pin is the stable channel's tag, or the lag is recorded
A level's pin MUST equal the tag the stable channel resolves to — the binary a
reader who copies the install commands actually gets — or the current record
under `docs/audit/` MUST name the level, the tag it stays at, and why.

#### Scenario: Stable tag promoted
- **WHEN** the stable channel moves to a new tag
- **THEN** each level is re-verified and moved to it, or the dated audit record
  of that run names each level left behind and the reason

#### Scenario: A level lags by design
- **WHEN** one level's pin is behind the others' (level 5 accepts only tiny
  deltas and may lag)
- **THEN** the page header shows the newest pin across levels, the lagging
  level's row in `LEVELS` shows its own tag, and the audit record names the lag

### Requirement: The checked build passes before publish
Before a page is published, a build with a checkout present for every pinned
tag MUST pass: for every footnote the path exists at its tag, the line range is
inside the file, and the quote — verbatim, contiguous, copied from the cited
range — appears inside that range after whitespace is collapsed. No level is
published while the build lists a broken target or a drifted quote for it.

#### Scenario: Quote drifted
- **WHEN** a footnote's quote is no longer inside its cited range at the tag
- **THEN** the build reports the footnote and exits non-zero, and the page is
  not published until the target or the quote is corrected

#### Scenario: Footnote without a quote
- **WHEN** a footnote is an external URL or covers a range too long to quote
- **THEN** it MAY carry no quote, and the build checks only that the target
  resolves

### Requirement: RED lifecycle at a pin bump
Every RED MUST be true of the code at the level's pinned tag and MUST be
followed by a PATH. When a level's pin moves: a RED the new pin's code has fixed
becomes a past-tense flag or a GREEN; a RED fixed only in a build newer than the
pin stays RED and its PATH says when the fix landed, citing it with that build's
`@vTAG` footnote; a partial fix says what remains; and when the repository
records no remedy, the PATH says exactly that, after looking.

#### Scenario: The pin outruns a RED
- **WHEN** a level's pin moves to a tag whose code fixes a RED
- **THEN** the RED is rewritten as a past-tense flag or a GREEN, footnoted at
  the new pin

#### Scenario: A daily fixes a RED
- **WHEN** a fix exists only in a build newer than the level's pin
- **THEN** the RED stays, and its PATH names the build the fix landed in with an
  `@vTAG` footnote

### Requirement: Requirement text carries no dated finding
The requirement text of a page spec MUST NOT contain a dated finding, an order
or packet identifier, a ledger line number, a file count, or a mandated verdict
on a specific flag. Such findings are work items in the change's `tasks.md`
(paths only) and notes in the dated audit record; the spec states the property
the finding is an instance of.

#### Scenario: An audit produces a finding
- **WHEN** an audit finds a claim on a page false at its pin
- **THEN** the finding is filed as a work item and the page is corrected, and
  the spec is unchanged unless a durable property was missing from it

### Requirement: Audit records and their inputs
Each run of the update loop MUST write its record to
`docs/audit/<YYYY-MM-DD>-<tag>.md`. The `docs/matrix/*.audit.md` files are
dated inputs valid for the pin named in their header; they are superseded by
the next record under `docs/audit/` and are never a source of requirement text.

#### Scenario: Audit file at an old pin
- **WHEN** a level's pin has moved past the tag an `*.audit.md` file names
- **THEN** that file's findings are history, and the current `docs/audit/`
  record is what an editor consults

### Requirement: Argument markers are used sparingly
Where a page reasons rather than reports, it MAY mark the strength of its own
argument with PROVEN (code or a test can be pointed at), PLAUSIBLE (sounds
right, not demonstrated) or REFUTED (tried, and failed), per
`docs/matrix/README.md`, and MUST use the markers sparingly: GREEN and RED say
what the thing does; the markers say how good the argument is. The prose is the
content: a page that is all flags has stopped being prose.

#### Scenario: An argument is marked PROVEN
- **WHEN** a page marks an argument PROVEN
- **THEN** the line cites the code or the test that demonstrates it

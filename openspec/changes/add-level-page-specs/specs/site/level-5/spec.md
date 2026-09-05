## Purpose

The "I'm a MathWiz / Hacker" page (`docs/matrix/level-5-phd.md`) is the formal
content: obligation-state lattices, fixed points, the finite-iteration theorem,
the strong-law / monotone-convergence floor, and the CRDT material — stated as
claims with hypotheses, sorted into standard theorems invoked, what the
repository asserts, what follows, and what does not. It is edited in this
repository, by this repository's operator, under the delta discipline
`docs/matrix/README.md` states: tiny, individually justified changes, each
proposed before it lands. The rules shared by every level are in
`site/level-common`.

## ADDED Requirements

### Requirement: Own pin, which may lag
Level 5 MUST pin its own tag in the `LEVELS` table of `scripts/build-matrix.py`.
Its pin MAY lag the other levels' pins, and the lag MUST be visible: the page
header shows the newest pin across levels, the level's own row shows its tag,
and the current audit record names the lag. A pin bump for level 5 is itself an
OpenSpec change.

#### Scenario: Other levels move first
- **WHEN** levels 1 to 4 are moved to a new stable tag and level 5 is not
- **THEN** level 5's footnotes still resolve at its own tag, the header shows the
  newer pin, and the audit record names level 5 as lagging and why

### Requirement: Delta discipline
Every change to the page's text and every bump of its pin MUST land through an
OpenSpec change under `openspec/changes/` that lists one delta per requirement,
flag or footnote it touches, each with `path#Lstart-Lend` evidence and a
verbatim quote at the target tag. An editor MAY apply the deltas it lists, and
MUST apply no others: the record and the diff are checked against each other,
and the operator reviews the change before it is archived. A structural rewrite
is out of scope for a delta and needs its own change with a `design.md`.

#### Scenario: Pin bump proposed
- **WHEN** a pin bump for level 5 is proposed
- **THEN** the change lists one delta per footnote whose target or quote drifted
  between the tags, each with evidence at the target tag, and the change is not
  archived until the operator has reviewed it

#### Scenario: The diff exceeds the record
- **WHEN** the page's diff contains a hunk that no delta in the change lists
- **THEN** that hunk is a defect: it is reverted, or the change is amended to
  list it with its evidence before the change is archived

#### Scenario: Agent proposes a rewrite
- **WHEN** an agent proposes reorganising or rewriting the page rather than a
  set of deltas
- **THEN** the proposal is refused as exceeding delta scope

### Requirement: Claim-with-hypotheses form
Every mathematical claim on the page MUST name the theorem it invokes and the
hypotheses it needs, and MUST be sorted into the page's four bins: the standard
theorem invoked, what the repository asserts, what follows, and what does not.
The strength of the page's own arguments is marked PROVEN, PLAUSIBLE or REFUTED
per `docs/matrix/README.md`, sparingly; every RED has a PATH.

#### Scenario: Form is preserved
- **WHEN** the page is revised
- **THEN** each claim still names its theorem and hypotheses and sits in one of
  the four bins, and the markers are used where the page reasons, not
  everywhere

### Requirement: Verdicts are re-derived, never frozen
At each pin bump the proposal MUST re-examine every RED and every PLAUSIBLE
against the target tag and propose past-tense or GREEN wording where the code
has moved, while a fix present only in a build newer than the pin stays RED with
that build named in its PATH. This spec requires the form of the verdicts and
never a particular verdict: which hypotheses are discharged and which are
assumed is a fact of the pin, restated at each bump.

#### Scenario: A daily fixes a RED
- **WHEN** a RED on the page is fixed only in a build newer than level 5's pin
- **THEN** the RED stays, and its PATH names that build with an `@vTAG` footnote

#### Scenario: The pin outruns a hypothesis flag
- **WHEN** a pin bump reaches a tag whose code discharges a hypothesis the page
  called assumed
- **THEN** the change proposes the past-tense or GREEN wording for that flag with
  evidence at the new tag

### Requirement: Sourcing
Repository claims MUST cite `methodology/` or `crates/` (or another repository
path) at the pin with verbatim quotes that pass the checked build. External
references MUST cite a DOI or a stable URL and carry no quote. Measured numbers
in the prose (line counts, dashboard figures) MUST be re-measured at every pin
bump.

#### Scenario: Footnotes resolve at the pin
- **WHEN** a checked build is run for this page
- **THEN** every footnote target exists at the pinned tag within its cited line
  range and every quote is found inside that range

#### Scenario: A measured number is carried across a bump
- **WHEN** a pin bump is proposed and the prose contains a measured number
- **THEN** the change re-measures it at the target tag or lists it as a delta

### Requirement: Audit annotations are the proposal's input
Audit annotations for level 5 MUST be accepted as dated notes valid for the pin
they name; they are allowed and expected, they are the input to the next delta
proposal, and they are superseded per pin as `site/level-common` says.

#### Scenario: An audit annotates level 5
- **WHEN** an audit at a tag finds a level-5 claim drifted or outrun
- **THEN** the finding is recorded as a dated note and becomes a listed delta in
  the next OpenSpec change for the page; the page itself is not edited by the
  auditor
